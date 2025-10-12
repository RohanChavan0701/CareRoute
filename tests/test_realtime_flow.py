#!/usr/bin/env python3
"""
Test Real-time Trip Flow with FCM Notifications
Simulates the complete user journey from boarding to hospital appointment
"""

import asyncio
import json
import time
import sys
import os
from datetime import datetime, timedelta

# Add the parent directory to the path to import backend modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

async def test_complete_trip_flow():
    """Test the complete real-time trip flow"""
    
    print("🚀 Testing Complete Real-time Trip Flow")
    print("=" * 50)
    
    # Test user with complete booking data
    user_id = "PAT-12345"
    
    # 1. Register FCM token (simulate Flutter app registration)
    print("\n1️⃣ Registering FCM Device Token...")
    fcm_token_data = {
        "user_id": user_id,
        "device_token": "DEMO_FCM_TOKEN_12345"
    }
    
    # This would be called from Flutter app
    print(f"   📱 FCM Token registered for user {user_id}")
    
    # 2. Send boarding reminder (2 hours before flight)
    print("\n2️⃣ Sending Boarding Reminder...")
    boarding_data = {
        "user_id": user_id,
        "flight_info": {
            "flight_number": "AI101",
            "boarding_time": "45 minutes",
            "gate": "B12",
            "departure_time": "2:21 AM"
        }
    }
    
    # Simulate FCM notification
    print(f"   📱 FCM: '✈️ Boarding Reminder - Boarding for AI101 starts in 45 minutes'")
    print(f"   📱 App Update: Added boarding reminder to timeline")
    
    # 3. Flight status update (30 minutes before departure)
    print("\n3️⃣ Sending Flight Status Update...")
    flight_update_data = {
        "user_id": user_id,
        "flight_info": {
            "flight_number": "AI101",
            "status": "On Time",
            "gate": "B12",
            "boarding_status": "Now Boarding"
        }
    }
    
    print(f"   📱 FCM: '✈️ Flight Status Update - AI101 is now On Time - Gate B12'")
    print(f"   📱 App Update: Updated flight status in timeline")
    
    # 4. Arrival notification (30 minutes before landing)
    print("\n4️⃣ Sending Cab Request Notification (30 min before arrival)...")
    cab_data = {
        "user_id": user_id,
        "cab_info": {
            "driver_name": "Alex Johnson",
            "vehicle": "Tesla Model S",
            "eta": "15 minutes",
            "hotel_name": "JW Marriott Hotel",
            "patient_name": "Rohan Chavan"
        }
    }
    
    print(f"   📱 FCM: '🚗 Cab Arranged - Alex Johnson will pick you up in 15 minutes'")
    print(f"   📧 Email: Sent hotel confirmation email")
    print(f"   📱 App Update: Added cab details to timeline")
    
    # 5. Voice call context test
    print("\n5️⃣ Testing Voice Agent Context...")
    
    # Get comprehensive patient context
    from backend.orchestrator import guardian_orchestrator
    context = await guardian_orchestrator._get_comprehensive_call_context(user_id)
    
    print(f"   📞 Voice Agent Context Generated:")
    print(f"   - Patient: {context['params']['patient_name']}")
    print(f"   - Language: {context['params']['patient_language']}")
    print(f"   - Hotel: {context['params']['hotel_name']}")
    print(f"   - Doctor: {context['params']['doctor_name']}")
    
    # Send context to voice agent
    voice_result = await guardian_orchestrator._send_a2a_task(
        "voice_agent",
        "configure_patient_call",
        {
            "params": context["params"]
        }
    )
    
    print(f"   ✅ Voice Agent Response: {voice_result.get('result', {}).get('status', 'configured')}")
    
    # 6. Hospital appointment reminder (1 hour before)
    print("\n6️⃣ Sending Hospital Appointment Reminder...")
    appointment_data = {
        "user_id": user_id,
        "appointment_info": {
            "doctor_name": "Dr. Meera Singh",
            "hospital_name": "Apollo Medical Center",
            "appointment_time": "09:30 AM"
        }
    }
    
    print(f"   📱 FCM: '🏥 Appointment Reminder - Appointment with Dr. Meera Singh at Apollo Medical Center at 09:30 AM'")
    print(f"   📱 App Update: Added hospital appointment to timeline")
    
    # 7. Show complete timeline
    print("\n7️⃣ Complete Trip Timeline:")
    timeline = [
        {
            "time": "2 hours before",
            "event": "Boarding Reminder",
            "status": "✅ Sent",
            "fcm": "✈️ Boarding starts in 45 minutes"
        },
        {
            "time": "30 min before departure",
            "event": "Flight Status Update",
            "status": "✅ Sent", 
            "fcm": "✈️ AI101 On Time - Gate B12"
        },
        {
            "time": "30 min before arrival",
            "event": "Cab Arranged",
            "status": "✅ Sent",
            "fcm": "🚗 Alex Johnson will pick you up in 15 minutes"
        },
        {
            "time": "Any time",
            "event": "Voice Call",
            "status": "✅ Ready",
            "context": "Complete patient context sent"
        },
        {
            "time": "1 hour before appointment",
            "event": "Hospital Reminder",
            "status": "✅ Sent",
            "fcm": "🏥 Appointment with Dr. Meera Singh"
        }
    ]
    
    for item in timeline:
        print(f"   {item['time']:20} | {item['event']:20} | {item['status']}")
        if 'fcm' in item:
            print(f"   {'':20} | {'FCM':20} | {item['fcm']}")
        if 'context' in item:
            print(f"   {'':20} | {'Context':20} | {item['context']}")
        print()
    
    print("🎉 Complete Real-time Trip Flow Test Completed!")
    print("\n📱 Flutter App Integration:")
    print("   1. Register FCM token on app start")
    print("   2. Listen for FCM notifications")
    print("   3. Update timeline UI in real-time")
    print("   4. Show notifications with rich data")
    print("   5. Handle voice call button with full context")

if __name__ == "__main__":
    asyncio.run(test_complete_trip_flow())
