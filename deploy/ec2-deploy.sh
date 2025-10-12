#!/bin/bash

# Guardian A2A Orchestrator - EC2 Deployment Script
# This script deploys the Guardian Orchestrator to an AWS EC2 instance

set -e  # Exit on any error

# Configuration
EC2_INSTANCE_IP=""
EC2_USER="ec2-user"
EC2_KEY_PATH=""
DOCKER_IMAGE_NAME="guardian-orchestrator"
DOCKER_TAG="latest"
REGISTRY_URL=""  # Optional: AWS ECR or Docker Hub

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

# Function to check if required tools are installed
check_requirements() {
    print_status "Checking requirements..."
    
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    if ! command -v ssh &> /dev/null; then
        print_error "SSH is not installed. Please install SSH client first."
        exit 1
    fi
    
    if ! command -v scp &> /dev/null; then
        print_error "SCP is not installed. Please install SCP client first."
        exit 1
    fi
    
    print_success "All requirements are met!"
}

# Function to build Docker image
build_image() {
    print_status "Building Docker image..."
    
    docker build -t ${DOCKER_IMAGE_NAME}:${DOCKER_TAG} .
    
    if [ $? -eq 0 ]; then
        print_success "Docker image built successfully!"
    else
        print_error "Failed to build Docker image!"
        exit 1
    fi
}

# Function to push image to registry (optional)
push_image() {
    if [ -n "$REGISTRY_URL" ]; then
        print_status "Pushing image to registry..."
        
        docker tag ${DOCKER_IMAGE_NAME}:${DOCKER_TAG} ${REGISTRY_URL}/${DOCKER_IMAGE_NAME}:${DOCKER_TAG}
        docker push ${REGISTRY_URL}/${DOCKER_IMAGE_NAME}:${DOCKER_TAG}
        
        if [ $? -eq 0 ]; then
            print_success "Image pushed to registry successfully!"
        else
            print_error "Failed to push image to registry!"
            exit 1
        fi
    else
        print_warning "No registry URL specified. Skipping image push."
    fi
}

# Function to prepare deployment files
prepare_deployment() {
    print_status "Preparing deployment files..."
    
    # Create deployment directory
    mkdir -p deploy/temp
    
    # Copy necessary files
    cp docker-compose.yml deploy/temp/
    cp nginx.conf deploy/temp/
    cp production.env deploy/temp/.env
    
    # Create deployment script for EC2
    cat > deploy/temp/deploy-on-server.sh << 'EOF'
#!/bin/bash

# Guardian Orchestrator - Server Deployment Script

set -e

print_status() {
    echo "[INFO] $1"
}

print_success() {
    echo "[SUCCESS] $1"
}

print_error() {
    echo "[ERROR] $1"
}

# Update system packages
print_status "Updating system packages..."
sudo yum update -y

# Install Docker if not installed
if ! command -v docker &> /dev/null; then
    print_status "Installing Docker..."
    sudo yum install -y docker
    sudo systemctl start docker
    sudo systemctl enable docker
    sudo usermod -a -G docker ec2-user
    print_success "Docker installed successfully!"
else
    print_status "Docker is already installed."
fi

# Install Docker Compose if not installed
if ! command -v docker-compose &> /dev/null; then
    print_status "Installing Docker Compose..."
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    sudo ln -sf /usr/local/bin/docker-compose /usr/bin/docker-compose
    print_success "Docker Compose installed successfully!"
else
    print_status "Docker Compose is already installed."
fi

# Stop existing containers
print_status "Stopping existing containers..."
docker-compose down || true

# Pull latest image (if using registry)
if [ -n "$REGISTRY_URL" ]; then
    print_status "Pulling latest image from registry..."
    docker pull ${REGISTRY_URL}/${DOCKER_IMAGE_NAME}:${DOCKER_TAG}
fi

# Start services
print_status "Starting Guardian Orchestrator services..."
docker-compose up -d

# Wait for services to be ready
print_status "Waiting for services to start..."
sleep 30

# Check service health
print_status "Checking service health..."
if curl -f http://localhost:8000/ag-ui/health; then
    print_success "Guardian Orchestrator is healthy and running!"
else
    print_error "Guardian Orchestrator health check failed!"
    docker-compose logs guardian-orchestrator
    exit 1
fi

print_success "Deployment completed successfully!"
print_status "Guardian Orchestrator is available at: http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4):8000"
EOF
    
    chmod +x deploy/temp/deploy-on-server.sh
    
    print_success "Deployment files prepared!"
}

