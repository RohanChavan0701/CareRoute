#!/usr/bin/env python3
"""
Test script for Guardian Orchestrator FastAPI Backend
Tests the AG-UI protocol integration and API endpoints
"""

import asyncio
import json
import logging
import httpx
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

BASE_URL = "http://localhost:8000"

async def test_backend_api():
    """Test the Guardian Orchestrator backend API"""
    
    async with httpx.AsyncClient() as client:
        logger.info("🧪 Testing Guardian Orchestrator Backend API")
        logger.info("=" * 50)
        
        # Test 1: Health check
        logger.info("\n1️⃣ Testing Health Check...")
        try:
            response = await client.get(f"{BASE_URL}/health")
            if response.status_code == 200:
                logger.info("✅ Health check passed")
                logger.info(f"   Response: {response.json()}")
            else:
                logger.error(f"❌ Health check failed: {response.status_code}")
        except Exception as e:
            logger.error(f"❌ Health check error: {e}")
        
        # Test 2: Booking orchestration
        logger.info("\n2️⃣ Testing Booking Orchestration...")
        booking_data = {
            "patient_id": "PAT_TEST_001",
            "patient_name": "Test Patient",
            "patient_email": "test@example.com",
            "flight_number": "AA100",
            "flight_date": "2025-10-15",
            "departure_airport": "JFK",
            "arrival_airport": "LAX",
            "hotel_booking_reference": "HOTEL_TEST_123",
            "hospital_booking_reference": "HOSP_TEST_456",
            "special_requirements": "Wheelchair assistance",
            "medical_conditions": ["diabetes"],
            "age": 65,
            "emergency_contacts": [
                {"name": "Jane Doe", "phone": "+1-555-0123", "relationship": "spouse"}
            ],
            "flight_time": "09:00"
        }
        
        try:
            response = await client.post(f"{BASE_URL}/orchestrate/booking", json=booking_data)
            if response.status_code == 200:
                logger.info("✅ Booking orchestration started successfully")
                result = response.json()
                logger.info(f"   Patient ID: {result['patient_id']}")
                logger.info(f"   Status: {result['status']}")
            else:
                logger.error(f"❌ Booking orchestration failed: {response.status_code}")
                logger.error(f"   Response: {response.text}")
        except Exception as e:
            logger.error(f"❌ Booking orchestration error: {e}")
        
        # Test 3: Knowledge base query
        logger.info("\n3️⃣ Testing Knowledge Base Query...")
        query_data = {
            "patient_id": "PAT_TEST_001",
            "question": "What's my flight status?",
            "context": {"current_time": datetime.now().isoformat()}
        }
        
        try:
            response = await client.post(f"{BASE_URL}/knowledge/query", json=query_data)
            if response.status_code == 200:
                logger.info("✅ Knowledge query successful")
                result = response.json()
                logger.info(f"   Response: {result.get('response', 'No response')[:100]}...")
            else:
                logger.error(f"❌ Knowledge query failed: {response.status_code}")
                logger.error(f"   Response: {response.text}")
        except Exception as e:
            logger.error(f"❌ Knowledge query error: {e}")
        
        # Test 4: AG-UI Events
        logger.info("\n4️⃣ Testing AG-UI Events...")
        try:
            response = await client.get(f"{BASE_URL}/ag-ui/events/PAT_TEST_001")
            if response.status_code == 200:
                logger.info("✅ AG-UI events retrieved successfully")
                result = response.json()
                logger.info(f"   Event count: {result['count']}")
                if result['events']:
                    logger.info(f"   Latest event: {result['events'][-1]['type']}")
            else:
                logger.error(f"❌ AG-UI events failed: {response.status_code}")
        except Exception as e:
            logger.error(f"❌ AG-UI events error: {e}")
        
        # Test 5: Incoming call simulation
        logger.info("\n5️⃣ Testing Incoming Call...")
        call_data = {
            "patient_id": "PAT_TEST_001",
            "call_type": "general_inquiry",
            "call_data": {
                "caller_id": "+1-555-0123",
                "timestamp": datetime.now().isoformat()
            }
        }
        
        try:
            response = await client.post(f"{BASE_URL}/calls/incoming", json=call_data)
            if response.status_code == 200:
                logger.info("✅ Incoming call handled successfully")
                result = response.json()
                logger.info(f"   Call context ID: {result.get('call_context_id')}")
                logger.info(f"   Voice agent ready: {result.get('voice_agent_ready')}")
            else:
                logger.error(f"❌ Incoming call failed: {response.status_code}")
                logger.error(f"   Response: {response.text}")
        except Exception as e:
            logger.error(f"❌ Incoming call error: {e}")
        
        # Test 6: Schedule amendment
        logger.info("\n6️⃣ Testing Schedule Amendment...")
        amendment_data = {
            "patient_id": "PAT_TEST_001",
            "amendment_type": "flight_change",
            "amendment_data": {
                "new_flight_number": "AA101",
                "new_departure_time": "10:30",
                "reason": "Patient requested later departure"
            }
        }
        
        try:
            response = await client.post(f"{BASE_URL}/schedule/amend", json=amendment_data)
            if response.status_code == 200:
                logger.info("✅ Schedule amendment processed successfully")
                result = response.json()
                logger.info(f"   Amendment type: {result.get('amendment_type')}")
                logger.info(f"   Status: {result.get('status')}")
            else:
                logger.error(f"❌ Schedule amendment failed: {response.status_code}")
                logger.error(f"   Response: {response.text}")
        except Exception as e:
            logger.error(f"❌ Schedule amendment error: {e}")
        
        logger.info("\n🎉 Backend API testing completed!")

async def main():
    """Main test function"""
    try:
        await test_backend_api()
    except Exception as e:
        logger.error(f"❌ Test suite failed: {e}")

if __name__ == "__main__":
    print("🚀 Starting Guardian Orchestrator Backend API Tests")
    print("📝 Make sure the backend server is running on http://localhost:8000")
    print("   Run: cd backend && python main.py")
    print()
    
    asyncio.run(main())
