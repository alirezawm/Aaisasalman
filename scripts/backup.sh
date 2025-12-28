#!/bin/bash

# ========================================
# Database Backup Script
# Asia Salman Flask Application
# ========================================

set -e

# Configuration
BACKUP_DIR="/backups"
# Database locations (check new location first, then old locations)
DB_PATHS=(
    "/root/data/asia_salman.db"
    "/data/instance/asia_salman.db"
    "/root/application/instance/asia_salman.db"
)
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

# Find database file
DB_FILE=""
for db_path in "${DB_PATHS[@]}"; do
    if [ -f "$db_path" ]; then
        DB_FILE="$db_path"
        break
    fi
done

# Check if database file exists
if [ -z "$DB_FILE" ]; then
    error "Database file not found. Searched in: ${DB_PATHS[*]}"
fi

# Create backup
log "Creating database backup from: $DB_FILE"
cp "$DB_FILE" "$BACKUP_FILE"

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
