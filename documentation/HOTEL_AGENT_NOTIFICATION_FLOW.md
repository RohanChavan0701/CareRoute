# 🏨 Hotel Agent Notification Flow

## 🎯 Overview

The **Hotel Agent** is responsible for handling all notifications related to patient arrival, hotel services, and family communication when patients land at their destination airport. This creates a seamless experience where families are immediately informed and hotels are prepared for guest arrival.

## 🚀 Hotel Agent Responsibilities

### **📧 Family Notifications**
- **Flight Landed**: Notify family when patient's flight has arrived safely
- **Hotel Check-in**: Confirm when patient has checked into accommodation  
- **Stay Extensions**: Inform family when hotel stay is extended
- **Cab Arrival**: Notify family when transportation arrives

### **🏨 Hotel Operations**
- **Guest Arrival Alert**: Notify hotel 30 minutes before guest arrival
- **Special Requirements**: Communicate patient's accessibility needs
- **Room Preparation**: Ensure room is ready for medical tourism guest
- **Service Coordination**: Arrange for any special services needed

### **🚗 Transportation**
- **Cab Arrangement**: Dispatch cab to airport when flight lands
- **Driver Communication**: Provide driver with guest details and pickup location
- **Accessibility**: Ensure wheelchair accessible vehicles when needed
- **Tracking**: Monitor cab arrival and provide updates

## 🔄 Notification Flow

```
Flight Agent detects landing
        ↓
Guardian Orchestrator
        ↓
Hotel Agent receives HandleFlightLanded
        ↓
┌─────────────────┬─────────────────┬─────────────────┐
│ Family          │ Hotel           │ Transportation  │
│ Notification    │ Notification    │ Arrangement     │
│                 │                 │                 │
│ "Patient landed │ "Guest arriving │ "Cab dispatched │
│  safely at JFK" │  in 30 minutes" │  to Gate B12"   │
└─────────────────┴─────────────────┴─────────────────┘
```

## 📋 Hotel Agent API Integration

### **HandleFlightLanded Method**
```json
{
  "jsonrpc": "2.0",
  "id": "flight_landed_user_123",
  "method": "HandleFlightLanded",
  "params": {
    "user_id": "user_123",
    "patient_name": "Dr. Sarah Johnson",
    "flight_details": {
      "flight_number": "AA2990",
      "airline": "American Airlines",
      "arrival_time": "2025-10-11T17:40:00",
      "gate": "B12",
      "terminal": "8",
      "status": "LANDED"
    },
    "airport_details": {
      "airport_code": "JFK",
      "airport_name": "John F. Kennedy International Airport",
      "latitude": 40.6413,
      "longitude": -73.7781
    },
    "hotel_details": {
      "hotel_name": "Manhattan Medical Suites",
      "hotel_room_number": "Suite 405",
      "booking_reference": "HOTEL_NOTIFY_XYZ",
      "check_in_date": "2025-10-12T15:00:00"
    },
    "family_contacts": [
      "+1-555-HOTEL-FAMILY-001",
      "+1-555-HOTEL-FAMILY-002",
      "+1-555-HOTEL-FAMILY-003"
    ],
    "special_requirements": "Wheelchair accessible, diabetic meals",
    "orchestration_id": "ORCH_user_123",
    "tasks": {
      "notify_family": true,
      "notify_hotel": true,
      "arrange_cab": true,
      "estimated_arrival_to_hotel": "30 minutes"
    }
  }
}
```

## 🎛️ Hotel Agent Internal Actions

### **1. Family Notification**
```json
POST /notification-agent/a2a/tasks
{
  "jsonrpc": "2.0",
  "method": "SendFlightBookingNotification",
  "params": {
    "notification_type": "flight_landed",
    "recipients": [
      {
        "email": "family@example.com",
        "name": "Family Member",
        "preferred_method": "SMS"
      }
    ],
    "message": {
      "subject": "Patient Landed Safely",
      "body": "Dr. Sarah Johnson has landed safely at JFK Airport, Gate B12. Cab has been arranged and will arrive in 5 minutes."
    }
  }
}
```

