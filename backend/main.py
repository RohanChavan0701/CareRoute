#!/usr/bin/env python3
"""
Guardian A2A Orchestrator - FastAPI Backend with AG-UI Protocol
Provides REST API endpoints for Flutter frontend communication
"""

import asyncio
import logging
import json
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
import uvicorn

# Import our orchestrator
from orchestrator import guardian_orchestrator

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# AG-UI Event Types for Guardian Orchestrator
class AGUIEventType:
    """AG-UI compatible event types for Guardian Orchestrator"""
    # Core events
    AGENT_START = "agent_start"
    AGENT_END = "agent_end"
    AGENT_ERROR = "agent_error"
    
    # Orchestration events
    ORCHESTRATION_STARTED = "orchestration_started"
    ORCHESTRATION_COMPLETED = "orchestration_completed"
    ORCHESTRATION_FAILED = "orchestration_failed"
    
    # Flight events
    FLIGHT_STATUS_UPDATE = "flight_status_update"
    FLIGHT_DELAY_NOTIFICATION = "flight_delay_notification"
    
    # Agent coordination events
    HOTEL_CONFIRMED = "hotel_confirmed"
    HOSPITAL_CONFIRMED = "hospital_confirmed"
    NOTIFICATION_SENT = "notification_sent"
    VOICE_CALL_INITIATED = "voice_call_initiated"
    ACCESSIBILITY_ARRANGED = "accessibility_arranged"
    
    # Knowledge base events
    KNOWLEDGE_QUERY_RESPONSE = "knowledge_query_response"
    CONTEXT_UPDATED = "context_updated"
    
    # Call events
    INCOMING_CALL = "incoming_call"
    CALL_CONTEXT_SHARED = "call_context_shared"
    SCHEDULE_AMENDMENT = "schedule_amendment"

# Pydantic models for API requests/responses
class BookingRequest(BaseModel):
    """Request model for patient booking orchestration"""
    patient_id: str = Field(..., description="Unique patient identifier")
    patient_name: str = Field(..., description="Patient's full name")
    patient_email: str = Field(..., description="Patient's email address")
    flight_number: str = Field(..., description="Flight number")
    flight_date: str = Field(..., description="Flight date (YYYY-MM-DD)")
    departure_airport: str = Field(..., description="Departure airport code")
    arrival_airport: str = Field(..., description="Arrival airport code")
    hotel_booking_reference: str = Field(..., description="Hotel booking reference")
    hospital_booking_reference: str = Field(..., description="Hospital booking reference")
    special_requirements: str = Field(default="", description="Special requirements")
    medical_conditions: List[str] = Field(default=[], description="Medical conditions")
    age: int = Field(..., description="Patient age")
    emergency_contacts: List[Dict[str, str]] = Field(default=[], description="Emergency contacts")
    flight_time: Optional[str] = Field(default="09:00", description="Flight departure time")

class KnowledgeQueryRequest(BaseModel):
    """Request model for knowledge base queries"""
    patient_id: str = Field(..., description="Patient identifier")
    question: str = Field(..., description="Question to ask")
    context: Optional[Dict[str, Any]] = Field(default=None, description="Additional context")

class CallRequest(BaseModel):
    """Request model for incoming calls"""
    patient_id: str = Field(..., description="Patient identifier")
    call_type: str = Field(default="general_inquiry", description="Type of call")
    call_data: Optional[Dict[str, Any]] = Field(default=None, description="Call metadata")

class ScheduleAmendmentRequest(BaseModel):
    """Request model for schedule amendments"""
    patient_id: str = Field(..., description="Patient identifier")
    amendment_type: str = Field(..., description="Type of amendment")
    amendment_data: Dict[str, Any] = Field(..., description="Amendment details")

class AGUIEvent(BaseModel):
    """AG-UI compatible event model"""
    type: str = Field(..., description="Event type")
    timestamp: str = Field(..., description="Event timestamp")
    data: Dict[str, Any] = Field(..., description="Event data")
    patient_id: Optional[str] = Field(default=None, description="Patient identifier")
    orchestration_id: Optional[str] = Field(default=None, description="Orchestration identifier")

# Global event storage for real-time updates
active_events: Dict[str, List[AGUIEvent]] = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    logger.info("🚀 Guardian A2A Orchestrator Backend starting up...")
    
    # Initialize orchestrator
    await guardian_orchestrator.initialize()
    logger.info("✅ Guardian Orchestrator initialized")
    
    yield
    
    logger.info("🛑 Guardian A2A Orchestrator Backend shutting down...")