# Function to deploy to EC2
deploy_to_ec2() {
    if [ -z "$EC2_INSTANCE_IP" ]; then
        print_error "EC2_INSTANCE_IP is not set. Please set it in the script."
        exit 1
    fi
    
    if [ -z "$EC2_KEY_PATH" ]; then
        print_error "EC2_KEY_PATH is not set. Please set it in the script."
        exit 1
    fi
    
    print_status "Deploying to EC2 instance: $EC2_INSTANCE_IP"
    
    # Upload files to EC2
    print_status "Uploading files to EC2..."
    scp -i "$EC2_KEY_PATH" -r deploy/temp/* ${EC2_USER}@${EC2_INSTANCE_IP}:/home/${EC2_USER}/guardian/
    
    # Execute deployment script on EC2
    print_status "Executing deployment on EC2..."
    ssh -i "$EC2_KEY_PATH" ${EC2_USER}@${EC2_INSTANCE_IP} << EOF
        mkdir -p /home/${EC2_USER}/guardian
        cd /home/${EC2_USER}/guardian
        chmod +x deploy-on-server.sh
        REGISTRY_URL="$REGISTRY_URL" DOCKER_IMAGE_NAME="$DOCKER_IMAGE_NAME" DOCKER_TAG="$DOCKER_TAG" ./deploy-on-server.sh
EOF
    
    if [ $? -eq 0 ]; then
        print_success "Deployment to EC2 completed successfully!"
        print_status "Guardian Orchestrator is running at: http://$EC2_INSTANCE_IP:8000"
    else
        print_error "Deployment to EC2 failed!"
        exit 1
    fi
}

# Function to setup security group rules
setup_security_group() {
    print_warning "Don't forget to configure your EC2 Security Group with the following rules:"
    echo ""
    echo "Inbound Rules:"
    echo "  - Type: HTTP, Port: 80, Source: 0.0.0.0/0"
    echo "  - Type: HTTPS, Port: 443, Source: 0.0.0.0/0"
    echo "  - Type: Custom TCP, Port: 8000, Source: 0.0.0.0/0 (for direct access)"
    echo "  - Type: SSH, Port: 22, Source: YOUR_IP/32"
    echo ""
    echo "Outbound Rules:"
    echo "  - Type: All Traffic, Port: All, Destination: 0.0.0.0/0"
}

# Function to show usage
show_usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -i, --ip IP_ADDRESS     EC2 instance IP address"
    echo "  -k, --key KEY_PATH      Path to EC2 private key file"
    echo "  -r, --registry URL      Docker registry URL (optional)"
    echo "  -t, --tag TAG           Docker image tag (default: latest)"
    echo "  -h, --help              Show this help message"
    echo ""
    echo "Environment Variables:"
    echo "  EC2_INSTANCE_IP         EC2 instance IP address"
    echo "  EC2_KEY_PATH            Path to EC2 private key file"
    echo "  REGISTRY_URL            Docker registry URL"
    echo ""
    echo "Example:"
    echo "  $0 -i 54.123.45.67 -k ~/.ssh/my-key.pem"
}

# Main execution
main() {
    echo "🚀 Guardian A2A Orchestrator - EC2 Deployment"
    echo "=============================================="
    
    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            -i|--ip)
                EC2_INSTANCE_IP="$2"
                shift 2
                ;;
            -k|--key)
                EC2_KEY_PATH="$2"
                shift 2
                ;;
            -r|--registry)
                REGISTRY_URL="$2"
                shift 2
                ;;
            -t|--tag)
                DOCKER_TAG="$2"
                shift 2
                ;;
            -h|--help)
                show_usage
                exit 0
                ;;
            *)
                print_error "Unknown option: $1"
                show_usage
                exit 1
                ;;
        esac
    done
    
    # Check requirements
    check_requirements
    
    # Build image
    build_image
    
    # Push image (if registry specified)
    push_image
    
    # Prepare deployment
    prepare_deployment
    
    # Deploy to EC2
    deploy_to_ec2
    
    # Show security group setup
    setup_security_group
    
    print_success "🎉 Deployment completed successfully!"
    print_status "Your Guardian Orchestrator is now running on EC2!"
}

# Run main function
main "$@"
