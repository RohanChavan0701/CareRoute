#!/usr/bin/env python3
"""
Test FCM Endpoints for Real-time Updates
"""

import asyncio
import httpx
import json

async def test_fcm_endpoints():
    """Test all FCM endpoints"""
    
    base_url = "http://localhost:8000"
    
    print("🧪 Testing FCM Endpoints")
    print("=" * 30)
    
    # 1. Register FCM token
    print("\n1️⃣ Registering FCM Token...")
    register_data = {
        "user_id": "PAT-12345",
        "device_token": "DEMO_FCM_TOKEN_12345"
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(f"{base_url}/fcm/register", json=register_data)
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.json()}")
        except Exception as e:
            print(f"   Error: {e}")
    
    # 2. Send boarding reminder
    print("\n2️⃣ Sending Boarding Reminder...")
    boarding_data = {
        "user_id": "PAT-12345",
        "flight_info": {
            "flight_number": "AI101",
            "boarding_time": "45 minutes",
            "gate": "B12"
        }
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(f"{base_url}/fcm/send-boarding-reminder", json=boarding_data)
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.json()}")
        except Exception as e:
            print(f"   Error: {e}")
    
    # 3. Send flight update
    print("\n3️⃣ Sending Flight Update...")
    flight_data = {
        "user_id": "PAT-12345",
        "flight_info": {
            "flight_number": "AI101",
            "status": "On Time",
            "gate": "B12"
        }
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(f"{base_url}/fcm/send-flight-update", json=flight_data)
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.json()}")
        except Exception as e:
            print(f"   Error: {e}")
    
    # 4. Send cab notification
    print("\n4️⃣ Sending Cab Notification...")
    cab_data = {
        "user_id": "PAT-12345",
        "cab_info": {
            "driver_name": "Alex Johnson",
            "vehicle": "Tesla Model S",
            "eta": "15 minutes",
            "hotel_name": "JW Marriott Hotel",
            "patient_name": "Rohan Chavan"
        }
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(f"{base_url}/fcm/send-cab-notification", json=cab_data)
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.json()}")
        except Exception as e:
            print(f"   Error: {e}")
    
    # 5. Send appointment reminder
    print("\n5️⃣ Sending Appointment Reminder...")
    appointment_data = {
        "user_id": "PAT-12345",
        "appointment_info": {
            "doctor_name": "Dr. Meera Singh",
            "hospital_name": "Apollo Medical Center",
            "appointment_time": "09:30 AM"
        }
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(f"{base_url}/fcm/send-appointment-reminder", json=appointment_data)
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.json()}")
        except Exception as e:
            print(f"   Error: {e}")
    
    print("\n✅ FCM Endpoints Test Completed!")

if __name__ == "__main__":
    asyncio.run(test_fcm_endpoints())
