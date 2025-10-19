#!/bin/bash

# ========================================
# Asia Salman Flask App Deployment Script
# Production deployment for Linux servers
# ========================================

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
APP_NAME="asia-salman"
COMPOSE_FILE="docker-compose.yaml"
BACKUP_DIR="./backups"
LOG_FILE="./deployment.log"

# Functions
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1" | tee -a "$LOG_FILE"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_FILE"
    exit 1
}

# Check if running as root
check_root() {
    if [[ $EUID -eq 0 ]]; then
        error "This script should not be run as root for security reasons"
    fi
}

# Check prerequisites
check_prerequisites() {
    log "Checking prerequisites..."
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        error "Docker is not installed. Please install Docker first."
    fi
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        error "Docker Compose is not installed. Please install Docker Compose first."
    fi
    
    # Check if Docker daemon is running
    if ! docker info &> /dev/null; then
        error "Docker daemon is not running. Please start Docker service."
    fi
    
    success "Prerequisites check passed"
}

# Create necessary directories
create_directories() {
    log "Creating necessary directories..."
    
    mkdir -p "$BACKUP_DIR"
    mkdir -p ./logs
    mkdir -p ./ssl_certs
    
    success "Directories created"
}

# Backup existing data
backup_data() {
    log "Creating backup of existing data..."
    
    if [ -d "./instance" ]; then
        BACKUP_FILE="$BACKUP_DIR/backup-$(date +%Y%m%d-%H%M%S).tar.gz"
        tar -czf "$BACKUP_FILE" ./instance ./uploads 2>/dev/null || warning "Backup creation failed or no data to backup"
        success "Backup created: $BACKUP_FILE"
    else
        warning "No existing data to backup"
    fi
}

# Pull latest images
pull_images() {
    log "Pulling latest images..."
    
    docker-compose -f "$COMPOSE_FILE" pull || warning "Failed to pull some images"
    success "Images pulled"
}

# Build application
build_app() {
    log "Building application..."
    
    docker-compose -f "$COMPOSE_FILE" build --no-cache || error "Build failed"
    success "Application built successfully"
}

# Stop existing containers
stop_containers() {
    log "Stopping existing containers..."
    
    docker-compose -f "$COMPOSE_FILE" down || warning "Some containers were not running"
    success "Containers stopped"
}

# Start services
start_services() {
    log "Starting services..."
    
    docker-compose -f "$COMPOSE_FILE" up -d || error "Failed to start services"
    success "Services started"
}

# Wait for services to be ready
wait_for_services() {
    log "Waiting for services to be ready..."
    
    # Wait for web service
    local max_attempts=30
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if docker-compose -f "$COMPOSE_FILE" exec -T web curl -f http://localhost:8000/health &> /dev/null; then
            success "Web service is ready"
            break
        fi
        
        if [ $attempt -eq $max_attempts ]; then
            error "Web service failed to start within expected time"
        fi
        
        log "Waiting for web service... (attempt $attempt/$max_attempts)"
        sleep 10
        ((attempt++))
    done
    
    # Wait for Redis
    attempt=1
    while [ $attempt -le $max_attempts ]; do
        if docker-compose -f "$COMPOSE_FILE" exec -T redis redis-cli ping &> /dev/null; then
            success "Redis service is ready"
            break
        fi
        
        if [ $attempt -eq $max_attempts ]; then
            error "Redis service failed to start within expected time"
        fi
        
        log "Waiting for Redis service... (attempt $attempt/$max_attempts)"
        sleep 5
        ((attempt++))
    done
}

# Run database migrations
run_migrations() {
    log "Running database migrations..."
    
    docker-compose -f "$COMPOSE_FILE" exec -T web python -c "
import sys
sys.path.append('/usr/src/app')
from app import app
from models import db
with app.app_context():
    db.create_all()
    print('Database tables created/updated successfully')
" || warning "Database migration failed"
    
    success "Database migrations completed"
}

# Health check
health_check() {
    log "Performing health check..."
    
    # Check web service
    if curl -f http://localhost/health &> /dev/null; then
        success "Application health check passed"
    else
        error "Application health check failed"
    fi
}

# Show service status
show_status() {
    log "Service status:"
    docker-compose -f "$COMPOSE_FILE" ps
}

# Cleanup old images
cleanup() {
    log "Cleaning up old Docker images..."
    
    docker image prune -f || warning "Image cleanup failed"
    success "Cleanup completed"
}

# Main deployment function
deploy() {
    log "Starting deployment of $APP_NAME..."
    
    check_root
    check_prerequisites
    create_directories
    backup_data
    pull_images
    build_app
    stop_containers
    start_services
    wait_for_services
    run_migrations
    health_check
    show_status
    cleanup
    
    success "Deployment completed successfully!"
    log "Application is available at: http://localhost"
    log "Admin panel: http://localhost/admin"
    log "Health check: http://localhost/health"
}

# Rollback function
rollback() {
    log "Starting rollback..."
    
    stop_containers
    
    # Find latest backup
    LATEST_BACKUP=$(ls -t "$BACKUP_DIR"/backup-*.tar.gz 2>/dev/null | head -n1)
    
    if [ -n "$LATEST_BACKUP" ]; then
        log "Restoring from backup: $LATEST_BACKUP"
        tar -xzf "$LATEST_BACKUP" || error "Backup restoration failed"
        success "Backup restored"
    else
        warning "No backup found for rollback"
    fi
    
    start_services
    wait_for_services
    
    success "Rollback completed"
}

# Show help
show_help() {
    echo "Usage: $0 [OPTION]"
    echo ""
    echo "Options:"
    echo "  deploy     Deploy the application (default)"
    echo "  rollback   Rollback to previous version"
    echo "  status     Show service status"
    echo "  logs       Show application logs"
    echo "  stop       Stop all services"
    echo "  start      Start all services"
    echo "  restart    Restart all services"
    echo "  help       Show this help message"
    echo ""
}

# Handle command line arguments
case "${1:-deploy}" in
    deploy)
        deploy
        ;;
    rollback)
        rollback
        ;;
    status)
        show_status
        ;;
    logs)
        docker-compose -f "$COMPOSE_FILE" logs -f
        ;;
    stop)
        docker-compose -f "$COMPOSE_FILE" down
        ;;
    start)
        docker-compose -f "$COMPOSE_FILE" up -d
        ;;
    restart)
        docker-compose -f "$COMPOSE_FILE" restart
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        error "Unknown option: $1. Use 'help' for usage information."
        ;;
esac