# Create FastAPI app
app = FastAPI(
    title="Guardian A2A Orchestrator API",
    description="Backend API for Guardian Medical Tourism Orchestrator with AG-UI protocol support",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware for Flutter frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def emit_agui_event(event_type: str, data: Dict[str, Any], patient_id: str = None, orchestration_id: str = None):
    """Emit an AG-UI compatible event"""
    event = AGUIEvent(
        type=event_type,
        timestamp=datetime.now().isoformat(),
        data=data,
        patient_id=patient_id,
        orchestration_id=orchestration_id
    )
    
    # Store event for real-time access
    if patient_id:
        if patient_id not in active_events:
            active_events[patient_id] = []
        active_events[patient_id].append(event)
        
        # Keep only last 50 events per patient
        if len(active_events[patient_id]) > 50:
            active_events[patient_id] = active_events[patient_id][-50:]
    
    logger.info(f"📡 AG-UI Event emitted: {event_type} for {patient_id or 'system'}")

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "Guardian A2A Orchestrator",
        "version": "1.0.0"
    }

# AG-UI Protocol endpoints
@app.get("/ag-ui/events/{patient_id}")
async def get_agui_events(patient_id: str, limit: int = 20):
    """Get AG-UI events for a patient (for real-time updates)"""
    events = active_events.get(patient_id, [])
    return {
        "events": events[-limit:] if events else [],
        "count": len(events),
        "patient_id": patient_id
    }

@app.get("/ag-ui/events")
async def get_all_agui_events(limit: int = 50):
    """Get all recent AG-UI events"""
    all_events = []
    for patient_id, events in active_events.items():
        all_events.extend(events[-10:])  # Last 10 events per patient
    
    # Sort by timestamp and return most recent
    all_events.sort(key=lambda x: x.timestamp, reverse=True)
    return {
        "events": all_events[:limit],
        "count": len(all_events)
    }

