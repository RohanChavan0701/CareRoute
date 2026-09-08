#!/bin/bash

# Guardian Orchestrator - Final EC2 Deployment Script
# This script handles complete deployment to EC2 with error handling and rollback

set -e

# Configuration
EC2_IP=${1:-""}
SSH_KEY_PATH=${2:-"deploy/codefest.pem"}
EC2_USER=${3:-"ubuntu"}
APP_DIR="/opt/guardian-orchestrator"
BACKUP_DIR="/opt/guardian-orchestrator-backup"

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

# Function to check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    if [ ! -f "$SSH_KEY_PATH" ]; then
        print_error "SSH key not found: $SSH_KEY_PATH"
        exit 1
    fi
    
    if [ ! -x "$SSH_KEY_PATH" ]; then
        print_warning "Setting SSH key permissions..."
        chmod 400 "$SSH_KEY_PATH"
    fi
    
    # Test SSH connection
    print_status "Testing SSH connection to EC2..."
    if ! ssh -i "$SSH_KEY_PATH" -o ConnectTimeout=10 -o StrictHostKeyChecking=no "$EC2_USER@$EC2_IP" "echo 'SSH connection successful'" > /dev/null 2>&1; then
        print_error "Cannot connect to EC2 instance. Check IP, key, and security groups."
        exit 1
    fi
    
    print_success "Prerequisites check passed"
}

# Function to create backup
create_backup() {
    print_status "Creating backup of current deployment..."
    
    ssh -i "$SSH_KEY_PATH" "$EC2_USER@$EC2_IP" << EOF
        set -e
        
        # Stop current container if running
        if docker ps | grep -q guardian-orchestrator; then
            echo "Stopping current container..."
            cd $APP_DIR && docker-compose down || true
        fi
        
        # Create backup
        if [ -d "$APP_DIR" ]; then
            echo "Creating backup..."
            sudo rm -rf $BACKUP_DIR || true
            sudo cp -r $APP_DIR $BACKUP_DIR
            echo "Backup created at $BACKUP_DIR"
        else
            echo "No existing deployment found"
        fi
EOF
    
    print_success "Backup created successfully"
}

# Function to deploy application
deploy_application() {
    print_status "Deploying Guardian Orchestrator to EC2..."
    
    # Create deployment archive
    print_status "Creating deployment archive..."
    tar -czf guardian-orchestrator.tar.gz \
        --exclude='.git' \
        --exclude='__pycache__' \
        --exclude='*.pyc' \
        --exclude='.DS_Store' \
        --exclude='venv' \
        --exclude='.venv' \
        --exclude='logs' \
        --exclude='data' \
        --exclude='*.log' \
        backend/ deploy/ tests/ samples/ \
        Dockerfile docker-compose.yml nginx.conf production.env hipaa.env.example \
        README.md DEPLOYMENT.md *.md
    
    # Copy files to EC2
    print_status "Copying files to EC2 instance..."
    scp -i "$SSH_KEY_PATH" guardian-orchestrator.tar.gz "$EC2_USER@$EC2_IP:/tmp/"
    
    # Deploy on EC2
    print_status "Deploying application on EC2..."
    ssh -i "$SSH_KEY_PATH" "$EC2_USER@$EC2_IP" << EOF
        set -e
        
        # Extract files
        echo "Extracting deployment files..."
        sudo rm -rf $APP_DIR
        sudo mkdir -p $APP_DIR
        sudo tar -xzf /tmp/guardian-orchestrator.tar.gz -C $APP_DIR
        sudo chown -R $EC2_USER:$EC2_USER $APP_DIR
        
        # Build and start container
        echo "Building Docker image..."
        cd $APP_DIR
        docker build -t guardian-orchestrator .
        
        echo "Starting application..."
        docker-compose up -d
        
        # Clean up
        rm -f /tmp/guardian-orchestrator.tar.gz
        
        echo "Deployment completed on EC2"
EOF
    
    # Clean up local archive
    rm -f guardian-orchestrator.tar.gz
    
    print_success "Application deployed successfully"
}

