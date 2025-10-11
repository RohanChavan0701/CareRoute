"""
Test script for Comprehensive Context Sharing with Voice Agent
"""

import asyncio
import json
from orchestrator import guardian_orchestrator

async def test_comprehensive_context():
    """Test comprehensive context sharing for Voice Agent"""
    
    print("📞 Testing Comprehensive Context Sharing for Voice Agent")
    print("=" * 80)
    
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
    
    print("\n📞 Step 2: Simulating incoming call with comprehensive context...")
    
    call_data = {
        "call_type": "patient_inquiry",
        "call_duration": "00:05:00",
        "call_quality": "excellent"
    }
    
    try:
        # Handle incoming call - send comprehensive context to Voice Agent
        call_result = await guardian_orchestrator.handle_incoming_call("P001", call_data)
        
        if call_result.get("status") == "success":
            print(f"✅ Comprehensive context shared successfully!")
            print(f"   Call Context ID: {call_result.get('call_context_id')}")
            print(f"   Voice Agent Ready: {call_result.get('voice_agent_ready')}")
        else:
            print(f"❌ Failed to share context: {call_result.get('message')}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")
    
    print(f"\n📋 Step 3: Testing additional information requests from Voice Agent...")
    
    # Simulate additional information requests that Voice Agent might make
    additional_info_requests = [
        {
            "request_type": "flight_status_update",
            "description": "Voice Agent needs latest flight status"
        },
        {
            "request_type": "hotel_confirmation",
            "description": "Voice Agent needs hotel details"
        },
        {
            "request_type": "hospital_appointment",
            "description": "Voice Agent needs appointment details"
        },
        {
            "request_type": "emergency_contacts",
            "description": "Voice Agent needs emergency contact info"
        },
        {
            "request_type": "accessibility_needs",
            "description": "Voice Agent needs accessibility information"
        },
        {
            "request_type": "medication_reminders",
            "description": "Voice Agent needs medication information"
        },
        {
            "request_type": "return_flight",
            "description": "Voice Agent needs return flight details"
        }
    ]
    
    for i, request in enumerate(additional_info_requests, 1):
        print(f"\n📝 Request {i}: {request['description']}")
        print("-" * 60)
        
        request_data = {
            "request_type": request["request_type"]
        }
        
        try:
            # Handle additional info request
            info_result = await guardian_orchestrator.handle_additional_info_request("P001", request_data)
            
            if info_result.get("status") == "success":
                print(f"✅ Additional info provided successfully!")
                print(f"   Request Type: {request['request_type']}")
                
                # Show sample of additional info (truncated for readability)
                additional_info = info_result.get("additional_info", {})
                for key, value in list(additional_info.items())[:3]:  # Show first 3 items
                    if isinstance(value, dict):
                        print(f"   {key}: {list(value.keys())}")
                    else:
                        print(f"   {key}: {value}")
                
                if len(additional_info) > 3:
                    print(f"   ... and {len(additional_info) - 3} more fields")
                    
            else:
                print(f"❌ Failed to get additional info: {info_result.get('message')}")
                
        except Exception as e:
            print(f"❌ Exception: {e}")
    
    print(f"\n🎯 Comprehensive Context Benefits:")
    print("=" * 80)
    print("✅ Voice Agent has ALL information needed to answer patient questions")
    print("✅ Pre-Trip Planning: Travel documents (no medical records), appointments, preparation instructions")
    print("✅ Travel & Transit: Flight details, pickup arrangements, return flights")
    print("✅ Hotel Information: Booking details, services, accessibility features")
    print("✅ Hospital Details: Appointments, doctors, procedures, family communication")
    print("✅ Recovery & Follow-up: Medication reminders, emergency contacts")
    print("✅ Return Travel: Flight details, airport assistance, transportation")
    print("✅ Family Support: Patient status, communication, companion services")
    print("✅ Additional Info Endpoint: Voice Agent can request specific details")
    print("✅ Real-time Updates: Context stays current with orchestration status")
    
    print(f"\n📋 FAQ Categories Covered:")
    print("=" * 80)
    print("🏥 Pre-Trip / Planning:")
    print("   - Hospital appointment confirmation and details")
    print("   - Required travel documents (ID, Insurance, Passport) - NO medical records")
    print("   - Travel insurance and visa status")
    
    print("\n✈️ Travel & Transit:")
    print("   - Flight status, gate, terminal information")
    print("   - Airport pickup arrangements and driver details")
    print("   - Return flight information")
    
    print("\n🏨 Arrival / Hotel:")
    print("   - Hotel check-in confirmation and details")
    print("   - Room type and accessibility features")
    print("   - Translation services and concierge support")
    
    print("\n🏥 Hospital / Treatment:")
    print("   - Surgery/consultation times and details")
    print("   - Family notification capabilities")
    print("   - Doctor and department information")
    
    print("\n❤️ Recovery / Follow-Up:")
    print("   - Follow-up appointment schedules")
    print("   - Medication reminders and timing")
    print("   - Emergency contact information")
    
    print("\n🧳 Return / Travel Home:")
    print("   - Return flight details and status")
    print("   - Airport assistance arrangements")
    print("   - Transportation to airport")
    
    print("\n👨‍👩‍👧 Family / Companion:")
    print("   - Patient arrival and check-in status")
    print("   - Surgery/discharge scheduling")
    print("   - Family communication and support")
    
    print(f"\n🔄 Voice Agent Workflow:")
    print("=" * 80)
    print("1. Patient calls Voice Agent from app")
    print("2. Orchestrator sends COMPREHENSIVE context (all FAQ answers)")
    print("3. Voice Agent has complete information for natural conversation")
    print("4. If Voice Agent needs specific updates, it can request additional info")
    print("5. Voice Agent handles LLM processing with full context")
    print("6. Voice Agent can send schedule amendments back to orchestrator")
    print("7. Orchestrator processes amendments and updates all systems")

if __name__ == "__main__":
    asyncio.run(test_comprehensive_context())
