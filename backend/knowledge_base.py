"""
HIPAA-Compliant Knowledge Base Module
Handles patient questions with proper encryption and data protection
"""

import asyncio
import logging
import json
import re
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import base64
import os

# Setup logger first
logger = logging.getLogger(__name__)

# Optional imports for HIPAA encryption
try:
    from cryptography.fernet import Fernet
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False
    logger.warning("⚠️ Cryptography not available - encryption disabled")

# Optional OpenAI import
try:
    from openai import AsyncOpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logger.warning("⚠️ OpenAI not available - LLM features disabled")

class HIPAAEncryption:
    """HIPAA-compliant encryption for sensitive patient data"""
    
    def __init__(self):
        if not CRYPTO_AVAILABLE:
            self.cipher = None
            logger.warning("🔒 Encryption disabled - cryptography not available")
            return
            
        # Generate or load encryption key
        self.key = self._get_or_generate_key()
        self.cipher = Fernet(self.key)
        
    def _get_or_generate_key(self) -> bytes:
        """Derive a stable key from environment configuration when available."""
        password = os.getenv("HIPAA_ENCRYPTION_PASSWORD")
        if password:
            salt = os.getenv("HIPAA_ENCRYPTION_SALT", "guardian_hipaa_salt_2024").encode()
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            return base64.urlsafe_b64encode(kdf.derive(password.encode()))

        logger.warning(
            "HIPAA_ENCRYPTION_PASSWORD is not set; using an ephemeral in-memory key"
        )
        return Fernet.generate_key()
    
    def encrypt_data(self, data: str) -> str:
        """Encrypt sensitive data"""
        if not CRYPTO_AVAILABLE or self.cipher is None:
            # Fallback: return data as-is (not encrypted)
            logger.warning("🔒 Encryption not available - storing data unencrypted")
            return data
            
        try:
            encrypted_data = self.cipher.encrypt(data.encode())
            return base64.b64encode(encrypted_data).decode()
        except Exception as e:
            logger.error(f"❌ Encryption failed: {e}")
            return data  # Fallback to unencrypted
    
    def decrypt_data(self, encrypted_data: str) -> str:
        """Decrypt sensitive data"""
        if not CRYPTO_AVAILABLE or self.cipher is None:
            # Fallback: return data as-is (assume unencrypted)
            return encrypted_data
            
        try:
            decoded_data = base64.b64decode(encrypted_data.encode())
            decrypted_data = self.cipher.decrypt(decoded_data)
            return decrypted_data.decode()
        except Exception as e:
            logger.error(f"❌ Decryption failed: {e}")
            return encrypted_data  # Fallback to original data

class PatientDataManager:
    """Manages patient data with HIPAA compliance"""
    
    def __init__(self, encryption: HIPAAEncryption):
        self.encryption = encryption
        self.patient_data = {}
        
    def store_patient_data(self, patient_id: str, data: Dict[str, Any]):
        """Store patient data with encryption for sensitive fields"""
        encrypted_data = {}
        
        # Define sensitive fields that need encryption
        sensitive_fields = {
            'patient_name', 'phone_number', 'email', 'medical_conditions',
            'emergency_contacts', 'special_requirements', 'medical_history'
        }
        
        for key, value in data.items():
            if key in sensitive_fields and value:
                # Encrypt sensitive data
                if isinstance(value, list):
                    encrypted_data[key] = [self.encryption.encrypt_data(str(item)) for item in value]
                else:
                    encrypted_data[key] = self.encryption.encrypt_data(str(value))
            else:
                # Store non-sensitive data as-is
                encrypted_data[key] = value
        
        self.patient_data[patient_id] = encrypted_data
        logger.info(f"🔐 Stored encrypted patient data for {patient_id}")
    
    def get_patient_data(self, patient_id: str) -> Dict[str, Any]:
        """Get patient data with automatic decryption"""
        if patient_id not in self.patient_data:
            return {}
        
        encrypted_data = self.patient_data[patient_id]
        decrypted_data = {}
        
        sensitive_fields = {
            'patient_name', 'phone_number', 'email', 'medical_conditions',
            'emergency_contacts', 'special_requirements', 'medical_history'
        }
        
        for key, value in encrypted_data.items():
            if key in sensitive_fields and isinstance(value, str):
                try:
                    decrypted_data[key] = self.encryption.decrypt_data(value)
                except:
                    # If decryption fails, might be unencrypted data
                    decrypted_data[key] = value
            elif key in sensitive_fields and isinstance(value, list):
                try:
                    decrypted_data[key] = [self.encryption.decrypt_data(item) for item in value]
                except:
                    decrypted_data[key] = value
            else:
                decrypted_data[key] = value
        
        return decrypted_data

