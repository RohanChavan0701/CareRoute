"""
Test script for complete Guardian trip flow
Tests the entire user journey from booking to arrival
"""

import asyncio
import json
import requests
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8000"

def test_complete_trip_flow():
    """Test the complete trip flow from booking to arrival"""
    
    print("🧪 Testing Complete Guardian Trip Flow")
    print("=" * 50)
    
    # Test user data
    user_id = "test_user_123"
    
    # 1. Create Booking
    print("\n1️⃣ Creating Booking...")
    booking_data = {
        "user_id": user_id,
        "patient_name": "John Doe",
        "flight_number": "AA1234",
        "flight_date": (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d"),
        "flight_time": "14:30:00",
        "departure_airport": "JFK",
        "arrival_airport": "LAX",
        "hotel_booking_reference": "HOTEL_REF_123",
        "hospital_appointment_id": "MED_APPT_456",
        "hospital_appointment_time": (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%dT09:00:00"),
        "email": "john.doe@example.com",
        "emergency_contacts": ["+1-555-FAMILY"],
        "special_requirements": "Wheelchair accessible",
        "medical_conditions": ["Diabetes", "Hypertension"],
        "hotel_check_in": (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%dT15:00:00")
    }
    
    response = requests.post(f"{BASE_URL}/guardian/booking/create", json=booking_data)
    print(f"✅ Booking Created: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    # 2. Check Trip Status
    print("\n2️⃣ Checking Trip Status...")
    response = requests.get(f"{BASE_URL}/guardian/trip/status/{user_id}")
    print(f"✅ Trip Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    # 3. Check Flight Reminders (simulate 7 hours before departure)
    print("\n3️⃣ Checking Flight Reminders...")
    reminder_data = {"user_id": user_id}
    response = requests.post(f"{BASE_URL}/guardian/flight/check-reminders", json=reminder_data)
    print(f"✅ Flight Reminders: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    # 4. Update User Location (simulate arrival at airport)
    print("\n4️⃣ Updating User Location (Airport Arrival)...")
    location_data = {
        "user_id": user_id,
        "latitude": 33.9425,
        "longitude": -118.4081,
        "airport_name": "Los Angeles International Airport",
        "airport_code": "LAX",
        "timestamp": datetime.now().isoformat()
    }
    response = requests.post(f"{BASE_URL}/guardian/location/update", json=location_data)
    print(f"✅ Location Updated: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    # 5. Handle Cab Arrival
    print("\n5️⃣ Handling Cab Arrival...")
    cab_data = {
        "user_id": user_id,
        "gate": "Gate A1",
        "pickup_location": "Terminal 1, Gate A1",
        "estimated_arrival": "5 minutes",
        "cab_details": {
            "driver_name": "Mike Johnson",
            "car_model": "Toyota Camry",
            "license_plate": "ABC123",
            "phone": "+1-555-CAB123"
        }
    }
    response = requests.post(f"{BASE_URL}/guardian/cab/arrival", json=cab_data)
    print(f"✅ Cab Arrival: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    # 6. Final Trip Status
    print("\n6️⃣ Final Trip Status...")
    response = requests.get(f"{BASE_URL}/guardian/trip/status/{user_id}")
    print(f"✅ Final Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    print("\n🎉 Complete Trip Flow Test Completed!")
    print("=" * 50)

def test_agui_endpoints():
    """Test AG-UI protocol endpoints"""
    
    print("\n🔌 Testing AG-UI Protocol Endpoints")
    print("=" * 50)
    
    # Health check
    print("\n1️⃣ Health Check...")
    response = requests.get(f"{BASE_URL}/ag-ui/health")
    print(f"✅ Health: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    # Send message
    print("\n2️⃣ Send Message...")
    message_data = {
        "user_id": "test_user_123",
        "message": "What's my flight status?",
        "message_type": "text"
    }
    response = requests.post(f"{BASE_URL}/ag-ui/message", json=message_data)
    print(f"✅ Message: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    # Get events
    print("\n3️⃣ Get Events...")
    response = requests.get(f"{BASE_URL}/ag-ui/events/test_user_123")
    print(f"✅ Events: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

if __name__ == "__main__":
    print("🚀 Guardian Orchestrator - Complete Trip Flow Test")
    print("=" * 60)
    
    try:
        # Test AG-UI endpoints first
        test_agui_endpoints()
        
        # Test complete trip flow
        test_complete_trip_flow()
        
        print("\n✅ All tests completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
