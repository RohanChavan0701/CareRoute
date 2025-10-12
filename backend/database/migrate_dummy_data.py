#!/usr/bin/env python3
"""
Migration script to transfer dummy data to HIPAA-compliant database
"""

import os
import sys
import logging
from datetime import datetime
from typing import Dict, List, Any

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.dummy_data import dummy_db
from backend.database.connection import database_manager
from backend.database.repository import create_repository
from backend.database.models import Patient, Booking, FlightStatus, DeviceToken

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def migrate_patients_and_bookings():
    """Migrate patients and bookings from dummy data to HIPAA database"""
    logger.info("🚀 Starting migration of dummy data to HIPAA database...")
    
    # Get database session
    session = database_manager.get_session_sync()
    repository = create_repository(session)
    
    try:
        # Get all dummy bookings
        dummy_bookings = dummy_db.data.get("bookings", {})
        migrated_count = 0
        
        for user_id, booking_list in dummy_bookings.items():
            for booking_data in booking_list:
                try:
                    logger.info(f"📋 Migrating booking for user {user_id}: {booking_data.get('patient_name', 'Unknown')}")
                    
                    # Check if patient already exists
                    existing_patient = repository.get_patient_by_id(booking_data.get('user_id', user_id), 'migration_script')
                    
                    if existing_patient:
                        patient = existing_patient
                        logger.info(f"✅ Found existing patient: {patient.patient_id}")
                    else:
                        # Prepare patient data
                        patient_data = {
                            'patient_id': booking_data.get('user_id', user_id),
                            'first_name': booking_data.get('patient_name', '').split(' ')[0] if booking_data.get('patient_name') else '',
                            'last_name': ' '.join(booking_data.get('patient_name', '').split(' ')[1:]) if booking_data.get('patient_name') else '',
                            'date_of_birth': booking_data.get('date_of_birth', '1990-01-01'),
                            'patient_language': booking_data.get('patient_language', booking_data.get('preferred_language', 'English')),
                            'emergency_contact': booking_data.get('emergency_contacts', [''])[0] if booking_data.get('emergency_contacts') else '',
                            'email': booking_data.get('patient_email', ''),
                            'medical_conditions': booking_data.get('medical_conditions', []),
                            'special_requirements': booking_data.get('special_requirements', []),
                            'companion_name': booking_data.get('companion_name', '')
                        }
                        
                        # Create patient in database
                        patient = repository.create_patient(patient_data, 'migration_script')
                        logger.info(f"✅ Created patient: {patient.patient_id}")
                    
                    # Prepare booking data
                    booking_data_db = {
                        'booking_id': booking_data.get('booking_id', f'BOOK_{user_id}'),
                        'travel_date': booking_data.get('flight_date', ''),
                        'return_date': booking_data.get('expected_discharge_date', ''),
                        'flight_number': booking_data.get('flight_number', ''),
                        'departure_airport': booking_data.get('departure_airport', ''),
                        'arrival_airport': booking_data.get('arrival_airport', ''),
                        'hotel_name': booking_data.get('hotel_name', ''),
                        'hotel_room_number': booking_data.get('hotel_room_number', ''),
                        'hotel_check_in': booking_data.get('hotel_check_in', ''),
                        'hotel_check_out': booking_data.get('hotel_check_out', ''),
                        'hospital_name': booking_data.get('hospital_name', ''),
                        'doctor_name': booking_data.get('doctor_name', ''),
                        'appointment_time': booking_data.get('hospital_appointment_time', ''),
                        'expected_discharge_date': booking_data.get('expected_discharge_date', ''),
                        'pickup_time': booking_data.get('pickup_time', ''),
                        'shuttle_driver': booking_data.get('shuttle_driver', '')
                    }
                    
                    # Create booking in database
                    booking = repository.create_booking(booking_data_db, patient.patient_id, 'migration_script')
                    logger.info(f"✅ Created booking: {booking.booking_id}")
                    
                    # Create flight status if flight data exists
                    if booking_data.get('flight_number'):
                        flight_data = {
                            'booking_id': booking.id,
                            'flight_number': booking_data.get('flight_number', ''),
                            'departure_airport': booking_data.get('departure_airport', ''),
                            'arrival_airport': booking_data.get('arrival_airport', ''),
                            'departure_date': booking_data.get('flight_date', ''),
                            'status': 'scheduled',
                            'gate': 'TBD',
                            'terminal': 'TBD'
                        }
                        
                        flight = repository.create_flight_status(flight_data, 'migration_script')
                        logger.info(f"✅ Created flight: {flight.flight_number}")
                    
                    migrated_count += 1
                    
                except Exception as e:
                    logger.error(f"❌ Failed to migrate booking for {user_id}: {e}")
                    continue
        
        logger.info(f"🎉 Migration completed! Migrated {migrated_count} bookings")
        
    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
        raise
    finally:
        session.close()

