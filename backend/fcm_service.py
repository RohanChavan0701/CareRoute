#!/usr/bin/env python3
"""
Firebase Cloud Messaging (FCM) Service for Real-time Updates
Handles sending push notifications to Flutter app for trip updates
"""

import json
import logging
from typing import Dict, List, Optional, Any
import httpx
import asyncio
from datetime import datetime

logger = logging.getLogger(__name__)

class FCMService:
    def __init__(self):
        # FCM Server Key (you'll need to get this from Firebase Console)
        self.fcm_server_key = "YOUR_FCM_SERVER_KEY_HERE"
        self.fcm_url = "https://fcm.googleapis.com/fcm/send"
        
        # Device tokens storage (in production, this would be in database)
        self.device_tokens = {}
        
    def register_device_token(self, user_id: str, device_token: str):
        """Register a device token for a user"""
        self.device_tokens[user_id] = device_token
        logger.info(f"📱 Registered FCM token for user {user_id}")
    
    async def send_notification(
        self, 
        user_id: str, 
        title: str, 
        body: str, 
        data: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Send push notification to user's device"""
        try:
            device_token = self.device_tokens.get(user_id)
            if not device_token:
                logger.warning(f"⚠️ No FCM token found for user {user_id}")
                return False
            
            payload = {
                "to": device_token,
                "notification": {
                    "title": title,
                    "body": body,
                    "sound": "default",
                    "badge": 1
                },
                "data": data or {}
            }
            
            headers = {
                "Authorization": f"key={self.fcm_server_key}",
                "Content-Type": "application/json"
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.fcm_url,
                    json=payload,
                    headers=headers,
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    logger.info(f"✅ FCM notification sent to user {user_id}: {title}")
                    return True
                else:
                    logger.error(f"❌ FCM notification failed: {response.status_code} - {response.text}")
                    return False
                    
        except Exception as e:
            logger.error(f"❌ FCM notification error for user {user_id}: {e}")
            return False
    
    async def send_boarding_reminder(self, user_id: str, flight_info: Dict[str, Any]):
        """Send boarding reminder notification"""
        flight_number = flight_info.get("flight_number", "Your flight")
        boarding_time = flight_info.get("boarding_time", "soon")
        
        title = "✈️ Boarding Reminder"
        body = f"Boarding for {flight_number} starts in {boarding_time}"
        
        data = {
            "type": "boarding_reminder",
            "flight_number": flight_number,
            "boarding_time": boarding_time,
            "timestamp": datetime.now().isoformat()
        }
        
        return await self.send_notification(user_id, title, body, data)
    
    async def send_flight_status_update(self, user_id: str, flight_info: Dict[str, Any]):
        """Send flight status update notification"""
        flight_number = flight_info.get("flight_number", "Your flight")
        status = flight_info.get("status", "updated")
        gate = flight_info.get("gate", "")
        
        title = "✈️ Flight Status Update"
        body = f"{flight_number} is now {status}"
        if gate:
            body += f" - Gate {gate}"
        
        data = {
            "type": "flight_status_update",
            "flight_number": flight_number,
            "status": status,
            "gate": gate,
            "timestamp": datetime.now().isoformat()
        }
        
        return await self.send_notification(user_id, title, body, data)
    
    async def send_cab_request_notification(self, user_id: str, cab_info: Dict[str, Any]):
        """Send cab request notification (30 minutes before arrival)"""
        driver_name = cab_info.get("driver_name", "Our driver")
        vehicle = cab_info.get("vehicle", "vehicle")
        eta = cab_info.get("eta", "soon")
        
        title = "🚗 Cab Arranged"
        body = f"{driver_name} will pick you up in {eta}"
        
        data = {
            "type": "cab_requested",
            "driver_name": driver_name,
            "vehicle": vehicle,
            "eta": eta,
            "timestamp": datetime.now().isoformat()
        }
        
        return await self.send_notification(user_id, title, body, data)
    
    async def send_hospital_appointment_reminder(self, user_id: str, appointment_info: Dict[str, Any]):
        """Send hospital appointment reminder"""
        doctor_name = appointment_info.get("doctor_name", "Your doctor")
        hospital_name = appointment_info.get("hospital_name", "the hospital")
        appointment_time = appointment_info.get("appointment_time", "")
        
        title = "🏥 Appointment Reminder"
        body = f"Appointment with {doctor_name} at {hospital_name}"
        if appointment_time:
            body += f" at {appointment_time}"
        
        data = {
            "type": "hospital_appointment",
            "doctor_name": doctor_name,
            "hospital_name": hospital_name,
            "appointment_time": appointment_time,
            "timestamp": datetime.now().isoformat()
        }
        
        return await self.send_notification(user_id, title, body, data)
    
    async def send_general_trip_update(self, user_id: str, update_type: str, message: str, details: Optional[Dict] = None):
        """Send general trip update notification"""
        title = "🔄 Trip Update"
        body = message
        
        data = {
            "type": update_type,
            "message": message,
            "details": details or {},
            "timestamp": datetime.now().isoformat()
        }
        
        return await self.send_notification(user_id, title, body, data)

# Global FCM service instance
fcm_service = FCMService()
