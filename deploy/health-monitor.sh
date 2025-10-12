#!/bin/bash

# Guardian A2A Orchestrator - Health Monitoring Script
# This script monitors the health of the Guardian Orchestrator services

set -e

# Configuration
BASE_URL="http://localhost:8000"
LOG_FILE="/var/log/guardian-health.log"
ALERT_EMAIL="admin@your-domain.com"
SLACK_WEBHOOK=""  # Optional: Slack webhook URL for alerts

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

# Function to log messages
log_message() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" >> "$LOG_FILE"
}

# Function to check if service is running
check_service_health() {
    local service_name="$1"
    local endpoint="$2"
    local expected_status="$3"
    
    print_status "Checking $service_name health..."
    
    response=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL$endpoint" || echo "000")
    
    if [ "$response" = "$expected_status" ]; then
        print_success "$service_name is healthy (HTTP $response)"
        log_message "HEALTHY: $service_name - HTTP $response"
        return 0
    else
        print_error "$service_name is unhealthy (HTTP $response)"
        log_message "UNHEALTHY: $service_name - HTTP $response"
        return 1
    fi
}

# Function to check Docker container status
check_docker_containers() {
    print_status "Checking Docker container status..."
    
    # Check if guardian-orchestrator container is running
    if docker ps --format "table {{.Names}}\t{{.Status}}" | grep -q "guardian-orchestrator.*Up"; then
        print_success "Guardian Orchestrator container is running"
        log_message "DOCKER: Guardian Orchestrator container is running"
    else
        print_error "Guardian Orchestrator container is not running"
        log_message "DOCKER: Guardian Orchestrator container is not running"
        return 1
    fi
    
    # Check container resource usage
    print_status "Checking container resource usage..."
    docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}" | grep guardian-orchestrator
    log_message "DOCKER: Container resource usage checked"
}

# Function to check system resources
check_system_resources() {
    print_status "Checking system resources..."
    
    # Check disk usage
    disk_usage=$(df / | awk 'NR==2 {print $5}' | sed 's/%//')
    if [ "$disk_usage" -gt 80 ]; then
        print_warning "Disk usage is high: ${disk_usage}%"
        log_message "SYSTEM: High disk usage: ${disk_usage}%"
    else
        print_success "Disk usage is normal: ${disk_usage}%"
        log_message "SYSTEM: Disk usage normal: ${disk_usage}%"
    fi
    
    # Check memory usage
    memory_usage=$(free | awk 'NR==2{printf "%.0f", $3*100/$2}')
    if [ "$memory_usage" -gt 80 ]; then
        print_warning "Memory usage is high: ${memory_usage}%"
        log_message "SYSTEM: High memory usage: ${memory_usage}%"
    else
        print_success "Memory usage is normal: ${memory_usage}%"
        log_message "SYSTEM: Memory usage normal: ${memory_usage}%"
    fi
    
    # Check CPU load
    cpu_load=$(uptime | awk -F'load average:' '{print $2}' | awk '{print $1}' | sed 's/,//')
    print_status "CPU load: $cpu_load"
    log_message "SYSTEM: CPU load: $cpu_load"
}

# Function to check external agent connectivity
check_external_agents() {
    print_status "Checking external agent connectivity..."
    
    # Check Flight Agent
    if curl -s --max-time 10 "http://54.158.27.0:8001/a2a" > /dev/null; then
        print_success "Flight Agent is reachable"
        log_message "EXTERNAL: Flight Agent is reachable"
    else
        print_warning "Flight Agent is not reachable"
        log_message "EXTERNAL: Flight Agent is not reachable"
    fi
    
    # Check Notification Agent
    if curl -s --max-time 10 "https://notification-system-h36d.onrender.com/a2a/tasks" > /dev/null; then
        print_success "Notification Agent is reachable"
        log_message "EXTERNAL: Notification Agent is reachable"
    else
        print_warning "Notification Agent is not reachable"
        log_message "EXTERNAL: Notification Agent is not reachable"
    fi
}

# Function to check application logs
check_application_logs() {
    print_status "Checking application logs for errors..."
    
    # Check for recent errors in container logs
    error_count=$(docker logs guardian-orchestrator --since 1h 2>&1 | grep -i "error\|exception\|failed" | wc -l)
    
    if [ "$error_count" -gt 0 ]; then
        print_warning "Found $error_count errors in the last hour"
        log_message "LOGS: Found $error_count errors in the last hour"
        
        # Show recent errors
        print_status "Recent errors:"
        docker logs guardian-orchestrator --since 1h 2>&1 | grep -i "error\|exception\|failed" | tail -5
    else
        print_success "No errors found in the last hour"
        log_message "LOGS: No errors found in the last hour"
    fi
}

