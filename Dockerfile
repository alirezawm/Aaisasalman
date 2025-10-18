# ========================================
# Multi-stage Dockerfile for Asia Salman Flask App
# Optimized for production deployment on Linux servers
# ========================================

# Stage 1: Build stage
FROM python:3.11-slim as builder

# Set build arguments
ARG BUILDPLATFORM
ARG TARGETPLATFORM

# Environment variables for build
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies for building Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    g++ \
    libxml2-dev \
    libxslt1-dev \
    libjpeg62-turbo-dev \
    libpng-dev \
    zlib1g-dev \
    libffi-dev \
    libssl-dev \
    libpq-dev \
    libsqlite3-dev \
    sqlite3 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip setuptools wheel && \
    pip install -r requirements.txt

# Stage 2: Production stage
FROM python:3.11-slim as production

# Set production environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_ENV=production \
    FLASK_APP=app.py \
    PORT=8000 \
    PATH="/opt/venv/bin:$PATH"

# Install runtime dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    libxml2 \
    libxslt1.1 \
    libjpeg62-turbo \
    libpng16-16 \
    zlib1g \
    libffi-dev \
    libssl-dev \
    libpq-dev \
    libsqlite3-0 \
    sqlite3 \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy virtual environment from builder stage
COPY --from=builder /opt/venv /opt/venv

# Create non-root user for security
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Create application directory
WORKDIR /usr/src/app

# Copy only essential application files first
COPY --chown=appuser:appuser app.py ./
COPY --chown=appuser:appuser models.py ./
COPY --chown=appuser:appuser routes.py ./
COPY --chown=appuser:appuser database_utils.py ./
COPY --chown=appuser:appuser search_engine.py ./
COPY --chown=appuser:appuser points_service.py ./
COPY --chown=appuser:appuser shop_sync_service.py ./
COPY --chown=appuser:appuser tadbir_api_service.py ./
COPY --chown=appuser:appuser tadbir_sync_service.py ./
COPY --chown=appuser:appuser tadbir_scheduler_service.py ./
COPY --chown=appuser:appuser detection_service.py ./
COPY --chown=appuser:appuser detection_api.py ./
COPY --chown=appuser:appuser detection_models.py ./
COPY --chown=appuser:appuser brand_vehicle_detector.py ./
COPY --chown=appuser:appuser invoice_notification_service.py ./
COPY --chown=appuser:appuser persian_date_utils.py ./

# Copy Python service files
COPY --chown=appuser:appuser *.py ./

# Copy templates and static directories
COPY --chown=appuser:appuser templates/ ./templates/
COPY --chown=appuser:appuser static/ ./static/

# Create necessary directories with proper permissions
RUN mkdir -p \
    uploads/products \
    uploads/logos \
    uploads/documents \
    uploads/receipts \
    instance \
    logs \
    backups \
    && chown -R appuser:appuser /usr/src/app

# Set proper permissions
RUN chmod -R 755 /usr/src/app && \
    chmod -R 777 /usr/src/app/uploads && \
    chmod -R 777 /usr/src/app/instance && \
    chmod -R 777 /usr/src/app/logs

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Use gunicorn with optimized settings for production
CMD ["gunicorn", \
     "--bind", "0.0.0.0:8000", \
     "--workers", "4", \
     "--worker-class", "gevent", \
     "--worker-connections", "1000", \
     "--max-requests", "1000", \
     "--max-requests-jitter", "100", \
     "--timeout", "120", \
     "--graceful-timeout", "30", \
     "--keep-alive", "5", \
     "--preload", \
     "--access-logfile", "-", \
     "--error-logfile", "-", \
     "--log-level", "info", \
     "app:app"]