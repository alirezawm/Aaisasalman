#!/bin/bash

# Script to clean up disk space before installing packages
# This helps resolve "No space left on device" errors

echo "🧹 Starting disk space cleanup..."
echo ""

# Check current disk usage
echo "📊 Current disk usage:"
df -h /
echo ""

# Clean pip cache
echo "🗑️  Cleaning pip cache..."
pip cache purge 2>/dev/null || python3 -m pip cache purge 2>/dev/null || echo "⚠️  Could not clean pip cache (may not be installed yet)"
echo ""

# Clean pip download cache in user directory
if [ -d ~/.cache/pip ]; then
    echo "🗑️  Removing pip download cache from ~/.cache/pip..."
    rm -rf ~/.cache/pip/*
    echo "✅ Pip cache cleaned"
fi

# Clean temporary files
echo "🗑️  Cleaning temporary files..."
if [ -d /tmp ]; then
    find /tmp -type f -atime +7 -delete 2>/dev/null || true
    echo "✅ Temporary files cleaned"
fi

# Clean old logs (if any)
if [ -d /var/log ]; then
    echo "🗑️  Cleaning old log files..."
    sudo journalctl --vacuum-time=3d 2>/dev/null || true
    sudo find /var/log -type f -name "*.log" -mtime +7 -delete 2>/dev/null || true
    echo "✅ Log files cleaned"
fi

# Clean apt cache (if on Debian/Ubuntu)
if command -v apt-get &> /dev/null; then
    echo "🗑️  Cleaning apt cache..."
    sudo apt-get clean 2>/dev/null || true
    sudo apt-get autoclean 2>/dev/null || true
    echo "✅ Apt cache cleaned"
fi

# Clean Python __pycache__ directories (optional, be careful)
echo "🗑️  Cleaning Python cache files..."
find . -type d -name "__pycache__" -exec rm -r {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true
find . -type f -name "*.pyo" -delete 2>/dev/null || true
echo "✅ Python cache cleaned"

# Show disk usage after cleanup
echo ""
echo "📊 Disk usage after cleanup:"
df -h /
echo ""

# Show largest directories (top 10)
echo "📁 Largest directories in current location:"
du -h --max-depth=1 . 2>/dev/null | sort -rh | head -10 || true
echo ""

echo "✅ Cleanup complete!"
echo ""
echo "💡 If you still have space issues, consider:"
echo "   - Removing old virtual environments"
echo "   - Removing old Docker images/containers (if using Docker)"
echo "   - Checking for large log files"
echo "   - Removing unused packages"
