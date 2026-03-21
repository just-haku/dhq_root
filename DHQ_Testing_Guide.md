# 🧪 DHQ Test API Testing Guide

## 📋 **Prerequisites**

### **Environment Setup**
```bash
# Activate virtual environment
source /home/haku/projects/venv/DHQ_Root/bin/activate

# Navigate to backend directory
cd /home/haku/projects/DHQ_Root/backend
```

### **System Status Check**
```bash
# Run integration test to verify everything is ready
python3 test_integration.py
```

**Expected Output:**
```
🎉 All systems ready for testing!
Test API Server: ✅ OK
Main Backend: ✅ OK
```

## 🚀 **Quick Start Testing**

### **Step 1: Start Test API Server**
```bash
# Terminal 1 - Start test API server
source /home/haku/projects/venv/DHQ_Root/bin/activate
python3 test_api_server.py
```

**Expected Output:**
```
🧪 Starting DHQ Test API Server on port 8002...
📝 This server simulates SMM API behavior for testing
🔗 Available endpoints:
   POST /api/v2 - Main SMM API endpoint
   GET /test-api - Direct test endpoint
   GET /test-orders - List test orders
   DELETE /test-orders - Clear test orders
   GET /health - Health check
```

### **Step 2: Enable Test Mode in Frontend**
1. Go to: `https://haku.io.vn`
2. Navigate to: **Admin Panel** → **OP Configuration Center**
3. Look for the **Test Mode Toggle** at the top
4. **Enable Test Mode** (switch turns blue)
5. Page will automatically refresh

**Visual Indicators:**
- Toggle shows: **"🧪 Test Mode ON"**
- Hint text: **"API calls route to local backend (haku.io.vn:8000)"**
- Browser console: **"🧪 Test mode enabled"**

### **Step 3: Configure Test API**
1. In OP Configuration Center, click **"Test API"** tab
2. Create new configuration:

#### **Configuration 1: Mock Mode (Recommended First)**
```
✅ Enable Configuration
✅ Use Mock Responses
✅ Intercept Channel Growth Orders
✅ Log Requests
✅ Log Responses

Name: Growth Order Test
Description: Test configuration for Channel Growth orders
Response Delay: 2000ms
Failure Rate: 10%
```

#### **Configuration 2: Real Test Server**
```
✅ Enable Configuration
❌ Use Mock Responses (UNCHECK)
✅ Intercept Channel Growth Orders

Name: Growth Order Real Test
Description: Test with real test API server
Real API URL: http://localhost:8002
Real API Key: test_api_key_123
Response Delay: 1000ms
Failure Rate: 0%
```

### **Step 4: Test Channel Growth Integration**
1. Navigate to **Channel Growth** page
2. Create new order:
   - **Service**: Any available service (e.g., Views, Likes)
   - **Target Link**: `https://youtube.com/watch?v=test123`
   - **Quantity**: 1000
   - **Duration**: 60 minutes
   - **API Key**: `test_api_key_123`
3. Click **"Create Order"**
4. Click **"Run Now"** on any sub-order

### **Step 5: Verify Test Results**
Check these locations to confirm the test is working:

#### **A. Test Server Logs**
In Terminal 1 (test API server), you should see:
```
POST /api/v2 - {"action": "add", "service": "102", "quantity": 1000}
```

#### **B. OP Panel API Logs**
1. Go to **OP Configuration Center** → **Test API** → **"API Logs"** tab
2. Look for entries with **"🧪 TEST MODE"** indicator
3. Verify response times match your delay settings

#### **C. Growth Order Status**
1. In Channel Growth page, check your order:
   - **Status**: Should be "Processing" or "Completed"
   - **External Order ID**: Should be 100000+ (test-generated)
   - **Error Logs**: Should show test errors if failure rate > 0%

## 🎯 **Test Scenarios**

### **Scenario 1: Basic Mock Test**
**Purpose:** Verify basic interception works
```
Settings: Mock=ON, Intercept=ON, Delay=2000ms, Failure=10%
Expected: 
- Orders succeed with 2-second delay
- Random order IDs (100000-999999)
- ~10% orders fail with test errors
- Logs show "🧪 TEST MODE"
```

### **Scenario 2: Failure Simulation**
**Purpose:** Test error handling
```
Settings: Mock=ON, Intercept=ON, Delay=500ms, Failure=50%
Expected:
- Half orders fail
- Fast response (500ms)
- Error messages from template
- Growth system handles failures gracefully
```

### **Scenario 3: Real Test Server**
**Purpose:** Test with actual API server
```
Settings: Mock=OFF, Intercept=ON, URL=http://localhost:8002
Expected:
- Orders go to real test server
- Server logs show actual requests
- Can inspect request/response format
- More realistic API behavior
```

### **Scenario 4: Toggle Test**
**Purpose:** Verify switching works
```
1. Start with Test Mode OFF (normal operation)
2. Create Growth order → Should go to real API
3. Enable Test Mode ON
4. Create another order → Should go to test API
5. Disable Test Mode OFF
6. Create order → Should go back to real API
```

