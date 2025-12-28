#!/bin/bash

# Script to create and setup virtual environment for Asia Salman project

echo "Creating virtual environment..."

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "Error: python3 is not installed. Please install Python 3 first."
    exit 1
fi

# Check disk space before proceeding
echo "Checking disk space..."
df -h / | tail -1 | awk '{print "Available space: " $4 " (Used: " $5 ")"}'
echo ""

# Clean pip cache to free up space
echo "Cleaning pip cache to free up space..."
pip cache purge 2>/dev/null || python3 -m pip cache purge 2>/dev/null || echo "Note: pip cache clean skipped (pip may not be installed yet)"
if [ -d ~/.cache/pip ]; then
    rm -rf ~/.cache/pip/* 2>/dev/null || true
fi
echo ""

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install requirements with no cache to save space
echo "Installing requirements..."
echo "Note: Using --no-cache-dir to save disk space during installation"
pip install --no-cache-dir -r requirements.txt

echo ""
echo "✅ Virtual environment created and dependencies installed!"
echo ""
echo "To activate the virtual environment in the future, run:"
echo "  source venv/bin/activate"
echo ""
echo "To deactivate, run:"
echo "  deactivate"

