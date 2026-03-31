from app.models.user import User
from app.core.security import verify_password
from mongoengine import connect

connect('dhq_db')
u = User.objects(username="admin").first()
if u:
    print(f"User: {u.username}, Status: {u.status}, Role: {u.role}")
    print(f"Password hash: {u.password_hash}")
    is_valid = verify_password("password123", u.password_hash)
    print(f"Password valid: {is_valid}")
else:
    print("User admin not found")
