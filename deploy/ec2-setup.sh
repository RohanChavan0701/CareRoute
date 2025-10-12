#!/bin/bash

# Guardian Orchestrator EC2 Setup Script
# This script sets up the complete environment on a fresh Ubuntu EC2 instance

set -e

echo "🚀 Guardian Orchestrator EC2 Setup Starting..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Update system
print_status "Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install essential packages
print_status "Installing essential packages..."
sudo apt install -y \
    curl \
    wget \
    git \
    unzip \
    htop \
    vim \
    ufw \
    fail2ban \
    nginx \
    certbot \
    python3-certbot-nginx

# Install Docker
print_status "Installing Docker..."
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
rm get-docker.sh

# Install Docker Compose
print_status "Installing Docker Compose..."
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Configure firewall
print_status "Configuring firewall..."
sudo ufw --force enable
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 8000/tcp

# Configure fail2ban
print_status "Configuring fail2ban..."
sudo systemctl enable fail2ban
sudo systemctl start fail2ban

# Create application directory
print_status "Creating application directory..."
sudo mkdir -p /opt/guardian-orchestrator
sudo chown $USER:$USER /opt/guardian-orchestrator

# Create environment file
print_status "Creating environment configuration..."
sudo tee /opt/guardian-orchestrator/.env > /dev/null <<EOF
# Guardian Orchestrator Environment Configuration

# Application Settings
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO
SECRET_KEY=$(openssl rand -hex 32)

# External agent endpoints (AWS URLs for production)
HOTEL_AGENT_URL=https://hotel-agent.aws.region.elb.amazonaws.com
HOSPITAL_AGENT_URL=https://hospital-agent.aws.region.elb.amazonaws.com
VOICE_AGENT_URL=https://voice-agent.aws.region.elb.amazonaws.com
NOTIFICATION_AGENT_URL=https://notification-system-h36d.onrender.com/a2a/tasks
FLIGHT_AGENT_URL=http://54.158.27.0:8001/a2a

# LLM Integration (Optional)
OPENAI_API_KEY=

# Security Settings
JWT_SECRET_KEY=$(openssl rand -hex 32)
ENCRYPTION_KEY=$(openssl rand -hex 32)

# HIPAA Compliance
HIPAA_MODE=true
AUDIT_LOG_ENABLED=true
DATA_RETENTION_DAYS=2555

# Monitoring
PROMETHEUS_ENABLED=true
HEALTH_CHECK_INTERVAL_HOURS=1
EOF

# Create systemd service file
print_status "Creating systemd service..."
sudo tee /etc/systemd/system/guardian-orchestrator.service > /dev/null <<EOF
[Unit]
Description=Guardian Orchestrator
After=docker.service
Requires=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/opt/guardian-orchestrator
ExecStart=/usr/local/bin/docker-compose up -d
ExecStop=/usr/local/bin/docker-compose down
TimeoutStartSec=0
User=$USER

[Install]
WantedBy=multi-user.target
EOF

# Create Nginx configuration
print_status "Creating Nginx configuration..."
sudo tee /etc/nginx/sites-available/guardian-orchestrator > /dev/null <<EOF
server {
    listen 80;
    server_name _;

    # Rate limiting
    limit_req_zone \$binary_remote_addr zone=api:10m rate=10r/s;
    limit_req zone=api burst=20 nodelay;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;

    # Proxy to Guardian Orchestrator
    location / {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_cache_bypass \$http_upgrade;
        proxy_read_timeout 86400;
    }

    # Health check endpoint
    location /health {
        proxy_pass http://localhost:8000/ag-ui/health;
        access_log off;
    }
}
EOF

# Enable Nginx site
sudo ln -sf /etc/nginx/sites-available/guardian-orchestrator /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Test Nginx configuration
sudo nginx -t

# Create log rotation
print_status "Setting up log rotation..."
sudo tee /etc/logrotate.d/guardian-orchestrator > /dev/null <<EOF
/opt/guardian-orchestrator/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 $USER $USER
    postrotate
        docker-compose -f /opt/guardian-orchestrator/docker-compose.yml restart guardian-orchestrator
    endscript
}
EOF

# Create monitoring script
print_status "Creating monitoring script..."
sudo tee /opt/guardian-orchestrator/monitor.sh > /dev/null <<EOF
#!/bin/bash

# Guardian Orchestrator Health Monitor
LOG_FILE="/opt/guardian-orchestrator/logs/health.log"
mkdir -p /opt/guardian-orchestrator/logs

echo "\$(date): Checking Guardian Orchestrator health..." >> \$LOG_FILE

# Check if container is running
if ! docker ps | grep -q guardian-orchestrator; then
    echo "\$(date): Container not running, attempting restart..." >> \$LOG_FILE
    cd /opt/guardian-orchestrator && docker-compose up -d
fi

# Check health endpoint
if curl -f http://localhost:8000/ag-ui/health > /dev/null 2>&1; then
    echo "\$(date): Health check passed" >> \$LOG_FILE
else
    echo "\$(date): Health check failed" >> \$LOG_FILE
    # Restart if health check fails
    cd /opt/guardian-orchestrator && docker-compose restart guardian-orchestrator
fi

# Clean up old logs (keep last 7 days)
find /opt/guardian-orchestrator/logs -name "*.log" -mtime +7 -delete
EOF

sudo chmod +x /opt/guardian-orchestrator/monitor.sh

# Create cron job for monitoring
print_status "Setting up monitoring cron job..."
(crontab -l 2>/dev/null; echo "*/5 * * * * /opt/guardian-orchestrator/monitor.sh") | crontab -

# Start services
print_status "Starting services..."
sudo systemctl daemon-reload
sudo systemctl enable nginx
sudo systemctl start nginx

print_success "EC2 setup completed successfully!"
print_status "Next steps:"
echo "1. Copy your application files to /opt/guardian-orchestrator/"
echo "2. Run: cd /opt/guardian-orchestrator && docker-compose up -d"
echo "3. Configure your domain (optional)"
echo "4. Set up SSL certificate (optional)"

print_warning "Please log out and log back in for Docker group changes to take effect!"
