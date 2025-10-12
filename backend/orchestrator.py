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
from .knowledge_base import knowledge_base
from .dummy_data import dummy_db
from .database.orchestrator_service import orchestrator_db_service
from .fcm_service import fcm_service

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
            "voice_agent": os.getenv("VOICE_AGENT_URL", "http://18.217.151.15:8000/jsonrpc"),
            "notification_agent": os.getenv("NOTIFICATION_AGENT_URL", "http://3.143.225.130:8000"),
            "flight_agent": os.getenv("FLIGHT_AGENT_URL", "http://54.158.27.0:8001/a2a"),
        }
        
        # Agent health status
        self.agent_health = {}
        
        # Active orchestrations
        self.active_orchestrations = {}
        
        # Initialize HIPAA-compliant Knowledge Base
        self.knowledge_base = knowledge_base
        
        # Initialize database service
        self.orchestrator_db_service = orchestrator_db_service
        
        logger.info("Guardian A2A Orchestrator with Knowledge Base initialized")
    
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
            
            # Step 2: Start flight monitoring
            await self._orchestrate_flight_monitoring(orchestration_id, booking_data)
            
            # Step 3: Wait for coordination trigger (in real system, this would be event-driven)
            # For now, we'll simulate the trigger after a short delay
            await asyncio.sleep(2)
            
            # Step 4: Execute coordination workflow
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
            "method": "get_flight_status",
            "params": {
                "flight_num": flight_number,
                "departure_date": booking_data["flight_date"],
                "locale": "en-US",
                "user_id": patient_id
            }
        }
        
        # Send A2A task to Flight Agent
        result = await self._send_a2a_task("flight_agent", "get_flight_status", task_data)
        
        # Handle flight agent response in JSON-RPC format
        if result.get("jsonrpc") == "2.0" and "result" in result and result["result"] is not None:
            # Extract flight data from the actual flight agent response
            flight_data = result["result"].get("flight_data", {})
            
            # Store flight data for knowledge base context
            self.active_orchestrations[orchestration_id]["flight_data"] = flight_data
            
            # Update knowledge base with patient context
            await self.update_knowledge_base_context(orchestration_id, booking_data, flight_data)
            
            # Log flight information
            if flight_data:
                logger.info(f"📊 Flight Status: {flight_data.get('status', 'Unknown')}")
                logger.info(f"   Route: {flight_data.get('origin_city', 'Unknown')} → {flight_data.get('destination_city', 'Unknown')}")
                if flight_data.get('delay_minutes'):
                    logger.info(f"   Delay: {flight_data['delay_minutes']} minutes")
            
            # Update result with flight data
            result["flight_data"] = flight_data
            
            # Log flight status for coordination decisions
            if flight_data:
                logger.info(f"✅ Flight {flight_number} status: {flight_data.get('status', 'Unknown')}")
                logger.info(f"   Gate: {flight_data.get('gate', 'Unknown')}, Terminal: {flight_data.get('terminal', 'Unknown')}")
                logger.info(f"   ETA: {flight_data.get('estimated_arrival_local', 'Unknown')}")
                delay_info = f"{flight_data['delay_minutes']} minutes" if flight_data.get('delay_minutes') else "No delay"
                logger.info(f"   Delay: {delay_info}")
                logger.info(f"   Route: {flight_data.get('origin_city', 'Unknown')} → {flight_data.get('destination_city', 'Unknown')}")
            else:
                logger.warning(f"⚠️ No flight data received for {flight_number}")
        
        # Store task result
        self.active_orchestrations[orchestration_id]["tasks"]["flight_monitoring"] = {
            "agent": "flight_agent",
            "task": "get_flight_status",
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
            self._coordinate_voice_communication(orchestration_id, booking_data),
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
                "hotel_booking_reference": booking_data.get("hotel_booking_reference"),
                "special_requirements": booking_data.get("special_requirements"),
                "arrival_time": booking_data.get("flight_time"),
                "coordination_type": "pre_arrival_confirmation",
                "orchestration_id": orchestration_id
            }
        }
        
        result = await self._send_a2a_task("hotel_agent", "coordinate_booking", task_data)
        
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
                "hospital_appointment_id": booking_data.get("appointment_id"),
                "appointment_time": booking_data.get("appointment_time"),
                "medical_conditions": booking_data.get("medical_conditions", []),
                "coordination_type": "medical_tourism_preparation",
                "orchestration_id": orchestration_id
            }
        }
        
        result = await self._send_a2a_task("hospital_agent", "coordinate_appointment", task_data)
        
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
        """Coordinate with Notification Agent using frontend booking data"""
        patient_id = booking_data["patient_id"]
        
        logger.info(f"📱 Coordinating with Notification Agent for {patient_id}")
        
        task_data = {
            "method": "SendFlightBookingNotification",
            "params": {
                "booking_id": booking_data.get("booking_id", f"FLIGHT_{booking_data.get('flight_number', '')}_{patient_id}"),
                "notification_type": "booking_confirmation",
                "recipients": [
                    {
                        "email": booking_data.get("email", "patient@example.com"),
                        "name": booking_data.get("patient_name", booking_data.get("first_name", "") + " " + booking_data.get("last_name", "")),
                        "preferred_method": "email"
                    }
                ],
                "flight_details": {
                    "airline": "American Airlines",  # Use actual airline from frontend
                    "flight_number": booking_data.get("flight_number"),
                    "confirmation_number": f"AA{booking_data.get('flight_number', '')}",
                    "passenger_name": booking_data.get("patient_name", booking_data.get("first_name", "") + " " + booking_data.get("last_name", "")),
                    "origin_iata": booking_data.get("departure_airport"),
                    "origin_city": "New York",  # Map from airport codes
                    "destination_iata": booking_data.get("arrival_airport"),
                    "destination_city": "Miami",  # Map from airport codes
                    "departure_time": f"{booking_data.get('flight_date')}T{booking_data.get('flight_time', '09:00')}:00",
                    "arrival_time": f"{booking_data.get('flight_date')}T12:00:00",
                    "gate": "B22",
                    "terminal": "3",
                    "seat_number": "12A",
                    "baggage_allowance": "2 checked bags, 1 carry-on"
                },
                "orchestration_id": orchestration_id,
                "priority": "normal"
            }
        }
        
        result = await self._send_a2a_task("notification_agent", "SendNotification", task_data)
        
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
        """Coordinate with Voice Agent using frontend booking data"""
        patient_id = booking_data["patient_id"]
        
        logger.info(f"📞 Coordinating with Voice Agent for {patient_id}")
        
        # Use the exact format the voice agent expects
        voice_payload = {
            "patient_name": booking_data.get("patient_name", booking_data.get("first_name", "") + " " + booking_data.get("last_name", "")),
            "patient_id": patient_id,
            "patient_language": booking_data.get("patient_language", "English"),
            "patient_contact": booking_data.get("emergency_contact", "5409348370"),
            "patient_dob": booking_data.get("date_of_birth", "1975-03-15"),
            "companion_name": booking_data.get("companion_name", "Jane Doe"),
            "check_in_date": booking_data.get("hotel_check_in", booking_data.get("travel_date", "2025-10-28")),
            "check_out_date": booking_data.get("hotel_check_out", booking_data.get("return_date", "2025-11-02")),
            "hotel_name": booking_data.get("hotel_name", "Seaside Recovery Resort"),
            "hotel_room_number": booking_data.get("hotel_room_number", "Suite 205"),
            "shuttle_driver": booking_data.get("shuttle_driver", "Mike Johnson"),
            "hospital_name": booking_data.get("hospital_name", "Miami General Hospital"),
            "doctor_name": booking_data.get("doctor_name", "Dr. Smith"),
            "appointment_date": booking_data.get("appointment_date", "2025-10-30"),
            "appointment_time": booking_data.get("appointment_time", "09:00 AM"),
            "pickup_time": booking_data.get("pickup_time", "2025-10-28 13:30"),
            "discharge_date": booking_data.get("expected_discharge_date", "2025-11-01"),
            "discharge_status": booking_data.get("discharge_status", "Pending")
        }
        
        result = await self._send_a2a_task("voice_agent", "configure-patient-call", voice_payload)
        
        # Store task result
        self.active_orchestrations[orchestration_id]["tasks"]["voice_coordination"] = {
            "agent": "voice_agent",
            "task": "configure-patient-call",
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
        
        logger.info(f"✅ Voice coordination completed for {patient_id}")
        return result
    
    
    async def send_boarding_reminder(self, user_id: str, flight_info: Dict[str, Any]):
        """Send boarding reminder via FCM"""
        try:
            await fcm_service.send_boarding_reminder(user_id, flight_info)
            logger.info(f"📱 Boarding reminder sent to user {user_id}")
        except Exception as e:
            logger.error(f"❌ Failed to send boarding reminder: {e}")
    
    async def send_flight_status_update(self, user_id: str, flight_info: Dict[str, Any]):
        """Send flight status update via FCM"""
        try:
            await fcm_service.send_flight_status_update(user_id, flight_info)
            logger.info(f"📱 Flight status update sent to user {user_id}")
        except Exception as e:
            logger.error(f"❌ Failed to send flight status update: {e}")
    
    async def send_arrival_cab_notification(self, user_id: str, cab_info: Dict[str, Any]):
        """Send cab request notification 30 minutes before arrival"""
        try:
            # Send FCM notification
            await fcm_service.send_cab_request_notification(user_id, cab_info)
            
            # Also send email via notification agent
            await self._send_a2a_task(
                "notification_agent",
                "SendHotelBookingNotification",
                {
                    "params": {
                        "user_id": user_id,
                        "patient_name": cab_info.get("patient_name", "Patient"),
                        "hotel_name": cab_info.get("hotel_name", "Hotel"),
                        "arrival_time": cab_info.get("eta", "soon"),
                        "driver_name": cab_info.get("driver_name", "Driver"),
                        "vehicle": cab_info.get("vehicle", "Vehicle")
                    }
                }
            )
            
            logger.info(f"📱 Arrival cab notification sent to user {user_id}")
        except Exception as e:
            logger.error(f"❌ Failed to send arrival cab notification: {e}")
    
    async def send_hospital_appointment_reminder(self, user_id: str, appointment_info: Dict[str, Any]):
        """Send hospital appointment reminder"""
        try:
            await fcm_service.send_hospital_appointment_reminder(user_id, appointment_info)
            logger.info(f"📱 Hospital appointment reminder sent to user {user_id}")
        except Exception as e:
            logger.error(f"❌ Failed to send hospital appointment reminder: {e}")

    async def _send_a2a_task(self, agent_id: str, method: str, task_data: Dict[str, Any]) -> Dict[str, Any]:
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
                "method": method,
                "params": task_data["params"]
            }
            
            logger.info(f"🤖 Sending A2A task: {method} to {agent_id}")
            
            # Make real HTTP requests to external agents
            async with httpx.AsyncClient() as client:
                try:
                    # For flight agent and voice agent, use the endpoint directly
                    if agent_id in ["flight_agent", "voice_agent"]:
                        response = await client.post(agent_url, json=a2a_request, timeout=10.0)
                    else:
                        # For other agents, use the /a2a/tasks endpoint
                        response = await client.post(f"{agent_url}/a2a/tasks", json=a2a_request, timeout=10.0)
                    
                    response_data = response.json()
                    logger.info(f"✅ A2A response from {agent_id}: {response.status_code}")
                    return response_data
                    
                except httpx.TimeoutException:
                    logger.error(f"⏰ Timeout calling {agent_id}")
                    return {"error": "timeout", "message": f"Timeout calling {agent_id}"}
                except httpx.ConnectError:
                    logger.error(f"🔌 Connection error to {agent_id}")
                    return {"error": "connection_error", "message": f"Cannot connect to {agent_id}"}
                except Exception as e:
                    logger.error(f"❌ Error calling {agent_id}: {e}")
                    return {"error": "api_error", "message": str(e)}
                    
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
    
    async def update_knowledge_base_context(self, orchestration_id: str, booking_data: Dict[str, Any], flight_data: Dict[str, Any]):
        """Update knowledge base with patient context data"""
        try:
            patient_id = booking_data["patient_id"]
            
            # Prepare context data for knowledge base
            context_data = {
                "patient_id": patient_id,
                "patient_name": booking_data.get("patient_name"),
                "patient_email": booking_data.get("patient_email"),  # Add email for notifications
                "flight_data": flight_data,
                "hotel_booking_reference": booking_data.get("hotel_booking_reference"),
                "hospital_appointment_id": booking_data.get("hospital_appointment_id"),
                "emergency_contacts": booking_data.get("emergency_contacts", []),
                "special_requirements": booking_data.get("special_requirements", ""),
                "medical_conditions": booking_data.get("medical_conditions", []),
                "age": booking_data.get("age"),
                "preferred_language": booking_data.get("preferred_language", "English"),
                "orchestration_status": self.active_orchestrations[orchestration_id].get("status"),
                "hotel_status": "confirmed",  # Dummy data
                "hospital_status": "confirmed"  # Dummy data
            }
            
            # Update knowledge base with encrypted patient data
            await self.knowledge_base.update_patient_context(patient_id, context_data)
            
            logger.info(f"🧠 Updated knowledge base context for patient {patient_id}")
            
        except Exception as e:
            logger.error(f"❌ Failed to update knowledge base context: {e}")
    
    async def handle_knowledge_query(self, question: str, patient_id: str) -> Dict[str, Any]:
        """Handle knowledge base queries from agents"""
        try:
            logger.info(f"🧠 Processing knowledge query from {patient_id}: {question}")
            
            # Get answer from knowledge base
            response = await self.knowledge_base.answer_question(question, patient_id)
            
            # Log the query for audit purposes
            logger.info(f"✅ Knowledge query processed - Intent: {response.get('intent', 'unknown')}")
            
            return response
            
        except Exception as e:
            logger.error(f"❌ Failed to process knowledge query: {e}")
            return {
                "status": "error",
                "message": "I apologize, but I'm experiencing technical difficulties. Please try again or contact support.",
                "timestamp": datetime.now().isoformat()
            }
    
    async def handle_incoming_call(self, patient_id: str, call_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle incoming call from patient - send complete context to Voice Agent"""
        try:
            logger.info(f"📞 Incoming call from patient {patient_id}")
            
            # Get complete patient context
            patient_context = await self._get_complete_patient_context(patient_id)
            
            if not patient_context:
                return {
                    "status": "error",
                    "message": f"No active orchestration found for patient {patient_id}",
                    "timestamp": datetime.now().isoformat()
                }
            
            # Prepare comprehensive call context payload for Voice Agent
            call_context_payload = {
                # Voice Agent Template Variables (Required)
                "patient_name": patient_context.get("patient_name"),
                "patient_id": patient_id,
                "patient_language": patient_context.get("preferred_language", "English"),
                "patient_contact": patient_context.get("emergency_contacts", [""])[0] if patient_context.get("emergency_contacts") else "",
                "companion_name": patient_context.get("companion_name", "Not specified"),
                "check_in_date": patient_context.get("hotel_check_in", "").split("T")[0] if patient_context.get("hotel_check_in") else "",
                "check_out_date": patient_context.get("new_discharge_date", "").split("T")[0] if patient_context.get("new_discharge_date") else "",
                "hotel_name": "Denver Accessible Suites",
                "hotel_room_number": "Suite 205",
                "hospital_name": "Denver Medical Center",
                "doctor_name": "Dr. Smith",
                "appointment_date": patient_context.get("hospital_appointment_time", "").split("T")[0] if patient_context.get("hospital_appointment_time") else "",
                "appointment_time": patient_context.get("hospital_appointment_time", "").split("T")[1][:5] if patient_context.get("hospital_appointment_time") else "",
                "pickup_time": "15 minutes",
                "discharge_date": patient_context.get("new_discharge_date", "").split("T")[0] if patient_context.get("new_discharge_date") else "",
                
                # Call Context
                "patient_id": patient_id,
                "call_type": call_data.get("call_type", "patient_inquiry"),
                "call_initiated_by": "patient_app",
                "call_timestamp": datetime.now().isoformat(),
                "patient_context": patient_context,
                
                # 🏥 Pre-Trip / Planning Information
                "pre_trip_info": {
                    "hospital_appointment": {
                        "appointment_id": patient_context.get("hospital_appointment_id"),
                        "appointment_time": patient_context.get("hospital_appointment_time"),
                        "hospital_name": "Denver Medical Center",  # From hospital agent
                        "doctor_name": "Dr. Smith",
                        "appointment_type": "consultation",
                        "confirmed": patient_context.get("hospital_status") == "confirmed",
                        "required_documents": ["ID", "Insurance Card", "Passport"],
                        "preparation_instructions": "Fast for 8 hours before appointment"
                    },
                    "travel_documents": {
                        "passport_required": True,
                        "visa_status": "Valid",
                        "medical_insurance": "Travel Medical Insurance Active",
                        "emergency_contacts_list": patient_context.get("emergency_contacts", [])
                    }
                },
                
                # ✈️ Travel & Transit Information
                "travel_info": {
                    "flight_details": {
                        "flight_number": patient_context.get("flight_data", {}).get("flight_number"),
                        "airline": patient_context.get("flight_data", {}).get("airline", "Southwest Airlines"),
                        "status": patient_context.get("flight_data", {}).get("status"),
                        "gate": patient_context.get("flight_data", {}).get("gate"),
                        "terminal": patient_context.get("flight_data", {}).get("terminal"),
                        "departure_time": patient_context.get("flight_data", {}).get("scheduled_departure_local"),
                        "arrival_time": patient_context.get("flight_data", {}).get("estimated_arrival_local"),
                        "delay_minutes": patient_context.get("flight_data", {}).get("delay_minutes"),
                        "origin_city": patient_context.get("flight_data", {}).get("origin_city"),
                        "destination_city": patient_context.get("flight_data", {}).get("destination_city")
                    },
                    "airport_pickup": {
                        "arranged": True,
                        "driver_name": "John Smith",
                        "driver_phone": "+1-555-DRIVER",
                        "vehicle_type": "Wheelchair Accessible Vehicle",
                        "meeting_location": "Baggage Claim Area",
                        "driver_instructions": "Will hold sign with patient name"
                    },
                    "return_flight": {
                        "flight_number": "WN124",  # Return flight
                        "departure_time": "2025-10-15T16:00:00",
                        "gate": "A15",
                        "terminal": "1"
                    }
                },
                
                # 🏨 Arrival / Hotel Information
                "hotel_info": {
                    "booking_details": {
                        "hotel_name": "Denver Accessible Suites",
                        "booking_reference": patient_context.get("hotel_booking_reference"),
                        "check_in_time": "15:00",
                        "check_out_time": "11:00",
                        "room_type": "Accessible Suite",
                        "confirmed": patient_context.get("hotel_status") == "confirmed"
                    },
                    "hotel_services": {
                        "wheelchair_accessible": True,
                        "medical_equipment_storage": True,
                        "dietary_accommodations": True,
                        "concierge_services": True,
                        "translation_services": ["Spanish", "French", "German"]
                    },
                    "hotel_contact": {
                        "phone": "+1-303-HOTEL-01",
                        "address": "123 Medical Tourism Ave, Denver, CO",
                        "concierge_email": "concierge@denveraccessible.com"
                    }
                },
                
                # 🏥 Hospital / Treatment Information
                "hospital_info": {
                    "appointment_details": {
                        "hospital_name": "Denver Medical Center",
                        "appointment_time": patient_context.get("hospital_appointment_time"),
                        "procedure_type": "Medical Consultation",
                        "doctor_name": "Dr. Smith",
                        "department": "Cardiology",
                        "room_number": "Room 205"
                    },
                    "hospital_services": {
                        "family_notification": True,
                        "patient_portal_access": True,
                        "emergency_protocols": "24/7 Emergency Contact Available"
                    },
                    "family_communication": {
                        "auto_notifications": True,
                        "emergency_contacts": patient_context.get("emergency_contacts", []),
                        "status_updates": "Real-time via SMS and Email"
                    }
                },
                
                # ❤️ Recovery / Follow-Up Information
                "recovery_info": {
                    "follow_up_schedule": {
                        "next_appointment": "2025-10-14T10:00:00",
                        "appointment_type": "Follow-up Consultation",
                        "doctor": "Dr. Smith"
                    },
                    "medication_reminders": {
                        "diabetes_medication": "Metformin - Take with meals",
                        "blood_pressure_medication": "Lisinopril - Take daily",
                        "reminder_times": ["08:00", "20:00"]
                    },
                    "emergency_contacts": {
                        "medical_emergency": "911",
                        "guardian_emergency": "+1-800-MED-HELP",
                        "family_contacts": patient_context.get("emergency_contacts", [])
                    }
                },
                
                # 🧳 Return / Travel Home Information
                "return_travel_info": {
                    "return_flight": {
                        "flight_number": "WN124",
                        "departure_time": "2025-10-15T16:00:00",
                        "gate": "A15",
                        "terminal": "1",
                        "status": "Confirmed"
                    },
                    "airport_assistance": {
                        "wheelchair_service": True,
                        "priority_boarding": True,
                        "medical_equipment_transport": True
                    },
                    "transportation_arrangements": {
                        "hotel_to_airport": "Scheduled pickup at 14:00",
                        "driver_contact": "+1-555-DRIVER",
                        "vehicle_type": "Wheelchair Accessible"
                    }
                },
                
                # 👨‍👩‍👧 Family / Companion Information
                "family_info": {
                    "patient_status": {
                        "current_location": "Denver, Colorado",
                        "health_status": "Stable",
                        "last_update": datetime.now().isoformat()
                    },
                    "family_communication": {
                        "emergency_contacts": patient_context.get("emergency_contacts", []),
                        "auto_notifications": True,
                        "status_updates_enabled": True
                    },
                    "companion_services": {
                        "family_accommodation": "Nearby hotel arranged",
                        "visiting_hours": "09:00-21:00",
                        "family_support_contact": "+1-800-FAMILY"
                    }
                },
                
                # 📞 Additional Support Information
                "support_info": {
                    "language_preferences": {
                        "primary": patient_context.get("preferred_language", "English"),
                        "available_languages": ["English", "Spanish", "French", "German"]
                    },
                    "emergency_protocols": {
                        "medical_emergency": "Call 911 immediately",
                        "travel_emergency": "+1-800-TRAVEL-HELP",
                        "guardian_support": "+1-800-GUARDIAN"
                    }
                }
            }
            
            # Send context to Voice Agent
            task_data = {
                "method": "ReceiveCallContext",
                "params": call_context_payload
            }
            
            result = await self._send_a2a_task("voice_agent", "ReceiveCallContext", task_data)
            
            # Store call context sharing result
            if patient_id in [data.get("patient_id") for data in self.active_orchestrations.values()]:
                for orchestration_id, orchestration_data in self.active_orchestrations.items():
                    if orchestration_data.get("patient_id") == patient_id:
                        orchestration_data["tasks"]["call_context_shared"] = {
                            "agent": "voice_agent",
                            "task": "ReceiveCallContext",
                            "result": result,
                            "timestamp": datetime.now().isoformat(),
                            "call_data": call_data
                        }
                        break
            
            logger.info(f"✅ Patient context shared with Voice Agent for {patient_id}")
            
            return {
                "status": "success",
                "message": "Patient context successfully shared with Voice Agent",
                "call_context_id": result.get("call_context_id"),
                "voice_agent_ready": True,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to handle incoming call for {patient_id}: {e}")
            return {
                "status": "error",
                "message": "Failed to share context with Voice Agent",
                "timestamp": datetime.now().isoformat()
            }
    
    async def handle_schedule_amendment(self, patient_id: str, amendment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle schedule amendments from Voice Agent"""
        try:
            logger.info(f"📅 Processing schedule amendment for patient {patient_id}")
            
            # Find active orchestration
            orchestration_id = None
            for oid, data in self.active_orchestrations.items():
                if data.get("patient_id") == patient_id:
                    orchestration_id = oid
                    break
            
            if not orchestration_id:
                return {
                    "status": "error",
                    "message": f"No active orchestration found for patient {patient_id}",
                    "timestamp": datetime.now().isoformat()
                }
            
            # Process different types of amendments
            amendment_type = amendment_data.get("amendment_type")
            
            if amendment_type == "flight_change":
                await self._handle_flight_amendment(orchestration_id, amendment_data)
            elif amendment_type == "hotel_change":
                await self._handle_hotel_amendment(orchestration_id, amendment_data)
            elif amendment_type == "hospital_appointment_change":
                await self._handle_hospital_amendment(orchestration_id, amendment_data)
            elif amendment_type == "emergency_contact_update":
                await self._handle_emergency_contact_update(orchestration_id, amendment_data)
            else:
                logger.warning(f"⚠️ Unknown amendment type: {amendment_type}")
            
            # Store amendment
            self.active_orchestrations[orchestration_id]["tasks"]["schedule_amendment"] = {
                "agent": "voice_agent",
                "amendment_type": amendment_type,
                "amendment_data": amendment_data,
                "timestamp": datetime.now().isoformat(),
                "status": "processed"
            }
            
            # Update knowledge base with new information
            await self._update_context_from_amendment(patient_id, amendment_data)
            
            logger.info(f"✅ Schedule amendment processed for {patient_id}: {amendment_type}")
            
            return {
                "status": "success",
                "message": f"Schedule amendment processed: {amendment_type}",
                "orchestration_id": orchestration_id,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to process schedule amendment for {patient_id}: {e}")
            return {
                "status": "error",
                "message": "Failed to process schedule amendment",
                "timestamp": datetime.now().isoformat()
            }
    
    async def _get_comprehensive_call_context(self, user_id: str) -> Dict[str, Any]:
        """Get comprehensive patient context for Voice Agent calls"""
        try:
            # Get user data from dummy database
            user_bookings = dummy_db.get_user_bookings(user_id)
            user_flights = dummy_db.get_user_flights(user_id)
            user_location = dummy_db.get_user_location(user_id)
            
            if not user_bookings:
                logger.warning(f"No booking data found for user {user_id}")
                # Return default context for users without bookings in the exact format required
                return {
                    "jsonrpc": "2.0",
                    "method": "configure_patient_call",
                    "params": {
                        "patient_name": "Guest User",
                        "patient_id": user_id,
                        "patient_language": "English",
                        "patient_contact": "",
                        "patient_dob": "Not specified",
                        "companion_name": "Not specified",
                        "check_in_date": "",
                        "check_out_date": "",
                        "hotel_name": "Not booked",
                        "hotel_room_number": "Not assigned",
                        "shuttle_driver": "Not assigned",
                        "hospital_name": "Not scheduled",
                        "doctor_name": "Not assigned",
                        "appointment_date": "",
                        "appointment_time": "",
                        "pickup_time": "",
                        "discharge_date": "",
                        "discharge_status": "Pending"
                    },
                    "id": f"orchestrator-request-{user_id}"
                }
            
            booking = user_bookings[0]
            flight = user_flights[0] if user_flights else {}
            
            # Prepare comprehensive context for voice agent in the exact format required
            context_data = {
                "jsonrpc": "2.0",
                "method": "configure_patient_call",
                "params": {
                    "patient_name": booking.get("patient_name", "Guest User"),
                    "patient_id": booking.get("user_id", user_id),
                    "patient_language": booking.get("patient_language", "English"),
                    "patient_contact": booking.get("emergency_contact", "5409348370"),
                    "patient_dob": booking.get("date_of_birth", "Not specified"),
                    "companion_name": booking.get("companion_name", "Not specified"),
                "check_in_date": booking.get("hotel_check_in", "").replace("T", " ").split(".")[0][:16] if booking.get("hotel_check_in") else "",
                "check_out_date": booking.get("hotel_check_out", "").replace("T", " ").split(".")[0][:16] if booking.get("hotel_check_out") else "",
                    "hotel_name": booking.get("hotel_name", "Denver Accessible Suites"),
                    "hotel_room_number": booking.get("hotel_room_number", "Suite 205"),
                    "shuttle_driver": booking.get("shuttle_driver", "Not assigned"),
                    "hospital_name": booking.get("hospital_name", "Denver Medical Center"),
                    "doctor_name": booking.get("doctor_name", "Dr. Smith"),
                    "appointment_date": booking.get("appointment_date", "2025-10-30"),
                    "appointment_time": booking.get("appointment_time", "09:00 AM"),
                    "pickup_time": booking.get("pickup_time", "").replace("T", " ").split(".")[0][:16] if booking.get("pickup_time") else "2025-10-28 13:30",
                    "discharge_date": booking.get("expected_discharge_date", "2025-11-01") + " 01:00 PM",
                    "discharge_status": booking.get("discharge_status", "Pending")
                },
                "id": f"orchestrator-request-{user_id}"
            }
            
            return context_data
            
        except Exception as e:
            logger.error(f"❌ Failed to get comprehensive call context: {e}")
            # Return minimal context on error in the exact format required
            return {
                "jsonrpc": "2.0",
                "method": "configure_patient_call",
                "params": {
                    "patient_name": "Guest User",
                    "patient_id": user_id,
                    "patient_language": "English",
                    "patient_contact": "",
                    "patient_dob": "Not specified",
                    "companion_name": "Not specified",
                    "check_in_date": "",
                    "check_out_date": "",
                    "hotel_name": "Not available",
                    "hotel_room_number": "Not available",
                    "shuttle_driver": "Not available",
                    "hospital_name": "Not available",
                    "doctor_name": "Not available",
                    "appointment_date": "",
                    "appointment_time": "",
                    "pickup_time": "",
                    "discharge_date": "",
                    "discharge_status": "Pending"
                },
                "id": f"orchestrator-request-{user_id}",
                "error": str(e)
            }
    
    async def _handle_flight_amendment(self, orchestration_id: str, amendment_data: Dict[str, Any]):
        """Handle flight-related amendments"""
        logger.info(f"✈️ Processing flight amendment for orchestration {orchestration_id}")
        # Implementation for flight changes
        
    async def _handle_hotel_amendment(self, orchestration_id: str, amendment_data: Dict[str, Any]):
        """Handle hotel-related amendments"""
        logger.info(f"🏨 Processing hotel amendment for orchestration {orchestration_id}")
        # Implementation for hotel changes
        
    async def _handle_hospital_amendment(self, orchestration_id: str, amendment_data: Dict[str, Any]):
        """Handle hospital appointment amendments"""
        logger.info(f"🏥 Processing hospital amendment for orchestration {orchestration_id}")
        # Implementation for hospital appointment changes
        
    async def _handle_emergency_contact_update(self, orchestration_id: str, amendment_data: Dict[str, Any]):
        """Handle emergency contact updates"""
        logger.info(f"📞 Processing emergency contact update for orchestration {orchestration_id}")
        # Implementation for emergency contact changes
        
    async def _update_context_from_amendment(self, patient_id: str, amendment_data: Dict[str, Any]):
        """Update knowledge base context from schedule amendments"""
        try:
            # Get current context
            current_context = self.knowledge_base.data_manager.get_patient_data(patient_id)
            
            # Update based on amendment type
            amendment_type = amendment_data.get("amendment_type")
            
            if amendment_type == "flight_change" and amendment_data.get("new_flight_data"):
                current_context["flight_data"] = amendment_data["new_flight_data"]
            elif amendment_type == "hotel_change" and amendment_data.get("new_hotel_data"):
                current_context.update(amendment_data["new_hotel_data"])
            elif amendment_type == "hospital_appointment_change" and amendment_data.get("new_appointment_data"):
                current_context.update(amendment_data["new_appointment_data"])
            elif amendment_type == "emergency_contact_update" and amendment_data.get("new_contacts"):
                current_context["emergency_contacts"] = amendment_data["new_contacts"]
            
            # Update knowledge base
            await self.knowledge_base.update_patient_context(patient_id, current_context)
            
            logger.info(f"🧠 Updated knowledge base context from amendment: {amendment_type}")
            
        except Exception as e:
            logger.error(f"❌ Failed to update context from amendment: {e}")
    
    async def handle_additional_info_request(self, patient_id: str, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle additional information requests from Voice Agent"""
        try:
            logger.info(f"📋 Processing additional info request from Voice Agent for {patient_id}")
            
            request_type = request_data.get("request_type")
            requested_fields = request_data.get("requested_fields", [])
            
            # Get current patient context
            patient_context = self.knowledge_base.data_manager.get_patient_data(patient_id)
            
            if not patient_context:
                return {
                    "status": "error",
                    "message": f"No patient context found for {patient_id}",
                    "timestamp": datetime.now().isoformat()
                }
            
            # Prepare additional information based on request
            additional_info = {}
            
            if request_type == "flight_status_update":
                # Get latest flight information
                additional_info["flight_status"] = {
                    "current_status": patient_context.get("flight_data", {}).get("status"),
                    "gate": patient_context.get("flight_data", {}).get("gate"),
                    "terminal": patient_context.get("flight_data", {}).get("terminal"),
                    "delay_minutes": patient_context.get("flight_data", {}).get("delay_minutes"),
                    "last_updated": datetime.now().isoformat()
                }
            
            elif request_type == "hotel_confirmation":
                # Get hotel details
                additional_info["hotel_details"] = {
                    "hotel_name": "Denver Accessible Suites",
                    "booking_reference": patient_context.get("hotel_booking_reference"),
                    "check_in_time": "15:00",
                    "room_type": "Accessible Suite",
                    "confirmed": patient_context.get("hotel_status") == "confirmed"
                }
            
            elif request_type == "hospital_appointment":
                # Get hospital appointment details
                additional_info["hospital_appointment"] = {
                    "appointment_time": patient_context.get("hospital_appointment_time"),
                    "hospital_name": "Denver Medical Center",
                    "doctor_name": "Dr. Smith",
                    "department": "Cardiology",
                    "room_number": "Room 205"
                }
            
            elif request_type == "emergency_contacts":
                # Get emergency contact information
                additional_info["emergency_contacts"] = {
                    "family_contacts": patient_context.get("emergency_contacts", []),
                    "medical_emergency": "911",
                    "guardian_emergency": "+1-800-MED-HELP"
                }
            
            
            elif request_type == "medication_reminders":
                # Get medication information
                additional_info["medication_reminders"] = {
                    "diabetes_medication": "Metformin - Take with meals",
                    "blood_pressure_medication": "Lisinopril - Take daily",
                    "reminder_times": ["08:00", "20:00"],
                    "next_reminder": "2025-10-12T08:00:00"
                }
            
            elif request_type == "return_flight":
                # Get return flight information
                additional_info["return_flight"] = {
                    "flight_number": "WN124",
                    "departure_time": "2025-10-15T16:00:00",
                    "gate": "A15",
                    "terminal": "1",
                    "status": "Confirmed"
                }
            
            else:
                # Generic request - return requested fields
                for field in requested_fields:
                    if field in patient_context:
                        additional_info[field] = patient_context[field]
            
            # Log the request
            logger.info(f"✅ Additional info provided for {patient_id}: {request_type}")
            
            return {
                "status": "success",
                "message": f"Additional information provided for {request_type}",
                "patient_id": patient_id,
                "request_type": request_type,
                "additional_info": additional_info,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to handle additional info request for {patient_id}: {e}")
            return {
                "status": "error",
                "message": "Failed to retrieve additional information",
                "timestamp": datetime.now().isoformat()
            }
    
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

    # ==================== TRIP FLOW METHODS ====================
    
    async def handle_booking_creation(self, user_id: str, booking_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle booking creation - save to database and send notifications"""
        try:
            # 1. Create booking using dummy data (bypass database for now)
            booking_id = dummy_db.create_booking(user_id, booking_data)
            
            # 2. Create flight tracking using dummy data
            flight_data = {
                "flight_number": booking_data.get("flight_number"),
                "departure_date": booking_data.get("flight_date"),
                "departure_airport": booking_data.get("departure_airport"),
                "arrival_airport": booking_data.get("arrival_airport"),
                "departure_time": booking_data.get("flight_time"),
                "passenger_name": booking_data.get("patient_name"),
                "email": booking_data.get("email")
            }
            flight_id = dummy_db.create_flight(user_id, flight_data)
            
            # 3. Send booking confirmation notification
            await self._send_booking_confirmation_notification(booking_data)
            
            # 4. Create orchestration tracking
            orchestration_id = f"ORCH_{user_id}_{int(datetime.now().timestamp())}"
            dummy_db.create_orchestration(orchestration_id, {
                "user_id": user_id,
                "booking_id": booking_id,
                "flight_id": flight_id,
                "status": "booking_created",
                "flow_step": "initial_booking"
            })
            
            logger.info(f"✅ Booking created and orchestration started for user {user_id}")
            
            return {
                "status": "success",
                "booking_id": booking_id,
                "flight_id": flight_id,
                "orchestration_id": orchestration_id,
                "message": "Booking created successfully. You will receive flight updates 7 hours before departure."
            }
            
        except Exception as e:
            logger.error(f"❌ Error handling booking creation: {e}")
            return {"status": "error", "message": str(e)}
    
    async def _send_booking_confirmation_notification(self, booking_data: Dict[str, Any]):
        """Send booking confirmation notification"""
        try:
            notification_payload = {
                "jsonrpc": "2.0",
                "id": f"booking_{booking_data.get('patient_name', 'unknown')}",
                "method": "SendFlightBookingNotification",
                "params": {
                    "booking_id": f"BOOK_{booking_data.get('patient_name', 'unknown')}",
                    "notification_type": "booking_confirmation",
                    "recipients": [
                        {
                            "email": booking_data.get("email", "patient@example.com"),
                            "name": booking_data.get("patient_name", "Patient"),
                            "preferred_method": "email"
                        }
                    ],
                    "flight_details": {
                        "flight_number": booking_data.get("flight_number"),
                        "departure_date": booking_data.get("flight_date"),
                        "departure_airport": booking_data.get("departure_airport"),
                        "arrival_airport": booking_data.get("arrival_airport"),
                        "departure_time": booking_data.get("flight_time")
                    },
                    "orchestration_id": "ORCH_001",
                    "priority": "normal"
                }
            }
            
            await self._send_a2a_task("notification_agent", "SendFlightBookingNotification", notification_payload)
            logger.info("✅ Booking confirmation notification sent")
            
        except Exception as e:
            logger.error(f"❌ Error sending booking notification: {e}")

    async def send_hotel_booking_notification(self, booking_data: Dict[str, Any]) -> Dict[str, Any]:
        """Send hotel booking notification using the exact format specified"""
        try:
            logger.info(f"🏨 Sending hotel booking notification for {booking_data.get('booking_id')}")
            
            # If the request already has the JSON-RPC structure, use it directly
            if "jsonrpc" in booking_data and "params" in booking_data:
                notification_payload = booking_data
            else:
                # Extract hotel_details and create params with both flattened and nested structure
                hotel_details = booking_data.get("hotel_details", {})
                params = {
                    "booking_id": booking_data.get("booking_id", "HOTEL_12345"),
                    "notification_type": booking_data.get("notification_type", "hotel_booking_confirmation"),
                    "recipients": booking_data.get("recipients", []),
                    "message": booking_data.get("message", {}),
                    "orchestration_id": booking_data.get("orchestration_id", "ORCH_001"),
                    "priority": booking_data.get("priority", "normal"),
                    "hotel_details": hotel_details
                }
                
                # Also add flattened hotel_details fields for compatibility
                params.update(hotel_details)
                
                # Use the exact format provided by the user
                notification_payload = {
                    "jsonrpc": "2.0",
                    "id": booking_data.get("booking_id", "hotel_001"),
                    "method": "SendHotelBookingNotification",
                    "params": params
                }
            
            # Send to notification agent
            result = await self._send_a2a_task("notification_agent", "SendHotelBookingNotification", notification_payload)
            
            logger.info(f"✅ Hotel booking notification sent for booking {booking_data.get('booking_id')}")
            return {"status": "success", "message": "Hotel booking notification sent", "result": result}
            
        except Exception as e:
            logger.error(f"❌ Error sending hotel booking notification: {e}")
            return {"status": "error", "message": str(e)}

    async def send_flight_landed_notification(self, flight_data: Dict[str, Any]) -> Dict[str, Any]:
        """Send flight landed notification using the exact format specified"""
        try:
            logger.info(f"✈️ Sending flight landed notification for {flight_data.get('booking_id')}")
            
            # If the request already has the JSON-RPC structure, use it directly
            if "jsonrpc" in flight_data and "params" in flight_data:
                notification_payload = flight_data
            else:
                # Extract flight_details and create params with both flattened and nested structure
                flight_details = flight_data.get("flight_details", {})
                params = {
                    "booking_id": flight_data.get("booking_id", "FLIGHT_LANDED_123"),
                    "notification_type": flight_data.get("notification_type", "flight_landed"),
                    "recipients": flight_data.get("recipients", []),
                    "message": flight_data.get("message", {}),
                    "orchestration_id": flight_data.get("orchestration_id", "ORCH_LANDED_001"),
                    "priority": flight_data.get("priority", "normal"),
                    "flight_details": flight_details
                }
                
                # Also add flattened flight_details fields for compatibility
                params.update(flight_details)
                
                # Use the exact format provided by the user
                notification_payload = {
                    "jsonrpc": "2.0",
                    "id": flight_data.get("booking_id", "flight_landed_001"),
                    "method": "SendFlightLandedNotification",
                    "params": params
                }
            
            # Send to notification agent
            result = await self._send_a2a_task("notification_agent", "SendFlightLandedNotification", notification_payload)
            
            logger.info(f"✅ Flight landed notification sent for booking {flight_data.get('booking_id')}")
            return {"status": "success", "message": "Flight landed notification sent", "result": result}
            
        except Exception as e:
            logger.error(f"❌ Error sending flight landed notification: {e}")
            return {"status": "error", "message": str(e)}

    async def send_hotel_shuttle_request(self, shuttle_data: Dict[str, Any]) -> Dict[str, Any]:
        """Send hotel shuttle request using the exact format specified"""
        try:
            logger.info(f"🚗 Sending hotel shuttle request for {shuttle_data.get('booking_id')}")
            
            # If the request already has the JSON-RPC structure, use it directly
            if "jsonrpc" in shuttle_data and "params" in shuttle_data:
                notification_payload = shuttle_data
            else:
                # Extract shuttle_details and create params with both flattened and nested structure
                shuttle_details = shuttle_data.get("shuttle_details", {})
                params = {
                    "booking_id": shuttle_data.get("booking_id", "SHUTTLE_12345"),
                    "notification_type": shuttle_data.get("notification_type", "shuttle_request"),
                    "recipients": shuttle_data.get("recipients", []),
                    "message": shuttle_data.get("message", {}),
                    "orchestration_id": shuttle_data.get("orchestration_id", "ORCH_003"),
                    "priority": shuttle_data.get("priority", "normal"),
                    "shuttle_details": shuttle_details
                }
                
                # Also add flattened shuttle_details fields for compatibility
                params.update(shuttle_details)
                
                # Use the exact format provided by the user
                notification_payload = {
                    "jsonrpc": "2.0",
                    "id": shuttle_data.get("booking_id", "shuttle_001"),
                    "method": "SendHotelShuttleRequest",
                    "params": params
                }
            
            # Send to notification agent
            result = await self._send_a2a_task("notification_agent", "SendHotelShuttleRequest", notification_payload)
            
            logger.info(f"✅ Hotel shuttle request sent for booking {shuttle_data.get('booking_id')}")
            return {"status": "success", "message": "Hotel shuttle request sent", "result": result}
            
        except Exception as e:
            logger.error(f"❌ Error sending hotel shuttle request: {e}")
            return {"status": "error", "message": str(e)}

    async def send_hospital_appointment_notification(self, appointment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Send hospital appointment notification"""
        try:
            logger.info(f"🏥 Sending hospital appointment notification for {appointment_data.get('appointment_id')}")
            
            notification_payload = {
                "jsonrpc": "2.0",
                "id": appointment_data.get("appointment_id", "hospital_001"),
                "method": "SendHospitalAppointmentNotification",
                "params": {
                    "appointment_id": appointment_data.get("appointment_id"),
                    "notification_type": appointment_data.get("notification_type", "appointment_reminder"),
                    "recipients": appointment_data.get("recipients", []),
                    "appointment_details": appointment_data.get("appointment_details", {}),
                    "hospital_details": appointment_data.get("hospital_details", {}),
                    "orchestration_id": appointment_data.get("orchestration_id", "ORCH_001"),
                    "priority": appointment_data.get("priority", "normal")
                }
            }
            
            result = await self._send_a2a_task("notification_agent", "SendHospitalAppointmentNotification", notification_payload)
            
            logger.info(f"✅ Hospital appointment notification sent for appointment {appointment_data.get('appointment_id')}")
            return {"status": "success", "message": "Hospital appointment notification sent", "result": result}
            
        except Exception as e:
            logger.error(f"❌ Error sending hospital appointment notification: {e}")
            return {"status": "error", "message": str(e)}

    async def send_stay_extension_notification(self, extension_data: Dict[str, Any]) -> Dict[str, Any]:
        """Send stay extension notification"""
        try:
            logger.info(f"📅 Sending stay extension notification for {extension_data.get('booking_id')}")
            
            notification_payload = {
                "jsonrpc": "2.0",
                "id": extension_data.get("booking_id", "extension_001"),
                "method": "SendStayExtensionNotification",
                "params": {
                    "booking_id": extension_data.get("booking_id"),
                    "notification_type": extension_data.get("notification_type", "stay_extended"),
                    "recipients": extension_data.get("recipients", []),
                    "extension_details": extension_data.get("extension_details", {}),
                    "hotel_details": extension_data.get("hotel_details", {}),
                    "orchestration_id": extension_data.get("orchestration_id", "ORCH_001"),
                    "priority": extension_data.get("priority", "high")
                }
            }
            
            result = await self._send_a2a_task("notification_agent", "SendStayExtensionNotification", notification_payload)
            
            logger.info(f"✅ Stay extension notification sent for booking {extension_data.get('booking_id')}")
            return {"status": "success", "message": "Stay extension notification sent", "result": result}
            
        except Exception as e:
            logger.error(f"❌ Error sending stay extension notification: {e}")
            return {"status": "error", "message": str(e)}

    async def send_discharge_notification(self, discharge_data: Dict[str, Any]) -> Dict[str, Any]:
        """Send discharge notification"""
        try:
            logger.info(f"🏥 Sending discharge notification for {discharge_data.get('patient_id')}")
            
            notification_payload = {
                "jsonrpc": "2.0",
                "id": discharge_data.get("patient_id", "discharge_001"),
                "method": "SendDischargeNotification",
                "params": {
                    "patient_id": discharge_data.get("patient_id"),
                    "notification_type": discharge_data.get("notification_type", "discharge_ready"),
                    "recipients": discharge_data.get("recipients", []),
                    "discharge_details": discharge_data.get("discharge_details", {}),
                    "hospital_details": discharge_data.get("hospital_details", {}),
                    "transportation_details": discharge_data.get("transportation_details", {}),
                    "orchestration_id": discharge_data.get("orchestration_id", "ORCH_001"),
                    "priority": discharge_data.get("priority", "high")
                }
            }
            
            result = await self._send_a2a_task("notification_agent", "SendDischargeNotification", notification_payload)
            
            logger.info(f"✅ Discharge notification sent for patient {discharge_data.get('patient_id')}")
            return {"status": "success", "message": "Discharge notification sent", "result": result}
            
        except Exception as e:
            logger.error(f"❌ Error sending discharge notification: {e}")
            return {"status": "error", "message": str(e)}
    
    async def check_flight_reminders(self, user_id: str) -> Dict[str, Any]:
        """Check if user needs flight reminders (7 hours before departure)"""
        try:
            user_flights = dummy_db.get_user_flights(user_id)
            current_time = datetime.now()
            
            for flight in user_flights:
                if flight.get("status") == "scheduled":
                    departure_date = datetime.strptime(flight.get("departure_date", ""), "%Y-%m-%d")
                    departure_time = datetime.strptime(flight.get("departure_time", ""), "%H:%M:%S")
                    departure_datetime = datetime.combine(departure_date, departure_time.time())
                    
                    # Check if 7 hours before departure
                    time_diff = departure_datetime - current_time
                    if timedelta(hours=6, minutes=30) <= time_diff <= timedelta(hours=7, minutes=30):
                        await self._trigger_flight_reminder(user_id, flight)
                        return {"status": "reminder_sent", "flight_id": flight.get("flight_id")}
            
            return {"status": "no_reminders_needed"}
            
        except Exception as e:
            logger.error(f"❌ Error checking flight reminders: {e}")
            return {"status": "error", "message": str(e)}
    
    async def _trigger_flight_reminder(self, user_id: str, flight: Dict[str, Any]):
        """Trigger 7-hour flight reminder"""
        try:
            # 1. Get flight status from flight agent
            flight_status = await self._get_flight_status(flight)
            
            # 2. Update flight status in dummy DB
            dummy_db.update_flight_status(flight.get("flight_id"), flight_status)
            
            # 3. Send reminder notification
            await self._send_flight_reminder_notification(user_id, flight, flight_status)
            
            # 4. Update orchestration status
            orchestration_id = f"ORCH_{user_id}"
            dummy_db.update_orchestration_status(orchestration_id, "flight_tracking", {
                "flow_step": "flight_reminder_sent",
                "flight_status": flight_status
            })
            
            logger.info(f"✅ Flight reminder triggered for user {user_id}")
            
        except Exception as e:
            logger.error(f"❌ Error triggering flight reminder: {e}")
    
    async def get_flight_status(self, flight_number: str, departure_date: str = None, locale: str = "en-US", user_id: str = None) -> Dict[str, Any]:
        """Get flight status by flight number - independent of users"""
        try:
            logger.info(f"✈️ Getting flight status for {flight_number}")
            
            # Call flight agent API with correct parameter format
            payload = {
                "jsonrpc": "2.0",
                "method": "get_flight_status",
                "params": {
                    "flight_num": flight_number,
                    "departure_date": departure_date or "2025-10-14",
                    "locale": locale,
                    "user_id": user_id or "optional_user_id"
                },
                "id": f"flight-status-{flight_number}"
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.agent_endpoints["flight_agent"],
                    json=payload,
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    flight_data = response.json()
                    if "result" in flight_data and flight_data["result"]:
                        logger.info(f"✅ Flight {flight_number} status retrieved")
                        return flight_data["result"]
                    elif "error" in flight_data:
                        logger.warning(f"⚠️ Flight API error for {flight_number}: {flight_data['error']}")
                        return {"error": flight_data["error"].get("message", "Flight API error")}
                    else:
                        logger.warning(f"⚠️ Invalid flight API response for {flight_number}")
                        return {"error": "Invalid flight API response"}
                else:
                    logger.error(f"❌ Flight API HTTP error for {flight_number}: {response.status_code}")
                    return {"error": f"Flight API HTTP error: {response.status_code}"}
                    
        except Exception as e:
            logger.error(f"❌ Flight status error for {flight_number}: {e}")
            return {"error": str(e)}
    
    async def get_flight_status_for_user(self, user_id: str) -> Dict[str, Any]:
        """Get flight status for a user by looking up their flight number"""
        try:
            user_bookings = self.orchestrator_db_service.get_user_bookings(user_id)
            if not user_bookings:
                return {"error": "No booking found for user"}
            
            booking = user_bookings[0]
            flight_number = booking.get("flight_number")
            
            if not flight_number:
                return {"error": "No flight number found in booking"}
            
            # Get flight status by flight number (independent of user)
            flight_status = await self.get_flight_status(
                flight_number=flight_number,
                departure_date=booking.get("flight_date"),
                locale="en-US",
                user_id=user_id
            )
            
            return flight_status
                    
        except Exception as e:
            logger.error(f"❌ User flight status error: {e}")
            return {"error": str(e)}

    async def _get_flight_status(self, flight: Dict[str, Any]) -> Dict[str, Any]:
        """Get flight status from flight agent"""
        try:
            payload = {
                "jsonrpc": "2.0",
                "method": "get_flight_status",
                "params": {
                    "flight_num": flight.get("flight_number"),
                    "departure_date": flight.get("departure_date"),
                    "locale": "en-US",
                    "user_id": flight.get("user_id")
                },
                "id": f"flight_status_{flight.get('flight_id')}"
            }
            
            response = await self._send_a2a_task("flight_agent", "get_flight_status", payload)
            return response.get("result", {}).get("flight_data", {})
            
        except Exception as e:
            logger.error(f"❌ Error getting flight status: {e}")
            return {}
    
    async def _send_flight_reminder_notification(self, user_id: str, flight: Dict[str, Any], flight_status: Dict[str, Any]):
        """Send flight reminder notification"""
        try:
            notification_payload = {
                "jsonrpc": "2.0",
                "id": f"reminder_{user_id}",
                "method": "SendFlightBookingNotification",
                "params": {
                    "booking_id": f"BOOK_{user_id}",
                    "notification_type": "flight_reminder",
                    "recipients": [
                        {
                            "email": flight.get("email", "patient@example.com"),
                            "name": flight.get("passenger_name", "Patient"),
                            "preferred_method": "email"
                        }
                    ],
                    "flight_details": flight_status,
                    "orchestration_id": f"ORCH_{user_id}",
                    "priority": "high"
                }
            }
            
            await self._send_a2a_task("notification_agent", "SendFlightBookingNotification", notification_payload)
            logger.info("✅ Flight reminder notification sent")
            
        except Exception as e:
            logger.error(f"❌ Error sending flight reminder: {e}")
    
    async def handle_arrival_detection(self, user_id: str, location_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle arrival detection - trigger cab arrangement and hotel confirmation"""
        try:
            # 1. Update user location
            dummy_db.update_user_location(user_id, location_data)
            
            # 2. Get user's flight and booking info
            user_flights = dummy_db.get_user_flights(user_id)
            user_bookings = dummy_db.get_user_bookings(user_id)
            
            if not user_flights or not user_bookings:
                return {"status": "error", "message": "No flight or booking data found"}
            
            flight = user_flights[0]  # Assume first flight
            booking = user_bookings[0]  # Assume first booking
            
            # 3. Check if flight has landed
            flight_status = await self._get_flight_status(flight)
            if flight_status.get("status") in ["LANDED", "ARRIVED"]:
                await self._trigger_arrival_flow(user_id, flight, booking, location_data)
                return {"status": "arrival_flow_triggered", "message": "Arrival services initiated"}
            else:
                return {"status": "flight_not_landed", "message": "Flight has not landed yet"}
                
        except Exception as e:
            logger.error(f"❌ Error handling arrival detection: {e}")
            return {"status": "error", "message": str(e)}
    
    async def _trigger_arrival_flow(self, user_id: str, flight: Dict[str, Any], booking: Dict[str, Any], location_data: Dict[str, Any]):
        """Trigger complete arrival flow - Hotel Agent handles family notifications and cab arrangement"""
        try:
            # 1. Send arrival notification to Hotel Agent (who will handle family notification + cab arrangement)
            await self._send_flight_landed_notification_to_hotel_agent(user_id, flight, booking, location_data)
            
            # 2. Send hospital appointment confirmation
            await self._send_hospital_confirmation(user_id, booking)
            
            # 3. Update orchestration status
            orchestration_id = f"ORCH_{user_id}"
            dummy_db.update_orchestration_status(orchestration_id, "arrival_services", {
                "flow_step": "arrival_services_triggered",
                "location": location_data,
                "services_requested": ["flight_landed_family_notification", "hotel_notification", "cab_arrangement", "hospital_confirmation"]
            })
            
            logger.info(f"✅ Arrival flow triggered for user {user_id} - Hotel Agent will handle family notification and cab")
            
        except Exception as e:
            logger.error(f"❌ Error triggering arrival flow: {e}")
    
    async def _send_flight_landed_notification_to_hotel_agent(self, user_id: str, flight: Dict[str, Any], booking: Dict[str, Any], location_data: Dict[str, Any]):
        """Send flight landed notification to Hotel Agent - they handle family notification, hotel notification, and cab arrangement"""
        try:
            hotel_payload = {
                "jsonrpc": "2.0",
                "id": f"flight_landed_{user_id}",
                "method": "HandleFlightLanded",
                "params": {
                    "user_id": user_id,
                    "patient_name": booking.get("patient_name"),
                    "flight_details": {
                        "flight_number": flight.get("flight_number"),
                        "airline": flight.get("airline"),
                        "arrival_time": flight.get("estimated_arrival_local"),
                        "gate": flight.get("gate"),
                        "terminal": flight.get("terminal"),
                        "status": flight.get("status")
                    },
                    "airport_details": {
                        "airport_code": location_data.get("airport_code"),
                        "airport_name": location_data.get("airport_name"),
                        "latitude": location_data.get("latitude"),
                        "longitude": location_data.get("longitude")
                    },
                    "hotel_details": {
                        "hotel_name": booking.get("hotel_name"),
                        "hotel_room_number": booking.get("hotel_room_number"),
                        "booking_reference": booking.get("hotel_booking_reference"),
                        "check_in_date": booking.get("hotel_check_in")
                    },
                    "family_contacts": booking.get("emergency_contacts", []),
                    "special_requirements": booking.get("special_requirements"),
                    "orchestration_id": f"ORCH_{user_id}",
                    "tasks": {
                        "notify_family": True,
                        "notify_hotel": True,
                        "arrange_cab": True,
                        "estimated_arrival_to_hotel": "30 minutes"
                    }
                }
            }
            
            await self._send_a2a_task("hotel_agent", "HandleFlightLanded", hotel_payload)
            logger.info("✅ Flight landed notification sent to Hotel Agent - they will handle family notification, hotel notification, and cab arrangement")
            
        except Exception as e:
            logger.error(f"❌ Error sending flight landed notification to Hotel Agent: {e}")

    async def _send_hotel_confirmation_request(self, user_id: str, booking: Dict[str, Any]):
        """Send hotel confirmation request"""
        try:
            hotel_payload = {
                "jsonrpc": "2.0",
                "id": f"hotel_confirm_{user_id}",
                "method": "ConfirmHotelBooking",
                "params": {
                    "booking_reference": booking.get("hotel_booking_reference"),
                    "guest_name": booking.get("patient_name"),
                    "check_in_date": booking.get("hotel_check_in"),
                    "special_requirements": booking.get("special_requirements"),
                    "orchestration_id": f"ORCH_{user_id}"
                }
            }
            
            await self._send_a2a_task("hotel_agent", "ConfirmHotelBooking", hotel_payload)
            logger.info("✅ Hotel confirmation request sent")
            
        except Exception as e:
            logger.error(f"❌ Error sending hotel confirmation: {e}")
    
    
    async def _send_hospital_confirmation(self, user_id: str, booking: Dict[str, Any]):
        """Send hospital appointment confirmation"""
        try:
            hospital_payload = {
                "jsonrpc": "2.0",
                "id": f"hospital_confirm_{user_id}",
                "method": "ConfirmHospitalAppointment",
                "params": {
                    "appointment_id": booking.get("hospital_appointment_id"),
                    "patient_name": booking.get("patient_name"),
                    "appointment_time": booking.get("hospital_appointment_time"),
                    "medical_conditions": booking.get("medical_conditions", []),
                    "orchestration_id": f"ORCH_{user_id}"
                }
            }
            
            await self._send_a2a_task("hospital_agent", "ConfirmHospitalAppointment", hospital_payload)
            logger.info("✅ Hospital confirmation sent")
            
        except Exception as e:
            logger.error(f"❌ Error sending hospital confirmation: {e}")
    
    async def handle_cab_arrival_notification(self, user_id: str, cab_details: Dict[str, Any]) -> Dict[str, Any]:
        """Handle cab arrival - trigger voice call to user"""
        try:
            # 1. Send voice call to inform user about cab arrival
            await self._trigger_cab_arrival_call(user_id, cab_details)
            
            # 2. Update orchestration status
            orchestration_id = f"ORCH_{user_id}"
            dummy_db.update_orchestration_status(orchestration_id, "cab_arrived", {
                "flow_step": "cab_arrival_notification",
                "cab_details": cab_details
            })
            
            logger.info(f"✅ Cab arrival notification handled for user {user_id}")
            
            return {"status": "voice_call_triggered", "message": "Voice call initiated to inform about cab arrival"}
            
        except Exception as e:
            logger.error(f"❌ Error handling cab arrival: {e}")
            return {"status": "error", "message": str(e)}
    
    async def _trigger_cab_arrival_call(self, user_id: str, cab_details: Dict[str, Any]):
        """Trigger voice call to inform user about cab arrival"""
        try:
            # Get user context for voice agent
            user_bookings = dummy_db.get_user_bookings(user_id)
            user_flights = dummy_db.get_user_flights(user_id)
            user_location = dummy_db.get_user_location(user_id)
            
            if not user_bookings:
                logger.error(f"No booking data found for user {user_id}")
                return
            
            booking = user_bookings[0]
            flight = user_flights[0] if user_flights else {}
            
            # Prepare comprehensive context for voice agent with required template variables
            context_data = {
                # Voice Agent Template Variables (Required)
                "patient_name": booking.get("patient_name"),
                "patient_id": booking.get("user_id", user_id),
                "patient_language": booking.get("patient_language", "English"),
                "patient_contact": booking.get("emergency_contacts", [""])[0] if booking.get("emergency_contacts") else "",
                "companion_name": booking.get("companion_name", "Not specified"),
                "check_in_date": booking.get("hotel_check_in", "").split("T")[0] if booking.get("hotel_check_in") else "",
                "check_out_date": booking.get("new_discharge_date", "").split("T")[0] if booking.get("new_discharge_date") else "",
                "hotel_name": booking.get("hotel_name", "Denver Accessible Suites"),
                "hotel_room_number": booking.get("hotel_room_number", "Suite 205"),
                "hospital_name": booking.get("hospital_name", "Denver Medical Center"),
                "doctor_name": booking.get("doctor_name", "Dr. Smith"),
                "appointment_date": booking.get("hospital_appointment_time", "").split("T")[0] if booking.get("hospital_appointment_time") else "",
                "appointment_time": booking.get("hospital_appointment_time", "").split("T")[1][:5] if booking.get("hospital_appointment_time") else "",
                "pickup_time": cab_details.get("estimated_arrival", "15 minutes"),
                "discharge_date": booking.get("new_discharge_date", "").split("T")[0] if booking.get("new_discharge_date") else "",
                
                # Additional Context for Voice Agent
                "user_id": user_id,
                "patient_info": {
                    "name": booking.get("patient_name"),
                    "medical_conditions": booking.get("medical_conditions", []),
                    "special_requirements": booking.get("special_requirements")
                },
                "current_status": {
                    "location": user_location,
                    "flight_status": flight.get("status_data", {}),
                    "cab_details": cab_details
                },
                "trip_details": {
                    "hotel": booking.get("hotel_booking_reference"),
                    "hospital_appointment": {
                        "id": booking.get("hospital_appointment_id"),
                        "time": booking.get("hospital_appointment_time")
                    }
                }
            }
            
            voice_payload = {
                "jsonrpc": "2.0",
                "id": f"voice_call_{user_id}",
                "method": "InitiateVoiceCall",
                "params": {
                    "user_id": user_id,
                    "call_type": "cab_arrival_notification",
                    "context": context_data,
                    "message": f"Your cab has arrived at {cab_details.get('gate', 'the gate')}. Please proceed to the pickup area.",
                    "orchestration_id": f"ORCH_{user_id}"
                }
            }
            
            await self._send_a2a_task("voice_agent", "InitiateVoiceCall", voice_payload)
            logger.info("✅ Cab arrival voice call triggered")
            
        except Exception as e:
            logger.error(f"❌ Error triggering cab arrival call: {e}")
    
    async def get_user_trip_status(self, user_id: str) -> Dict[str, Any]:
        """Get comprehensive trip status for user"""
        try:
            # Use dummy data instead of database for now
            user_bookings = dummy_db.get_user_bookings(user_id)
            user_flights = dummy_db.get_user_flights(user_id)
            user_location = dummy_db.get_user_location(user_id)
            
            # Get orchestration status
            orchestration_id = f"ORCH_{user_id}"
            orchestration = dummy_db.data.get("orchestrations", {}).get(orchestration_id, {})
            
            # Get adaptive stay information
            stay_info = self._get_adaptive_stay_info(user_bookings[0] if user_bookings else None)
            
            return {
                "user_id": user_id,
                "bookings": user_bookings,
                "flights": user_flights,
                "current_location": user_location,
                "orchestration_status": orchestration.get("status", "unknown"),
                "flow_step": orchestration.get("flow_step", "initial"),
                "last_updated": orchestration.get("updated_at", orchestration.get("created_at")),
                "adaptive_stay": stay_info
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting trip status: {e}")
            return {"status": "error", "message": str(e)}
    
    def _get_adaptive_stay_info(self, booking: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Get adaptive stay information for the booking"""
        try:
            # Handle case when no booking is provided
            if not booking:
                return {
                    "status": "planned",
                    "initial_estimate_days": 7,
                    "extended": False,
                    "flexible_booking": True,
                    "extension_capability": True,
                    "auto_rebooking": True,
                    "family_notifications": True
                }
            
            # Calculate stay duration and flexibility
            check_in_str = booking.get("hotel_check_in", "")
            hospital_appt_str = booking.get("hospital_appointment_time", "")
            
            # Parse dates
            check_in_date = None
            hospital_date = None
            
            if check_in_str:
                try:
                    check_in_date = datetime.fromisoformat(check_in_str.replace('Z', '+00:00'))
                except:
                    pass
            
            if hospital_appt_str:
                try:
                    hospital_date = datetime.fromisoformat(hospital_appt_str.replace('Z', '+00:00'))
                except:
                    pass
            
            # Calculate initial stay estimate
            initial_stay_days = 7  # Default estimate
            if check_in_date and hospital_date:
                diff_days = (hospital_date - check_in_date).days
                initial_stay_days = max(diff_days + 3, 7)  # At least 3 days after treatment
            
            # Determine stay status
            current_date = datetime.now()
            stay_status = "planned"
            
            if check_in_date and current_date >= check_in_date:
                stay_status = "active"
            
            if hospital_date and current_date >= hospital_date:
                stay_status = "treatment_phase"
            
            # Check for extensions
            extended = False
            if booking.get("stay_extended", False):
                extended = True
                stay_status = "extended"
            
            return {
                "status": stay_status,
                "initial_estimate_days": initial_stay_days,
                "extended": extended,
                "flexible_booking": True,
                "extension_capability": True,
                "auto_rebooking": True,
                "family_notifications": True
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get adaptive stay info: {e}")
            return {
                "status": "planned",
                "initial_estimate_days": 7,
                "extended": False,
                "flexible_booking": True,
                "extension_capability": True,
                "auto_rebooking": True,
                "family_notifications": True
            }
    
    # ==================== ADAPTIVE STAY MANAGEMENT ====================
    
    async def handle_stay_extension(self, user_id: str, extension_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle hospital stay extension - the core adaptive feature"""
        try:
            logger.info(f"🏥 Processing stay extension for user {user_id}")
            
            # Get current booking from database
            user_bookings = orchestrator_db_service.get_user_bookings(user_id)
            if not user_bookings:
                return {"status": "error", "message": "No booking found"}
            
            booking = user_bookings[0]
            
            # Extract extension details
            new_discharge_date = extension_data.get("new_discharge_date")
            extension_reason = extension_data.get("reason", "Medical treatment extended")
            extension_days = extension_data.get("extension_days", 3)
            
            logger.info(f"📅 Extending stay by {extension_days} days until {new_discharge_date}")
            
            # Update booking with extension
            booking["stay_extended"] = True
            booking["extension_reason"] = extension_reason
            booking["new_discharge_date"] = new_discharge_date
            booking["extension_days"] = extension_days
            
            # Update dummy database
            dummy_db.update_booking(user_id, booking)
            
            # Trigger adaptive responses - each agent handles its own voice/notification
            results = []
            
            # 1. Extend hotel booking (Hotel agent handles guest notification + voice call)
            hotel_result = await self._extend_hotel_booking(user_id, booking, new_discharge_date)
            results.append({"action": "hotel_extension_with_notification", "result": hotel_result})
            
            # 2. Update flight recommendations
            flight_result = await self._update_flight_recommendations(user_id, booking, new_discharge_date)
            results.append({"action": "flight_update", "result": flight_result})
            
            # 3. Coordinate hospital extension (Hospital agent handles family notification + medical updates)
            hospital_result = await self._coordinate_hospital_extension(user_id, booking, extension_data)
            results.append({"action": "hospital_coordination_with_family_notification", "result": hospital_result})
            
            logger.info(f"✅ Stay extension completed for user {user_id}")
            
            return {
                "status": "success",
                "message": f"Stay extended by {extension_days} days",
                "new_discharge_date": new_discharge_date,
                "actions_completed": results,
                "adaptive_response": "automatic"
            }
            
        except Exception as e:
            logger.error(f"❌ Error handling stay extension: {e}")
            return {"status": "error", "message": str(e)}
    
    async def _extend_hotel_booking(self, user_id: str, booking: Dict[str, Any], new_discharge_date: str) -> Dict[str, Any]:
        """Extend hotel booking automatically - Hotel agent handles its own voice/notification"""
        try:
            logger.info(f"🏨 Extending hotel booking for user {user_id}")
            
            # Prepare comprehensive hotel extension request
            # Hotel agent will handle: booking extension + guest notification + voice confirmation
            task_data = {
                "params": {
                    "booking_reference": booking.get("hotel_booking_reference"),
                    "guest_name": booking.get("patient_name"),
                    "new_checkout_date": new_discharge_date,
                    "extension_reason": "Medical treatment extended",
                    "special_requirements": booking.get("special_requirements", ""),
                    "contact_email": booking.get("email"),
                    "guest_phone": booking.get("emergency_contacts", [""])[0],
                    "auto_notify_guest": True,  # Hotel agent will notify guest
                    "auto_voice_call": True,    # Hotel agent will call guest to confirm
                    "orchestration_context": {
                        "user_id": user_id,
                        "stay_extension": True,
                        "adaptive_response": True
                    }
                }
            }
            
            # Call hotel agent - it handles extension + notification + voice internally
            result = await self._send_a2a_task("hotel_agent", "HandleStayExtension", task_data)
            
            logger.info(f"✅ Hotel extension handled (includes guest notification & voice call): {result.get('status', 'unknown')}")
            return result
            
        except Exception as e:
            logger.error(f"❌ Error extending hotel booking: {e}")
            return {"status": "error", "message": str(e)}
    
    async def _update_flight_recommendations(self, user_id: str, booking: Dict[str, Any], new_discharge_date: str) -> Dict[str, Any]:
        """Update flight recommendations based on new discharge date"""
        try:
            logger.info(f"✈️ Updating flight recommendations for user {user_id}")
            
            # Get current flight
            flight = dummy_db.get_user_flight(user_id)
            if not flight:
                return {"status": "no_flight", "message": "No flight found"}
            
            # Prepare flight update request
            task_data = {
                "params": {
                    "flight_number": flight.get("flight_number"),
                    "original_date": flight.get("departure_date"),
                    "new_departure_date": new_discharge_date,
                    "passenger_name": booking.get("patient_name"),
                    "booking_reference": flight.get("flight_id"),
                    "change_reason": "Medical treatment extended"
                }
            }
            
            # Call flight agent for rebooking options
            result = await self._send_a2a_task("flight_agent", "GetRebookingOptions", task_data)
            
            logger.info(f"✅ Flight rebooking options: {result.get('status', 'unknown')}")
            return result
            
        except Exception as e:
            logger.error(f"❌ Error updating flight recommendations: {e}")
            return {"status": "error", "message": str(e)}
    
    
    async def _coordinate_hospital_extension(self, user_id: str, booking: Dict[str, Any], extension_data: Dict[str, Any]) -> Dict[str, Any]:
        """Coordinate with hospital for extended stay - Hospital agent handles its own family notifications"""
        try:
            logger.info(f"🏥 Coordinating hospital extension for user {user_id}")
            
            # Prepare comprehensive hospital coordination request
            # Hospital agent will handle: medical coordination + family notifications + patient updates
            task_data = {
                "params": {
                    "appointment_id": booking.get("hospital_appointment_id"),
                    "patient_name": booking.get("patient_name"),
                    "new_discharge_date": extension_data.get("new_discharge_date"),
                    "extension_reason": extension_data.get("reason", "Medical treatment extended"),
                    "extension_days": extension_data.get("extension_days", 3),
                    "medical_conditions": booking.get("medical_conditions", []),
                    "special_requirements": booking.get("special_requirements", ""),
                    "family_contacts": booking.get("emergency_contacts", []),
                    "patient_email": booking.get("email"),
                    "auto_notify_family": True,  # Hospital agent will notify family
                    "auto_update_patient": True, # Hospital agent will update patient records
                    "orchestration_context": {
                        "user_id": user_id,
                        "stay_extension": True,
                        "adaptive_response": True
                    }
                }
            }
            
            # Coordinate with hospital agent - it handles medical + family notification internally
            result = await self._send_a2a_task("hospital_agent", "HandleStayExtension", task_data)
            
            logger.info(f"✅ Hospital coordination handled (includes family notification & medical updates): {result.get('status', 'unknown')}")
            return result
            
        except Exception as e:
            logger.error(f"❌ Error coordinating with hospital: {e}")
            return {"status": "error", "message": str(e)}
    
    async def check_daily_treatment_updates(self) -> Dict[str, Any]:
        """Check for daily treatment updates from hospital - adaptive scheduling"""
        try:
            logger.info("🔄 Checking daily treatment updates...")
            
            # Get all active patients
            # Get all active patients from database (this would need to be implemented)
            # For now, use a subset of known demo patients
            all_bookings = {}
            demo_users = ["PAT-DEMO-001", "PAT-DEMO-002", "PAT-DEMO-003"]
            for user_id in demo_users:
                user_bookings = orchestrator_db_service.get_user_bookings(user_id)
                if user_bookings:
                    all_bookings[user_id] = user_bookings
            updates_found = 0
            
            for booking_id, booking in all_bookings.items():
                if booking.get("status") == "confirmed":
                    user_id = booking.get("user_id")
                    appointment_id = booking.get("hospital_appointment_id")
                    
                    # Check for hospital updates (simulated)
                    hospital_update = await self._check_hospital_status(appointment_id)
                    
                    if hospital_update and hospital_update.get("discharge_date_changed"):
                        logger.info(f"📅 Discharge date changed for user {user_id}")
                        
                        # Handle automatic extension
                        extension_data = {
                            "new_discharge_date": hospital_update.get("new_discharge_date"),
                            "reason": hospital_update.get("reason", "Treatment progress updated"),
                            "extension_days": hospital_update.get("extension_days", 2)
                        }
                        
                        await self.handle_stay_extension(user_id, extension_data)
                        updates_found += 1
            
            logger.info(f"📊 Daily treatment check completed. Found {updates_found} updates.")
            
            return {
                "status": "success",
                "updates_found": updates_found,
                "message": f"Checked {len(all_bookings)} active patients"
            }
            
        except Exception as e:
            logger.error(f"❌ Error checking daily treatment updates: {e}")
            return {"status": "error", "message": str(e)}
    
    async def _check_hospital_status(self, appointment_id: str) -> Dict[str, Any]:
        """Check hospital status for treatment updates (simulated)"""
        try:
            # In real implementation, this would call hospital API
            # For demo, we'll simulate occasional updates
            
            import random
            if random.random() < 0.1:  # 10% chance of update
                return {
                    "discharge_date_changed": True,
                    "new_discharge_date": (datetime.now() + timedelta(days=3)).isoformat(),
                    "reason": "Recovery progressing well, extended monitoring recommended",
                    "extension_days": 2
                }
            
            return {"discharge_date_changed": False}
            
        except Exception as e:
            logger.error(f"❌ Error checking hospital status: {e}")
            return {"discharge_date_changed": False}

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
