#!/usr/bin/env python3
"""
Test script for the DHQ Test API Endpoint
This script demonstrates how to use the test API endpoint that simulates the external SMM API
"""

import requests
import json
import time

# Configuration
BASE_URL = "http://localhost:8000"
API_TOKEN = "YOUR_AUTH_TOKEN_HERE"  # Replace with actual OP token

def test_api_endpoint(action, params):
    """Test the API endpoint with different actions"""
    
    url = f"{BASE_URL}/api/test-api"
    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "action": action,
        "api_key": "test_api_key_123",
        **params
    }
    
    print(f"\n{'='*50}")
    print(f"Testing {action.upper()} action")
    print(f"URL: {url}")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    print(f"{'='*50}")
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        try:
            response_data = response.json()
            print(f"Response Body: {json.dumps(response_data, indent=2)}")
        except:
            print(f"Response Body: {response.text}")
            
        return response
        
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None

def main():
    """Main test function"""
    
    print("DHQ Test API Endpoint Test Script")
    print("==================================")
    print("This script tests the test API endpoint that simulates the external SMM API")
    print("\nMake sure:")
    print("1. Backend is running on http://localhost:8000")
    print("2. You have a valid OP auth token")
    print("3. A test API configuration is enabled in the OP dashboard")
    
    if API_TOKEN == "YOUR_AUTH_TOKEN_HERE":
        print("\n⚠️  WARNING: Please update the API_TOKEN variable with your actual token")
        return
    
    # Test 1: Add Order
    print("\n🧪 Test 1: Add Order")
    test_api_endpoint("add", {
        "service_id": "123",
        "link": "https://example.com/post/123",
        "quantity": 100
    })
    
    time.sleep(1)
    
    # Test 2: Check Order Status
    print("\n🧪 Test 2: Check Order Status")
    test_api_endpoint("status", {
        "order_id": "99999"
    })
    
    time.sleep(1)
    
    # Test 3: Check Balance
    print("\n🧪 Test 3: Check Balance")
    test_api_endpoint("balance", {})
    
    time.sleep(1)
    
    # Test 4: Invalid Action (should fail)
    print("\n🧪 Test 4: Invalid Action")
    test_api_endpoint("invalid_action", {})
    
    time.sleep(1)
    
    # Test 5: Missing Parameters (should fail)
    print("\n🧪 Test 5: Add Order with Missing Parameters")
    test_api_endpoint("add", {
        "service_id": "123"
        # Missing link and quantity
    })
    
    print("\n✅ All tests completed!")
    print("\nTo view the logs and manage the test API configuration:")
    print("1. Go to the Admin Panel in your frontend")
    print("2. Navigate to the 'API Test Management' section")
    print("3. Create or enable a test configuration")
    print("4. Monitor the API logs and statistics")

if __name__ == "__main__":
    main()
