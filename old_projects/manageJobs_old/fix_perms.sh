#!/bin/bash

# --- LUCKFOX / LINUX PERMISSION FIXER ---
# This script ensures the web server (www-data/nginx) can read your static files.

USER="haku"
PROJECT_DIR="/home/$USER/project"
USB_DIR="/home/$USER/usb"

echo ">>> 1. Unblocking Directory Traversal..."
# Allow 'others' (the web server) to traverse (x) the path to your project
# They cannot write, only pass through to get to the static folder.
sudo chmod o+x /home
sudo chmod o+x /home/$USER
sudo chmod o+x /home/$USER/project

echo ">>> 2. Setting Static Asset Permissions..."
# Static files must be Readable (r) and Executable (x - for directories) by everyone
sudo chmod -R 755 "$PROJECT_DIR/static"
sudo chmod -R 755 "$PROJECT_DIR/templates"

echo ">>> 3. Setting Ownership..."
# Ensure you (haku) own the files so you can still edit them
sudo chown -R $USER:$USER "$PROJECT_DIR"

echo ">>> 4. USB Storage Permissions..."
# Ensure the USB mount is accessible for database and media storage
if [ -d "$USB_DIR" ]; then
    sudo chmod -R 775 "$USB_DIR"
    sudo chown -R $USER:$USER "$USB_DIR"
    echo "    USB permissions updated."
else
    echo "    [WARN] USB directory not found at $USB_DIR"
fi

echo ">>> DONE. Try refreshing the clock page."