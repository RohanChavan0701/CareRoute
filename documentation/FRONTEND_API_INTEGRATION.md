# Guardian Medical Tourism Orchestrator - Frontend Integration Guide

## 🚀 **Base URL**
```
http://your-ec2-ip:8000  (or localhost:8000 for testing)
```

## 📋 **API Endpoints Overview**

### 1. **Booking Creation** - Main Entry Point
### 2. **Voice Integration** - Patient Support Calls  
### 3. **Trip Management** - Status & Updates
### 4. **Push Notifications** - FCM Integration
### 5. **Health & Status** - System Monitoring

---

## 📝 **1. BOOKING CREATION**

### **Endpoint:** `POST /api/booking`
**Purpose:** Create a new medical tourism booking and start complete orchestration

### **Request Format:**
```json
{
  "user_id": "string (required)",
  "booking_id": "string (required)", 
  "patient_id": "string (required)",
  
  // Patient Information
  "patient_name": "string (required)",
  "first_name": "string (required)",
  "last_name": "string (required)", 
  "date_of_birth": "YYYY-MM-DD (required)",
  "patient_language": "string (optional, default: 'English')",
  "age": "integer (optional)",
  
  // Contact Information
  "email": "string (required for notifications)",
  "emergency_contact": "string (optional)",
  
  // Medical Information
  "medical_conditions": ["condition1", "condition2"] (optional),
  "special_requirements": "string (optional)",
  
  // Companion Information
  "companion_name": "string (optional)",
  
  // Flight Information
  "flight_number": "string (required)",
  "flight_date": "YYYY-MM-DD (required)",
  "flight_time": "HH:MM (optional)",
  "departure_airport": "string (required)",
  "arrival_airport": "string (required)",
  
  // Hotel Information
  "hotel_name": "string (optional)",
  "hotel_booking_reference": "string (optional)",
  "hotel_check_in": "YYYY-MM-DD (optional)",
  "hotel_check_out": "YYYY-MM-DD (optional)",
  "hotel_room_number": "string (optional)",
  
  // Medical Appointments
  "hospital_name": "string (optional)",
  "doctor_name": "string (optional)",
  "appointment_date": "YYYY-MM-DD (optional)",
  "appointment_time": "HH:MM (optional)",
  "appointment_id": "string (optional)",
  
  // Travel Dates
  "travel_date": "YYYY-MM-DD (required)",
  "return_date": "YYYY-MM-DD (optional)",
  
  // Discharge Information
  "expected_discharge_date": "YYYY-MM-DD (optional)",
  "discharge_status": "string (optional, default: 'Pending')",
  
  // Transportation
  "pickup_time": "YYYY-MM-DDTHH:MM (optional)",
  "shuttle_driver": "string (optional)"
}
```

### **Example Request:**
```json
{
  "user_id": "patient_001",
  "booking_id": "BOOK_2025_001",
  "patient_id": "PAT_001",
  
  "patient_name": "John Doe",
  "first_name": "John",
  "last_name": "Doe",
  "date_of_birth": "1975-03-15",
  "patient_language": "English",
  "age": 49,
  
  "email": "john.doe@email.com",
  "emergency_contact": "+1234567890",
  
  "medical_conditions": ["Diabetes Type 2", "Hypertension"],
  "special_requirements": "Wheelchair accessible room, diabetic meals",
  
  "companion_name": "Jane Doe",
  
  "flight_number": "AA100",
  "flight_date": "2025-10-14",
  "flight_time": "14:30",
  "departure_airport": "JFK",
  "arrival_airport": "LAX",
  
  "hotel_name": "Seaside Recovery Resort",
  "hotel_booking_reference": "HOTEL_REF_123",
  "hotel_check_in": "2025-10-14",
  "hotel_check_out": "2025-10-21",
  
  "hospital_name": "Los Angeles Medical Center",
  "doctor_name": "Dr. Smith",
  "appointment_date": "2025-10-15",
  "appointment_time": "09:00",
  
  "travel_date": "2025-10-14",
  "return_date": "2025-10-21",
  "expected_discharge_date": "2025-10-20"
}
```

