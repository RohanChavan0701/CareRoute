#!/usr/bin/env python3
"""
Guardian A2A Orchestrator - Simplified AG-UI Protocol Backend
Uses standard AG-UI protocol for basic functionality
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
from .scheduler import guardian_scheduler

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
    title="Guardian Orchestrator - Simplified AG-UI Backend",
    description="Simplified version for testing core functionality",
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
    logger.info("🚀 Guardian A2A Orchestrator Simplified Backend starting up...")
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
    return {"message": "Guardian A2A Orchestrator - Simplified Backend", "status": "running"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "protocol": "AG-UI-Simplified",
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
                "initiate_call_with_context",
                {
                    "user_id": user_id,
                    "context": patient_context,
                    "call_reason": "user_requested_support"
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
            "initiate_call_with_context",
            {
                "user_id": request.user_id,
                "context": patient_context,
                "call_reason": "user_requested_support"
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

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
