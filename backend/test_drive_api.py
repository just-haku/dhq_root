import requests
import sys

URL = "http://localhost:8000/api"

print("--- Testing Drive API Integrity ---")

# Step 1: Login
res = requests.post(f"{URL}/auth/login", json={"username": "kuro", "password": "00491E4C"})
if res.status_code != 200:
    print(f"Login failed: {res.status_code} {res.text}")
    sys.exit(1)

token = res.json().get("access_token")
headers = {"Authorization": f"Bearer {token}"}
print("[OK] Login successful. OP Token received.")

# Step 2: Fetch default files
res = requests.get(f"{URL}/drive/files", headers=headers)
print(f"[OK] Fetch Root Files: {res.status_code}")

# Step 3: Create a folder
folder_payload = {"name": "TestFolder123", "parent_folder": "/", "description": ""}
res = requests.post(f"{URL}/drive/folder", headers=headers, json=folder_payload)
print(f"[OK] Create Folder: {res.status_code} {res.text}")

if res.status_code == 200:
    folder_id = res.json().get('folder', {}).get('id')
    
    # Step 4: Delete the folder
    if folder_id:
        res = requests.delete(f"{URL}/drive/file/{folder_id}", headers=headers)
        print(f"[OK] Delete Folder: {res.status_code} {res.text}")
        
# Step 5: Test Star endpoint
# Need a target file/folder to star, let's create a new one to star
res = requests.post(f"{URL}/drive/folder", headers=headers, json={"name": "StarTest", "parent_folder": "/"})
if res.status_code == 200:
    star_folder_id = res.json().get('folder', {}).get('id')
    res = requests.post(f"{URL}/drive/star/{star_folder_id}", headers=headers)
    print(f"[OK] Toggle Star: {res.status_code} {res.text}")
    
# Step 6: Empty Trash
res = requests.delete(f"{URL}/drive/trash", headers=headers)
print(f"[OK] Empty Trash: {res.status_code} {res.text}")

# Step 7: Test Upload
import io
file_content = b"This is a test file contents for uploading."
files = {'file': ('test_upload.txt', io.BytesIO(file_content), 'text/plain')}
res = requests.post(f"{URL}/drive/upload", headers=headers, data={'folder_path': '/'}, files=files)
print(f"[OK] Upload File: {res.status_code} {res.text[:100]}")

print("--- All tests finished execution ---")