### **Response Format:**
```json
{
  "status": "success",
  "message": "Booking created and orchestration started",
  "orchestration_id": "ORCH_PAT_001_20251012_143033",
  "booking_id": "BOOK_2025_001",
  "user_id": "patient_001",
  "result": {
    "status": "success",
    "booking_id": "BOOK_2025_001",
    "flight_id": "FLIGHT_123",
    "orchestration_id": "ORCH_PAT_001_20251012_143033",
    "message": "Booking created successfully. You will receive flight updates 7 hours before departure."
  }
}
```

---

## 📞 **2. VOICE INTEGRATION**

### **Endpoint:** `POST /guardian/voice/call`
**Purpose:** Trigger voice call with complete patient context to voice agent

### **Request Format:**
```json
{
  "user_id": "string (required)",
  "content": "string (required - call reason/context)"
}
```

### **Example Request:**
```json
{
  "user_id": "patient_001",
  "content": "I need help with my trip schedule"
}
```

### **Response Format:**
```json
{
  "status": "success",
  "data": {
    "message": "Voice call initiated with complete patient context",
    "context_sent": true,
    "voice_agent_response": {
      "jsonrpc": "2.0",
      "result": null,
      "error": null,
      "id": null
    }
  },
  "timestamp": "2025-10-12T14:36:50.668678"
}
```

---

## 📱 **3. TRIP MANAGEMENT**

### **Endpoint:** `GET /guardian/trip/status/{user_id}`
**Purpose:** Get complete trip status and progress

### **Response Format:**
```json
{
  "status": "success",
  "data": {
    "user_id": "patient_001",
    "bookings": [
      {
        "booking_id": "BOOK_2025_001",
        "patient_name": "John Doe",
        "flight_number": "AA100",
        "hotel_name": "Seaside Recovery Resort",
        "hospital_name": "Los Angeles Medical Center",
        "booking_status": "Confirmed"
      }
    ],
    "flights": [
      {
        "flight_number": "AA100",
        "departure_date": "2025-10-14",
        "status": "On Time",
        "departure_airport": "JFK",
        "arrival_airport": "LAX"
      }
    ],
    "current_location": {
      "user_id": "patient_001",
      "location": "Unknown",
      "timestamp": "2025-10-12T14:36:19.257717",
      "source": "database_service"
    },
    "orchestration_status": "active",
    "flow_step": "flight_monitoring",
    "last_updated": "2025-10-12T14:36:19.257777",
    "adaptive_stay": {
      "status": "planned",
      "initial_estimate_days": 7,
      "extended": false,
      "flexible_booking": true,
      "extension_capability": true,
      "auto_rebooking": true,
      "family_notifications": true
    }
  },
  "timestamp": "2025-10-12T14:36:19.257777"
}
```

### **Endpoint:** `GET /guardian/scheduler/status`
**Purpose:** Get background job status and scheduled tasks

### **Response Format:**
```json
{
  "status": "success",
  "data": {
    "is_running": true,
    "jobs": [
      {
        "id": "arrival_monitoring",
        "name": "Monitor Arrivals",
        "next_run": "2025-10-12T14:44:33.091711+00:00",
        "trigger": "interval[0:10:00]"
      },
      {
        "id": "flight_status_updates",
        "name": "Update Flight Statuses",
        "next_run": "2025-10-12T14:49:33.091588+00:00",
        "trigger": "interval[0:15:00]"
      }
    ],
    "timestamp": "2025-10-12T14:36:19.266645"
  },
  "timestamp": "2025-10-12T14:36:19.266666"
}
```

---

## 🔔 **4. PUSH NOTIFICATIONS (FCM)**

### **Endpoint:** `POST /fcm/register`
**Purpose:** Register device for push notifications

### **Request Format:**
```json
{
  "user_id": "string (required)",
  "device_token": "string (required)"
}
```

### **Example Request:**
```json
{
  "user_id": "patient_001",
  "device_token": "fcm_device_token_123456789"
}
```

