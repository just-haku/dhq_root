import os
import shutil
import random
import subprocess
import time
from .models import User, Role
from .extensions import db

def create_default_admin():
    """Initializes the DB with default roles and the 'kuro' operator."""
    # Check if we need to initialize (if no roles or no users exist)
    if Role.objects.count() == 0 or User.objects.count() == 0:
        print("Initializing Database Defaults...")

        # 1. Create Roles
        operator_role = Role.objects(name='operator').first()
        if not operator_role:
            operator_role = Role(name='operator', permissions=['all', 'operator'])
            operator_role.save()
        
        admin_role = Role.objects(name='admin').first()
        if not admin_role:
            admin_role = Role(name='admin', permissions=['all'])
            admin_role.save()
        
        user_role = Role.objects(name='user').first()
        if not user_role:
            user_role = Role(name='user', permissions=['basic'])
            user_role.save()

        # 2. Create Operator 'kuro' (The Project Owner)
        if not User.objects(username='kuro').first():
            kuro = User(username='kuro', role=operator_role)
            kuro.set_password('00491E4C')
            kuro.display_name = "System Operator"
            kuro.api_key = "OP-MASTER-KEY" 
            kuro.save()
            print(">>> Created Operator Account: kuro")

        # 3. Create generic admin (Backup)
        if not User.objects(username='admin').first():
            admin = User(username='admin', role=admin_role)
            admin.set_password('admin')
            admin.save()
            print(">>> Created Default Admin: admin/admin")

def clean_temp_files(app):
    """Deletes files in TEMP_FOLDER older than 24 hours."""
    folder = app.config.get('TEMP_FOLDER')
    if not folder or not os.path.exists(folder):
        return

    now = time.time()
    cutoff = now - (24 * 3600)

    print(f"Cleaning temp files in {folder}...")
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        if os.path.isfile(file_path):
            file_mtime = os.path.getmtime(file_path)
            if file_mtime < cutoff:
                try:
                    os.remove(file_path)
                    print(f"Deleted old temp file: {filename}")
                except Exception as e:
                    print(f"Error deleting {filename}: {e}")

def calculate_crooked_growth(total_a, days, step_hours, tolerance_pct):
    """
    Generates a timeline where 'a' varies per step but stays near the average.
    Returns: (timeline_list, final_total_a)
    """
    total_hours = days * 24
    num_steps = int(total_hours / step_hours)
    if num_steps < 1: num_steps = 1
    
    base_y = total_a / num_steps
    timeline = []
    final_total_a = 0
    used_values = set()

    for i in range(num_steps):
        tol_val = base_y * (tolerance_pct / 100.0)
        deviation = random.uniform(-tol_val, tol_val)
        val = int(base_y + deviation)
        if val < 1: val = 1
        
        attempts = 0
        while val in used_values and attempts < 5:
            val += random.choice([-1, 1])
            if val < 1: val = 1
            attempts += 1
        used_values.add(val)
        
        timeline.append({
            'step_index': i,
            'time_offset_hours': round(i * step_hours, 2),
            'amount': val,
            'comment': '',
            'status': 'Pending',
            'api_response': ''
        })
        final_total_a += val

    return timeline, final_total_a

def generate_thumbnail(video_path, output_path):
    """
    Extracts the first frame of a video using FFmpeg.
    Returns True if successful, False otherwise.
    """
    try:
        # Command: ffmpeg -i input.mp4 -ss 00:00:01 -vframes 1 output.jpg
        # -ss 1: Skip 1 second (avoid black frames at start)
        cmd = [
            'ffmpeg', 
            '-y', # Overwrite
            '-i', video_path,
            '-ss', '00:00:01', 
            '-vframes', '1',
            '-q:v', '5', # Quality (lower is better, 1-31)
            output_path
        ]
        # Run silently
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        return True
    except Exception as e:
        print(f"Thumbnail generation failed for {video_path}: {e}")
        return False