#!/usr/bin/env python3
"""
Guardian Medical Tourism Orchestrator - HIPAA-Compliant Backend
Secure REST API with database integration for medical tourism data
"""

import asyncio
import logging
import json
import uuid
import os
from datetime import datetime
from typing import Dict, Any, List, Optional, Generator
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field, EmailStr
from sqlalchemy.orm import Session
import uvicorn

# Import HIPAA-compliant database components
from .database.connection import get_db, database_manager
from .database.repository import create_repository
from .database.audit import create_audit_service
from .database.encryption import get_encryption_service

# Import orchestrator and scheduler
from .orchestrator import guardian_orchestrator
from .scheduler import guardian_scheduler
from .fcm_service import fcm_service

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Request/Response Models
class PatientCreateRequest(BaseModel):
    """Request model for creating a patient"""
    patient_id: str = Field(..., description="Unique patient identifier")
    first_name: str = Field(..., description="Patient first name")
    last_name: str = Field(..., description="Patient last name")
    date_of_birth: str = Field(..., description="Date of birth (YYYY-MM-DD)")
    patient_language: str = Field(default="English", description="Patient's preferred language")
    emergency_contact: Optional[str] = Field(default=None, description="Emergency contact phone")
    email: Optional[EmailStr] = Field(default=None, description="Patient email")
    medical_conditions: Optional[List[str]] = Field(default=None, description="Medical conditions")
    special_requirements: Optional[List[str]] = Field(default=None, description="Special requirements")
    companion_name: Optional[str] = Field(default=None, description="Companion name")

class BookingCreateRequest(BaseModel):
    """Request model for creating a booking"""
    booking_id: str = Field(..., description="Unique booking identifier")
    patient_id: str = Field(..., description="Associated patient ID")
    travel_date: str = Field(..., description="Travel date (YYYY-MM-DD)")
    return_date: str = Field(..., description="Return date (YYYY-MM-DD)")
    flight_number: Optional[str] = Field(default=None, description="Flight number")
    departure_airport: Optional[str] = Field(default=None, description="Departure airport code")
    arrival_airport: Optional[str] = Field(default=None, description="Arrival airport code")
    hotel_name: Optional[str] = Field(default=None, description="Hotel name")
    hospital_name: Optional[str] = Field(default=None, description="Hospital name")
    doctor_name: Optional[str] = Field(default=None, description="Doctor name")
    appointment_time: Optional[str] = Field(default=None, description="Appointment time")

class VoiceCallRequest(BaseModel):
    """Request model for voice agent calls"""
    content: str = Field(..., description="Call content")
    user_id: str = Field(..., description="User identifier")
    session_id: Optional[str] = Field(default=None, description="Session identifier")

class FCMTokenRequest(BaseModel):
    """Request model for FCM token registration"""
    user_id: str = Field(..., description="User identifier")
    device_token: str = Field(..., description="FCM device token")
    device_type: Optional[str] = Field(default="unknown", description="Device type (ios, android)")

class SimpleResponse(BaseModel):
    """Simple response model"""
    status: str = Field(..., description="Response status")
    message: str = Field(..., description="Response message")
    data: Optional[Dict[str, Any]] = Field(default=None, description="Response data")
    timestamp: str = Field(..., description="Response timestamp")

# HIPAA-compliant request handler
def get_user_id_from_request(request: Request) -> str:
    """Extract user ID from request headers or JWT token"""
    # In production, this would extract from JWT token
    user_id = request.headers.get("X-User-ID", "system")
    return user_id

def get_client_ip(request: Request) -> str:
    """Extract client IP address"""
    return request.client.host if request.client else "unknown"

def get_user_agent(request: Request) -> str:
    """Extract user agent"""
    return request.headers.get("User-Agent", "unknown")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    logger.info("🚀 Guardian HIPAA-Compliant Orchestrator starting up...")
    
    # Test database connection
    try:
        if not database_manager.test_connection():
            raise ConnectionError("Database connection failed")
        logger.info("✅ Database connection established")
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        raise
    
    # Initialize scheduler
    try:
        guardian_scheduler.start()
        logger.info("✅ Guardian Scheduler started")
    except Exception as e:
        logger.error(f"❌ Failed to start scheduler: {e}")
        raise
    
    logger.info("✅ Guardian HIPAA Orchestrator ready")
    
    yield
    
    # Cleanup
    logger.info("🛑 Shutting down Guardian Orchestrator...")
    guardian_scheduler.stop()
    logger.info("✅ Guardian Scheduler stopped")

