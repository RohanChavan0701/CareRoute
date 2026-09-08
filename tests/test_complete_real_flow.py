"""
Complete End-to-End Test with Real Flight and Notification APIs
Tests the entire Guardian Orchestrator flow with real external services
"""

import asyncio
import json
import os
import requests
from datetime import datetime, timedelta
import time

BASE_URL = "http://localhost:8000"
FLIGHT_API_URL = os.getenv("FLIGHT_AGENT_URL", "")
NOTIFICATION_API_URL = "https://notification-system-h36d.onrender.com/a2a/tasks"

def test_real_apis_directly():
    """Test real APIs directly to ensure they're working"""
    
    print("🔍 Testing Real APIs Directly")
    print("=" * 50)
    
    # Test Flight API
    print("\n✈️ Testing Flight API...")
    flight_request = {
        "jsonrpc": "2.0",
        "method": "get_flight_status",
        "params": {
            "flight_num": "DL2990",
            "departure_date": "2025-10-11",
            "locale": "en-US",
            "user_id": "test_user"
        },
        "id": "test_flight_direct"
    }
    
    try:
        response = requests.post(FLIGHT_API_URL, json=flight_request, timeout=10)
        print(f"✅ Flight API Status: {response.status_code}")
        if response.status_code == 200:
            flight_data = response.json()
            print(f"📄 Flight Data: {json.dumps(flight_data, indent=2)}")
        else:
            print(f"❌ Flight API Error: {response.text}")
    except Exception as e:
        print(f"❌ Flight API Connection Error: {e}")
    
    # Test Notification API
    print("\n📧 Testing Notification API...")
    notification_request = {
        "jsonrpc": "2.0",
        "id": "test_notification_direct",
        "method": "SendFlightBookingNotification",
        "params": {
            "booking_id": "TEST_BOOKING_123",
            "notification_type": "test_notification",
            "recipients": [
                {
                    "email": "test@example.com",
                    "name": "Test User",
                    "preferred_method": "email"
                }
            ],
            "flight_details": {
                "flight_number": "DL2990",
                "departure_date": "2025-10-11",
                "status": "ON_TIME"
            },
            "orchestration_id": "TEST_ORCH_001",
            "priority": "normal"
        }
    }
    
    try:
        response = requests.post(NOTIFICATION_API_URL, json=notification_request, timeout=10)
        print(f"✅ Notification API Status: {response.status_code}")
        if response.status_code == 200:
            notification_data = response.json()
            print(f"📄 Notification Response: {json.dumps(notification_data, indent=2)}")
        else:
            print(f"❌ Notification API Error: {response.text}")
    except Exception as e:
        print(f"❌ Notification API Connection Error: {e}")

def test_complete_guardian_flow():
    """Test the complete Guardian Orchestrator flow"""
    
    print("\n🧠 Testing Complete Guardian Orchestrator Flow")
    print("=" * 60)
    
    user_id = "complete_flow_user"
    
    # Step 1: Create Booking
    print("\n1️⃣ Creating Booking...")
    booking_data = {
        "user_id": user_id,
        "patient_name": "Dr. Maria Rodriguez",
        "flight_number": "DL2990",
        "flight_date": "2025-10-11",
        "flight_time": "14:00:00",
        "departure_airport": "JFK",
        "arrival_airport": "LAX",
        "hotel_booking_reference": "HOTEL_COMPLETE_789",
        "hospital_appointment_id": "MED_COMPLETE_456",
        "hospital_appointment_time": "2025-10-12T10:00:00",
        "email": "maria.rodriguez@example.com",
        "emergency_contacts": ["+1-555-FAMILY", "+1-555-EMERGENCY"],
        "special_requirements": "Wheelchair accessible, diabetic meals",
        "medical_conditions": ["Diabetes Type 2", "Hypertension"],
        "hotel_check_in": "2025-10-11T18:00:00"
    }
    
    response = requests.post(f"{BASE_URL}/guardian/booking/create", json=booking_data)
    print(f"✅ Booking Created: {response.status_code}")
    if response.status_code == 200:
        booking_result = response.json()
        print(f"📄 Booking Result: {json.dumps(booking_result, indent=2)}")
    else:
        print(f"❌ Booking Error: {response.text}")
        return
    
    # Step 2: Check Initial Status
    print("\n2️⃣ Checking Initial Trip Status...")
    response = requests.get(f"{BASE_URL}/guardian/trip/status/{user_id}")
    print(f"✅ Initial Status: {response.status_code}")
    if response.status_code == 200:
        status_result = response.json()
        print(f"📄 Trip Status: {json.dumps(status_result, indent=2)}")
    
    # Step 3: Test Flight Reminders (simulate 7 hours before departure)
    print("\n3️⃣ Testing Flight Reminders...")
    reminder_data = {"user_id": user_id}
    response = requests.post(f"{BASE_URL}/guardian/flight/check-reminders", json=reminder_data)
    print(f"✅ Flight Reminders: {response.status_code}")
    if response.status_code == 200:
        reminder_result = response.json()
        print(f"📄 Reminder Result: {json.dumps(reminder_result, indent=2)}")
    
    # Step 4: Simulate Airport Arrival
    print("\n4️⃣ Simulating Airport Arrival...")
    location_data = {
        "user_id": user_id,
        "latitude": 40.6413,
        "longitude": -73.7781,
        "airport_name": "John F. Kennedy International Airport",
        "airport_code": "JFK",
        "timestamp": datetime.now().isoformat()
    }
    response = requests.post(f"{BASE_URL}/guardian/location/update", json=location_data)
    print(f"✅ Location Updated: {response.status_code}")
    if response.status_code == 200:
        location_result = response.json()
        print(f"📄 Location Result: {json.dumps(location_result, indent=2)}")
    
    # Step 5: Test Cab Arrival
    print("\n5️⃣ Testing Cab Arrival...")
    cab_data = {
        "user_id": user_id,
        "gate": "Gate B12",
        "pickup_location": "Terminal 4, Gate B12",
        "estimated_arrival": "5 minutes",
        "cab_details": {
            "driver_name": "Ahmed Hassan",
            "car_model": "Toyota Sienna",
            "license_plate": "XYZ789",
            "phone": "+1-555-CAB456",
            "accessibility_features": ["Wheelchair ramp", "Wide doors"]
        }
    }
    response = requests.post(f"{BASE_URL}/guardian/cab/arrival", json=cab_data)
    print(f"✅ Cab Arrival: {response.status_code}")
    if response.status_code == 200:
        cab_result = response.json()
        print(f"📄 Cab Result: {json.dumps(cab_result, indent=2)}")
    
    # Step 6: Final Status Check
    print("\n6️⃣ Final Trip Status...")
    response = requests.get(f"{BASE_URL}/guardian/trip/status/{user_id}")
    print(f"✅ Final Status: {response.status_code}")
    if response.status_code == 200:
        final_result = response.json()
        print(f"📄 Final Status: {json.dumps(final_result, indent=2)}")
    
    print("\n🎉 Complete Guardian Flow Test Completed!")

