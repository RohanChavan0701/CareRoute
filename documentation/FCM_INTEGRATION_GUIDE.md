# FCM Real-time Updates Integration Guide

## 🚀 Overview

This guide explains how to implement Firebase Cloud Messaging (FCM) for real-time updates in the Guardian Medical Tourism Orchestrator, enabling the Flutter app to receive push notifications for the complete trip flow.

## 📱 Complete Trip Flow with FCM

### 1. **Boarding Reminder** (2 hours before flight)
- **FCM Notification**: "✈️ Boarding Reminder - Boarding for AI101 starts in 45 minutes"
- **App Update**: Adds boarding reminder to timeline
- **Data**: Flight number, boarding time, gate information

### 2. **Flight Status Update** (30 minutes before departure)
- **FCM Notification**: "✈️ Flight Status Update - AI101 is now On Time - Gate B12"
- **App Update**: Updates flight status in timeline
- **Data**: Flight status, gate, boarding status

### 3. **Cab Arrangement** (30 minutes before arrival)
- **FCM Notification**: "🚗 Cab Arranged - Alex Johnson will pick you up in 15 minutes"
- **Email**: Hotel confirmation email via notification agent
- **App Update**: Adds cab details to timeline
- **Data**: Driver name, vehicle, ETA, hotel information

### 4. **Voice Call Context** (Any time)
- **Trigger**: User presses "Call Agent" button
- **Action**: Complete patient context sent to voice agent
- **Data**: All patient information in exact JSON-RPC format

### 5. **Hospital Appointment Reminder** (1 hour before)
- **FCM Notification**: "🏥 Appointment Reminder - Appointment with Dr. Meera Singh at Apollo Medical Center at 09:30 AM"
- **App Update**: Adds hospital appointment to timeline
- **Data**: Doctor name, hospital, appointment time

## 🔧 Backend Implementation

### FCM Service (`backend/fcm_service.py`)
```python
class FCMService:
    async def send_notification(user_id, title, body, data)
    async def send_boarding_reminder(user_id, flight_info)
    async def send_flight_status_update(user_id, flight_info)
    async def send_cab_request_notification(user_id, cab_info)
    async def send_hospital_appointment_reminder(user_id, appointment_info)
```

### Orchestrator Integration (`backend/orchestrator.py`)
```python
async def send_boarding_reminder(user_id, flight_info)
async def send_flight_status_update(user_id, flight_info)
async def send_arrival_cab_notification(user_id, cab_info)
async def send_hospital_appointment_reminder(user_id, appointment_info)
```

### API Endpoints (`backend/ag_ui_backend_simple.py`)
```
POST /fcm/register - Register FCM device token
POST /fcm/send-boarding-reminder - Send boarding reminder
POST /fcm/send-flight-update - Send flight status update
POST /fcm/send-cab-notification - Send cab notification
POST /fcm/send-appointment-reminder - Send appointment reminder
```

## 📱 Flutter App Integration

### 1. **Register FCM Token**
```dart
// Get FCM token and register with backend
String? token = await FirebaseMessaging.instance.getToken();
await registerFCMToken(userId, token);
```

### 2. **Listen for Notifications**
```dart
FirebaseMessaging.onMessage.listen((RemoteMessage message) {
  // Handle notification when app is in foreground
  updateTimelineUI(message.data);
});
```

### 3. **Update Timeline UI**
```dart
void updateTimelineUI(Map<String, dynamic> data) {
  String type = data['type'];
  switch (type) {
    case 'boarding_reminder':
      addBoardingReminder(data);
      break;
    case 'flight_status_update':
      updateFlightStatus(data);
      break;
    case 'cab_requested':
      addCabDetails(data);
      break;
    case 'hospital_appointment':
      addHospitalAppointment(data);
      break;
  }
}
```

### 4. **Voice Call Integration**
```dart
void onCallAgentPressed() {
  // Send complete patient context to voice agent
  sendVoiceCallRequest(userId);
}
```

## 🧪 Testing

### Test Real-time Flow
```bash
cd tests
python test_realtime_flow.py
```

### Test FCM Endpoints
```bash
cd tests
python test_fcm_endpoints.py
```

## 🔑 Setup Requirements

### 1. **Firebase Console Setup**
1. Create Firebase project
2. Add Android/iOS app
3. Download `google-services.json` (Android) / `GoogleService-Info.plist` (iOS)
4. Get FCM Server Key from Project Settings

### 2. **Backend Configuration**
```python
# In backend/fcm_service.py
self.fcm_server_key = "YOUR_FCM_SERVER_KEY_HERE"
```

### 3. **Environment Variables**
```bash
FCM_SERVER_KEY=your_fcm_server_key_here
```

## 📊 Demo Flow Timeline

```
Timeline View (like your screenshots):
├── 2 hours before: ✈️ Boarding Reminder
├── 30 min before: ✈️ Flight Status Update  
├── 30 min before: 🚗 Cab Arranged
├── Any time: 📞 Call Agent (with full context)
└── 1 hour before: 🏥 Hospital Appointment
```

## 🎯 Key Features

✅ **Real-time Push Notifications** - Instant updates to mobile app
✅ **Rich Notification Data** - Structured data for timeline updates
✅ **Voice Agent Integration** - Complete patient context on call
✅ **Multi-channel Updates** - FCM + Email notifications
✅ **Timeline UI Updates** - Automatic UI updates from FCM data
✅ **Hospital Integration** - Appointment reminders and details

## 🚀 Demo Ready

The implementation is **demo-ready** and provides:
- Complete trip flow automation
- Real-time updates via FCM
- Voice agent with full context
- Timeline UI updates
- Hospital appointment integration

Just add your FCM server key and the system is ready for demo!
