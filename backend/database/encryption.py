"""
HIPAA-Compliant Encryption Service
Provides encryption/decryption for sensitive medical data
"""

import os
import base64
import json
from typing import Any, Dict, Optional
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import logging

logger = logging.getLogger(__name__)

class HIPAAEncryption:
    """
    HIPAA-compliant encryption service for sensitive medical data
    Uses AES-256 encryption with PBKDF2 key derivation
    """
    
    def __init__(self, password: Optional[str] = None):
        """
        Initialize encryption service
        
        Args:
            password: Encryption password (defaults to environment variable)
        """
        self.password = password or os.getenv("HIPAA_ENCRYPTION_PASSWORD")
        if not self.password:
            raise ValueError("HIPAA_ENCRYPTION_PASSWORD environment variable must be set")
        
        # Generate salt (in production, this should be stored securely)
        self.salt = os.getenv("HIPAA_ENCRYPTION_SALT", "guardian_hipaa_salt_2024").encode()
        
        # Derive encryption key
        self.key = self._derive_key(self.password, self.salt)
        self.fernet = Fernet(self.key)
    
    def _derive_key(self, password: str, salt: bytes) -> bytes:
        """Derive encryption key using PBKDF2"""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,  # High iteration count for security
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key
    
    def encrypt_data(self, data: Any) -> str:
        """
        Encrypt sensitive data
        
        Args:
            data: Data to encrypt (will be JSON serialized)
            
        Returns:
            Base64 encoded encrypted data
        """
        try:
            if isinstance(data, (dict, list)):
                json_data = json.dumps(data)
            else:
                json_data = str(data)
            
            encrypted_data = self.fernet.encrypt(json_data.encode())
            return base64.urlsafe_b64encode(encrypted_data).decode()
        
        except Exception as e:
            logger.error(f"❌ Encryption failed: {e}")
            raise ValueError(f"Failed to encrypt data: {e}")
    
    def decrypt_data(self, encrypted_data: str) -> Any:
        """
        Decrypt sensitive data
        
        Args:
            encrypted_data: Base64 encoded encrypted data
            
        Returns:
            Decrypted and deserialized data
        """
        try:
            # Decode base64
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_data.encode())
            
            # Decrypt
            decrypted_bytes = self.fernet.decrypt(encrypted_bytes)
            json_data = decrypted_bytes.decode()
            
            # Try to deserialize as JSON, fallback to string
            try:
                return json.loads(json_data)
            except json.JSONDecodeError:
                return json_data
        
        except Exception as e:
            logger.error(f"❌ Decryption failed: {e}")
            raise ValueError(f"Failed to decrypt data: {e}")
    
    def encrypt_patient_data(self, patient_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Encrypt sensitive patient data fields
        
        Args:
            patient_data: Patient data dictionary
            
        Returns:
            Patient data with encrypted sensitive fields
        """
        encrypted_data = patient_data.copy()
        
        # Fields that need encryption
        sensitive_fields = [
            'medical_conditions',
            'special_requirements',
            'emergency_contacts',
            'date_of_birth'  # Considered PHI
        ]
        
        for field in sensitive_fields:
            if field in encrypted_data and encrypted_data[field]:
                if field == 'emergency_contacts' and isinstance(encrypted_data[field], list):
                    # Encrypt each contact separately
                    encrypted_contacts = []
                    for contact in encrypted_data[field]:
                        if isinstance(contact, str):
                            encrypted_contacts.append(self.encrypt_data(contact))
                        else:
                            encrypted_contacts.append(self.encrypt_data(json.dumps(contact)))
                    encrypted_data[f"{field}_encrypted"] = json.dumps(encrypted_contacts)
                else:
                    encrypted_data[f"{field}_encrypted"] = self.encrypt_data(encrypted_data[field])
                
                # Remove original sensitive field
                del encrypted_data[field]
        
        return encrypted_data
    
    def decrypt_patient_data(self, encrypted_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Decrypt sensitive patient data fields
        
        Args:
            encrypted_data: Patient data with encrypted fields
            
        Returns:
            Patient data with decrypted sensitive fields
        """
        decrypted_data = encrypted_data.copy()
        
        # Fields that were encrypted
        encrypted_fields = [
            'medical_conditions_encrypted',
            'special_requirements_encrypted',
            'emergency_contacts_encrypted',
            'date_of_birth_encrypted'
        ]
        
        for encrypted_field in encrypted_fields:
            if encrypted_field in decrypted_data:
                # Determine original field name
                original_field = encrypted_field.replace('_encrypted', '')
                
                try:
                    if original_field == 'emergency_contacts':
                        # Decrypt each contact
                        encrypted_contacts = json.loads(decrypted_data[encrypted_field])
                        decrypted_contacts = []
                        for contact in encrypted_contacts:
                            decrypted_contact = self.decrypt_data(contact)
                            # Try to parse as JSON, fallback to string
                            try:
                                decrypted_contacts.append(json.loads(decrypted_contact))
                            except json.JSONDecodeError:
                                decrypted_contacts.append(decrypted_contact)
                        decrypted_data[original_field] = decrypted_contacts
                    else:
                        decrypted_data[original_field] = self.decrypt_data(decrypted_data[encrypted_field])
                    
                    # Remove encrypted field
                    del decrypted_data[encrypted_field]
                
                except Exception as e:
                    logger.error(f"❌ Failed to decrypt {encrypted_field}: {e}")
                    # Keep encrypted field if decryption fails
                    pass
        
        return decrypted_data

# Global encryption instance (will be initialized when needed)
hipaa_encryption = None

def get_encryption_service() -> HIPAAEncryption:
    """Get or create encryption service instance"""
    global hipaa_encryption
    if hipaa_encryption is None:
        hipaa_encryption = HIPAAEncryption()
    return hipaa_encryption
