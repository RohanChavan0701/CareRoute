"""
Hotel Agent - A2A Sub-Agent
Handles hotel booking confirmations and coordination for elderly travelers.
"""

import asyncio
import logging
from typing import Dict, Any
from datetime import datetime

from backend.a2a_client import AgentCard, TaskResult, A2AClient
from backend.base_agent import BaseAgent
from pydantic import BaseModel

logger = logging.getLogger(__name__)

class HotelBooking(BaseModel):
    """Hotel booking information"""
    booking_reference: str
    hotel_name: str
    check_in: datetime
    check_out: datetime
    special_requirements: str = ""
    accessibility_needs: bool = False

class HotelAgent(BaseAgent):
    """
    Hotel Agent for Guardian system
    Handles hotel booking confirmations and special accommodations
    """
    
    def __init__(self, a2a_client: A2AClient):
        agent_card = self._create_agent_card()
        super().__init__(
            agent_id="hotel_agent",
            agent_card=agent_card,
            a2a_client=a2a_client
        )
        self.active_bookings: Dict[str, HotelBooking] = {}
        
    def _create_agent_card(self) -> AgentCard:
        """Create Hotel agent card defining capabilities"""
        return AgentCard(
            agent_id="hotel_agent",
            name="Hotel Coordination Agent",
            description="Handles hotel bookings and accommodations for elderly travelers",
            version="1.0.0",
            capabilities=[
                "booking_confirmation",
                "accessibility_coordination",
                "special_requirements",
                "emergency_contact",
                "late_check_in"
            ],
            endpoints={
                "confirm": "/hotel/confirm",
                "modify": "/hotel/modify",
                "emergency": "/hotel/emergency"
            },
            health_check="/hotel/health",
            supported_tasks=[
                "ConfirmHotel",
                "CheckAccessibility",
                "ArrangeLateCheckIn",
                "SpecialRequirements",
                "EmergencyContact"
            ]
        )
    
    async def handle_task(self, task: str, payload: Dict[str, Any]) -> TaskResult:
        """
        Handle incoming A2A tasks
        """
        logger.info(f"Hotel Agent handling task: {task}")
        
        try:
            if task == "ConfirmHotel":
                return await self._confirm_hotel_booking(payload)
            elif task == "CheckAccessibility":
                return await self._check_accessibility(payload)
            elif task == "ArrangeLateCheckIn":
                return await self._arrange_late_checkin(payload)
            elif task == "SpecialRequirements":
                return await self._handle_special_requirements(payload)
            elif task == "EmergencyContact":
                return await self._emergency_contact(payload)
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
    
    async def _confirm_hotel_booking(self, payload: Dict[str, Any]) -> TaskResult:
        """Confirm hotel booking for passenger"""
        flight_number = payload.get("flight_number")
        passenger_id = payload.get("passenger_id")
        
        logger.info(f"Confirming hotel booking for flight {flight_number}, passenger {passenger_id}")
        
        # Mock hotel booking confirmation
        booking = HotelBooking(
            booking_reference=f"HOTEL_{flight_number}_{passenger_id}",
            hotel_name="Grand Medical Hotel",
            check_in=datetime.now(),
            check_out=datetime.now(),
            special_requirements="Wheelchair accessible room, ground floor",
            accessibility_needs=True
        )
        
        self.active_bookings[flight_number] = booking
        
        # Simulate hotel confirmation process
        await asyncio.sleep(0.5)  # Simulate API call
        
        logger.info(f"Hotel booking confirmed: {booking.booking_reference}")
        
        return TaskResult(
            success=True,
            data={
                "booking_reference": booking.booking_reference,
                "hotel_name": booking.hotel_name,
                "confirmed": True,
                "accessibility_confirmed": True,
                "special_requirements": booking.special_requirements,
                "confirmation_time": datetime.now().isoformat()
            }
        )
    
    async def _check_accessibility(self, payload: Dict[str, Any]) -> TaskResult:
        """Verify accessibility accommodations"""
        flight_number = payload.get("flight_number")
        
        if flight_number not in self.active_bookings:
            return TaskResult(
                success=False,
                error="Booking not found"
            )
        
        booking = self.active_bookings[flight_number]
        
        # Simulate accessibility verification
        await asyncio.sleep(0.3)
        
        return TaskResult(
            success=True,
            data={
                "wheelchair_accessible": True,
                "ground_floor_room": True,
                "medical_equipment_available": True,
                "emergency_call_button": True,
                "verified_time": datetime.now().isoformat()
            }
        )
    
    async def _arrange_late_checkin(self, payload: Dict[str, Any]) -> TaskResult:
        """Arrange late check-in for delayed flights"""
        flight_number = payload.get("flight_number")
        new_eta = payload.get("new_eta")
        
        logger.info(f"Arranging late check-in for flight {flight_number}, new ETA: {new_eta}")
        
        # Simulate late check-in arrangement
        await asyncio.sleep(0.4)
        
        return TaskResult(
            success=True,
            data={
                "late_checkin_arranged": True,
                "contact_person": "Hotel Manager - John Smith",
                "contact_phone": "+1-555-HOTEL",
                "arrangement_time": datetime.now().isoformat()
            }
        )
    
    async def _handle_special_requirements(self, payload: Dict[str, Any]) -> TaskResult:
        """Handle special medical or dietary requirements"""
        flight_number = payload.get("flight_number")
        requirements = payload.get("requirements", [])
        
        logger.info(f"Handling special requirements for flight {flight_number}: {requirements}")
        
        # Simulate requirement processing
        await asyncio.sleep(0.3)
        
        return TaskResult(
            success=True,
            data={
                "requirements_processed": requirements,
                "dietary_accommodations": True,
                "medical_support_available": True,
                "processed_time": datetime.now().isoformat()
            }
        )
    
    async def _emergency_contact(self, payload: Dict[str, Any]) -> TaskResult:
        """Handle emergency contact with hotel"""
        flight_number = payload.get("flight_number")
        emergency_type = payload.get("emergency_type", "medical")
        
        logger.warning(f"Emergency contact with hotel for flight {flight_number}: {emergency_type}")
        
        # Simulate emergency response
        await asyncio.sleep(0.2)
        
        return TaskResult(
            success=True,
            data={
                "emergency_contacted": True,
                "hotel_manager_notified": True,
                "medical_team_alerted": True,
                "response_time": datetime.now().isoformat()
            }
        )
    
    async def get_booking_status(self, flight_number: str) -> Dict[str, Any]:
        """Get current booking status"""
        if flight_number not in self.active_bookings:
            return {"error": "Booking not found"}
        
        booking = self.active_bookings[flight_number]
        return {
            "flight_number": flight_number,
            "booking_reference": booking.booking_reference,
            "hotel_name": booking.hotel_name,
            "accessibility_needs": booking.accessibility_needs,
            "special_requirements": booking.special_requirements
        }

# Global Hotel agent instance (will be initialized with A2A client)
hotel_agent = None
