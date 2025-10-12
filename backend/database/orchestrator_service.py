#!/usr/bin/env python3
"""
Database service for Guardian Orchestrator
Provides database-backed data access for orchestrator operations
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from .connection import database_manager
from .repository import create_repository
from .models import FlightStatus, DeviceToken
from .encryption import get_encryption_service

logger = logging.getLogger(__name__)

class OrchestratorDatabaseService:
    """Database service for orchestrator operations"""
    
    def __init__(self):
        self.db_manager = database_manager
        self._session = None
        self._repository = None
    
    def _get_session(self) -> Session:
        """Get database session"""
        if self._session is None:
            self._session = self.db_manager.get_session_sync()
        return self._session
    
    def _get_repository(self):
        """Get repository instance"""
        if self._repository is None:
            self._repository = create_repository(self._get_session())
        return self._repository
    
    def get_user_bookings(self, user_id: str) -> List[Dict[str, Any]]:
        """Get user bookings from database"""
        try:
            # Get patient by ID
            patient = self._get_repository().get_patient_by_id(user_id, 'orchestrator_service')
            if not patient:
                logger.warning(f"No patient found for user {user_id}")
                return []
            
            # Get bookings for patient
            bookings = self._get_repository().get_bookings_by_patient_id(patient.patient_id, 'orchestrator_service')
            
            # Convert to orchestrator format
            booking_list = []
            for booking in bookings:
                booking_dict = {
                    'booking_id': booking.booking_id,
                    'user_id': patient.patient_id,
                    'patient_name': f"{self._safe_decrypt(patient.first_name)} {self._safe_decrypt(patient.last_name)}",
                    'patient_email': self._safe_decrypt(patient.email),
                    'date_of_birth': patient.date_of_birth.strftime('%Y-%m-%d') if patient.date_of_birth else '',
                    'patient_language': self._safe_decrypt(patient.patient_language),
                    'emergency_contacts': [self._safe_decrypt(patient.emergency_contact)] if patient.emergency_contact else [],
                    'companion_name': self._safe_decrypt(patient.companion_name),
                    'medical_conditions': self._safe_decrypt(patient.medical_conditions_encrypted) if patient.medical_conditions_encrypted else [],
                    'special_requirements': self._safe_decrypt(patient.special_requirements_encrypted) if patient.special_requirements_encrypted else [],
                    
                    # Flight details
                    'flight_number': booking.flight_number,
                    'flight_date': booking.travel_date.isoformat() if booking.travel_date else '',
                    'departure_airport': booking.departure_airport,
                    'arrival_airport': booking.arrival_airport,
                    
                    # Hotel details
                    'hotel_name': booking.hotel_name,
                    'hotel_room_number': booking.hotel_room_number,
                    'hotel_check_in': booking.hotel_check_in.isoformat() if booking.hotel_check_in else '',
                    'hotel_check_out': booking.hotel_check_out.isoformat() if booking.hotel_check_out else '',
                    'hotel_booking_reference': booking.hotel_booking_reference,
                    'shuttle_driver': booking.shuttle_driver,
                    
                    # Hospital details
                    'hospital_name': booking.hospital_name,
                    'doctor_name': booking.doctor_name,
                    'hospital_appointment_time': booking.appointment_time.isoformat() if booking.appointment_time else '',
                    'hospital_appointment_id': booking.appointment_id,
                    
                    # Discharge details
                    'expected_discharge_date': booking.expected_discharge_date.isoformat() if booking.expected_discharge_date else '',
                    'new_discharge_date': booking.actual_discharge_date.isoformat() if booking.actual_discharge_date else '',
                    'discharge_status': booking.discharge_status,
                    'pickup_time': booking.pickup_time.isoformat() if booking.pickup_time else '',
                    
                    'created_at': booking.created_at.isoformat() if booking.created_at else '',
                    'updated_at': booking.updated_at.isoformat() if booking.updated_at else ''
                }
                booking_list.append(booking_dict)
            
            logger.info(f"Retrieved {len(booking_list)} bookings for user {user_id}")
            return booking_list
            
        except Exception as e:
            logger.error(f"Failed to get user bookings for {user_id}: {e}")
            return []
    
    def get_user_flights(self, user_id: str) -> List[Dict[str, Any]]:
        """Get user flight status from database"""
        try:
            # Get patient by ID
            patient = self._get_repository().get_patient_by_id(user_id, 'orchestrator_service')
            if not patient:
                logger.warning(f"No patient found for user {user_id}")
                return []
            
            # Get bookings for patient
            bookings = self._get_repository().get_bookings_by_patient_id(patient.patient_id, 'orchestrator_service')
            
            # Get flight statuses for bookings
            flight_list = []
            for booking in bookings:
                # Get flight statuses for this booking
                flight_statuses = self._get_session().query(FlightStatus).filter(
                    FlightStatus.booking_id == booking.id
                ).all()
                
                for flight_status in flight_statuses:
                    flight_dict = {
                        'flight_id': str(flight_status.id),
                        'flight_number': flight_status.flight_number,
                        'status': flight_status.status,
                        'gate': flight_status.gate,
                        'terminal': flight_status.terminal,
                        'departure_time': flight_status.departure_time.isoformat() if flight_status.departure_time else '',
                        'arrival_time': flight_status.arrival_time.isoformat() if flight_status.arrival_time else '',
                        'estimated_arrival': flight_status.estimated_arrival.isoformat() if flight_status.estimated_arrival else '',
                        'recorded_at': flight_status.recorded_at.isoformat() if flight_status.recorded_at else '',
                        'source': flight_status.source
                    }
                    flight_list.append(flight_dict)
            
            logger.info(f"Retrieved {len(flight_list)} flight statuses for user {user_id}")
            return flight_list
            
        except Exception as e:
            logger.error(f"Failed to get user flights for {user_id}: {e}")
            return []
    
    def get_user_location(self, user_id: str) -> Dict[str, Any]:
        """Get user location from database (placeholder - not implemented yet)"""
        # This would be implemented when location tracking is added
        return {
            'user_id': user_id,
            'location': 'Unknown',
            'timestamp': datetime.now().isoformat(),
            'source': 'database_service'
        }
    
    def update_user_location(self, user_id: str, location_data: Dict[str, Any]) -> bool:
        """Update user location in database (placeholder - not implemented yet)"""
        # This would be implemented when location tracking is added
        logger.info(f"Location update for {user_id}: {location_data}")
        return True
    
    def get_orchestration_data(self, orchestration_id: str) -> Dict[str, Any]:
        """Get orchestration data (placeholder - using in-memory for now)"""
        # This could be moved to database when needed
        return {}
    
    def update_orchestration_data(self, orchestration_id: str, data: Dict[str, Any]) -> bool:
        """Update orchestration data (placeholder - using in-memory for now)"""
        # This could be moved to database when needed
        logger.info(f"Orchestration update for {orchestration_id}: {data}")
        return True
    
    def get_device_token(self, user_id: str) -> Optional[str]:
        """Get FCM device token for user"""
        try:
            # Get patient by ID
            patient = self._get_repository().get_patient_by_id(user_id, 'orchestrator_service')
            if not patient:
                logger.warning(f"No patient found for user {user_id}")
                return None
            
            # Get device token for patient
            device_token = self._get_session().query(DeviceToken).filter(
                DeviceToken.patient_id == patient.id,
                DeviceToken.is_active == True
            ).first()
            
            if device_token:
                logger.info(f"Retrieved device token for user {user_id}")
                return device_token.device_token
            else:
                logger.warning(f"No device token found for user {user_id}")
                return None
                
        except Exception as e:
            logger.error(f"Failed to get device token for {user_id}: {e}")
            return None
    
    def create_sample_booking(self, user_id: str = "PAT-DEMO-001") -> str:
        """Create sample booking for testing (uses existing demo data)"""
        # This method is kept for compatibility with orchestrator
        # The actual data is already in the database
        logger.info(f"Sample booking requested for {user_id} - data already exists in database")
        return f"BOOK_{user_id}_sample"
    
    def _safe_decrypt(self, data: str) -> str:
        """Safely decrypt data, handling both encrypted and plain text data"""
        if not data:
            return ""
        
        try:
            # Check if data looks encrypted (base64-like and long)
            import re
            looks_encrypted = re.match(r'^[A-Za-z0-9+/=]+$', data) and len(data) > 20
            
            if looks_encrypted:
                # Try to decrypt
                return get_encryption_service().decrypt_data(data)
            else:
                # Data is already plain text
                return data
                
        except Exception as e:
            logger.warning(f"Decryption failed, using plain text: {e}")
            # If decryption fails, assume it's plain text
            return data
    
    def close(self):
        """Close database connections"""
        if self._session:
            self._session.close()
            self._session = None
        self._repository = None

# Global instance
orchestrator_db_service = OrchestratorDatabaseService()
