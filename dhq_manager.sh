#!/bin/bash

# =============================================================================
# 🚀 DHQ Digital Headquarters - Unified Management Script
# =============================================================================
# This script consolidates all DHQ management functions into one comprehensive tool
# =============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${PURPLE}$1${NC}"
}

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$SCRIPT_DIR/backend"
FRONTEND_DIR="$SCRIPT_DIR/frontend"

# Create logs directory
mkdir -p "$SCRIPT_DIR/logs"

# Function to check if service is running
check_service() {
    local service_name=$1
    local port=$2
    
    if ss -tlnp | grep -q ":$port "; then
        return 0
    fi
    return 1
}

# Function to check if a system port is open
check_system_port() {
    local port=$1
    if (echo > /dev/tcp/127.0.0.1/$port) >/dev/null 2>&1; then
        return 0
    fi
    return 1
}

# Function to wait for service
wait_for_service() {
    local service_name=$1
    local port=$2
    local max_attempts=30
    local attempt=1
    
    print_status "Waiting for $service_name to start on port $port..."
    
    while [ $attempt -le $max_attempts ]; do
        if ss -tlnp | grep -q ":$port "; then
            print_success "$service_name is running on port $port"
            return 0
        fi
        
        sleep 2
        attempt=$((attempt + 1))
    done
    
    print_error "$service_name failed to start within timeout"
    return 1
}

# Function to kill existing services
cleanup_services() {
    print_status "Cleaning up existing services..."
    
    pkill -f "python app/main.py" || true
    pkill -f "run_socketio.py" || true
    pkill -f "npm run dev" || true
    pkill -f "vite" || true
    
    sleep 2
    print_success "Cleanup completed"
}

# Function to start backend
start_backend() {
    print_status "Starting DHQ Backend..."
    
    cd "$BACKEND_DIR"
    
    if [ ! -d "/home/haku/projects/venv/DHQ_Root" ]; then
        print_error "Virtual environment not found at /home/haku/projects/venv/DHQ_Root"
        print_status "Please create virtual environment first:"
        print_status "  python -m venv /home/haku/projects/venv/DHQ_Root"
        print_status "  source /home/haku/projects/venv/DHQ_Root/bin/activate"
        print_status "  pip install -r requirements.txt"
        exit 1
    fi
    
    nohup bash -c "source /home/haku/projects/venv/DHQ_Root/bin/activate && PYTHONPATH=$BACKEND_DIR python app/main.py" > "$SCRIPT_DIR/logs/backend.log" 2>&1 &
    BACKEND_PID=$!
    echo $BACKEND_PID > "$SCRIPT_DIR/logs/backend.pid"
    
    wait_for_service "Backend" 8000
}

# Function to start Socket.IO server
start_socketio() {
    print_status "Starting DHQ Socket.IO Server..."
    
    cd "$BACKEND_DIR"
    
    nohup bash -c "source /home/haku/projects/venv/DHQ_Root/bin/activate && PYTHONPATH=$BACKEND_DIR python run_socketio.py" > "$SCRIPT_DIR/logs/socketio.log" 2>&1 &
    SOCKETIO_PID=$!
    echo $SOCKETIO_PID > "$SCRIPT_DIR/logs/socketio.pid"
    
    wait_for_service "Socket.IO" 8001
}

# Function to start frontend
start_frontend() {
    print_status "Starting DHQ Frontend..."
    
    cd "$FRONTEND_DIR"
    
    if [ ! -d "node_modules" ]; then
        print_status "Installing frontend dependencies..."
        npm install
    fi
    
    nohup npm run dev -- --host 0.0.0.0 > "$SCRIPT_DIR/logs/frontend.log" 2>&1 &
    FRONTEND_PID=$!
    echo $FRONTEND_PID > "$SCRIPT_DIR/logs/frontend.pid"
    
    wait_for_service "Frontend" 3001
}

