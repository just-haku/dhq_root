import time
import schedule
import os
import sys
import datetime
import requests
from app import create_app
from app.utils import clean_temp_files
from app.models import Collaboration, Order, User
from app.extensions import db

# Setup Environment
project_dir = os.environ.get('PROJECT_DIR', os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_dir)

# Load App Config (to get TEMP_FOLDER)
app = create_app()

API_URL = "https://tangtuongtacre.com/api/v2"

def job_cleanup():
    print(f"[Cron] Starting cleanup at {time.ctime()}")
    with app.app_context():
        clean_temp_files(app)
    print(f"[Cron] Cleanup finished.")

def run_job():
    print(f"[{datetime.datetime.now()}] --- START CRON JOB ---")
    
    with app.app_context():
        # 1. Find Active Collaborations
        # Assuming you've migrated 'auto_check' and 'is_deleted' to MongoDB fields in Collaboration model
        # Using MongoEngine syntax: objects(auto_check=True, is_deleted=False)
        active_collabs = Collaboration.objects(auto_check=True, is_deleted=False)
        print(f"Found {len(active_collabs)} active collaborations.")
        
        operator = User.objects(username='kuro').first()
        api_key = operator.api_key if operator else None
        if not api_key:
            print("CRITICAL: No Operator API Key. Aborting.")
            return

        for collab in active_collabs:
            # 2. Identify Orders
            now = datetime.datetime.now()
            
            # A. Handle "Not Ordered" (Missed Window)
            # MongoEngine query for Pending orders with scheduled_time < now - 1 hour
            missed_orders = Order.objects(
                collaboration=collab,
                status='Pending',
                scheduled_time__lt=(now - datetime.timedelta(hours=1))
            )
            
            for mo in missed_orders:
                mo.status = 'Not Ordered'
                mo.save()
                print(f" -> Order {mo.id}: Missed window (Not Ordered)")
            
            # B. Handle Due Orders
            # MongoEngine query for Pending orders with scheduled_time <= now
            due_orders = Order.objects(
                collaboration=collab,
                status='Pending',
                scheduled_time__lte=now
            )
            
            # Check for completion
            # If no due orders, check if there are ANY pending orders left for this collab
            if not due_orders:
                pending_count = Order.objects(collaboration=collab, status='Pending').count()
                if pending_count == 0:
                    print(f"Collab {collab.id} finished. Pausing.")
                    collab.auto_check = False
                    collab.save()
                continue
            
            print(f"Collab {collab.id}: Executing {len(due_orders)} orders...")
            
            # Execution Loop
            collab_error_occurred = False
            
            for order in due_orders:
                try:
                    payload = {
                        'key': api_key,
                        'action': 'add',
                        'service': collab.service_id,
                        'link': collab.link,
                        'quantity': order.quantity
                    }
                    
                    res = requests.post(API_URL, data=payload, timeout=15)
                    json_res = res.json()
                    
                    if json_res.get('order'):
                        order.status = 'Ordered'
                        order.api_order_id = str(json_res.get('order'))
                        order.executed_at = datetime.datetime.now()
                        order.save()
                        print(f" -> Order {order.id}: SUCCESS")
                    else:
                        # API ERROR -> Fail Order AND Pause Collab
                        order.status = 'Failed' 
                        order.api_response = str(json_res)
                        order.save()
                        collab_error_occurred = True
                        print(f" -> Order {order.id}: API REFUSED: {json_res}")
                        
                except Exception as e:
                    # NETWORK/SYSTEM ERROR -> Fail Order AND Pause Collab
                    order.status = 'Failed'
                    order.api_response = str(e)
                    order.save()
                    collab_error_occurred = True
                    print(f" -> Order {order.id}: EXCEPTION: {e}")
            
            # If any error occurred in this batch, PAUSE the automation for this collab
            if collab_error_occurred:
                print(f"!! Collab {collab.id} PAUSED due to errors. Manual Review Required.")
                collab.auto_check = False
                collab.save()

    print(f"[{datetime.datetime.now()}] --- END CRON JOB ---")

# Schedule: Run every hour for cleanup
schedule.every(1).hours.do(job_cleanup)

# Schedule: Run order processing every minute (or as desired)
# Adjust the frequency as needed. 'every(1).minutes' is common for checking due tasks.
schedule.every(1).minutes.do(run_job)

if __name__ == "__main__":
    print("Starting Cron Worker...")
    # Run cleanup once on startup
    job_cleanup()
    # Run job once on startup to catch up
    run_job()
    
    while True:
        schedule.run_pending()
        time.sleep(60)