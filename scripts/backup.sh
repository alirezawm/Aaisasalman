#!/bin/bash

# ========================================
# Database Backup Script
# Asia Salman Flask Application
# ========================================

set -e

# Configuration
BACKUP_DIR="/backups"
INSTANCE_DIR="/data/instance"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/asia_salman_backup_$DATE.db"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
    exit 1
}

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

# Check if database file exists
if [ ! -f "$INSTANCE_DIR/asia_salman.db" ]; then
    error "Database file not found: $INSTANCE_DIR/asia_salman.db"
fi

# Create backup
log "Creating database backup..."
cp "$INSTANCE_DIR/asia_salman.db" "$BACKUP_FILE"

# Compress backup
log "Compressing backup..."
gzip "$BACKUP_FILE"
BACKUP_FILE="$BACKUP_FILE.gz"

# Verify backup
if [ -f "$BACKUP_FILE" ]; then
    log "Backup created successfully: $BACKUP_FILE"
    log "Backup size: $(du -h "$BACKUP_FILE" | cut -f1)"
else
    error "Backup creation failed"
fi

# Cleanup old backups (keep last 7 days)
log "Cleaning up old backups..."
find "$BACKUP_DIR" -name "asia_salman_backup_*.db.gz" -mtime +7 -delete

log "Backup process completed successfully"
