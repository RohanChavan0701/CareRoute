# Guardian A2A Orchestrator

🧠 **Guardian** is a medical & wellness tourism companion app for elderly travelers, built with the real **A2A (Agent-to-Agent)** protocol from [github.com/a2aproject/A2A](https://github.com/a2aproject/A2A) for multi-agent collaboration.

## 🎯 Overview

Guardian automatically:
- Tracks flight ETAs and locations
- Confirms hotel and hospital bookings before arrival
- Sends notifications to patients and their families
- Handles voice communication (calls, updates)
- Operates in a HIPAA-conscious, autonomous manner

## 🏗️ Architecture

```
Flutter App (frontend)
│
▼
ChatGPT Voice Agent (user interface)
│ calls →
Guardian (A2A Orchestrator Agent)
├─ HotelAgent (A2A)
├─ HospitalAgent (A2A)
├─ VoiceAgent (A2A)
└─ FamilyNotifyAgent (A2A)
│
└─ FastAPI + LangGraph backend (execution core)
```

## 🤖 Agents

### Guardian Agent (Orchestrator)
- Main coordinator for medical tourism workflow
- Monitors flight status and triggers workflows
- Manages communication between sub-agents
- Handles emergency situations

### Hotel Agent
- Confirms hotel bookings
- Arranges accessibility accommodations
- Handles special requirements
- Manages late check-in scenarios

### Hospital Agent
- Confirms medical appointments
- Verifies medical history and medications
- Arranges medical transportation
- Handles emergency medical situations

### Voice Agent
- Initiates voice calls via Twilio/OpenAI Realtime
- Handles emergency voice alerts
- Provides multilingual support
- Manages call transcription

### Notify Agent
- Sends family notifications via SMS, email, push
- Handles emergency alerts
- Manages delivery confirmations
- Supports multiple communication channels

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

### Core Guardian Endpoints

- `POST /guardian/run` - Manually trigger Guardian workflow
- `GET /guardian/status/{flight_number}` - Get workflow status
- `POST /guardian/cancel/{flight_number}` - Cancel workflow

### A2A Protocol Endpoints

- `POST /a2a/receive` - Receive A2A messages from agents
- `POST /a2a/register` - Register new agent
- `GET /a2a/agents` - List registered agents

### Health & Monitoring

- `GET /health` - System health check
- `GET /metrics` - Prometheus metrics (if enabled)

## 🔧 Configuration

### Environment Variables

Key configuration options in `.env`:

```bash
# A2A Protocol
A2A_API_TOKEN=your-a2a-api-token
A2A_SIGNATURE_SECRET=your-signature-secret

# Twilio (Voice & SMS)
TWILIO_ACCOUNT_SID=your-account-sid
TWILIO_AUTH_TOKEN=your-auth-token

# OpenAI (Realtime Voice)
OPENAI_API_KEY=your-openai-key

# Flight Tracking
AVIATION_STACK_API_KEY=your-api-key

# Security
HIPAA_MODE=true
VOICE_POLICY_LEVEL=moderate
```

### Voice Policy Configuration

Voice communication is controlled by HIPAA-conscious policies:

- **Strict**: No voice calls allowed
- **Moderate**: Limited voice calls (default)
- **Permissive**: Most voice calls allowed
- **Emergency Only**: Only emergency calls

## 🏥 HIPAA Compliance

Guardian is designed with HIPAA compliance in mind:

- **No PHI Logging**: Only reference IDs are logged
- **Encrypted Communication**: All A2A messages are encrypted
- **Audit Logging**: Complete audit trail of all actions
- **Access Controls**: Role-based access to sensitive data
- **Data Retention**: 7-year retention policy
- **Voice Policies**: Controlled voice communication

## 📊 Monitoring & Observability

### Health Checks

- `/health` - Basic health status
- `/metrics` - Prometheus metrics
- Agent status monitoring
- Workflow progress tracking

### Logging

- Structured JSON logging
- HIPAA-compliant audit logs
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

## 🚀 Deployment

### Docker Production

```bash
docker-compose -f docker-compose.prod.yml up -d
```

### AWS ECS Fargate

1. Build and push Docker image to ECR
2. Create ECS task definition
3. Deploy to Fargate service
4. Configure RDS PostgreSQL
5. Set up CloudWatch logging

### Kubernetes

```bash
kubectl apply -f k8s/
```

## 📈 Scaling

### Horizontal Scaling

- Multiple Guardian instances behind load balancer
- Redis for shared state
- PostgreSQL read replicas
- Message queue for async processing

### Performance Optimization

- Connection pooling for databases
- Caching frequently accessed data
- Async processing for I/O operations
- Rate limiting for external APIs

## 🔒 Security

### A2A Security

- API token authentication
- Message signature verification
- Encrypted communication channels
- Agent identity verification

### Application Security

- JWT token authentication
- Role-based access control
- Input validation and sanitization
- SQL injection prevention
- XSS protection

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

### Development Guidelines

- Follow PEP 8 style guide
- Add type hints
- Write comprehensive tests
- Update documentation
- Ensure HIPAA compliance

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

- **Documentation**: [Wiki](link-to-wiki)
- **Issues**: [GitHub Issues](link-to-issues)
- **Discussions**: [GitHub Discussions](link-to-discussions)

## 🎯 Roadmap

### Phase 1 (Current)
- ✅ Core A2A agent implementation
- ✅ LangGraph workflow orchestration
- ✅ Basic voice and notification integration
- ✅ HIPAA-compliant logging

### Phase 2
- 🔄 Advanced voice AI integration
- 🔄 Machine learning for workflow optimization
- 🔄 Multi-language support
- 🔄 Advanced analytics dashboard

### Phase 3
- 📋 Integration with more medical systems
- 📋 IoT device integration
- 📋 Advanced emergency response
- 📋 Global deployment support

---

**Built with ❤️ for elderly travelers and their families**
