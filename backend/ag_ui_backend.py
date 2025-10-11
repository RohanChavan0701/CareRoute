#!/usr/bin/env python3
"""
Guardian A2A Orchestrator - AG-UI Protocol Compatible Backend
Implements AG-UI standard events and communication patterns
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
# Removed booking integration - handled by frontend

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# AG-UI Standard Event Types (based on AG-UI protocol)
class AGUIStandardEvents:
    """AG-UI standard event types for agent-user interaction"""
    
    # Core Agent Events
    AGENT_START = "agent_start"
    AGENT_END = "agent_end"
    AGENT_ERROR = "agent_error"
    AGENT_THINKING = "agent_thinking"
    
    # User Interaction Events
    USER_MESSAGE = "user_message"
    AGENT_MESSAGE = "agent_message"
    USER_ACTION = "user_action"
    AGENT_ACTION = "agent_action"
    
    # State Management Events
    STATE_UPDATE = "state_update"
    CONTEXT_UPDATE = "context_update"
    
    # Tool and Function Events
    TOOL_CALL = "tool_call"
    TOOL_RESULT = "tool_result"
    FUNCTION_CALL = "function_call"
    FUNCTION_RESULT = "function_result"
    
    # UI Events
    UI_UPDATE = "ui_update"
    UI_COMPONENT_UPDATE = "ui_component_update"
    UI_STREAMING_UPDATE = "ui_streaming_update"
    
    # Custom Guardian Events (extending AG-UI)
    ORCHESTRATION_STARTED = "orchestration_started"
    ORCHESTRATION_COMPLETED = "orchestration_completed"
    FLIGHT_STATUS_UPDATE = "flight_status_update"
    HOTEL_CONFIRMED = "hotel_confirmed"
    HOSPITAL_CONFIRMED = "hospital_confirmed"
    NOTIFICATION_SENT = "notification_sent"
    VOICE_CALL_INITIATED = "voice_call_initiated"
    ACCESSIBILITY_ARRANGED = "accessibility_arranged"
    KNOWLEDGE_QUERY_RESPONSE = "knowledge_query_response"
    INCOMING_CALL = "incoming_call"
    CALL_CONTEXT_SHARED = "call_context_shared"
    SCHEDULE_AMENDMENT = "schedule_amendment"

# AG-UI Compatible Models
class AGUIEvent(BaseModel):
    """AG-UI standard event model"""
    type: str = Field(..., description="Event type following AG-UI standards")
    timestamp: str = Field(..., description="ISO timestamp")
    data: Dict[str, Any] = Field(..., description="Event payload data")
    user_id: Optional[str] = Field(default=None, description="User identifier")
    session_id: Optional[str] = Field(default=None, description="Session identifier")
    agent_id: Optional[str] = Field(default="guardian_orchestrator", description="Agent identifier")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata")

class AGUIUserMessage(BaseModel):
    """AG-UI user message model"""
    message: str = Field(..., description="User message content")
    user_id: str = Field(..., description="User identifier")
    session_id: Optional[str] = Field(default=None, description="Session identifier")
    context: Optional[Dict[str, Any]] = Field(default=None, description="Message context")
    message_type: str = Field(default="text", description="Message type (text, voice, etc.)")

class AGUIAgentMessage(BaseModel):
    """AG-UI agent message model"""
    message: str = Field(..., description="Agent response message")
    user_id: str = Field(..., description="User identifier")
    session_id: Optional[str] = Field(default=None, description="Session identifier")
    message_type: str = Field(default="text", description="Message type")
    streaming: bool = Field(default=False, description="Whether message is streaming")
    components: Optional[List[Dict[str, Any]]] = Field(default=None, description="UI components")

class GuardianBookingRequest(BaseModel):
    """Guardian-specific booking request model"""
    user_id: str = Field(..., description="User identifier")
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
    session_id: Optional[str] = Field(default=None, description="Session identifier")

class UserRequest(BaseModel):
    """Simple user request model"""
    user_id: str

class BookingCreateRequest(BaseModel):
    """Booking creation request model"""
    user_id: str
    patient_name: str
    flight_number: str
    flight_date: str
    flight_time: str
    departure_airport: str
    arrival_airport: str
    hotel_booking_reference: str
    hospital_appointment_id: str
    hospital_appointment_time: str
    email: str
    emergency_contacts: List[str] = []
    special_requirements: str = ""
    medical_conditions: List[str] = []
    hotel_check_in: str = ""

class LocationUpdateRequest(BaseModel):
    """Location update request model"""
    user_id: str
    latitude: float
    longitude: float
    airport_name: str = ""
    airport_code: str = ""
    timestamp: str = ""

class CabArrivalRequest(BaseModel):
    """Cab arrival notification request model"""
    user_id: str
    gate: str
    pickup_location: str
    estimated_arrival: str = "15 minutes"
    cab_details: Dict[str, Any] = {}

class StayExtensionRequest(BaseModel):
    """Stay extension request model"""
    user_id: str
    new_discharge_date: str
    reason: str = "Medical treatment extended"
    extension_days: int = 3
    notify_family: bool = True

# Global event storage and session management
active_sessions: Dict[str, Dict[str, Any]] = {}
active_events: Dict[str, List[AGUIEvent]] = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    logger.info("🚀 Guardian A2A Orchestrator AG-UI Backend starting up...")
    
    # Database initialization removed - booking handled by frontend
    logger.info("✅ Backend initialized without database")
    
    # Orchestrator is already initialized when imported
    logger.info("✅ Guardian Orchestrator ready")
    
    # Start the scheduler
    await guardian_scheduler.start()
    logger.info("✅ Guardian Scheduler started")
    
    yield
    
    logger.info("🛑 Guardian A2A Orchestrator AG-UI Backend shutting down...")
    
    # Stop the scheduler
    await guardian_scheduler.stop()
    logger.info("✅ Guardian Scheduler stopped")

# Create FastAPI app
app = FastAPI(
    title="Guardian A2A Orchestrator - AG-UI Backend",
    description="AG-UI protocol compatible backend for Guardian Medical Tourism Orchestrator",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware for AG-UI frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
# Booking router removed - handled by frontend

def emit_agui_event(
    event_type: str, 
    data: Dict[str, Any], 
    user_id: str = None, 
    session_id: str = None,
    agent_id: str = "guardian_orchestrator",
    metadata: Dict[str, Any] = None
) -> AGUIEvent:
    """Emit an AG-UI compatible event"""
    event = AGUIEvent(
        type=event_type,
        timestamp=datetime.now().isoformat(),
        data=data,
        user_id=user_id,
        session_id=session_id,
        agent_id=agent_id,
        metadata=metadata or {}
    )
    
    # Store event for real-time access
    if user_id:
        if user_id not in active_events:
            active_events[user_id] = []
        active_events[user_id].append(event)
        
        # Keep only last 100 events per user
        if len(active_events[user_id]) > 100:
            active_events[user_id] = active_events[user_id][-100:]
    
    # Also store by session if provided
    if session_id:
        if session_id not in active_events:
            active_events[session_id] = []
        active_events[session_id].append(event)
        
        if len(active_events[session_id]) > 100:
            active_events[session_id] = active_events[session_id][-100:]
    
    logger.info(f"📡 AG-UI Event emitted: {event_type} for user {user_id} session {session_id}")
    return event

# AG-UI Standard Endpoints
@app.get("/ag-ui/health")
async def agui_health_check():
    """AG-UI health check endpoint"""
    return {
        "status": "healthy",
        "protocol": "AG-UI",
        "version": "1.0.0",
        "agent_id": "guardian_orchestrator",
        "timestamp": datetime.now().isoformat(),
        "capabilities": [
            "orchestration",
            "knowledge_query",
            "real_time_events",
            "voice_interaction",
            "schedule_management"
        ]
    }

@app.post("/ag-ui/message")
async def handle_user_message(message: AGUIUserMessage, background_tasks: BackgroundTasks):
    """Handle user message following AG-UI protocol"""
    try:
        session_id = message.session_id or f"session_{uuid.uuid4().hex[:8]}"
        
        # Emit user message event
        emit_agui_event(
            AGUIStandardEvents.USER_MESSAGE,
            {
                "message": message.message,
                "message_type": message.message_type,
                "context": message.context or {}
            },
            user_id=message.user_id,
            session_id=session_id
        )
        
        # Process message based on content
        if "start orchestration" in message.message.lower() or "book" in message.message.lower():
            # Extract booking information from message or context
            booking_data = extract_booking_from_message(message)
            if booking_data:
                background_tasks.add_task(process_booking_request, booking_data, message.user_id, session_id)
                return AGUIAgentMessage(
                    message="I've started your travel orchestration! I'll coordinate with all the agents to ensure everything is ready for your medical tourism trip.",
                    user_id=message.user_id,
                    session_id=session_id,
                    message_type="text",
                    components=[
                        {
                            "type": "status_card",
                            "data": {
                                "title": "Orchestration Started",
                                "status": "active",
                                "details": "Coordinating flight, hotel, hospital, and accessibility services"
                            }
                        }
                    ]
                )
        
        elif "flight status" in message.message.lower() or "flight" in message.message.lower():
            # Handle flight status query
            response = await handle_flight_query(message.user_id, message.message)
            return AGUIAgentMessage(
                message=response.get("response", "I'm checking your flight status..."),
                user_id=message.user_id,
                session_id=session_id,
                message_type="text"
            )
        
        elif "help" in message.message.lower() or "what can you do" in message.message.lower():
            return AGUIAgentMessage(
                message="I'm Guardian, your medical tourism orchestrator. I can help you with:\n\n• Start travel orchestration\n• Check flight status\n• Query knowledge base\n• Handle schedule changes\n• Coordinate with hotels, hospitals, and accessibility services\n\nWhat would you like to do?",
                user_id=message.user_id,
                session_id=session_id,
                message_type="text",
                components=[
                    {
                        "type": "action_buttons",
                        "data": {
                            "buttons": [
                                {"label": "Start Orchestration", "action": "start_booking"},
                                {"label": "Check Flight Status", "action": "check_flight"},
                                {"label": "Ask Question", "action": "knowledge_query"}
                            ]
                        }
                    }
                ]
            )
        
        else:
            # Default knowledge base query
            response = await handle_general_query(message.user_id, message.message)
            return AGUIAgentMessage(
                message=response.get("response", "I understand you're asking about your medical tourism trip. Let me help you with that."),
                user_id=message.user_id,
                session_id=session_id,
                message_type="text"
            )
        
    except Exception as e:
        logger.error(f"❌ Failed to handle user message: {e}")
        emit_agui_event(
            AGUIStandardEvents.AGENT_ERROR,
            {"error": str(e), "message": message.message},
            user_id=message.user_id,
            session_id=message.session_id
        )
        raise HTTPException(status_code=500, detail=str(e))

def extract_booking_from_message(message: AGUIUserMessage) -> Optional[Dict[str, Any]]:
    """Extract booking information from user message or context"""
    # This would typically use NLP to extract structured data
    # For now, return a default booking structure
    if message.context and "booking_data" in message.context:
        return message.context["booking_data"]
    
    # Default test booking data
    return {
        "patient_id": message.user_id,
        "patient_name": "Test Patient",
        "patient_email": "test@example.com",
        "flight_number": "AA100",
        "flight_date": "2025-10-15",
        "departure_airport": "JFK",
        "arrival_airport": "LAX",
        "hotel_booking_reference": "HOTEL_123",
        "hospital_booking_reference": "HOSP_456",
        "special_requirements": "Wheelchair assistance",
        "medical_conditions": ["diabetes"],
        "age": 65,
        "emergency_contacts": [
            {"name": "Jane Doe", "phone": "+1-555-0123", "relationship": "spouse"}
        ],
        "flight_time": "09:00"
    }

async def process_booking_request(booking_data: Dict[str, Any], user_id: str, session_id: str):
    """Process booking request asynchronously"""
    try:
        # Emit orchestration start event
        emit_agui_event(
            AGUIStandardEvents.ORCHESTRATION_STARTED,
            {
                "patient_name": booking_data["patient_name"],
                "flight_number": booking_data["flight_number"],
                "flight_date": booking_data["flight_date"],
                "route": f"{booking_data['departure_airport']} → {booking_data['arrival_airport']}"
            },
            user_id=user_id,
            session_id=session_id
        )
        
        # Start orchestration
        orchestration_id = await guardian_orchestrator.start_orchestration(booking_data)
        
        # Emit completion event
        emit_agui_event(
            AGUIStandardEvents.ORCHESTRATION_COMPLETED,
            {
                "orchestration_id": orchestration_id,
                "status": "completed",
                "tasks_completed": len(guardian_orchestrator.active_orchestrations.get(orchestration_id, {}).get("tasks", {}))
            },
            user_id=user_id,
            session_id=session_id
        )
        
    except Exception as e:
        logger.error(f"❌ Booking orchestration failed: {e}")
        emit_agui_event(
            AGUIStandardEvents.ORCHESTRATION_FAILED,
            {"error": str(e)},
            user_id=user_id,
            session_id=session_id
        )

async def handle_flight_query(user_id: str, query: str) -> Dict[str, Any]:
    """Handle flight-related queries"""
    try:
        return await guardian_orchestrator.handle_knowledge_query(user_id, query, {})
    except Exception as e:
        logger.error(f"❌ Flight query failed: {e}")
        return {"response": "I'm having trouble checking your flight status right now. Please try again later."}

async def handle_general_query(user_id: str, query: str) -> Dict[str, Any]:
    """Handle general knowledge queries"""
    try:
        return await guardian_orchestrator.handle_knowledge_query(user_id, query, {})
    except Exception as e:
        logger.error(f"❌ General query failed: {e}")
        return {"response": "I'm here to help with your medical tourism trip. What would you like to know?"}

# AG-UI Event Streaming
@app.get("/ag-ui/events/{user_id}")
async def get_user_events(user_id: str, limit: int = 20):
    """Get AG-UI events for a user"""
    events = active_events.get(user_id, [])
    return {
        "events": events[-limit:] if events else [],
        "count": len(events),
        "user_id": user_id,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/ag-ui/events/session/{session_id}")
async def get_session_events(session_id: str, limit: int = 20):
    """Get AG-UI events for a session"""
    events = active_events.get(session_id, [])
    return {
        "events": events[-limit:] if events else [],
        "count": len(events),
        "session_id": session_id,
        "timestamp": datetime.now().isoformat()
    }

# AG-UI Real-time Event Stream (Server-Sent Events)
@app.get("/ag-ui/stream/{user_id}")
async def stream_user_events(user_id: str):
    """Stream AG-UI events for a user using Server-Sent Events"""
    async def event_generator():
        last_count = 0
        
        while True:
            events = active_events.get(user_id, [])
            
            # Send new events
            if len(events) > last_count:
                new_events = events[last_count:]
                for event in new_events:
                    yield f"data: {event.json()}\n\n"
                last_count = len(events)
            
            # Wait before next check
            await asyncio.sleep(0.5)
    
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

# Guardian-specific endpoints (AG-UI compatible)
@app.post("/guardian/booking")
async def start_guardian_booking(request: GuardianBookingRequest, background_tasks: BackgroundTasks):
    """Start Guardian booking orchestration with AG-UI events"""
    try:
        session_id = request.session_id or f"session_{uuid.uuid4().hex[:8]}"
        
        # Emit agent start event
        emit_agui_event(
            AGUIStandardEvents.AGENT_START,
            {"action": "booking_orchestration"},
            user_id=request.user_id,
            session_id=session_id
        )
        
        # Convert request to booking data
        booking_data = {
            "patient_id": request.user_id,
            "patient_name": request.patient_name,
            "patient_email": request.patient_email,
            "flight_number": request.flight_number,
            "flight_date": request.flight_date,
            "departure_airport": request.departure_airport,
            "arrival_airport": request.arrival_airport,
            "hotel_booking_reference": request.hotel_booking_reference,
            "hospital_booking_reference": request.hospital_booking_reference,
            "special_requirements": request.special_requirements,
            "medical_conditions": request.medical_conditions,
            "age": request.age,
            "emergency_contacts": request.emergency_contacts,
            "flight_time": request.flight_time
        }
        
        # Start orchestration in background
        background_tasks.add_task(process_booking_request, booking_data, request.user_id, session_id)
        
        return {
            "status": "success",
            "message": "Guardian orchestration started successfully",
            "user_id": request.user_id,
            "session_id": session_id,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to start Guardian booking: {e}")
        emit_agui_event(
            AGUIStandardEvents.AGENT_ERROR,
            {"error": str(e)},
            user_id=request.user_id,
            session_id=request.session_id
        )
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/guardian/status/{user_id}")
async def get_guardian_status(user_id: str):
    """Get Guardian orchestration status for a user"""
    try:
        # Find active orchestration for user
        orchestration_id = None
        for oid, orchestration in guardian_orchestrator.active_orchestrations.items():
            if orchestration.get("patient_id") == user_id:
                orchestration_id = oid
                break
        
        if not orchestration_id:
            return {
                "status": "no_active_orchestration",
                "user_id": user_id,
                "timestamp": datetime.now().isoformat()
            }
        
        orchestration = guardian_orchestrator.active_orchestrations[orchestration_id]
        
        return {
            "status": orchestration["status"],
            "user_id": user_id,
            "orchestration_id": orchestration_id,
            "created_at": orchestration["created_at"],
            "tasks": orchestration.get("tasks", {}),
            "flight_data": orchestration.get("flight_data", {}),
            "coordination_results": orchestration.get("coordination_results", {}),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to get Guardian status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== TRIP FLOW ENDPOINTS ====================

@app.post("/guardian/booking/create")
async def create_booking(request: BookingCreateRequest):
    """Create a new booking and start orchestration"""
    try:
        booking_data = request.dict()
        result = await guardian_orchestrator.handle_booking_creation(request.user_id, booking_data)
        
        emit_agui_event("booking_created", result, request.user_id)
        
        return {
            "status": "success",
            "data": result,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to create booking: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/guardian/flight/check-reminders")
async def check_flight_reminders(request: UserRequest):
    """Check if user needs flight reminders (7 hours before departure)"""
    try:
        result = await guardian_orchestrator.check_flight_reminders(request.user_id)
        
        if result.get("status") == "reminder_sent":
            emit_agui_event("flight_reminder_sent", result, request.user_id)
        
        return {
            "status": "success",
            "data": result,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to check flight reminders: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/guardian/location/update")
async def update_user_location(request: LocationUpdateRequest):
    """Update user location and handle arrival detection"""
    try:
        location_data = request.dict()
        result = await guardian_orchestrator.handle_arrival_detection(request.user_id, location_data)
        
        if result.get("status") == "arrival_flow_triggered":
            emit_agui_event("arrival_detected", result, request.user_id)
        
        return {
            "status": "success",
            "data": result,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to update location: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/guardian/cab/arrival")
async def handle_cab_arrival(request: CabArrivalRequest):
    """Handle cab arrival notification and trigger voice call"""
    try:
        cab_details = request.dict()
        result = await guardian_orchestrator.handle_cab_arrival_notification(request.user_id, cab_details)
        
        if result.get("status") == "voice_call_triggered":
            emit_agui_event("voice_call_initiated", result, request.user_id)
        
        return {
            "status": "success",
            "data": result,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to handle cab arrival: {e}")
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

# ==================== ADAPTIVE STAY MANAGEMENT ENDPOINTS ====================

@app.post("/guardian/stay/extension")
async def handle_stay_extension(request: StayExtensionRequest):
    """Handle hospital stay extension - the core adaptive feature"""
    try:
        extension_data = {
            "new_discharge_date": request.new_discharge_date,
            "reason": request.reason,
            "extension_days": request.extension_days,
            "notify_family": request.notify_family
        }
        
        result = await guardian_orchestrator.handle_stay_extension(request.user_id, extension_data)
        
        # Emit AG-UI event
        emit_agui_event(
            "stay_extended",
            {
                "extension_days": request.extension_days,
                "new_discharge_date": request.new_discharge_date,
                "reason": request.reason,
                "adaptive_response": result.get("adaptive_response", "automatic")
            },
            request.user_id,
            None
        )
        
        return {
            "status": "success",
            "data": result,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to handle stay extension: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/guardian/treatment/check-updates")
async def check_treatment_updates(request: UserRequest):
    """Manually trigger treatment update check"""
    try:
        result = await guardian_orchestrator.check_daily_treatment_updates()
        
        return {
            "status": "success",
            "data": result,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to check treatment updates: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/guardian/stay/timeline/{user_id}")
async def get_adaptive_timeline(user_id: str):
    """Get adaptive timeline view for the frontend"""
    try:
        # Get trip status with adaptive stay info
        trip_status = await guardian_orchestrator.get_user_trip_status(user_id)
        
        if trip_status.get("status") == "error":
            raise HTTPException(status_code=404, detail="User not found")
        
        # Build adaptive timeline
        booking = trip_status.get("bookings", [{}])[0]
        adaptive_stay = trip_status.get("adaptive_stay", {})
        
        timeline = {
            "user_id": user_id,
            "current_status": adaptive_stay.get("status", "unknown"),
            "phases": [
                {
                    "phase": "arrival",
                    "status": "completed" if trip_status.get("current_location") else "planned",
                    "description": "Patient arrival and airport pickup"
                },
                {
                    "phase": "hotel_checkin",
                    "status": "completed" if adaptive_stay.get("status") == "active" else "planned",
                    "description": "Hotel check-in and accommodation"
                },
                {
                    "phase": "treatment",
                    "status": "completed" if adaptive_stay.get("status") == "treatment_phase" else "planned",
                    "description": "Medical treatment and hospital care"
                },
                {
                    "phase": "recovery",
                    "status": "ongoing" if adaptive_stay.get("status") in ["treatment_phase", "extended"] else "planned",
                    "description": "Recovery period and monitoring"
                },
                {
                    "phase": "departure",
                    "status": "pending",
                    "description": "Flight departure and return home"
                }
            ],
            "adaptive_features": {
                "flexible_booking": adaptive_stay.get("flexible_booking", True),
                "auto_extension": adaptive_stay.get("extension_capability", True),
                "family_notifications": adaptive_stay.get("family_notifications", True),
                "extended": adaptive_stay.get("extended", False)
            },
            "stay_details": {
                "initial_estimate_days": adaptive_stay.get("initial_estimate_days", 7),
                "extension_reason": booking.get("extension_reason"),
                "new_discharge_date": booking.get("new_discharge_date")
            }
        }
        
        return {
            "status": "success",
            "data": timeline,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to get adaptive timeline: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(
        "ag_ui_backend:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
