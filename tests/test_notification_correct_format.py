"""
Test script for correct notification format
"""

import asyncio
import httpx
import json

async def test_correct_notification_format():
    """Test the correct notification format"""
    
    print("📱 Testing Correct Notification Format")
    print("=" * 60)
    
    endpoint_url = "https://notification-system-h36d.onrender.com/a2a/tasks"
    
    # Test the correct format based on the provided example
    test_request = {
        "jsonrpc": "2.0",
        "id": "bookingHOTEL_001",
        "method": "SendHotelBookingNotification",
        "params": {
            "booking_id": "HOTEL_001",
            "notification_type": "booking_confirmation",
            "recipients": [
                {
                    "email": "patient@example.com",
                    "name": "Rohan",
                    "preferred_method": "email"
                }
            ],
            "hotel_details": {
                "booking_id": "HOTEL_001",
                "hotel_name": "Denver Accessible Suites",
                "hotel_address": "123 Medical Tourism Ave, Denver, CO",
                "check_in_date": "2025-10-12T15:00:00",
                "check_out_date": "2025-10-15T11:00:00",
                "room_type": "Accessible Suite",
                "confirmation_number": "HOTEL_001",
                "guest_name": "John Doe",
                "number_of_guests": 1
            },
            "message": {
                "subject": "Guardian Medical Tourism - Hotel Confirmation",
                "content": "Dear John Doe, your hotel booking has been confirmed for your medical tourism trip."
            },
            "orchestration_id": "ORCH_P001_20251011_121905",
            "priority": "normal"
        }
    }
    
    print("📤 Sending Test Request:")
    print(json.dumps(test_request, indent=2))
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.post(
                endpoint_url,
                json=test_request,
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json"
                }
            )
            
            print(f"\n📥 Response Status: {response.status_code}")
            print(f"Response Headers: {dict(response.headers)}")
            
            response_data = response.json()
            print(f"Response Body: {json.dumps(response_data, indent=2)}")
            
            # Check if it's a valid JSON-RPC response
            if "jsonrpc" in response_data and response_data["jsonrpc"] == "2.0":
                if "result" in response_data:
                    print("✅ SUCCESS! Notification sent successfully")
                    if "notification_id" in response_data["result"]:
                        print(f"📧 Notification ID: {response_data['result']['notification_id']}")
                elif "error" in response_data:
                    print("❌ Error response received")
                    error_code = response_data["error"].get("code", "unknown")
                    error_message = response_data["error"].get("message", "unknown")
                    print(f"   Error Code: {error_code}")
                    print(f"   Error Message: {error_message}")
                else:
                    print("❓ Unexpected JSON-RPC response format")
            else:
                print("❌ Not a valid JSON-RPC 2.0 response")
                
        except httpx.TimeoutException:
            print("❌ Request timed out")
        except httpx.ConnectError:
            print("❌ Connection error - endpoint may be down")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print(f"\n🔗 Testing Orchestrator Integration:")
    print("=" * 60)
    
    # Import and test orchestrator
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
        "hotel_booking_reference": "HOTEL_001",
        "hospital_appointment_id": "MED_APPT_001",
        "hospital_appointment_time": "2025-10-12T14:00:00",
        "emergency_contacts": ["+1-555-111-2222", "+1-555-999-8888"],
        "special_requirements": "Wheelchair accessible, Dietary restrictions",
        "medical_conditions": ["Diabetes", "Hypertension"],
        "age": 72,
        "preferred_language": "English"
    }
    
    print("🚀 Starting orchestration with correct notification format...")
    
    try:
        # Start orchestration (this will call the real notification endpoint)
        orchestration_id = await guardian_orchestrator.start_orchestration(booking_data)
        print(f"✅ Orchestration completed: {orchestration_id}")
        
        # Check if notification was sent successfully
        status = await guardian_orchestrator.get_orchestration_status(orchestration_id)
        if status and "tasks" in status:
            notification_task = status["tasks"].get("notification_coordination")
            if notification_task:
                result = notification_task.get('result', {})
                print(f"📱 Notification Task Result: {result}")
                
                if isinstance(result, dict) and "result" in result:
                    notification_result = result["result"]
                    if "notification_id" in notification_result:
                        print(f"✅ Notification sent successfully! ID: {notification_result['notification_id']}")
                    else:
                        print(f"⚠️ Notification response: {notification_result}")
                elif isinstance(result, dict) and "error" in result:
                    print(f"❌ Notification error: {result['error']}")
                else:
                    print(f"📋 Full notification result: {result}")
            else:
                print("❌ No notification task found in orchestration")
        else:
            print("❌ Could not retrieve orchestration status")
            
    except Exception as e:
        print(f"❌ Orchestration failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_correct_notification_format())