# Function to show status
show_status() {
    print_header "🚀 DHQ Service Status:"
    echo "================================"
    
    if check_service "Backend" 8000; then
        echo -e "Backend (FastAPI): ${GREEN}RUNNING${NC} on http://localhost:8000"
    else
        echo -e "Backend (FastAPI): ${RED}STOPPED${NC}"
    fi
    
    if check_service "Socket.IO" 8001; then
        echo -e "Socket.IO Server: ${GREEN}RUNNING${NC} on http://localhost:8001"
    else
        echo -e "Socket.IO Server: ${RED}STOPPED${NC}"
    fi
    
    if check_service "Frontend" 3001; then
        echo -e "Frontend (Vue.js): ${GREEN}RUNNING${NC} on http://localhost:3001"
    else
        echo -e "Frontend (Vue.js): ${RED}STOPPED${NC}"
    fi
    
    echo "================================"
    print_status "Log files available at: $SCRIPT_DIR/logs/"
}

# Function to stop services
stop_services() {
    print_status "Stopping DHQ services..."
    
    if [ -f "$SCRIPT_DIR/logs/backend.pid" ]; then
        kill $(cat "$SCRIPT_DIR/logs/backend.pid") 2>/dev/null || true
        rm "$SCRIPT_DIR/logs/backend.pid"
    fi
    
    if [ -f "$SCRIPT_DIR/logs/socketio.pid" ]; then
        kill $(cat "$SCRIPT_DIR/logs/socketio.pid") 2>/dev/null || true
        rm "$SCRIPT_DIR/logs/socketio.pid"
    fi
    
    if [ -f "$SCRIPT_DIR/logs/frontend.pid" ]; then
        kill $(cat "$SCRIPT_DIR/logs/frontend.pid") 2>/dev/null || true
        rm "$SCRIPT_DIR/logs/frontend.pid"
    fi
    
    cleanup_services
    print_success "All services stopped"
}

