"""
Database utility functions for handling SQLite lock issues and connection management
"""
import time
import logging
from functools import wraps
from sqlalchemy.exc import OperationalError
from sqlalchemy import text
from contextlib import contextmanager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def retry_on_database_lock(max_retries=3, delay=1, backoff=2):
    """
    Decorator to retry database operations on lock errors
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            current_delay = delay
            
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except OperationalError as e:
                    if "database is locked" in str(e).lower():
                        last_exception = e
                        if attempt < max_retries - 1:
                            logger.warning(f"Database locked on attempt {attempt + 1}/{max_retries}. Retrying in {current_delay}s...")
                            time.sleep(current_delay)
                            current_delay *= backoff
                        else:
                            logger.error(f"Database lock retry failed after {max_retries} attempts")
                    else:
                        # Re-raise non-lock errors immediately
                        raise e
                except Exception as e:
                    # Re-raise non-OperationalError exceptions immediately
                    raise e
            
            # If we get here, all retries failed
            raise last_exception
        return wrapper
    return decorator

@contextmanager
def database_transaction(db_session, commit=True):
    """
    Context manager for database transactions with proper error handling
    """
    try:
        yield db_session
        if commit:
            db_session.commit()
    except Exception as e:
        db_session.rollback()
        logger.error(f"Database transaction failed: {e}")
        raise e
    finally:
        # Always close the session to release locks
        db_session.close()

def checkpoint_wal_database(db_engine):
    """
    Checkpoint the WAL file to reduce lock contention
    """
    try:
        with db_engine.connect() as conn:
            # Checkpoint the WAL file
            conn.execute(text("PRAGMA wal_checkpoint(TRUNCATE)"))
            logger.info("WAL checkpoint completed successfully")
    except Exception as e:
        logger.warning(f"WAL checkpoint failed: {e}")

def optimize_sqlite_connection(db_engine):
    """
    Apply SQLite optimizations for better concurrency
    """
    try:
        with db_engine.connect() as conn:
            # Set pragmas for better concurrency
            conn.execute(text("PRAGMA journal_mode=WAL"))
            conn.execute(text("PRAGMA busy_timeout=30000"))  # 30 seconds
            conn.execute(text("PRAGMA synchronous=NORMAL"))
            conn.execute(text("PRAGMA cache_size=10000"))  # 10MB cache
            conn.execute(text("PRAGMA temp_store=MEMORY"))
            conn.execute(text("PRAGMA mmap_size=268435456"))  # 256MB memory mapping
            conn.commit()
            logger.info("SQLite optimizations applied successfully")
    except Exception as e:
        logger.warning(f"SQLite optimization failed: {e}")

def safe_db_operation(operation_func, *args, **kwargs):
    """
    Safely execute a database operation with retry logic
    """
    @retry_on_database_lock(max_retries=3, delay=0.5, backoff=2)
    def _execute():
        return operation_func(*args, **kwargs)
    
    return _execute()

def get_database_status(db_engine):
    """
    Get database status information for debugging
    """
    try:
        with db_engine.connect() as conn:
            # Get WAL file info
            wal_info = conn.execute(text("PRAGMA wal_checkpoint")).fetchone()
            
            # Get database info
            db_info = conn.execute(text("PRAGMA database_list")).fetchall()
            
            return {
                'wal_checkpoint': wal_info,
                'database_list': db_info,
                'connection_pool_size': db_engine.pool.size(),
                'checked_in_connections': db_engine.pool.checkedin(),
                'checked_out_connections': db_engine.pool.checkedout(),
                'overflow_connections': db_engine.pool.overflow()
            }
    except Exception as e:
        logger.error(f"Failed to get database status: {e}")
        return None
