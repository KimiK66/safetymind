#!/bin/bash
# SafetyMind Deployment Script
# Automated deployment script for production environments

set -e

echo "🚀 SafetyMind Production Deployment Script"
echo "=========================================="

# Configuration
APP_NAME="safetymind"
DOCKER_IMAGE="safetymind:latest"
CONTAINER_NAME="safetymind-app"
PORT="8000"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is installed
check_docker() {
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    log_info "Docker is available"
}

# Check if docker-compose is installed
check_docker_compose() {
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    log_info "Docker Compose is available"
}

# Build Docker image
build_image() {
    log_info "Building Docker image..."
    docker build -t $DOCKER_IMAGE .
    log_info "Docker image built successfully"
}

# Stop existing container
stop_container() {
    if docker ps -q -f name=$CONTAINER_NAME | grep -q .; then
        log_info "Stopping existing container..."
        docker stop $CONTAINER_NAME
        docker rm $CONTAINER_NAME
        log_info "Existing container stopped and removed"
    fi
}

# Start new container
start_container() {
    log_info "Starting new container..."
    docker run -d \
        --name $CONTAINER_NAME \
        -p $PORT:8000 \
        --env-file .env.production \
        -v $(pwd)/data:/app/data \
        -v $(pwd)/logs:/app/logs \
        --restart unless-stopped \
        $DOCKER_IMAGE
    log_info "Container started successfully"
}

# Health check
health_check() {
    log_info "Performing health check..."
    sleep 10
    
    for i in {1..30}; do
        if curl -f http://localhost:$PORT/ > /dev/null 2>&1; then
            log_info "Health check passed! Application is running."
            return 0
        fi
        log_info "Health check attempt $i/30..."
        sleep 2
    done
    
    log_error "Health check failed. Application may not be running properly."
    return 1
}

# Show logs
show_logs() {
    log_info "Showing container logs..."
    docker logs $CONTAINER_NAME --tail 50
}

# Main deployment function
deploy() {
    log_info "Starting deployment process..."
    
    check_docker
    check_docker_compose
    
    # Check if production environment file exists
    if [ ! -f ".env.production" ]; then
        log_warn "Production environment file (.env.production) not found."
        log_info "Copying template and creating .env.production..."
        cp env.production.template .env.production
        log_warn "Please edit .env.production with your actual configuration before deploying."
        exit 1
    fi
    
    build_image
    stop_container
    start_container
    
    if health_check; then
        log_info "🎉 Deployment completed successfully!"
        log_info "Application is available at: http://localhost:$PORT"
        log_info "API documentation: http://localhost:$PORT/docs"
    else
        log_error "Deployment failed health check."
        show_logs
        exit 1
    fi
}

# Docker Compose deployment
deploy_compose() {
    log_info "Starting Docker Compose deployment..."
    
    check_docker_compose
    
    # Check if production environment file exists
    if [ ! -f ".env.production" ]; then
        log_warn "Production environment file (.env.production) not found."
        log_info "Copying template and creating .env.production..."
        cp env.production.template .env.production
        log_warn "Please edit .env.production with your actual configuration before deploying."
        exit 1
    fi
    
    # Stop existing services
    docker-compose down
    
    # Start services
    docker-compose up -d --build
    
    log_info "Docker Compose deployment completed!"
    log_info "Application is available at: http://localhost:$PORT"
}

# Show usage
usage() {
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  deploy        Deploy using Docker (single container)"
    echo "  compose       Deploy using Docker Compose (with PostgreSQL/Redis)"
    echo "  stop          Stop the application"
    echo "  logs          Show application logs"
    echo "  status        Show application status"
    echo "  health        Perform health check"
    echo ""
}

# Handle commands
case "${1:-deploy}" in
    deploy)
        deploy
        ;;
    compose)
        deploy_compose
        ;;
    stop)
        log_info "Stopping application..."
        docker stop $CONTAINER_NAME 2>/dev/null || docker-compose down
        log_info "Application stopped"
        ;;
    logs)
        show_logs
        ;;
    status)
        docker ps -f name=$CONTAINER_NAME
        ;;
    health)
        health_check
        ;;
    *)
        usage
        ;;
esac
