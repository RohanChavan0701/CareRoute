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
