#!/usr/bin/env python3
"""
Test script to show expected growth order response structure
"""

def show_expected_responses():
    """Show what the frontend expects from the backend"""
    
    print("🎯 Expected API Response Structures")
    print("=" * 50)
    
    print("\n📊 Preview Response (what frontend expects):")
    preview_response = {
        "success": True,
        "preview": {
            "total_steps": 1440,
            "total_quantity": 100000,
            "start_time": "2026-02-05T02:00:00Z",
            "end_time": "2026-02-06T02:00:00Z",
            "timestamps": ["2026-02-05T02:00:00Z", "2026-02-05T02:40:00Z", "..."],
            "quantities": [69, 69, 69, "..."],
            "cumulative": [69, 138, 207, "..."]
        }
    }
    print(json.dumps(preview_response, indent=2))
    
    print("\n📋 List Response (what frontend expects):")
    list_response = {
        "success": True,
        "orders": [
            {
                "id": "507f1f77bfaf8677e5c39e1e",
                "name": "Test",
                "target_link": "https://youtube.com/watch?v=test123",
                "service_id": "817",
                "service_type": "Views",
                "total_quantity": 100000,
                "duration_minutes": 1440,
                "step_interval": 40,
                "graph_type": "Organic",
                "tolerance_percent": 10,
                "seed": 1234567,
                "status": "Active",
                "progress": 0.0,
                "total_executed": 0,
                "sub_orders_count": 1440,
                "created_at": "2026-02-05T01:50:00Z",
                "sub_orders": [
                    {
                        "id": "sub1",
                        "scheduled_time": "2026-02-05T02:00:00Z",
                        "quantity": 69,
                        "status": "Pending",
                        "executed_at": None,
                        "external_order_id": None
                    }
                ]
            }
        ]
    }
    print(json.dumps(list_response, indent=2))
    
    print("\n📝 Create Response (what frontend expects):")
    create_response = {
        "success": True,
        "order_id": "507f1f77bfaf8677e5c39e1e",
        "message": "Growth order created successfully",
        "preview": {
            "total_steps": 1440,
            "total_quantity": 100000,
            "start_time": "2026-02-05T02:00:00Z",
            "end_time": "2026-02-06T02:00:00Z"
        },
        "sub_orders_count": 1440,
        "start_time": "2026-02-05T02:00:00Z",
        "end_time": "2026-02-06T02:00:00Z"
    }
    print(json.dumps(create_response, indent=2))
    
    print("\n🔧 Debugging Steps:")
    print("1. Open browser dev tools (F12)")
    print("2. Go to Console tab")
    print("3. Try creating an order or preview")
    print("4. Look for console.log messages")
    print("5. Check Network tab for API requests")
    print("6. Verify response structure matches above")

if __name__ == "__main__":
    import json
    show_expected_responses()