# Function to show logs
show_logs() {
    local service=$1
    
    case $service in
        backend)
            tail -f "$SCRIPT_DIR/logs/backend.log"
            ;;
        socketio)
            tail -f "$SCRIPT_DIR/logs/socketio.log"
            ;;
        frontend)
            tail -f "$SCRIPT_DIR/logs/frontend.log"
            ;;
        all)
            print_status "Showing all logs (use Ctrl+C to exit):"
            tail -f "$SCRIPT_DIR/logs"/*.log
            ;;
        *)
            print_error "Unknown service: $service"
            print_status "Available services: backend, socketio, frontend, all"
            exit 1
            ;;
    esac
}

# Function to run health checks
health_check() {
    print_header "🏥 DHQ Health Check"
    echo "========================"
    
    # Check backend
    if curl -s http://localhost:8000/health >/dev/null 2>&1; then
        print_success "Backend health check: OK"
    else
        print_error "Backend health check: FAILED"
    fi
    
    # Check frontend
    if curl -s http://localhost:3001 >/dev/null 2>&1; then
        print_success "Frontend health check: OK"
    else
        print_error "Frontend health check: FAILED"
    fi
    
    # Check MongoDB
    if mongosh --eval "db.adminCommand('ping')" >/dev/null 2>&1; then
        print_success "MongoDB health check: OK"
    else
        print_error "MongoDB health check: FAILED"
    fi
    
    # Check Redis
    if redis-cli ping >/dev/null 2>&1; then
        print_success "Redis health check: OK"
    else
        print_error "Redis health check: FAILED"
    fi
}

# Function to initialize OP user
init_op() {
    print_status "Initializing OP user..."
    
    cd "$BACKEND_DIR"
    
    if bash -c "source /home/haku/projects/venv/DHQ_Root/bin/activate && PYTHONPATH=$BACKEND_DIR python init_op.py"; then
        print_success "OP user initialized successfully"
    else
        print_error "Failed to initialize OP user"
    fi
}

# Function to test complete system
test_complete() {
    print_header "🎯 DHQ Complete System Test"
    echo "==============================="
    
    # Test 1: Service Health Check
    echo -e "${BLUE}Test 1: Service Health Check${NC}"
    if curl -s http://localhost:3001 >/dev/null 2>&1; then
        echo -e "${GREEN}   ✅ Frontend running (Port 3001)${NC}"
    else
        echo -e "${RED}   ❌ Frontend not running${NC}"
        return 1
    fi

    if curl -s http://localhost:8000/health >/dev/null 2>&1; then
        echo -e "${GREEN}   ✅ Backend running (Port 8000)${NC}"
    else
        echo -e "${RED}   ❌ Backend not running${NC}"
        return 1
    fi

    # Test 2: OP Login
    echo -e "${BLUE}Test 2: OP Login Test${NC}"
    ENV_FILE="$BACKEND_DIR/.env"
    if [ -f "$ENV_FILE" ]; then
        OP_USER=$(grep "^OP_INIT_USER=" "$ENV_FILE" | cut -d'=' -f2 | tr -d '"' | tr -d "'")
        OP_PASS=$(grep "^OP_INIT_PASS=" "$ENV_FILE" | cut -d'=' -f2 | tr -d '"' | tr -d "'")
    else
        OP_USER="kuro"
        OP_PASS="00491E4C"
    fi

    LOGIN_RESPONSE=$(curl -s -X POST http://localhost:8000/api/auth/login \
        -H "Content-Type: application/json" \
        -d "{\"username\": \"$OP_USER\", \"password\": \"$OP_PASS\"}" 2>/dev/null || echo "")

    if [[ "$LOGIN_RESPONSE" == *"access_token"* ]]; then
        echo -e "${GREEN}   ✅ OP login successful${NC}"
        TOKEN=$(echo "$LOGIN_RESPONSE" | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)
    else
        echo -e "${RED}   ❌ OP login failed${NC}"
        return 1
    fi

    # Test 3: API Calls
    echo -e "${BLUE}Test 3: API Functionality${NC}"
    
    # Test KPI Bonus API
    KPI_RESPONSE=$(curl -s -H "Authorization: Bearer $TOKEN" \
        http://localhost:8000/api/kpi-bonus/dashboard 2>/dev/null || echo "")
    if [[ "$KPI_RESPONSE" == *"current_kpi"* ]]; then
        echo -e "${GREEN}   ✅ KPI Bonus API working${NC}"
    else
        echo -e "${RED}   ❌ KPI Bonus API failed${NC}"
    fi

    # Test Memory Allocation API
    MEMORY_RESPONSE=$(curl -s -H "Authorization: Bearer $TOKEN" \
        http://localhost:8000/api/user/memory-allocations 2>/dev/null || echo "")
    if [[ "$MEMORY_RESPONSE" == *"allocations"* ]]; then
        echo -e "${GREEN}   ✅ Memory Allocation API working${NC}"
    else
        echo -e "${RED}   ❌ Memory Allocation API failed${NC}"
    fi

    print_success "Complete system test finished!"
}

# Function to test login specifically
test_login() {
    print_header "🔑 DHQ Login Test"
    echo "===================="
    
    ENV_FILE="$BACKEND_DIR/.env"
    if [ -f "$ENV_FILE" ]; then
        OP_USER=$(grep "^OP_INIT_USER=" "$ENV_FILE" | cut -d'=' -f2 | tr -d '"' | tr -d "'")
        OP_PASS=$(grep "^OP_INIT_PASS=" "$ENV_FILE" | cut -d'=' -f2 | tr -d '"' | tr -d "'")
    else
        OP_USER="kuro"
        OP_PASS="00491E4C"
    fi

    echo -e "${YELLOW}📋 Testing OP Login:${NC}"
    echo -e "${YELLOW}   Username: $OP_USER${NC}"
    echo -e "${YELLOW}   Password: [SECURE]${NC}"
    echo ""

    # Test backend health
    if ! curl -s http://localhost:8000/health >/dev/null 2>&1; then
        print_error "Backend is not running"
        return 1
    fi

    # Test login
    LOGIN_RESPONSE=$(curl -s -X POST http://localhost:8000/api/auth/login \
        -H "Content-Type: application/json" \
        -d "{\"username\": \"$OP_USER\", \"password\": \"$OP_PASS\"}" 2>/dev/null || echo "")

    if [[ "$LOGIN_RESPONSE" == *"access_token"* ]]; then
        print_success "OP Login successful!"
        TOKEN=$(echo "$LOGIN_RESPONSE" | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)
        
        # Verify token
        VERIFY_RESPONSE=$(curl -s -H "Authorization: Bearer $TOKEN" \
            http://localhost:8000/api/auth/me 2>/dev/null || echo "")
        
        if [[ "$VERIFY_RESPONSE" == *"username"* ]]; then
            print_success "Token verification successful"
        else
            print_error "Token verification failed"
        fi
    else
        print_error "OP Login failed"
        return 1
    fi

    print_success "Login test completed successfully!"
}

# Function to test dashboard loading
test_dashboard() {
    print_header "📊 DHQ Dashboard Load Test"
    echo "=============================="
    
    # Test frontend
    if ! curl -s http://localhost:3001 >/dev/null 2>&1; then
        print_error "Frontend is not running"
        return 1
    fi

    # Test login first
    ENV_FILE="$BACKEND_DIR/.env"
    if [ -f "$ENV_FILE" ]; then
        OP_USER=$(grep "^OP_INIT_USER=" "$ENV_FILE" | cut -d'=' -f2 | tr -d '"' | tr -d "'")
        OP_PASS=$(grep "^OP_INIT_PASS=" "$ENV_FILE" | cut -d'=' -f2 | tr -d '"' | tr -d "'")
    else
        OP_USER="kuro"
        OP_PASS="00491E4C"
    fi

    LOGIN_RESPONSE=$(curl -s -X POST http://localhost:8000/api/auth/login \
        -H "Content-Type: application/json" \
        -d "{\"username\": \"$OP_USER\", \"password\": \"$OP_PASS\"}" 2>/dev/null || echo "")

    if [[ "$LOGIN_RESPONSE" == *"access_token"* ]]; then
        print_success "Login successful for dashboard test"
    else
        print_error "Login failed - cannot test dashboard"
        return 1
    fi

    # Check Vite configuration
    if grep -q "alias:" /home/haku/projects/DHQ_Root/frontend/vite.config.js; then
        print_success "Vite alias configured"
    else
        print_error "Vite alias not configured"
    fi

    # Check component files
    COMPONENTS=(
        "/home/haku/projects/DHQ_Root/frontend/src/components/Vault/FileGrid.vue"
        "/home/haku/projects/DHQ_Root/frontend/src/components/Hub/ChatInterface.vue"
        "/home/haku/projects/DHQ_Root/frontend/src/components/Dashboard/ActivityFeed.vue"
        "/home/haku/projects/DHQ_Root/frontend/src/components/Dashboard/AnalyticsDashboard.vue"
    )

    for component in "${COMPONENTS[@]}"; do
        if [[ -f "$component" ]]; then
            print_success "$(basename "$component") exists"
        else
            print_error "$(basename "$component") missing"
        fi
    done

    print_success "Dashboard load test completed!"
}

# Function to show help
show_help() {
    print_header "🚀 DHQ Digital Headquarters - Unified Manager"
    echo "=============================================="
    echo ""
    echo "Usage: $0 {command} [options]"
    echo ""
    echo "🔧 SERVICE MANAGEMENT:"
    echo "  start              Start all DHQ services"
    echo "  stop               Stop all DHQ services"
    echo "  restart            Restart all DHQ services"
    echo "  status             Show service status"
    echo "  logs [service]     Show logs (backend|socketio|frontend|all)"
    echo "  health             Run health checks"
    echo "  init-op            Initialize OP user"
    echo ""
    echo "🧪 TESTING & VALIDATION:"
    echo "  test-complete      Run complete system test"
    echo "  test-login         Test OP login functionality"
    echo "  test-dashboard     Test dashboard loading"
    echo "  test-all           Run all tests"
    echo ""
    echo "🔒 SECURITY:"
    echo "  nuke               Nuke all DHQ data (DANGEROUS)"
    echo "  nuke-selective     Selective data removal"
    echo ""
    echo "📚 HELP:"
    echo "  help               Show this help message"
    echo ""
    echo "🌐 ACCESS POINTS:"
    echo "  Frontend:          http://localhost:3001"
    echo "  Backend API:       http://localhost:8000"
    echo "  API Docs:          http://localhost:8000/docs"
    echo "  Socket.IO:         http://localhost:8001"
    echo "  Domain:            https://haku.io.vn"
    echo ""
    echo "📝 EXAMPLES:"
    echo "  $0 start           # Start all services"
    echo "  $0 test-complete   # Run full system test"
    echo "  $0 logs backend    # Show backend logs"
    echo "  $0 status          # Check service status"
}

# Function to nuke system (dangerous)
nuke_system() {
    print_warning "⚠️  THIS WILL DELETE ALL DHQ DATA!"
    echo -e "${RED}This action is irreversible!${NC}"
    echo ""
    read -p "Are you absolutely sure? Type 'NUKE' to confirm: " confirm
    
    if [ "$confirm" = "NUKE" ]; then
        print_status "Nuking DHQ system..."
        
        # Stop services
        stop_services
        
        # Clear MongoDB (if accessible)
        if command -v mongosh >/dev/null 2>&1; then
            print_status "Clearing MongoDB data..."
            mongosh --eval "db.runCommand({dropDatabase: 1})" >/dev/null 2>&1 || true
        fi
        
        # Clear Redis (if accessible)
        if command -v redis-cli >/dev/null 2>&1; then
            print_status "Clearing Redis data..."
            redis-cli FLUSHALL >/dev/null 2>&1 || true
        fi
        
        # Clear logs
        rm -rf "$SCRIPT_DIR/logs"/* 2>/dev/null || true
        
        print_success "DHQ system nuked successfully"
    else
        print_status "Nuke cancelled"
    fi
}

# Function to run all tests
test_all() {
    print_header "🧪 Running All DHQ Tests"
    echo "==========================="
    
    test_complete
    echo ""
    test_login
    echo ""
    test_dashboard
    
    print_success "All tests completed!"
}

# Main script logic
case "${1:-help}" in
    start)
        print_header "🚀 Starting DHQ Digital Headquarters"
        echo "======================================"
        
        # Check dependencies
        if ! check_system_port 27017; then
            print_warning "MongoDB is not accessible on localhost:27017"
        else
            print_success "MongoDB detected on port 27017"
        fi
        
        if ! check_system_port 6379; then
            print_warning "Redis is not accessible on localhost:6379"
        else
            print_success "Redis detected on port 6379"
        fi
        
        if ! command -v npm >/dev/null 2>&1; then
            print_error "Node.js/npm not found. Please install Node.js."
            exit 1
        fi
        
        # Start services
        cleanup_services
        start_backend
        start_socketio
        start_frontend
        
        echo ""
        print_success "DHQ Digital Headquarters is now running!"
        echo "================================"
        echo -e "Frontend: ${GREEN}http://localhost:3001${NC}"
        echo -e "Backend API: ${GREEN}http://localhost:8000${NC}"
        echo -e "API Docs: ${GREEN}http://localhost:8000/docs${NC}"
        echo -e "Socket.IO: ${GREEN}http://localhost:8001${NC}"
        echo -e "Domain: ${GREEN}https://haku.io.vn${NC}"
        echo ""
        
        # Read credentials from .env
        ENV_FILE="$BACKEND_DIR/.env"
        if [ -f "$ENV_FILE" ]; then
            OP_USER=$(grep "^OP_INIT_USER=" "$ENV_FILE" | cut -d'=' -f2 | tr -d '"' | tr -d "'")
            OP_PASS=$(grep "^OP_INIT_PASS=" "$ENV_FILE" | cut -d'=' -f2 | tr -d '"' | tr -d "'")
            
            if [ ! -z "$OP_USER" ] && [ ! -z "$OP_PASS" ]; then
                print_status "Default login: ${GREEN}$OP_USER${NC} / ${GREEN}[SECURE]${NC} + OTP"
            else
                print_status "Default login: haku / haku123 + OTP (Could not read .env)"
            fi
        else
            print_status "Default login: haku / haku123 + OTP"
        fi
        
        print_status "Use './dhq_manager.sh status' to check service status"
        print_status "Use './dhq_manager.sh test-all' to run all tests"
        ;;
        
    stop)
        stop_services
        ;;
        
    restart)
        stop_services
        sleep 2
        $0 start
        ;;
        
    status)
        show_status
        ;;
        
    logs)
        show_logs "${2:-all}"
        ;;
        
    health)
        health_check
        ;;
        
    init-op)
        init_op
        ;;
        
    test-complete)
        test_complete
        ;;
        
    test-login)
        test_login
        ;;
        
    test-dashboard)
        test_dashboard
        ;;
        
    test-all)
        test_all
        ;;
        
    nuke)
        nuke_system
        ;;
        
    help|--help|-h)
        show_help
        ;;
        
    *)
        print_error "Unknown command: $1"
        echo ""
        show_help
        exit 1
        ;;
esac
