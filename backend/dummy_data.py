"""
Dummy database for Guardian Orchestrator
Stores booking and flight data for trip orchestration
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

class DummyDatabase:
    def __init__(self):
        self.data_file = "dummy_data.json"
        self.data = self._load_data()
    
    def _load_data(self) -> Dict:
        """Load data from JSON file or create default structure"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading data: {e}")
        
        # Default structure
        return {
            "bookings": {},
            "flights": {},
            "users": {},
            "locations": {},
            "orchestrations": {}
        }
    
    def _save_data(self):
        """Save data to JSON file"""
        try:
            with open(self.data_file, 'w') as f:
                json.dump(self.data, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Error saving data: {e}")
    
    def create_sample_booking(self, user_id: str = "PAT-12345") -> str:
        """Create sample booking data for testing voice agent"""
        sample_booking = {
            "booking_id": f"BOOK_{user_id}_{int(datetime.now().timestamp())}",
            "user_id": user_id,
            "patient_name": "Marie Dubois",
            "patient_email": "marie.dubois@example.com",
            "date_of_birth": "1985-03-15",
            "patient_language": "French",
            "emergency_contacts": ["+33-123-456-789"],
            "companion_name": "Jean Dubois",
            "medical_conditions": ["Diabetes", "Hypertension"],
            "special_requirements": ["Wheelchair accessible", "French speaking staff"],
            
            # Flight details
            "flight_number": "AI101",
            "flight_date": "2025-10-14T08:00:00",
            "departure_airport": "CDG",
            "arrival_airport": "DEN",
            
            # Hotel details
            "hotel_name": "JW Marriott Hotel",
            "hotel_room_number": "Room 205",
            "hotel_check_in": "2025-10-14T14:00:00",
            "hotel_check_out": "2025-10-18T11:00:00",
            "hotel_booking_reference": "MAR-12345",
            "shuttle_driver": "Ahmed Hassan",
            
            # Hospital details
            "hospital_name": "Apollo Medical Center",
            "doctor_name": "Dr. Meera Singh",
            "hospital_appointment_time": "2025-10-15T09:30:00",
            "hospital_appointment_id": "APT-789",
            
            # Discharge details
            "expected_discharge_date": "2025-10-17T11:00:00",
            "new_discharge_date": "2025-10-17T11:00:00",
            "discharge_status": "Pending",
            "pickup_time": "2025-10-14T13:45:00",
            
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        self.data["bookings"][user_id] = [sample_booking]
        self._save_data()
        logger.info(f"✅ Created sample booking for user {user_id}")
        return sample_booking["booking_id"]
    
    def create_booking(self, user_id: str, booking_data: Dict) -> str:
        """Create a new booking"""
        booking_id = f"BOOK_{user_id}_{int(datetime.now().timestamp())}"
        
        booking = {
            "booking_id": booking_id,
            "user_id": user_id,
            "created_at": datetime.now().isoformat(),
            "status": "confirmed",
            **booking_data
        }
        
        self.data["bookings"][booking_id] = booking
        
        # Create user if not exists
        if user_id not in self.data["users"]:
            self.data["users"][user_id] = {
                "user_id": user_id,
                "created_at": datetime.now().isoformat(),
                "bookings": []
            }
        
        self.data["users"][user_id]["bookings"].append(booking_id)
        self._save_data()
        
        logger.info(f"✅ Created booking {booking_id} for user {user_id}")
        return booking_id
    
    def create_flight(self, user_id: str, flight_data: Dict) -> str:
        """Create flight tracking data"""
        flight_id = f"FLIGHT_{user_id}_{int(datetime.now().timestamp())}"
        
        flight = {
            "flight_id": flight_id,
            "user_id": user_id,
            "created_at": datetime.now().isoformat(),
            "status": "scheduled",
            **flight_data
        }
        
        self.data["flights"][flight_id] = flight
        self._save_data()
        
        logger.info(f"✅ Created flight {flight_id} for user {user_id}")
        return flight_id
    
    def update_flight_status(self, flight_id: str, status_data: Dict):
        """Update flight status with real-time data"""
        if flight_id in self.data["flights"]:
            self.data["flights"][flight_id].update({
                "updated_at": datetime.now().isoformat(),
                "status_data": status_data
            })
            self._save_data()
            logger.info(f"✅ Updated flight status for {flight_id}")
    
    def get_user_bookings(self, user_id: str) -> List[Dict]:
        """Get all bookings for a user"""
        # Check if user has bookings stored directly by user_id
        if user_id in self.data["bookings"]:
            return self.data["bookings"][user_id]
        
        # Fallback to the old method for backward compatibility
        user_bookings = []
        if user_id in self.data["users"]:
            for booking_id in self.data["users"][user_id]["bookings"]:
                if booking_id in self.data["bookings"]:
                    user_bookings.append(self.data["bookings"][booking_id])
        return user_bookings
    
    def get_user_booking(self, user_id: str) -> Optional[Dict]:
        """Get the first booking for a user"""
        bookings = self.get_user_bookings(user_id)
        return bookings[0] if bookings else None
    
    def update_booking(self, user_id: str, booking_data: Dict) -> bool:
        """Update a booking for a user"""
        try:
            bookings = self.get_user_bookings(user_id)
            if not bookings:
                return False
            
            # Update the first booking
            booking_id = bookings[0]["booking_id"]
            if booking_id in self.data["bookings"]:
                self.data["bookings"][booking_id].update(booking_data)
                self._save_data()
                logger.info(f"✅ Updated booking {booking_id} for user {user_id}")
                return True
            
            return False
        except Exception as e:
            logger.error(f"❌ Error updating booking: {e}")
            return False
    
    def get_user_flights(self, user_id: str) -> List[Dict]:
        """Get all flights for a user"""
        user_flights = []
        for flight_id, flight in self.data["flights"].items():
            if flight["user_id"] == user_id:
                user_flights.append(flight)
        return user_flights
    
    def update_user_location(self, user_id: str, location_data: Dict):
        """Update user's current location"""
        self.data["locations"][user_id] = {
            "updated_at": datetime.now().isoformat(),
            **location_data
        }
        self._save_data()
        logger.info(f"✅ Updated location for user {user_id}")
    
    def get_user_location(self, user_id: str) -> Optional[Dict]:
        """Get user's current location"""
        return self.data["locations"].get(user_id)
    
    def create_orchestration(self, orchestration_id: str, orchestration_data: Dict):
        """Create orchestration tracking"""
        self.data["orchestrations"][orchestration_id] = {
            "created_at": datetime.now().isoformat(),
            "status": "active",
            **orchestration_data
        }
        self._save_data()
        logger.info(f"✅ Created orchestration {orchestration_id}")
    
    def update_orchestration_status(self, orchestration_id: str, status: str, data: Dict = None):
        """Update orchestration status"""
        if orchestration_id in self.data["orchestrations"]:
            self.data["orchestrations"][orchestration_id]["status"] = status
            self.data["orchestrations"][orchestration_id]["updated_at"] = datetime.now().isoformat()
            if data:
                self.data["orchestrations"][orchestration_id].update(data)
            self._save_data()
            logger.info(f"✅ Updated orchestration {orchestration_id} to {status}")

# Global instance
dummy_db = DummyDatabase()
