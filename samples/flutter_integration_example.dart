// Flutter Integration Example for Guardian Orchestrator Backend
// This shows how Flutter frontend would communicate with the AG-UI enabled backend

import 'dart:async';
import 'dart:convert';
import 'package:http/http.dart' as http;

class GuardianOrchestratorClient {
  static const String baseUrl = 'http://localhost:8000';
  
  // AG-UI Event Stream for real-time updates
  StreamController<AGUIEvent> eventController = StreamController<AGUIEvent>.broadcast();
  late StreamSubscription<AGUIEvent> eventSubscription;

  GuardianOrchestratorClient() {
    _setupEventStream();
  }

  void _setupEventStream() {
    // Set up real-time event listening using Server-Sent Events
    eventSubscription = _listenToEvents('PAT_001').listen((event) {
      eventController.add(event);
      _handleAGUIEvent(event);
    });
  }

  // Handle different AG-UI event types
  void _handleAGUIEvent(AGUIEvent event) {
    switch (event.type) {
      case 'orchestration_started':
        print('🚀 Orchestration started for ${event.patientId}');
        _showNotification('Orchestration Started', 'Your travel coordination has begun');
        break;
        
      case 'flight_status_update':
        print('✈️ Flight status updated: ${event.data['status']}');
        _updateFlightStatus(event.data);
        break;
        
      case 'hotel_confirmed':
        print('🏨 Hotel confirmed: ${event.data['hotel_name']}');
        _updateHotelStatus(event.data);
        break;
        
      case 'hospital_confirmed':
        print('🏥 Hospital confirmed: ${event.data['hospital_name']}');
        _updateHospitalStatus(event.data);
        break;
        
      case 'notification_sent':
        print('📱 Notification sent to ${event.data['recipient']}');
        _showNotification('Notification Sent', 'Updates sent to your family');
        break;
        
      case 'incoming_call':
        print('📞 Incoming call from ${event.data['caller_id']}');
        _handleIncomingCall(event.data);
        break;
        
      case 'knowledge_query_response':
        print('🧠 Knowledge response: ${event.data['response']}');
        _displayKnowledgeResponse(event.data);
        break;
        
      default:
        print('📡 Unknown event type: ${event.type}');
    }
  }

  // Start patient booking orchestration
  Future<Map<String, dynamic>> startOrchestration({
    required String patientId,
    required String patientName,
    required String patientEmail,
    required String flightNumber,
    required String flightDate,
    required String departureAirport,
    required String arrivalAirport,
    required String hotelBookingRef,
    required String hospitalBookingRef,
    String specialRequirements = '',
    List<String> medicalConditions = const [],
    required int age,
    List<Map<String, String>> emergencyContacts = const [],
    String flightTime = '09:00',
  }) async {
    final requestBody = {
      'patient_id': patientId,
      'patient_name': patientName,
      'patient_email': patientEmail,
      'flight_number': flightNumber,
      'flight_date': flightDate,
      'departure_airport': departureAirport,
      'arrival_airport': arrivalAirport,
      'hotel_booking_reference': hotelBookingRef,
      'hospital_booking_reference': hospitalBookingRef,
      'special_requirements': specialRequirements,
      'medical_conditions': medicalConditions,
      'age': age,
      'emergency_contacts': emergencyContacts,
      'flight_time': flightTime,
    };

    final response = await http.post(
      Uri.parse('$baseUrl/orchestrate/booking'),
      headers: {'Content-Type': 'application/json'},
      body: json.encode(requestBody),
    );

    if (response.statusCode == 200) {
      return json.decode(response.body);
    } else {
      throw Exception('Failed to start orchestration: ${response.statusCode}');
    }
  }

  // Query knowledge base
  Future<Map<String, dynamic>> queryKnowledge({
    required String patientId,
    required String question,
    Map<String, dynamic>? context,
  }) async {
    final requestBody = {
      'patient_id': patientId,
      'question': question,
      'context': context ?? {},
    };

    final response = await http.post(
      Uri.parse('$baseUrl/knowledge/query'),
      headers: {'Content-Type': 'application/json'},
      body: json.encode(requestBody),
    );

    if (response.statusCode == 200) {
      return json.decode(response.body);
    } else {
      throw Exception('Failed to query knowledge: ${response.statusCode}');
    }
  }

  // Handle incoming call
  Future<Map<String, dynamic>> handleIncomingCall({
    required String patientId,
    String callType = 'general_inquiry',
    Map<String, dynamic>? callData,
  }) async {
    final requestBody = {
      'patient_id': patientId,
      'call_type': callType,
      'call_data': callData ?? {},
    };

    final response = await http.post(
      Uri.parse('$baseUrl/calls/incoming'),
      headers: {'Content-Type': 'application/json'},
      body: json.encode(requestBody),
    );

    if (response.statusCode == 200) {
      return json.decode(response.body);
    } else {
      throw Exception('Failed to handle incoming call: ${response.statusCode}');
    }
  }

  // Submit schedule amendment
  Future<Map<String, dynamic>> submitScheduleAmendment({
    required String patientId,
    required String amendmentType,
    required Map<String, dynamic> amendmentData,
  }) async {
    final requestBody = {
      'patient_id': patientId,
      'amendment_type': amendmentType,
      'amendment_data': amendmentData,
    };

    final response = await http.post(
      Uri.parse('$baseUrl/schedule/amend'),
      headers: {'Content-Type': 'application/json'},
      body: json.encode(requestBody),
    );

    if (response.statusCode == 200) {
      return json.decode(response.body);
    } else {
      throw Exception('Failed to submit schedule amendment: ${response.statusCode}');
    }
  }

