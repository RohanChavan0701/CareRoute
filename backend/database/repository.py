"""
HIPAA-Compliant Data Repository
Provides secure data access methods with encryption and audit logging
"""

from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc
from datetime import datetime
import logging

from .models import Patient, Booking, FlightStatus, DeviceToken, AuditLog
from .encryption import get_encryption_service
from .audit import HIPAAAuditService

logger = logging.getLogger(__name__)

class HIPAACompliantRepository:
    """
    HIPAA-compliant data repository
    Provides secure access to patient and booking data
    """
    
    def __init__(self, db_session: Session):
        self.db_session = db_session
        self.audit_service = HIPAAAuditService(db_session)
    
    # Patient Management
    def create_patient(self, patient_data: Dict[str, Any], user_id: str) -> Patient:
        """
        Create new patient with encryption and audit logging
        
        Args:
            patient_data: Patient data dictionary
            user_id: User creating the patient
            
        Returns:
            Created patient record
        """
        try:
            # Encrypt sensitive data
            encryption = get_encryption_service()
            encrypted_data = encryption.encrypt_patient_data(patient_data)
            
            # Parse date of birth
            date_of_birth = None
            if patient_data.get("date_of_birth"):
                try:
                    date_of_birth = datetime.strptime(patient_data["date_of_birth"], "%Y-%m-%d")
                except ValueError:
                    date_of_birth = None
            
            # Create patient record
            patient = Patient(
                patient_id=encrypted_data.get("patient_id"),
                first_name=encrypted_data.get("first_name"),
                last_name=encrypted_data.get("last_name"),
                date_of_birth=date_of_birth,
                patient_language=encrypted_data.get("patient_language", "English"),
                emergency_contact=encrypted_data.get("emergency_contact"),
                email=encrypted_data.get("email"),
                medical_conditions_encrypted=encrypted_data.get("medical_conditions_encrypted"),
                special_requirements_encrypted=encrypted_data.get("special_requirements_encrypted"),
                companion_name=encrypted_data.get("companion_name")
            )
            
            self.db_session.add(patient)
            self.db_session.commit()
            self.db_session.refresh(patient)
            
            # Log patient creation
            self.audit_service.log_patient_access(
                patient_id=str(patient.id),
                action="CREATE",
                user_id=user_id,
                new_values=patient_data
            )
            
            logger.info(f"✅ Created patient {patient.patient_id}")
            return patient
        
        except Exception as e:
            logger.error(f"❌ Failed to create patient: {e}")
            self.db_session.rollback()
            raise
    
    def get_patient_by_id(self, patient_id: str, user_id: str) -> Optional[Patient]:
        """
        Get patient by ID with audit logging
        
        Args:
            patient_id: Patient identifier
            user_id: User accessing the patient
            
        Returns:
            Patient record or None
        """
        try:
            patient = self.db_session.query(Patient).filter(
                Patient.patient_id == patient_id,
                Patient.is_active == True
            ).first()
            
            if patient:
                # Log patient access
                self.audit_service.log_patient_access(
                    patient_id=str(patient.id),
                    action="READ",
                    user_id=user_id
                )
                
                logger.info(f"📖 Retrieved patient {patient_id}")
            
            return patient
        
        except Exception as e:
            logger.error(f"❌ Failed to get patient {patient_id}: {e}")
            raise
    
    def update_patient(self, patient_id: str, update_data: Dict[str, Any], user_id: str) -> Optional[Patient]:
        """
        Update patient with encryption and audit logging
        
        Args:
            patient_id: Patient identifier
            update_data: Data to update
            user_id: User updating the patient
            
        Returns:
            Updated patient record or None
        """
        try:
            patient = self.get_patient_by_id(patient_id, user_id)
            if not patient:
                return None
            
            # Store old values for audit
            old_values = {
                "first_name": patient.first_name,
                "last_name": patient.last_name,
                "patient_language": patient.patient_language,
                "emergency_contact": patient.emergency_contact,
                "email": patient.email
            }
            
            # Encrypt sensitive update data
            encryption = get_encryption_service()
            encrypted_data = encryption.encrypt_patient_data(update_data)
            
            # Update fields
            if "first_name" in encrypted_data:
                patient.first_name = encrypted_data["first_name"]
            if "last_name" in encrypted_data:
                patient.last_name = encrypted_data["last_name"]
            if "patient_language" in encrypted_data:
                patient.patient_language = encrypted_data["patient_language"]
            if "emergency_contact" in encrypted_data:
                patient.emergency_contact = encrypted_data["emergency_contact"]
            if "email" in encrypted_data:
                patient.email = encrypted_data["email"]
            if "medical_conditions_encrypted" in encrypted_data:
                patient.medical_conditions_encrypted = encrypted_data["medical_conditions_encrypted"]
            if "special_requirements_encrypted" in encrypted_data:
                patient.special_requirements_encrypted = encrypted_data["special_requirements_encrypted"]
            if "companion_name" in encrypted_data:
                patient.companion_name = encrypted_data["companion_name"]
            
            patient.updated_at = datetime.utcnow()
            
            self.db_session.commit()
            self.db_session.refresh(patient)
            
            # Log patient update
            self.audit_service.log_patient_access(
                patient_id=str(patient.id),
                action="UPDATE",
                user_id=user_id,
                old_values=old_values,
                new_values=update_data
            )
            
            logger.info(f"✅ Updated patient {patient_id}")
            return patient
        
        except Exception as e:
            logger.error(f"❌ Failed to update patient {patient_id}: {e}")
            self.db_session.rollback()
            raise
    
    def get_patient_for_voice_call(self, patient_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get patient data formatted for voice agent calls
        
        Args:
            patient_id: Patient identifier
            user_id: User accessing the patient
            
        Returns:
            Formatted patient data for voice agent
        """
        try:
            patient = self.get_patient_by_id(patient_id, user_id)
            if not patient:
                return None
            
            # Get latest booking
            booking = self.db_session.query(Booking).filter(
                Booking.patient_id == patient.id,
                Booking.is_active == True
            ).order_by(desc(Booking.created_at)).first()
            
            if not booking:
                return None
            
            # Decrypt sensitive data for voice agent context
            patient_data = {
                "patient_name": f"{patient.first_name} {patient.last_name}",
                "patient_id": patient.patient_id,
                "patient_language": patient.patient_language,
                "patient_contact": patient.emergency_contact or "",
                "patient_dob": patient.date_of_birth.strftime("%Y-%m-%d") if patient.date_of_birth else "Not specified",
                "companion_name": patient.companion_name or "Not specified",
                
                # Booking information
                "check_in_date": booking.hotel_check_in.strftime("%Y-%m-%d %H:%M") if booking.hotel_check_in else "",
                "check_out_date": booking.hotel_check_out.strftime("%Y-%m-%d %H:%M") if booking.hotel_check_out else "",
                "hotel_name": booking.hotel_name or "Not booked",
                "hotel_room_number": booking.hotel_room_number or "Not assigned",
                "shuttle_driver": booking.shuttle_driver or "Not assigned",
                
                # Medical information
                "hospital_name": booking.hospital_name or "Not scheduled",
                "doctor_name": booking.doctor_name or "Not assigned",
                "appointment_date": booking.appointment_time.strftime("%Y-%m-%d") if booking.appointment_time else "",
                "appointment_time": booking.appointment_time.strftime("%H:%M %p") if booking.appointment_time else "",
                "pickup_time": booking.pickup_time.strftime("%Y-%m-%d %H:%M") if booking.pickup_time else "",
                "discharge_date": booking.actual_discharge_date.strftime("%Y-%m-%d %H:%M") if booking.actual_discharge_date else "",
                "discharge_status": booking.discharge_status or "Pending"
            }
            
            # Decrypt medical conditions and special requirements if needed
            encryption = get_encryption_service()
            if patient.medical_conditions_encrypted:
                try:
                    medical_conditions = encryption.decrypt_data(patient.medical_conditions_encrypted)
                    patient_data["medical_conditions"] = medical_conditions
                except:
                    patient_data["medical_conditions"] = "Available but encrypted"
            
            if patient.special_requirements_encrypted:
                try:
                    special_requirements = encryption.decrypt_data(patient.special_requirements_encrypted)
                    patient_data["special_requirements"] = special_requirements
                except:
                    patient_data["special_requirements"] = "Available but encrypted"
            
            logger.info(f"🎤 Prepared voice call context for patient {patient_id}")
            return patient_data
        
        except Exception as e:
            logger.error(f"❌ Failed to get patient voice call data {patient_id}: {e}")
            raise
    
    # Booking Management
    def create_booking(self, booking_data: Dict[str, Any], patient_id: str, user_id: str) -> Booking:
        """
        Create new booking with audit logging
        
        Args:
            booking_data: Booking data dictionary
            patient_id: Associated patient ID
            user_id: User creating the booking
            
        Returns:
            Created booking record
        """
        try:
            # Get patient
            patient = self.get_patient_by_id(patient_id, user_id)
            if not patient:
                raise ValueError(f"Patient {patient_id} not found")
            
            # Create booking record
            booking = Booking(
                booking_id=booking_data.get("booking_id"),
                patient_id=patient.id,
                travel_date=datetime.fromisoformat(booking_data.get("travel_date", "").replace("T", " ").split(".")[0]) if booking_data.get("travel_date") else None,
                return_date=datetime.fromisoformat(booking_data.get("return_date", "").replace("T", " ").split(".")[0]) if booking_data.get("return_date") else None,
                flight_number=booking_data.get("flight_number"),
                departure_airport=booking_data.get("departure_airport"),
                arrival_airport=booking_data.get("arrival_airport"),
                hotel_name=booking_data.get("hotel_name"),
                hotel_room_number=booking_data.get("hotel_room_number"),
                hotel_check_in=datetime.fromisoformat(booking_data.get("hotel_check_in", "").replace("T", " ").split(".")[0]) if booking_data.get("hotel_check_in") else None,
                hotel_check_out=datetime.fromisoformat(booking_data.get("hotel_check_out", "").replace("T", " ").split(".")[0]) if booking_data.get("hotel_check_out") else None,
                hospital_name=booking_data.get("hospital_name"),
                doctor_name=booking_data.get("doctor_name"),
                appointment_time=datetime.fromisoformat(booking_data.get("appointment_time", "").replace("T", " ").split(".")[0]) if booking_data.get("appointment_time") else None,
                expected_discharge_date=datetime.fromisoformat(booking_data.get("expected_discharge_date", "").replace("T", " ").split(".")[0]) if booking_data.get("expected_discharge_date") else None,
                pickup_time=datetime.fromisoformat(booking_data.get("pickup_time", "").replace("T", " ").split(".")[0]) if booking_data.get("pickup_time") else None,
                shuttle_driver=booking_data.get("shuttle_driver")
            )
            
            self.db_session.add(booking)
            self.db_session.commit()
            self.db_session.refresh(booking)
            
            # Log booking creation
            self.audit_service.log_booking_access(
                booking_id=str(booking.id),
                action="CREATE",
                user_id=user_id,
                new_values=booking_data
            )
            
            logger.info(f"✅ Created booking {booking.booking_id}")
            return booking
        
        except Exception as e:
            logger.error(f"❌ Failed to create booking: {e}")
            self.db_session.rollback()
            raise
    
    def get_booking_by_id(self, booking_id: str, user_id: str) -> Optional[Booking]:
        """
        Get booking by ID with audit logging
        
        Args:
            booking_id: Booking identifier
            user_id: User accessing the booking
            
        Returns:
            Booking record or None
        """
        try:
            booking = self.db_session.query(Booking).filter(
                Booking.booking_id == booking_id,
                Booking.is_active == True
            ).first()
            
            if booking:
                # Log booking access
                self.audit_service.log_booking_access(
                    booking_id=str(booking.id),
                    action="READ",
                    user_id=user_id
                )
                
                logger.info(f"📖 Retrieved booking {booking_id}")
            
            return booking
        
        except Exception as e:
            logger.error(f"❌ Failed to get booking {booking_id}: {e}")
            raise
    
    def update_booking(self, booking_id: str, update_data: Dict[str, Any], user_id: str) -> Optional[Booking]:
        """
        Update booking with audit logging
        
        Args:
            booking_id: Booking identifier
            update_data: Data to update
            user_id: User updating the booking
            
        Returns:
            Updated booking record or None
        """
        try:
            booking = self.get_booking_by_id(booking_id, user_id)
            if not booking:
                return None
            
            # Store old values for audit
            old_values = {
                "booking_status": booking.booking_status,
                "hotel_room_number": booking.hotel_room_number,
                "appointment_time": booking.appointment_time.isoformat() if booking.appointment_time else None,
                "discharge_status": booking.discharge_status
            }
            
            # Update fields
            for field, value in update_data.items():
                if hasattr(booking, field):
                    if field.endswith("_date") or field.endswith("_time"):
                        if value:
                            setattr(booking, field, datetime.fromisoformat(value.replace("T", " ").split(".")[0]))
                    else:
                        setattr(booking, field, value)
            
            booking.updated_at = datetime.utcnow()
            
            self.db_session.commit()
            self.db_session.refresh(booking)
            
            # Log booking update
            self.audit_service.log_booking_access(
                booking_id=str(booking.id),
                action="UPDATE",
                user_id=user_id,
                old_values=old_values,
                new_values=update_data
            )
            
            logger.info(f"✅ Updated booking {booking_id}")
            return booking
        
        except Exception as e:
            logger.error(f"❌ Failed to update booking {booking_id}: {e}")
            self.db_session.rollback()
            raise
    
    # Device Token Management
    def register_device_token(self, patient_id: str, device_token: str, device_type: str = "unknown", user_id: str = "system") -> DeviceToken:
        """
        Register FCM device token for patient
        
        Args:
            patient_id: Patient identifier
            device_token: FCM device token
            device_type: Device type (ios, android)
            user_id: User registering the token
            
        Returns:
            Device token record
        """
        try:
            # Get patient
            patient = self.get_patient_by_id(patient_id, user_id)
            if not patient:
                raise ValueError(f"Patient {patient_id} not found")
            
            # Check if token already exists
            existing_token = self.db_session.query(DeviceToken).filter(
                DeviceToken.patient_id == patient.id,
                DeviceToken.device_token == device_token
            ).first()
            
            if existing_token:
                existing_token.last_used = datetime.utcnow()
                existing_token.is_active = True
                self.db_session.commit()
                logger.info(f"📱 Updated existing device token for patient {patient_id}")
                return existing_token
            
            # Create new device token
            device_token_record = DeviceToken(
                patient_id=patient.id,
                device_token=device_token,
                device_type=device_type,
                last_used=datetime.utcnow()
            )
            
            self.db_session.add(device_token_record)
            self.db_session.commit()
            self.db_session.refresh(device_token_record)
            
            # Log device token registration
            self.audit_service.log_system_access(
                action="REGISTER_DEVICE_TOKEN",
                resource_type="device_token",
                user_id=user_id,
                details={"patient_id": patient_id, "device_type": device_type}
            )
            
            logger.info(f"📱 Registered device token for patient {patient_id}")
            return device_token_record
        
        except Exception as e:
            logger.error(f"❌ Failed to register device token for patient {patient_id}: {e}")
            self.db_session.rollback()
            raise
    
    def get_device_tokens_for_patient(self, patient_id: str, user_id: str) -> List[str]:
        """
        Get active device tokens for patient
        
        Args:
            patient_id: Patient identifier
            user_id: User accessing the tokens
            
        Returns:
            List of active device tokens
        """
        try:
            patient = self.get_patient_by_id(patient_id, user_id)
            if not patient:
                return []
            
            tokens = self.db_session.query(DeviceToken).filter(
                DeviceToken.patient_id == patient.id,
                DeviceToken.is_active == True
            ).all()
            
            device_tokens = [token.device_token for token in tokens]
            
            # Log token access
            self.audit_service.log_system_access(
                action="READ_DEVICE_TOKENS",
                resource_type="device_token",
                user_id=user_id,
                details={"patient_id": patient_id, "token_count": len(device_tokens)}
            )
            
            logger.info(f"📱 Retrieved {len(device_tokens)} device tokens for patient {patient_id}")
            return device_tokens
        
        except Exception as e:
            logger.error(f"❌ Failed to get device tokens for patient {patient_id}: {e}")
            raise

    def get_all_patients(self, user_id: str) -> List[Patient]:
        """Get all patients (for migration/verification)"""
        try:
            patients = self.db_session.query(Patient).filter(Patient.is_active == True).all()
            self.audit_service.log_system_access("all", user_id, "patients", "read")
            return patients
        except Exception as e:
            logger.error(f"Failed to get all patients: {e}")
            return []

    def get_all_bookings(self, user_id: str) -> List[Booking]:
        """Get all bookings (for migration/verification)"""
        try:
            bookings = self.db_session.query(Booking).filter(Booking.is_active == True).all()
            self.audit_service.log_system_access("all", user_id, "bookings", "read")
            return bookings
        except Exception as e:
            logger.error(f"Failed to get all bookings: {e}")
            return []

    def get_bookings_by_patient_id(self, patient_id: str, user_id: str) -> List[Booking]:
        """Get all bookings for a specific patient"""
        try:
            # First get the patient by patient_id
            patient = self.get_patient_by_id(patient_id, user_id)
            if not patient:
                logger.warning(f"Patient {patient_id} not found")
                return []
            
            # Get bookings for this patient
            bookings = self.db_session.query(Booking).filter(
                Booking.patient_id == patient.id,
                Booking.is_active == True
            ).all()
            
            self.audit_service.log_system_access(
                patient_id, user_id, "bookings", "read"
            )
            
            logger.info(f"Retrieved {len(bookings)} bookings for patient {patient_id}")
            return bookings
            
        except Exception as e:
            logger.error(f"Failed to get bookings for patient {patient_id}: {e}")
            return []

    def get_all_flight_statuses(self, user_id: str) -> List[FlightStatus]:
        """Get all flight statuses (for migration/verification)"""
        try:
            flights = self.db_session.query(FlightStatus).all()
            self.audit_service.log_system_access("all", user_id, "flights", "read")
            return flights
        except Exception as e:
            logger.error(f"Failed to get all flight statuses: {e}")
            return []

    def get_all_device_tokens(self, user_id: str) -> List[DeviceToken]:
        """Get all device tokens (for migration/verification)"""
        try:
            tokens = self.db_session.query(DeviceToken).filter(DeviceToken.is_active == True).all()
            self.audit_service.log_system_access("all", user_id, "device_tokens", "read")
            return tokens
        except Exception as e:
            logger.error(f"Failed to get all device tokens: {e}")
            return []

    def create_flight_status(self, flight_data: Dict[str, Any], user_id: str) -> FlightStatus:
        """Create flight status record"""
        try:
            flight = FlightStatus(**flight_data)
            self.db_session.add(flight)
            self.db_session.commit()
            self.db_session.refresh(flight)
            
            self.audit_service.log_system_access(
                str(flight.id),
                user_id,
                "flight_status",
                "CREATE"
            )
            
            logger.info(f"✅ Created flight status: {flight.flight_number}")
            return flight
            
        except Exception as e:
            logger.error(f"❌ Failed to create flight status: {e}")
            self.db_session.rollback()
            raise

    def create_device_token(self, token_data: Dict[str, Any], user_id: str) -> DeviceToken:
        """Create device token record"""
        try:
            device_token = DeviceToken(**token_data)
            self.db_session.add(device_token)
            self.db_session.commit()
            self.db_session.refresh(device_token)
            
            self.audit_service.log_system_access(
                str(device_token.id),
                user_id,
                "device_token",
                "CREATE"
            )
            
            logger.info(f"✅ Created device token for patient {token_data.get('patient_id')}")
            return device_token
            
        except Exception as e:
            logger.error(f"❌ Failed to create device token: {e}")
            self.db_session.rollback()
            raise

def create_repository(db_session: Session) -> HIPAACompliantRepository:
    """
    Create repository instance
    
    Args:
        db_session: Database session
        
    Returns:
        Repository instance
    """
    return HIPAACompliantRepository(db_session)
