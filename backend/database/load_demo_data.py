#!/usr/bin/env python3
"""
Load comprehensive demo data for Guardian Orchestrator testing
"""

import os
import sys
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.database.connection import database_manager
from backend.database.repository import create_repository
from backend.database.models import Patient, Booking, FlightStatus, DeviceToken

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_comprehensive_demo_data():
    """Load comprehensive demo data for testing all orchestrator flows"""
    logger.info("🚀 Loading comprehensive demo data for Guardian Orchestrator...")
    
    # Get database session
    session = database_manager.get_session_sync()
    repository = create_repository(session)
    
    try:
        # Demo data for different patient scenarios
        demo_patients = [
            {
                'patient_id': 'PAT-DEMO-001',
                'first_name': 'John',
                'last_name': 'Smith',
                'date_of_birth': '1980-05-15',
                'patient_language': 'English',
                'emergency_contact': '+1-555-123-4567',
                'email': 'john.smith@example.com',
                'medical_conditions': ['Hypertension', 'Diabetes'],
                'special_requirements': ['Wheelchair accessible', 'English speaking staff'],
                'companion_name': 'Mary Smith'
            },
            {
                'patient_id': 'PAT-DEMO-002',
                'first_name': 'Maria',
                'last_name': 'Garcia',
                'date_of_birth': '1975-08-22',
                'patient_language': 'Spanish',
                'emergency_contact': '+1-555-234-5678',
                'email': 'maria.garcia@example.com',
                'medical_conditions': ['Heart Condition'],
                'special_requirements': ['Spanish speaking staff', 'Ground floor room'],
                'companion_name': 'Carlos Garcia'
            },
            {
                'patient_id': 'PAT-DEMO-003',
                'first_name': 'Ahmed',
                'last_name': 'Hassan',
                'date_of_birth': '1988-12-10',
                'patient_language': 'Arabic',
                'emergency_contact': '+1-555-345-6789',
                'email': 'ahmed.hassan@example.com',
                'medical_conditions': ['Orthopedic Surgery'],
                'special_requirements': ['Arabic speaking staff', 'Halal meals'],
                'companion_name': 'Fatima Hassan'
            }
        ]
        
        # Create patients and bookings
        created_patients = []
        created_bookings = []
        
        for patient_data in demo_patients:
            try:
                # Check if patient already exists
                existing_patient = repository.get_patient_by_id(patient_data['patient_id'], 'demo_loader')
                if existing_patient:
                    patient = existing_patient
                    logger.info(f"✅ Found existing patient: {patient.patient_id}")
                else:
                    # Create patient
                    patient = repository.create_patient(patient_data, 'demo_loader')
                    logger.info(f"✅ Created patient: {patient.patient_id}")
                created_patients.append(patient)
                
                # Create comprehensive booking data
                booking_data = {
                    'booking_id': f'BOOK_{patient.patient_id}_{int(datetime.now().timestamp())}',
                    'travel_date': (datetime.now() + timedelta(days=2)).isoformat(),
                    'return_date': (datetime.now() + timedelta(days=7)).isoformat(),
                    'flight_number': f'AA{100 + len(created_patients)}',
                    'departure_airport': ['JFK', 'LAX', 'ORD'][len(created_patients) % 3],
                    'arrival_airport': 'DEN',
                    'hotel_name': ['Marriott Downtown', 'Hilton Garden Inn', 'Hyatt Regency'][len(created_patients) % 3],
                    'hotel_room_number': f'Room {200 + len(created_patients)}',
                    'hotel_check_in': (datetime.now() + timedelta(days=2, hours=14)).isoformat(),
                    'hotel_check_out': (datetime.now() + timedelta(days=7, hours=11)).isoformat(),
                    'hospital_name': 'Denver Medical Center',
                    'doctor_name': ['Dr. Johnson', 'Dr. Williams', 'Dr. Brown'][len(created_patients) % 3],
                    'appointment_time': (datetime.now() + timedelta(days=3, hours=10)).isoformat(),
                    'expected_discharge_date': (datetime.now() + timedelta(days=6, hours=11)).isoformat(),
                    'pickup_time': (datetime.now() + timedelta(days=2, hours=13, minutes=30)).isoformat(),
                    'shuttle_driver': ['Mike Johnson', 'Sarah Wilson', 'David Lee'][len(created_patients) % 3]
                }
                
                # Create booking
                booking = repository.create_booking(booking_data, patient.patient_id, 'demo_loader')
                created_bookings.append(booking)
                logger.info(f"✅ Created booking: {booking.booking_id}")
                
                # Create flight status
                flight_data = {
                    'booking_id': booking.id,
                    'flight_number': booking_data['flight_number'],
                    'status': 'scheduled',
                    'gate': f'Gate {len(created_patients) + 10}',
                    'terminal': f'Terminal {len(created_patients) % 3 + 1}',
                    'departure_time': datetime.fromisoformat(booking_data['travel_date'].replace('T', ' ').split('.')[0]),
                    'estimated_arrival': datetime.now() + timedelta(days=2, hours=16),
                    'source': 'demo_loader'
                }
                
                # Create flight status using repository method
                flight = repository.create_flight_status(flight_data, 'demo_loader')
                logger.info(f"✅ Created flight: {flight.flight_number}")
                
                # Create device token for FCM using repository method
                device_token_data = {
                    'patient_id': patient.id,
                    'device_token': f'demo_token_{patient.patient_id}_{int(datetime.now().timestamp())}',
                    'device_type': 'ios',
                    'app_version': '1.0.0'
                }
                
                device_token = repository.create_device_token(device_token_data, 'demo_loader')
                logger.info(f"✅ Created device token for {patient.patient_id}")
                
            except Exception as e:
                logger.error(f"❌ Failed to create demo data for {patient_data['patient_id']}: {e}")
                continue
        
        logger.info(f"🎉 Demo data loading completed!")
        logger.info(f"   Patients: {len(created_patients)}")
        logger.info(f"   Bookings: {len(created_bookings)}")
        
    except Exception as e:
        logger.error(f"❌ Demo data loading failed: {e}")
        raise
    finally:
        session.close()

