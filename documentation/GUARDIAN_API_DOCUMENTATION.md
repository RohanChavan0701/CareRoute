# Guardian Orchestrator API Documentation

## Overview

The Guardian Orchestrator is a FastAPI-based backend service that provides A2A (Agent-to-Agent) orchestration for medical tourism, AG-UI protocol support for frontend communication, and comprehensive trip management capabilities.

**Base URL**: `http://your-ec2-ip:8000`

---

## 🔍 Health & Status Endpoints

### GET `/ag-ui/health`
**Description**: Health check endpoint following AG-UI protocol

**Response**:
```json
{
  "status": "healthy",
  "protocol": "AG-UI",
  "version": "1.0.0",
  "agent_id": "guardian_orchestrator",
  "timestamp": "2025-10-11T23:09:23.717060",
  "capabilities": [
    "orchestration",
    "knowledge_query", 
    "real_time_events",
    "voice_interaction",
    "schedule_management"
  ]
}
```

### GET `/guardian/scheduler/status`
**Description**: Get scheduler status and job information

**Response**:
```json
{
  "status": "running",
  "jobs": [
    {
      "id": "check_flight_reminders",
      "next_run_time": "2025-10-12T06:00:00Z",
      "trigger": "interval[0:30:00]"
    }
  ],
  "active_orchestrations": 5
}
```

---

## 💬 AG-UI Communication Endpoints

### POST `/ag-ui/message`
**Description**: Handle user messages following AG-UI protocol

**Request Body**:
```json
{
  "message": "What's my flight status?",
  "user_id": "user123",
  "session_id": "session456",
  "context": {},
  "message_type": "text"
}
```

**Response**:
```json
{
  "response": "Your flight AA100 is on time and scheduled to depart at 2:00 PM",
  "user_id": "user123",
  "session_id": "session456",
  "timestamp": "2025-10-11T23:09:23.717060",
  "events_emitted": 2
}
```

### GET `/ag-ui/events/{user_id}`
**Description**: Get AG-UI events for a user

**Parameters**:
- `user_id` (path): User identifier
- `limit` (query, optional): Number of events to return (default: 20)

**Response**:
```json
{
  "events": [
    {
      "type": "agent_message",
      "timestamp": "2025-10-11T23:09:23.717060",
      "data": {"message": "Flight status updated"},
      "user_id": "user123",
      "agent_id": "guardian_orchestrator"
    }
  ],
  "count": 1,
  "user_id": "user123"
}
```

### GET `/ag-ui/stream/{user_id}`
**Description**: Stream AG-UI events using Server-Sent Events

**Response**: Continuous stream of events in SSE format
```
data: {"type": "agent_message", "data": {...}}
data: {"type": "state_update", "data": {...}}
```

---

## 🏥 Trip Management Endpoints

### POST `/guardian/booking/create`
**Description**: Create a new booking and start orchestration

**Request Body**:
```json
{
  "user_id": "user123",
  "patient_name": "John Doe",
  "flight_number": "AA100",
  "flight_date": "2025-10-15",
  "departure_airport": "JFK",
  "arrival_airport": "LAX",
  "hotel_name": "Grand Plaza Hotel",
  "hospital_name": "Cedars-Sinai Medical Center",
  "patient_email": "john@example.com",
  "patient_phone": "+1234567890",
  "companion_name": "Jane Doe",
  "special_requirements": "Wheelchair assistance"
}
```

**Response**:
```json
{
  "booking_id": "BK_12345",
  "orchestration_id": "ORCH_67890",
  "status": "created",
  "message": "Booking created and orchestration started",
  "events_emitted": 3
}
```

### GET `/guardian/trip/status/{user_id}`
**Description**: Get comprehensive trip status for user

**Parameters**:
- `user_id` (path): User identifier

