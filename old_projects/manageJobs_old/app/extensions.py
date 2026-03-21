import os
from flask_mongoengine import MongoEngine
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
import vt

# Initialize MongoEngine
# This allows us to use db.Document, db.StringField, etc.
db = MongoEngine()

# Initialize Login Manager
login_manager = LoginManager()
csrf = CSRFProtect()
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'info'

# Initialize CSRF Protection
csrf = CSRFProtect()

# VirusTotal Client Helper
def get_vt_client():
    api_key = os.environ.get('VT_API_KEY')
    if not api_key:
        return None
    return vt.Client(api_key)

def init_extensions(app):
    # MongoDB Config for MongoEngine
    # If MONGODB_SETTINGS is not set, it defaults to localhost:27017/test
    if not app.config.get("MONGODB_SETTINGS"):
        app.config["MONGODB_SETTINGS"] = {
            'host': os.environ.get('MONGO_URI', 'mongodb://localhost:27017/manageJobsDB')
        }
    
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    # Login Manager user loader
    @login_manager.user_loader
    def load_user(user_id):
        from app.models import User
        try:
            return User.objects.get(id=user_id)
        except Exception:
            return None