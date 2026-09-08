# 🚀 Guardian A2A Orchestrator - Production Deployment Guide

## 📋 Overview

This guide describes the repository's AWS EC2 and Docker deployment scaffolding. It is a starting point for evaluation, not a production-readiness or security attestation.

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    AWS EC2 Instance                        │
│  ┌─────────────────┬─────────────────┬─────────────────┐   │
│  │   Nginx Proxy   │  Guardian App   │   Monitoring    │   │
│  │   (Port 80/443) │   (Port 8000)   │   & Logging     │   │
│  └─────────────────┴─────────────────┴─────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────┐
│                  External A2A Agents                       │
│  ┌─────────────┬─────────────┬─────────────┬─────────────┐ │
│  │Hotel Agent  │Hospital     │Voice Agent  │Notification │ │
│  │             │Agent        │             │Agent        │ │
│  └─────────────┴─────────────┴─────────────┴─────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## 🔧 Prerequisites

### Local Machine Requirements
- Docker and Docker Compose
- SSH client
- AWS EC2 instance with:
  - Ubuntu 20.04+ or Amazon Linux 2
  - Minimum 2GB RAM, 1 CPU core
  - 20GB storage
  - Security group with ports 22, 80, 443, 8000 open

### AWS EC2 Instance Requirements
- **Instance Type**: t3.small or larger
- **Storage**: 20GB+ EBS volume
- **Security Group Rules**:
  ```
  Inbound:
  - HTTP (80): 0.0.0.0/0
  - HTTPS (443): 0.0.0.0/0
  - Custom TCP (8000): 0.0.0.0/0
  - SSH (22): Your IP/32
  
  Outbound:
  - All Traffic: 0.0.0.0/0
  ```

## 🚀 Quick Deployment

### 1. Configure Deployment Script

Edit the deployment script with your EC2 details:

```bash
# Edit deploy/ec2-deploy.sh
EC2_INSTANCE_IP="your-ec2-ip-address"
EC2_KEY_PATH="/path/to/your/key.pem"
REGISTRY_URL=""  # Optional: for Docker registry
```

### 2. Set Environment Variables

Copy and configure the production environment:

```bash
cp production.env .env
# Edit .env with your actual values
```

### 3. Run Deployment

```bash
# Make deployment script executable
chmod +x deploy/ec2-deploy.sh

# Deploy to EC2
./deploy/ec2-deploy.sh -i YOUR_EC2_IP -k /path/to/key.pem
```

## 📝 Detailed Deployment Steps

### Step 1: Build and Test Locally

```bash
# Build Docker image
docker build -t guardian-orchestrator .

# Test locally
docker-compose up -d
curl http://localhost:8000/ag-ui/health

# Stop local services
docker-compose down
```

### Step 2: Configure Production Environment

```bash
# Copy production environment template
cp production.env .env

# Edit with your values
nano .env
```

**Required Environment Variables:**
```bash
# Security (CHANGE THESE!)
SECRET_KEY=your-super-secret-production-key
JWT_SECRET_KEY=your-jwt-secret-key-32-chars-minimum
ENCRYPTION_KEY=your-encryption-key-exactly-32-chars

# External Agent URLs
HOTEL_AGENT_URL=https://hotel-agent.your-domain.com/a2a/tasks
HOSPITAL_AGENT_URL=https://hospital-agent.your-domain.com/a2a/tasks
VOICE_AGENT_URL=https://voice-agent.your-domain.com/a2a/tasks
NOTIFICATION_AGENT_URL=https://notification-system-h36d.onrender.com/a2a/tasks
FLIGHT_AGENT_URL=https://flight-agent.example.com/a2a

# Optional: LLM Integration
OPENAI_API_KEY=your_openai_api_key_here
```

### Step 3: Deploy to EC2

```bash
# Method 1: Using deployment script
./deploy/ec2-deploy.sh -i ec2-host.example.com -k ~/.ssh/my-key.pem

# Method 2: Manual deployment
scp -i ~/.ssh/my-key.pem -r . ec2-user@ec2-host.example.com:/home/ec2-user/guardian/
ssh -i ~/.ssh/my-key.pem ec2-user@ec2-host.example.com
cd /home/ec2-user/guardian
docker-compose up -d
```

### Step 4: Verify Deployment

```bash
# Check service health
curl http://YOUR_EC2_IP:8000/ag-ui/health

# Check Docker containers
ssh -i ~/.ssh/my-key.pem ec2-user@YOUR_EC2_IP
docker ps
docker logs guardian-orchestrator
```