**Response**:
```json
{
  "user_id": "user123",
  "booking_status": "confirmed",
  "flight_status": {
    "flight_number": "AA100",
    "status": "on_time",
    "gate": "B12",
    "terminal": "8"
  },
  "hotel_status": {
    "name": "Grand Plaza Hotel",
    "check_in": "2025-10-15T15:00:00Z",
    "status": "confirmed"
  },
  "hospital_status": {
    "name": "Cedars-Sinai Medical Center",
    "appointment_date": "2025-10-16T10:00:00Z",
    "status": "confirmed"
  },
  "adaptive_stay": {
    "status": "planned",
    "expected_discharge": "2025-10-20",
    "flexible": true
  }
}
```

### POST `/guardian/location/update`
**Description**: Update user location and handle arrival detection

**Request Body**:
```json
{
  "user_id": "user123",
  "latitude": 34.0522,
  "longitude": -118.2437,
  "airport_name": "LAX"
}
```

**Response**:
```json
{
  "status": "arrival_detected",
  "actions_triggered": [
    "hotel_notification",
    "cab_arrangement",
    "family_notification"
  ],
  "message": "Arrival detected at LAX. Hotel and cab arrangements initiated."
}
```

### POST `/guardian/cab/arrival`
**Description**: Handle cab arrival notification and trigger voice call

**Request Body**:
```json
{
  "user_id": "user123",
  "gate": "B12",
  "pickup_location": "Terminal 8, Gate B12",
  "estimated_arrival": "5 minutes"
}
```

**Response**:
```json
{
  "status": "voice_call_initiated",
  "call_context": {
    "patient_name": "John Doe",
    "gate": "B12",
    "pickup_time": "5 minutes",
    "hotel_name": "Grand Plaza Hotel"
  },
  "message": "Voice call initiated to inform patient of cab arrival"
}
```

---

## ✈️ Flight Management

### POST `/guardian/flight/check-reminders`
**Description**: Check if user needs flight reminders (7 hours before departure)

**Request Body**:
```json
{
  "user_id": "user123"
}
```

**Response**:
```json
{
  "reminder_sent": true,
  "flight_details": {
    "flight_number": "AA100",
    "departure_time": "2025-10-15T14:00:00Z",
    "hours_until_departure": 6.5
  },
  "message": "Flight reminder sent to user"
}
```

---

## 🏥 Adaptive Stay Management

### POST `/guardian/stay/extension`
**Description**: Handle hospital stay extension - the core adaptive feature

**Request Body**:
```json
{
  "user_id": "user123",
  "new_discharge_date": "2025-10-25",
  "reason": "Extended recovery needed",
  "extension_days": 5
}
```

**Response**:
```json
{
  "status": "extension_processed",
  "actions_taken": [
    "hotel_booking_extended",
    "family_notified",
    "flight_recommendations_updated"
  ],
  "new_timeline": {
    "original_discharge": "2025-10-20",
    "new_discharge": "2025-10-25",
    "extension_days": 5
  },
  "message": "Stay extension processed successfully"
}
```

### GET `/guardian/stay/timeline/{user_id}`
**Description**: Get adaptive timeline view for the frontend

**Parameters**:
- `user_id` (path): User identifier

**Response**:
```json
{
  "user_id": "user123",
  "timeline": [
    {
      "date": "2025-10-15",
      "event": "arrival",
      "status": "completed",
      "details": "Arrived at LAX, checked into hotel"
    },
    {
      "date": "2025-10-16", 
      "event": "hospital_appointment",
      "status": "scheduled",
      "details": "Consultation at Cedars-Sinai"
    },
    {
      "date": "2025-10-20",
      "event": "original_discharge",
      "status": "cancelled",
      "details": "Extended due to recovery needs"
    },
    {
      "date": "2025-10-25",
      "event": "new_discharge", 
      "status": "planned",
      "details": "Updated discharge date"
    }
  ],
  "adaptive_status": "extended",
  "flexibility_score": 0.8
}
```

### POST `/guardian/treatment/check-updates`
**Description**: Manually trigger treatment update check

**Request Body**:
```json
{
  "user_id": "user123"
}
```

**Response**:
```json
{
  "status": "checked",
  "updates_found": true,
  "changes": [
    {
      "type": "discharge_date_change",
      "old_value": "2025-10-20",
      "new_value": "2025-10-25"
    }
  ],
  "message": "Treatment updates checked. Stay extension processed."
}
```

---

