#!/usr/bin/env python3
"""
Guardian Medical Tourism Orchestrator - Main Backend
Simple REST API for Flutter app integration with real-time updates
"""

import asyncio
import logging
import json
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional, AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
import uvicorn

# Import our orchestrator and scheduler
from .orchestrator import guardian_orchestrator
from .database.orchestrator_service import orchestrator_db_service
from .scheduler import guardian_scheduler
from .fcm_service import fcm_service

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Simple request/response models for testing
class SimpleMessage(BaseModel):
    """Simple message model for testing"""
    content: str = Field(..., description="Message content")
    user_id: str = Field(..., description="User identifier")
    session_id: Optional[str] = Field(default=None, description="Session identifier")

class SimpleResponse(BaseModel):
    """Simple response model for testing"""
    content: str = Field(..., description="Response content")
    user_id: str = Field(..., description="User identifier")
    session_id: Optional[str] = Field(default=None, description="Session identifier")

# Create FastAPI app
app = FastAPI(
    title="Guardian Medical Tourism Orchestrator",
    description="Backend API for medical tourism trip orchestration with real-time updates",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    """Startup event handler"""
    logger.info("🚀 Guardian Medical Tourism Orchestrator starting up...")
    
    # Initialize database service
    try:
        # Test database connection
        if orchestrator_db_service.db_manager.test_connection():
            logger.info("✅ Database connection successful")
            logger.info("✅ Backend initialized with HIPAA database")
        else:
            logger.warning("⚠️ Database connection failed - falling back to dummy data")
            logger.info("✅ Backend initialized without database")
    except Exception as e:
        logger.warning(f"⚠️ Database initialization failed: {e} - falling back to dummy data")
        logger.info("✅ Backend initialized without database")
    
    logger.info("✅ Guardian Orchestrator ready")
    
    # Start scheduler
    try:
        await guardian_scheduler.start()
        logger.info("✅ Guardian Scheduler started")
    except Exception as e:
        logger.error(f"❌ Failed to start scheduler: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown event handler"""
    logger.info("🛑 Shutting down Guardian Orchestrator...")
    try:
        await guardian_scheduler.stop()
        logger.info("✅ Guardian Scheduler stopped")
    except Exception as e:
        logger.error(f"❌ Failed to stop scheduler: {e}")

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Guardian Medical Tourism Orchestrator", "status": "running"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "protocol": "REST-API",
        "version": "1.0.0",
        "agent_id": "guardian_orchestrator",
        "timestamp": datetime.now().isoformat(),
        "capabilities": [
            "orchestration",
            "real_time_events",
            "voice_interaction",
            "schedule_management"
        ]
    }

@app.post("/message")
async def handle_message(message: SimpleMessage):
    """Handle user message - simplified version"""
    try:
        user_id = message.user_id
        session_id = message.session_id or f"session_{uuid.uuid4().hex[:8]}"
        
        # Process message based on content
        if "start orchestration" in message.content.lower() or "book" in message.content.lower():
            return SimpleResponse(
                content="I've started your travel orchestration! I'll coordinate with all the agents to ensure everything is ready for your medical tourism trip.",
                user_id=user_id,
                session_id=session_id
            )
        
        elif "flight status" in message.content.lower() or "flight" in message.content.lower():
            # Handle flight status query - get trip status
            trip_status = await guardian_orchestrator.get_user_trip_status(user_id)
            flight_info = trip_status.get("data", {}).get("flight_status", {})
            
            if flight_info:
                return SimpleResponse(
                    content=f"Your flight {flight_info.get('flight_number', 'N/A')} is {flight_info.get('status', 'unknown')}. Estimated arrival: {flight_info.get('estimated_arrival_local', 'N/A')}",
                    user_id=user_id,
                    session_id=session_id
                )
            else:
                return SimpleResponse(
                    content="I don't have any active flight information for you. Please start an orchestration first.",
                    user_id=user_id,
                    session_id=session_id
                )
        
        elif "help" in message.content.lower() or "what can you do" in message.content.lower():
            return SimpleResponse(
                content="I'm Guardian, your medical tourism orchestrator. I can help you with:\n\n• Start travel orchestration\n• Check flight status\n• Coordinate with hotels, hospitals, and accessibility services\n• Handle schedule changes\n\nFor detailed questions, please use the voice call button to speak directly with our support team.",
                user_id=user_id,
                session_id=session_id
            )
        
        elif "call" in message.content.lower() or "voice" in message.content.lower() or "speak" in message.content.lower():
            # Get comprehensive patient context
            patient_context = await guardian_orchestrator._get_comprehensive_call_context(user_id)
            
            # Send context to voice agent
            voice_result = await guardian_orchestrator._send_a2a_task(
                "voice_agent", 
                "configure_patient_call",
                {
                    "params": patient_context["params"]  # Extract just the params from the JSON-RPC structure
                }
            )
            
            return SimpleResponse(
                content="I'm connecting you to our voice support team with your complete travel information. They'll be able to help you with any questions about your medical tourism trip.",
                user_id=user_id,
                session_id=session_id
            )
        
        else:
            # Default response - suggest voice call for complex queries
            return SimpleResponse(
                content="I understand you have a question about your medical tourism trip. For detailed assistance, please use the voice call button to speak directly with our support team who will have access to all your travel information.",
                user_id=user_id,
                session_id=session_id
            )
        
    except Exception as e:
        logger.error(f"❌ Failed to handle user message: {e}")
        return SimpleResponse(
            content=f"I'm sorry, I encountered an error: {str(e)}",
            user_id=message.user_id,
            session_id=message.session_id
        )

@app.post("/guardian/voice/call")
async def trigger_voice_call(request: SimpleMessage):
    """Trigger voice call with complete patient context"""
    try:
        # Get comprehensive patient context
        patient_context = await guardian_orchestrator._get_comprehensive_call_context(request.user_id)
        
        # Send context to voice agent
        voice_result = await guardian_orchestrator._send_a2a_task(
            "voice_agent", 
            "configure_patient_call",
            {
                "params": patient_context["params"]  # Extract just the params from the JSON-RPC structure
            }
        )
        
        return {
            "status": "success",
            "data": {
                "message": "Voice call initiated with complete patient context",
                "context_sent": True,
                "voice_agent_response": voice_result
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to trigger voice call: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/guardian/scheduler/status")
async def get_scheduler_status():
    """Get scheduler status and job information"""
    try:
        status = await guardian_scheduler.get_scheduler_status()
        
        return {
            "status": "success",
            "data": status,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to get scheduler status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/guardian/trip/status/{user_id}")
async def get_trip_status(user_id: str):
    """Get comprehensive trip status for user"""
    try:
        result = await guardian_orchestrator.get_user_trip_status(user_id)
        
        return {
            "status": "success",
            "data": result,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to get trip status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/fcm/register")
async def register_fcm_token(request: dict):
    """Register FCM device token for push notifications"""
    try:
        user_id = request.get("user_id")
        device_token = request.get("device_token")
        
        if not user_id or not device_token:
            raise HTTPException(status_code=400, detail="user_id and device_token are required")
        
        fcm_service.register_device_token(user_id, device_token)
        
        return {
            "status": "success",
            "message": "FCM token registered successfully",
            "user_id": user_id
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to register FCM token: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/fcm/send-boarding-reminder")
async def send_boarding_reminder(request: dict):
    """Send boarding reminder notification"""
    try:
        user_id = request.get("user_id")
        flight_info = request.get("flight_info", {})
        
        if not user_id:
            raise HTTPException(status_code=400, detail="user_id is required")
        
        await guardian_orchestrator.send_boarding_reminder(user_id, flight_info)
        
        return {
            "status": "success",
            "message": "Boarding reminder sent",
            "user_id": user_id
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to send boarding reminder: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/fcm/send-flight-update")
async def send_flight_update(request: dict):
    """Send flight status update notification"""
    try:
        user_id = request.get("user_id")
        flight_info = request.get("flight_info", {})
        
        if not user_id:
            raise HTTPException(status_code=400, detail="user_id is required")
        
        await guardian_orchestrator.send_flight_status_update(user_id, flight_info)
        
        return {
            "status": "success",
            "message": "Flight status update sent",
            "user_id": user_id
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to send flight update: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/fcm/send-cab-notification")
async def send_cab_notification(request: dict):
    """Send cab arrival notification"""
    try:
        user_id = request.get("user_id")
        cab_info = request.get("cab_info", {})
        
        if not user_id:
            raise HTTPException(status_code=400, detail="user_id is required")
        
        await guardian_orchestrator.send_arrival_cab_notification(user_id, cab_info)
        
        return {
            "status": "success",
            "message": "Cab notification sent",
            "user_id": user_id
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to send cab notification: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/fcm/send-appointment-reminder")
async def send_appointment_reminder(request: dict):
    """Send hospital appointment reminder"""
    try:
        user_id = request.get("user_id")
        appointment_info = request.get("appointment_info", {})
        
        if not user_id:
            raise HTTPException(status_code=400, detail="user_id is required")
        
        await guardian_orchestrator.send_hospital_appointment_reminder(user_id, appointment_info)
        
        return {
            "status": "success",
            "message": "Appointment reminder sent",
            "user_id": user_id
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to send appointment reminder: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/booking")
async def create_booking(booking_data: dict):
    """Create a new booking and start orchestration"""
    try:
        user_id = booking_data.get("user_id")
        if not user_id:
            raise HTTPException(status_code=400, detail="user_id is required")
        
        # Start orchestration with booking data
        orchestration_id = await guardian_orchestrator.start_orchestration(booking_data)
        
        # Handle booking creation (send notifications, etc.)
        result = await guardian_orchestrator.handle_booking_creation(user_id, booking_data)
        
        return {
            "status": "success",
            "message": "Booking created and orchestration started",
            "orchestration_id": orchestration_id,
            "booking_id": booking_data.get("booking_id"),
            "user_id": user_id,
            "result": result
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to create booking: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
