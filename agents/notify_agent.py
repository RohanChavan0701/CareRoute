"""
Notify Agent - A2A Sub-Agent
Handles family notifications via SMS, FCM, and other communication channels.
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum

from backend.a2a_client import AgentCard, TaskResult, A2AClient
from backend.base_agent import BaseAgent
from pydantic import BaseModel

logger = logging.getLogger(__name__)

class NotificationType(str, Enum):
    """Types of notifications"""
    STATUS_UPDATE = "status_update"
    EMERGENCY_ALERT = "emergency_alert"
    APPOINTMENT_REMINDER = "appointment_reminder"
    FLIGHT_UPDATE = "flight_update"
    ARRIVAL_CONFIRMATION = "arrival_confirmation"

class NotificationChannel(str, Enum):
    """Notification channels"""
    SMS = "sms"
    EMAIL = "email"
    PUSH = "push"
    VOICE = "voice"

class FamilyNotification(BaseModel):
    """Family notification record"""
    notification_id: str
    notification_type: NotificationType
    channel: NotificationChannel
    recipient: str
    message: str
    sent_time: datetime
    status: str = "pending"
    delivery_confirmed: bool = False

class NotifyAgent(BaseAgent):
    """
    Notify Agent for Guardian system
    Handles family notifications and communication
    """
    
    def __init__(self, a2a_client: A2AClient):
        agent_card = self._create_agent_card()
        super().__init__(
            agent_id="notify_agent",
            agent_card=agent_card,
            a2a_client=a2a_client
        )
        self.active_notifications: Dict[str, FamilyNotification] = {}
        self.family_contacts: Dict[str, List[str]] = {}  # passenger_id -> contact list
        
    def _create_agent_card(self) -> AgentCard:
        """Create Notify agent card defining capabilities"""
        return AgentCard(
            agent_id="notify_agent",
            name="Family Notification Agent",
            description="Handles family notifications and communication for elderly travelers",
            version="1.0.0",
            capabilities=[
                "sms_notifications",
                "email_notifications", 
                "push_notifications",
                "emergency_alerts",
                "multilingual_messages",
                "delivery_confirmation"
            ],
            endpoints={
                "send": "/notify/send",
                "emergency": "/notify/emergency",
                "confirm": "/notify/confirm"
            },
            health_check="/notify/health",
            supported_tasks=[
                "SendFamilyUpdate",
                "EmergencyAlert",
                "AppointmentReminder",
                "FlightUpdate",
                "ArrivalConfirmation",
                "DeliveryConfirmation"
            ]
        )
    
    async def handle_task(self, task: str, payload: Dict[str, Any]) -> TaskResult:
        """
        Handle incoming A2A tasks
        """
        logger.info(f"Notify Agent handling task: {task}")
        
        try:
            if task == "SendFamilyUpdate":
                return await self._send_family_update(payload)
            elif task == "EmergencyAlert":
                return await self._emergency_alert(payload)
            elif task == "AppointmentReminder":
                return await self._appointment_reminder(payload)
            elif task == "FlightUpdate":
                return await self._flight_update(payload)
            elif task == "ArrivalConfirmation":
                return await self._arrival_confirmation(payload)
            elif task == "DeliveryConfirmation":
                return await self._delivery_confirmation(payload)
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
    
    async def _send_family_update(self, payload: Dict[str, Any]) -> TaskResult:
        """Send status update to family"""
        passenger_id = payload.get("passenger_id")
        flight_number = payload.get("flight_number")
        status = payload.get("status", "good")
        family_contacts = payload.get("family_contacts", [])
        
        logger.info(f"Sending family update for passenger {passenger_id}, flight {flight_number}")
        
        # Store family contacts for this passenger
        if passenger_id:
            self.family_contacts[passenger_id] = family_contacts
        
        # Generate update message
        message = self._generate_status_message(flight_number, status)
        
        # Send to all family contacts
        notification_results = []
        
        for contact in family_contacts:
            notification_id = f"UPDATE_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            notification = FamilyNotification(
                notification_id=notification_id,
                notification_type=NotificationType.STATUS_UPDATE,
                channel=NotificationChannel.SMS,
                recipient=contact,
                message=message,
                sent_time=datetime.now(),
                status="sent"
            )
            
            self.active_notifications[notification_id] = notification
            notification_results.append(notification_id)
        
        # Simulate sending notifications
        await asyncio.sleep(0.8)
        
        # Mark as delivered
        for notification_id in notification_results:
            if notification_id in self.active_notifications:
                self.active_notifications[notification_id].delivery_confirmed = True
                self.active_notifications[notification_id].status = "delivered"
        
        return TaskResult(
            success=True,
            data={
                "notifications_sent": len(notification_results),
                "recipients": family_contacts,
                "message": message,
                "delivery_confirmed": True,
                "send_time": datetime.now().isoformat()
            }
        )
    
    async def _emergency_alert(self, payload: Dict[str, Any]) -> TaskResult:
        """Send emergency alert to family"""
        passenger_id = payload.get("passenger_id")
        emergency_type = payload.get("emergency_type", "medical")
        location = payload.get("location", "Unknown")
        severity = payload.get("severity", "high")
        
        logger.warning(f"Emergency alert: {emergency_type} for passenger {passenger_id}")
        
        # Get family contacts
        family_contacts = self.family_contacts.get(passenger_id, [])
        if not family_contacts:
            family_contacts = payload.get("emergency_contacts", [])
        
        # Generate emergency message
        message = self._generate_emergency_message(emergency_type, location, severity)
        
        # Send emergency notifications to all channels
        notification_results = []
        
        for contact in family_contacts:
            # SMS notification
            sms_id = f"EMERG_SMS_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            sms_notification = FamilyNotification(
                notification_id=sms_id,
                notification_type=NotificationType.EMERGENCY_ALERT,
                channel=NotificationChannel.SMS,
                recipient=contact,
                message=message,
                sent_time=datetime.now(),
                status="sent"
            )
            self.active_notifications[sms_id] = sms_notification
            notification_results.append(sms_id)
            
            # Push notification
            push_id = f"EMERG_PUSH_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            push_notification = FamilyNotification(
                notification_id=push_id,
                notification_type=NotificationType.EMERGENCY_ALERT,
                channel=NotificationChannel.PUSH,
                recipient=contact,
                message=message,
                sent_time=datetime.now(),
                status="sent"
            )
            self.active_notifications[push_id] = push_notification
            notification_results.append(push_id)
        
        # Simulate emergency notification sending
        await asyncio.sleep(0.5)
        
        # Mark as delivered
        for notification_id in notification_results:
            if notification_id in self.active_notifications:
                self.active_notifications[notification_id].delivery_confirmed = True
                self.active_notifications[notification_id].status = "delivered"
        
        return TaskResult(
            success=True,
            data={
                "emergency_notifications_sent": len(notification_results),
                "recipients": family_contacts,
                "emergency_type": emergency_type,
                "location": location,
                "severity": severity,
                "alert_time": datetime.now().isoformat()
            }
        )
    
    async def _appointment_reminder(self, payload: Dict[str, Any]) -> TaskResult:
        """Send appointment reminder to family"""
        passenger_id = payload.get("passenger_id")
        appointment_time = payload.get("appointment_time")
        hospital_name = payload.get("hospital_name", "Medical Center")
        family_contacts = self.family_contacts.get(passenger_id, [])
        
        logger.info(f"Appointment reminder for passenger {passenger_id}")
        
        # Generate reminder message
        message = f"Reminder: {passenger_id} has a medical appointment at {hospital_name} scheduled for {appointment_time}. Please ensure they have all necessary documents and medications."
        
        # Send reminder notifications
        notification_results = []
        
        for contact in family_contacts:
            notification_id = f"REMINDER_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            notification = FamilyNotification(
                notification_id=notification_id,
                notification_type=NotificationType.APPOINTMENT_REMINDER,
                channel=NotificationChannel.SMS,
                recipient=contact,
                message=message,
                sent_time=datetime.now(),
                status="sent"
            )
            
            self.active_notifications[notification_id] = notification
            notification_results.append(notification_id)
        
        # Simulate sending
        await asyncio.sleep(0.4)
        
        return TaskResult(
            success=True,
            data={
                "reminder_notifications_sent": len(notification_results),
                "appointment_time": appointment_time,
                "hospital_name": hospital_name,
                "send_time": datetime.now().isoformat()
            }
        )
    
    async def _flight_update(self, payload: Dict[str, Any]) -> TaskResult:
        """Send flight update to family"""
        passenger_id = payload.get("passenger_id")
        flight_number = payload.get("flight_number")
        update_type = payload.get("update_type", "status")
        new_eta = payload.get("new_eta")
        
        logger.info(f"Flight update for passenger {passenger_id}, flight {flight_number}")
        
        # Generate flight update message
        message = self._generate_flight_update_message(flight_number, update_type, new_eta)
        
        family_contacts = self.family_contacts.get(passenger_id, [])
        notification_results = []
        
        for contact in family_contacts:
            notification_id = f"FLIGHT_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            notification = FamilyNotification(
                notification_id=notification_id,
                notification_type=NotificationType.FLIGHT_UPDATE,
                channel=NotificationChannel.SMS,
                recipient=contact,
                message=message,
                sent_time=datetime.now(),
                status="sent"
            )
            
            self.active_notifications[notification_id] = notification
            notification_results.append(notification_id)
        
        # Simulate sending
        await asyncio.sleep(0.3)
        
        return TaskResult(
            success=True,
            data={
                "flight_update_sent": True,
                "flight_number": flight_number,
                "update_type": update_type,
                "recipients": family_contacts,
                "send_time": datetime.now().isoformat()
            }
        )
    
    async def _arrival_confirmation(self, payload: Dict[str, Any]) -> TaskResult:
        """Send arrival confirmation to family"""
        passenger_id = payload.get("passenger_id")
        flight_number = payload.get("flight_number")
        arrival_time = payload.get("arrival_time")
        
        logger.info(f"Arrival confirmation for passenger {passenger_id}")
        
        # Generate arrival message
        message = f"✅ Arrival Confirmed: {passenger_id} has safely arrived via flight {flight_number} at {arrival_time}. All hotel and hospital arrangements are confirmed."
        
        family_contacts = self.family_contacts.get(passenger_id, [])
        notification_results = []
        
        for contact in family_contacts:
            notification_id = f"ARRIVAL_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            notification = FamilyNotification(
                notification_id=notification_id,
                notification_type=NotificationType.ARRIVAL_CONFIRMATION,
                channel=NotificationChannel.SMS,
                recipient=contact,
                message=message,
                sent_time=datetime.now(),
                status="sent"
            )
            
            self.active_notifications[notification_id] = notification
            notification_results.append(notification_id)
        
        # Simulate sending
        await asyncio.sleep(0.4)
        
        return TaskResult(
            success=True,
            data={
                "arrival_confirmation_sent": True,
                "flight_number": flight_number,
                "arrival_time": arrival_time,
                "recipients": family_contacts,
                "send_time": datetime.now().isoformat()
            }
        )
    
    async def _delivery_confirmation(self, payload: Dict[str, Any]) -> TaskResult:
        """Confirm delivery of notification"""
        notification_id = payload.get("notification_id")
        delivery_status = payload.get("delivery_status", "delivered")
        
        logger.info(f"Delivery confirmation for notification {notification_id}: {delivery_status}")
        
        if notification_id in self.active_notifications:
            notification = self.active_notifications[notification_id]
            notification.delivery_confirmed = True
            notification.status = delivery_status
            
            return TaskResult(
                success=True,
                data={
                    "notification_id": notification_id,
                    "delivery_status": delivery_status,
                    "confirmation_time": datetime.now().isoformat()
                }
            )
        else:
            return TaskResult(
                success=False,
                error="Notification not found"
            )
    
    def _generate_status_message(self, flight_number: str, status: str) -> str:
        """Generate status update message"""
        if status == "good":
            return f"✅ Status Update: Flight {flight_number} is on schedule. All hotel and hospital arrangements are confirmed. Patient is doing well."
        elif status == "delayed":
            return f"⚠️ Flight Update: Flight {flight_number} has been delayed. We're monitoring the situation and will update hotel and hospital arrangements as needed."
        elif status == "arrived":
            return f"🎉 Arrival Update: Flight {flight_number} has arrived safely. Patient is being assisted with hotel check-in and hospital registration."
        else:
            return f"📱 Guardian Update: Flight {flight_number} status update. All arrangements remain on track."
    
    def _generate_emergency_message(self, emergency_type: str, location: str, severity: str) -> str:
        """Generate emergency alert message"""
        urgency = "🚨 URGENT" if severity == "high" else "⚠️ ALERT"
        
        return f"{urgency} MEDICAL EMERGENCY: {emergency_type} situation at {location}. Guardian system has been activated. Please contact emergency services and the patient immediately."
    
    def _generate_flight_update_message(self, flight_number: str, update_type: str, new_eta: str) -> str:
        """Generate flight update message"""
        if update_type == "delay":
            return f"⏰ Flight Update: Flight {flight_number} has been delayed. New estimated arrival time: {new_eta}. Guardian is updating all arrangements accordingly."
        elif update_type == "on_time":
            return f"✅ Flight Update: Flight {flight_number} is on schedule. ETA: {new_eta}. All arrangements remain confirmed."
        elif update_type == "early":
            return f"⚡ Flight Update: Flight {flight_number} is arriving early. New ETA: {new_eta}. Guardian is coordinating updated arrangements."
        else:
            return f"📱 Flight Update: Flight {flight_number} status update. Guardian continues to monitor and coordinate all arrangements."
    
    async def get_notification_status(self, notification_id: str) -> Dict[str, Any]:
        """Get notification delivery status"""
        if notification_id not in self.active_notifications:
            return {"error": "Notification not found"}
        
        notification = self.active_notifications[notification_id]
        return {
            "notification_id": notification_id,
            "type": notification.notification_type.value,
            "channel": notification.channel.value,
            "recipient": notification.recipient,
            "status": notification.status,
            "delivery_confirmed": notification.delivery_confirmed,
            "sent_time": notification.sent_time.isoformat()
        }

# Global Notify agent instance (will be initialized with A2A client)
notify_agent = None
