# Stage 1: Builder
FROM python:3.11-slim as builder

ARG BUILDPLATFORM
ARG TARGETPLATFORM

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential gcc g++ \
    libxml2-dev libxslt1-dev libjpeg62-turbo-dev libpng-dev zlib1g-dev \
    libffi-dev libssl-dev libpq-dev libsqlite3-dev sqlite3 curl ca-certificates \
    && rm -rf /var/lib/apt/lists/*

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .
RUN pip install --upgrade pip setuptools wheel && pip install -r requirements.txt


# Stage 2: Production
FROM python:3.11-slim as production

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_ENV=production \
    FLASK_APP=app.py \
    PORT=8000 \
    PATH="/opt/venv/bin:$PATH"

RUN apt-get update && apt-get install -y --no-install-recommends \
    libxml2 libxslt1.1 libjpeg62-turbo libpng16-16 zlib1g \
    libffi-dev libssl-dev libpq-dev libsqlite3-0 sqlite3 \
    curl ca-certificates wget gnupg dirmngr \
    && rm -rf /var/lib/apt/lists/* && apt-get clean

COPY --from=builder /opt/venv /opt/venv

RUN groupadd -r appuser && useradd -r -g appuser -m -d /home/appuser appuser

WORKDIR /usr/src/app

COPY --chown=appuser:appuser . .

# ?? ÓÇÎÊ ÇÓ˜ÑíÊ startup.sh (Èå ÕæÑÊ ˜Çãá ÈÓÊåÔÏå)
RUN set -eux; \
cat > /usr/src/app/startup.sh <<'EOF'
#!/bin/sh
echo "Starting Asia Salman application (as $(id -u -n))..."
mkdir -p /usr/src/app/uploads/products \
         /usr/src/app/uploads/logos \
         /usr/src/app/uploads/documents \
         /usr/src/app/uploads/receipts \
         /usr/src/app/instance \
         /usr/src/app/logs \
         /usr/src/app/backups

chmod -R 755 /usr/src/app/uploads || true
chmod -R 755 /usr/src/app/instance || true
chmod -R 755 /usr/src/app/logs || true
chmod -R 755 /usr/src/app/backups || true

echo "Directory setup completed."
echo "Starting Gunicorn..."
exec gunicorn \
    --bind 0.0.0.0:8000 \
    --workers 4 \
    --worker-class gevent \
    --worker-connections 1000 \
    --max-requests 1000 \
    --max-requests-jitter 100 \
    --timeout 120 \
    --graceful-timeout 30 \
    --keep-alive 5 \
    --preload \
    --access-logfile - \
    --error-logfile - \
    --log-level info \
    app:app
EOF

RUN chmod +x /usr/src/app/startup.sh && chown appuser:appuser /usr/src/app/startup.sh

# ?? äÕÈ gosu ÈÑÇí ÇÌÑÇí Çãä ˜ÇÑÈÑ appuser
ENV GOSU_VERSION=1.16
RUN set -eux; \
    dpkgArch="$(dpkg --print-architecture)"; \
    wget -O /usr/local/bin/gosu "https://github.com/tianon/gosu/releases/download/$GOSU_VERSION/gosu-${dpkgArch}"; \
    chmod +x /usr/local/bin/gosu; \
    gosu --version

# ?? ÓÇÎÊ entrypoint.sh (Èå ÕæÑÊ ÕÍíÍ ÈÓÊåÔÏå)
RUN set -eux; \
cat > /usr/local/bin/entrypoint.sh <<'EOF'
#!/bin/sh
set -e
echo "Entrypoint: fixing permissions and creating folders..."
for d in /usr/src/app/uploads /usr/src/app/instance /usr/src/app/logs /usr/src/app/backups; do
  mkdir -p "$d"
  chown -R appuser:appuser "$d" || true
done
chown appuser:appuser /usr/src/app/startup.sh || true
echo "Entrypoint: switching to appuser..."
exec gosu appuser /usr/src/app/startup.sh
EOF

RUN chmod +x /usr/local/bin/entrypoint.sh

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
CMD ["/usr/src/app/startup.sh"]