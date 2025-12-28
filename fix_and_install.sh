#!/bin/bash

# Comprehensive fix and install script for disk space issues

set -e  # Exit on error

echo "🔧 Fixing disk space issues and installing dependencies..."
echo ""

# Make scripts executable
echo "📝 Making scripts executable..."
chmod +x cleanup_disk_space.sh setup_venv.sh install_without_triton.sh 2>/dev/null || true
echo "✅ Scripts are executable"
echo ""

# Check disk space
echo "📊 Checking disk space..."
df -h / | tail -1
echo ""

# Check /tmp space (pip uses this for downloads)
echo "📊 Checking /tmp space..."
df -h /tmp | tail -1
TMP_USAGE=$(df /tmp | tail -1 | awk '{print $5}' | sed 's/%//')
if [ "$TMP_USAGE" -gt 80 ]; then
    echo "⚠️  /tmp is ${TMP_USAGE}% full. Cleaning..."
    sudo find /tmp -type f -atime +1 -delete 2>/dev/null || true
    sudo rm -rf /tmp/pip-* /tmp/tmp* 2>/dev/null || true
    echo "✅ /tmp cleaned"
fi
echo ""

# Set alternative temp directory if needed
export TMPDIR="${HOME}/tmp"
mkdir -p "$TMPDIR"
echo "📁 Using temp directory: $TMPDIR"
echo ""

# Clean pip cache
echo "🗑️  Cleaning pip cache..."
python3 -m pip cache purge 2>/dev/null || pip cache purge 2>/dev/null || true
rm -rf ~/.cache/pip/* /root/.cache/pip/* 2>/dev/null || true
echo "✅ Pip cache cleaned"
echo ""

# Clean Python cache in current directory
echo "🗑️  Cleaning Python cache files..."
find . -type d -name "__pycache__" -exec rm -r {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true
echo "✅ Python cache cleaned"
echo ""

# Check if venv exists and remove if corrupted
if [ -d "venv" ]; then
    echo "📦 Existing venv found. Checking size..."
    VENV_SIZE=$(du -sh venv 2>/dev/null | cut -f1)
    echo "   Current venv size: $VENV_SIZE"
    read -p "   Remove existing venv and create new one? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "🗑️  Removing existing venv..."
        rm -rf venv
        echo "✅ Venv removed"
    fi
fi
echo ""

# Create or use existing venv
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "📦 Using existing virtual environment"
fi
echo ""

# Activate venv
echo "🔌 Activating virtual environment..."
source venv/bin/activate
echo "✅ Virtual environment activated"
echo ""

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --no-cache-dir --upgrade pip
echo "✅ Pip upgraded"
echo ""

# Install requirements
echo "📥 Installing requirements (this may take a while)..."
echo "   Using --no-cache-dir to save disk space"
echo ""

# Try to install, catch triton errors specifically
if pip install --no-cache-dir -r requirements.txt 2>&1 | tee install.log; then
    echo ""
    echo "✅ All packages installed successfully!"
else
    INSTALL_ERROR=$?
    echo ""
    echo "⚠️  Installation encountered an error (exit code: $INSTALL_ERROR)"
    
    # Check if error is related to triton
    if grep -qi "triton\|No space" install.log; then
        echo ""
        echo "🔍 Error appears to be related to triton or disk space"
        echo "💡 Attempting to install without triton dependency..."
        echo ""
        
        # Try installing without triton
        pip install --no-cache-dir -r requirements.txt --ignore-installed triton 2>&1 | tee install_retry.log || {
            echo ""
            echo "⚠️  Installation still failed. Checking what was installed..."
            pip list
            echo ""
            echo "💡 You may need to:"
            echo "   1. Free up more disk space"
            echo "   2. Install packages individually"
            echo "   3. Skip optional dependencies like triton"
        }
    else
        echo "❌ Installation failed. Check install.log for details."
        exit $INSTALL_ERROR
    fi
fi

echo ""
echo "📊 Final disk usage:"
df -h / | tail -1
echo ""
echo "✅ Setup complete!"
echo ""
echo "To activate the virtual environment in the future:"
echo "  source venv/bin/activate"

