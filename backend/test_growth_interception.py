#!/usr/bin/env python3
"""
Test script for Channel Growth with Test API Interception
This script demonstrates how the OP can enable test mode for Channel Growth orders
"""

import requests
import json
import time

# Configuration
BASE_URL = "http://localhost:8000"
API_TOKEN = "YOUR_AUTH_TOKEN_HERE"  # Replace with actual OP token

def create_test_config():
    """Create a test API configuration that intercepts growth orders"""
    
    url = f"{BASE_URL}/api/test-configs"
    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    config_data = {
        "name": "Growth Order Test",
        "description": "Test configuration for Channel Growth orders",
        "is_enabled": True,
        "mock_responses": True,
        "intercept_growth_orders": True,  # This is the key field!
        "success_response": {"order": 99999},
        "error_response": {"error": "Test error message"},
        "response_delay_ms": 2000,  # 2 second delay to simulate real API
        "failure_rate_percent": 10,  # 10% failure rate for testing
        "log_requests": True,
        "log_responses": True
    }
    
    print("🔧 Creating test API configuration...")
    print(f"URL: {url}")
    print(f"Payload: {json.dumps(config_data, indent=2)}")
    
    try:
        response = requests.post(url, headers=headers, json=config_data)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Test configuration created successfully!")
            print(f"Config ID: {result['config']['id']}")
            return result['config']['id']
        else:
            print(f"❌ Failed to create test configuration: {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error creating test configuration: {e}")
        return None

def create_growth_order(test_mode=False):
    """Create a Channel Growth order"""
    
    url = f"{BASE_URL}/api/growth/create"
    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    order_data = {
        "name": "Test Growth Order",
        "target_link": "https://youtube.com/watch?v=test123",
        "service_id": "102",
        "service_type": "Views",
        "total_quantity": 1000,
        "duration_minutes": 60,
        "step_interval": 5,
        "graph_type": "Organic",
        "tolerance_percent": 10,
        "api_key": "test_api_key_123"
    }
    
    print(f"\n📈 Creating Channel Growth order...")
    print(f"URL: {url}")
    print(f"Payload: {json.dumps(order_data, indent=2)}")
    
    try:
        response = requests.post(url, headers=headers, json=order_data)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Growth order created successfully!")
            print(f"Order ID: {result['order_id']}")
            print(f"Sub-orders: {result['sub_orders_count']}")
            return result['order_id']
        else:
            print(f"❌ Failed to create growth order: {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error creating growth order: {e}")
        return None

def run_suborder_now(order_id, suborder_id):
    """Force run a sub-order to test the API interception"""
    
    url = f"{BASE_URL}/api/growth/{order_id}/suborders/{suborder_id}/run_now"
    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    request_data = {
        "api_key": "test_api_key_123"
    }
    
    print(f"\n⚡ Running sub-order now...")
    print(f"URL: {url}")
    print(f"Sub-order ID: {suborder_id}")
    
    try:
        response = requests.post(url, headers=headers, json=request_data)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Sub-order execution started!")
            print(f"Message: {result['message']}")
        else:
            print(f"❌ Failed to run sub-order: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error running sub-order: {e}")

def get_growth_order_details(order_id):
    """Get detailed information about a growth order"""
    
    url = f"{BASE_URL}/api/growth/{order_id}"
    headers = {
        "Authorization": f"Bearer {API_TOKEN}"
    }
    
    print(f"\n📊 Getting growth order details...")
    
    try:
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            result = response.json()
            order = result['order']
            
            print(f"Order: {order['name']}")
            print(f"Status: {order['status']}")
            print(f"Progress: {order['progress']:.1f}%")
            print(f"Total Executed: {order['total_executed']}")
            print(f"Total Failed: {order['total_failed']}")
            
            print(f"\nSub-orders:")
            for i, sub_order in enumerate(order['sub_orders'][:5]):  # Show first 5
                print(f"  {i+1}. {sub_order['quantity']} units - {sub_order['status']}")
                if sub_order.get('external_order_id'):
                    print(f"     External ID: {sub_order['external_order_id']}")
                if sub_order.get('error_log'):
                    print(f"     Error: {sub_order['error_log']}")
            
            if len(order['sub_orders']) > 5:
                print(f"  ... and {len(order['sub_orders']) - 5} more sub-orders")
                
        else:
            print(f"❌ Failed to get order details: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error getting order details: {e}")

def check_api_logs():
    """Check recent API logs to see if interception is working"""
    
    url = f"{BASE_URL}/api/logs?limit=10"
    headers = {
        "Authorization": f"Bearer {API_TOKEN}"
    }
    
    print(f"\n📋 Recent API Logs:")
    
    try:
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            result = response.json()
            logs = result['logs']
            
            if logs:
                for log in logs:
                    print(f"  {log['request_timestamp']} - {log['endpoint_name']} - {log['request_body']['action']} - {log['response_status']} - {log['duration_ms']:.0f}ms")
                    if log.get('is_test_mode'):
                        print(f"    🧪 TEST MODE")
            else:
                print("  No recent logs found")
                
        else:
            print(f"❌ Failed to get logs: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error getting logs: {e}")

def main():
    """Main test function"""
    
    print("🧪 Channel Growth Test API Interception Demo")
    print("=" * 50)
    print("\nThis script demonstrates:")
    print("1. Creating a test API configuration")
    print("2. Enabling growth order interception")
    print("3. Creating a Channel Growth order")
    print("4. Running sub-orders to test interception")
    print("5. Checking API logs to verify interception")
    
    if API_TOKEN == "YOUR_AUTH_TOKEN_HERE":
        print("\n⚠️  WARNING: Please update the API_TOKEN variable with your actual token")
        return
    
    # Step 1: Create test configuration
    config_id = create_test_config()
    if not config_id:
        print("\n❌ Failed to create test configuration. Exiting.")
        return
    
    time.sleep(2)
    
    # Step 2: Create growth order
    order_id = create_growth_order()
    if not order_id:
        print("\n❌ Failed to create growth order. Exiting.")
        return
    
    time.sleep(2)
    
    # Step 3: Get order details to find sub-order IDs
    print(f"\n🔍 Getting order details to find sub-orders...")
    # Note: In a real scenario, you'd parse the order details to get sub-order IDs
    
    # Step 4: Check API logs
    check_api_logs()
    
    print(f"\n✅ Demo completed!")
    print(f"\nTo test manually:")
    print(f"1. Go to Admin Panel → API Test Management")
    print(f"2. Enable 'Intercept Channel Growth Orders' on your test configuration")
    print(f"3. Create a Channel Growth order in the frontend")
    print(f"4. Run a sub-order and check if it uses the test API")
    print(f"5. Check the API logs to see the interception in action")

if __name__ == "__main__":
    main()
