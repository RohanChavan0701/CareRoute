"""
Voice Agent - A2A Sub-Agent
Handles voice communication via Twilio/OpenAI Realtime for elderly travelers.
"""

import asyncio
import logging
from typing import Dict, Any, Optional
from datetime import datetime
from enum import Enum

from backend.a2a_client import AgentCard, TaskResult, A2AClient
from backend.base_agent import BaseAgent
from pydantic import BaseModel

logger = logging.getLogger(__name__)

class CallType(str, Enum):
    """Types of voice calls"""
    INFORMATION = "information"
    EMERGENCY = "emergency"
    REMINDER = "reminder"
    CHECK_IN = "check_in"
    FAMILY_UPDATE = "family_update"

class VoiceCall(BaseModel):
    """Voice call information"""
    call_id: str
    call_type: CallType
    phone_number: str
    scheduled_time: datetime
    status: str = "scheduled"
    duration: Optional[int] = None
    transcript: Optional[str] = None

class VoiceAgent(BaseAgent):
    """
    Voice Agent for Guardian system
    Handles voice communication using Twilio and OpenAI Realtime
    """
    
    def __init__(self, a2a_client: A2AClient):
        agent_card = self._create_agent_card()
        super().__init__(
            agent_id="voice_agent",
            agent_card=agent_card,
            a2a_client=a2a_client
        )
        self.active_calls: Dict[str, VoiceCall] = {}
        
    def _create_agent_card(self) -> AgentCard:
        """Create Voice agent card defining capabilities"""
        return AgentCard(
            agent_id="voice_agent",
            name="Voice Communication Agent",
            description="Handles voice calls and real-time communication for elderly travelers",
            version="1.0.0",
            capabilities=[
                "outbound_calls",
                "real_time_communication",
                "voice_transcription",
                "emergency_voice_alerts",
                "multilingual_support",
                "accessibility_features"
            ],
            endpoints={
                "call": "/voice/call",
                "transcribe": "/voice/transcribe",
                "emergency": "/voice/emergency"
            },
            health_check="/voice/health",
            supported_tasks=[
                "InitiateCall",
                "ScheduleCall",
                "EmergencyVoiceAlert",
                "TranscribeCall",
                "VoiceReminder",
                "FamilyVoiceUpdate"
            ]
        )
    
    async def handle_task(self, task: str, payload: Dict[str, Any]) -> TaskResult:
        """
        Handle incoming A2A tasks
        """
        logger.info(f"Voice Agent handling task: {task}")
        
        try:
            if task == "InitiateCall":
                return await self._initiate_call(payload)
            elif task == "ScheduleCall":
                return await self._schedule_call(payload)
            elif task == "EmergencyVoiceAlert":
                return await self._emergency_voice_alert(payload)
            elif task == "TranscribeCall":
                return await self._transcribe_call(payload)
            elif task == "VoiceReminder":
                return await self._voice_reminder(payload)
            elif task == "FamilyVoiceUpdate":
                return await self._family_voice_update(payload)
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
    
    async def _initiate_call(self, payload: Dict[str, Any]) -> TaskResult:
        """Initiate immediate voice call"""
        phone_number = payload.get("phone_number")
        call_type = CallType(payload.get("call_type", "information"))
        message = payload.get("message", "")
        
        logger.info(f"Initiating {call_type} call to {phone_number}")
        
        # Create call record
        call_id = f"VOICE_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        voice_call = VoiceCall(
            call_id=call_id,
            call_type=call_type,
            phone_number=phone_number,
            scheduled_time=datetime.now(),
            status="initiating"
        )
        
        self.active_calls[call_id] = voice_call
        
        # Simulate Twilio/OpenAI Realtime call initiation
        await asyncio.sleep(1.0)  # Simulate call setup
        
        # Mock call content based on type
        call_content = self._generate_call_content(call_type, payload)
        
        voice_call.status = "completed"
        voice_call.duration = 120  # Mock 2-minute call
        voice_call.transcript = call_content
        
        logger.info(f"Voice call {call_id} completed")
        
        return TaskResult(
            success=True,
            data={
                "call_id": call_id,
                "call_type": call_type.value,
                "phone_number": phone_number,
                "status": "completed",
                "duration_seconds": voice_call.duration,
                "transcript": call_content,
                "completion_time": datetime.now().isoformat()
            }
        )
    
    async def _schedule_call(self, payload: Dict[str, Any]) -> TaskResult:
        """Schedule future voice call"""
        phone_number = payload.get("phone_number")
        call_type = CallType(payload.get("call_type", "reminder"))
        scheduled_time = payload.get("scheduled_time")
        
        logger.info(f"Scheduling {call_type} call to {phone_number} for {scheduled_time}")
        
        # Create scheduled call record
        call_id = f"SCHED_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        voice_call = VoiceCall(
            call_id=call_id,
            call_type=call_type,
            phone_number=phone_number,
            scheduled_time=datetime.fromisoformat(scheduled_time),
            status="scheduled"
        )
        
        self.active_calls[call_id] = voice_call
        
        # Simulate scheduling
        await asyncio.sleep(0.3)
        
        return TaskResult(
            success=True,
            data={
                "call_id": call_id,
                "call_type": call_type.value,
                "phone_number": phone_number,
                "scheduled_time": scheduled_time,
                "status": "scheduled",
                "scheduling_time": datetime.now().isoformat()
            }
        )
    
    async def _emergency_voice_alert(self, payload: Dict[str, Any]) -> TaskResult:
        """Send emergency voice alert"""
        phone_numbers = payload.get("phone_numbers", [])
        emergency_type = payload.get("emergency_type", "medical")
        location = payload.get("location", "Unknown")
        
        logger.warning(f"Emergency voice alert: {emergency_type} at {location}")
        
        # Create emergency call records
        emergency_calls = []
        
        for phone_number in phone_numbers:
            call_id = f"EMERG_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            voice_call = VoiceCall(
                call_id=call_id,
                call_type=CallType.EMERGENCY,
                phone_number=phone_number,
                scheduled_time=datetime.now(),
                status="initiating"
            )
            
            self.active_calls[call_id] = voice_call
            emergency_calls.append(call_id)
        
        # Simulate emergency calls
        await asyncio.sleep(0.5)
        
        # Update all emergency calls as completed
        for call_id in emergency_calls:
            if call_id in self.active_calls:
                self.active_calls[call_id].status = "completed"
                self.active_calls[call_id].duration = 60
        
        return TaskResult(
            success=True,
            data={
                "emergency_calls": emergency_calls,
                "emergency_type": emergency_type,
                "location": location,
                "phones_contacted": phone_numbers,
                "alert_time": datetime.now().isoformat()
            }
        )
    
    async def _transcribe_call(self, payload: Dict[str, Any]) -> TaskResult:
        """Transcribe voice call"""
        call_id = payload.get("call_id")
        audio_data = payload.get("audio_data")  # Would be actual audio in real implementation
        
        logger.info(f"Transcribing call {call_id}")
        
        # Simulate transcription process
        await asyncio.sleep(0.8)
        
        # Mock transcription result
        transcript = "This is a mock transcription of the voice call. The patient confirmed their hotel booking and hospital appointment."
        
        if call_id in self.active_calls:
            self.active_calls[call_id].transcript = transcript
        
        return TaskResult(
            success=True,
            data={
                "call_id": call_id,
                "transcript": transcript,
                "confidence_score": 0.95,
                "language": "en-US",
                "transcription_time": datetime.now().isoformat()
            }
        )
    
    async def _voice_reminder(self, payload: Dict[str, Any]) -> TaskResult:
        """Send voice reminder"""
        phone_number = payload.get("phone_number")
        reminder_type = payload.get("reminder_type", "appointment")
        reminder_time = payload.get("reminder_time")
        
        logger.info(f"Voice reminder: {reminder_type} to {phone_number}")
        
        # Create reminder call
        call_id = f"REMIND_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        voice_call = VoiceCall(
            call_id=call_id,
            call_type=CallType.REMINDER,
            phone_number=phone_number,
            scheduled_time=datetime.now(),
            status="completed"
        )
        
        self.active_calls[call_id] = voice_call
        
        # Simulate reminder call
        await asyncio.sleep(0.6)
        
        return TaskResult(
            success=True,
            data={
                "call_id": call_id,
                "reminder_type": reminder_type,
                "phone_number": phone_number,
                "status": "completed",
                "reminder_time": datetime.now().isoformat()
            }
        )
    
    async def _family_voice_update(self, payload: Dict[str, Any]) -> TaskResult:
        """Send voice update to family"""
        family_phone = payload.get("family_phone")
        update_type = payload.get("update_type", "status")
        patient_status = payload.get("patient_status", "good")
        
        logger.info(f"Family voice update: {update_type} to {family_phone}")
        
        # Create family update call
        call_id = f"FAMILY_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        voice_call = VoiceCall(
            call_id=call_id,
            call_type=CallType.FAMILY_UPDATE,
            phone_number=family_phone,
            scheduled_time=datetime.now(),
            status="completed"
        )
        
        self.active_calls[call_id] = voice_call
        
        # Simulate family update call
        await asyncio.sleep(0.7)
        
        return TaskResult(
            success=True,
            data={
                "call_id": call_id,
                "update_type": update_type,
                "family_phone": family_phone,
                "patient_status": patient_status,
                "status": "completed",
                "update_time": datetime.now().isoformat()
            }
        )
    
    def _generate_call_content(self, call_type: CallType, payload: Dict[str, Any]) -> str:
        """Generate mock call content based on call type"""
        if call_type == CallType.INFORMATION:
            return "Hello, this is Guardian calling to confirm your hotel booking and hospital appointment. Your flight is on schedule and all arrangements are confirmed."
        elif call_type == CallType.EMERGENCY:
            return "EMERGENCY ALERT: There has been a medical emergency. Please contact the hospital immediately. Location and details have been sent to your emergency contacts."
        elif call_type == CallType.REMINDER:
            return "This is a reminder that your hospital appointment is in 2 hours. Please ensure you have all your medications and medical documents ready."
        elif call_type == CallType.CHECK_IN:
            return "Hello, this is Guardian checking in. How are you feeling? Do you need any assistance with your medical travel arrangements?"
        elif call_type == CallType.FAMILY_UPDATE:
            return "This is Guardian with an update for the family. The patient has arrived safely and all medical appointments are confirmed. They are in good spirits."
        else:
            return "This is Guardian calling with an important update regarding your medical travel arrangements."
    
    async def get_call_status(self, call_id: str) -> Dict[str, Any]:
        """Get current call status"""
        if call_id not in self.active_calls:
            return {"error": "Call not found"}
        
        call = self.active_calls[call_id]
        return {
            "call_id": call_id,
            "call_type": call.call_type.value,
            "phone_number": call.phone_number,
            "status": call.status,
            "duration": call.duration,
            "transcript": call.transcript
        }

# Global Voice agent instance (will be initialized with A2A client)
voice_agent = None
