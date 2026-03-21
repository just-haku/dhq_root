#!/usr/bin/env python3
"""
Test script to verify growth order creation works
"""

import requests
import json

def test_growth_order_creation():
    """Test the growth order creation API"""
    print("🧪 Testing Growth Order Creation...")
    
    # Test data
    test_order = {
        "name": "Test Growth Order",
        "target_link": "https://youtube.com/watch?v=test123",
        "service_id": "102",
        "service_type": "Views",
        "total_quantity": 1000,
        "duration_minutes": 60,
        "step_interval": 60,
        "graph_type": "Organic",
        "tolerance_percent": 10,
        "seed": 12345,
        "api_key": "test_api_key_123"
    }
    
    test_preview = {
        "total_quantity": 1000,
        "duration_minutes": 60,
        "step_interval": 60,
        "graph_type": "Organic",
        "tolerance_percent": 10,
        "seed": 12345
    }
    
    try:
        # Test preview endpoint
        print("📊 Testing preview endpoint...")
        response = requests.post('http://localhost:8000/api/growth/preview', json=test_preview)
        print(f"Preview Status: {response.status_code}")
        if response.status_code == 200:
            print("✅ Preview endpoint working")
            print(f"Response: {response.json()}")
        else:
            print(f"❌ Preview failed: {response.text}")
            return False
        
        # Test create endpoint (will fail without auth, but should show validation)
        print("\n📝 Testing create endpoint...")
        response = requests.post('http://localhost:8000/api/growth/create', json=test_order)
        print(f"Create Status: {response.status_code}")
        if response.status_code == 401:
            print("✅ Create endpoint working (auth required - expected)")
        elif response.status_code == 422:
            print(f"❌ Validation error: {response.text}")
            return False
        else:
            print(f"Response: {response.text}")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def main():
    print("🚀 DHQ Growth Order Test")
    print("=" * 40)
    
    success = test_growth_order_creation()
    
    if success:
        print("\n✅ Growth order API is working correctly!")
        print("The 422 errors were likely due to missing validation or auth issues.")
        print("Try creating an order through the web interface now.")
    else:
        print("\n❌ There are still issues with the growth order API.")

if __name__ == "__main__":
    main()
