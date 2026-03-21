from app.models.user import User
from mongoengine import connect
import hashlib

connect('dhq_db')
u = User.objects(username="admin").first()
if u:
    u.status = "ACTIVE"
    u.save()
    print("Updated admin user status to ACTIVE")
else:
    print("User admin not found")
