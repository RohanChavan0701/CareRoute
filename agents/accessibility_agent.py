"""
Accessibility Agent - A2A Agent for Medical Tourism Accessibility
Handles accessibility requirements, mobility assistance, and special needs coordination
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import json

logger = logging.getLogger(__name__)

class AccessibilityAgent:
    """
    A2A Accessibility Agent for Guardian Medical Tourism Orchestrator
    
    Provides accessibility services including:
    - Mobility assistance coordination
    - Special dietary requirements
    - Medical equipment transportation
    - Accessibility-friendly accommodation verification
    - Transportation accessibility coordination
    - Language/communication assistance
    """
    
    def __init__(self):
        self.agent_id = "accessibility_agent"
        self.capabilities = [
            "AssessAccessibilityNeeds",
            "CoordinateMobilityAssistance", 
            "ArrangeSpecialTransport",
            "VerifyAccessibleAccommodations",
            "CoordinateMedicalEquipment",
            "ArrangeLanguageSupport",
            "ProvideAccessibilityGuidance",
            "MonitorAccessibilityCompliance"
        ]
        self.active_requests = {}
        
        logger.info(f"🤝 Accessibility Agent {self.agent_id} initialized")
    
    async def handle_a2a_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle incoming A2A requests"""
        method = request.get("method")
        params = request.get("params", {})
        
        logger.info(f"🤝 Accessibility Agent received request: {method}")
        
        try:
            if method == "AssessAccessibilityNeeds":
                return await self.assess_accessibility_needs(params)
            elif method == "CoordinateMobilityAssistance":
                return await self.coordinate_mobility_assistance(params)
            elif method == "ArrangeSpecialTransport":
                return await self.arrange_special_transport(params)
            elif method == "VerifyAccessibleAccommodations":
                return await self.verify_accessible_accommodations(params)
            elif method == "CoordinateMedicalEquipment":
                return await self.coordinate_medical_equipment(params)
            elif method == "ArrangeLanguageSupport":
                return await self.arrange_language_support(params)
            elif method == "ProvideAccessibilityGuidance":
                return await self.provide_accessibility_guidance(params)
            elif method == "MonitorAccessibilityCompliance":
                return await self.monitor_accessibility_compliance(params)
            else:
                return {
                    "error": f"Unknown method: {method}",
                    "available_methods": self.capabilities
                }
        
        except Exception as e:
            logger.error(f"❌ Error in Accessibility Agent: {e}")
            return {
                "error": str(e),
                "status": "failed"
            }
    
    async def assess_accessibility_needs(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Assess patient's accessibility requirements"""
        patient_id = params.get("patient_id")
        medical_conditions = params.get("medical_conditions", [])
        special_requirements = params.get("special_requirements", "")
        age = params.get("age")
        
        logger.info(f"🔍 Assessing accessibility needs for patient {patient_id}")
        
        # Analyze accessibility requirements
        accessibility_needs = {
            "mobility_assistance": [],
            "dietary_requirements": [],
            "medical_equipment": [],
            "communication_needs": [],
            "transportation_needs": [],
            "accommodation_needs": []
        }
        
        # Mobility assessment
        if any(condition.lower() in ["diabetes", "hypertension", "arthritis", "stroke"] for condition in medical_conditions):
            accessibility_needs["mobility_assistance"].append("wheelchair_accessible")
            accessibility_needs["mobility_assistance"].append("elevator_access")
        
        if "wheelchair" in special_requirements.lower():
            accessibility_needs["mobility_assistance"].append("wheelchair_provided")
            accessibility_needs["transportation_needs"].append("wheelchair_accessible_vehicle")
        
        # Age-based considerations
        if age and age >= 70:
            accessibility_needs["mobility_assistance"].append("assistance_required")
            accessibility_needs["communication_needs"].append("clear_instructions")
        
        # Dietary requirements
        if "dietary" in special_requirements.lower():
            accessibility_needs["dietary_requirements"].append("special_meal_arrangements")
        
        # Medical equipment
        if any(condition.lower() in ["diabetes", "heart", "respiratory"] for condition in medical_conditions):
            accessibility_needs["medical_equipment"].append("medical_monitoring_available")
        
        assessment_result = {
            "patient_id": patient_id,
            "assessment_timestamp": datetime.now().isoformat(),
            "accessibility_needs": accessibility_needs,
            "risk_level": self._calculate_accessibility_risk(accessibility_needs),
            "recommendations": self._generate_recommendations(accessibility_needs),
            "status": "completed"
        }
        
        # Store assessment for future reference
        self.active_requests[patient_id] = assessment_result
        
        logger.info(f"✅ Accessibility assessment completed for patient {patient_id}")
        return assessment_result
    
    async def coordinate_mobility_assistance(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Coordinate mobility assistance services"""
        patient_id = params.get("patient_id")
        flight_number = params.get("flight_number")
        arrival_airport = params.get("arrival_airport")
        mobility_needs = params.get("mobility_needs", [])
        
        logger.info(f"♿ Coordinating mobility assistance for patient {patient_id}")
        
        assistance_coordination = {
            "patient_id": patient_id,
            "flight_number": flight_number,
            "airport": arrival_airport,
            "services_arranged": [],
            "provider_contacts": [],
            "estimated_costs": {},
            "timeline": {}
        }
        
        # Airport assistance
        if "wheelchair_accessible" in mobility_needs:
            assistance_coordination["services_arranged"].append("airport_wheelchair_service")
            assistance_coordination["provider_contacts"].append("airport_disability_services")
            assistance_coordination["timeline"]["airport_assistance"] = "on_arrival"
        
        # Ground transportation
        if "wheelchair_accessible_vehicle" in mobility_needs:
            assistance_coordination["services_arranged"].append("accessible_taxi_booking")
            assistance_coordination["provider_contacts"].append("accessible_transport_company")
            assistance_coordination["estimated_costs"]["transportation"] = "$50-100"
        
        # Hotel assistance
        if "elevator_access" in mobility_needs:
            assistance_coordination["services_arranged"].append("ground_floor_or_elevator_access")
            assistance_coordination["timeline"]["hotel_checkin"] = "priority_assistance"
        
        assistance_coordination["status"] = "coordinated"
        assistance_coordination["coordination_timestamp"] = datetime.now().isoformat()
        
        logger.info(f"✅ Mobility assistance coordinated for patient {patient_id}")
        return assistance_coordination
    
    async def arrange_special_transport(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Arrange special transportation services"""
        patient_id = params.get("patient_id")
        transport_type = params.get("transport_type", "general")
        accessibility_requirements = params.get("accessibility_requirements", [])
        
        logger.info(f"🚐 Arranging special transport for patient {patient_id}")
        
        transport_arrangement = {
            "patient_id": patient_id,
            "transport_type": transport_type,
            "requirements": accessibility_requirements,
            "arrangements": {},
            "backup_options": [],
            "estimated_duration": "30-45 minutes",
            "estimated_cost": "$75-150"
        }
        
        # Specialized transport options
        if "wheelchair_accessible_vehicle" in accessibility_requirements:
            transport_arrangement["arrangements"]["primary"] = {
                "vehicle_type": "wheelchair_accessible_van",
                "provider": "Accessible Transport Co.",
                "features": ["wheelchair_ramp", "safety_restraints", "medical_equipment_space"]
            }
            
            transport_arrangement["backup_options"].append({
                "vehicle_type": "accessible_sedan",
                "provider": "Medical Transport Services",
                "features": ["wheelchair_folding", "assistance_provided"]
            })
        
        # Medical transport
        if "medical_monitoring" in accessibility_requirements:
            transport_arrangement["arrangements"]["medical"] = {
                "vehicle_type": "medical_transport",
                "provider": "Medical Transport Specialists",
                "features": ["oxygen_support", "vital_monitoring", "trained_staff"]
            }
            transport_arrangement["estimated_cost"] = "$150-300"
        
        transport_arrangement["status"] = "arranged"
        transport_arrangement["arrangement_timestamp"] = datetime.now().isoformat()
        
        logger.info(f"✅ Special transport arranged for patient {patient_id}")
        return transport_arrangement
    
    async def verify_accessible_accommodations(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Verify hotel accommodations meet accessibility requirements"""
        patient_id = params.get("patient_id")
        hotel_booking_reference = params.get("hotel_booking_reference")
        accessibility_needs = params.get("accessibility_needs", {})
        
        logger.info(f"🏨 Verifying accessible accommodations for patient {patient_id}")
        
        accommodation_verification = {
            "patient_id": patient_id,
            "hotel_reference": hotel_booking_reference,
            "verification_status": "pending",
            "accessibility_features": {},
            "compliance_check": {},
            "recommendations": [],
            "alternative_options": []
        }
        
        # Check accessibility features
        required_features = accessibility_needs.get("accommodation_needs", [])
        
        # Simulate verification process
        verified_features = []
        missing_features = []
        
        for feature in required_features:
            if feature in ["wheelchair_accessible", "elevator_access", "ground_floor"]:
                verified_features.append(feature)
                accommodation_verification["compliance_check"][feature] = "verified"
            else:
                missing_features.append(feature)
                accommodation_verification["compliance_check"][feature] = "not_available"
        
        accommodation_verification["accessibility_features"] = {
            "verified": verified_features,
            "missing": missing_features,
            "available_amenities": [
                "wheelchair_accessible_rooms",
                "accessible_bathrooms", 
                "elevator_access",
                "ground_floor_options",
                "accessible_restaurant",
                "wheelchair_accessible_parking"
            ]
        }
        
        # Generate recommendations
        if missing_features:
            accommodation_verification["recommendations"].append("Contact hotel to arrange alternative accommodations")
            accommodation_verification["alternative_options"].append("Request room change to accessible room")
        
        accommodation_verification["status"] = "verified" if not missing_features else "requires_attention"
        accommodation_verification["verification_timestamp"] = datetime.now().isoformat()
        
        logger.info(f"✅ Accommodation verification completed for patient {patient_id}")
        return accommodation_verification
    
    async def coordinate_medical_equipment(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Coordinate medical equipment needs"""
        patient_id = params.get("patient_id")
        medical_conditions = params.get("medical_conditions", [])
        equipment_needs = params.get("equipment_needs", [])
        
        logger.info(f"🩺 Coordinating medical equipment for patient {patient_id}")
        
        equipment_coordination = {
            "patient_id": patient_id,
            "required_equipment": [],
            "rental_arrangements": {},
            "delivery_schedule": {},
            "backup_equipment": [],
            "estimated_costs": {}
        }
        
        # Determine equipment needs based on conditions
        for condition in medical_conditions:
            condition_lower = condition.lower()
            if "diabetes" in condition_lower:
                equipment_coordination["required_equipment"].append("glucose_monitor")
                equipment_coordination["required_equipment"].append("insulin_cooler")
            elif "heart" in condition_lower:
                equipment_coordination["required_equipment"].append("blood_pressure_monitor")
            elif "respiratory" in condition_lower:
                equipment_coordination["required_equipment"].append("portable_oxygen")
        
        # Add specific equipment needs
        equipment_coordination["required_equipment"].extend(equipment_needs)
        
        # Arrange equipment rental
        for equipment in equipment_coordination["required_equipment"]:
            equipment_coordination["rental_arrangements"][equipment] = {
                "provider": "Medical Equipment Rentals Inc.",
                "delivery_location": "hotel",
                "rental_period": "duration_of_stay",
                "setup_required": True
            }
            
            # Estimate costs
            if equipment == "glucose_monitor":
                equipment_coordination["estimated_costs"][equipment] = "$15/day"
            elif equipment == "portable_oxygen":
                equipment_coordination["estimated_costs"][equipment] = "$50/day"
            else:
                equipment_coordination["estimated_costs"][equipment] = "$25/day"
        
        # Schedule delivery
        equipment_coordination["delivery_schedule"] = {
            "delivery_date": "day_before_arrival",
            "delivery_time": "10:00 AM",
            "setup_time": "11:00 AM",
            "pickup_schedule": "day_after_departure"
        }
        
        equipment_coordination["status"] = "coordinated"
        equipment_coordination["coordination_timestamp"] = datetime.now().isoformat()
        
        logger.info(f"✅ Medical equipment coordinated for patient {patient_id}")
        return equipment_coordination
    
    async def arrange_language_support(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Arrange language and communication support"""
        patient_id = params.get("patient_id")
        preferred_language = params.get("preferred_language", "English")
        communication_needs = params.get("communication_needs", [])
        
        logger.info(f"🗣️ Arranging language support for patient {patient_id}")
        
        language_support = {
            "patient_id": patient_id,
            "preferred_language": preferred_language,
            "support_arrangements": {},
            "interpreter_services": [],
            "translation_services": [],
            "estimated_costs": {}
        }
        
        # Interpreter services
        if preferred_language != "English":
            language_support["interpreter_services"].append({
                "service_type": "medical_interpreter",
                "provider": "Global Language Services",
                "availability": "24/7",
                "specialization": "medical_terminology"
            })
            
            language_support["estimated_costs"]["interpreter"] = "$75/hour"
        
        # Communication assistance
        if "clear_instructions" in communication_needs:
            language_support["support_arrangements"]["communication"] = {
                "service": "simplified_communication",
                "provider": "Accessibility Services",
                "features": ["visual_aids", "written_instructions", "step_by_step_guidance"]
            }
        
        # Translation services
        language_support["translation_services"] = [
            {
                "service_type": "document_translation",
                "provider": "Medical Translation Co.",
                "documents": ["medical_records", "prescriptions", "instructions"]
            }
        ]
        
        language_support["estimated_costs"]["translation"] = "$50/document"
        language_support["status"] = "arranged"
        language_support["arrangement_timestamp"] = datetime.now().isoformat()
        
        logger.info(f"✅ Language support arranged for patient {patient_id}")
        return language_support
    
    async def provide_accessibility_guidance(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Provide accessibility guidance and recommendations"""
        patient_id = params.get("patient_id")
        destination = params.get("destination")
        accessibility_needs = params.get("accessibility_needs", {})
        
        logger.info(f"📋 Providing accessibility guidance for patient {patient_id}")
        
        guidance = {
            "patient_id": patient_id,
            "destination": destination,
            "guidance_categories": {},
            "travel_tips": [],
            "emergency_contacts": [],
            "accessibility_resources": [],
            "local_services": []
        }
        
        # General travel guidance
        guidance["travel_tips"] = [
            "Arrive at airport 2 hours early for assistance",
            "Carry medical documentation and prescriptions",
            "Inform airline of mobility equipment in advance",
            "Pack extra medication in carry-on luggage",
            "Bring accessibility equipment documentation"
        ]
        
        # Emergency contacts
        guidance["emergency_contacts"] = [
            {
                "service": "Accessibility Emergency Line",
                "number": "+1-800-ACCESS-01",
                "available": "24/7"
            },
            {
                "service": "Medical Equipment Emergency",
                "number": "+1-800-MED-EQUIP",
                "available": "24/7"
            }
        ]
        
        # Local accessibility resources
        guidance["accessibility_resources"] = [
            {
                "type": "accessibility_map",
                "description": "Interactive map of accessible locations",
                "url": "https://accessibility-maps.com/destination"
            },
            {
                "type": "local_accessibility_guide",
                "description": "Comprehensive accessibility guide for destination",
                "url": "https://accessibility-guides.com/destination"
            }
        ]
        
        # Category-specific guidance
        if "mobility_assistance" in accessibility_needs:
            guidance["guidance_categories"]["mobility"] = [
                "Wheelchair accessibility verified at all locations",
                "Elevator access confirmed at hotel and hospital",
                "Accessible transportation arranged",
                "Ground floor room requested"
            ]
        
        if "dietary_requirements" in accessibility_needs:
            guidance["guidance_categories"]["dietary"] = [
                "Special dietary requirements communicated to hotel",
                "Local restaurants with dietary options identified",
                "Emergency food options available"
            ]
        
        guidance["status"] = "provided"
        guidance["guidance_timestamp"] = datetime.now().isoformat()
        
        logger.info(f"✅ Accessibility guidance provided for patient {patient_id}")
        return guidance
    
    async def monitor_accessibility_compliance(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Monitor ongoing accessibility compliance during travel"""
        patient_id = params.get("patient_id")
        current_location = params.get("current_location")
        accessibility_requirements = params.get("accessibility_requirements", [])
        
        logger.info(f"👁️ Monitoring accessibility compliance for patient {patient_id}")
        
        compliance_monitoring = {
            "patient_id": patient_id,
            "current_location": current_location,
            "monitoring_timestamp": datetime.now().isoformat(),
            "compliance_status": {},
            "issues_detected": [],
            "resolutions": [],
            "next_check": (datetime.now() + timedelta(hours=2)).isoformat()
        }
        
        # Check compliance for each requirement
        for requirement in accessibility_requirements:
            # Simulate compliance check
            if requirement == "wheelchair_accessible":
                compliance_monitoring["compliance_status"][requirement] = "compliant"
            elif requirement == "medical_monitoring":
                compliance_monitoring["compliance_status"][requirement] = "compliant"
            else:
                compliance_monitoring["compliance_status"][requirement] = "compliant"
        
        # Check for any issues
        issues = []
        for requirement, status in compliance_monitoring["compliance_status"].items():
            if status != "compliant":
                issues.append({
                    "requirement": requirement,
                    "status": status,
                    "severity": "medium",
                    "action_required": True
                })
        
        compliance_monitoring["issues_detected"] = issues
        
        # Overall compliance score
        total_requirements = len(accessibility_requirements)
        compliant_requirements = sum(1 for status in compliance_monitoring["compliance_status"].values() if status == "compliant")
        compliance_score = (compliant_requirements / total_requirements * 100) if total_requirements > 0 else 100
        
        compliance_monitoring["overall_compliance_score"] = compliance_score
        compliance_monitoring["status"] = "monitored"
        
        logger.info(f"✅ Accessibility compliance monitored for patient {patient_id} - Score: {compliance_score}%")
        return compliance_monitoring
    
    def _calculate_accessibility_risk(self, accessibility_needs: Dict[str, Any]) -> str:
        """Calculate accessibility risk level"""
        total_needs = sum(len(needs) for needs in accessibility_needs.values())
        
        if total_needs >= 8:
            return "high"
        elif total_needs >= 4:
            return "medium"
        else:
            return "low"
    
    def _generate_recommendations(self, accessibility_needs: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on accessibility needs"""
        recommendations = []
        
        if accessibility_needs.get("mobility_assistance"):
            recommendations.append("Arrange wheelchair assistance at airport")
            recommendations.append("Book accessible ground transportation")
        
        if accessibility_needs.get("medical_equipment"):
            recommendations.append("Coordinate medical equipment rental")
            recommendations.append("Ensure hotel has medical equipment space")
        
        if accessibility_needs.get("communication_needs"):
            recommendations.append("Arrange language interpreter services")
            recommendations.append("Provide written instructions in preferred language")
        
        return recommendations

# Global instance for A2A communication
accessibility_agent = AccessibilityAgent()

async def main():
    """Test the Accessibility Agent"""
    print("🤝 Accessibility Agent Test Suite")
    print("=" * 50)
    
    # Test accessibility assessment
    test_params = {
        "patient_id": "P_ACCESS_001",
        "medical_conditions": ["Diabetes", "Arthritis"],
        "special_requirements": "Wheelchair accessible, Dietary restrictions",
        "age": 72
    }
    
    result = await accessibility_agent.handle_a2a_request({
        "method": "AssessAccessibilityNeeds",
        "params": test_params
    })
    
    print(f"✅ Accessibility Assessment Result:")
    print(f"   Risk Level: {result['risk_level']}")
    print(f"   Recommendations: {len(result['recommendations'])}")
    
    # Test mobility assistance coordination
    mobility_params = {
        "patient_id": "P_ACCESS_001",
        "flight_number": "AA1234",
        "arrival_airport": "LAX",
        "mobility_needs": ["wheelchair_accessible", "elevator_access"]
    }
    
    mobility_result = await accessibility_agent.handle_a2a_request({
        "method": "CoordinateMobilityAssistance",
        "params": mobility_params
    })
    
    print(f"✅ Mobility Assistance Coordinated:")
    print(f"   Services: {len(mobility_result['services_arranged'])}")
    print(f"   Status: {mobility_result['status']}")

if __name__ == "__main__":
    asyncio.run(main())