# Main orchestration endpoint
@app.post("/orchestrate/booking")
async def orchestrate_booking(request: BookingRequest, background_tasks: BackgroundTasks):
    """Start patient booking orchestration"""
    try:
        logger.info(f"🎯 Starting orchestration for patient {request.patient_id}")
        
        # Emit orchestration start event
        emit_agui_event(
            AGUIEventType.ORCHESTRATION_STARTED,
            {
                "patient_name": request.patient_name,
                "flight_number": request.flight_number,
                "flight_date": request.flight_date,
                "route": f"{request.departure_airport} → {request.arrival_airport}"
            },
            patient_id=request.patient_id
        )
        
        # Convert request to booking data
        booking_data = request.dict()
        
        # Start orchestration in background
        background_tasks.add_task(run_orchestration, booking_data)
        
        return {
            "status": "success",
            "message": "Orchestration started successfully",
            "patient_id": request.patient_id,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to start orchestration: {e}")
        emit_agui_event(
            AGUIEventType.ORCHESTRATION_FAILED,
            {"error": str(e)},
            patient_id=request.patient_id
        )
        raise HTTPException(status_code=500, detail=str(e))

async def run_orchestration(booking_data: Dict[str, Any]):
    """Run the orchestration workflow"""
    orchestration_id = None
    try:
        # Start orchestration
        orchestration_id = await guardian_orchestrator.start_orchestration(booking_data)
        
        # Emit completion event
        emit_agui_event(
            AGUIEventType.ORCHESTRATION_COMPLETED,
            {
                "orchestration_id": orchestration_id,
                "status": "completed",
                "tasks_completed": len(guardian_orchestrator.active_orchestrations.get(orchestration_id, {}).get("tasks", {}))
            },
            patient_id=booking_data["patient_id"],
            orchestration_id=orchestration_id
        )
        
    except Exception as e:
        logger.error(f"❌ Orchestration failed: {e}")
        emit_agui_event(
            AGUIEventType.ORCHESTRATION_FAILED,
            {
                "error": str(e),
                "orchestration_id": orchestration_id
            },
            patient_id=booking_data["patient_id"],
            orchestration_id=orchestration_id
        )

# Knowledge base endpoint
@app.post("/knowledge/query")
async def query_knowledge(request: KnowledgeQueryRequest):
    """Query the knowledge base"""
    try:
        logger.info(f"🧠 Knowledge query from {request.patient_id}: {request.question}")
        
        result = await guardian_orchestrator.handle_knowledge_query(
            request.patient_id,
            request.question,
            request.context or {}
        )
        
        # Emit knowledge response event
        emit_agui_event(
            AGUIEventType.KNOWLEDGE_QUERY_RESPONSE,
            {
                "question": request.question,
                "response": result.get("response", ""),
                "confidence": result.get("confidence", 0.8)
            },
            patient_id=request.patient_id
        )
        
        return result
        
    except Exception as e:
        logger.error(f"❌ Knowledge query failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Incoming call endpoint
@app.post("/calls/incoming")
async def handle_incoming_call(request: CallRequest):
    """Handle incoming call from patient"""
    try:
        logger.info(f"📞 Incoming call from {request.patient_id}")
        
        # Emit incoming call event
        emit_agui_event(
            AGUIEventType.INCOMING_CALL,
            {
                "call_type": request.call_type,
                "call_data": request.call_data or {}
            },
            patient_id=request.patient_id
        )
        
        result = await guardian_orchestrator.handle_incoming_call(
            request.patient_id,
            request.call_data or {}
        )
        
        # Emit call context shared event
        emit_agui_event(
            AGUIEventType.CALL_CONTEXT_SHARED,
            {
                "call_context_id": result.get("call_context_id"),
                "voice_agent_ready": result.get("voice_agent_ready", False)
            },
            patient_id=request.patient_id
        )
        
        return result
        
    except Exception as e:
        logger.error(f"❌ Failed to handle incoming call: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Schedule amendment endpoint
@app.post("/schedule/amend")
async def handle_schedule_amendment(request: ScheduleAmendmentRequest):
    """Handle schedule amendments from Voice Agent"""
    try:
        logger.info(f"📝 Schedule amendment for {request.patient_id}: {request.amendment_type}")
        
        result = await guardian_orchestrator.handle_schedule_amendment(
            request.patient_id,
            request.amendment_data
        )
        
        # Emit schedule amendment event
        emit_agui_event(
            AGUIEventType.SCHEDULE_AMENDMENT,
            {
                "amendment_type": request.amendment_type,
                "amendment_data": request.amendment_data,
                "status": result.get("status")
            },
            patient_id=request.patient_id
        )
        
        return result
        
    except Exception as e:
        logger.error(f"❌ Failed to handle schedule amendment: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Additional info request endpoint
@app.post("/additional-info/{patient_id}")
async def handle_additional_info_request(patient_id: str, request_type: str, request_data: Dict[str, Any] = None):
    """Handle additional info requests from Voice Agent"""
    try:
        logger.info(f"ℹ️ Additional info request for {patient_id}: {request_type}")
        
        result = await guardian_orchestrator.handle_additional_info_request(
            patient_id,
            request_type,
            request_data or {}
        )
        
        return result
        
    except Exception as e:
        logger.error(f"❌ Failed to handle additional info request: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Orchestration status endpoint
@app.get("/orchestration/{orchestration_id}/status")
async def get_orchestration_status(orchestration_id: str):
    """Get orchestration status"""
    try:
        orchestration = guardian_orchestrator.active_orchestrations.get(orchestration_id)
        
        if not orchestration:
            raise HTTPException(status_code=404, detail="Orchestration not found")
        
        return {
            "orchestration_id": orchestration_id,
            "status": orchestration["status"],
            "patient_id": orchestration["patient_id"],
            "created_at": orchestration["created_at"],
            "tasks": orchestration.get("tasks", {}),
            "flight_data": orchestration.get("flight_data", {}),
            "coordination_results": orchestration.get("coordination_results", {})
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to get orchestration status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Patient context endpoint
@app.get("/patient/{patient_id}/context")
async def get_patient_context(patient_id: str):
    """Get complete patient context"""
    try:
        context = await guardian_orchestrator._get_complete_patient_context(patient_id)
        return context
        
    except Exception as e:
        logger.error(f"❌ Failed to get patient context: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Real-time events stream endpoint (Server-Sent Events)
@app.get("/stream/events/{patient_id}")
async def stream_events(patient_id: str):
    """Stream AG-UI events for a patient using Server-Sent Events"""
    async def event_generator():
        last_count = 0
        
        while True:
            events = active_events.get(patient_id, [])
            
            # Send new events
            if len(events) > last_count:
                new_events = events[last_count:]
                for event in new_events:
                    yield f"data: {event.json()}\n\n"
                last_count = len(events)
            
            # Wait before next check
            await asyncio.sleep(1)
    
    return StreamingResponse(
        event_generator(),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "*",
        }
    )

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
