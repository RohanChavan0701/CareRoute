"""
Guardian Orchestrator Scheduler
Handles automated tasks like flight reminders and status checks
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
from dummy_data import dummy_db
from orchestrator import guardian_orchestrator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GuardianScheduler:
    """
    Scheduler for Guardian Orchestrator automated tasks
    """
    
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.is_running = False
        
    async def start(self):
        """Start the scheduler"""
        if not self.is_running:
            logger.info("🚀 Starting Guardian Scheduler...")
            
            # Schedule flight reminder checks every 30 minutes
            self.scheduler.add_job(
                self._check_flight_reminders,
                trigger=IntervalTrigger(minutes=30),
                id='flight_reminders',
                name='Check Flight Reminders',
                max_instances=1,
                coalesce=True
            )
            
            # Schedule orchestration cleanup every hour
            self.scheduler.add_job(
                self._cleanup_old_orchestrations,
                trigger=IntervalTrigger(hours=1),
                id='orchestration_cleanup',
                name='Cleanup Old Orchestrations',
                max_instances=1,
                coalesce=True
            )
            
            # Schedule flight status updates every 15 minutes for active flights
            self.scheduler.add_job(
                self._update_flight_statuses,
                trigger=IntervalTrigger(minutes=15),
                id='flight_status_updates',
                name='Update Flight Statuses',
                max_instances=1,
                coalesce=True
            )
            
            # Schedule arrival monitoring every 10 minutes
            self.scheduler.add_job(
                self._monitor_arrivals,
                trigger=IntervalTrigger(minutes=10),
                id='arrival_monitoring',
                name='Monitor Arrivals',
                max_instances=1,
                coalesce=True
            )
            
            # Schedule daily treatment updates check every 6 hours
            self.scheduler.add_job(
                self._check_treatment_updates,
                trigger=IntervalTrigger(hours=6),
                id='treatment_updates',
                name='Check Treatment Updates',
                max_instances=1,
                coalesce=True
            )
            
            self.scheduler.start()
            self.is_running = True
            logger.info("✅ Guardian Scheduler started successfully")
            
            # Run initial checks
            await self._check_flight_reminders()
            await self._cleanup_old_orchestrations()
            
        else:
            logger.warning("⚠️ Scheduler is already running")
    
    async def stop(self):
        """Stop the scheduler"""
        if self.is_running:
            logger.info("🛑 Stopping Guardian Scheduler...")
            self.scheduler.shutdown()
            self.is_running = False
            logger.info("✅ Guardian Scheduler stopped")
        else:
            logger.warning("⚠️ Scheduler is not running")
    
    async def _check_flight_reminders(self):
        """Check for flights that need 7-hour reminders"""
        try:
            logger.info("🔍 Checking flight reminders...")
            current_time = datetime.now()
            reminders_sent = 0
            
            # Get all active flights
            all_flights = dummy_db.data.get("flights", {})
            
            for flight_id, flight in all_flights.items():
                if flight.get("status") == "scheduled":
                    try:
                        departure_date = datetime.strptime(flight.get("departure_date", ""), "%Y-%m-%d")
                        departure_time = datetime.strptime(flight.get("departure_time", ""), "%H:%M:%S")
                        departure_datetime = datetime.combine(departure_date, departure_time.time())
                        
                        # Check if 7 hours before departure (with 30-minute window)
                        time_diff = departure_datetime - current_time
                        
                        if timedelta(hours=6, minutes=30) <= time_diff <= timedelta(hours=7, minutes=30):
                            user_id = flight.get("user_id")
                            if user_id:
                                logger.info(f"⏰ Sending 7-hour reminder for flight {flight.get('flight_number')} to user {user_id}")
                                
                                # Trigger flight reminder
                                result = await guardian_orchestrator.check_flight_reminders(user_id)
                                
                                if result.get("status") == "reminder_sent":
                                    reminders_sent += 1
                                    logger.info(f"✅ Reminder sent for flight {flight.get('flight_number')}")
                                else:
                                    logger.info(f"ℹ️ No reminder needed for flight {flight.get('flight_number')}")
                    
                    except Exception as e:
                        logger.error(f"❌ Error processing flight {flight_id}: {e}")
                        continue
            
            logger.info(f"📊 Flight reminder check completed. Sent {reminders_sent} reminders.")
            
        except Exception as e:
            logger.error(f"❌ Error in flight reminder check: {e}")
    
    async def _update_flight_statuses(self):
        """Update flight statuses for active flights"""
        try:
            logger.info("🔄 Updating flight statuses...")
            current_time = datetime.now()
            updates_made = 0
            
            # Get all active flights
            all_flights = dummy_db.data.get("flights", {})
            
            for flight_id, flight in all_flights.items():
                if flight.get("status") == "scheduled":
                    try:
                        departure_date = datetime.strptime(flight.get("departure_date", ""), "%Y-%m-%d")
                        departure_time = datetime.strptime(flight.get("departure_time", ""), "%H:%M:%S")
                        departure_datetime = datetime.combine(departure_date, departure_time.time())
                        
                        # Update flights within 24 hours of departure or after departure
                        time_diff = departure_datetime - current_time
                        
                        if time_diff <= timedelta(hours=24):
                            user_id = flight.get("user_id")
                            if user_id:
                                logger.info(f"📡 Updating status for flight {flight.get('flight_number')}")
                                
                                # Get latest flight status
                                flight_status = await guardian_orchestrator._get_flight_status(flight)
                                
                                if flight_status:
                                    dummy_db.update_flight_status(flight_id, flight_status)
                                    updates_made += 1
                                    logger.info(f"✅ Updated status for flight {flight.get('flight_number')}: {flight_status.get('status', 'unknown')}")
                    
                    except Exception as e:
                        logger.error(f"❌ Error updating flight {flight_id}: {e}")
                        continue
            
            logger.info(f"📊 Flight status update completed. Updated {updates_made} flights.")
            
        except Exception as e:
            logger.error(f"❌ Error in flight status update: {e}")
    
    async def _monitor_arrivals(self):
        """Monitor for flight arrivals and trigger arrival flows"""
        try:
            logger.info("🛬 Monitoring arrivals...")
            current_time = datetime.now()
            arrivals_detected = 0
            
            # Get all active flights
            all_flights = dummy_db.data.get("flights", {})
            
            for flight_id, flight in all_flights.items():
                try:
                    departure_date = datetime.strptime(flight.get("departure_date", ""), "%Y-%m-%d")
                    departure_time = datetime.strptime(flight.get("departure_time", ""), "%H:%M:%S")
                    departure_datetime = datetime.combine(departure_date, departure_time.time())
                    
                    # Estimate arrival time (assuming 3.5 hour flight)
                    estimated_arrival = departure_datetime + timedelta(hours=3, minutes=30)
                    
                    # Check if flight should have arrived (within 2 hours of estimated arrival)
                    time_since_estimated_arrival = current_time - estimated_arrival
                    
                    if timedelta(hours=-1) <= time_since_estimated_arrival <= timedelta(hours=2):
                        user_id = flight.get("user_id")
                        if user_id:
                            # Check if user has location data (at airport)
                            user_location = dummy_db.get_user_location(user_id)
                            
                            if user_location and user_location.get("airport_name"):
                                logger.info(f"🛬 Flight {flight.get('flight_number')} appears to have arrived for user {user_id}")
                                
                                # Trigger arrival flow
                                result = await guardian_orchestrator.handle_arrival_detection(user_id, user_location)
                                
                                if result.get("status") == "arrival_flow_triggered":
                                    arrivals_detected += 1
                                    logger.info(f"✅ Arrival flow triggered for user {user_id}")
                
                except Exception as e:
                    logger.error(f"❌ Error monitoring arrival for flight {flight_id}: {e}")
                    continue
            
            logger.info(f"📊 Arrival monitoring completed. Detected {arrivals_detected} arrivals.")
            
        except Exception as e:
            logger.error(f"❌ Error in arrival monitoring: {e}")
    
    async def _cleanup_old_orchestrations(self):
        """Clean up old completed orchestrations"""
        try:
            logger.info("🧹 Cleaning up old orchestrations...")
            
            # Get all orchestrations
            all_orchestrations = dummy_db.data.get("orchestrations", {})
            current_time = datetime.now()
            cleaned_count = 0
            
            for orchestration_id, orchestration in all_orchestrations.items():
                try:
                    created_at_str = orchestration.get("created_at")
                    if created_at_str:
                        created_at = datetime.fromisoformat(created_at_str.replace('Z', '+00:00'))
                        
                        # Clean up orchestrations older than 7 days
                        if current_time - created_at > timedelta(days=7):
                            # Check if orchestration is completed
                            status = orchestration.get("status", "")
                            if status in ["completed", "failed", "cancelled"]:
                                del dummy_db.data["orchestrations"][orchestration_id]
                                cleaned_count += 1
                                logger.info(f"🗑️ Cleaned up old orchestration: {orchestration_id}")
                
                except Exception as e:
                    logger.error(f"❌ Error cleaning orchestration {orchestration_id}: {e}")
                    continue
            
            if cleaned_count > 0:
                dummy_db._save_data()
            
            logger.info(f"📊 Orchestration cleanup completed. Cleaned {cleaned_count} old orchestrations.")
            
        except Exception as e:
            logger.error(f"❌ Error in orchestration cleanup: {e}")
    
    async def _check_treatment_updates(self):
        """Check for daily treatment updates and handle stay extensions"""
        try:
            logger.info("🏥 Checking daily treatment updates...")
            
            # Call the orchestrator's treatment update check
            result = await guardian_orchestrator.check_daily_treatment_updates()
            
            updates_found = result.get("updates_found", 0)
            logger.info(f"📊 Treatment update check completed. Found {updates_found} updates.")
            
        except Exception as e:
            logger.error(f"❌ Error in treatment update check: {e}")
    
    async def get_scheduler_status(self) -> Dict:
        """Get current scheduler status"""
        return {
            "is_running": self.is_running,
            "jobs": [
                {
                    "id": job.id,
                    "name": job.name,
                    "next_run": job.next_run_time.isoformat() if job.next_run_time else None,
                    "trigger": str(job.trigger)
                }
                for job in self.scheduler.get_jobs()
            ] if self.is_running else [],
            "timestamp": datetime.now().isoformat()
        }

# Global scheduler instance
guardian_scheduler = GuardianScheduler()

# Example usage
async def main():
    """Example of how to use the scheduler"""
    scheduler = GuardianScheduler()
    
    try:
        await scheduler.start()
        
        # Keep running
        while True:
            await asyncio.sleep(60)
            
    except KeyboardInterrupt:
        logger.info("🛑 Received interrupt signal")
        await scheduler.stop()

if __name__ == "__main__":
    asyncio.run(main())