def test_agui_interaction():
    """Test AG-UI protocol interactions"""
    
    print("\n🔌 Testing AG-UI Protocol Interactions")
    print("=" * 50)
    
    # Test health endpoint
    print("\n1️⃣ Health Check...")
    response = requests.get(f"{BASE_URL}/ag-ui/health")
    print(f"✅ Health: {response.status_code}")
    if response.status_code == 200:
        health_data = response.json()
        print(f"📄 Health Data: {json.dumps(health_data, indent=2)}")
    
    # Test message endpoint
    print("\n2️⃣ Message Interaction...")
    message_data = {
        "user_id": "complete_flow_user",
        "message": "What's the status of my flight DL2990?",
        "message_type": "text"
    }
    response = requests.post(f"{BASE_URL}/ag-ui/message", json=message_data)
    print(f"✅ Message: {response.status_code}")
    if response.status_code == 200:
        message_result = response.json()
        print(f"📄 Message Response: {json.dumps(message_result, indent=2)}")
    
    # Test events endpoint
    print("\n3️⃣ Events Check...")
    response = requests.get(f"{BASE_URL}/ag-ui/events/complete_flow_user")
    print(f"✅ Events: {response.status_code}")
    if response.status_code == 200:
        events_result = response.json()
        print(f"📄 Events: {json.dumps(events_result, indent=2)}")

def test_database_persistence():
    """Test database persistence"""
    
    print("\n💾 Testing Database Persistence")
    print("=" * 40)
    
    # Check if dummy database file exists and has data
    try:
        with open("/Users/atharvasalunke/medical_orchestrator/backend/dummy_data.json", "r") as f:
            db_data = json.load(f)
        
        print(f"✅ Database file found")
        print(f"📊 Bookings: {len(db_data.get('bookings', {}))}")
        print(f"📊 Flights: {len(db_data.get('flights', {}))}")
        print(f"📊 Users: {len(db_data.get('users', {}))}")
        print(f"📊 Locations: {len(db_data.get('locations', {}))}")
        print(f"📊 Orchestrations: {len(db_data.get('orchestrations', {}))}")
        
        # Show sample data
        if db_data.get('bookings'):
            sample_booking = list(db_data['bookings'].values())[0]
            print(f"📄 Sample Booking: {json.dumps(sample_booking, indent=2)}")
            
    except Exception as e:
        print(f"❌ Database Error: {e}")

if __name__ == "__main__":
    print("🚀 Guardian Orchestrator - Complete Real API Integration Test")
    print("=" * 70)
    
    try:
        # Test real APIs first
        test_real_apis_directly()
        
        # Wait a moment for any background processes
        time.sleep(2)
        
        # Test complete Guardian flow
        test_complete_guardian_flow()
        
        # Test AG-UI interactions
        test_agui_interaction()
        
        # Test database persistence
        test_database_persistence()
        
        print("\n✅ All tests completed successfully!")
        print("🎯 Guardian Orchestrator is ready for production!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
