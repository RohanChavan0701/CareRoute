"""
Simple test for Knowledge Base functionality
"""

import asyncio
import json
from knowledge_base import knowledge_base

async def test_knowledge_base_direct():
    """Test the knowledge base directly"""
    
    print("🧠 Testing Knowledge Base Directly")
    print("=" * 50)
    
    # Sample patient data
    patient_data = {
        "patient_id": "P001",
        "patient_name": "John Doe",
        "flight_data": {
            "flight_number": "WN123",
            "status": "BOARDING",
            "gate": "B22",
            "terminal": "3",
            "estimated_arrival_local": "2025-10-12T12:00"
        },
        "medical_conditions": ["Diabetes", "Hypertension"],
        "emergency_contacts": ["+1-555-111-2222"],
        "special_requirements": "Wheelchair accessible"
    }
    
    # Store patient data
    print("📊 Storing patient data...")
    await knowledge_base.update_patient_context("P001", patient_data)
    
    # Test questions
    test_questions = [
        "What's my flight status?",
        "What gate is my flight?",
        "Is my flight delayed?",
        "I don't feel well, who can I contact?",
        "What's my overall status?"
    ]
    
    print(f"\n🧠 Testing Knowledge Base Queries")
    print("=" * 50)
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n📝 Question {i}: {question}")
        
        try:
            response = await knowledge_base.answer_question(question, "P001")
            
            if response.get("status") == "success":
                print(f"✅ Response: {response['response']}")
                print(f"   Intent: {response.get('intent', 'unknown')}")
            else:
                print(f"❌ Error: {response.get('message', 'Unknown error')}")
                
        except Exception as e:
            print(f"❌ Exception: {e}")
    
    # Test data retrieval
    print(f"\n🔒 Testing Data Retrieval:")
    print("=" * 50)
    
    retrieved_data = knowledge_base.data_manager.get_patient_data("P001")
    print(f"✅ Patient name: {retrieved_data.get('patient_name', 'N/A')}")
    print(f"✅ Medical conditions: {retrieved_data.get('medical_conditions', [])}")
    print(f"✅ Flight data: {'Yes' if retrieved_data.get('flight_data') else 'No'}")
    
    if retrieved_data.get('flight_data'):
        flight_info = retrieved_data['flight_data']
        print(f"   Flight: {flight_info.get('flight_number')} - {flight_info.get('status')}")
        print(f"   Gate: {flight_info.get('gate')}, Terminal: {flight_info.get('terminal')}")

if __name__ == "__main__":
    asyncio.run(test_knowledge_base_direct())
