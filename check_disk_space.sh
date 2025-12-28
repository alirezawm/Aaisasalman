#!/bin/bash

# Script to check disk space and identify what's using space

echo "=========================================="
echo "Disk Space Analysis"
echo "=========================================="
echo ""

# Check overall disk usage
echo "📊 Overall Disk Usage:"
df -h
echo ""

# Check root filesystem specifically
echo "📊 Root Filesystem (/):"
df -h /
echo ""

# Find largest directories in root (top 10)
echo "🔍 Top 10 Largest Directories in /root:"
du -h --max-depth=1 /root 2>/dev/null | sort -rh | head -10
echo ""

# Check for large log files
echo "📄 Large Log Files (>100MB):"
find /var/log -type f -size +100M 2>/dev/null | head -10
echo ""

# Check Docker disk usage (if Docker is installed)
if command -v docker &> /dev/null; then
    echo "🐳 Docker Disk Usage:"
    docker system df
    echo ""
fi

# Check for old/unused packages
echo "📦 Checking for old kernels and packages..."
echo "Old kernels: $(dpkg -l | grep -E 'linux-image-[0-9]+' | wc -l) installed"
echo ""

# Check tmp directory size
echo "🗑️  /tmp directory size:"
du -sh /tmp 2>/dev/null || echo "Cannot access /tmp"
echo ""

echo "=========================================="
echo "Recommendations:"
echo "=========================================="
echo "1. Clean Docker (if installed): docker system prune -a --volumes"
echo "2. Clean apt cache: apt-get clean && apt-get autoremove -y"
echo "3. Remove old logs: journalctl --vacuum-time=7d"
echo "4. Remove old kernels: apt-get autoremove --purge"
echo "5. Clear /tmp: rm -rf /tmp/* (be careful!)"
echo "=========================================="