## 🔍 Health Monitoring

### Automated Health Checks

```bash
# Run health checks
./deploy/health-monitor.sh --check

# Start continuous monitoring
./deploy/health-monitor.sh --monitor

# Generate health report
./deploy/health-monitor.sh --generate
```

### Manual Health Checks

```bash
# Service endpoints
curl http://YOUR_EC2_IP:8000/ag-ui/health
curl http://YOUR_EC2_IP:8000/guardian/health

# Docker container status
docker ps
docker logs guardian-orchestrator --since 1h

# System resources
df -h
free -h
uptime
```

## 🔒 Security Configuration

### SSL/TLS Setup (Optional)

1. **Obtain SSL Certificate**:
   ```bash
   # Using Let's Encrypt
   sudo certbot certonly --standalone -d your-domain.com
   ```

2. **Configure Nginx**:
   ```bash
   # Uncomment HTTPS section in nginx.conf
   # Update SSL certificate paths
   ```

3. **Update Docker Compose**:
   ```bash
   # Enable nginx profile
   docker-compose --profile with-nginx up -d
   ```

### Security Best Practices

- ✅ Use strong passwords and secrets
- ✅ Enable firewall (ufw/iptables)
- ✅ Keep system packages updated
- ✅ Use HTTPS in production
- ✅ Regular security audits
- ✅ Monitor access logs

## 📊 Monitoring and Logging

### Log Locations

```bash
# Application logs
docker logs guardian-orchestrator

# System logs
/var/log/guardian-health.log

# Nginx logs (if enabled)
/var/log/nginx/access.log
/var/log/nginx/error.log
```

### Performance Monitoring

```bash
# Container resource usage
docker stats guardian-orchestrator

# System monitoring
htop
iostat
netstat -tulpn
```

## 🔄 Maintenance and Updates

### Updating the Application

```bash
# Pull latest code
git pull origin main

# Rebuild and deploy
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# Verify deployment
curl http://YOUR_EC2_IP:8000/ag-ui/health
```

### Backup and Recovery

```bash
# Backup application data
docker exec guardian-orchestrator tar czf /tmp/backup.tar.gz /app/data

# Backup Docker volumes
docker run --rm -v guardian_data:/data -v $(pwd):/backup alpine tar czf /backup/data-backup.tar.gz /data
```

### Scaling

```bash
# Scale application (if using load balancer)
docker-compose up -d --scale guardian-orchestrator=3

# Add Redis for session management
docker-compose --profile with-redis up -d

# Add PostgreSQL for persistent data
docker-compose --profile with-postgres up -d
```

## 🚨 Troubleshooting

### Common Issues

1. **Service Not Starting**:
   ```bash
   # Check logs
   docker logs guardian-orchestrator
   
   # Check environment variables
   docker-compose config
   
   # Restart services
   docker-compose restart
   ```

2. **External Agent Connectivity**:
   ```bash
   # Test connectivity
   curl -v "$FLIGHT_AGENT_URL"
   curl -v https://notification-system-h36d.onrender.com/a2a/tasks
   ```

3. **High Memory Usage**:
   ```bash
   # Check memory usage
   docker stats guardian-orchestrator
   
   # Restart container
   docker-compose restart guardian-orchestrator
   ```

4. **SSL Certificate Issues**:
   ```bash
   # Check certificate
   openssl x509 -in /etc/nginx/ssl/cert.pem -text -noout
   
   # Renew certificate
   sudo certbot renew
   ```

### Emergency Procedures

1. **Service Down**:
   ```bash
   # Quick restart
   docker-compose restart guardian-orchestrator
   
   # Full restart
   docker-compose down && docker-compose up -d
   ```

2. **Data Recovery**:
   ```bash
   # Restore from backup
   docker run --rm -v guardian_data:/data -v $(pwd):/backup alpine tar xzf /backup/data-backup.tar.gz -C /
   ```

## 📞 Support and Maintenance

### Health Check Endpoints

- **Main Health**: `GET /ag-ui/health`
- **API Health**: `GET /guardian/health`
- **Scheduler Status**: `GET /guardian/scheduler/status`

### Monitoring Dashboard

Access the monitoring dashboard at:
- **Health Status**: `http://YOUR_EC2_IP:8000/ag-ui/health`
- **API Documentation**: `http://YOUR_EC2_IP:8000/docs`

Successful startup only verifies that the configured process and health endpoint respond. Availability, security, scalability, monitoring coverage, backups, and regulated-data controls require separate deployment-specific validation.
