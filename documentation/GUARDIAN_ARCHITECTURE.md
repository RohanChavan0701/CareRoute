# Guardian A2A Orchestrator - The Medical Tourism Brain 🧠

## Overview
Guardian is the **intelligent orchestrator** that coordinates medical tourism for elderly patients. We're the **brain** that receives inputs from the Flutter app and coordinates with external agent microservices.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Flutter App                              │
│              (Patient Booking Input)                        │
└─────────────────────┬───────────────────────────────────────┘
                      │ POST /flutter/patient-booking
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                Guardian Orchestrator                        │
│                     (The Brain)                             │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐  │
│  │   LangGraph     │  │   Scheduler     │  │  Flight     │  │
│  │   Workflow      │  │   Service       │  │  Tracker    │  │
│  └─────────────────┘  └─────────────────┘  └─────────────┘  │
└─────────────────────┬───────────────────────────────────────┘
                      │ A2A Protocol (JSON-RPC 2.0)
                      ▼
      ┌───────────────┬───────────────┐
      │               │               │
┌─────▼───────┐ ┌─────▼───────┐ ┌─────▼─────┐
│   Voice     │ │Notification │ │  Flight   │
│   Agent     │ │   Agent     │ │   Agent   │
│             │ │             │ │           │
│ - Twilio    │ │ - SMS       │ │ - Track   │
│ - OpenAI    │ │ - Email     │ │   Flight  │
│ - Calls     │ │ - Push      │ │ - ETA     │
│ - Real-time │ │ - FCM       │ │ - Status  │
│ - Alerts    │ │ - Family    │ │ - Delays  │
└─────────────┘ └─────────────┘ └───────────┘
```

## Guardian Brain Workflow

### 1. **Input from Flutter App**
```json
POST /flutter/patient-booking
{
  "patient_id": "P123456",
  "patient_name": "John Doe",
  "flight_number": "AA1234",
  "flight_date": "2024-02-15",
  "flight_time": "14:30:00",
  "departure_airport": "JFK",
  "arrival_airport": "LAX",
  "hotel_booking_reference": "HOTEL_REF_123",
  "hospital_appointment_id": "MED_APPT_456",
  "hospital_appointment_time": "2024-02-16T09:00:00",
  "emergency_contacts": ["+1-555-FAMILY"],
  "special_requirements": "Wheelchair accessible",
  "medical_conditions": ["Diabetes", "Hypertension"]
}
```

### 2. **Guardian Brain Activates** 🧠
- Stores patient booking data
- Starts flight tracking
- Adds to monitoring system
- Calculates coordination trigger time

### 3. **Flight Monitoring** ✈️
- Continuously tracks flight status
- Monitors ETA and delays
- Updates patient status

### 4. **Coordination Trigger** ⚡
**When flight ETA < 6 hours, Guardian Brain triggers:**

#### Hotel Agent Coordination:
```json
{
  "method": "ConfirmHotel",
  "params": {
    "agent_id": "hotel_agent",
    "payload": {
      "flight_number": "AA1234",
      "passenger_id": "P123456",
      "hotel_booking_reference": "HOTEL_REF_123",
      "eta": "2024-02-15T20:30:00Z",
      "special_requirements": "Wheelchair accessible"
    }
  }
}
```

#### Hospital Agent Coordination:
```json
{
  "method": "ConfirmHospital",
  "params": {
    "agent_id": "hospital_agent", 
    "payload": {
      "flight_number": "AA1234",
      "passenger_id": "P123456",
      "hospital_appointment_id": "MED_APPT_456",
      "eta": "2024-02-15T20:30:00Z",
      "medical_conditions": ["Diabetes", "Hypertension"]
    }
  }
}
```

#### Notification Agent:
```json
{
  "method": "SendFamilyUpdate",
  "params": {
    "agent_id": "notification_agent",
    "payload": {
      "flight_number": "AA1234",
      "passenger_id": "P123456", 
      "status": "coordination_started",
      "family_contacts": ["+1-555-FAMILY"]
    }
  }
}
```

#### Voice Agent:
```json
{
  "method": "InitiateCall",
  "params": {
    "agent_id": "voice_agent",
    "payload": {
      "phone_number": "+1-555-PATIENT",
      "call_type": "information",
      "message": "Guardian coordination update for flight AA1234"
    }
  }
}
```

## Key Features

### 🧠 **Guardian as The Brain**
- **Intelligent Orchestration**: Coordinates all external agents
- **A2A Protocol Compliance**: Uses real Agent-to-Agent communication
- **Automatic Triggering**: Monitors flight ETA and triggers coordination
- **Error Handling**: Manages agent failures and retries

### 🏥 **HIPAA-Conscious Design**
- **Opaque Agents**: Each service maintains its own data
- **Secure Communication**: A2A protocol with authentication
- **Audit Logging**: Complete trail of all actions
- **No PHI Exposure**: Only reference IDs in logs

### ☁️ **AWS Cloud Ready**
- **ECS Fargate Deployment**: Serverless container deployment
- **Auto-scaling**: Handles multiple patients simultaneously
- **Health Monitoring**: CloudWatch integration
- **Secret Management**: AWS Secrets Manager for API keys

## API Endpoints

### **Main Flutter Integration**
- `POST /flutter/patient-booking` - Create new patient booking and start monitoring

### **Guardian Control**
- `GET /health` - System health and agent status
- `POST /guardian/run` - Manual workflow trigger
- `GET /guardian/status/{flight_number}` - Get workflow status
- `POST /guardian/cancel/{flight_number}` - Cancel workflow

### **A2A Protocol**
- `POST /a2a/receive` - Receive A2A messages from agents
- `POST /a2a/tasks` - Handle A2A task requests
- `GET /a2a/agents` - List registered agents

## Deployment

### **Local Development**
```bash
# Start Guardian orchestrator only
docker-compose up guardian-orchestrator

# Other agents will be provided by other teams
```

### **AWS Production**
```bash
# Deploy to ECS Fargate
./aws/deploy.sh
```

## What Makes Guardian Special

1. **True A2A Implementation**: One of the first real-world A2A protocol implementations
2. **Healthcare Scenario**: Models medical-travel coordination without claiming regulatory compliance
3. **Service Boundaries**: Each external agent is deployed and configured separately
4. **Intelligent Coordination**: Automatic triggering based on flight ETA
5. **Flutter Integration**: Seamless mobile app integration
6. **AWS Native**: Built for cloud-scale deployment

## Guardian Brain Logic

```python
# When Flutter app sends patient booking:
1. Store booking data
2. Start flight tracking
3. Monitor continuously

# When flight ETA < 6 hours:
1. Trigger hotel agent confirmation
2. Trigger hospital agent confirmation  
3. Send family notifications
4. Initiate voice calls
5. Monitor all responses
6. Handle any failures/retries

# Guardian is the conductor of this medical tourism orchestra! 🎼
```

Guardian is not just a service - it's the **intelligent brain** that makes medical tourism seamless and safe for elderly patients! 🧠✨
