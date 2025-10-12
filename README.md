# CareRoute Medical Tourism Orchestrator

🏥 **CareRoute** - *where care meets comfort* - is a comprehensive medical tourism orchestration system that coordinates multi-agent workflows for elderly travelers, providing seamless coordination between hotels, hospitals, voice agents, and family notifications.

## 📁 Repository Structure

This project consists of multiple interconnected repositories:

### 🎯 **Main Orchestrator** (This Repository)
- **[CareRoute Medical Tourism Orchestrator](https://github.com/atharvasalunke/medical_orchestrator)** - Core orchestration engine
- **Function**: Central coordinator for all medical tourism workflows
- **Status**:  **Hosted on AWS** - Deployed at `http://ec2-3-16-29-184.us-east-2.compute.amazonaws.com:8000/`

### 🤖 **External Agent Repositories**

#### 📱 **Flutter Frontend App**
- **[Flutter Medical Tourism App](https://github.com/ForgottenLight4415/codefest-25-app)** - Patient booking interface
- **Function**: Patient booking input and trip management
- **Status**: ✅ **READY** - Flutter app for medical tourism planning

#### ✈️ **Flight Agent**
- **[Flight API Repository](https://github.com/rohanpc0701/Codefest_Flightapi)** - Real-time flight tracking
- **Function**: Flight status monitoring and updates

#### 📧 **Notification Agent**  
- **[Notification System Repository](https://github.com/uma1902/notification-system)** - Email Notifications
- **Function**: Family notifications and booking confirmations

#### 📞 **Voice Agent**
- **[Voice Agent Repository](https://github.com/uma1902/notification-system)** (Voice functionality)
- **Function**: AI-powered voice communication with patients

## 🎯 Overview

CareRoute automatically orchestrates:
- ✈️ **Flight Monitoring** - Real-time flight status tracking and updates via external Flight Agent
- 📞 **Voice Communication** - AI-powered voice calls with complete patient context via Voice Agent
- 📱 **Family Notifications** - Automated updates to family members via email/SMS via Notification Agent
- 🏥 **HIPAA-Compliant Database** - Secure patient data management with encryption 
- 🎯 **Multi-Agent Coordination** - Seamless integration with external services via JSON-RPC protocol

## 🏗️ System Architecture

![CareRoute Medical Tourism Orchestrator Architecture](https://github.com/atharvasalunke/medical_orchestrator/blob/main/docs/architecture-diagram.png)

### Architecture Flow

1. **User Interaction Layer**: Flutter App for patient booking input
2. **Core Orchestrator**: CareRoute Orchestrator (The Brain) running on AWS EC2
   - Booking Agent: Handles initial booking processing
   - Scheduler Service: Manages task scheduling and workflows
   - Flight Tracker: Monitors flight status and updates
3. **Data Storage**: Dummy data storage for testing (in-memory)
4. **External Agents**: Voice, Notification, and Flight agents via JSON-RPC 2.0

### Key Components

- **🎯 CareRoute Orchestrator**: Central intelligence coordinating all workflows
- **📱 Flutter Frontend**: Patient booking interface
- **🗄️ PostgreSQL Database**: HIPAA-compliant data storage
- **🔐 A2A Protocol**: Secure JSON-RPC 2.0 communication
- **🤖 External Agents**: Specialized microservices for specific functions

## 🚀 Live Demo & Deployment

- **🌐 URL**: `http://3.16.29.184:8000`
- **📊 Health Check**: `http://3.16.29.184:8000/health`
- **📚 API Docs**: `http://3.16.29.184:8000/docs`
- **🐳 Docker Ready**: Full containerization with deployment

## 🤖 External Agent Integration

### CareRoute Orchestrator (This Repository)
- **Main coordinator** for medical tourism workflow
- **Flight monitoring** and status tracking
- **A2A protocol** communication with external agents
- **HIPAA-compliant** database management
- **Real-time notifications** via FCM (Future Sc)
- **Background scheduling** for automated workflows

### External Agents (Active Repositories)

#### 📞 Voice Agent
- **Repository**: [Voice Agent Repository](https://github.com/uma1902/notification-system) (Voice functionality)
- **Function**: AI-powered voice communication with patients
- **Integration**: JSON-RPC protocol at `http://18.217.151.15:8000/jsonrpc`
- **Status**: ✅ **WORKING** - Successfully tested with complete patient context

#### 📧 Notification Agent
- **Repository**: [Notification System Repository](https://github.com/uma1902/notification-system)
- **Function**: Email/SMS notifications to patients and families
- **Integration**: JSON-RPC protocol at `http://3.143.225.130:8000/a2a/tasks`
- **Status**: ✅ **WORKING** - Successfully tested with booking confirmations

#### ✈️ Flight Agent
- **Repository**: [Flight API Repository](https://github.com/rohanpc0701/Codefest_Flightapi)
- **Function**: Real-time flight status and tracking
- **Integration**: JSON-RPC protocol at `http://54.158.27.0:8001/a2a`
- **Status**: ✅ **WORKING** - Successfully tested with UAL606 flight data
- **Features**: Live flight data, delay notifications, gate information

### Future Agents Ideas

#### ♿ Accessibility Agent
- **Status**: Not currently integrated
- **Function**: Special requirements and mobility assistance
- **Note**: Removed from current workflow per user requirements

#### 🏨 Hotel Agent
- **Function**: Hotel booking confirmations and arrangements
- **Note**: Using direct notification system instead

#### 🏥 Hospital Agent  
- **Function**: Medical appointment scheduling and confirmations
- **Note**: Using direct notification system instead

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose
- Python 3.11+
- PostgreSQL (or use Docker)
- Redis (or use Docker)
- A2A SDK (`pip install a2a-sdk>=0.3.0`)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd medical_orchestrator
   ```

2. **Set up environment variables**
   ```bash
   cp env.example .env
   # Edit .env with your actual API keys and configuration
   ```

3. **Start with Docker Compose**
   ```bash
   docker-compose up -d
   ```

4. **Access the application**
   - API: http://localhost:8000
   - Health Check: http://localhost:8000/health
   - Swagger UI: http://localhost:8000/docs

### Manual Setup (Development)

1. **Install dependencies**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. **Start PostgreSQL and Redis**
   ```bash
   # Using Docker
   docker run -d --name postgres -p 5432:5432 -e POSTGRES_PASSWORD=password postgres:15
   docker run -d --name redis -p 6379:6379 redis:7-alpine
   ```

3. **Run the application**
   ```bash
   cd backend
   python main.py
   ```

## 📡 API Endpoints

### 🎯 Core Orchestration Endpoints

- `POST /api/booking` - **Create booking and start orchestration**
- `GET /guardian/trip/status/{user_id}` - **Get complete trip status**
- `GET /guardian/scheduler/status` - **Background job status**

### 📞 Voice Integration

- `POST /guardian/voice/call` - **Trigger voice call with patient context**

### ✈️ Flight Status

- `POST /api/flight/status` - **Get flight status by flight number and date**

### 📧 Notification Endpoints

- `POST /api/notifications/hotel-booking` - **Send hotel booking confirmation**
- `POST /api/notifications/flight-landed` - **Send flight landed notification**
- `POST /api/notifications/hotel-shuttle` - **Send hotel shuttle request**

### 🏥 Health & Monitoring

- `GET /health` - **System health check**
- `GET /` - **Root endpoint**

### 📱 Frontend Integration

- `POST /message` - **General message handling**
- `GET /docs` - **Interactive API documentation**


### Voice Policy Configuration

Voice communication is controlled by HIPAA-conscious policies:

- **Strict**: No voice calls allowed
- **Moderate**: Limited voice calls (default)
- **Permissive**: Most voice calls allowed
- **Emergency Only**: Only emergency calls

## 🏥 HIPAA Compliance

CareRoute is designed with HIPAA compliance in mind:

- **No PHI Logging**: Only reference IDs are logged
- **Encrypted Communication**: All A2A messages are encrypted
- **Audit Logging**: Complete audit trail of all actions
- **Access Controls**: Role-based access to sensitive data
- **Data Retention**: 1 month retention policy
- **Voice Policies**: Controlled voice communication

## 📊 Monitoring & Observability

### Health Checks

- `/health` - Basic health status
- `/metrics` - Prometheus metrics
- Agent status monitoring
- Workflow progress tracking

### Logging

- Structured JSON logging
- Error tracking and alerting
- Performance monitoring

## 🔄 Workflow Process

1. **Flight Monitoring**: Continuous monitoring of flight ETAs
2. **Trigger Condition**: When ETA < 6 hours, Guardian workflow starts
3. **Hotel Coordination**: Confirm hotel booking and accommodations
4. **Hospital Coordination**: Confirm medical appointments
5. **Family Notification**: Send status updates to family
6. **Voice Communication**: Initiate voice calls if needed
7. **Completion**: Log results and cleanup

## 🧪 Testing

### Run Tests

```bash
cd backend
pytest tests/ -v
```

### Test A2A Integration

```bash
python test_a2a_integration.py
```

### Test Coverage

```bash
pytest --cov=backend tests/
```

### Integration Tests

```bash
pytest tests/integration/ -v
```

## 📁 Repository Structure

```
careRoute_medical_orchestrator/
├── backend/                    # CareRoute Orchestrator Backend
│   ├── main_backend.py        # FastAPI application entry point
│   ├── orchestrator.py        # Core orchestration logic
│   ├── scheduler.py           # Background task scheduler
│   ├── fcm_service.py         # Firebase Cloud Messaging
│   ├── dummy_data.py          # In-memory data storage for testing
│   ├── knowledge_base.py      # Knowledge base for context
│   ├── database/              # HIPAA-compliant database layer (available but not active)
│   │   ├── models.py          # SQLAlchemy models
│   │   ├── repository.py      # Data access layer
│   │   ├── orchestrator_service.py # Orchestrator database service
│   │   ├── encryption.py      # HIPAA encryption utilities
│   │   ├── audit.py           # Audit logging
│   │   ├── connection.py      # Database connection management
│   │   └── migrations.py      # Database migration scripts
│   └── requirements.txt       # Python dependencies
├── agents/                    # Agent implementations (legacy)
│   ├── voice_agent.py         # Voice agent integration
│   ├── notify_agent.py        # Notification agent integration
│   ├── accessibility_agent.py # Accessibility services
│   ├── hotel_agent.py         # Hotel coordination
│   └── hospital_agent.py      # Hospital coordination
├── deploy/                    # Deployment scripts
│   ├── deploy-to-ec2.sh       # EC2 deployment script
│   ├── Dockerfile             # Docker container
│   ├── docker-compose.yml     # Local development setup
│   └── health-monitor.sh      # Health monitoring
├── aws/                       # AWS deployment configurations
│   ├── deploy.sh              # AWS deployment script
│   ├── ecs-service.json       # ECS service definition
│   └── ecs-task-definition.json # ECS task definition
├── tests/                     # Comprehensive test suite
│   ├── test_orchestrator.py   # Core orchestration tests
│   ├── test_complete_trip_flow.py # End-to-end flow tests
│   ├── test_voice_agent_context.py # Voice agent integration tests
│   ├── test_notification_endpoint.py # Notification tests
│   └── test_flight_agent_compatibility.py # Flight agent tests
├── samples/                   # Sample data and requests
│   ├── flutter_integration_example.dart # Flutter integration example
│   ├── sample_voice_call_context.json # Voice agent context template
│   └── sample_notification_with_email.json # Notification examples
├── sample_requests/           # API request examples
│   ├── voice_agent_requests.json # Voice agent request formats
│   └── notification_agent_requests.json # Notification request formats
├── sample_responses/          # API response examples
│   └── notification_agent_responses.json # Notification response examples
├── documentation/             # Comprehensive documentation
│   ├── GUARDIAN_ARCHITECTURE.md # System architecture guide
│   ├── HIPAA_COMPLIANCE_GUIDE.md # HIPAA compliance documentation
│   ├── FRONTEND_API_INTEGRATION.md # Frontend integration guide
│   ├── HOTEL_AGENT_NOTIFICATION_FLOW.md # Hotel agent workflow
│   └── DEPLOYMENT.md          # Deployment guide
├── docs/                      # Architecture diagrams and visuals
│   └── architecture-diagram.png # System architecture diagram
├── nginx.conf                 # Nginx configuration
├── .gitignore                 # Git ignore rules
└── README.md                  # This file
```

##  Deployment

### 🐳 Docker Local Development

```bash
# Start local development environment
docker-compose up --build -d

# Access the application
curl http://localhost:8000/health
```

### ☁️ AWS EC2 Deployment

```bash
# Deploy to EC2 (replace with your IP and key)
./deploy/deploy-final.sh 3.16.29.184 deploy/codefest.pem ubuntu

# Verify deployment
curl http://3.16.29.184:8000/health
```

### 🔧 Setup

1. **EC2 Instance**: Ubuntu 20.04+ with Docker installed
2. **Environment**: Environment variables configured
3. **Database**: PostgreSQL 
4. **Monitoring**: Health checks and audit logging enabled
5. **Security**: HTTPS endpoints and encrypted communication



### Development Guidelines

- Follow PEP 8 style guide
- Add type hints
- Write comprehensive tests
- Update documentation


## 🏆 Key Features Implemented

### **Complete Medical Tourism Workflow**
- **End-to-end orchestration** from booking to discharge
- **Real-time flight monitoring** with automated updates via external Flight Agent
- **Multi-agent coordination** via JSON-RPC protocol
- **Dummy data storage** for testing (bypassing database per user requirements)

###  **Deployment**
- **Docker containerization** with health checks
- **AWS EC2 deployment** with automated scripts at `http://ec2-3-16-29-184.us-east-2.compute.amazonaws.com:8000`
- **Background job scheduling** with APScheduler
- **Comprehensive API documentation**

### **Real-Time Communication**
- **Voice agent integration** with complete patient context 
- **Email/SMS notifications** to patients and families via Notification Agent 
- **Flight status updates** via Flight Agent

### **Frontend Integration Ready**
- **Flutter app compatibility** 
- **Booking API** accepting complete patient data from frontend
- **Voice call API** with user context
- **Trip status API** for real-time updates

## 🎯 Development Status

- ✅ **Core orchestration engine** with multi-agent coordination via JSON-RPC
- ✅ **Dummy data storage** for testing (in-memory) 
- ✅ **Real-time notifications** via external Notification Agent
- ✅ **Voice integration** with complete patient context sharing via Voice Agent
- ✅ **Deployment** on AWS EC2 at `http://ec2-3-16-29-184.us-east-2.compute.amazonaws.com:8000`
- ✅ **Comprehensive API** with booking, voice, flight status, and notification endpoints
- ✅ **Background scheduling** for automated workflows
- ✅ **Flight monitoring** with live status updates via Flight Agent
- ✅ **Flutter frontend integration** with snake_case field format support

## 📊 System Metrics

- **🏗️ Architecture**: Microservices with JSON-RPC protocol
- **🔒 Security**: Environment-based configuration
- **⚡ Performance**: Real-time processing with background jobs
- **🌐 Deployment**: Deployed on AWS EC2 at `http://ec2-3-16-29-184.us-east-2.compute.amazonaws.com:8000`
- **📱 Integration**: Flutter app + Voice UI + Orchestrator
- **🤖 Agents**: 3 active external agents (Voice, Notification, Flight) coordinated via CareRoute

---

**🏥 CareRoute Medical Tourism Orchestrator**  
*from check-in to checkup*  
*Built with ❤️ for elderly travelers and their families*  

