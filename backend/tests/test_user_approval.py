import requests
import json

BASE_URL = "http://localhost:8000"  # Assuming dev server port
AUTH_TOKEN = None
ADMIN_TOKEN = None

def test_user_flow():
    print("--- Starting User Approval Flow Test ---")
    
    # 1. Register a new user
    user_data = {
        "username": "testuser_" + str(int(requests.utils.time.time())),
        "password": "Password123!",
        "confirm_password": "Password123!",
        "display_name": "Test User",
        "email": f"test_{int(requests.utils.time.time())}@example.com",
        "otp": "123456" # Mock OTP if needed or bypass if possible
    }
    
    # Note: In a real test, you'd need a valid OTP from Redis or mock the check.
    # For this verification script, we assume the environment might need manual bypass or mock.
    print(f"User Data: {user_data['username']}")
    
    # 2. Try to login
    login_resp = requests.post(f"{BASE_URL}/shadow-garden/login", json={
        "username": user_data['username'],
        "password": user_data['password']
    })
    
    if login_resp.status_code == 401:
        print("PASS: Non-existent user cannot login.")
    
    # 3. List users as Admin
    # ... assuming we have admin creds ...
    admin_login = requests.post(f"{BASE_URL}/shadow-garden/login", json={
        "username": "kuro",
        "password": "00491E4C"
    })
    
    if admin_login.status_code == 200:
        admin_data = admin_login.json()
        print("PASS: Admin logged in.")
        # If it was a real admin login without OTP
        if 'access_token' in admin_data:
            token = admin_data['access_token']
            
            # List users
            users_resp = requests.get(f"{BASE_URL}/api/user/admin/users", headers={"Authorization": f"Bearer {token}"})
            if users_resp.status_code == 200:
                print(f"PASS: Listed {len(users_resp.json()['users'])} users.")
            else:
                print(f"FAIL: Could not list users. Status: {users_resp.status_code}")
        else:
            print("INFO: Admin login requires OTP in this environment.")

if __name__ == "__main__":
    # This is a template script. Actual execution might require running server.
    print("Verification script template ready.")
