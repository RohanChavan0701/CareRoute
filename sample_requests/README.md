# Guardian Orchestrator - Agent Request Specifications

This directory contains the **input JSON requests** that the Guardian A2A Orchestrator will send to external agents, so agent development teams can build their services to handle these requests properly.

## 📁 Files Overview

### Request Files (Input to Agents)
### 1. `voice_agent_requests.json`
**Purpose**: Input requests for Voice Agent team  
**Contains**: A2A JSON-RPC 2.0 requests for voice communication tasks

### 2. `notification_agent_requests.json` 
**Purpose**: Input requests for Notification Agent team  
**Contains**: A2A JSON-RPC 2.0 requests for notification tasks

### Response Files (Output from Agents)
### 3. `../sample_responses/voice_agent_responses.json`
**Purpose**: Expected responses from Voice Agent team  
**Contains**: Sample A2A JSON-RPC 2.0 responses for voice communication tasks

### 4. `../sample_responses/notification_agent_responses.json`
**Purpose**: Expected responses from Notification Agent team  
**Contains**: Sample A2A JSON-RPC 2.0 responses for notification tasks

## 🎯 What Each Agent Team Needs to Build

### Voice Agent Requirements
The Voice Agent must implement these A2A methods:

1. **`InitiateCall`** - Standard coordination update calls
2. **`EmergencyCall`** - Emergency medical assistance calls  
3. **`FollowUpCall`** - Post-treatment follow-up calls
4. **`LanguageSupportCall`** - Calls with interpreter support
5. **`AccessibilityCall`** - Calls with accessibility features
6. **`FamilyNotificationCall`** - Calls to notify family members

**Key Features to Implement:**
- Twilio integration for actual voice calls
- Call transcription and recording
- Language interpreter services
- Accessibility features (TTS, volume control, speech rate)
- Emergency escalation procedures
- A2A JSON-RPC 2.0 response format

### Notification Agent Requirements
The Notification Agent must implement these A2A methods:

1. **`SendFamilyUpdate`** - Status updates to family members
2. **`SendEmergencyAlert`** - Emergency alerts to family and medical team
3. **`SendTreatmentReminder`** - Appointment and treatment reminders
4. **`SendAccessibilityUpdate`** - Accessibility services updates
5. **`SendLanguageNotification`** - Notifications in patient's preferred language
6. **`SendRecoveryUpdate`** - Post-treatment recovery updates

**Key Features to Implement:**
- Multi-channel delivery (SMS, Email, Push notifications)
- Language translation services
- Emergency notification escalation
- Delivery confirmation tracking
- HIPAA compliance for medical notifications
- Accessibility features for disabled patients

## 🔧 Technical Implementation Notes

### A2A Protocol Compliance
- **Protocol**: JSON-RPC 2.0 over HTTPS
- **Authentication**: A2A API tokens
- **Endpoint**: `/a2a/tasks`
- **Response Format**: Standard JSON-RPC 2.0 response/error format

### Error Handling
- Implement proper error codes (-32000 series for application errors)
- Provide detailed error information in `data` field
- Include retry availability and alternative methods
- Log all requests and responses for audit purposes

### Rate Limiting & Retry Logic
- Handle rate limiting with exponential backoff
- Implement retry logic with max 3 attempts
- Provide fallback delivery methods when primary fails

### Security & Compliance
- HIPAA compliance for medical data
- Encrypt sensitive information in transit
- Implement proper access controls
- Audit logging for all operations

## 📋 Sample Request Structure

```json
{
  "jsonrpc": "2.0",
  "id": "guardian_voice_001_20251011_102732",
  "method": "InitiateCall",
  "params": {
    "patient_id": "P001",
    "call_type": "coordination_update",
    "patient_phone": "+1-555-111-2222",
    "orchestration_id": "ORCH_P001_20251011_102732",
    "context": {
      "flight_number": "AA1234",
      "arrival_time": "2024-02-15T14:30:00Z"
    }
  }
}
```

## 📋 Sample Response Structure

```json
{
  "jsonrpc": "2.0",
  "id": "guardian_voice_001_20251011_102732",
  "result": {
    "status": "success",
    "call_id": "CALL_12345_ABC",
    "agent": "voice_agent",
    "task": "InitiateCall",
    "call_details": {
      "call_status": "completed",
      "call_duration": "00:03:45"
    },
    "timestamp": "2024-02-15T14:33:45Z"
  }
}
```

## 🚀 Next Steps for Agent Teams

1. **Review the request specifications** in the JSON files
2. **Implement the required A2A methods** for your agent
3. **Set up the required integrations** (Twilio, SMS providers, etc.)
4. **Implement error handling and retry logic**
5. **Add logging and monitoring** for production deployment
6. **Test with Guardian Orchestrator** using these request formats
7. **Deploy on AWS** with the specified endpoint URLs

## 📞 Support

For questions about these specifications, contact the Guardian Orchestrator team or refer to the A2A protocol documentation at https://github.com/a2aproject/A2A.