# Function to send alert
send_alert() {
    local message="$1"
    local severity="$2"
    
    print_warning "Sending alert: $message"
    log_message "ALERT: $severity - $message"
    
    # Send email alert (if configured)
    if [ -n "$ALERT_EMAIL" ] && command -v mail &> /dev/null; then
        echo "$message" | mail -s "Guardian Orchestrator Alert - $severity" "$ALERT_EMAIL"
    fi
    
    # Send Slack alert (if configured)
    if [ -n "$SLACK_WEBHOOK" ]; then
        curl -X POST -H 'Content-type: application/json' \
            --data "{\"text\":\"🚨 Guardian Orchestrator Alert - $severity: $message\"}" \
            "$SLACK_WEBHOOK"
    fi
}

# Function to restart services if needed
restart_services_if_needed() {
    local needs_restart=false
    
    # Check if main service is unhealthy
    if ! check_service_health "Guardian Orchestrator" "/ag-ui/health" "200"; then
        needs_restart=true
    fi
    
    # Check if Docker container is not running
    if ! docker ps --format "table {{.Names}}" | grep -q "guardian-orchestrator"; then
        needs_restart=true
    fi
    
    if [ "$needs_restart" = true ]; then
        print_warning "Restarting Guardian Orchestrator services..."
        log_message "RESTART: Restarting services due to health issues"
        
        cd /home/ec2-user/guardian
        docker-compose restart guardian-orchestrator
        
        # Wait for service to be ready
        sleep 30
        
        # Check if restart was successful
        if check_service_health "Guardian Orchestrator" "/ag-ui/health" "200"; then
            print_success "Services restarted successfully"
            log_message "RESTART: Services restarted successfully"
        else
            print_error "Services restart failed"
            log_message "RESTART: Services restart failed"
            send_alert "Guardian Orchestrator restart failed" "CRITICAL"
        fi
    fi
}

# Function to generate health report
generate_health_report() {
    local report_file="/tmp/guardian-health-report-$(date +%Y%m%d-%H%M%S).txt"
    
    print_status "Generating health report: $report_file"
    
    cat > "$report_file" << EOF
Guardian A2A Orchestrator - Health Report
Generated: $(date)
Hostname: $(hostname)
Uptime: $(uptime)

=== SERVICE STATUS ===
EOF
    
    # Service health checks
    check_service_health "Guardian Orchestrator" "/ag-ui/health" "200" >> "$report_file" 2>&1
    check_service_health "Guardian API" "/guardian/health" "200" >> "$report_file" 2>&1
    
    cat >> "$report_file" << EOF

=== DOCKER STATUS ===
EOF
    
    # Docker status
    docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" >> "$report_file"
    
    cat >> "$report_file" << EOF

=== SYSTEM RESOURCES ===
EOF
    
    # System resources
    echo "Disk Usage:" >> "$report_file"
    df -h >> "$report_file"
    echo "" >> "$report_file"
    echo "Memory Usage:" >> "$report_file"
    free -h >> "$report_file"
    echo "" >> "$report_file"
    echo "CPU Load:" >> "$report_file"
    uptime >> "$report_file"
    
    cat >> "$report_file" << EOF

=== RECENT LOGS ===
EOF
    
    # Recent logs
    docker logs guardian-orchestrator --since 1h 2>&1 | tail -50 >> "$report_file"
    
    print_success "Health report generated: $report_file"
    log_message "REPORT: Health report generated: $report_file"
}

# Function to show usage
show_usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -c, --check           Run health checks only"
    echo "  -m, --monitor         Run continuous monitoring"
    echo "  -r, --restart         Restart services if unhealthy"
    echo "  -g, --generate        Generate health report"
    echo "  -l, --logs            Show recent logs"
    echo "  -h, --help            Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 --check            # Run health checks once"
    echo "  $0 --monitor          # Run continuous monitoring"
    echo "  $0 --restart          # Check and restart if needed"
    echo "  $0 --generate         # Generate health report"
}

# Main execution
main() {
    echo "🏥 Guardian A2A Orchestrator - Health Monitor"
    echo "=============================================="
    
    # Parse command line arguments
    case "${1:-}" in
        -c|--check)
            print_status "Running health checks..."
            check_service_health "Guardian Orchestrator" "/ag-ui/health" "200"
            check_service_health "Guardian API" "/guardian/health" "200"
            check_docker_containers
            check_system_resources
            check_external_agents
            check_application_logs
            print_success "Health checks completed!"
            ;;
        -m|--monitor)
            print_status "Starting continuous monitoring..."
            while true; do
                echo "--- Health Check at $(date) ---"
                main --check
                restart_services_if_needed
                echo "Sleeping for 5 minutes..."
                sleep 300
            done
            ;;
        -r|--restart)
            print_status "Checking and restarting if needed..."
            restart_services_if_needed
            ;;
        -g|--generate)
            generate_health_report
            ;;
        -l|--logs)
            print_status "Recent application logs:"
            docker logs guardian-orchestrator --since 1h
            ;;
        -h|--help)
            show_usage
            ;;
        *)
            print_error "Unknown option: ${1:-}"
            show_usage
            exit 1
            ;;
    esac
}

# Run main function
main "$@"
