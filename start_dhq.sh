#!/bin/bash

# =============================================================================
# 🚀 DHQ Quick Start Script
# =============================================================================
# Simple script to start DHQ services with proper configuration
# =============================================================================

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo -e "${BLUE}🚀 Starting DHQ Digital Headquarters${NC}"
echo "=================================="

# Function to check if port is in use
check_port() {
    local port=$1
    if ss -tlnp | grep -q ":$port "; then
        echo -e "${YELLOW}Port $port is already in use${NC}"
        return 0
    else
        echo -e "${GREEN}Port $port is available${NC}"
        return 1
    fi
}

# Function to wait for service
wait_for_service() {
    local port=$1
    local service=$2
    local max_attempts=30
    local attempt=1
    
    echo -e "${BLUE}Waiting for $service to start on port $port...${NC}"
    
    while [ $attempt -le $max_attempts ]; do
        if ss -tlnp | grep -q ":$port "; then
            echo -e "${GREEN}✅ $service is running!${NC}"
            return 0
        fi
        sleep 2
        attempt=$((attempt + 1))
    done
    
    echo -e "${YELLOW}⚠️  $service failed to start within timeout${NC}"
    return 1
}

# Check if services are already running
echo "Checking existing services..."
if check_port 8000 || check_port 8001 || check_port 3001; then
    echo -e "${YELLOW}Some services are already running. Stopping them first...${NC}"
    pkill -f "python app/main.py" || true
    pkill -f "run_socketio.py" || true
    pkill -f "npm run dev" || true
    pkill -f "vite" || true
    sleep 3
fi

# Start Backend
echo -e "${BLUE}🔧 Starting Backend (FastAPI)...${NC}"
cd "$SCRIPT_DIR/backend"
if [ ! -d "/home/haku/projects/venv/DHQ_Root" ]; then
    echo -e "${YELLOW}⚠️  Virtual environment not found. Creating...${NC}"
    python -m venv /home/haku/projects/venv/DHQ_Root
    source /home/haku/projects/venv/DHQ_Root/bin/activate
    pip install -r requirements.txt
fi

nohup bash -c "source /home/haku/projects/venv/DHQ_Root/bin/activate && PYTHONPATH=$SCRIPT_DIR/backend python app/main.py" > "$SCRIPT_DIR/logs/backend.log" 2>&1 &
wait_for_service 8000 "Backend"

# Start Socket.IO
echo -e "${BLUE}🔌 Starting Socket.IO Server...${NC}"
cd "$SCRIPT_DIR/backend"
nohup bash -c "source /home/haku/projects/venv/DHQ_Root/bin/activate && PYTHONPATH=$SCRIPT_DIR/backend python run_socketio.py" > "$SCRIPT_DIR/logs/socketio.log" 2>&1 &
wait_for_service 8001 "Socket.IO"

# Start Frontend
echo -e "${BLUE}🎨 Starting Frontend (Vue.js)...${NC}"
cd "$SCRIPT_DIR/frontend"
if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}Installing frontend dependencies...${NC}"
    npm install
fi

nohup npm run dev -- --host 0.0.0.0 > "$SCRIPT_DIR/logs/frontend.log" 2>&1 &
wait_for_service 3001 "Frontend"

# Final status
echo ""
echo -e "${GREEN}🎉 DHQ Digital Headquarters is now running!${NC}"
echo "=============================================="
echo -e "🌐 Frontend:      ${GREEN}http://localhost:3001${NC}"
echo -e "🔧 Backend API:   ${GREEN}http://localhost:8000${NC}"
echo -e "📚 API Docs:      ${GREEN}http://localhost:8000/docs${NC}"
echo -e "🔌 Socket.IO:     ${GREEN}http://localhost:8001${NC}"
echo -e "🌍 Domain:        ${GREEN}https://haku.io.vn${NC}"
echo ""

# Read credentials
ENV_FILE="$SCRIPT_DIR/backend/.env"
if [ -f "$ENV_FILE" ]; then
    OP_USER=$(grep "^OP_INIT_USER=" "$ENV_FILE" | cut -d'=' -f2 | tr -d '"' | tr -d "'")
    if [ ! -z "$OP_USER" ]; then
        echo -e "👤 Default login: ${GREEN}$OP_USER${NC} / [SECURE] + OTP"
    fi
else
    echo -e "👤 Default login: ${GREEN}kuro${NC} / [SECURE] + OTP"
fi

echo ""
echo -e "${BLUE}📋 Useful commands:${NC}"
echo -  "./dhq_manager.sh status     # Check service status"
echo -  "./dhq_manager.sh logs       # View logs"
echo -  "./dhq_manager.sh stop       # Stop all services"
echo -  "./dhq_manager.sh test-all   # Run all tests"
echo ""
echo -e "${GREEN}✅ All services started successfully!${NC}"
