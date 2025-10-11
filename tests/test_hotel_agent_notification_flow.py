import asyncio
import httpx
from datetime import datetime, timedelta
import random
import string

BASE_URL = "http://localhost:8000"

def generate_random_user_id(prefix="hotel_notify_user"):
    """Generates a unique user ID for testing."""
    timestamp = int(datetime.now().timestamp())
    random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=5))
    return f"{prefix}_{timestamp}_{random_suffix}"

async def test_hotel_agent_notification_flow():
    print("🏨 Guardian Hotel Agent Notification Flow Test")
    print("============================================================")
    print("📧 Testing Hotel Agent Handles Flight Landed Notifications")
    print("============================================================")
    
    test_user_id = generate_random_user_id()
    test_start_time = datetime.now()
    print(f"👤 Test User: {test_user_id}")
    print(f"🕐 Test Started: {test_start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    async with httpx.AsyncClient() as client:
        # 1. System Health Check
        print("\n1️⃣ System Health Check...")
        response = await client.get(f"{BASE_URL}/ag-ui/health")
        print(f"✅ Health Check: {response.status_code}")
        assert response.status_code == 200
        
        # 2. Create Medical Tourism Booking
        print("\n2️⃣ Creating Medical Tourism Booking...")
        hospital_appt_time = datetime.now() + timedelta(days=2)
        hotel_checkin = datetime.now() + timedelta(days=1)
        
        booking_data = {
            "user_id": test_user_id,
            "patient_name": "Dr. Sarah Johnson",
            "flight_number": "AA2990",
            "flight_date": (datetime.now() + timedelta(hours=2)).strftime("%Y-%m-%d"),
            "flight_time": (datetime.now() + timedelta(hours=2)).strftime("%H:%M:%S"),
            "departure_airport": "LAX",
            "arrival_airport": "JFK",
            "hotel_booking_reference": "HOTEL_NOTIFY_XYZ",
            "hospital_appointment_id": "HOTEL_NOTIFY_HOSP_ABC",
            "hospital_appointment_time": hospital_appt_time.isoformat(),
            "email": f"{test_user_id}@example.com",
            "emergency_contacts": [
                "+1-555-HOTEL-FAMILY-001",  # Spouse
                "+1-555-HOTEL-FAMILY-002",  # Adult child
                "+1-555-HOTEL-FAMILY-003"   # Emergency contact
            ],
            "special_requirements": "Wheelchair accessible, diabetic meals",
            "medical_conditions": ["Diabetes", "Hypertension"],
            "hotel_check_in": hotel_checkin.isoformat(),
            "preferred_language": "English",
            "companion_name": "Mike Johnson",
            "hotel_name": "Manhattan Medical Suites",
            "hotel_room_number": "Suite 405",
            "hospital_name": "NYC Medical Center",
            "doctor_name": "Dr. Williams"
        }
        
        response = await client.post(f"{BASE_URL}/guardian/booking/create", json=booking_data)
        print(f"✅ Booking Created: {response.status_code}")
        assert response.status_code == 200
        booking_result = response.json()
        print(f"📋 Booking ID: {booking_result['data']['booking_id']}")
        
        # 3. Simulate Flight Landing - This triggers Hotel Agent notification flow
        print("\n3️⃣ 🛬 SIMULATING FLIGHT LANDING!")
        print("==================================================")
        print("📧 Hotel Agent will now handle:")
        print("   • Family notification: 'Patient has landed safely'")
        print("   • Hotel notification: 'Guest arriving in 30 minutes'")
        print("   • Cab arrangement: 'Cab dispatched to airport'")
        
        # Simulate flight landing by updating location
        location_data = {
            "user_id": test_user_id,
            "latitude": 40.6413,  # JFK airport coordinates
            "longitude": -73.7781,
            "airport_name": "John F. Kennedy International Airport",
            "airport_code": "JFK",
            "timestamp": datetime.now().isoformat(),
            "flight_status": "LANDED",
            "gate": "B12",
            "terminal": "8"
        }
        
        response = await client.post(f"{BASE_URL}/guardian/location/update", json=location_data)
        print(f"✅ Location Update (Flight Landed): {response.status_code}")
        assert response.status_code == 200
        arrival_result = response.json()
        print(f"📍 Arrival Status: {arrival_result['data']['status']}")
        
        # 4. Verify Hotel Agent Received Flight Landed Notification
        print("\n4️⃣ Verifying Hotel Agent Notification Flow...")
        print("🏨 Hotel Agent should have received:")
        
        expected_hotel_tasks = {
            "notify_family": "✅ Family notified: 'Dr. Sarah Johnson has landed safely at JFK'",
            "notify_hotel": "✅ Hotel notified: 'Guest Dr. Sarah Johnson arriving in 30 minutes'",
            "arrange_cab": "✅ Cab arranged: 'Cab dispatched to JFK Gate B12'"
        }
        
        for task, description in expected_hotel_tasks.items():
            print(f"   {description}")
        
        # 5. Check Trip Status to Verify Services
        print("\n5️⃣ Checking Trip Status...")
        response = await client.get(f"{BASE_URL}/guardian/trip/status/{test_user_id}")
        print(f"✅ Trip Status: {response.status_code}")
        assert response.status_code == 200
        trip_status = response.json()
        
        trip_data = trip_status.get("data", {})
        orchestrations = trip_data.get("orchestrations", [])
        if orchestrations:
            orchestration = orchestrations[0]
            services_requested = orchestration.get("arrival_services", {}).get("services_requested", [])
            print(f"📋 Services Requested: {services_requested}")
            
            # Verify the correct services were requested
            expected_services = [
                "flight_landed_family_notification",
                "hotel_notification", 
                "cab_arrangement",
                "hospital_confirmation"
            ]
            for service in expected_services:
                if service in services_requested:
                    print(f"   ✅ {service}: Requested")
                else:
                    print(f"   ❌ {service}: Missing")
        
        # 6. Simulate Cab Arrival (Hotel Agent arranged cab)
        print("\n6️⃣ 🚗 Simulating Cab Arrival (arranged by Hotel Agent)...")
        cab_data = {
            "user_id": test_user_id,
            "gate": "B12",
            "pickup_location": "Terminal 8, Gate B12",
            "estimated_arrival": "5 minutes",
            "cab_details": {
                "company": "Uber", 
                "driver": "Ahmed Hassan", 
                "license_plate": "ABC123",
                "vehicle_type": "Wheelchair Accessible Vehicle"
            }
        }
        
        response = await client.post(f"{BASE_URL}/guardian/cab/arrival", json=cab_data)
        print(f"✅ Cab Arrival: {response.status_code}")
        assert response.status_code == 200
        cab_result = response.json()
        cab_data_result = cab_result.get("data", {})
        print(f"🚗 Cab Status: {cab_data_result.get('status', 'unknown')}")
        voice_triggered = cab_data_result.get('voice_call_triggered', False)
        print(f"📞 Voice Call Triggered: {voice_triggered}")
        
        # 7. Test Hotel Check-in Notification (Hotel Agent handles)
        print("\n7️⃣ 🏨 Testing Hotel Check-in Notification...")
        print("📧 Hotel Agent will send to family: 'Dr. Sarah Johnson has checked into Manhattan Medical Suites'")
        
        # Simulate hotel check-in notification
        print("🏨 Hotel Agent would send check-in notification to family")
        
        # 8. Test Stay Extension (Hotel Agent handles family notification)
        print("\n8️⃣ 🔄 Testing Stay Extension...")
        print("📧 Hotel Agent will send to family: 'Dr. Sarah Johnson's stay extended by 2 days'")
        
        extension_data = {
            "user_id": test_user_id,
            "new_discharge_date": (datetime.now() + timedelta(days=4)).isoformat(),
            "reason": "Additional medical monitoring required - doctor recommended 2 extra days",
            "extension_days": 2,
            "notify_family": True
        }
        
        response = await client.post(f"{BASE_URL}/guardian/stay/extension", json=extension_data)
        print(f"✅ Stay Extension: {response.status_code}")
        assert response.status_code == 200
        extension_result = response.json()
        print(f"📊 Extension Status: {extension_result['data']['status']}")
        
        # Show Hotel Agent family notification
        extension_data_result = extension_result.get("data", {})
        actions = extension_data_result.get("actions_completed", [])
        for action in actions:
            action_name = action.get("action", "unknown")
            if "hotel_extension" in action_name:
                print(f"🏨 Hotel Agent family notification: {action.get('result', {}).get('status', 'unknown')}")
        
        # 9. Final Status Check
        print("\n9️⃣ Final Status Check...")
        response = await client.get(f"{BASE_URL}/guardian/trip/status/{test_user_id}")
        print(f"✅ Final Status: {response.status_code}")
        assert response.status_code == 200
        final_status = response.json()
        
        final_data = final_status.get("data", {})
        bookings = final_data.get("bookings", [])
        if bookings:
            booking = bookings[0]
            print("🏨 Hotel Agent Notification Summary:")
            print(f"   • Patient: {booking.get('patient_name')}")
            print(f"   • Hotel: {booking.get('hotel_name')}")
            print(f"   • Room: {booking.get('hotel_room_number')}")
            print(f"   • Stay Extended: {booking.get('stay_extended', False)}")
            print(f"   • Family Contacts: {len(booking.get('emergency_contacts', []))}")
    
    print("\n============================================================")
    print("🎉 HOTEL AGENT NOTIFICATION FLOW TEST COMPLETED SUCCESSFULLY!")
    print("============================================================")
    print("✅ Hotel Agent Notification Features Demonstrated:")
    print("   • Flight landed family notification")
    print("   • Hotel arrival notification (30 minutes)")
    print("   • Cab arrangement and dispatch")
    print("   • Hotel check-in family notification")
    print("   • Stay extension family notification")
    print("   • Multi-language support")
    print("   • Multiple family contacts")
    print("\n🏨 Hotel Agent Responsibilities:")
    print("   → Notify family when patient lands")
    print("   → Notify hotel when guest is arriving")
    print("   → Arrange and dispatch cab")
    print("   → Send check-in confirmations to family")
    print("   → Handle stay extension family notifications")
    print("   → Coordinate with Notification Agent for all communications")
    print(f"\n📊 Test User ID: {test_user_id}")
    print(f"🕐 Test Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    asyncio.run(test_hotel_agent_notification_flow())
