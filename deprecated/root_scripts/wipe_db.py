from app.models.drive import DriveFile, DriveQuota
from mongoengine import connect
import os
from dotenv import load_dotenv

load_dotenv('.env')
connect('kuro_server', host=os.getenv('MONGODB_URI', 'mongodb://localhost:27017/kuro_server'))

print(f'Deleted files: {DriveFile.objects.delete()}')
print(f'Deleted quotas: {DriveQuota.objects.delete()}')
