#!/bin/bash

# DHQ Comprehensive Test Suite
# Tests all main and side features

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test configuration
BASE_URL="http://localhost:3001"
API_URL="http://localhost:8000"
OP_USER="kuro"
OP_PASS="00491E4C"

print_header() {
    echo -e "${BLUE}=====================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}=====================================${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ️  $1${NC}"
}

# Get auth token
get_token() {
    curl -s -X POST "$API_URL/api/auth/login" \
        -H "Content-Type: application/json" \
        -d "{\"username\": \"$OP_USER\", \"password\": \"$OP_PASS\"}" | \
        jq -r '.access_token'
}

# Test function
test_api() {
    local endpoint="$1"
    local method="${2:-GET}"
    local data="$3"
    local expected_field="$4"
    
    TOKEN=$(get_token)
    
    if [ "$method" = "POST" ] && [ -n "$data" ]; then
        response=$(curl -s -X POST "$API_URL$endpoint" \
            -H "Content-Type: application/json" \
            -H "Authorization: Bearer $TOKEN" \
            -d "$data")
    else
        response=$(curl -s -X GET "$API_URL$endpoint" \
            -H "Authorization: Bearer $TOKEN")
    fi
    
    if [[ "$response" == *"$expected_field"* ]]; then
        print_success "$endpoint - $expected_field found"
        return 0
    else
        print_error "$endpoint - $expected_field not found"
        echo "Response: $response"
        return 1
    fi
}

# Start testing
print_header "🧪 DHQ Comprehensive Test Suite"

# 1. Authentication Tests
print_header "🔐 Authentication Tests"

TOKEN=$(get_token)
if [ -n "$TOKEN" ] && [ "$TOKEN" != "null" ]; then
    print_success "OP Login successful"
else
    print_error "OP Login failed"
    exit 1
fi

# 2. User Management Tests
print_header "👥 User Management Tests"

# Test user listing
test_api "/api/admin/users" "GET" "" "username"

# Test user creation
test_api "/api/admin/users" "POST" '{"username": "testuser2", "email": "test2@example.com", "password": "test123", "display_name": "Test User 2", "role": "USER"}' "message"

# 3. Growth Order Tests
print_header "📈 Growth Order Tests"

# Test preview
test_api "/api/growth/preview" "POST" '{"total_quantity": 10000, "duration_minutes": 1440, "step_interval": 60, "graph_type": "Organic", "tolerance_percent": 10}' "timestamps"

# Test order creation
test_api "/api/growth/create" "POST" '{"name": "Test Order", "target_link": "https://example.com/video", "service_id": "102", "service_type": "Views", "total_quantity": 10000, "duration_minutes": 1440, "step_interval": 60, "graph_type": "Organic", "tolerance_percent": 10, "api_key": "test-key"}' "order_id"

# Test order listing
test_api "/api/growth/list" "GET" "" "orders"

# 4. Vault/Drive Tests
print_header "📁 Vault & Drive Tests"

# Test folder creation
test_api "/api/vault-drive/vault/folder" "POST" '{"folder_path": "/test-comprehensive"}' "folder"

test_api "/api/vault-drive/drive/folder" "POST" '{"folder_path": "/test-drive-comprehensive"}' "folder"

# 5. Shop Tests
print_header "🛍️ Shop Tests"

# Test shop item creation
test_api "/api/vault-drive/shop/create-item" "POST" '{"name": "Test Item", "type": "Avatar Frame", "rarity": "COMMON", "price": 100, "description": "Test item"}' "item"

# 6. Collaboration Tests
print_header "🤝 Collaboration Tests"

# Test collaboration listing
test_api "/api/collaboration/collaborations" "GET" "" "collaborations"

# 7. KPI Bonus Tests
print_header "💎 KPI Bonus Tests"

# Test KPI bonus dashboard
test_api "/api/kpi-bonus/dashboard" "GET" "" "current_kpi"

# 8. Memory Allocation Tests
print_header "💾 Memory Allocation Tests"

# Test memory allocations
test_api "/api/user/memory-allocations" "GET" "" "allocations"

# 9. Activity Feed Tests
print_header "📊 Activity Feed Tests"

# Test activity feed
test_api "/api/activity/feed" "GET" "" "activities"

# 10. System Status Tests
print_header "🖥️ System Status Tests"

# Test system health
if curl -s "$API_URL/health" | grep -q "healthy"; then
    print_success "Backend health check"
else
    print_error "Backend health check failed"
fi

# Test frontend
if curl -s "$BASE_URL" | grep -q "DOCTYPE"; then
    print_success "Frontend accessible"
else
    print_error "Frontend not accessible"
fi

# 11. File Upload Tests
print_header "📤 File Upload Tests"

# Create test file
echo "Test content for upload" > /tmp/test-upload-comprehensive.txt

# Test vault upload
TOKEN=$(get_token)
if curl -s -X POST "$API_URL/api/vault-drive/vault/upload" \
    -H "Authorization: Bearer $TOKEN" \
    -F "file=@/tmp/test-upload-comprehensive.txt" \
    -F "folder_path=/test-comprehensive" | grep -q "uploaded successfully"; then
    print_success "Vault upload working"
else
    print_error "Vault upload failed"
fi

# Test drive upload
if curl -s -X POST "$API_URL/api/vault-drive/drive/upload" \
    -H "Authorization: Bearer $TOKEN" \
    -F "file=@/tmp/test-upload-comprehensive.txt" \
    -F "folder_path=/test-drive-comprehensive" | grep -q "uploaded successfully"; then
    print_success "Drive upload working"
else
    print_error "Drive upload failed"
fi

# Cleanup
rm -f /tmp/test-upload-comprehensive.txt

print_header "🎉 Test Summary"
print_info "All major DHQ features have been tested"
print_info "For detailed testing of chat/voice/video features, please test manually in the browser"
print_info "Access the system at: $BASE_URL"
print_info "Login with: $OP_USER / [SECURE]"

echo -e "${GREEN}✅ Comprehensive testing completed!${NC}"