## 📊 **Verification Commands**

### **Check Test Server Status**
```bash
# Health check
curl http://localhost:8002/health

# List test orders
curl http://localhost:8002/test-orders

# Clear test orders
curl -X DELETE http://localhost:8002/test-orders
```

### **Check Main Backend**
```bash
# Backend health
curl http://localhost:8000/health

# Test configs (should return 403 without auth - this is expected)
curl http://localhost:8000/api/test-configs
```

### **Manual API Test**
```bash
# Test order directly
curl -X POST http://localhost:8002/api/v2 \
  -H "Content-Type: application/json" \
  -d '{
    "action": "add",
    "key": "test_api_key_123",
    "service": "102",
    "link": "https://youtube.com/watch?v=test123",
    "quantity": 1000
  }'
```

## 🔍 **Troubleshooting**

### **Common Issues & Solutions**

#### **Issue: "Test API server connection refused"**
```bash
# Solution: Make sure test server is running
source /home/haku/projects/venv/DHQ_Root/bin/activate
python3 test_api_server.py
```

#### **Issue: "Orders not being intercepted"**
**Solution:**
1. Verify Test Mode is enabled in OP Panel
2. Check "Intercept Channel Growth Orders" is checked
3. Ensure only ONE test config is active
4. Refresh the page after enabling

#### **Issue: "Still getting 401 errors"**
**Solution:**
1. Verify Test Mode toggle is blue (enabled)
2. Check browser console for "Test mode enabled" message
3. Refresh page to apply new routing
4. Check you're logged in with valid session

#### **Issue: "Test server not receiving requests"**
**Solution:**
1. Check test server logs for incoming requests
2. Verify test configuration is saved
3. Check API logs in OP Panel for "🧪 TEST MODE" entries
4. Make sure Channel Growth order uses API key `test_api_key_123`

### **Debug Mode**
Enable detailed logging:
1. Go to **OP Configuration Center** → **System** → **Monitoring Settings**
2. Enable:
   - ✅ Real-time Alerts
   - ✅ Performance Tracking
   - ✅ Log Monitoring

## 📈 **Success Indicators**

### **✅ Test Mode Working**
- Frontend shows "🧪 Test Mode ON"
- API calls route to `haku.io.vn:8000`
- Browser console shows test mode activation

### **✅ Interception Working**
- Channel Growth orders route to test API when enabled
- Orders route to real API when disabled
- No changes to Growth order logic
- Seamless switching between modes

### **✅ Test API Working**
- Test server logs show incoming requests
- API logs show "🧪 TEST MODE" entries
- Growth orders get test order IDs (100000+)
- Response delays match configuration

### **✅ Error Handling**
- Failed orders show test error messages
- Growth system handles failures gracefully
- Error rates match configuration
- Logs capture both success and failure

## 🎮 **Advanced Testing**

### **Load Testing**
```bash
# Create multiple orders quickly to test performance
# Use different quantities and services
# Monitor response times and system load
```

### **Failure Testing**
```bash
# Set failure rate to 100% to test error handling
# Verify Growth system recovers properly
# Check error logs and user notifications
```

### **Performance Testing**
```bash
# Test with different delay settings
# Monitor system resource usage
# Verify no impact on other functions
```

## 🔄 **Cleanup & Reset**

### **Clear Test Data**
```bash
# Clear all test orders
curl -X DELETE http://localhost:8002/test-orders

# Reset test mode
# In OP Panel: Disable Test Mode toggle
```

### **Return to Production**
1. **Disable Test Mode** in OP Panel
2. **Delete test configurations** (optional)
3. **Stop test server** (Ctrl+C in Terminal 1)
4. **Verify normal operation** with a real order

## 📝 **Test Results Template**

### **Test Session Log**
```
Date: ___________
Test Mode: Enabled/Disabled
Configuration: Mock/Real Server
Response Delay: ___ms
Failure Rate: ___%

Orders Created: ___
Orders Succeeded: ___
Orders Failed: ___
Average Response Time: ___s

Issues Found:
1. ___________
2. ___________

Notes:
- ___________
- ___________
```

---

## 🎯 **Quick Test Checklist**

- [ ] Test API server running on port 8002
- [ ] Test Mode enabled in OP Panel
- [ ] Test API configuration created
- [ ] Channel Growth order created
- [ ] Order routed to test API (check logs)
- [ ] Test server received request
- [ ] Order status updated correctly
- [ ] API logs show "🧪 TEST MODE"
- [ ] External order ID is 100000+
- [ ] Response delay matches configuration

---

**🎉 Your DHQ Test API system is ready for comprehensive testing!**

Start with Scenario 1 (Basic Mock Test) and gradually try more advanced scenarios. The system is designed for safe, isolated testing without affecting production functionality.