### **2. Hotel Notification**
```json
POST /notification-agent/a2a/tasks
{
  "jsonrpc": "2.0",
  "method": "SendHotelBookingNotification", 
  "params": {
    "notification_type": "guest_arrival",
    "recipients": [
      {
        "email": "hotel@manhattanmedical.com",
        "name": "Hotel Staff",
        "preferred_method": "email"
      }
    ],
    "message": {
      "subject": "Guest Arriving in 30 Minutes",
      "body": "Dr. Sarah Johnson will arrive at Manhattan Medical Suites in 30 minutes. Room Suite 405 is ready. Special requirements: Wheelchair accessible, diabetic meals."
    }
  }
}
```

### **3. Cab Arrangement**
```json
POST /cab-service/a2a/tasks
{
  "jsonrpc": "2.0",
  "method": "ArrangeCab",
  "params": {
    "pickup_location": {
      "airport_code": "JFK",
      "terminal": "8",
      "gate": "B12",
      "latitude": 40.6413,
      "longitude": -73.7781
    },
    "destination": {
      "hotel_name": "Manhattan Medical Suites",
      "address": "123 Medical Tourism Ave, NYC",
      "latitude": 40.7589,
      "longitude": -73.9851
    },
    "passenger_details": {
      "name": "Dr. Sarah Johnson",
      "special_requirements": "Wheelchair accessible vehicle",
      "contact": "+1-555-PATIENT"
    },
    "estimated_arrival": "30 minutes"
  }
}
```

## 📱 Notification Examples

### **Family Notification - Flight Landed**
```
📧 SMS to Family:

Dr. Sarah Johnson has landed safely at JFK Airport, Gate B12. 
Cab has been arranged and will arrive in 5 minutes. 
Hotel check-in will be ready at Manhattan Medical Suites, Suite 405.

Guardian Medical Tourism
```

### **Hotel Notification - Guest Arrival**
```
📧 Email to Hotel:

Subject: Guest Arriving in 30 Minutes - Dr. Sarah Johnson

Dear Hotel Staff,

Dr. Sarah Johnson will arrive at Manhattan Medical Suites in 30 minutes.

Guest Details:
• Room: Suite 405
• Check-in: 15:00 (3:00 PM)
• Special Requirements: Wheelchair accessible, diabetic meals
• Medical Conditions: Diabetes, Hypertension
• Companion: Mike Johnson

Please ensure:
✅ Room is prepared with accessibility features
✅ Diabetic meal options are available
✅ Wheelchair accessible path to room
✅ Welcome package with medical tourism information

Thank you,
Guardian Medical Tourism
```

### **Cab Driver Notification**
```
📱 SMS to Driver:

Pickup: JFK Airport, Terminal 8, Gate B12
Passenger: Dr. Sarah Johnson
Destination: Manhattan Medical Suites, Suite 405
Special: Wheelchair accessible vehicle required
ETA: 30 minutes to hotel

Contact: +1-555-PATIENT
```

## 🔒 Security & Privacy

### **Security status**
- The examples are intended to minimize medical details in notification payloads.
- Transport security, authorization, consent, and audit coverage depend on the configured external services and have not been verified end to end.
- Do not use the prototype with real patient data without a security and compliance review.

### **Data Protection**
- **Minimal Data**: Only necessary information shared
- **Consent Management**: Patient controls family notifications
- **Secure Channels**: All communications use secure protocols

## 📊 Evaluation status

This repository contains no measured notification speed, delivery rate, satisfaction, room-readiness, accessibility, or transportation-performance results. The flow below is a demo scenario, not evidence of real-world outcomes.

## 🎯 Benefits

### **For Families**
- ✅ **Immediate Updates**: Know patient status in real-time
- ✅ **Peace of Mind**: Confirmed safe arrival and transportation
- ✅ **Transparency**: Full visibility into patient journey
- ✅ **Emergency Response**: Immediate alerts for any issues

### **For Hotels**
- ✅ **Guest Preparation**: 30 minutes to prepare for arrival
- ✅ **Service Excellence**: All special requirements met
- ✅ **Operational Efficiency**: Streamlined check-in process
- ✅ **Guest Satisfaction**: Smooth arrival experience

### **For Patients**
- ✅ **Seamless Arrival**: Transportation ready upon landing
- ✅ **Accessibility request**: Vehicle requirements are forwarded to the configured service
- ✅ **Stress Reduction**: Everything arranged automatically
- ✅ **Focus on Health**: No logistics to worry about

---

**The Hotel Agent Notification Flow ensures that from the moment a patient's flight lands, families are informed, hotels are prepared, and transportation is arranged - creating a truly seamless medical tourism experience.** 🏨✈️👨‍👩‍👧‍👦
