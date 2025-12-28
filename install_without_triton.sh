#!/bin/bash

# Alternative installation script that skips triton if it causes issues
# Triton is typically only needed for PyTorch GPU acceleration

echo "Installing requirements (skipping optional triton dependency)..."

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Clean pip cache first
echo "Cleaning pip cache..."
pip cache purge 2>/dev/null || python3 -m pip cache purge 2>/dev/null || true
if [ -d ~/.cache/pip ]; then
    rm -rf ~/.cache/pip/* 2>/dev/null || true
fi

# Install requirements without cache
echo "Installing packages (this may take a while)..."
pip install --no-cache-dir -r requirements.txt

# If triton installation fails, you can exclude it explicitly
# Uncomment the following if you need to skip triton:
# pip install --no-cache-dir -r requirements.txt --no-deps triton || echo "Skipping triton (optional dependency)"

echo ""
echo "✅ Installation complete!"
echo ""
echo "Note: If triton is required by your application, you may need to:"
echo "  1. Free up more disk space"
echo "  2. Install triton separately after other packages"
echo "  3. Use a CPU-only version of packages that depend on triton"

