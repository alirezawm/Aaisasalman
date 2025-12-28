#!/bin/bash

# اسکریپت ایجاد پیکربندی nginx برای پروژه آسیا سلمان

set -e

echo "Creating nginx configuration..."

# ایجاد پوشه‌های لازم
mkdir -p nginx/conf.d ssl_certs

# ایجاد nginx.conf اصلی
cat > nginx/nginx.conf << 'EOF'
user nginx;
worker_processes auto;
error_log /var/log/nginx/error.log warn;
pid /var/run/nginx.pid;

events {
    worker_connections 1024;
    use epoll;
    multi_accept on;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for"';

    access_log /var/log/nginx/access.log main;

    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;
    client_max_body_size 20M;

    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types
        text/plain
        text/css
        text/xml
        text/javascript
        application/json
        application/javascript
        application/xml+rss
        application/atom+xml
        image/svg+xml;

    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=login:10m rate=5r/m;

    include /etc/nginx/conf.d/*.conf;
}
EOF

# ایجاد default.conf
cat > nginx/conf.d/default.conf << 'EOF'
upstream asiasalman_backend {
    server web:8000;
    keepalive 32;
}

server {
    listen 80;
    server_name _;  # تغییر دهید به domain name خود
    
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;

    limit_req zone=api burst=20 nodelay;
    limit_req zone=login burst=5 nodelay;

    # Static files - مهم: مسیر باید با volume mount در docker-compose مطابقت داشته باشد
    location /static/ {
        alias /usr/src/app/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
        access_log off;
    }

    # Uploaded files
    location /uploads/ {
        alias /usr/src/app/uploads/;
        expires 1y;
        add_header Cache-Control "public, immutable";
        access_log off;
    }

    # Health check
    location /health {
        proxy_pass http://asiasalman_backend/health;
        access_log off;
    }

    # All other requests to Flask
    location / {
        proxy_pass http://asiasalman_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
        
        proxy_buffering on;
        proxy_buffer_size 4k;
        proxy_buffers 8 4k;
    }
}
EOF

echo "✅ Nginx configuration created successfully!"
echo ""
echo "📝 Next steps:"
echo "1. Edit nginx/conf.d/default.conf and change 'server_name _;' to your domain"
echo "2. If using HTTPS, add SSL certificates to ssl_certs/ folder"
echo "3. Run: docker-compose up -d nginx"
echo ""
echo "⚠️  Important: Make sure static and uploads folders are mounted in docker-compose.yaml"

