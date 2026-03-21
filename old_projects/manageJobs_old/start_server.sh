#!/bin/bash

# --- CONFIGURATION ---
PROJECT_DIR="/home/haku/projects/manageJobs"
USB_DIR="/home/haku/storage/manageJobs"
VENV_DIR="$PROJECT_DIR/../kuro"
DOMAIN="haku.servegame.com"
GUNICORN_WORKERS=2
GUNICORN_THREADS=4
PORT=${PORT:-8000}

# Stop execution on any error
set -e

# --- FUNCTIONS ---
check_dependencies() {
    echo ">>> [3/6] Verifying Dependencies..."
    MISSING_DEPS=0
    if ! command -v gunicorn &> /dev/null; then MISSING_DEPS=1; fi
    if ! python3 -c "import flask, pymongo, dotenv" 2>/dev/null; then MISSING_DEPS=1; fi
    
    if [ $MISSING_DEPS -eq 1 ]; then
        echo "    - Installing dependencies..."
        if [ -f "requirements.txt" ]; then
            pip install -r requirements.txt; pip install gunicorn
        else
            echo "ERROR: requirements.txt missing!"; exit 1
        fi
    fi
}

setup_network() {
    echo ">>> [4/6] Configuring Network..."

    # 1. Check for Nginx Conflict
    if pgrep nginx > /dev/null; then
        echo "    ! WARNING: Nginx is running."
        echo "    ! If Nginx is proxying to port $PORT, you do NOT need iptables."
        echo "    ! This script will proceed, but iptables might conflict with Nginx."
    fi

    # 2. Check for SSL Certificates (Auto-Detect)
    CERT_PATH="/etc/letsencrypt/live/$DOMAIN/fullchain.pem"
    KEY_PATH="/etc/letsencrypt/live/$DOMAIN/privkey.pem"
    
    if sudo test -f "$CERT_PATH" && sudo test -f "$KEY_PATH"; then
        echo "    - SSL Certificates FOUND for $DOMAIN."
        export USE_SSL=1
        export GUNICORN_CERT_ARGS="--certfile=$CERT_PATH --keyfile=$KEY_PATH"
        
        # SSL MODE: Redirect 443 -> 8000
        if command -v iptables &> /dev/null; then
            # CRITICAL: Remove stale Port 80 forwarding if it exists.
            # Forwarding HTTP (80) to HTTPS (8000) causes [SSL: HTTP_REQUEST] errors.
            if sudo iptables -t nat -C PREROUTING -p tcp --dport 80 -j REDIRECT --to-port $PORT 2>/dev/null; then
                 echo "    - Removing conflicting Port 80 -> $PORT forwarding..."
                 sudo iptables -t nat -D PREROUTING -p tcp --dport 80 -j REDIRECT --to-port $PORT
            fi

            echo "    - SSL MODE: Forwarding Port 443 -> $PORT..."
            sudo iptables -t nat -C PREROUTING -p tcp --dport 443 -j REDIRECT --to-port $PORT 2>/dev/null || \
            sudo iptables -t nat -A PREROUTING -p tcp --dport 443 -j REDIRECT --to-port $PORT
        fi
    else
        echo "    - SSL Certificates NOT found (or no permission). Using HTTP."
        export USE_SSL=0
        export GUNICORN_CERT_ARGS=""
        
        # HTTP MODE: Redirect 80 -> 8000
        if command -v iptables &> /dev/null; then
            echo "    - HTTP MODE: Forwarding Port 80 -> $PORT..."
            sudo iptables -t nat -C PREROUTING -p tcp --dport 80 -j REDIRECT --to-port $PORT 2>/dev/null || \
            sudo iptables -t nat -A PREROUTING -p tcp --dport 80 -j REDIRECT --to-port $PORT
        fi
    fi
}

echo "-----------------------------------------------------"
echo " SYSTEM CHECK"
echo "-----------------------------------------------------"

echo ">>> [1/6] Checking USB Mount at $USB_DIR..."
if [ ! -d "$USB_DIR" ]; then echo "ERROR: USB directory missing"; exit 1; fi
mkdir -p "$USB_DIR/db" "$USB_DIR/videos" "$USB_DIR/images" "$USB_DIR/media" "$USB_DIR/temp"

# --- ENVIRONMENT SETUP ---
cd "$PROJECT_DIR"
echo ">>> [2/6] Checking Virtual Environment..."
if [ ! -f "$VENV_DIR/bin/activate" ]; then python3 -m venv "$VENV_DIR"; fi
source "$VENV_DIR/bin/activate"

check_dependencies
setup_network

# --- CLEANUP OLD PROCESSES ---
echo ">>> Checking Port $PORT..."
if lsof -i :$PORT > /dev/null 2>&1; then
    fuser -k -n tcp $PORT > /dev/null 2>&1 || true; sleep 1
fi

# --- DATABASE INIT ---
echo ">>> [5/6] Initializing Database..."
export PROJECT_DIR="$PROJECT_DIR"
python3 -c "from app import create_app; create_app(); print('    - DB Verified.')"

# --- START SERVER ---
echo "-----------------------------------------------------"
echo ">>> SERVER ONLINE <<<"
MY_IP=$(hostname -I | awk '{print $1}')
if [ "$USE_SSL" -eq "1" ]; then
    echo "Mode:    HTTPS (Secure)"
    echo "Address: https://$MY_IP/ (Local) or https://$DOMAIN/ (Public)"
    echo "WARNING: You MUST use 'https://' locally. You will see a security warning."
    echo "         Port 80 (HTTP) is disabled to prevent SSL errors."
else
    echo "Mode:    HTTP (Plain)"
    echo "Address: http://$MY_IP/"
fi
echo "Venv:    $VENV_DIR"
echo "-----------------------------------------------------"

GUNICORN_BIN="$VENV_DIR/bin/gunicorn"
[ ! -f "$GUNICORN_BIN" ] && GUNICORN_BIN="gunicorn"

exec sudo "$GUNICORN_BIN" -w $GUNICORN_WORKERS --threads $GUNICORN_THREADS \
    -b 0.0.0.0:$PORT \
    $GUNICORN_CERT_ARGS \
    "run:app" \
    --worker-class gthread \
    --timeout 120 \
    --keep-alive 5 \
    --access-logfile - \
    --error-logfile - \
    --log-level info