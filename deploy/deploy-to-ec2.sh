#!/bin/bash

# Guardian Orchestrator EC2 Deployment Script
# This script deploys the application to an EC2 instance

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if required parameters are provided
if [ $# -lt 2 ]; then
    echo "Usage: $0 <EC2_IP_ADDRESS> <SSH_KEY_PATH> [EC2_USER]"
    echo "Example: $0 3.15.123.45 ~/.ssh/guardian-key.pem ubuntu"
    exit 1
fi

EC2_IP=$1
SSH_KEY=$2
EC2_USER=${3:-ubuntu}

print_status "Deploying Guardian Orchestrator to EC2 instance: $EC2_IP"

# Check if SSH key exists
if [ ! -f "$SSH_KEY" ]; then
    print_error "SSH key not found: $SSH_KEY"
    exit 1
fi

# Set correct permissions for SSH key
chmod 400 "$SSH_KEY"

# Test SSH connection
print_status "Testing SSH connection..."
if ! ssh -i "$SSH_KEY" -o ConnectTimeout=10 -o StrictHostKeyChecking=no "$EC2_USER@$EC2_IP" "echo 'SSH connection successful'"; then
    print_error "Failed to connect to EC2 instance. Please check your IP address and SSH key."
    exit 1
fi

# Create deployment archive
print_status "Creating deployment archive..."
cd "$(dirname "$0")/.."
tar -czf guardian-deployment.tar.gz \
    --exclude='.git' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='.env' \
    --exclude='venv' \
    --exclude='.pytest_cache' \
    --exclude='node_modules' \
    backend/ \
    samples/ \
    tests/ \
    Dockerfile \
    docker-compose.yml \
    nginx.conf \
    production.env \
    deploy/

# Copy files to EC2
print_status "Copying files to EC2 instance..."
scp -i "$SSH_KEY" -o StrictHostKeyChecking=no guardian-deployment.tar.gz "$EC2_USER@$EC2_IP:/tmp/"

# Deploy on EC2
print_status "Deploying application on EC2..."
ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no "$EC2_USER@$EC2_IP" << 'EOF'
set -e

# Extract application files
cd /opt/guardian-orchestrator
sudo tar -xzf /tmp/guardian-deployment.tar.gz
sudo chown -R $USER:$USER /opt/guardian-orchestrator

# Copy production environment
sudo cp production.env .env

# Build and start the application
docker-compose down || true
docker-compose build --no-cache
docker-compose up -d

# Wait for application to start
echo "Waiting for application to start..."
sleep 30

# Check if application is running
if curl -f http://localhost:8000/ag-ui/health; then
    echo "✅ Application deployed successfully!"
else
    echo "❌ Application health check failed"
    echo "Checking logs..."
    docker-compose logs guardian-orchestrator
    exit 1
fi

# Clean up
rm /tmp/guardian-deployment.tar.gz
EOF

# Clean up local archive
rm guardian-deployment.tar.gz

print_success "Deployment completed successfully!"
print_status "Application is now running at:"
echo "  HTTP: http://$EC2_IP"
echo "  HTTPS: https://$EC2_IP (if SSL is configured)"
echo "  API Health: http://$EC2_IP/ag-ui/health"
echo "  Direct API: http://$EC2_IP:8000/ag-ui/health"

print_status "To check logs, run:"
echo "  ssh -i $SSH_KEY $EC2_USER@$EC2_IP 'cd /opt/guardian-orchestrator && docker-compose logs -f'"

print_status "To restart the application, run:"
echo "  ssh -i $SSH_KEY $EC2_USER@$EC2_IP 'cd /opt/guardian-orchestrator && docker-compose restart'"
