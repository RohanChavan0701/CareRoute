"""
Guardian A2A Orchestrator
Pure A2A agent orchestration service - no API, just orchestration logic
"""

import asyncio
import logging
import os
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import httpx

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class GuardianOrchestrator:
    """
    Guardian A2A Orchestrator
    Manages coordination between external A2A agents for medical tourism
    """
    
    def __init__(self):
        # External agent endpoints (from other teams)
        self.agent_endpoints = {
            "hotel_agent": os.getenv("HOTEL_AGENT_URL", "https://hotel-agent.aws.region.elb.amazonaws.com"),
            "hospital_agent": os.getenv("HOSPITAL_AGENT_URL", "https://hospital-agent.aws.region.elb.amazonaws.com"),
            "voice_agent": os.getenv("VOICE_AGENT_URL", "https://voice-agent.aws.region.elb.amazonaws.com"),
            "notification_agent": os.getenv("NOTIFICATION_AGENT_URL", "https://notification-agent.aws.region.elb.amazonaws.com"),
            "flight_agent": os.getenv("FLIGHT_AGENT_URL", "https://flight-agent.aws.region.elb.amazonaws.com"),
        }
        
        # Agent health status
        self.agent_health = {}
        
        # Active orchestrations
        self.active_orchestrations = {}
        
        logger.info("Guardian A2A Orchestrator initialized")
    
    async def start_orchestration(self, booking_data: Dict[str, Any]) -> str:
        """
        Start orchestration for a patient's medical tourism journey
        """
        patient_id = booking_data["patient_id"]
        flight_number = booking_data["flight_number"]
        
        orchestration_id = f"ORCH_{patient_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        logger.info(f"🧠 Starting Guardian orchestration {orchestration_id} for patient {patient_id}")
        
        # Store orchestration
        self.active_orchestrations[orchestration_id] = {
            "patient_id": patient_id,
            "flight_number": flight_number,
            "booking_data": booking_data,
            "status": "active",
            "started_at": datetime.now().isoformat(),
            "tasks": {}
        }
        
        try:
            # Step 1: Start flight monitoring
            await self._orchestrate_flight_monitoring(orchestration_id, booking_data)
            
            # Step 2: Wait for coordination trigger (in real system, this would be event-driven)
            # For now, we'll simulate the trigger after a short delay
            await asyncio.sleep(2)
            
            # Step 3: Execute coordination workflow
            await self._execute_coordination_workflow(orchestration_id, booking_data)
            
            # Mark orchestration as completed
            self.active_orchestrations[orchestration_id]["status"] = "completed"
            self.active_orchestrations[orchestration_id]["completed_at"] = datetime.now().isoformat()
            
            logger.info(f"✅ Guardian orchestration {orchestration_id} completed successfully")
            
            return orchestration_id
            
        except Exception as e:
            logger.error(f"❌ Guardian orchestration {orchestration_id} failed: {e}")
            self.active_orchestrations[orchestration_id]["status"] = "failed"
            self.active_orchestrations[orchestration_id]["error"] = str(e)
            raise
    
    async def _orchestrate_flight_monitoring(self, orchestration_id: str, booking_data: Dict[str, Any]):
        """Orchestrate flight monitoring with Flight Agent"""
        patient_id = booking_data["patient_id"]
        flight_number = booking_data["flight_number"]
        
        logger.info(f"✈️ Orchestrating flight monitoring for {flight_number}")
        
        task_data = {
            "method": "TrackFlight",
            "params": {
                "flight_number": flight_number,
                "passenger_id": patient_id,
                "flight_date": booking_data["flight_date"],
                "flight_time": booking_data["flight_time"],
                "departure_airport": booking_data["departure_airport"],
                "arrival_airport": booking_data["arrival_airport"],
                "coordination_threshold_hours": 6,  # Trigger coordination 6 hours before ETA
                "orchestration_id": orchestration_id
            }
        }
        
        # Send A2A task to Flight Agent
        result = await self._send_a2a_task("flight_agent", task_data)
        
        # Store task result
        self.active_orchestrations[orchestration_id]["tasks"]["flight_monitoring"] = {
            "agent": "flight_agent",
            "task": "TrackFlight",
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
        
        logger.info(f"✅ Flight monitoring orchestrated for {flight_number}")
    
    async def _execute_coordination_workflow(self, orchestration_id: str, booking_data: Dict[str, Any]):
        """Execute the main coordination workflow"""
        patient_id = booking_data["patient_id"]
        
        logger.info(f"🎼 Executing coordination workflow for {patient_id}")
        
        # Define coordination tasks
        coordination_tasks = [
            self._coordinate_hotel(orchestration_id, booking_data),
            self._coordinate_hospital(orchestration_id, booking_data),
            self._coordinate_notifications(orchestration_id, booking_data),
            self._coordinate_voice_communication(orchestration_id, booking_data)
        ]
        
        # Execute coordination tasks in parallel
        results = await asyncio.gather(*coordination_tasks, return_exceptions=True)
        
        # Process results
        successful_tasks = 0
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Coordination task {i} failed: {result}")
            else:
                successful_tasks += 1
        
        # Store coordination results
        self.active_orchestrations[orchestration_id]["coordination_results"] = {
            "successful_tasks": successful_tasks,
            "total_tasks": len(coordination_tasks),
            "completed_at": datetime.now().isoformat()
        }
        
        logger.info(f"🎯 Coordination workflow completed: {successful_tasks}/{len(coordination_tasks)} tasks successful")
    
    async def _coordinate_hotel(self, orchestration_id: str, booking_data: Dict[str, Any]):
        """Coordinate with Hotel Agent"""
        patient_id = booking_data["patient_id"]
        
        logger.info(f"🏨 Coordinating with Hotel Agent for {patient_id}")
        
        task_data = {
            "method": "ConfirmHotel",
            "params": {
                "patient_id": patient_id,
                "hotel_booking_reference": booking_data["hotel_booking_reference"],
                "special_requirements": booking_data["special_requirements"],
                "arrival_time": booking_data["flight_time"],
                "coordination_type": "pre_arrival_confirmation",
                "orchestration_id": orchestration_id
            }
        }
        
        result = await self._send_a2a_task("hotel_agent", task_data)
        
        # Store task result
        self.active_orchestrations[orchestration_id]["tasks"]["hotel_coordination"] = {
            "agent": "hotel_agent",
            "task": "ConfirmHotel",
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
        
        logger.info(f"✅ Hotel coordination completed for {patient_id}")
        return result
    
    async def _coordinate_hospital(self, orchestration_id: str, booking_data: Dict[str, Any]):
        """Coordinate with Hospital Agent"""
        patient_id = booking_data["patient_id"]
        
        logger.info(f"🏥 Coordinating with Hospital Agent for {patient_id}")
        
        task_data = {
            "method": "ConfirmHospital",
            "params": {
                "patient_id": patient_id,
                "hospital_appointment_id": booking_data["hospital_appointment_id"],
                "appointment_time": booking_data["hospital_appointment_time"],
                "medical_conditions": booking_data["medical_conditions"],
                "coordination_type": "medical_tourism_preparation",
                "orchestration_id": orchestration_id
            }
        }
        
        result = await self._send_a2a_task("hospital_agent", task_data)
        
        # Store task result
        self.active_orchestrations[orchestration_id]["tasks"]["hospital_coordination"] = {
            "agent": "hospital_agent",
            "task": "ConfirmHospital",
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
        
        logger.info(f"✅ Hospital coordination completed for {patient_id}")
        return result
    
    async def _coordinate_notifications(self, orchestration_id: str, booking_data: Dict[str, Any]):
        """Coordinate with Notification Agent"""
        patient_id = booking_data["patient_id"]
        
        logger.info(f"📱 Coordinating with Notification Agent for {patient_id}")
        
        task_data = {
            "method": "SendFamilyUpdate",
            "params": {
                "patient_id": patient_id,
                "flight_number": booking_data["flight_number"],
                "family_contacts": booking_data["emergency_contacts"],
                "message_type": "coordination_started",
                "status": "Guardian coordination activated",
                "orchestration_id": orchestration_id
            }
        }
        
        result = await self._send_a2a_task("notification_agent", task_data)
        
        # Store task result
        self.active_orchestrations[orchestration_id]["tasks"]["notification_coordination"] = {
            "agent": "notification_agent",
            "task": "SendFamilyUpdate",
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
        
        logger.info(f"✅ Notification coordination completed for {patient_id}")
        return result
    
    async def _coordinate_voice_communication(self, orchestration_id: str, booking_data: Dict[str, Any]):
        """Coordinate with Voice Agent"""
        patient_id = booking_data["patient_id"]
        
        logger.info(f"📞 Coordinating with Voice Agent for {patient_id}")
        
        task_data = {
            "method": "InitiateCall",
            "params": {
                "patient_id": patient_id,
                "call_type": "coordination_update",
                "message": f"Guardian coordination update for flight {booking_data['flight_number']}",
                "call_priority": "normal",
                "orchestration_id": orchestration_id
            }
        }
        
        result = await self._send_a2a_task("voice_agent", task_data)
        
        # Store task result
        self.active_orchestrations[orchestration_id]["tasks"]["voice_coordination"] = {
            "agent": "voice_agent",
            "task": "InitiateCall",
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
        
        logger.info(f"✅ Voice coordination completed for {patient_id}")
        return result
    
    async def _send_a2a_task(self, agent_id: str, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send A2A task to external agent
        """
        try:
            agent_url = self.agent_endpoints.get(agent_id)
            if not agent_url:
                raise ValueError(f"Agent {agent_id} endpoint not configured")
            
            # A2A JSON-RPC 2.0 request
            a2a_request = {
                "jsonrpc": "2.0",
                "id": f"{agent_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "method": task_data["method"],
                "params": task_data["params"]
            }
            
            logger.info(f"🤖 Sending A2A task: {task_data['method']} to {agent_id}")
            
            # In production, this would make real HTTP requests
            # For now, we'll simulate the A2A communication
            async with httpx.AsyncClient() as client:
                try:
                    # Real A2A call would be:
                    # response = await client.post(f"{agent_url}/a2a/tasks", json=a2a_request)
                    # return response.json()
                    
                    # Simulate successful response
                    await asyncio.sleep(0.5)  # Simulate processing time
                    
                    simulated_response = {
                        "jsonrpc": "2.0",
                        "id": a2a_request["id"],
                        "result": {
                            "status": "success",
                            "message": f"Task {task_data['method']} completed successfully",
                            "timestamp": datetime.now().isoformat()
                        }
                    }
                    
                    logger.info(f"✅ A2A task {task_data['method']} completed successfully with {agent_id}")
                    return simulated_response
                    
                except httpx.RequestError as e:
                    logger.error(f"❌ A2A request failed to {agent_id}: {e}")
                    raise
                    
        except Exception as e:
            logger.error(f"❌ A2A task {task_data['method']} failed with {agent_id}: {e}")
            raise
    
    async def check_agent_health(self, agent_id: str) -> bool:
        """Check health of external agent"""
        try:
            agent_url = self.agent_endpoints.get(agent_id)
            if not agent_url:
                return False
            
            # In production, this would make a real health check request
            # For now, we'll simulate it
            await asyncio.sleep(0.1)
            
            # Simulate health check
            self.agent_health[agent_id] = "healthy"
            return True
            
        except Exception as e:
            logger.error(f"❌ Health check failed for {agent_id}: {e}")
            self.agent_health[agent_id] = "unhealthy"
            return False
    
    async def get_orchestration_status(self, orchestration_id: str) -> Optional[Dict[str, Any]]:
        """Get status of orchestration"""
        return self.active_orchestrations.get(orchestration_id)
    
    def get_all_orchestrations(self) -> Dict[str, Dict[str, Any]]:
        """Get all active orchestrations"""
        return self.active_orchestrations
    
    async def cleanup_completed_orchestrations(self, max_age_hours: int = 24):
        """Clean up old completed orchestrations"""
        cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
        
        to_remove = []
        for orchestration_id, orchestration in self.active_orchestrations.items():
            if orchestration["status"] in ["completed", "failed"]:
                completed_at = datetime.fromisoformat(orchestration.get("completed_at", orchestration["started_at"]))
                if completed_at < cutoff_time:
                    to_remove.append(orchestration_id)
        
        for orchestration_id in to_remove:
            del self.active_orchestrations[orchestration_id]
            logger.info(f"🧹 Cleaned up old orchestration: {orchestration_id}")
        
        return len(to_remove)

# Global orchestrator instance
guardian_orchestrator = GuardianOrchestrator()

# Example usage function
async def example_orchestration():
    """Example of how to use the Guardian Orchestrator"""
    
    # Sample booking data
    booking_data = {
        "patient_id": "P123456",
        "patient_name": "John Doe",
        "flight_number": "AA1234",
        "flight_date": "2024-02-15",
        "flight_time": "14:30:00",
        "departure_airport": "JFK",
        "arrival_airport": "LAX",
        "hotel_booking_reference": "HOTEL_REF_123",
        "hospital_appointment_id": "MED_APPT_456",
        "hospital_appointment_time": "2024-02-16T09:00:00",
        "emergency_contacts": ["+1-555-FAMILY"],
        "special_requirements": "Wheelchair accessible",
        "medical_conditions": ["Diabetes", "Hypertension"]
    }
    
    # Start orchestration
    orchestration_id = await guardian_orchestrator.start_orchestration(booking_data)
    print(f"Orchestration started: {orchestration_id}")
    
    # Check status
    status = await guardian_orchestrator.get_orchestration_status(orchestration_id)
    print(f"Orchestration status: {status['status']}")

if __name__ == "__main__":
    # Run example
    asyncio.run(example_orchestration())
