import os
import re

def scan_and_fix_assets(root_dir):
    """
    Scans the project for deprecated 'images' folder references 
    and updates them to 'img'. Also fixes incorrect asset paths 
    found in server logs (favicon and default thumbnails) and 
    hardcoded strings in Python files.
    """
    # 1. Fix /static/images/ references
    deprecated_images_pattern = re.compile(r'/static/images/')
    images_replacement = '/static/img/'
    
    # 2. Fix broken default.png references seen in logs
    # Catching /media/default.png, /dashboard/default.png, etc.
    deprecated_media_pattern = re.compile(r'/(?:media|dashboard|auth|static)/default\.png')
    media_replacement = '/static/img/placeholder.png'

    # 3. Fix hardcoded "default.png" strings in Python files (Models/Blueprints)
    # Based on rg output: avatar = db.StringField(default="default.png"...)
    py_default_pattern = re.compile(r'["\']default\.png["\']')
    py_default_replacement = '"placeholder.png"'

    # 4. Fix favicon references
    # Replace any hardcoded /favicon.ico with the correct static path
    favicon_pattern = re.compile(r'href=["\']/(?:favicon\.ico|static/images/favicon\.svg)["\']')
    favicon_replacement = 'href="/static/img/favicon.svg"'
    
    # Extensions we want to scan
    target_extensions = ('.html', '.js', '.css', '.py')
    
    modified_files = []
    script_name = os.path.basename(__file__)

    print(f"--- Starting scan in: {root_dir} ---")

    for root, dirs, files in os.walk(root_dir):
        # Skip hidden folders and pycache
        if '.git' in root or '__pycache__' in root:
            continue
            
        for file in files:
            # IGNORE THIS SCRIPT to avoid self-modification loops
            if file == script_name:
                continue

            if file.endswith(target_extensions):
                file_path = os.path.join(root, file)
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    changed = False
                    new_content = content
                    
                    # Apply replacement logic for images folder
                    if deprecated_images_pattern.search(new_content):
                        new_content = deprecated_images_pattern.sub(images_replacement, new_content)
                        changed = True
                        
                    # Fix broken thumbnails/default images in URLs
                    if deprecated_media_pattern.search(new_content):
                        new_content = deprecated_media_pattern.sub(media_replacement, new_content)
                        changed = True

                    # Fix hardcoded "default.png" in Python logic
                    if file.endswith('.py') and py_default_pattern.search(new_content):
                        new_content = py_default_pattern.sub(py_default_replacement, new_content)
                        changed = True

                    # Fix favicon paths in HTML
                    if favicon_pattern.search(new_content):
                        new_content = favicon_pattern.sub(favicon_replacement, new_content)
                        changed = True
                    
                    # Special check for HTML files to ensure a favicon link exists
                    if file.endswith('.html') and '<head>' in new_content and 'favicon.svg' not in new_content:
                        # Use svg+xml for favicon.svg or just image/x-icon for favicon.ico
                        favicon_link = '\n    <link rel="icon" type="image/svg+xml" href="/static/img/favicon.svg">'
                        new_content = new_content.replace('<head>', f'<head>{favicon_link}')
                        changed = True
                    
                    if changed:
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(new_content)
                        
                        relative_path = os.path.relpath(file_path, root_dir)
                        print(f"[FIXED] {relative_path}")
                        modified_files.append(relative_path)
                        
                except Exception as e:
                    print(f"[ERROR] Could not process {file_path}: {e}")

    if not modified_files:
        print("No deprecated asset references found.")
    else:
        print(f"\n--- Scan Complete. Modified {len(modified_files)} files. ---")

if __name__ == "__main__":
    # Get the project root relative to this script location
    project_root = os.path.dirname(os.path.abspath(__file__))
    scan_and_fix_assets(project_root)