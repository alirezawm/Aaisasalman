FROM python:3.11-slim

# Environment
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV FLASK_ENV=production
ENV PORT=8000

# Install system dependencies needed by lxml/Pillow/gevent/etc.
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        gcc \
        libxml2-dev \
        libxslt1-dev \
        libjpeg62-turbo-dev \
        zlib1g-dev \
        libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Create app user
RUN adduser --disabled-password --gecos "" appuser

WORKDIR /usr/src/app

# Install Python deps first (better layer caching)
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Ensure required writable dirs exist and are owned by non-root user
RUN mkdir -p uploads/products uploads/logos uploads/documents uploads/receipts instance \
    && chown -R appuser:appuser /usr/src/app

USER appuser

EXPOSE 8000

# Use gunicorn to serve the Flask app object named `app` in app.py
CMD ["gunicorn", "-k", "gevent", "-w", "3", "-b", "0.0.0.0:8000", "app:app", "--timeout", "120", "--graceful-timeout", "30"]