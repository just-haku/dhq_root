import os
from flask import Flask, send_from_directory, session
from datetime import timedelta
from .extensions import db, login_manager, csrf

# Try to import create_default_admin, but handle gracefully if utils isn't updated
"""
try:
    from .utils import create_default_admin
except ImportError:
    def create_default_admin(): pass
"""

def create_app(config=None):
    app = Flask(__name__)

    # Load configuration from the config.py file
    app.config.from_object('config.Config')

    # --- 1. CONFIGURATION ---
    # Load config passed from run.py (Environment variables & Paths)
    if config:
        app.config.update(config)

    # Defaults/Fallbacks
    app.config.setdefault('SECRET_KEY', os.environ.get('SECRET_KEY', 'luckfox_kuro_secret_key_CHANGE_IN_PROD'))
    app.config.setdefault('PERMANENT_SESSION_LIFETIME', timedelta(minutes=30))
    
    # MongoDB Config
    # MongoEngine looks for 'MONGODB_SETTINGS'
    if 'MONGODB_SETTINGS' not in app.config:
        app.config['MONGODB_SETTINGS'] = {
            'host': os.environ.get('MONGO_URI', 'mongodb://localhost:27017/manageJobsDB')
        }

    # Upload Configuration (Moved to Env)
    # Default: 16MB
    app.config['MAX_CONTENT_LENGTH'] = int(os.environ.get('MAX_CONTENT_LENGTH', 16 * 1024 * 1024))
    # Default: Common image types
    app.config['ALLOWED_EXTENSIONS'] = set(os.environ.get('ALLOWED_EXTENSIONS', 'png,jpg,jpeg,gif,pdf,txt,doc,docx').split(','))

    # Ensure critical directories exist
    # If UPLOAD_FOLDER is not in config, set a default inside static
    if not app.config.get('UPLOAD_FOLDER'):
        app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static', 'uploads')

    upload_folder = app.config['UPLOAD_FOLDER']
    os.makedirs(upload_folder, exist_ok=True)
    os.makedirs(os.path.join(upload_folder, 'avatars'), exist_ok=True)
    os.makedirs(os.path.join(upload_folder, 'shop'), exist_ok=True)
    os.makedirs(os.path.join(upload_folder, 'temp'), exist_ok=True) # For temp scan files
    
    from app.models import User

    @login_manager.user_loader
    def load_user(user_id):
        try:
            return User.objects(pk=user_id).first()
        except Exception:
            return None

    # --- 2. EXTENSIONS ---
    db.init_app(app)
    login_manager.init_app(app)
    # Note: Ensure csrf is defined in app/extensions.py
    if csrf:
        csrf.init_app(app)

    # --- 3. CUSTOM ASSET ROUTES ---
    @app.route('/avatars/<path:filename>')
    def serve_avatar(filename):
        return send_from_directory(os.path.join(app.config['UPLOAD_FOLDER'], 'avatars'), filename)

    @app.route('/shop_assets/<path:filename>')
    def serve_shop_asset(filename):
        return send_from_directory(os.path.join(app.config['UPLOAD_FOLDER'], 'shop'), filename)
    
    @app.before_request
    def make_session_permanent():
        session.permanent = True

    # --- 4. REGISTER BLUEPRINTS ---
    # Using relative imports since we are inside the package
    try:
        from .blueprints.auth import auth_bp
        app.register_blueprint(auth_bp)
    except ImportError as e:
        print(f"Warning: 'auth' blueprint failed to import: {e}")

    try:
        from .blueprints.dashboard import dashboard_bp
        app.register_blueprint(dashboard_bp)
    except ImportError: pass

    try:
        from .blueprints.admin import admin_bp
        app.register_blueprint(admin_bp)
    except ImportError: pass

    try:
        from .blueprints.scan import scan_bp
        app.register_blueprint(scan_bp)
    except ImportError: pass

    try:
        from .blueprints.media import media_bp
        app.register_blueprint(media_bp)
    except ImportError: pass

    try:
        from .blueprints.clock import clock_bp
        app.register_blueprint(clock_bp)
    except ImportError: pass

    try:
        from .blueprints.orders import orders_bp
        app.register_blueprint(orders_bp)
    except ImportError: pass

    try:
        from .blueprints.shop import shop_bp
        app.register_blueprint(shop_bp)
    except ImportError: pass
    
    try:
        from .blueprints.maintenance import maintenance_bp
        app.register_blueprint(maintenance_bp)
    except ImportError: pass

    # --- 5. DATABASE INIT ---
    """
    with app.app_context():
        try:
            try:
                create_default_admin()
            except Exception as ex:
                pass
            
            # 2. Create Operator Account
            create_operator_account()
            
        except Exception as e:
            print(f"Startup maintenance skipped: {e}")
    """

    # --- 6. CLI COMMANDS ---
    from app.commands import init_db
    app.cli.add_command(init_db)
    
    # --- Auto-Create Operator on Startup ---
    with app.app_context():
        try:
            # Import the function from the script (make sure script is in a module or valid path)
            # OR define the logic directly here or in app/utils.py
            from create_operator import create_operator
            create_operator()
        except Exception as e:
            print(f"Startup Operator Check Failed: {e}")
            
    return app

def create_operator_account():
    """Creates the operator account using env vars."""
    from .models import User, Role
    
    # Get credentials from env or fallback to defaults
    op_user = os.environ.get('OPERATOR_USERNAME', 'kuro')
    op_pass = os.environ.get('OPERATOR_PASSWORD', '00491E4C')
    op_email = os.environ.get('OPERATOR_EMAIL', 'kuro@localhost.local')

    # Check if operator exists
    if not User.objects(username=op_user).first():
        print(f">>> Creating Operator Account: {op_user}")
        
        # Ensure operator role exists
        op_role = Role.objects(name='operator').first()
        if not op_role:
            op_role = Role(name='operator', permissions=['all', 'operator'])
            op_role.save()

        # Create User
        op = User(
            username=op_user, 
            role=op_role,
            email=op_email, 
            status='active'
        )
        op.set_password(op_pass) 
        op.save()
        print(f"Operator '{op_user}' created.")