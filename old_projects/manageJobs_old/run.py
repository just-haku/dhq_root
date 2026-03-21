import os
from app import create_app
from dotenv import load_dotenv

# Load environment variables
project_dir = os.environ.get('PROJECT_DIR', os.getcwd())
load_dotenv(os.path.join(project_dir, '.env'))

# Configuration Mapping
config = {
    'SECRET_KEY': os.environ.get('SECRET_KEY', 'dev_key_change_me'),
    'MONGODB_SETTINGS': {
        'db': os.environ.get('MONGODB_DB', 'managejobs_db'),
        'host': os.environ.get('MONGODB_HOST', 'localhost'),
        'port': int(os.environ.get('MONGODB_PORT', 27017))
    },
    # Use environment vars or default to the haku paths
    'USB_DIR': os.environ.get('USB_DIR', '/home/haku/storage/manageJobs'),
    'UPLOAD_FOLDER': os.path.join(os.environ.get('USB_DIR', '/home/haku/storage/manageJobs'), 'media'),
    'TEMP_FOLDER': os.path.join(os.environ.get('USB_DIR', '/home/haku/storage/manageJobs'), 'temp'),
    'VIRUSTOTAL_API_KEY': os.environ.get('VIRUSTOTAL_API_KEY', '')
}

app = create_app(config)

if __name__ == '__main__':
    # Fetch PORT from environment, default to 8000 if missing
    port = int(os.environ.get('PORT', 8000))
    
    # Fetch debug mode (looks for '1', 'True', or 'true')
    debug_val = os.environ.get('FLASK_DEBUG', '0')
    debug_mode = debug_val in ['1', 'True', 'true']
    
    print(f"Starting server on port {port} (Debug: {debug_mode})...")
    app.run(host='0.0.0.0', port=port, debug=debug_mode)