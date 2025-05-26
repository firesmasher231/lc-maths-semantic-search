#!/bin/bash

# LC Mathematics Search - Docker Deployment Script
# Usage: ./deploy.sh [build|start|stop|restart|logs|status]

set -e

APP_NAME="lc-math-search"
IMAGE_NAME="lc-math-search:latest"

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

# Check if Docker is installed
check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
}

# Create necessary directories
setup_directories() {
    print_status "Setting up directories..."
    mkdir -p data/papers
    mkdir -p logs
    print_success "Directories created"
}

# Build the Docker image
build_image() {
    print_status "Building Docker image..."
    docker-compose build --no-cache
    print_success "Docker image built successfully"
}

# Start the application
start_app() {
    print_status "Starting LC Mathematics Search application..."
    docker-compose up -d
    print_success "Application started successfully"
    print_status "Application will be available at: http://localhost:5000"
    print_status "Use './deploy.sh logs' to view application logs"
}

# Stop the application
stop_app() {
    print_status "Stopping LC Mathematics Search application..."
    docker-compose down
    print_success "Application stopped successfully"
}

# Restart the application
restart_app() {
    print_status "Restarting LC Mathematics Search application..."
    docker-compose restart
    print_success "Application restarted successfully"
}

# Show application logs
show_logs() {
    print_status "Showing application logs (Press Ctrl+C to exit)..."
    docker-compose logs -f
}

# Show application status
show_status() {
    print_status "Application Status:"
    docker-compose ps
    
    if docker-compose ps | grep -q "Up"; then
        print_success "Application is running"
        print_status "Health check: $(curl -s http://localhost:5000/api/status | jq -r '.status' 2>/dev/null || echo 'Unable to connect')"
    else
        print_warning "Application is not running"
    fi
}

# Update application (pull latest code and rebuild)
update_app() {
    print_status "Updating application..."
    
    # Stop current container
    docker-compose down
    
    # Pull latest code (if using git)
    if [ -d ".git" ]; then
        print_status "Pulling latest code from git..."
        git pull
    fi
    
    # Rebuild and start
    docker-compose build --no-cache
    docker-compose up -d
    
    print_success "Application updated successfully"
}

# Main script logic
case "${1:-help}" in
    "build")
        check_docker
        setup_directories
        build_image
        ;;
    "start")
        check_docker
        setup_directories
        start_app
        ;;
    "stop")
        check_docker
        stop_app
        ;;
    "restart")
        check_docker
        restart_app
        ;;
    "logs")
        check_docker
        show_logs
        ;;
    "status")
        check_docker
        show_status
        ;;
    "update")
        check_docker
        update_app
        ;;
    "deploy")
        check_docker
        setup_directories
        build_image
        start_app
        ;;
    "help"|*)
        echo "LC Mathematics Search - Deployment Script"
        echo ""
        echo "Usage: $0 [command]"
        echo ""
        echo "Commands:"
        echo "  build     - Build the Docker image"
        echo "  start     - Start the application"
        echo "  stop      - Stop the application"
        echo "  restart   - Restart the application"
        echo "  logs      - Show application logs"
        echo "  status    - Show application status"
        echo "  update    - Update and redeploy application"
        echo "  deploy    - Full deployment (build + start)"
        echo "  help      - Show this help message"
        echo ""
        echo "Examples:"
        echo "  $0 deploy    # First time deployment"
        echo "  $0 start     # Start existing application"
        echo "  $0 logs      # View logs"
        echo "  $0 update    # Update to latest version"
        ;;
esac 