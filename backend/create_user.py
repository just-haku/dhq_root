from app.models.user import User
from mongoengine import connect
import hashlib
connect('dhq_db')
pw_hash = hashlib.sha256("password123".encode()).hexdigest()
u = User(username="admin", email="admin@test.com", password_hash=pw_hash, role="OP")
u.save()
print("Created OP user: admin / password123")
