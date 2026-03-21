import os
import shutil
from app import create_app
from app.models import User, Role, Group, Collaboration, Order, Task, ChatMessage, Notification, Media, MediaGroup, ScanResult

def perform_nuke(app_instance):
    """
    Deletes all documents from MongoDB collections and wipes the upload folder.
    """
    logs = []
    
    # Ensure we are in an app context
    with app_instance.app_context():
        # 1. Wipe Database Collections
        # List of MongoEngine Document classes to clear
        collections = [
            User, Role, Group, Collaboration, Order, 
            Task, ChatMessage, Notification, Media, 
            MediaGroup, ScanResult
        ]

        print("--- Wiping Database Collections ---")
        for Model in collections:
            count = Model.objects.count()
            if count > 0:
                Model.objects.delete()
                msg = f"Deleted {count} documents from {Model.__name__}"
                print(msg)
                logs.append(msg)
            else:
                print(f"{Model.__name__} is already empty.")

        # 2. Wipe Upload Folder
        upload_folder = app_instance.config.get('UPLOAD_FOLDER')
        if upload_folder and os.path.exists(upload_folder):
            print(f"--- Wiping Upload Folder: {upload_folder} ---")
            try:
                # Iterate over items in the upload folder
                for filename in os.listdir(upload_folder):
                    file_path = os.path.join(upload_folder, filename)
                    try:
                        if os.path.isfile(file_path) or os.path.islink(file_path):
                            os.unlink(file_path)
                        elif os.path.isdir(file_path):
                            shutil.rmtree(file_path)
                        logs.append(f"Deleted: {filename}")
                    except Exception as e:
                        err = f"Failed to delete {file_path}. Reason: {e}"
                        print(err)
                        logs.append(err)
                
                # Re-create critical subdirectories
                os.makedirs(os.path.join(upload_folder, 'avatars'), exist_ok=True)
                os.makedirs(os.path.join(upload_folder, 'shop'), exist_ok=True)
                os.makedirs(os.path.join(upload_folder, 'temp'), exist_ok=True)
                print("Re-created default subfolders (avatars, shop, temp).")
                
            except Exception as e:
                logs.append(f"Error accessing upload folder: {e}")
        else:
            logs.append("Upload folder not found or not configured.")

    return logs

def nuke_data_cli():
    """
    CLI Entry point to run the nuke.
    """
    app = create_app()
    
    print("\n" + "!"*40)
    print("!!! DANGER ZONE !!!")
    print("!"*40)
    print(f"Target Files:    {app.config.get('UPLOAD_FOLDER')}")
    print("Action:          DELETE EVERYTHING (Collections + Files)")
    print("!"*40 + "\n")
    
    confirm = input("Type 'NUKE' to confirm: ")
    if confirm == 'NUKE':
        logs = perform_nuke(app)
        print("\n--- Operation Log ---")
        for log in logs:
            print(log)
        print("\nNUKE COMPLETE.")
    else:
        print("Operation cancelled.")

if __name__ == "__main__":
    nuke_data_cli()