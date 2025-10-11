"""
Test script to discover available notification methods
"""

import asyncio
import httpx
import json

async def test_notification_methods():
    """Test different notification methods to find supported ones"""
    
    print("🔍 Discovering Notification Agent Methods")
    print("=" * 60)
    
    endpoint_url = "https://notification-system-h36d.onrender.com/a2a/tasks"
    
    # Test various possible method names
    test_methods = [
        "send_notification",
        "send_message",
        "notify",
        "send_family_update",
        "send_status_update",
        "send_emergency_alert",
        "SendNotification",
        "SendMessage",
        "Notify",
        "SendFamilyUpdate",
        "SendStatusUpdate", 
        "SendEmergencyAlert",
        "create_notification",
        "send_email",
        "send_sms",
        "send_push",
        "broadcast",
        "alert",
        "update_family",
        "status_update"
    ]
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        for method in test_methods:
            try:
                request = {
                    "jsonrpc": "2.0",
                    "id": f"test_{method}",
                    "method": method,
                    "params": {
                        "patient_id": "P001",
                        "message": "Test message"
                    }
                }
                
                response = await client.post(
                    endpoint_url,
                    json=request,
                    headers={
                        "Content-Type": "application/json",
                        "Accept": "application/json"
                    }
                )
                
                if response.status_code == 200:
                    response_data = response.json()
                    
                    if "error" in response_data:
                        error_code = response_data["error"].get("code", "unknown")
                        error_message = response_data["error"].get("message", "unknown")
                        
                        if error_code == -32601:  # Method not found
                            print(f"❌ {method}: Method not found")
                        elif error_code == -32602:  # Invalid params
                            print(f"⚠️ {method}: Invalid params (method exists!)")
                        else:
                            print(f"❓ {method}: Error {error_code} - {error_message}")
                    else:
                        print(f"✅ {method}: SUCCESS! Method found and working")
                        print(f"   Response: {response_data}")
                        
            except Exception as e:
                print(f"❌ {method}: Exception - {e}")
    
    print(f"\n🔍 Testing Generic Methods:")
    print("=" * 60)
    
    # Test some generic A2A methods
    generic_methods = [
        "ping",
        "health",
        "status",
        "info",
        "capabilities",
        "methods",
        "list_methods",
        "get_info",
        "version"
    ]
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        for method in generic_methods:
            try:
                request = {
                    "jsonrpc": "2.0",
                    "id": f"test_{method}",
                    "method": method,
                    "params": {}
                }
                
                response = await client.post(
                    endpoint_url,
                    json=request,
                    headers={
                        "Content-Type": "application/json",
                        "Accept": "application/json"
                    }
                )
                
                if response.status_code == 200:
                    response_data = response.json()
                    
                    if "error" in response_data:
                        error_code = response_data["error"].get("code", "unknown")
                        if error_code != -32601:  # Not method not found
                            print(f"⚠️ {method}: Error {error_code} (method exists)")
                    else:
                        print(f"✅ {method}: SUCCESS! Response: {response_data}")
                        
            except Exception as e:
                print(f"❌ {method}: Exception - {e}")

if __name__ == "__main__":
    asyncio.run(test_notification_methods())