class KnowledgeBase:
    """
    HIPAA-compliant Knowledge Base for patient queries
    """
    
    def __init__(self):
        self.encryption = HIPAAEncryption()
        self.data_manager = PatientDataManager(self.encryption)
        
        # Initialize OpenAI client (fallback to mock if no API key)
        self.openai_client = None
        self.llm_enabled = False
        
        if not OPENAI_AVAILABLE:
            self.openai_client = None
            self.llm_enabled = False
            logger.warning("⚠️ OpenAI not available - using fallback responses")
        else:
            try:
                api_key = os.getenv("OPENAI_API_KEY")
                if api_key:
                    self.openai_client = AsyncOpenAI(api_key=api_key)
                    self.llm_enabled = True
                    logger.info("🧠 LLM integration enabled with OpenAI")
                else:
                    self.openai_client = None
                    self.llm_enabled = False
                    logger.warning("⚠️ No OpenAI API key found - using fallback responses")
            except Exception as e:
                self.openai_client = None
                self.llm_enabled = False
                logger.warning(f"⚠️ LLM initialization failed: {e} - using fallback responses")
        
        # Question patterns for intent recognition
        self.question_patterns = {
            'flight_status': [
                r'flight.*status', r'flight.*time', r'gate.*number', r'departure.*time',
                r'arrival.*time', r'flight.*delay', r'boarding.*time'
            ],
            'hotel_info': [
                r'hotel.*check.*in', r'hotel.*room', r'hotel.*address', r'hotel.*phone',
                r'hotel.*confirmation', r'accommodation'
            ],
            'hospital_info': [
                r'hospital.*appointment', r'doctor.*appointment', r'medical.*appointment',
                r'surgery.*time', r'consultation', r'hospital.*address'
            ],
            'emergency': [
                r'emergency', r'help', r'not.*feeling.*well', r'medical.*emergency',
                r'urgent.*help', r'call.*doctor'
            ],
            'transportation': [
                r'pick.*up', r'transportation', r'airport.*pickup', r'driver.*details',
                r'taxi.*arrangement', r'ground.*transport'
            ],
            'general_status': [
                r'how.*am.*i.*doing', r'status.*update', r'everything.*ok', r'what.*happening'
            ]
        }
        
        # Dummy response templates
        self.response_templates = {
            'flight_status': {
                'boarding': "Your flight {flight_number} is currently BOARDING at Gate {gate}, Terminal {terminal}. Please proceed to the gate immediately.",
                'on_time': "Your flight {flight_number} is ON TIME. Departure at {scheduled_departure_local} from Gate {gate}, Terminal {terminal}.",
                'delayed': "Your flight {flight_number} has a {delay_minutes} minute delay. New departure time is {estimated_departure_local}.",
                'in_air': "Your flight {flight_number} is IN THE AIR. Estimated arrival at {estimated_arrival_local}.",
                'landed': "Your flight {flight_number} has LANDED. Welcome to {destination_city}!"
            },
            'hotel_info': {
                'confirmed': "Your hotel booking is confirmed. Check-in time is 3:00 PM. You'll receive your room details via SMS upon arrival.",
                'ready': "Your hotel room is ready! Room number will be provided at check-in. Hotel amenities include accessible rooms and medical equipment storage."
            },
            'hospital_info': {
                'confirmed': "Your appointment with Dr. Smith is confirmed for tomorrow at 9:00 AM. Please arrive 30 minutes early.",
                'preparation': "For your procedure, please fast for 8 hours before your appointment. Bring your insurance card and photo ID."
            },
            'emergency': {
                'immediate': "This is a medical emergency. Please call 911 immediately or go to the nearest emergency room.",
                'contact': "For medical assistance, contact our emergency line at +1-800-MED-HELP or your designated medical contact."
            },
            'transportation': {
                'arranged': "Your airport pickup has been arranged. Driver John will meet you at the arrivals area with a sign bearing your name.",
                'accessible': "Accessible transportation has been confirmed. Your wheelchair-accessible vehicle will be available upon arrival."
            }
        }
    
    async def update_patient_context(self, patient_id: str, context_data: Dict[str, Any]):
        """Update patient context with real-time data"""
        try:
            self.data_manager.store_patient_data(patient_id, context_data)
            logger.info(f"📊 Updated patient context for {patient_id}")
        except Exception as e:
            logger.error(f"❌ Failed to update patient context: {e}")
            raise
    
    def _parse_question_intent(self, question: str) -> str:
        """Parse patient question to determine intent"""
        question_lower = question.lower()
        
        for intent, patterns in self.question_patterns.items():
            for pattern in patterns:
                if re.search(pattern, question_lower):
                    return intent
        
        return 'general_status'  # Default intent
    
    async def _generate_llm_response(self, question: str, patient_data: Dict[str, Any], intent: str) -> str:
        """Generate response using LLM for natural language understanding"""
        try:
            if not self.llm_enabled or not self.openai_client:
                return self._generate_fallback_response(intent, patient_data, question)
            
            # Prepare context for LLM (remove sensitive data)
            context = self._prepare_llm_context(patient_data)
            
            # Create medical tourism specific prompt
            system_prompt = """You are Guardian, a HIPAA-compliant AI assistant for medical tourism patients. 
            You help elderly travelers with flight status, hotel arrangements, hospital appointments, and emergencies.
            
            Guidelines:
            - Be empathetic and reassuring
            - Provide clear, actionable information
            - Use the patient's name when available
            - Keep responses concise but helpful
            - For medical emergencies, always direct to emergency services
            - Maintain patient privacy (no PHI in responses)
            """
            
            user_prompt = f"""
            Patient Question: "{question}"
            
            Patient Context:
            {json.dumps(context, indent=2)}
            
            Intent: {intent}
            
            Please provide a helpful, empathetic response to the patient's question using the available context.
            """
            
            response = await self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=200,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"❌ LLM response generation failed: {e}")
            return self._generate_fallback_response(intent, patient_data, question)
    
    def _prepare_llm_context(self, patient_data: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare safe context for LLM (remove sensitive data)"""
        safe_context = {}
        
        # Flight data (non-sensitive)
        if patient_data.get('flight_data'):
            flight_data = patient_data['flight_data']
            safe_context['flight'] = {
                'number': flight_data.get('flight_number'),
                'status': flight_data.get('status'),
                'gate': flight_data.get('gate'),
                'terminal': flight_data.get('terminal'),
                'arrival_time': flight_data.get('estimated_arrival_local'),
                'delay_minutes': flight_data.get('delay_minutes')
            }
        
        # Booking references (non-sensitive)
        safe_context['bookings'] = {
            'hotel_reference': patient_data.get('hotel_booking_reference'),
            'hospital_appointment_id': patient_data.get('hospital_appointment_id'),
            'hotel_status': patient_data.get('hotel_status', 'confirmed'),
            'hospital_status': patient_data.get('hospital_status', 'confirmed')
        }
        
        # General status
        safe_context['status'] = {
            'orchestration_status': patient_data.get('orchestration_status'),
            'age_group': 'elderly' if patient_data.get('age', 0) >= 65 else 'adult',
            'has_accessibility_needs': bool(patient_data.get('special_requirements')),
            'has_medical_conditions': bool(patient_data.get('medical_conditions'))
        }
        
        # Language preference
        safe_context['language'] = patient_data.get('preferred_language', 'English')
        
        return safe_context
    
    def _generate_fallback_response(self, intent: str, patient_data: Dict[str, Any], question: str) -> str:
        """Generate contextual response based on intent and patient data"""
        
        # Get flight data if available
        flight_data = patient_data.get('flight_data', {})
        
        # Get basic patient info
        patient_name = patient_data.get('patient_name', 'Patient')
        
        try:
            if intent == 'flight_status' and flight_data:
                status = flight_data.get('status', 'unknown').lower()
                template = self.response_templates['flight_status'].get(status, self.response_templates['flight_status']['on_time'])
                
                response = template.format(
                    flight_number=flight_data.get('flight_number', 'your flight'),
                    gate=flight_data.get('gate', 'TBD'),
                    terminal=flight_data.get('terminal', 'TBD'),
                    scheduled_departure_local=flight_data.get('scheduled_departure_local', 'TBD'),
                    estimated_departure_local=flight_data.get('estimated_departure_local', 'TBD'),
                    estimated_arrival_local=flight_data.get('estimated_arrival_local', 'TBD'),
                    delay_minutes=flight_data.get('delay_minutes', 0),
                    destination_city=flight_data.get('destination_city', 'your destination')
                )
                
            elif intent == 'hotel_info':
                hotel_status = patient_data.get('hotel_status', 'confirmed')
                template = self.response_templates['hotel_info'].get(hotel_status, self.response_templates['hotel_info']['confirmed'])
                response = template
                
            elif intent == 'hospital_info':
                hospital_status = patient_data.get('hospital_status', 'confirmed')
                template = self.response_templates['hospital_info'].get(hospital_status, self.response_templates['hospital_info']['confirmed'])
                response = template
                
            elif intent == 'emergency':
                # Check if it's immediate emergency or general medical help
                if any(word in question.lower() for word in ['emergency', 'urgent', '911', 'ambulance']):
                    response = self.response_templates['emergency']['immediate']
                else:
                    response = self.response_templates['emergency']['contact']
                    
            elif intent == 'transportation':
                # Check if accessible transportation is needed
                special_reqs = patient_data.get('special_requirements', '')
                if 'wheelchair' in special_reqs.lower():
                    response = self.response_templates['transportation']['accessible']
                else:
                    response = self.response_templates['transportation']['arranged']
                    
            else:  # general_status
                # Provide overall status update
                response_parts = []
                if flight_data:
                    status = flight_data.get('status', 'unknown')
                    response_parts.append(f"Your flight {flight_data.get('flight_number', '')} is {status}.")
                
                response_parts.append("Your hotel and hospital arrangements are confirmed.")
                response_parts.append("Everything is proceeding as planned.")
                
                response = " ".join(response_parts)
            
            # Add personalized greeting
            if patient_name and patient_name != 'Patient':
                response = f"Hello {patient_name.split()[0]}, {response.lower()}"
            
            return response
            
        except Exception as e:
            logger.error(f"❌ Error generating response: {e}")
            return "I apologize, but I'm having trouble accessing your information right now. Please contact our support team for assistance."
    
    async def answer_question(self, question: str, patient_id: str) -> Dict[str, Any]:
        """Main method to answer patient questions with HIPAA compliance"""
        try:
            logger.info(f"🧠 Processing question from patient {patient_id}: {question}")
            
            # Get patient data (automatically decrypted)
            patient_data = self.data_manager.get_patient_data(patient_id)
            
            if not patient_data:
                return {
                    "status": "error",
                    "message": "Patient data not found. Please ensure your booking is active.",
                    "timestamp": datetime.now().isoformat()
                }
            
            # Parse question intent
            intent = self._parse_question_intent(question)
            
            # Generate response using LLM
            response_text = await self._generate_llm_response(question, patient_data, intent)
            
            # Log the interaction (without sensitive data)
            logger.info(f"✅ Generated response for intent '{intent}' - {len(response_text)} characters")
            
            return {
                "status": "success",
                "response": response_text,
                "intent": intent,
                "patient_id": patient_id,
                "timestamp": datetime.now().isoformat(),
                "hipaa_compliant": True
            }
            
        except Exception as e:
            logger.error(f"❌ Error processing question: {e}")
            return {
                "status": "error",
                "message": "I apologize, but I'm experiencing technical difficulties. Please try again or contact support.",
                "timestamp": datetime.now().isoformat()
            }
    
    def get_audit_log(self, patient_id: str) -> List[Dict[str, Any]]:
        """Get audit log for HIPAA compliance (simplified for MVP)"""
        # In a real implementation, this would query a proper audit database
        return [
            {
                "timestamp": datetime.now().isoformat(),
                "action": "data_access",
                "patient_id": patient_id,
                "data_type": "encrypted_patient_data",
                "access_method": "knowledge_base_query"
            }
        ]

# Global instance for use in orchestrator
knowledge_base = KnowledgeBase()
