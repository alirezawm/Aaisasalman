# Database Lock Issue - Fixed ✓

## Problem Summary

Your Flask application was experiencing `sqlalchemy.exc.OperationalError: database is locked` errors. This occurred because:

1. **SQLite Default Limitations**: SQLite uses file-based locking and has limited concurrent access support by default
2. **Background Scheduler**: The Tadbir scheduler runs in a background thread, creating concurrent database access
3. **Poor Session Management**: Database sessions weren't being properly closed in background threads
4. **No Timeout Configuration**: SQLite was using default short timeout values

## Solutions Implemented

### 1. SQLite Engine Configuration (`app.py`)

Added proper SQLite configuration for better concurrency:

```python
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'connect_args': {
        'timeout': 30,  # 30 seconds timeout for database locks
        'check_same_thread': False  # Allow SQLite to be accessed from multiple threads
    },
    'pool_pre_ping': True,  # Verify connections before using them
    'pool_recycle': 3600,  # Recycle connections after 1 hour
}
```

**Benefits:**
- Increased timeout from 5 seconds (default) to 30 seconds
- Allows multi-threaded access
- Automatically verifies connection health
- Prevents stale connections

### 2. WAL (Write-Ahead Logging) Mode

Enabled WAL mode for significantly better concurrent access:

```python
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_conn, connection_record):
    if 'sqlite' in str(dbapi_conn):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA busy_timeout=30000")  # 30 seconds
        cursor.execute("PRAGMA synchronous=NORMAL")
        cursor.close()
```

**Benefits:**
- Allows concurrent reads while writing
- Better performance for multi-threaded applications
- Reduces lock contention significantly
- Industry standard for SQLite in production

### 3. Proper Session Management

Added session cleanup in the scheduler service:

```python
# In background jobs
try:
    # ... database operations ...
finally:
    db.session.remove()  # Always clean up
```

**Benefits:**
- Prevents sessions from holding locks indefinitely
- Ensures proper connection pool management
- Reduces memory leaks

### 4. Application Context for Background Threads

Wrapped scheduler jobs in Flask application context:

```python
with app.app_context():
    try:
        # ... sync operations ...
    finally:
        db.session.remove()
```

**Benefits:**
- Proper Flask context for database operations
- Ensures session scoping works correctly
- Prevents context-related errors

## How to Apply the Fix

### Step 1: Stop Your Application

Press `Ctrl+C` in the terminal running your Flask app.

### Step 2: Clear Database Locks

Run the helper script:

```bash
python restart_app.py
```

This script will:
- Check for existing locks
- Enable WAL mode on your database
- Verify the database is ready

### Step 3: Restart the Application

```bash
python app.py
```

The application will now:
- Automatically enable WAL mode on startup
- Configure proper timeouts
- Manage sessions correctly

## Verifying the Fix

After restarting, you should see:

```
SQLite WAL mode and optimizations enabled
Tadbir scheduler started successfully
 * Running on http://0.0.0.0:5000
```

## Understanding WAL Mode

### What is WAL?

Write-Ahead Logging (WAL) is a different approach to journaling in SQLite:

- **Normal Mode**: Writes are exclusive (locks entire database)
- **WAL Mode**: Writes go to a separate log file, allowing concurrent reads

### WAL Files

You'll see new files created:
- `asia_salman.db` - Main database
- `asia_salman.db-wal` - Write-ahead log
- `asia_salman.db-shm` - Shared memory file

These are normal and expected!

### Performance Improvements

| Operation | Normal Mode | WAL Mode |
|-----------|-------------|----------|
| Concurrent Reads | Blocked during write | Allowed |
| Write Speed | Moderate | Faster |
| Lock Contention | High | Low |

## Preventing Future Issues

### Best Practices

1. **Always Use Application Context in Background Threads**
   ```python
   with app.app_context():
       # ... database operations ...
   ```

2. **Clean Up Sessions**
   ```python
   try:
       # ... operations ...
   finally:
       db.session.remove()
   ```

3. **Use Proper Timeouts**
   - Already configured in `app.py`
   - 30 seconds should handle most scenarios

4. **Monitor Database Size**
   - WAL files grow with activity
   - Checkpoints happen automatically
   - Manual checkpoint: `PRAGMA wal_checkpoint(TRUNCATE)`

### Things to Avoid

❌ **Don't:**
- Open database in external tools while app is running
- Use long-running transactions
- Forget to close database connections
- Run multiple instances of the app pointing to same database

✓ **Do:**
- Use the single application instance approach
- Let Flask handle session management
- Trust the automatic checkpointing
- Monitor application logs for errors

## Troubleshooting

### If You Still Get "Database is Locked"

1. **Check for Multiple Processes**
   ```bash
   # Windows
   tasklist | findstr python
   
   # Linux/Mac
   ps aux | grep python
   ```

2. **Close Database Viewers**
   - DB Browser for SQLite
   - SQLite extensions in VS Code
   - Any other database tools

3. **Run the Restart Helper**
   ```bash
   python restart_app.py
   ```

4. **Check File Permissions**
   - Ensure the `instance/` directory is writable
   - Verify user has permissions for database files

5. **Increase Timeout (if needed)**
   Edit `app.py`:
   ```python
   'timeout': 60,  # Increase to 60 seconds
   ```

### If WAL Mode Causes Issues

WAL mode is incompatible with:
- Network file systems (NFS, SMB) - use local filesystem
- Read-only databases
- Very old SQLite versions (< 3.7.0)

To disable WAL mode (not recommended):
```python
cursor.execute("PRAGMA journal_mode=DELETE")
```

## Performance Monitoring

### Check WAL Size

```python
import os
wal_path = 'instance/asia_salman.db-wal'
if os.path.exists(wal_path):
    size_mb = os.path.getsize(wal_path) / (1024 * 1024)
    print(f"WAL size: {size_mb:.2f} MB")
```

### Manual Checkpoint (if needed)

```python
import sqlite3
conn = sqlite3.connect('instance/asia_salman.db')
conn.execute('PRAGMA wal_checkpoint(TRUNCATE)')
conn.close()
```

## Migration to PostgreSQL (Future)

If your application grows significantly, consider PostgreSQL:

### When to Migrate

- More than 100 concurrent users
- Heavy write operations
- Complex queries taking > 1 second
- Need for advanced features (full-text search, JSON queries)

### Benefits of PostgreSQL

- True concurrent write support
- Better performance at scale
- Advanced features
- Industry standard for production

### Current SQLite is Fine For

- Development and testing
- Small to medium deployments
- Read-heavy applications
- Single-server deployments

## Summary

✅ **Fixed:**
- Database lock errors
- Concurrent access issues
- Session management problems
- Timeout configurations

✅ **Improved:**
- Application reliability
- Performance under load
- Error handling
- Background job management

✅ **Added:**
- WAL mode for better concurrency
- Proper session cleanup
- Restart helper script
- Comprehensive documentation

## Need Help?

If you continue to experience issues:

1. Check application logs for specific errors
2. Run `python restart_app.py` to diagnose
3. Review the troubleshooting section above
4. Consider the PostgreSQL migration for high-load scenarios

---

**Last Updated:** October 11, 2025
**Version:** 1.0

