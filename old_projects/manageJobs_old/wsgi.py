import os
from dotenv import load_dotenv
from app import create_app

# --- 1. Load Environment Variables ---
# Get the folder where THIS file (wsgi.py) is located
project_folder = os.path.dirname(os.path.abspath(__file__))

# Load the .env file from that folder
load_dotenv(os.path.join(project_folder, '.env'))

# --- 2. Create Application ---
app = create_app()

if __name__ == "__main__":
    app.run()