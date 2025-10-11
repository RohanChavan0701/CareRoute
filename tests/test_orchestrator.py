"""
Test script for Guardian A2A Orchestrator
Demonstrates the orchestration capabilities
"""

import asyncio
import json
from orchestrator import guardian_orchestrator

async def test_multiple_orchestrations():
    """Test multiple orchestrations running in parallel"""
    
    # Sample booking data for multiple patients
    bookings = [
        {
            "patient_id": "P001",
            "patient_name": "John Doe",
            "flight_number": "AA1234",
            "flight_date": "2024-02-15",
            "flight_time": "14:30:00",
            "departure_airport": "JFK",
            "arrival_airport": "LAX",
            "hotel_booking_reference": "HOTEL_REF_001",
            "hospital_appointment_id": "MED_APPT_001",
            "hospital_appointment_time": "2024-02-16T09:00:00",
            "emergency_contacts": ["+1-555-0001"],
            "special_requirements": "Wheelchair accessible, Dietary restrictions",
            "medical_conditions": ["Diabetes", "Hypertension", "Arthritis"],
            "age": 72,
            "preferred_language": "English"
        },
        {
            "patient_id": "P002",
            "patient_name": "Jane Smith",
            "flight_number": "UA5678",
            "flight_date": "2024-02-20",
            "flight_time": "10:15:00",
            "departure_airport": "LAX",
            "arrival_airport": "MIA",
            "hotel_booking_reference": "HOTEL_REF_002",
            "hospital_appointment_id": "MED_APPT_002",
            "hospital_appointment_time": "2024-02-21T14:00:00",
            "emergency_contacts": ["+1-555-0002", "+1-555-0003"],
            "special_requirements": "Dietary restrictions, Visual impairment",
            "medical_conditions": ["Heart condition", "Diabetes"],
            "age": 68,
            "preferred_language": "Spanish"
        },
        {
            "patient_id": "P003",
            "patient_name": "Bob Wilson",
            "flight_number": "DL9012",
            "flight_date": "2024-02-25",
            "flight_time": "16:45:00",
            "departure_airport": "MIA",
            "arrival_airport": "SFO",
            "hotel_booking_reference": "HOTEL_REF_003",
            "hospital_appointment_id": "MED_APPT_003",
            "hospital_appointment_time": "2024-02-26T11:30:00",
            "emergency_contacts": ["+1-555-0004"],
            "special_requirements": "Mobility assistance",
            "medical_conditions": ["Arthritis"]
        }
    ]
    
    print("🧠 Starting Guardian A2A Orchestrator Test")
    print("=" * 60)
    
    # Start orchestrations for all patients
    orchestration_tasks = []
    for booking in bookings:
        task = guardian_orchestrator.start_orchestration(booking)
        orchestration_tasks.append(task)
    
    # Wait for all orchestrations to complete
    orchestration_ids = await asyncio.gather(*orchestration_tasks)
    
    print(f"\n✅ All orchestrations completed!")
    print(f"Orchestration IDs: {orchestration_ids}")
    
    # Check status of each orchestration
    print("\n📊 Orchestration Status Report:")
    print("-" * 60)
    
    for orchestration_id in orchestration_ids:
        status = await guardian_orchestrator.get_orchestration_status(orchestration_id)
        patient_id = status["patient_id"]
        flight_number = status["flight_number"]
        workflow_status = status["status"]
        coordination_results = status.get("coordination_results", {})
        
        print(f"Patient: {patient_id}")
        print(f"Flight: {flight_number}")
        print(f"Status: {workflow_status}")
        if coordination_results:
            successful = coordination_results["successful_tasks"]
            total = coordination_results["total_tasks"]
            print(f"Coordination: {successful}/{total} tasks successful")
        print("-" * 60)
    
    # Show all active orchestrations
    print("\n📋 All Active Orchestrations:")
    all_orchestrations = guardian_orchestrator.get_all_orchestrations()
    print(f"Total orchestrations: {len(all_orchestrations)}")
    
    for orchestration_id, orchestration in all_orchestrations.items():
        print(f"\nOrchestration ID: {orchestration_id}")
        print(f"Patient: {orchestration['patient_id']}")
        print(f"Flight: {orchestration['flight_number']}")
        print(f"Status: {orchestration['status']}")
        print(f"Started: {orchestration['started_at']}")
        
        # Show task results
        tasks = orchestration.get("tasks", {})
        if tasks:
            print("Task Results:")
            for task_name, task_result in tasks.items():
                agent = task_result["agent"]
                task_type = task_result["task"]
                print(f"  - {task_name}: {agent} -> {task_type} ✅")
    
    # Test agent health checks
    print("\n🏥 Agent Health Check:")
    print("-" * 60)
    
    for agent_id in guardian_orchestrator.agent_endpoints.keys():
        is_healthy = await guardian_orchestrator.check_agent_health(agent_id)
        status_icon = "✅" if is_healthy else "❌"
        print(f"{agent_id}: {status_icon} {'Healthy' if is_healthy else 'Unhealthy'}")
    
    print("\n🎉 Guardian A2A Orchestrator Test Completed Successfully!")
    print("=" * 60)

async def test_orchestration_details():
    """Test detailed orchestration functionality"""
    
    print("\n🔍 Testing Orchestration Details")
    print("-" * 60)
    
    # Get all orchestrations
    all_orchestrations = guardian_orchestrator.get_all_orchestrations()
    
    if not all_orchestrations:
        print("No orchestrations found. Run test_multiple_orchestrations() first.")
        return
    
    # Pick the first orchestration for detailed analysis
    orchestration_id = list(all_orchestrations.keys())[0]
    orchestration = all_orchestrations[orchestration_id]
    
    print(f"Analyzing orchestration: {orchestration_id}")
    print(f"Patient: {orchestration['patient_id']}")
    print(f"Flight: {orchestration['flight_number']}")
    print(f"Status: {orchestration['status']}")
    
    # Show detailed task breakdown
    tasks = orchestration.get("tasks", {})
    if tasks:
        print("\n📋 Task Breakdown:")
        for task_name, task_result in tasks.items():
            print(f"\n{task_name.upper()}:")
            print(f"  Agent: {task_result['agent']}")
            print(f"  Task: {task_result['task']}")
            print(f"  Timestamp: {task_result['timestamp']}")
            print(f"  Result: {task_result['result']['result']['status']}")
    
    # Show coordination results
    coordination_results = orchestration.get("coordination_results")
    if coordination_results:
        print(f"\n🎯 Coordination Results:")
        print(f"  Successful tasks: {coordination_results['successful_tasks']}")
        print(f"  Total tasks: {coordination_results['total_tasks']}")
        print(f"  Completed at: {coordination_results['completed_at']}")

if __name__ == "__main__":
    print("🚀 Guardian A2A Orchestrator Test Suite")
    print("=" * 60)
    
    # Run the tests
    asyncio.run(test_multiple_orchestrations())
    asyncio.run(test_orchestration_details())