def verify_demo_data():
    """Verify that demo data was loaded successfully"""
    logger.info("🔍 Verifying demo data...")
    
    session = database_manager.get_session_sync()
    repository = create_repository(session)
    
    try:
        # Count all data
        patients = repository.get_all_patients('verification_script')
        bookings = repository.get_all_bookings('verification_script')
        flights = repository.get_all_flight_statuses('verification_script')
        device_tokens = repository.get_all_device_tokens('verification_script')
        
        logger.info(f"📊 Demo Data Verification:")
        logger.info(f"   Patients: {len(patients)}")
        logger.info(f"   Bookings: {len(bookings)}")
        logger.info(f"   Flights: {len(flights)}")
        logger.info(f"   Device Tokens: {len(device_tokens)}")
        
        # Show sample data
        if patients:
            demo_patients = [p for p in patients if p.patient_id.startswith('PAT-DEMO-')]
            logger.info(f"\\n📋 Demo Patients ({len(demo_patients)}):")
            for patient in demo_patients[:3]:
                logger.info(f"   - {patient.patient_id}: {patient.first_name} {patient.last_name} ({patient.patient_language})")
        
        logger.info("✅ Demo data verification completed!")
        
    except Exception as e:
        logger.error(f"❌ Verification failed: {e}")
    finally:
        session.close()

def main():
    """Main function to load demo data"""
    logger.info("🚀 Guardian Demo Data Loader")
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
        
        # Load demo data
        load_comprehensive_demo_data()
        verify_demo_data()
        
        logger.info("🎉 Demo data loading completed successfully!")
        
    except Exception as e:
        logger.error(f"❌ Demo data loading failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
