#!/bin/bash

# DockFlask Development Helper Script

set -e

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

# Function to show help
show_help() {
    echo "DockFlask Development Helper"
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  build       Build the Docker image"
    echo "  run         Run the application in production mode"
    echo "  dev         Run the application in development mode"
    echo "  stop        Stop all running containers"
    echo "  clean       Remove containers and images"
    echo "  logs        Show application logs"
    echo "  health      Check application health"
    echo "  help        Show this help message"
    echo ""
}

# Function to build the Docker image
build_image() {
    print_status "Building DockFlask Docker image..."
    docker-compose build
    print_success "Docker image built successfully!"
}

# Function to run in production mode
run_production() {
    print_status "Starting DockFlask in production mode..."
    docker-compose up -d
    print_success "Application started at http://localhost:5000"
}

# Function to run in development mode
run_development() {
    print_status "Starting DockFlask in development mode..."
    docker-compose --profile dev up -d
    print_success "Development server started at http://localhost:5001"
}

# Function to stop containers
stop_containers() {
    print_status "Stopping DockFlask containers..."
    docker-compose down
    print_success "Containers stopped successfully!"
}

# Function to clean up
clean_up() {
    print_status "Cleaning up containers and images..."
    docker-compose down --rmi all --volumes --remove-orphans
    print_success "Cleanup completed!"
}

# Function to show logs
show_logs() {
    print_status "Showing application logs..."
    docker-compose logs -f
}

# Function to check health
check_health() {
    print_status "Checking application health..."
    
    # Check if container is running
    if docker-compose ps | grep -q "Up"; then
        print_success "Container is running"
        
        # Try to access health endpoint
        if curl -f http://localhost:5000/api/health >/dev/null 2>&1; then
            print_success "Health check passed!"
            curl -s http://localhost:5000/api/health | python -m json.tool
        else
            print_warning "Health check failed - application may be starting up"
        fi
    else
        print_error "Container is not running"
        exit 1
    fi
}

# Main script logic
case "${1:-help}" in
    build)
        build_image
        ;;
    run)
        run_production
        ;;
    dev)
        run_development
        ;;
    stop)
        stop_containers
        ;;
    clean)
        clean_up
        ;;
    logs)
        show_logs
        ;;
    health)
        check_health
        ;;
    help|*)
        show_help
        ;;
esac
