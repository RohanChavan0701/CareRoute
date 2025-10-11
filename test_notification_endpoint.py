"""
Test script for Notification Agent endpoint
"""

import asyncio
import httpx
import json
from datetime import datetime

async def test_notification_endpoint():
    """Test the Notification Agent endpoint"""
    
    print("📱 Testing Notification Agent Endpoint")
    print("=" * 60)
    
    endpoint_url = "https://notification-system-h36d.onrender.com/a2a/tasks"
    
    # Test 1: Basic SendFamilyUpdate request
    test_request_1 = {
        "jsonrpc": "2.0",
        "id": "test_001",
        "method": "SendFamilyUpdate",
        "params": {
            "patient_id": "P001",
            "patient_email": "john.doe@example.com",
            "flight_number": "WN123",
            "family_contacts": ["+1-555-111-2222", "+1-555-999-8888"],
            "message_type": "coordination_started",
            "status": "Guardian coordination activated",
            "orchestration_id": "ORCH_P001_20251011_121905"
        }
    }
    
    # Test 2: SendStatusUpdate request
    test_request_2 = {
        "jsonrpc": "2.0",
        "id": "test_002",
        "method": "SendStatusUpdate",
        "params": {
            "patient_id": "P001",
            "patient_email": "john.doe@example.com",
            "message_type": "flight_status_update",
            "content": "Your flight WN123 is now boarding at Gate B22",
            "priority": "normal",
            "channels": ["email", "sms", "push"]
        }
    }
    
    # Test 3: SendEmergencyAlert request
    test_request_3 = {
        "jsonrpc": "2.0",
        "id": "test_003",
        "method": "SendEmergencyAlert",
        "params": {
            "patient_id": "P001",
            "patient_email": "john.doe@example.com",
            "emergency_contacts": ["+1-555-111-2222", "+1-555-999-8888"],
            "alert_type": "medical_emergency",
            "message": "Patient requires immediate medical attention",
            "location": "Denver International Airport",
            "priority": "high",
            "channels": ["email", "sms", "phone", "push"]
        }
    }
    
    test_requests = [
        ("SendFamilyUpdate", test_request_1),
        ("SendStatusUpdate", test_request_2),
        ("SendEmergencyAlert", test_request_3)
    ]
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        for i, (method_name, request) in enumerate(test_requests, 1):
            print(f"\n📤 Test {i}: {method_name}")
            print("-" * 50)
            
            try:
                print(f"Request: {json.dumps(request, indent=2)}")
                
                response = await client.post(
                    endpoint_url,
                    json=request,
                    headers={
                        "Content-Type": "application/json",
                        "Accept": "application/json"
                    }
                )
                
                print(f"\n📥 Response Status: {response.status_code}")
                print(f"Response Headers: {dict(response.headers)}")
                
                try:
                    response_data = response.json()
                    print(f"Response Body: {json.dumps(response_data, indent=2)}")
                    
                    # Check if it's a valid JSON-RPC response
                    if "jsonrpc" in response_data and response_data["jsonrpc"] == "2.0":
                        if "result" in response_data:
                            print("✅ Valid JSON-RPC 2.0 success response")
                        elif "error" in response_data:
                            print("⚠️ Valid JSON-RPC 2.0 error response")
                        else:
                            print("❓ Unexpected JSON-RPC response format")
                    else:
                        print("❌ Not a valid JSON-RPC 2.0 response")
                        
                except json.JSONDecodeError:
                    print(f"Response Body (not JSON): {response.text}")
                    
            except httpx.TimeoutException:
                print("❌ Request timed out")
            except httpx.ConnectError:
                print("❌ Connection error - endpoint may be down")
            except Exception as e:
                print(f"❌ Error: {e}")
    
    print(f"\n🔍 Endpoint Analysis:")
    print("=" * 60)
    print("✅ Endpoint URL: https://notification-system-h36d.onrender.com/a2a/tasks")
    print("✅ Expected Format: JSON-RPC 2.0")
    print("✅ Supported Methods: SendFamilyUpdate, SendStatusUpdate, SendEmergencyAlert")
    print("✅ Required Headers: Content-Type: application/json")
    
    print(f"\n📋 Integration Notes:")
    print("=" * 60)
    print("1. Update orchestrator.py to use this real endpoint")
    print("2. Test with actual patient data")
    print("3. Verify response handling in orchestrator")
    print("4. Check error handling for failed notifications")

async def test_orchestrator_integration():
    """Test orchestrator integration with real endpoint"""
    
    print(f"\n🔗 Testing Orchestrator Integration")
    print("=" * 60)
    
    # Import orchestrator after testing endpoint
    from orchestrator import guardian_orchestrator
    
    # Sample booking data
    booking_data = {
        "patient_id": "P001",
        "patient_name": "John Doe",
        "patient_email": "john.doe@example.com",
        "flight_number": "WN123",
        "flight_date": "2025-10-12",
        "flight_time": "09:00",
        "departure_airport": "LAS",
        "arrival_airport": "DEN",
        "hotel_booking_reference": "HOTEL_REF_001",
        "hospital_appointment_id": "MED_APPT_001",
        "hospital_appointment_time": "2025-10-12T14:00:00",
        "emergency_contacts": ["+1-555-111-2222", "+1-555-999-8888"],
        "special_requirements": "Wheelchair accessible, Dietary restrictions",
        "medical_conditions": ["Diabetes", "Hypertension"],
        "age": 72,
        "preferred_language": "English"
    }
    
    print("🚀 Starting orchestration with real notification endpoint...")
    
    try:
        # Start orchestration (this will call the real notification endpoint)
        orchestration_id = await guardian_orchestrator.start_orchestration(booking_data)
        print(f"✅ Orchestration completed: {orchestration_id}")
        
        # Check if notification was sent successfully
        status = await guardian_orchestrator.get_orchestration_status(orchestration_id)
        if status and "tasks" in status:
            notification_task = status["tasks"].get("notification_coordination")
            if notification_task:
                print(f"📱 Notification Task Result: {notification_task.get('result')}")
            else:
                print("❌ No notification task found in orchestration")
        else:
            print("❌ Could not retrieve orchestration status")
            
    except Exception as e:
        print(f"❌ Orchestration failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_notification_endpoint())
    # Uncomment to test orchestrator integration
    # asyncio.run(test_orchestrator_integration())
