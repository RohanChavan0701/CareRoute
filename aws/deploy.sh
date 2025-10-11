#!/bin/bash

# Guardian A2A Orchestrator AWS Deployment Script
# This script deploys the Guardian orchestrator to AWS ECS Fargate

set -e

# Configuration
AWS_REGION="us-east-1"
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
ECR_REPOSITORY="guardian-orchestrator"
ECS_CLUSTER="guardian-cluster"
ECS_SERVICE="guardian-orchestrator-service"

echo "🚀 Deploying Guardian A2A Orchestrator to AWS..."
echo "Region: $AWS_REGION"
echo "Account: $AWS_ACCOUNT_ID"

# Build and push Docker image to ECR
echo "📦 Building and pushing Docker image..."

# Create ECR repository if it doesn't exist
aws ecr describe-repositories --repository-names $ECR_REPOSITORY --region $AWS_REGION 2>/dev/null || \
aws ecr create-repository --repository-name $ECR_REPOSITORY --region $AWS_REGION

# Get ECR login token
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com

# Build image
docker build -t $ECR_REPOSITORY:latest .

# Tag and push
docker tag $ECR_REPOSITORY:latest $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPOSITORY:latest
docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPOSITORY:latest

echo "✅ Docker image pushed to ECR"

# Update ECS task definition
echo "🔄 Updating ECS task definition..."

# Replace placeholders in task definition
sed "s/ACCOUNT_ID/$AWS_ACCOUNT_ID/g; s/REGION/$AWS_REGION/g" aws/ecs-task-definition.json > aws/ecs-task-definition-updated.json

# Register new task definition
aws ecs register-task-definition \
    --cli-input-json file://aws/ecs-task-definition-updated.json \
    --region $AWS_REGION

echo "✅ Task definition updated"

# Update ECS service
echo "🔄 Updating ECS service..."

aws ecs update-service \
    --cluster $ECS_CLUSTER \
    --service $ECS_SERVICE \
    --task-definition guardian-orchestrator \
    --region $AWS_REGION \
    --force-new-deployment

echo "✅ Service updated"

# Wait for deployment to complete
echo "⏳ Waiting for deployment to complete..."
aws ecs wait services-stable \
    --cluster $ECS_CLUSTER \
    --services $ECS_SERVICE \
    --region $AWS_REGION

echo "🎉 Guardian A2A Orchestrator deployed successfully!"

# Get service endpoint
echo "🌐 Getting service endpoint..."
ALB_DNS=$(aws elbv2 describe-load-balancers \
    --names guardian-alb \
    --query 'LoadBalancers[0].DNSName' \
    --output text \
    --region $AWS_REGION 2>/dev/null || echo "N/A")

if [ "$ALB_DNS" != "N/A" ]; then
    echo "Service URL: http://$ALB_DNS"
    echo "Health Check: http://$ALB_DNS/health"
    echo "API Docs: http://$ALB_DNS/docs"
else
    echo "⚠️ Load balancer not found. Check your ALB configuration."
fi

# Clean up temporary files
rm -f aws/ecs-task-definition-updated.json

echo "✅ Deployment complete!"