## 🔄 Legacy Orchestration Endpoints

### POST `/guardian/booking`
**Description**: Start Guardian booking orchestration with AG-UI events (legacy)

**Request Body**:
```json
{
  "user_id": "user123",
  "patient_name": "John Doe",
  "patient_email": "john@example.com",
  "flight_number": "AA100",
  "flight_date": "2025-10-15",
  "departure_airport": "JFK",
  "arrival_airport": "LAX"
}
```

### GET `/guardian/status/{user_id}`
**Description**: Get Guardian orchestration status for a user (legacy)

**Response**:
```json
{
  "user_id": "user123",
  "orchestration_id": "ORCH_67890",
  "status": "active",
  "tasks_completed": 3,
  "total_tasks": 5,
  "last_update": "2025-10-11T23:09:23.717060"
}
```

---

## 📡 Event Types

The Guardian Orchestrator emits various AG-UI events:

### Core Events
- `agent_start` - Agent initialization
- `agent_end` - Agent completion
- `agent_error` - Error occurred
- `agent_thinking` - Agent processing

### User Interaction Events
- `user_message` - User sent message
- `agent_message` - Agent response
- `user_action` - User performed action
- `agent_action` - Agent performed action

### Guardian-Specific Events
- `orchestration_started` - Orchestration began
- `orchestration_completed` - Orchestration finished
- `flight_status_update` - Flight status changed
- `hotel_confirmed` - Hotel booking confirmed
- `hospital_confirmed` - Hospital appointment confirmed
- `notification_sent` - Notification delivered
- `voice_call_initiated` - Voice call started
- `accessibility_arranged` - Accessibility services arranged
- `knowledge_query_response` - Knowledge base response
- `incoming_call` - Incoming voice call
- `call_context_shared` - Context shared with voice agent

---

## 🚨 Error Handling

All endpoints return appropriate HTTP status codes:

- `200` - Success
- `400` - Bad Request (invalid input)
- `404` - Not Found (user/resource not found)
- `500` - Internal Server Error

Error responses follow this format:
```json
{
  "detail": "Error description",
  "error_code": "VALIDATION_ERROR",
  "timestamp": "2025-10-11T23:09:23.717060"
}
```

---

## 🔧 Development Notes

### Authentication
Currently, the API does not implement authentication. In production, you should add:
- JWT tokens
- API keys
- Rate limiting

### HIPAA Compliance
- All patient data is encrypted at rest
- Audit logging is enabled
- Data retention policies are enforced
- No PHI is logged in plain text

### A2A Protocol
The orchestrator communicates with external agents using JSON-RPC 2.0:
- Flight Agent: `http://54.158.27.0:8001/a2a`
- Notification Agent: `https://notification-system-h36d.onrender.com/a2a/tasks`
- Hotel/Hospital/Voice Agents: Configurable endpoints

### Rate Limiting
Consider implementing rate limiting for production:
- Per-user limits
- Per-endpoint limits
- IP-based throttling

---

## 📝 Example Usage

### Complete Trip Flow
```bash
# 1. Create booking
curl -X POST http://localhost:8000/guardian/booking/create \
  -H "Content-Type: application/json" \
  -d '{"user_id": "user123", "patient_name": "John Doe", ...}'

# 2. Check trip status
curl http://localhost:8000/guardian/trip/status/user123

# 3. Update location (arrival)
curl -X POST http://localhost:8000/guardian/location/update \
  -H "Content-Type: application/json" \
  -d '{"user_id": "user123", "latitude": 34.0522, "longitude": -118.2437}'

# 4. Handle cab arrival
curl -X POST http://localhost:8000/guardian/cab/arrival \
  -H "Content-Type: application/json" \
  -d '{"user_id": "user123", "gate": "B12", "pickup_location": "Terminal 8"}'

# 5. Extend stay if needed
curl -X POST http://localhost:8000/guardian/stay/extension \
  -H "Content-Type: application/json" \
  -d '{"user_id": "user123", "new_discharge_date": "2025-10-25"}'
```

This documentation provides a complete reference for frontend developers and other team members working with the Guardian Orchestrator API.
