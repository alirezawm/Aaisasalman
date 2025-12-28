# Quick Fix Commands for Disk Space Issue

Run these commands on your Linux server:

## Step 1: Make scripts executable
```bash
chmod +x cleanup_disk_space.sh setup_venv.sh install_without_triton.sh
```

## Step 2: Clean up disk space
```bash
./cleanup_disk_space.sh
```

## Step 3: Check what's using space (if needed)
```bash
# Check space in current directory
du -sh ~/Aaisasalman/* | sort -rh | head -10

# Check if there's a venv already taking space
du -sh ~/Aaisasalman/venv 2>/dev/null || echo "No venv found"
```

## Step 4: Clean pip cache manually (if script doesn't work)
```bash
# Clean pip cache
python3 -m pip cache purge 2>/dev/null || pip cache purge 2>/dev/null

# Remove pip cache directory
rm -rf ~/.cache/pip/* 2>/dev/null
rm -rf /root/.cache/pip/* 2>/dev/null

# Clean temporary files
find /tmp -type f -atime +7 -delete 2>/dev/null
```

## Step 5: Install with no cache (recommended)
```bash
# If venv doesn't exist, create it
python3 -m venv venv

# Activate venv
source venv/bin/activate

# Install with no cache to save space
pip install --no-cache-dir --upgrade pip
pip install --no-cache-dir -r requirements.txt
```

## Alternative: If triton keeps failing, skip it
```bash
source venv/bin/activate
pip install --no-cache-dir -r requirements.txt --ignore-installed triton 2>&1 | grep -v triton || pip install --no-cache-dir -r requirements.txt
```

## Check if triton is actually needed
```bash
# Check if any package in requirements.txt needs triton
grep -i "torch\|triton" requirements.txt
# If nothing found, triton is likely optional
```

