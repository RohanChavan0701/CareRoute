"""
Test script for Guardian Orchestrator with Real Flight API
Tests the complete trip flow using real flight data
"""

import asyncio
import json
import requests
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8000"
FLIGHT_API_URL = "http://54.158.27.0:8001/a2a"

def test_real_flight_api():
    """Test the real flight API directly"""
    
    print("✈️ Testing Real Flight API")
    print("=" * 40)
    
    # Test flight status request
    flight_request = {
        "jsonrpc": "2.0",
        "method": "get_flight_status",
        "params": {
            "flight_num": "DL2990",
            "departure_date": "2025-10-11",
            "locale": "en-US",
            "user_id": "test_user_123"
        },
        "id": "test_flight_123"
    }
    
    print("📡 Sending request to real flight API...")
    response = requests.post(FLIGHT_API_URL, json=flight_request)
    
    print(f"✅ Response Status: {response.status_code}")
    print(f"📄 Response Data:")
    print(json.dumps(response.json(), indent=2))
    
    return response.json()

def test_guardian_with_real_flight():
    """Test Guardian orchestrator with real flight data"""
    
    print("\n🧠 Testing Guardian Orchestrator with Real Flight Data")
    print("=" * 60)
    
    # Test user data with real flight
    user_id = "real_flight_user"
    
    # 1. Create Booking with real flight
    print("\n1️⃣ Creating Booking with Real Flight...")
    booking_data = {
        "user_id": user_id,
        "patient_name": "Sarah Johnson",
        "flight_number": "DL2990",
        "flight_date": "2025-10-11",
        "flight_time": "14:00:00",
        "departure_airport": "JFK",
        "arrival_airport": "LAX",
        "hotel_booking_reference": "HOTEL_REAL_456",
        "hospital_appointment_id": "MED_REAL_789",
        "hospital_appointment_time": "2025-10-12T09:00:00",
        "email": "sarah.johnson@example.com",
        "emergency_contacts": ["+1-555-FAMILY"],
        "special_requirements": "Wheelchair accessible",
        "medical_conditions": ["Diabetes"],
        "hotel_check_in": "2025-10-11T18:00:00"
    }
    
    response = requests.post(f"{BASE_URL}/guardian/booking/create", json=booking_data)
    print(f"✅ Booking Created: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    # 2. Check Trip Status
    print("\n2️⃣ Checking Trip Status...")
    response = requests.get(f"{BASE_URL}/guardian/trip/status/{user_id}")
    print(f"✅ Trip Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    # 3. Test Flight Reminders (simulate 7 hours before departure)
    print("\n3️⃣ Testing Flight Reminders...")
    reminder_data = {"user_id": user_id}
    response = requests.post(f"{BASE_URL}/guardian/flight/check-reminders", json=reminder_data)
    print(f"✅ Flight Reminders: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    # 4. Simulate Arrival at Airport
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
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    # 5. Test Cab Arrival
    print("\n5️⃣ Testing Cab Arrival...")
    cab_data = {
        "user_id": user_id,
        "gate": "Gate B12",
        "pickup_location": "Terminal 4, Gate B12",
        "estimated_arrival": "10 minutes",
        "cab_details": {
            "driver_name": "Ahmed Hassan",
            "car_model": "Toyota Sienna",
            "license_plate": "XYZ789",
            "phone": "+1-555-CAB456"
        }
    }
    response = requests.post(f"{BASE_URL}/guardian/cab/arrival", json=cab_data)
    print(f"✅ Cab Arrival: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    # 6. Final Status Check
    print("\n6️⃣ Final Trip Status...")
    response = requests.get(f"{BASE_URL}/guardian/trip/status/{user_id}")
    print(f"✅ Final Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    print("\n🎉 Real Flight API Integration Test Completed!")
    print("=" * 60)

def test_agui_with_real_flight():
    """Test AG-UI endpoints with flight queries"""
    
    print("\n🔌 Testing AG-UI with Flight Queries")
    print("=" * 40)
    
    # Test flight status query
    print("\n1️⃣ Flight Status Query...")
    message_data = {
        "user_id": "real_flight_user",
        "message": "What's the status of flight DL2990?",
        "message_type": "text"
    }
    response = requests.post(f"{BASE_URL}/ag-ui/message", json=message_data)
    print(f"✅ Flight Query: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    # Test trip planning query
    print("\n2️⃣ Trip Planning Query...")
    message_data = {
        "user_id": "real_flight_user",
        "message": "When should I arrive at the airport for my flight?",
        "message_type": "text"
    }
    response = requests.post(f"{BASE_URL}/ag-ui/message", json=message_data)
    print(f"✅ Trip Planning: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

if __name__ == "__main__":
    print("🚀 Guardian Orchestrator - Real Flight API Integration Test")
    print("=" * 70)
    
    try:
        # Test real flight API first
        flight_response = test_real_flight_api()
        
        # Test Guardian with real flight data
        test_guardian_with_real_flight()
        
        # Test AG-UI with flight queries
        test_agui_with_real_flight()
        
        print("\n✅ All real flight API tests completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
