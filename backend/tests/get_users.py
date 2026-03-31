from app.models.user import User
from mongoengine import connect
connect('dhq_db')
users = User.objects()
for u in users:
    print(f"User: {u.username} - Role: {u.role}")
