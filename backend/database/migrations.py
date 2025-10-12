"""
Database Migration Script for HIPAA-Compliant Database
Handles database initialization and schema updates
"""

import os
import sys
from datetime import datetime
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
import logging

# Add the backend directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.models import Base
from database.connection import DatabaseManager

logger = logging.getLogger(__name__)

class DatabaseMigration:
    """
    Database migration manager for HIPAA-compliant setup
    """
    
    def __init__(self, database_url: str = None):
        """
        Initialize migration manager
        
        Args:
            database_url: Database connection URL
        """
        self.database_url = database_url or os.getenv("DATABASE_URL")
        if not self.database_url:
            raise ValueError("DATABASE_URL environment variable must be set")
        
        self.db_manager = DatabaseManager(self.database_url)
    
    def create_database(self):
        """Create database if it doesn't exist (PostgreSQL only)"""
        try:
            # Extract database name from URL
            if "postgresql" in self.database_url:
                # Parse URL to get database name
                db_name = self.database_url.split("/")[-1].split("?")[0]
                base_url = self.database_url.rsplit("/", 1)[0]
                
                # Connect to postgres database to create target database
                admin_url = f"{base_url}/postgres"
                admin_engine = create_engine(admin_url)
                
                with admin_engine.connect() as conn:
                    # Check if database exists
                    result = conn.execute(text(
                        "SELECT 1 FROM pg_database WHERE datname = :db_name"
                    ), {"db_name": db_name})
                    
                    if not result.fetchone():
                        # Create database
                        conn.execute(text("COMMIT"))  # End current transaction
                        conn.execute(text(f'CREATE DATABASE "{db_name}"'))
                        logger.info(f"✅ Created database: {db_name}")
                    else:
                        logger.info(f"📋 Database {db_name} already exists")
            
            else:
                logger.info("📋 Non-PostgreSQL database, skipping database creation")
        
        except Exception as e:
            logger.error(f"❌ Failed to create database: {e}")
            raise
    
    def create_tables(self):
        """Create all database tables"""
        try:
            # Test connection first
            if not self.db_manager.test_connection():
                raise ConnectionError("Database connection failed")
            
            # Create tables
            self.db_manager.create_tables()
            logger.info("✅ Database tables created successfully")
        
        except Exception as e:
            logger.error(f"❌ Failed to create tables: {e}")
            raise
    
    def create_indexes(self):
        """Create performance indexes for HIPAA compliance"""
        try:
            with self.db_manager.engine.connect() as conn:
                # Patient indexes
                conn.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_patients_patient_id 
                    ON patients(patient_id);
                """))
                
                conn.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_patients_active 
                    ON patients(is_active);
                """))
                
                # Booking indexes
                conn.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_bookings_patient_id 
                    ON bookings(patient_id);
                """))
                
                conn.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_bookings_booking_id 
                    ON bookings(booking_id);
                """))
                
                conn.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_bookings_travel_date 
                    ON bookings(travel_date);
                """))
                
                # Audit log indexes
                conn.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_audit_logs_patient_id 
                    ON audit_logs(patient_id);
                """))
                
                conn.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_audit_logs_timestamp 
                    ON audit_logs(timestamp);
                """))
                
                conn.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_audit_logs_action 
                    ON audit_logs(action);
                """))
                
                # Device token indexes
                conn.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_device_tokens_patient_id 
                    ON device_tokens(patient_id);
                """))
                
                conn.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_device_tokens_active 
                    ON device_tokens(is_active);
                """))
                
                conn.commit()
                logger.info("✅ Database indexes created successfully")
        
        except Exception as e:
            logger.error(f"❌ Failed to create indexes: {e}")
            raise
    
    def setup_hipaa_compliance(self):
        """Set up HIPAA compliance features"""
        try:
            with self.db_manager.engine.connect() as conn:
                # Enable row-level security (if supported)
                try:
                    conn.execute(text("""
                        ALTER TABLE patients ENABLE ROW LEVEL SECURITY;
                    """))
                    
                    conn.execute(text("""
                        ALTER TABLE bookings ENABLE ROW LEVEL SECURITY;
                    """))
                    
                    conn.execute(text("""
                        ALTER TABLE audit_logs ENABLE ROW LEVEL SECURITY;
                    """))
                    
                    logger.info("✅ Row-level security enabled")
                
                except SQLAlchemyError:
                    logger.warning("⚠️ Row-level security not supported by database")
                
                # Create audit trigger function (PostgreSQL)
                if "postgresql" in self.database_url:
                    try:
                        conn.execute(text("""
                            CREATE OR REPLACE FUNCTION audit_trigger_function()
                            RETURNS TRIGGER AS $$
                            BEGIN
                                INSERT INTO audit_logs (
                                    patient_id, booking_id, action, resource_type,
                                    old_values, new_values, timestamp
                                ) VALUES (
                                    COALESCE(NEW.patient_id, OLD.patient_id),
                                    COALESCE(NEW.id, OLD.id),
                                    TG_OP,
                                    TG_TABLE_NAME,
                                    CASE WHEN TG_OP = 'DELETE' THEN row_to_json(OLD) ELSE NULL END,
                                    CASE WHEN TG_OP != 'DELETE' THEN row_to_json(NEW) ELSE NULL END,
                                    NOW()
                                );
                                RETURN COALESCE(NEW, OLD);
                            END;
                            $$ LANGUAGE plpgsql;
                        """))
                        
                        # Create audit triggers
                        conn.execute(text("""
                            DROP TRIGGER IF EXISTS audit_trigger_patients ON patients;
                            CREATE TRIGGER audit_trigger_patients
                                AFTER INSERT OR UPDATE OR DELETE ON patients
                                FOR EACH ROW EXECUTE FUNCTION audit_trigger_function();
                        """))
                        
                        conn.execute(text("""
                            DROP TRIGGER IF EXISTS audit_trigger_bookings ON bookings;
                            CREATE TRIGGER audit_trigger_bookings
                                AFTER INSERT OR UPDATE OR DELETE ON bookings
                                FOR EACH ROW EXECUTE FUNCTION audit_trigger_function();
                        """))
                        
                        logger.info("✅ Audit triggers created")
                    
                    except SQLAlchemyError as e:
                        logger.warning(f"⚠️ Audit triggers not created: {e}")
                
                conn.commit()
                logger.info("✅ HIPAA compliance features configured")
        
        except Exception as e:
            logger.error(f"❌ Failed to setup HIPAA compliance: {e}")
            raise
    
    def run_full_migration(self):
        """Run complete database migration"""
        logger.info("🚀 Starting HIPAA-compliant database migration...")
        
        try:
            # Step 1: Create database
            self.create_database()
            
            # Step 2: Create tables
            self.create_tables()
            
            # Step 3: Create indexes
            self.create_indexes()
            
            # Step 4: Setup HIPAA compliance
            self.setup_hipaa_compliance()
            
            logger.info("🎉 Database migration completed successfully!")
            
        except Exception as e:
            logger.error(f"❌ Database migration failed: {e}")
            raise

def main():
    """Main migration function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Guardian HIPAA Database Migration")
    parser.add_argument("--database-url", help="Database connection URL")
    parser.add_argument("--create-db", action="store_true", help="Create database")
    parser.add_argument("--create-tables", action="store_true", help="Create tables")
    parser.add_argument("--create-indexes", action="store_true", help="Create indexes")
    parser.add_argument("--setup-hipaa", action="store_true", help="Setup HIPAA compliance")
    parser.add_argument("--full", action="store_true", help="Run full migration")
    
    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    try:
        migration = DatabaseMigration(args.database_url)
        
        if args.full:
            migration.run_full_migration()
        else:
            if args.create_db:
                migration.create_database()
            if args.create_tables:
                migration.create_tables()
            if args.create_indexes:
                migration.create_indexes()
            if args.setup_hipaa:
                migration.setup_hipaa_compliance()
    
    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