def create_sample_device_tokens():
    """Create sample device tokens for FCM testing"""
    logger.info("📱 Creating sample device tokens...")
    
    session = database_manager.get_session_sync()
    repository = create_repository(session)
    
    try:
        # Create device tokens for migrated patients
        patients = repository.get_all_patients('migration_script')
        
        for patient in patients[:2]:  # Create tokens for first 2 patients
            device_token_data = {
                'patient_id': patient.id,
                'device_token': f'sample_token_{patient.patient_id}_{datetime.now().strftime("%Y%m%d_%H%M%S")}',
                'device_type': 'mobile',
                'platform': 'ios'
            }
            
            device_token = repository.create_device_token(device_token_data, 'migration_script')
            logger.info(f"✅ Created device token for {patient.patient_id}")
        
    except Exception as e:
        logger.error(f"❌ Failed to create device tokens: {e}")
    finally:
        session.close()

def verify_migration():
    """Verify that migration was successful"""
    logger.info("🔍 Verifying migration...")
    
    session = database_manager.get_session_sync()
    repository = create_repository(session)
    
    try:
        # Count migrated data
        patients = repository.get_all_patients('verification_script')
        bookings = repository.get_all_bookings('verification_script')
        flights = repository.get_all_flight_statuses('verification_script')
        device_tokens = repository.get_all_device_tokens('verification_script')
        
        logger.info(f"📊 Migration Verification:")
        logger.info(f"   Patients: {len(patients)}")
        logger.info(f"   Bookings: {len(bookings)}")
        logger.info(f"   Flights: {len(flights)}")
        logger.info(f"   Device Tokens: {len(device_tokens)}")
        
        # Show sample patient data
        if patients:
            sample_patient = patients[0]
            logger.info(f"\\n📋 Sample Patient:")
            logger.info(f"   ID: {sample_patient.patient_id}")
            logger.info(f"   Name: {sample_patient.first_name} {sample_patient.last_name}")
            logger.info(f"   Language: {sample_patient.patient_language}")
            logger.info(f"   Email: {sample_patient.email}")
        
        logger.info("✅ Migration verification completed!")
        
    except Exception as e:
        logger.error(f"❌ Verification failed: {e}")
    finally:
        session.close()

def main():
    """Main migration function"""
    logger.info("🚀 Guardian Dummy Data Migration to HIPAA Database")
    logger.info("=" * 60)
    
    try:
        # Set environment variables
        os.environ.setdefault('DATABASE_URL', 'postgresql://guardian_user:guardian_secure_2024@localhost:5432/guardian_hipaa_db')
        os.environ.setdefault('HIPAA_ENCRYPTION_PASSWORD', 'guardian_hipaa_encryption_password_2024_secure')
        os.environ.setdefault('HIPAA_ENCRYPTION_SALT', 'guardian_hipaa_salt_2024_secure')
        
        # Test database connection
        if not database_manager.test_connection():
            logger.error("❌ Database connection failed")
            return
        
        logger.info("✅ Database connection successful")
        
        # Migrate data
        migrate_patients_and_bookings()
        create_sample_device_tokens()
        verify_migration()
        
        logger.info("🎉 Migration completed successfully!")
        
    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