  // Get orchestration status
  Future<Map<String, dynamic>> getOrchestrationStatus(String orchestrationId) async {
    final response = await http.get(
      Uri.parse('$baseUrl/orchestration/$orchestrationId/status'),
    );

    if (response.statusCode == 200) {
      return json.decode(response.body);
    } else {
      throw Exception('Failed to get orchestration status: ${response.statusCode}');
    }
  }

  // Get patient context
  Future<Map<String, dynamic>> getPatientContext(String patientId) async {
    final response = await http.get(
      Uri.parse('$baseUrl/patient/$patientId/context'),
    );

    if (response.statusCode == 200) {
      return json.decode(response.body);
    } else {
      throw Exception('Failed to get patient context: ${response.statusCode}');
    }
  }

  // Listen to AG-UI events for a patient
  Stream<AGUIEvent> _listenToEvents(String patientId) async* {
    final client = http.Client();
    
    try {
      final request = http.Request('GET', Uri.parse('$baseUrl/stream/events/$patientId'));
      final streamedResponse = await client.send(request);
      
      await for (String line in streamedResponse.stream.transform(utf8.decoder).transform(const LineSplitter())) {
        if (line.startsWith('data: ')) {
          final eventData = line.substring(6);
          try {
            final eventJson = json.decode(eventData);
            yield AGUIEvent.fromJson(eventJson);
          } catch (e) {
            print('Error parsing event: $e');
          }
        }
      }
    } finally {
      client.close();
    }
  }

  // Get recent AG-UI events
  Future<List<AGUIEvent>> getRecentEvents(String patientId, {int limit = 20}) async {
    final response = await http.get(
      Uri.parse('$baseUrl/ag-ui/events/$patientId?limit=$limit'),
    );

    if (response.statusCode == 200) {
      final data = json.decode(response.body);
      return (data['events'] as List)
          .map((event) => AGUIEvent.fromJson(event))
          .toList();
    } else {
      throw Exception('Failed to get recent events: ${response.statusCode}');
    }
  }

  // UI Helper methods (implement these based on your UI framework)
  void _showNotification(String title, String message) {
    // Implement notification display
    print('🔔 Notification: $title - $message');
  }

  void _updateFlightStatus(Map<String, dynamic> flightData) {
    // Update flight status in UI
    print('✈️ Flight Status: ${flightData['status']}');
  }

  void _updateHotelStatus(Map<String, dynamic> hotelData) {
    // Update hotel status in UI
    print('🏨 Hotel Status: ${hotelData['status']}');
  }

  void _updateHospitalStatus(Map<String, dynamic> hospitalData) {
    // Update hospital status in UI
    print('🏥 Hospital Status: ${hospitalData['status']}');
  }

  void _handleIncomingCall(Map<String, dynamic> callData) {
    // Handle incoming call in UI
    print('📞 Incoming call from: ${callData['caller_id']}');
  }

  void _displayKnowledgeResponse(Map<String, dynamic> responseData) {
    // Display knowledge response in UI
    print('🧠 Response: ${responseData['response']}');
  }

  void dispose() {
    eventSubscription.cancel();
    eventController.close();
  }
}

// AG-UI Event model
class AGUIEvent {
  final String type;
  final String timestamp;
  final Map<String, dynamic> data;
  final String? patientId;
  final String? orchestrationId;

  AGUIEvent({
    required this.type,
    required this.timestamp,
    required this.data,
    this.patientId,
    this.orchestrationId,
  });

  factory AGUIEvent.fromJson(Map<String, dynamic> json) {
    return AGUIEvent(
      type: json['type'],
      timestamp: json['timestamp'],
      data: json['data'],
      patientId: json['patient_id'],
      orchestrationId: json['orchestration_id'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'type': type,
      'timestamp': timestamp,
      'data': data,
      'patient_id': patientId,
      'orchestration_id': orchestrationId,
    };
  }
}

// Example usage in a Flutter widget
class GuardianOrchestratorWidget extends StatefulWidget {
  @override
  _GuardianOrchestratorWidgetState createState() => _GuardianOrchestratorWidgetState();
}

class _GuardianOrchestratorWidgetState extends State<GuardianOrchestratorWidget> {
  late GuardianOrchestratorClient client;
  List<AGUIEvent> events = [];

  @override
  void initState() {
    super.initState();
    client = GuardianOrchestratorClient();
    
    // Listen to events
    client.eventController.stream.listen((event) {
      setState(() {
        events.add(event);
      });
    });
  }

  @override
  void dispose() {
    client.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Guardian Orchestrator')),
      body: Column(
        children: [
          ElevatedButton(
            onPressed: () async {
              try {
                final result = await client.startOrchestration(
                  patientId: 'PAT_001',
                  patientName: 'John Doe',
                  patientEmail: 'john@example.com',
                  flightNumber: 'AA100',
                  flightDate: '2025-10-15',
                  departureAirport: 'JFK',
                  arrivalAirport: 'LAX',
                  hotelBookingRef: 'HOTEL_123',
                  hospitalBookingRef: 'HOSP_456',
                  age: 65,
                );
                print('Orchestration started: $result');
              } catch (e) {
                print('Error: $e');
              }
            },
            child: Text('Start Orchestration'),
          ),
          Expanded(
            child: ListView.builder(
              itemCount: events.length,
              itemBuilder: (context, index) {
                final event = events[index];
                return ListTile(
                  title: Text(event.type),
                  subtitle: Text(event.timestamp),
                  trailing: Text(event.patientId ?? 'System'),
                );
              },
            ),
          ),
        ],
      ),
    );
  }
}
