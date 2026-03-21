#!/usr/bin/env python3
"""
Check if test API configuration exists and is properly set up
"""

import sys
import os
sys.path.append('/home/haku/projects/DHQ_Root/backend')

from app.models.test_api import TestAPIConfig

def check_test_api_config():
    """Check if test API configuration exists"""
    print("🔍 Checking Test API Configuration...")
    
    try:
        # Check for any test API configs
        all_configs = TestAPIConfig.objects()
        print(f"Found {len(all_configs)} total test API configurations")
        
        # Check for enabled configs
        enabled_configs = TestAPIConfig.objects(is_enabled=True)
        print(f"Found {len(enabled_configs)} enabled configurations")
        
        # Check for intercept configs
        intercept_configs = TestAPIConfig.objects(intercept_growth_orders=True)
        print(f"Found {len(intercept_configs)} configurations with growth interception")
        
        # Check for both enabled AND intercept
        active_configs = TestAPIConfig.objects(is_enabled=True, intercept_growth_orders=True)
        print(f"Found {len(active_configs)} active configurations (enabled + intercept)")
        
        if active_configs:
            print("\n✅ Active Test API Configurations:")
            for config in active_configs:
                print(f"  - Name: {config.name}")
                print(f"    Mock Responses: {config.mock_responses}")
                print(f"    Failure Rate: {config.failure_rate_percent}%")
                print(f"    Response Delay: {config.response_delay_ms}ms")
                print(f"    Log Requests: {config.log_requests}")
        else:
            print("\n❌ No active test API configurations found!")
            print("You need to create a test API configuration in the OP Panel:")
            print("1. Go to OP Configuration Center → Test API")
            print("2. Create a new configuration")
            print("3. Enable: ✅ Enable Configuration")
            print("4. Enable: ✅ Intercept Channel Growth Orders")
            print("5. Set Failure Rate: 0%")
            print("6. Save the configuration")
        
        return len(active_configs) > 0
        
    except Exception as e:
        print(f"❌ Error checking test API configuration: {e}")
        return False

if __name__ == "__main__":
    success = check_test_api_config()
    
    if success:
        print("\n✅ Test API configuration is ready!")
    else:
        print("\n❌ Test API configuration needs to be set up!")
