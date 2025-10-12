"""
HIPAA-Compliant Database Models for Guardian Orchestrator
Defines secure data structures for medical tourism data
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid

Base = declarative_base()

class Patient(Base):
    """HIPAA-compliant patient information"""
    __tablename__ = "patients"
    
    # Primary identifiers
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_id = Column(String(50), unique=True, nullable=False, index=True)  # External patient ID
    
    # Basic demographics (minimal required info)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    date_of_birth = Column(DateTime, nullable=False)
    patient_language = Column(String(10), nullable=False, default="English")
    
    # Contact information
    emergency_contact = Column(String(20))  # Phone number only
    email = Column(String(255))  # Optional for notifications
    
    # Medical information (encrypted in application layer)
    medical_conditions_encrypted = Column(Text)  # Encrypted JSON
    special_requirements_encrypted = Column(Text)  # Encrypted JSON
    
    # Companion information
    companion_name = Column(String(200))  # Optional
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    bookings = relationship("Booking", back_populates="patient")
    audit_logs = relationship("AuditLog", back_populates="patient")

class Booking(Base):
    """Medical tourism booking information"""
    __tablename__ = "bookings"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    booking_id = Column(String(100), unique=True, nullable=False, index=True)
    
    # Foreign keys
    patient_id = Column(UUID(as_uuid=True), ForeignKey("patients.id"), nullable=False)
    
    # Travel dates
    travel_date = Column(DateTime, nullable=False)
    return_date = Column(DateTime, nullable=False)
    
    # Flight information
    flight_number = Column(String(20))
    departure_airport = Column(String(10))
    arrival_airport = Column(String(10))
    
    # Hotel information
    hotel_name = Column(String(200))
    hotel_room_number = Column(String(50))
    hotel_check_in = Column(DateTime)
    hotel_check_out = Column(DateTime)
    hotel_booking_reference = Column(String(100))
    
    # Medical appointments
    hospital_name = Column(String(200))
    doctor_name = Column(String(200))
    appointment_time = Column(DateTime)
    appointment_id = Column(String(100))
    
    # Discharge information
    expected_discharge_date = Column(DateTime)
    actual_discharge_date = Column(DateTime)
    discharge_status = Column(String(50), default="Pending")
    
    # Transportation
    pickup_time = Column(DateTime)
    shuttle_driver = Column(String(200))
    
    # Status tracking
    booking_status = Column(String(50), default="Confirmed")
    payment_status = Column(String(50), default="Pending")
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    patient = relationship("Patient", back_populates="bookings")
    flight_statuses = relationship("FlightStatus", back_populates="booking")
    audit_logs = relationship("AuditLog", back_populates="booking")

class FlightStatus(Base):
    """Flight status tracking"""
    __tablename__ = "flight_statuses"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    booking_id = Column(UUID(as_uuid=True), ForeignKey("bookings.id"), nullable=False)
    
    flight_number = Column(String(20), nullable=False)
    status = Column(String(50), nullable=False)  # On Time, Delayed, Cancelled, etc.
    gate = Column(String(10))
    terminal = Column(String(10))
    departure_time = Column(DateTime)
    arrival_time = Column(DateTime)
    estimated_arrival = Column(DateTime)
    
    # Metadata
    recorded_at = Column(DateTime, default=datetime.utcnow)
    source = Column(String(100))  # API source
    
    # Relationships
    booking = relationship("Booking", back_populates="flight_statuses")

class DeviceToken(Base):
    """FCM device tokens for push notifications"""
    __tablename__ = "device_tokens"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_id = Column(UUID(as_uuid=True), ForeignKey("patients.id"), nullable=False)
    
    device_token = Column(Text, nullable=False)
    device_type = Column(String(20))  # ios, android
    app_version = Column(String(20))
    
    # Metadata
    registered_at = Column(DateTime, default=datetime.utcnow)
    last_used = Column(DateTime)
    is_active = Column(Boolean, default=True)

class AuditLog(Base):
    """HIPAA-compliant audit logging"""
    __tablename__ = "audit_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Entity references
    patient_id = Column(UUID(as_uuid=True), ForeignKey("patients.id"), nullable=True)
    booking_id = Column(UUID(as_uuid=True), ForeignKey("bookings.id"), nullable=True)
    
    # Audit information
    action = Column(String(100), nullable=False)  # CREATE, READ, UPDATE, DELETE
    resource_type = Column(String(50), nullable=False)  # patient, booking, etc.
    user_id = Column(String(100))  # System user or API key
    ip_address = Column(String(45))
    user_agent = Column(Text)
    
    # Change tracking
    old_values = Column(JSON)  # Previous values (encrypted)
    new_values = Column(JSON)  # New values (encrypted)
    
    # Metadata
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    patient = relationship("Patient", back_populates="audit_logs")
    booking = relationship("Booking", back_populates="audit_logs")

class SystemConfiguration(Base):
    """System configuration and settings"""
    __tablename__ = "system_configurations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    config_key = Column(String(100), unique=True, nullable=False)
    config_value = Column(Text)
    config_type = Column(String(20), default="string")  # string, json, boolean, number
    description = Column(Text)
    is_encrypted = Column(Boolean, default=False)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