### **Response Format:**
```json
{
  "status": "success",
  "message": "FCM token registered successfully",
  "user_id": "patient_001"
}
```

### **Available FCM Endpoints:**
- `POST /fcm/send-boarding-reminder` - Send boarding reminders
- `POST /fcm/send-flight-update` - Send flight status updates  
- `POST /fcm/send-cab-notification` - Send cab arrival notifications
- `POST /fcm/send-appointment-reminder` - Send appointment reminders

---

## 🏥 **5. HEALTH & STATUS**

### **Endpoint:** `GET /health`
**Purpose:** System health check

### **Response Format:**
```json
{
  "status": "healthy",
  "protocol": "REST-API",
  "version": "1.0.0",
  "agent_id": "guardian_orchestrator",
  "timestamp": "2025-10-12T14:35:33.840414",
  "capabilities": [
    "orchestration",
    "real_time_events", 
    "voice_interaction",
    "schedule_management"
  ]
}
```

### **Endpoint:** `GET /`
**Purpose:** Root endpoint

### **Response Format:**
```json
{
  "message": "Guardian Medical Tourism Orchestrator",
  "status": "running"
}
```

---

## 🔄 **AUTOMATED WORKFLOWS**

### **What Happens After Booking Creation:**

1. **Immediate (0-5 seconds):**
   - Booking saved to HIPAA-compliant database
   - Orchestration workflow started
   - Confirmation email sent
   - FCM device registered

2. **Background Processing (5-30 seconds):**
   - Accessibility assessment initiated
   - Flight monitoring started
   - Hotel/hospital confirmation requests sent
   - Family notifications sent

3. **Scheduled Tasks:**
   - **7 hours before flight:** Reminder notifications
   - **2 hours before flight:** Boarding reminders
   - **Flight departure:** Real-time status updates
   - **Flight arrival:** Hotel/hospital coordination
   - **Daily:** Treatment updates and status checks

---

## 🚨 **ERROR HANDLING**

### **Common Error Responses:**
```json
{
  "detail": "Field required: user_id"
}
```

```json
{
  "detail": "Failed to create booking: Database connection error"
}
```

### **HTTP Status Codes:**
- `200` - Success
- `400` - Bad Request (missing required fields)
- `404` - Not Found (invalid endpoint)
- `500` - Internal Server Error

---

## 🔐 **SECURITY & COMPLIANCE**

- **HIPAA Compliant:** All patient data encrypted at rest
- **Audit Logging:** All data access tracked
- **CORS Enabled:** Frontend integration ready
- **Input Validation:** All requests validated
- **Error Handling:** Graceful error responses

---

## 📱 **FRONTEND INTEGRATION CHECKLIST**

- [ ] Register FCM device token after user login
- [ ] Create booking form with all required fields
- [ ] Implement voice call button with user_id
- [ ] Add trip status display page
- [ ] Handle push notifications for real-time updates
- [ ] Add error handling for all API calls
- [ ] Implement loading states for async operations

---

## 🧪 **TESTING**

### **Test Booking Creation:**
```bash
curl -X POST http://localhost:8000/api/booking \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user_001",
    "booking_id": "TEST_BOOKING_001",
    "patient_id": "TEST_PATIENT_001",
    "patient_name": "Test Patient",
    "first_name": "Test",
    "last_name": "Patient",
    "date_of_birth": "1980-01-01",
    "email": "test@example.com",
    "flight_number": "AA100",
    "flight_date": "2025-10-14",
    "departure_airport": "JFK",
    "arrival_airport": "LAX",
    "travel_date": "2025-10-14"
  }'
```

### **Test Voice Call:**
```bash
curl -X POST http://localhost:8000/guardian/voice/call \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user_001",
    "content": "I need help with my trip"
  }'
```

---

## 📞 **SUPPORT**

For technical questions or issues:
- Check health endpoint: `GET /health`
- Review system logs via scheduler status: `GET /guardian/scheduler/status`
- Verify trip status: `GET /guardian/trip/status/{user_id}`

---

**Ready for integration! 🚀**

