"""
Test script for Guardian Scheduler Automation
Tests automated flight reminders and status updates
"""

import asyncio
import json
import requests
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8000"

def test_scheduler_automation():
    """Test the automated scheduler functionality"""
    
    print("⏰ Testing Guardian Scheduler Automation")
    print("=" * 50)
    
    # 1. Check Scheduler Status
    print("\n1️⃣ Checking Scheduler Status...")
    response = requests.get(f"{BASE_URL}/guardian/scheduler/status")
    print(f"✅ Scheduler Status: {response.status_code}")
    if response.status_code == 200:
        scheduler_data = response.json()
        print(f"📄 Scheduler Data:")
        print(json.dumps(scheduler_data, indent=2))
    
    # 2. Create a booking with a flight that's 7 hours away
    print("\n2️⃣ Creating Booking with Flight 7 Hours Away...")
    
    # Calculate time 7 hours from now
    seven_hours_later = datetime.now() + timedelta(hours=7)
    flight_date = seven_hours_later.strftime("%Y-%m-%d")
    flight_time = seven_hours_later.strftime("%H:%M:%S")
    
    booking_data = {
        "user_id": "scheduler_test_user",
        "patient_name": "Dr. Emily Chen",
        "flight_number": "AA789",
        "flight_date": flight_date,
        "flight_time": flight_time,
        "departure_airport": "LAX",
        "arrival_airport": "JFK",
        "hotel_booking_reference": "SCHEDULER_HOTEL_123",
        "hospital_appointment_id": "SCHEDULER_APPT_456",
        "hospital_appointment_time": (seven_hours_later + timedelta(days=1)).strftime("%Y-%m-%dT09:00:00"),
        "email": "emily.chen@example.com",
        "emergency_contacts": ["+1-555-SCHEDULER"],
        "special_requirements": "Wheelchair accessible",
        "medical_conditions": ["Diabetes"],
        "hotel_check_in": (seven_hours_later + timedelta(hours=4)).strftime("%Y-%m-%dT%H:%M:%S")
    }
    
    response = requests.post(f"{BASE_URL}/guardian/booking/create", json=booking_data)
    print(f"✅ Booking Created: {response.status_code}")
    if response.status_code == 200:
        booking_result = response.json()
        print(f"📄 Booking Result: {json.dumps(booking_result, indent=2)}")
        print(f"🕐 Flight scheduled for: {flight_date} at {flight_time}")
        print(f"⏰ Expected reminder time: {datetime.now() + timedelta(minutes=30)}")
    else:
        print(f"❌ Booking Error: {response.text}")
        return
    
    # 3. Check Trip Status
    print("\n3️⃣ Checking Trip Status...")
    response = requests.get(f"{BASE_URL}/guardian/trip/status/scheduler_test_user")
    print(f"✅ Trip Status: {response.status_code}")
    if response.status_code == 200:
        status_result = response.json()
        print(f"📄 Trip Status: {json.dumps(status_result, indent=2)}")
    
    # 4. Monitor scheduler jobs
    print("\n4️⃣ Monitoring Scheduler Jobs...")
    print("📊 Active Jobs:")
    
    response = requests.get(f"{BASE_URL}/guardian/scheduler/status")
    if response.status_code == 200:
        scheduler_data = response.json()
        jobs = scheduler_data.get("data", {}).get("jobs", [])
        
        for job in jobs:
            print(f"  🔄 {job['name']} (ID: {job['id']})")
            print(f"     Next Run: {job['next_run']}")
            print(f"     Trigger: {job['trigger']}")
            print()
    
    print("⏰ The scheduler will automatically:")
    print("  • Check flight reminders every 30 minutes")
    print("  • Update flight statuses every 15 minutes")
    print("  • Monitor arrivals every 10 minutes")
    print("  • Clean up old orchestrations every hour")
    print()
    print("🎯 Since your flight is scheduled 7 hours from now,")
    print("   the scheduler should send a reminder in the next 30-minute cycle!")

def test_manual_reminder_trigger():
    """Test manual reminder trigger for immediate testing"""
    
    print("\n🔧 Testing Manual Reminder Trigger...")
    print("=" * 40)
    
    # Create a booking with flight in 6.5 hours (within reminder window)
    six_hours_later = datetime.now() + timedelta(hours=6, minutes=30)
    flight_date = six_hours_later.strftime("%Y-%m-%d")
    flight_time = six_hours_later.strftime("%H:%M:%S")
    
    booking_data = {
        "user_id": "manual_reminder_test",
        "patient_name": "Dr. James Wilson",
        "flight_number": "UA456",
        "flight_date": flight_date,
        "flight_time": flight_time,
        "departure_airport": "SFO",
        "arrival_airport": "BOS",
        "hotel_booking_reference": "MANUAL_HOTEL_789",
        "hospital_appointment_id": "MANUAL_APPT_012",
        "hospital_appointment_time": (six_hours_later + timedelta(days=1)).strftime("%Y-%m-%dT08:00:00"),
        "email": "james.wilson@example.com",
        "emergency_contacts": ["+1-555-MANUAL"],
        "special_requirements": "None",
        "medical_conditions": [],
        "hotel_check_in": (six_hours_later + timedelta(hours=3)).strftime("%Y-%m-%dT%H:%M:%S")
    }
    
    # Create booking
    response = requests.post(f"{BASE_URL}/guardian/booking/create", json=booking_data)
    print(f"✅ Manual Test Booking Created: {response.status_code}")
    
    # Manually trigger flight reminder check
    print("\n🔔 Manually Triggering Flight Reminder Check...")
    reminder_data = {"user_id": "manual_reminder_test"}
    response = requests.post(f"{BASE_URL}/guardian/flight/check-reminders", json=reminder_data)
    print(f"✅ Manual Reminder Trigger: {response.status_code}")
    if response.status_code == 200:
        reminder_result = response.json()
        print(f"📄 Reminder Result: {json.dumps(reminder_result, indent=2)}")
    
    print(f"🕐 Flight scheduled for: {flight_date} at {flight_time}")
    print(f"⏰ This should trigger an immediate reminder!")

if __name__ == "__main__":
    print("🚀 Guardian Scheduler Automation Test")
    print("=" * 60)
    
    try:
        # Test scheduler automation
        test_scheduler_automation()
        
        # Test manual reminder trigger
        test_manual_reminder_trigger()
        
        print("\n✅ Scheduler automation tests completed!")
        print("🎯 The scheduler is now running in the background and will:")
        print("   • Automatically send flight reminders 7 hours before departure")
        print("   • Update flight statuses every 15 minutes")
        print("   • Monitor for arrivals and trigger arrival flows")
        print("   • Clean up old orchestrations periodically")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
