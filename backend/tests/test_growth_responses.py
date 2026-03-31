#!/usr/bin/env python3
"""
Test script to verify the growth order API responses
"""

import requests
import json

def test_growth_api_responses():
    """Test the growth API responses to see what frontend expects"""
    print("🧪 Testing Growth API Responses...")
    
    # Test preview request
    preview_request = {
        "total_quantity": 100000,
        "duration_minutes": 1440,
        "step_interval": 40,
        "graph_type": "Organic",
        "tolerance_percent": 10,
        "seed": 1234567
    }
    
    try:
        print("📊 Testing preview endpoint...")
        response = requests.post('http://localhost:8000/api/growth/preview', json=preview_request)
        print(f"Preview Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print("✅ Preview response structure:")
            print(json.dumps(data, indent=2))
        else:
            print(f"❌ Preview failed: {response.text}")
            return False
        
    except Exception as e:
        print(f"❌ Preview test failed: {e}")
        return False
    
    # Test list endpoint
    try:
        print("\n📋 Testing list endpoint...")
        response = requests.get('http://localhost:8000/api/growth/list')
        print(f"List Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print("✅ List response structure:")
            print(json.dumps(data, indent=2))
        else:
            print(f"❌ List failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ List test failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("🚀 DHQ Growth API Response Test")
    print("=" * 50)
    
    success = test_growth_api_responses()
    
    if success:
        print("\n✅ API responses look good!")
        print("Check the browser console for frontend debugging.")
    else:
        print("\n❌ API has issues that need fixing.")
