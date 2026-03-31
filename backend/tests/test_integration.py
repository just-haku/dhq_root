#!/usr/bin/env python3
"""
Quick test to verify the test API server works with the main DHQ system
"""

import requests
import json
import time

def test_test_api_server():
    """Test the test API server directly"""
    print("🧪 Testing Test API Server...")
    
    try:
        # Test health endpoint
        response = requests.get('http://localhost:8002/health')
        print(f"✅ Health check: {response.json()}")
        
        # Test API endpoint
        test_order = {
            "action": "add",
            "key": "test_api_key_123",
            "service": "102",
            "link": "https://youtube.com/watch?v=test123",
            "quantity": 1000
        }
        
        response = requests.post('http://localhost:8002/api/v2', json=test_order)
        print(f"✅ Test order: {response.json()}")
        
        return True
    except Exception as e:
        print(f"❌ Test API server error: {e}")
        return False

def test_main_backend_integration():
    """Test main backend can reach test API"""
    print("\n🔧 Testing Main Backend Integration...")
    
    try:
        # Test main backend health
        response = requests.get('http://localhost:8000/health')
        print(f"✅ Main backend health: {response.json()}")
        
        # Test if test API endpoint exists in main backend
        response = requests.get('http://localhost:8000/api/test-configs')
        print(f"✅ Test configs endpoint: {response.status_code}")
        
        return True
    except Exception as e:
        print(f"❌ Main backend error: {e}")
        return False

def main():
    print("🚀 DHQ Test API Integration Test")
    print("=" * 50)
    
    # Test test API server
    test_api_ok = test_test_api_server()
    
    # Test main backend
    main_backend_ok = test_main_backend_integration()
    
    print("\n📊 Test Results:")
    print(f"Test API Server: {'✅ OK' if test_api_ok else '❌ FAILED'}")
    print(f"Main Backend: {'✅ OK' if main_backend_ok else '❌ FAILED'}")
    
    if test_api_ok and main_backend_ok:
        print("\n🎉 All systems ready for testing!")
        print("\nNext steps:")
        print("1. Enable test mode in OP Panel")
        print("2. Configure Test API with http://localhost:8002")
        print("3. Create Channel Growth order")
        print("4. Check if it routes to test API")
    else:
        print("\n❌ Fix issues before proceeding")

if __name__ == "__main__":
    main()