# Function to verify deployment
verify_deployment() {
    print_status "Verifying deployment..."
    
    # Wait for application to start
    print_status "Waiting for application to start..."
    sleep 10
    
    # Check container status
    ssh -i "$SSH_KEY_PATH" "$EC2_USER@$EC2_IP" << EOF
        echo "Checking container status..."
        docker ps -f name=guardian-orchestrator
        
        echo "Checking container health..."
        docker inspect --format='{{.State.Health.Status}}' guardian-orchestrator || echo "No health check configured"
EOF
    
    # Test health endpoint
    print_status "Testing health endpoint..."
    if curl -f -s "http://$EC2_IP:8000/health" > /dev/null; then
        print_success "Health check passed"
        
        # Show health response
        print_status "Health endpoint response:"
        curl -s "http://$EC2_IP:8000/health" | python3 -m json.tool || curl -s "http://$EC2_IP:8000/health"
    else
        print_error "Health check failed"
        return 1
    fi
}

# Function to rollback deployment
rollback_deployment() {
    print_warning "Rolling back deployment..."
    
    ssh -i "$SSH_KEY_PATH" "$EC2_USER@$EC2_IP" << EOF
        set -e
        
        # Stop current container
        cd $APP_DIR && docker-compose down || true
        
        # Restore backup
        if [ -d "$BACKUP_DIR" ]; then
            echo "Restoring from backup..."
            sudo rm -rf $APP_DIR
            sudo mv $BACKUP_DIR $APP_DIR
            sudo chown -R $EC2_USER:$EC2_USER $APP_DIR
            
            # Start restored application
            cd $APP_DIR && docker-compose up -d
            
            echo "Rollback completed"
        else
            echo "No backup found for rollback"
        fi
EOF
    
    print_warning "Rollback completed"
}

# Function to show deployment info
show_deployment_info() {
    print_success "🚀 Guardian Orchestrator deployed successfully!"
    echo ""
    echo "📋 Deployment Information:"
    echo "  • EC2 Instance: $EC2_IP"
    echo "  • Application Directory: $APP_DIR"
    echo "  • Container Name: guardian-orchestrator"
    echo ""
    echo "🌐 Access URLs:"
    echo "  • Direct API: http://$EC2_IP:8000/health"
    echo "  • Health Check: http://$EC2_IP:8000/health"
    echo "  • Nginx Proxy: http://$EC2_IP (if configured)"
    echo ""
    echo "🔧 Management Commands:"
    echo "  • View logs: ssh -i $SSH_KEY_PATH $EC2_USER@$EC2_IP 'cd $APP_DIR && docker-compose logs -f'"
    echo "  • Restart: ssh -i $SSH_KEY_PATH $EC2_USER@$EC2_IP 'cd $APP_DIR && docker-compose restart'"
    echo "  • Stop: ssh -i $SSH_KEY_PATH $EC2_USER@$EC2_IP 'cd $APP_DIR && docker-compose down'"
    echo ""
    echo "📊 Test the deployment:"
    echo "  curl -s http://$EC2_IP:8000/health | python3 -m json.tool"
}

# Main deployment function
main() {
    echo "🚀 Guardian Orchestrator - Final EC2 Deployment"
    echo "=============================================="
    echo ""
    
    # Check arguments
    if [ $# -lt 1 ]; then
        echo "Usage: $0 <EC2_IP> [SSH_KEY_PATH] [EC2_USER]"
        echo ""
        echo "Example: $0 ec2-host.example.com deploy/codefest.pem ubuntu"
        exit 1
    fi
    
    print_status "Starting deployment to EC2 instance: $EC2_IP"
    echo ""
    
    # Execute deployment steps
    check_prerequisites
    create_backup
    
    if deploy_application && verify_deployment; then
        show_deployment_info
        print_success "✅ Deployment completed successfully!"
        exit 0
    else
        print_error "❌ Deployment failed!"
        rollback_deployment
        exit 1
    fi
}

# Run main function
main "$@"
