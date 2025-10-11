"""
Guardian Agent - Main Orchestrator
Coordinates all sub-agents using A2A protocol for medical tourism assistance.
"""

import asyncio
import logging
from typing import Dict, Any, List
from datetime import datetime, timedelta

from backend.a2a_client import AgentCard, TaskResult, A2AClient
from backend.base_agent import BaseAgent
from pydantic import BaseModel

logger = logging.getLogger(__name__)

class GuardianState(BaseModel):
    """Guardian workflow state"""
    flight_number: str
    passenger_id: str
    flight_eta: datetime = None
    hotel_confirmed: bool = False
    hospital_confirmed: bool = False
    family_notified: bool = False
    voice_call_completed: bool = False
    status: str = "pending"
    last_updated: datetime = None

class GuardianAgent(BaseAgent):
    """
    Guardian Orchestrator Agent
    Main coordinator for medical tourism workflow
    """
    
    def __init__(self, a2a_client: A2AClient):
        agent_card = self._create_agent_card()
        super().__init__(
            agent_id="guardian",
            agent_card=agent_card,
            a2a_client=a2a_client
        )
        self.active_workflows: Dict[str, GuardianState] = {}
        
    def _create_agent_card(self) -> AgentCard:
        """Create Guardian agent card defining capabilities"""
        return AgentCard(
            agent_id="guardian",
            name="Guardian Orchestrator",
            description="Medical tourism coordinator for elderly travelers",
            version="1.0.0",
            capabilities=[
                "flight_monitoring",
                "hotel_coordination", 
                "hospital_coordination",
                "family_notification",
                "voice_communication",
                "workflow_orchestration"
            ],
            endpoints={
                "workflow": "/guardian/workflow",
                "status": "/guardian/status",
                "emergency": "/guardian/emergency"
            },
            health_check="/guardian/health",
            supported_tasks=[
                "MonitorFlight",
                "CoordinateHotel",
                "CoordinateHospital", 
                "NotifyFamily",
                "InitiateVoiceCall",
                "HandleEmergency"
            ]
        )
    
    async def handle_task(self, task: str, payload: Dict[str, Any]) -> TaskResult:
        """
        Handle incoming A2A tasks
        """
        logger.info(f"Guardian handling task: {task}")
        
        try:
            if task == "MonitorFlight":
                return await self._monitor_flight(payload)
            elif task == "CoordinateHotel":
                return await self._coordinate_hotel(payload)
            elif task == "CoordinateHospital":
                return await self._coordinate_hospital(payload)
            elif task == "NotifyFamily":
                return await self._notify_family(payload)
            elif task == "InitiateVoiceCall":
                return await self._initiate_voice_call(payload)
            elif task == "HandleEmergency":
                return await self._handle_emergency(payload)
            else:
                return TaskResult(
                    success=False,
                    error=f"Unknown task: {task}"
                )
                
        except Exception as e:
            logger.error(f"Error handling task {task}: {e}")
            return TaskResult(
                success=False,
                error=str(e)
            )
    
    async def _monitor_flight(self, payload: Dict[str, Any]) -> TaskResult:
        """Monitor flight status and ETA"""
        flight_number = payload.get("flight_number")
        passenger_id = payload.get("passenger_id")
        
        logger.info(f"Monitoring flight {flight_number} for passenger {passenger_id}")
        
        # Initialize workflow state
        state = GuardianState(
            flight_number=flight_number,
            passenger_id=passenger_id,
            status="monitoring"
        )
        self.active_workflows[flight_number] = state
        
        # Check if we need to trigger workflow (ETA < 6 hours)
        # This would integrate with flight tracking API
        eta_hours = 4  # Mock value - would come from flight API
        
        if eta_hours < 6:
            logger.info(f"Flight {flight_number} arriving in {eta_hours} hours - triggering workflow")
            await self._trigger_workflow(state)
        
        return TaskResult(
            success=True,
            data={
                "flight_number": flight_number,
                "eta_hours": eta_hours,
                "workflow_triggered": eta_hours < 6
            }
        )
    
    async def _trigger_workflow(self, state: GuardianState):
        """Trigger the complete Guardian workflow"""
        logger.info(f"Triggering Guardian workflow for flight {state.flight_number}")
        
        # Execute workflow steps in sequence
        tasks = [
            ("CoordinateHotel", {"flight_number": state.flight_number, "passenger_id": state.passenger_id}),
            ("CoordinateHospital", {"flight_number": state.flight_number, "passenger_id": state.passenger_id}),
            ("NotifyFamily", {"flight_number": state.flight_number, "passenger_id": state.passenger_id}),
            ("InitiateVoiceCall", {"flight_number": state.flight_number, "passenger_id": state.passenger_id})
        ]
        
        for task_name, task_payload in tasks:
            try:
                # Send task to appropriate sub-agent via A2A
                result = await self._send_a2a_task(task_name, task_payload)
                
                if result.success:
                    # Update state based on task completion
                    if task_name == "CoordinateHotel":
                        state.hotel_confirmed = True
                    elif task_name == "CoordinateHospital":
                        state.hospital_confirmed = True
                    elif task_name == "NotifyFamily":
                        state.family_notified = True
                    elif task_name == "InitiateVoiceCall":
                        state.voice_call_completed = True
                        
                    logger.info(f"Task {task_name} completed successfully")
                else:
                    logger.error(f"Task {task_name} failed: {result.error}")
                    
            except Exception as e:
                logger.error(f"Error executing task {task_name}: {e}")
        
        # Update final state
        state.status = "completed" if all([
            state.hotel_confirmed,
            state.hospital_confirmed, 
            state.family_notified,
            state.voice_call_completed
        ]) else "partial"
        state.last_updated = datetime.now()
    
    async def _coordinate_hotel(self, payload: Dict[str, Any]) -> TaskResult:
        """Coordinate with Hotel Agent"""
        return await self._send_a2a_task("ConfirmHotel", payload)
    
    async def _coordinate_hospital(self, payload: Dict[str, Any]) -> TaskResult:
        """Coordinate with Hospital Agent"""
        return await self._send_a2a_task("ConfirmHospital", payload)
    
    async def _notify_family(self, payload: Dict[str, Any]) -> TaskResult:
        """Notify family via Notify Agent"""
        return await self._send_a2a_task("SendFamilyUpdate", payload)
    
    async def _initiate_voice_call(self, payload: Dict[str, Any]) -> TaskResult:
        """Initiate voice call via Voice Agent"""
        return await self._send_a2a_task("InitiateCall", payload)
    
    async def _handle_emergency(self, payload: Dict[str, Any]) -> TaskResult:
        """Handle emergency situations"""
        logger.warning(f"Emergency situation: {payload}")
        
        # Immediately notify family and hospital
        emergency_tasks = [
            ("SendEmergencyAlert", payload),
            ("NotifyHospitalEmergency", payload)
        ]
        
        results = []
        for task_name, task_payload in emergency_tasks:
            result = await self._send_a2a_task(task_name, task_payload)
            results.append(result)
        
        return TaskResult(
            success=all(r.success for r in results),
            data={"emergency_tasks": results}
        )
    
    async def _send_a2a_task(self, task: str, payload: Dict[str, Any]) -> TaskResult:
        """Send task to sub-agent via A2A protocol"""
        logger.info(f"Sending A2A task {task} to sub-agent")
        
        # Determine target agent based on task type
        target_agent_id = self._get_target_agent_for_task(task)
        
        if not target_agent_id:
            return self.create_task_result(
                success=False,
                error=f"No target agent found for task: {task}"
            )
        
        # Send task via A2A protocol
        return await self.send_task_to_agent(target_agent_id, task, payload)
    
    def _get_target_agent_for_task(self, task: str) -> str:
        """Determine which agent should handle a specific task"""
        task_agent_mapping = {
            "ConfirmHotel": "hotel_agent",
            "CheckAccessibility": "hotel_agent",
            "ArrangeLateCheckIn": "hotel_agent",
            "ConfirmHospital": "hospital_agent",
            "VerifyMedicalHistory": "hospital_agent",
            "CheckMedications": "hospital_agent",
            "SendFamilyUpdate": "notify_agent",
            "EmergencyAlert": "notify_agent",
            "InitiateCall": "voice_agent",
            "EmergencyVoiceAlert": "voice_agent"
        }
        
        return task_agent_mapping.get(task, "")
    
    async def get_workflow_status(self, flight_number: str) -> Dict[str, Any]:
        """Get current workflow status"""
        if flight_number not in self.active_workflows:
            return {"error": "Workflow not found"}
        
        state = self.active_workflows[flight_number]
        return {
            "flight_number": flight_number,
            "status": state.status,
            "hotel_confirmed": state.hotel_confirmed,
            "hospital_confirmed": state.hospital_confirmed,
            "family_notified": state.family_notified,
            "voice_call_completed": state.voice_call_completed,
            "last_updated": state.last_updated.isoformat() if state.last_updated else None
        }
    
    async def cancel_workflow(self, flight_number: str) -> Dict[str, Any]:
        """Cancel active workflow"""
        if flight_number in self.active_workflows:
            state = self.active_workflows[flight_number]
            state.status = "cancelled"
            state.last_updated = datetime.now()
            
            logger.info(f"Cancelled workflow for flight {flight_number}")
            return {"status": "cancelled", "flight_number": flight_number}
        else:
            return {"error": "Workflow not found"}

# Global Guardian agent instance (will be initialized with A2A client)
guardian_agent = None
