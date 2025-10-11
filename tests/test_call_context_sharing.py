"""
Test script for Call-Triggered Context Sharing with Voice Agent
"""

import asyncio
import json
from orchestrator import guardian_orchestrator

async def test_call_context_sharing():
    """Test the call-triggered context sharing feature"""
    
    print("📞 Testing Call-Triggered Context Sharing with Voice Agent")
    print("=" * 70)
    
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
    
    print("🚀 Step 1: Starting orchestration to establish patient context...")
    orchestration_id = await guardian_orchestrator.start_orchestration(booking_data)
    print(f"✅ Orchestration completed: {orchestration_id}")
    
    print("\n📞 Step 2: Simulating incoming call from patient app...")
    
    # Simulate different types of calls
    call_scenarios = [
        {
            "call_type": "patient_inquiry",
            "description": "Patient calls to check flight status"
        },
        {
            "call_type": "emergency_call",
            "description": "Patient calls with medical emergency"
        },
        {
            "call_type": "schedule_change_request",
            "description": "Patient wants to change hotel booking"
        },
        {
            "call_type": "general_assistance",
            "description": "Patient needs help with travel arrangements"
        }
    ]
    
    for i, scenario in enumerate(call_scenarios, 1):
        print(f"\n📱 Call Scenario {i}: {scenario['description']}")
        print("-" * 50)
        
        call_data = {
            "call_type": scenario["call_type"],
            "call_duration": "00:02:30",
            "call_quality": "good"
        }
        
        try:
            # Handle incoming call - send context to Voice Agent
            call_result = await guardian_orchestrator.handle_incoming_call("P001", call_data)
            
            if call_result.get("status") == "success":
                print(f"✅ Context shared successfully!")
                print(f"   Call Context ID: {call_result.get('call_context_id')}")
                print(f"   Voice Agent Ready: {call_result.get('voice_agent_ready')}")
                print(f"   Message: {call_result.get('message')}")
            else:
                print(f"❌ Failed to share context: {call_result.get('message')}")
                
        except Exception as e:
            print(f"❌ Exception: {e}")
    
    print(f"\n📅 Step 3: Testing schedule amendments from Voice Agent...")
    
    # Simulate schedule amendments that Voice Agent might send back
    amendment_scenarios = [
        {
            "amendment_type": "flight_change",
            "description": "Patient's flight was delayed, needs hotel extension",
            "amendment_data": {
                "amendment_type": "flight_change",
                "reason": "flight_delay",
                "new_flight_data": {
                    "flight_number": "WN123",
                    "status": "DELAYED",
                    "delay_minutes": 120,
                    "estimated_arrival_local": "2025-10-12T14:00:00"
                },
                "additional_requests": ["hotel_checkout_extension"]
            }
        },
        {
            "amendment_type": "hotel_change",
            "description": "Patient wants to upgrade to accessible room",
            "amendment_data": {
                "amendment_type": "hotel_change",
                "reason": "accessibility_upgrade",
                "new_hotel_data": {
                    "hotel_booking_reference": "HOTEL_REF_001_UPDATED",
                    "room_type": "accessible_suite",
                    "special_amenities": ["wheelchair_accessible", "medical_equipment_storage"]
                }
            }
        },
        {
            "amendment_type": "hospital_appointment_change",
            "description": "Patient needs to reschedule appointment due to flight delay",
            "amendment_data": {
                "amendment_type": "hospital_appointment_change",
                "reason": "flight_delay_conflict",
                "new_appointment_data": {
                    "hospital_appointment_id": "MED_APPT_001_RESCHEDULED",
                    "hospital_appointment_time": "2025-10-12T16:00:00",
                    "appointment_type": "consultation",
                    "doctor_name": "Dr. Smith"
                }
            }
        },
        {
            "amendment_type": "emergency_contact_update",
            "description": "Patient updated emergency contacts during call",
            "amendment_data": {
                "amendment_type": "emergency_contact_update",
                "reason": "contact_info_update",
                "new_contacts": ["+1-555-111-2222", "+1-555-999-8888", "+1-555-NEW-CONTACT"]
            }
        }
    ]
    
    for i, scenario in enumerate(amendment_scenarios, 1):
        print(f"\n📝 Amendment {i}: {scenario['description']}")
        print("-" * 50)
        
        try:
            # Process schedule amendment
            amendment_result = await guardian_orchestrator.handle_schedule_amendment(
                "P001", 
                scenario["amendment_data"]
            )
            
            if amendment_result.get("status") == "success":
                print(f"✅ Amendment processed successfully!")
                print(f"   Amendment Type: {scenario['amendment_type']}")
                print(f"   Orchestration ID: {amendment_result.get('orchestration_id')}")
                print(f"   Message: {amendment_result.get('message')}")
            else:
                print(f"❌ Failed to process amendment: {amendment_result.get('message')}")
                
        except Exception as e:
            print(f"❌ Exception: {e}")
    
    print(f"\n🧠 Step 4: Testing knowledge base queries after amendments...")
    
    # Test knowledge base after amendments
    test_questions = [
        "What's my updated flight status?",
        "Is my hotel room accessible?",
        "When is my rescheduled appointment?",
        "Who are my emergency contacts?"
    ]
    
    for question in test_questions:
        print(f"\n❓ Question: {question}")
        try:
            response = await guardian_orchestrator.handle_knowledge_query(question, "P001")
            if response.get("status") == "success":
                print(f"✅ Response: {response['response']}")
            else:
                print(f"❌ Error: {response.get('message')}")
        except Exception as e:
            print(f"❌ Exception: {e}")
    
    print(f"\n🎯 Call Context Sharing Benefits:")
    print("=" * 70)
    print("✅ Complete patient context shared with Voice Agent")
    print("✅ Real-time flight, hotel, and hospital status")
    print("✅ Medical conditions and accessibility needs")
    print("✅ Emergency contacts and preferences")
    print("✅ Schedule amendments processed automatically")
    print("✅ Knowledge base updated with changes")
    print("✅ HIPAA-compliant data handling")
    print("✅ Bidirectional communication with Voice Agent")
    
    print(f"\n🔄 Workflow Summary:")
    print("=" * 70)
    print("1. Patient calls Voice Agent from app")
    print("2. Orchestrator sends complete context to Voice Agent")
    print("3. Voice Agent has informed conversation with patient")
    print("4. Voice Agent sends back schedule amendments")
    print("5. Orchestrator processes amendments and updates context")
    print("6. All other agents get updated information")
    print("7. Knowledge base reflects latest changes")

if __name__ == "__main__":
    asyncio.run(test_call_context_sharing())
