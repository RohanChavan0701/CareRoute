"""
Hospital Agent - A2A Sub-Agent
Handles hospital appointment confirmations and medical coordination for elderly travelers.
"""

import asyncio
import logging
from typing import Dict, Any, List
from datetime import datetime, timedelta

from backend.a2a_client import AgentCard, TaskResult, A2AClient
from backend.base_agent import BaseAgent
from pydantic import BaseModel

logger = logging.getLogger(__name__)

class MedicalAppointment(BaseModel):
    """Medical appointment information"""
    appointment_id: str
    hospital_name: str
    doctor_name: str
    appointment_time: datetime
    procedure_type: str
    medical_history: str = ""
    medications: List[str] = []
    emergency_contact: str = ""

class HospitalAgent(BaseAgent):
    """
    Hospital Agent for Guardian system
    Handles medical appointments and hospital coordination
    """
    
    def __init__(self, a2a_client: A2AClient):
        agent_card = self._create_agent_card()
        super().__init__(
            agent_id="hospital_agent",
            agent_card=agent_card,
            a2a_client=a2a_client
        )
        self.active_appointments: Dict[str, MedicalAppointment] = {}
        
    def _create_agent_card(self) -> AgentCard:
        """Create Hospital agent card defining capabilities"""
        return AgentCard(
            agent_id="hospital_agent",
            name="Hospital Coordination Agent",
            description="Handles medical appointments and hospital coordination for elderly travelers",
            version="1.0.0",
            capabilities=[
                "appointment_confirmation",
                "medical_history_review",
                "medication_verification",
                "emergency_coordination",
                "specialist_referral",
                "post_procedure_care"
            ],
            endpoints={
                "confirm": "/hospital/confirm",
                "emergency": "/hospital/emergency",
                "medical": "/hospital/medical"
            },
            health_check="/hospital/health",
            supported_tasks=[
                "ConfirmHospital",
                "VerifyMedicalHistory",
                "CheckMedications",
                "ArrangeTransportation",
                "EmergencyMedical",
                "PostProcedureCare"
            ]
        )
    
    async def handle_task(self, task: str, payload: Dict[str, Any]) -> TaskResult:
        """
        Handle incoming A2A tasks
        """
        logger.info(f"Hospital Agent handling task: {task}")
        
        try:
            if task == "ConfirmHospital":
                return await self._confirm_hospital_appointment(payload)
            elif task == "VerifyMedicalHistory":
                return await self._verify_medical_history(payload)
            elif task == "CheckMedications":
                return await self._check_medications(payload)
            elif task == "ArrangeTransportation":
                return await self._arrange_transportation(payload)
            elif task == "EmergencyMedical":
                return await self._emergency_medical(payload)
            elif task == "PostProcedureCare":
                return await self._post_procedure_care(payload)
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
    
    async def _confirm_hospital_appointment(self, payload: Dict[str, Any]) -> TaskResult:
        """Confirm hospital appointment for passenger"""
        flight_number = payload.get("flight_number")
        passenger_id = payload.get("passenger_id")
        
        logger.info(f"Confirming hospital appointment for flight {flight_number}, passenger {passenger_id}")
        
        # Mock hospital appointment confirmation
        appointment = MedicalAppointment(
            appointment_id=f"MED_{flight_number}_{passenger_id}",
            hospital_name="Advanced Medical Center",
            doctor_name="Dr. Sarah Johnson",
            appointment_time=datetime.now() + timedelta(hours=2),
            procedure_type="Cardiology Consultation",
            medical_history="Hypertension, Diabetes Type 2",
            medications=["Metformin", "Lisinopril"],
            emergency_contact="Family: +1-555-FAMILY"
        )
        
        self.active_appointments[flight_number] = appointment
        
        # Simulate hospital confirmation process
        await asyncio.sleep(0.6)  # Simulate API call
        
        logger.info(f"Hospital appointment confirmed: {appointment.appointment_id}")
        
        return TaskResult(
            success=True,
            data={
                "appointment_id": appointment.appointment_id,
                "hospital_name": appointment.hospital_name,
                "doctor_name": appointment.doctor_name,
                "appointment_time": appointment.appointment_time.isoformat(),
                "procedure_type": appointment.procedure_type,
                "confirmed": True,
                "confirmation_time": datetime.now().isoformat()
            }
        )
    
    async def _verify_medical_history(self, payload: Dict[str, Any]) -> TaskResult:
        """Verify patient's medical history"""
        flight_number = payload.get("flight_number")
        
        if flight_number not in self.active_appointments:
            return TaskResult(
                success=False,
                error="Appointment not found"
            )
        
        appointment = self.active_appointments[flight_number]
        
        # Simulate medical history verification
        await asyncio.sleep(0.4)
        
        return TaskResult(
            success=True,
            data={
                "medical_history_verified": True,
                "allergies_confirmed": ["Penicillin", "Latex"],
                "chronic_conditions": ["Hypertension", "Diabetes Type 2"],
                "previous_procedures": ["Cataract Surgery 2022"],
                "verified_time": datetime.now().isoformat()
            }
        )
    
    async def _check_medications(self, payload: Dict[str, Any]) -> TaskResult:
        """Verify current medications and dosages"""
        flight_number = payload.get("flight_number")
        
        if flight_number not in self.active_appointments:
            return TaskResult(
                success=False,
                error="Appointment not found"
            )
        
        appointment = self.active_appointments[flight_number]
        
        # Simulate medication verification
        await asyncio.sleep(0.3)
        
        return TaskResult(
            success=True,
            data={
                "medications_verified": appointment.medications,
                "dosages_confirmed": True,
                "interactions_checked": True,
                "medication_notes": "Continue current dosages, bring all medications to appointment",
                "verified_time": datetime.now().isoformat()
            }
        )
    
    async def _arrange_transportation(self, payload: Dict[str, Any]) -> TaskResult:
        """Arrange medical transportation"""
        flight_number = payload.get("flight_number")
        pickup_time = payload.get("pickup_time")
        
        logger.info(f"Arranging medical transportation for flight {flight_number}")
        
        # Simulate transportation arrangement
        await asyncio.sleep(0.5)
        
        return TaskResult(
            success=True,
            data={
                "transportation_arranged": True,
                "vehicle_type": "Medical Van with Wheelchair Access",
                "driver_name": "Mike Wilson",
                "driver_phone": "+1-555-MEDTRANS",
                "estimated_pickup": pickup_time or datetime.now().isoformat(),
                "arrangement_time": datetime.now().isoformat()
            }
        )
    
    async def _emergency_medical(self, payload: Dict[str, Any]) -> TaskResult:
        """Handle emergency medical situation"""
        flight_number = payload.get("flight_number")
        emergency_type = payload.get("emergency_type", "medical")
        severity = payload.get("severity", "moderate")
        
        logger.warning(f"Medical emergency for flight {flight_number}: {emergency_type} - {severity}")
        
        # Simulate emergency response
        await asyncio.sleep(0.2)
        
        return TaskResult(
            success=True,
            data={
                "emergency_response_activated": True,
                "medical_team_notified": True,
                "ambulance_dispatched": severity == "high",
                "hospital_alerted": True,
                "family_contacted": True,
                "response_time": datetime.now().isoformat()
            }
        )
    
    async def _post_procedure_care(self, payload: Dict[str, Any]) -> TaskResult:
        """Arrange post-procedure care"""
        flight_number = payload.get("flight_number")
        procedure_type = payload.get("procedure_type")
        
        logger.info(f"Arranging post-procedure care for flight {flight_number}")
        
        # Simulate post-procedure care arrangement
        await asyncio.sleep(0.4)
        
        return TaskResult(
            success=True,
            data={
                "post_care_arranged": True,
                "recovery_monitoring": True,
                "follow_up_appointment": True,
                "care_instructions": "Rest for 24 hours, avoid heavy lifting",
                "emergency_contact": "Hospital: +1-555-HOSPITAL",
                "arrangement_time": datetime.now().isoformat()
            }
        )
    
    async def get_appointment_status(self, flight_number: str) -> Dict[str, Any]:
        """Get current appointment status"""
        if flight_number not in self.active_appointments:
            return {"error": "Appointment not found"}
        
        appointment = self.active_appointments[flight_number]
        return {
            "flight_number": flight_number,
            "appointment_id": appointment.appointment_id,
            "hospital_name": appointment.hospital_name,
            "doctor_name": appointment.doctor_name,
            "appointment_time": appointment.appointment_time.isoformat(),
            "procedure_type": appointment.procedure_type
        }

# Global Hospital agent instance (will be initialized with A2A client)
hospital_agent = None