# Create FastAPI app with HIPAA compliance
app = FastAPI(
    title="Guardian Medical Tourism Orchestrator - HIPAA Compliant",
    description="Secure backend API for medical tourism trip orchestration with HIPAA compliance",
    version="2.0.0",
    lifespan=lifespan
)

# Add CORS middleware with security headers
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:8080").split(","),
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Health Check Endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "protocol": "HIPAA-REST-API",
        "version": "2.0.0",
        "agent_id": "guardian_orchestrator_hipaa",
        "timestamp": datetime.now().isoformat(),
        "capabilities": [
            "hipaa_compliant_orchestration",
            "encrypted_data_storage",
            "audit_logging",
            "real_time_events",
            "voice_interaction",
            "schedule_management"
        ],
        "database_status": "connected" if database_manager.test_connection() else "disconnected"
    }

# Patient Management Endpoints
@app.post("/patients", response_model=SimpleResponse)
async def create_patient(
    patient_data: PatientCreateRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """Create a new patient with HIPAA compliance"""
    try:
        repository = create_repository(db)
        user_id = get_user_id_from_request(request)
        
        # Convert Pydantic model to dict
        patient_dict = patient_data.dict()
        
        # Create patient with audit logging
        patient = repository.create_patient(patient_dict, user_id)
        
        return SimpleResponse(
            status="success",
            message="Patient created successfully",
            data={
                "patient_id": patient.patient_id,
                "id": str(patient.id),
                "created_at": patient.created_at.isoformat()
            },
            timestamp=datetime.now().isoformat()
        )
    
    except Exception as e:
        logger.error(f"❌ Failed to create patient: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create patient: {str(e)}")

@app.get("/patients/{patient_id}", response_model=SimpleResponse)
async def get_patient(
    patient_id: str,
    request: Request,
    db: Session = Depends(get_db)
):
    """Get patient by ID with HIPAA audit logging"""
    try:
        repository = create_repository(db)
        user_id = get_user_id_from_request(request)
        
        patient = repository.get_patient_by_id(patient_id, user_id)
        
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")
        
        # Return patient data (non-sensitive fields only)
        patient_data = {
            "patient_id": patient.patient_id,
            "first_name": patient.first_name,
            "last_name": patient.last_name,
            "patient_language": patient.patient_language,
            "companion_name": patient.companion_name,
            "created_at": patient.created_at.isoformat(),
            "updated_at": patient.updated_at.isoformat()
        }
        
        return SimpleResponse(
            status="success",
            message="Patient retrieved successfully",
            data=patient_data,
            timestamp=datetime.now().isoformat()
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to get patient {patient_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get patient: {str(e)}")

# Booking Management Endpoints
@app.post("/bookings", response_model=SimpleResponse)
async def create_booking(
    booking_data: BookingCreateRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """Create a new booking with HIPAA compliance"""
    try:
        repository = create_repository(db)
        user_id = get_user_id_from_request(request)
        
        # Convert Pydantic model to dict
        booking_dict = booking_data.dict()
        
        # Create booking with audit logging
        booking = repository.create_booking(booking_dict, booking_data.patient_id, user_id)
        
        return SimpleResponse(
            status="success",
            message="Booking created successfully",
            data={
                "booking_id": booking.booking_id,
                "id": str(booking.id),
                "patient_id": booking_data.patient_id,
                "created_at": booking.created_at.isoformat()
            },
            timestamp=datetime.now().isoformat()
        )
    
    except Exception as e:
        logger.error(f"❌ Failed to create booking: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create booking: {str(e)}")

@app.get("/bookings/{booking_id}", response_model=SimpleResponse)
async def get_booking(
    booking_id: str,
    request: Request,
    db: Session = Depends(get_db)
):
    """Get booking by ID with HIPAA audit logging"""
    try:
        repository = create_repository(db)
        user_id = get_user_id_from_request(request)
        
        booking = repository.get_booking_by_id(booking_id, user_id)
        
        if not booking:
            raise HTTPException(status_code=404, detail="Booking not found")
        
        # Return booking data
        booking_data = {
            "booking_id": booking.booking_id,
            "patient_id": booking.patient_id,
            "travel_date": booking.travel_date.isoformat() if booking.travel_date else None,
            "return_date": booking.return_date.isoformat() if booking.return_date else None,
            "flight_number": booking.flight_number,
            "hotel_name": booking.hotel_name,
            "hospital_name": booking.hospital_name,
            "doctor_name": booking.doctor_name,
            "booking_status": booking.booking_status,
            "created_at": booking.created_at.isoformat(),
            "updated_at": booking.updated_at.isoformat()
        }
        
        return SimpleResponse(
            status="success",
            message="Booking retrieved successfully",
            data=booking_data,
            timestamp=datetime.now().isoformat()
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to get booking {booking_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get booking: {str(e)}")

# Voice Agent Integration
@app.post("/guardian/voice/call", response_model=SimpleResponse)
async def initiate_voice_call(
    request_data: VoiceCallRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """Initiate voice call with complete patient context"""
    try:
        repository = create_repository(db)
        user_id = get_user_id_from_request(request)
        
        # Get comprehensive patient context for voice agent
        patient_context = repository.get_patient_for_voice_call(request_data.user_id, user_id)
        
        if not patient_context:
            # Return default context if no patient data found
            patient_context = {
                "patient_name": "Guest User",
                "patient_id": request_data.user_id,
                "patient_language": "English",
                "patient_contact": "",
                "patient_dob": "Not specified",
                "companion_name": "Not specified",
                "check_in_date": "",
                "check_out_date": "",
                "hotel_name": "Not available",
                "hotel_room_number": "Not available",
                "shuttle_driver": "Not available",
                "hospital_name": "Not available",
                "doctor_name": "Not available",
                "appointment_date": "",
                "appointment_time": "",
                "pickup_time": "",
                "discharge_date": "",
                "discharge_status": "Pending"
            }
        
        # Send to voice agent via orchestrator
        voice_response = await guardian_orchestrator._send_a2a_task(
            "voice_agent", "configure_patient_call", patient_context
        )
        
        return SimpleResponse(
            status="success",
            message="Voice call initiated with complete patient context",
            data={
                "context_sent": True,
                "voice_agent_response": voice_response,
                "patient_context": patient_context
            },
            timestamp=datetime.now().isoformat()
        )
    
    except Exception as e:
        logger.error(f"❌ Failed to initiate voice call: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to initiate voice call: {str(e)}")

# FCM Integration
@app.post("/fcm/register", response_model=SimpleResponse)
async def register_fcm_token(
    token_data: FCMTokenRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """Register FCM device token for push notifications"""
    try:
        repository = create_repository(db)
        user_id = get_user_id_from_request(request)
        
        # Register device token with audit logging
        device_token = repository.register_device_token(
            token_data.user_id,
            token_data.device_token,
            token_data.device_type,
            user_id
        )
        
        return SimpleResponse(
            status="success",
            message="FCM token registered successfully",
            data={
                "user_id": token_data.user_id,
                "device_token_id": str(device_token.id),
                "registered_at": device_token.registered_at.isoformat()
            },
            timestamp=datetime.now().isoformat()
        )
    
    except Exception as e:
        logger.error(f"❌ Failed to register FCM token: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to register FCM token: {str(e)}")

@app.post("/fcm/send-boarding-reminder", response_model=SimpleResponse)
async def send_boarding_reminder(
    request_data: Dict[str, Any],
    request: Request,
    db: Session = Depends(get_db)
):
    """Send boarding reminder notification"""
    try:
        repository = create_repository(db)
        user_id = get_user_id_from_request(request)
        
        user_id_param = request_data.get("user_id")
        flight_info = request_data.get("flight_info", {})
        
        # Get device tokens for user
        device_tokens = repository.get_device_tokens_for_patient(user_id_param, user_id)
        
        if not device_tokens:
            return SimpleResponse(
                status="warning",
                message="No device tokens found for user",
                data={"user_id": user_id_param},
                timestamp=datetime.now().isoformat()
            )
        
        # Send FCM notification
        success = await fcm_service.send_boarding_reminder(user_id_param, flight_info)
        
        return SimpleResponse(
            status="success" if success else "warning",
            message="Boarding reminder sent" if success else "Failed to send boarding reminder",
            data={
                "user_id": user_id_param,
                "flight_info": flight_info,
                "tokens_sent": len(device_tokens)
            },
            timestamp=datetime.now().isoformat()
        )
    
    except Exception as e:
        logger.error(f"❌ Failed to send boarding reminder: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to send boarding reminder: {str(e)}")

# Audit and Compliance Endpoints
@app.get("/audit/logs", response_model=SimpleResponse)
async def get_audit_logs(
    patient_id: Optional[str] = None,
    action: Optional[str] = None,
    limit: int = 100,
    request: Request = None,
    db: Session = Depends(get_db)
):
    """Get audit logs with filtering (HIPAA compliance)"""
    try:
        audit_service = create_audit_service(db)
        user_id = get_user_id_from_request(request)
        
        # Log audit log access
        audit_service.log_system_access(
            action="READ_AUDIT_LOGS",
            resource_type="audit_log",
            user_id=user_id,
            ip_address=get_client_ip(request),
            user_agent=get_user_agent(request)
        )
        
        # Get audit logs
        logs = audit_service.get_audit_logs(
            patient_id=patient_id,
            action=action,
            limit=limit
        )
        
        return SimpleResponse(
            status="success",
            message="Audit logs retrieved successfully",
            data={
                "logs": logs,
                "total_count": len(logs),
                "filters": {
                    "patient_id": patient_id,
                    "action": action,
                    "limit": limit
                }
            },
            timestamp=datetime.now().isoformat()
        )
    
    except Exception as e:
        logger.error(f"❌ Failed to get audit logs: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get audit logs: {str(e)}")

@app.get("/compliance/report", response_model=SimpleResponse)
async def generate_compliance_report(
    start_date: str,
    end_date: str,
    patient_id: Optional[str] = None,
    request: Request = None,
    db: Session = Depends(get_db)
):
    """Generate HIPAA compliance report"""
    try:
        audit_service = create_audit_service(db)
        user_id = get_user_id_from_request(request)
        
        # Parse dates
        start_dt = datetime.fromisoformat(start_date)
        end_dt = datetime.fromisoformat(end_date)
        
        # Generate report
        report = audit_service.generate_compliance_report(
            start_date=start_dt,
            end_date=end_dt,
            patient_id=patient_id
        )
        
        # Log report generation
        audit_service.log_system_access(
            action="GENERATE_COMPLIANCE_REPORT",
            resource_type="compliance_report",
            user_id=user_id,
            ip_address=get_client_ip(request),
            user_agent=get_user_agent(request),
            details={"start_date": start_date, "end_date": end_date, "patient_id": patient_id}
        )
        
        return SimpleResponse(
            status="success",
            message="Compliance report generated successfully",
            data=report,
            timestamp=datetime.now().isoformat()
        )
    
    except Exception as e:
        logger.error(f"❌ Failed to generate compliance report: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate compliance report: {str(e)}")

# Scheduler Status
@app.get("/scheduler/status", response_model=SimpleResponse)
async def get_scheduler_status():
    """Get scheduler status"""
    return SimpleResponse(
        status="success",
        message="Scheduler status retrieved",
        data={
            "is_running": guardian_scheduler.is_running(),
            "job_count": len(guardian_scheduler.get_jobs()) if guardian_scheduler.is_running() else 0,
            "next_run_times": guardian_scheduler.get_next_run_times() if guardian_scheduler.is_running() else []
        },
        timestamp=datetime.now().isoformat()
    )

if __name__ == "__main__":
    uvicorn.run(
        "backend.hipaa_backend:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
