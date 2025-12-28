# Disk Space Troubleshooting Guide

## Problem
You're encountering `OSError: [Errno 28] No space left on device` when installing packages, particularly when downloading large packages like `triton` (170.5 MB).

## Quick Solutions

### 1. Clean Up Disk Space (Recommended First Step)

Run the cleanup script:
```bash
./cleanup_disk_space.sh
```

Or manually clean pip cache:
```bash
pip cache purge
# Or
python3 -m pip cache purge

# Also clean user cache
rm -rf ~/.cache/pip/*
```

### 2. Check Disk Space

```bash
# Check overall disk usage
df -h /

# Check space in current directory
du -sh .

# Find largest files/directories
du -h --max-depth=1 . | sort -rh | head -10
```

### 3. Install with No Cache

The updated `setup_venv.sh` now uses `--no-cache-dir` flag automatically. If you need to install manually:

```bash
source venv/bin/activate
pip install --no-cache-dir -r requirements.txt
```

### 4. Skip Optional Dependencies

If `triton` is not essential (it's typically only needed for PyTorch GPU acceleration), you can:

1. Use the alternative installer:
   ```bash
   ./install_without_triton.sh
   ```

2. Or install packages one by one, skipping problematic ones:
   ```bash
   pip install --no-cache-dir -r requirements.txt --ignore-installed triton
   ```

### 5. Free Up More Space

If cleanup isn't enough, consider:

- **Remove old virtual environments:**
  ```bash
  find . -type d -name "venv*" -exec du -sh {} \; | sort -rh
  # Remove unused ones
  ```

- **Clean Docker (if using Docker):**
  ```bash
  docker system prune -a --volumes
  ```

- **Remove old log files:**
  ```bash
  sudo journalctl --vacuum-time=3d
  find /var/log -type f -name "*.log" -mtime +7 -delete
  ```

- **Remove old Python cache:**
  ```bash
  find . -type d -name "__pycache__" -exec rm -r {} +
  find . -type f -name "*.pyc" -delete
  ```

## About Triton

`triton` is a GPU programming language compiler, typically used by PyTorch for GPU acceleration. If your application doesn't use PyTorch or doesn't need GPU acceleration, you can skip it.

To check if triton is actually needed:
```bash
grep -i "torch\|triton" requirements.txt
```

If neither appears in your requirements.txt, triton is likely a transitive dependency that can be skipped.

## Prevention

1. **Always use `--no-cache-dir`** for installations on systems with limited disk space
2. **Regular cleanup:** Run `cleanup_disk_space.sh` periodically
3. **Monitor disk usage:** Set up alerts when disk usage exceeds 80%

## Next Steps

1. Run `./cleanup_disk_space.sh` to free up space
2. Check available space with `df -h /`
3. If space is still low, remove unnecessary files
4. Retry installation with the updated `setup_venv.sh` script

