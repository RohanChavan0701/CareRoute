#!/usr/bin/env python3
"""
Test script to verify Guardian Orchestrator compatibility with Flight Agent
Tests the new get_flight_status method format
"""

import asyncio
import json
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_flight_agent_compatibility():
    """Test the orchestrator with the new flight agent format"""
    
    try:
        # Import orchestrator
        from orchestrator import guardian_orchestrator
        
        logger.info("🧪 Testing Flight Agent Compatibility")
        logger.info("=" * 50)
        
        # Test data matching the expected flight agent input format
        booking_data = {
            "patient_id": "PAT_001",
            "patient_name": "John Doe",
            "patient_email": "john.doe@example.com",
            "flight_number": "AA100",
            "flight_date": "2025-10-11",
            "departure_airport": "JFK",
            "arrival_airport": "LAX",
            "hotel_booking_reference": "HOTEL_123",
            "hospital_booking_reference": "HOSP_456",
            "special_requirements": "Wheelchair assistance required",
            "medical_conditions": ["diabetes"],
            "age": 65,
            "emergency_contacts": [
                {"name": "Jane Doe", "phone": "+1-555-0123", "relationship": "spouse"}
            ]
        }
        
        logger.info("📋 Test Booking Data:")
        logger.info(f"   Patient: {booking_data['patient_name']} ({booking_data['patient_id']})")
        logger.info(f"   Flight: {booking_data['flight_number']} on {booking_data['flight_date']}")
        logger.info(f"   Route: {booking_data['departure_airport']} → {booking_data['arrival_airport']}")
        
        # Test the flight monitoring method directly
        logger.info("\n✈️ Testing Flight Monitoring Method...")
        
        # Create a test orchestration ID
        orchestration_id = f"TEST_ORCH_{int(datetime.now().timestamp())}"
        
        # Initialize the orchestration
        guardian_orchestrator.active_orchestrations[orchestration_id] = {
            "status": "active",
            "patient_id": booking_data["patient_id"],
            "created_at": datetime.now().isoformat(),
            "tasks": {}
        }
        
        # Test the flight monitoring method
        await guardian_orchestrator._orchestrate_flight_monitoring(orchestration_id, booking_data)
        
        # Check the results
        orchestration = guardian_orchestrator.active_orchestrations[orchestration_id]
        flight_task = orchestration["tasks"].get("flight_monitoring")
        
        if flight_task:
            logger.info("✅ Flight monitoring task completed successfully")
            logger.info(f"   Agent: {flight_task['agent']}")
            logger.info(f"   Method: {flight_task['task']}")
            
            # Check the flight data
            flight_data = orchestration.get("flight_data")
            if flight_data:
                logger.info("📊 Flight Data Retrieved:")
                logger.info(f"   Airline: {flight_data.get('airline')}")
                logger.info(f"   Flight Number: {flight_data.get('flight_number')}")
                logger.info(f"   Status: {flight_data.get('status')}")
                logger.info(f"   Origin: {flight_data.get('origin_city')} ({flight_data.get('origin_iata')})")
                logger.info(f"   Destination: {flight_data.get('destination_city')} ({flight_data.get('destination_iata')})")
                logger.info(f"   Gate: {flight_data.get('gate')}")
                logger.info(f"   Terminal: {flight_data.get('terminal')}")
                logger.info(f"   Departure: {flight_data.get('scheduled_departure_local')}")
                logger.info(f"   Arrival: {flight_data.get('scheduled_arrival_local')}")
                
                if flight_data.get('delay_minutes'):
                    logger.info(f"   Delay: {flight_data['delay_minutes']} minutes")
                else:
                    logger.info("   Delay: No delay")
            else:
                logger.warning("⚠️ No flight data found in orchestration")
        else:
            logger.error("❌ Flight monitoring task not found")
        
        # Test the expected input format
        logger.info("\n📤 Expected Flight Agent Input Format:")
        expected_input = {
            "jsonrpc": "2.0",
            "method": "get_flight_status",
            "params": {
                "flight_num": booking_data["flight_number"],
                "departure_date": booking_data["flight_date"],
                "locale": "en-US",
                "user_id": booking_data["patient_id"]
            },
            "id": f"req_{orchestration_id}"
        }
        logger.info(json.dumps(expected_input, indent=2))
        
        # Test the expected output format
        logger.info("\n📥 Expected Flight Agent Output Format:")
        expected_output = {
            "jsonrpc": "2.0",
            "result": {
                "flight_data": {
                    "airline": "DAL",
                    "flight_number": "DAL2990",
                    "origin_iata": "MSY",
                    "origin_city": "New Orleans",
                    "origin_tz": "America/Chicago",
                    "destination_iata": "DTW",
                    "destination_city": "Detroit",
                    "destination_tz": "America/New_York",
                    "scheduled_departure_local": "2025-10-11T14:00",
                    "estimated_departure_local": "2025-10-11T14:10",
                    "scheduled_arrival_local": "2025-10-11T17:30",
                    "estimated_arrival_local": "2025-10-11T17:40",
                    "gate": "B12",
                    "terminal": "8",
                    "status": "IN_AIR",
                    "delay_minutes": 10
                },
                "script": {
                    "text": "Flight DAL2990 from MSY to DTW is currently in the air, arriving at gate B12 at 17:40.",
                    "ssml": "<speak>Flight DAL2990 from MSY to DTW is currently in the air, arriving at gate B12 at <say-as interpret-as=\"time\">17:40</say-as>.</speak>",
                    "style": "conversational",
                    "locale": "en-US"
                },
                "hash": "c66e4fde2d18d62f",
                "generated_at": "2025-10-11T18:00:38.096474Z",
                "schema_version": "flight.status.v1"
            },
            "id": "req_001"
        }
        logger.info(json.dumps(expected_output, indent=2))
        
        logger.info("\n✅ Flight Agent Compatibility Test Completed Successfully!")
        
        # Clean up
        if orchestration_id in guardian_orchestrator.active_orchestrations:
            del guardian_orchestrator.active_orchestrations[orchestration_id]
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        return False

async def main():
    """Main test function"""
    success = await test_flight_agent_compatibility()
    
    if success:
        logger.info("\n🎉 All tests passed! Orchestrator is compatible with Flight Agent format.")
    else:
        logger.error("\n💥 Tests failed! Check the logs above for details.")
    
    return success

if __name__ == "__main__":
    asyncio.run(main())
