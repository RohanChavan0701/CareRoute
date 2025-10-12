"""
HIPAA-Compliant Audit Logging Service
Provides comprehensive audit trails for all data access and modifications
"""

import json
from datetime import datetime
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc
import logging

from .models import AuditLog, Patient, Booking
from .encryption import get_encryption_service

logger = logging.getLogger(__name__)

class HIPAAAuditService:
    """
    HIPAA-compliant audit logging service
    Tracks all access and modifications to PHI (Protected Health Information)
    """
    
    def __init__(self, db_session: Session):
        self.db_session = db_session
    
    def log_patient_access(
        self, 
        patient_id: str, 
        action: str, 
        user_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        old_values: Optional[Dict] = None,
        new_values: Optional[Dict] = None
    ):
        """
        Log patient data access
        
        Args:
            patient_id: Patient identifier
            action: Action performed (CREATE, READ, UPDATE, DELETE)
            user_id: User/system performing the action
            ip_address: IP address of the request
            user_agent: User agent string
            old_values: Previous values (for updates)
            new_values: New values (for creates/updates)
        """
        try:
            # Encrypt sensitive data before logging
            encrypted_old = self._encrypt_audit_data(old_values) if old_values else None
            encrypted_new = self._encrypt_audit_data(new_values) if new_values else None
            
            audit_entry = AuditLog(
                patient_id=patient_id,
                action=action,
                resource_type="patient",
                user_id=user_id,
                ip_address=ip_address,
                user_agent=user_agent,
                old_values=encrypted_old,
                new_values=encrypted_new
            )
            
            self.db_session.add(audit_entry)
            self.db_session.commit()
            
            logger.info(f"📝 Audit log created: {action} patient {patient_id} by {user_id}")
        
        except Exception as e:
            logger.error(f"❌ Failed to log patient access: {e}")
            self.db_session.rollback()
            raise
    
    def log_booking_access(
        self,
        booking_id: str,
        action: str,
        user_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        old_values: Optional[Dict] = None,
        new_values: Optional[Dict] = None
    ):
        """
        Log booking data access
        
        Args:
            booking_id: Booking identifier
            action: Action performed
            user_id: User/system performing the action
            ip_address: IP address of the request
            user_agent: User agent string
            old_values: Previous values (for updates)
            new_values: New values (for creates/updates)
        """
        try:
            # Encrypt sensitive data before logging
            encrypted_old = self._encrypt_audit_data(old_values) if old_values else None
            encrypted_new = self._encrypt_audit_data(new_values) if new_values else None
            
            audit_entry = AuditLog(
                booking_id=booking_id,
                action=action,
                resource_type="booking",
                user_id=user_id,
                ip_address=ip_address,
                user_agent=user_agent,
                old_values=encrypted_old,
                new_values=encrypted_new
            )
            
            self.db_session.add(audit_entry)
            self.db_session.commit()
            
            logger.info(f"📝 Audit log created: {action} booking {booking_id} by {user_id}")
        
        except Exception as e:
            logger.error(f"❌ Failed to log booking access: {e}")
            self.db_session.rollback()
            raise
    
    def log_system_access(
        self,
        action: str,
        resource_type: str,
        user_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        details: Optional[Dict] = None
    ):
        """
        Log system-level access
        
        Args:
            action: Action performed
            resource_type: Type of resource accessed
            user_id: User/system performing the action
            ip_address: IP address of the request
            user_agent: User agent string
            details: Additional details
        """
        try:
            encrypted_details = self._encrypt_audit_data(details) if details else None
            
            audit_entry = AuditLog(
                action=action,
                resource_type=resource_type,
                user_id=user_id,
                ip_address=ip_address,
                user_agent=user_agent,
                new_values=encrypted_details
            )
            
            self.db_session.add(audit_entry)
            self.db_session.commit()
            
            logger.info(f"📝 System audit log created: {action} {resource_type} by {user_id}")
        
        except Exception as e:
            logger.error(f"❌ Failed to log system access: {e}")
            self.db_session.rollback()
            raise
    
    def get_audit_logs(
        self,
        patient_id: Optional[str] = None,
        booking_id: Optional[str] = None,
        action: Optional[str] = None,
        resource_type: Optional[str] = None,
        user_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Retrieve audit logs with filtering
        
        Args:
            patient_id: Filter by patient ID
            booking_id: Filter by booking ID
            action: Filter by action type
            resource_type: Filter by resource type
            user_id: Filter by user ID
            start_date: Filter by start date
            end_date: Filter by end date
            limit: Maximum number of records to return
            
        Returns:
            List of audit log records
        """
        try:
            query = self.db_session.query(AuditLog)
            
            # Apply filters
            if patient_id:
                query = query.filter(AuditLog.patient_id == patient_id)
            if booking_id:
                query = query.filter(AuditLog.booking_id == booking_id)
            if action:
                query = query.filter(AuditLog.action == action)
            if resource_type:
                query = query.filter(AuditLog.resource_type == resource_type)
            if user_id:
                query = query.filter(AuditLog.user_id == user_id)
            if start_date:
                query = query.filter(AuditLog.timestamp >= start_date)
            if end_date:
                query = query.filter(AuditLog.timestamp <= end_date)
            
            # Order by timestamp (most recent first) and limit
            query = query.order_by(desc(AuditLog.timestamp)).limit(limit)
            
            audit_logs = query.all()
            
            # Decrypt sensitive data and format response
            result = []
            for log in audit_logs:
                log_dict = {
                    "id": str(log.id),
                    "patient_id": str(log.patient_id) if log.patient_id else None,
                    "booking_id": str(log.booking_id) if log.booking_id else None,
                    "action": log.action,
                    "resource_type": log.resource_type,
                    "user_id": log.user_id,
                    "ip_address": log.ip_address,
                    "timestamp": log.timestamp.isoformat()
                }
                
                # Decrypt sensitive values if present
                encryption = get_encryption_service()
                if log.old_values:
                    try:
                        log_dict["old_values"] = encryption.decrypt_data(log.old_values)
                    except:
                        log_dict["old_values"] = "Encrypted data (decryption failed)"
                
                if log.new_values:
                    try:
                        log_dict["new_values"] = encryption.decrypt_data(log.new_values)
                    except:
                        log_dict["new_values"] = "Encrypted data (decryption failed)"
                
                result.append(log_dict)
            
            logger.info(f"📋 Retrieved {len(result)} audit logs")
            return result
        
        except Exception as e:
            logger.error(f"❌ Failed to retrieve audit logs: {e}")
            raise
    
    def _encrypt_audit_data(self, data: Dict[str, Any]) -> str:
        """
        Encrypt sensitive audit data
        
        Args:
            data: Data to encrypt
            
        Returns:
            Encrypted data as string
        """
        try:
            encryption = get_encryption_service()
            return encryption.encrypt_data(data)
        except Exception as e:
            logger.error(f"❌ Failed to encrypt audit data: {e}")
            return json.dumps({"error": "Encryption failed", "timestamp": datetime.utcnow().isoformat()})
    
    def generate_compliance_report(
        self,
        start_date: datetime,
        end_date: datetime,
        patient_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate HIPAA compliance report
        
        Args:
            start_date: Report start date
            end_date: Report end date
            patient_id: Optional patient filter
            
        Returns:
            Compliance report data
        """
        try:
            logs = self.get_audit_logs(
                patient_id=patient_id,
                start_date=start_date,
                end_date=end_date,
                limit=10000  # Large limit for report
            )
            
            # Analyze logs
            total_accesses = len(logs)
            access_by_user = {}
            access_by_action = {}
            access_by_resource = {}
            
            for log in logs:
                # Count by user
                user = log.get("user_id", "Unknown")
                access_by_user[user] = access_by_user.get(user, 0) + 1
                
                # Count by action
                action = log.get("action", "Unknown")
                access_by_action[action] = access_by_action.get(action, 0) + 1
                
                # Count by resource
                resource = log.get("resource_type", "Unknown")
                access_by_resource[resource] = access_by_resource.get(resource, 0) + 1
            
            report = {
                "report_period": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat()
                },
                "summary": {
                    "total_accesses": total_accesses,
                    "unique_users": len(access_by_user),
                    "unique_patients_accessed": len(set(log["patient_id"] for log in logs if log.get("patient_id")))
                },
                "access_by_user": access_by_user,
                "access_by_action": access_by_action,
                "access_by_resource": access_by_resource,
                "generated_at": datetime.utcnow().isoformat()
            }
            
            logger.info(f"📊 Generated compliance report: {total_accesses} total accesses")
            return report
        
        except Exception as e:
            logger.error(f"❌ Failed to generate compliance report: {e}")
            raise

def create_audit_service(db_session: Session) -> HIPAAAuditService:
    """
    Create audit service instance
    
    Args:
        db_session: Database session
        
    Returns:
        Audit service instance
    """
    return HIPAAAuditService(db_session)
