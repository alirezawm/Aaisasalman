#!/bin/bash

# ========================================
# اسکریپت خودکار راه‌اندازی پروژه آسیا سلمان
# برای سرور لینوکس با IP: 192.168.1.4
# ========================================

set -e  # خروج در صورت خطا

# رنگ‌ها برای نمایش بهتر
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# توابع کمکی
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# بررسی دسترسی root
if [ "$EUID" -ne 0 ]; then
    print_error "لطفاً با دسترسی root اجرا کنید: sudo $0"
    exit 1
fi

print_status "شروع راه‌اندازی پروژه آسیا سلمان..."

# مرحله 1: پاک‌سازی کامل سرور
print_status "مرحله 1: پاک‌سازی کامل سرور..."

# توقف تمام سرویس‌های وب
print_status "توقف سرویس‌های وب..."
systemctl stop apache2 2>/dev/null || true
systemctl stop httpd 2>/dev/null || true
systemctl stop nginx 2>/dev/null || true
systemctl stop mysql 2>/dev/null || true
systemctl stop postgresql 2>/dev/null || true
systemctl stop php*-fpm 2>/dev/null || true

# توقف Docker
print_status "توقف Docker containers..."
docker stop $(docker ps -aq) 2>/dev/null || true
docker rm $(docker ps -aq) 2>/dev/null || true

# کشتن پروسه‌های Python/Node
print_status "توقف پروسه‌های اپلیکیشن..."
pkill -f python 2>/dev/null || true
pkill -f gunicorn 2>/dev/null || true
pkill -f node 2>/dev/null || true

# پاک کردن سرویس‌های غیرضروری
print_status "حذف سرویس‌های غیرضروری..."
apt-get remove --purge apache2 apache2-utils apache2-bin apache2-data -y 2>/dev/null || true
apt-get remove --purge nginx nginx-common nginx-core -y 2>/dev/null || true
apt-get remove --purge php* -y 2>/dev/null || true
apt-get remove --purge nodejs npm -y 2>/dev/null || true

# پاک کردن فایل‌های اضافی
print_status "پاک کردن فایل‌های اضافی..."
rm -rf /var/www/* 2>/dev/null || true
rm -rf /usr/share/nginx/* 2>/dev/null || true
rm -rf /home/*/public_html 2>/dev/null || true
rm -rf /var/log/apache2/* 2>/dev/null || true
rm -rf /var/log/nginx/* 2>/dev/null || true
rm -rf /var/log/php* 2>/dev/null || true
rm -rf /tmp/*
rm -rf /var/tmp/*

print_success "پاک‌سازی کامل انجام شد"

# مرحله 2: تنظیم فایروال
print_status "مرحله 2: تنظیم فایروال..."

# نصب UFW
apt-get update
apt-get install ufw -y

# تنظیم فایروال
ufw --force reset
ufw default deny incoming
ufw default allow outgoing
ufw allow 2222/tcp  # SSH
ufw allow 8081/tcp  # Application
ufw --force enable

print_success "فایروال تنظیم شد"

# مرحله 3: نصب Docker
print_status "مرحله 3: نصب Docker..."

# حذف نسخه‌های قدیمی
apt-get remove docker docker-engine docker.io containerd runc -y 2>/dev/null || true

# نصب پیش‌نیازها
apt-get install -y \
    ca-certificates \
    curl \
    gnupg \
    lsb-release

# اضافه کردن کلید GPG Docker
mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg

# اضافه کردن repository
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null

# نصب Docker
apt-get update
apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# راه‌اندازی Docker
systemctl start docker
systemctl enable docker
usermod -aG docker root

# نصب Docker Compose
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose
ln -s /usr/local/bin/docker-compose /usr/bin/docker-compose

print_success "Docker نصب شد"

# مرحله 4: آماده‌سازی پروژه
print_status "مرحله 4: آماده‌سازی پروژه..."

# ایجاد مسیر پروژه
mkdir -p /root/application
cd /root/application

# حذف محتویات قبلی
rm -rf * .*

# کلون کردن پروژه
print_status "دانلود پروژه از Git..."
git clone https://git.agarvand.ir/Alirezawm/asiasalman.git .

# تنظیم دسترسی‌ها
chown -R root:root /root/application
chmod -R 755 /root/application

print_success "پروژه آماده شد"

# مرحله 5: ایجاد فایل‌های تنظیمات
print_status "مرحله 5: ایجاد فایل‌های تنظیمات..."

# ایجاد فایل .env
cat > .env << 'EOF'
# تنظیمات اصلی
SECRET_KEY=asia-salman-super-secret-key-2024-production
FLASK_ENV=production
FLASK_APP=app.py
DOMAIN_NAME=192.168.1.4

# تنظیمات دیتابیس
SQLALCHEMY_DATABASE_URI=sqlite:///asia_salman.db
SQLALCHEMY_TRACK_MODIFICATIONS=False

# تنظیمات آپلود
UPLOAD_FOLDER=uploads
MAX_CONTENT_LENGTH=16777216

# تنظیمات Redis
REDIS_URL=redis://redis:6379/0

# تنظیمات ایمیل (اختیاری)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password

# تنظیمات API تدبیر
TADBIR_API_URL=https://your-tadbir-api.com
TADBIR_USERNAME=your-username
TADBIR_PASSWORD=your-password

# تنظیمات ISACO
ENABLE_ISACO_WH15=True
ISACO_BRAND_ID=63
ISACO_WAREHOUSE_ID=15
ISACO_ALLOWED_PLANS=isaco_cash,isaco_1m,isaco_2m,isaco_3m

# تنظیمات پورت
PORT=8081
HOST=0.0.0.0
EOF

# ایجاد docker-compose.yaml
cat > docker-compose.yaml << 'EOF'
version: '3.8'

services:
  web:
    build: .
    container_name: asiasalman_web
    restart: unless-stopped
    ports:
      - "8081:8000"
    environment:
      - FLASK_ENV=production
      - FLASK_APP=app.py
    volumes:
      - ./instance:/usr/src/app/instance
      - ./uploads:/usr/src/app/uploads
      - ./logs:/usr/src/app/logs
      - ./backups:/usr/src/app/backups
    depends_on:
      - redis
    networks:
      - asiasalman_network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  redis:
    image: redis:7-alpine
    container_name: asiasalman_redis
    restart: unless-stopped
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data
    networks:
      - asiasalman_network
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 30s
      timeout: 10s
      retries: 3

  nginx:
    image: nginx:alpine
    container_name: asiasalman_nginx
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/conf.d:/etc/nginx/conf.d:ro
      - ./ssl_certs:/etc/nginx/ssl:ro
    depends_on:
      - web
    networks:
      - asiasalman_network

volumes:
  redis_data:

networks:
  asiasalman_network:
    driver: bridge
EOF

# ایجاد پیکربندی Nginx
mkdir -p nginx/conf.d ssl_certs

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

cat > nginx/conf.d/default.conf << 'EOF'
upstream asiasalman_backend {
    server web:8000;
    keepalive 32;
}

server {
    listen 80;
    server_name 192.168.1.4;
    
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;

    limit_req zone=api burst=20 nodelay;
    limit_req zone=login burst=5 nodelay;

    location /static/ {
        alias /usr/src/app/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    location /uploads/ {
        alias /usr/src/app/uploads/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

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

    location /health {
        proxy_pass http://asiasalman_backend/health;
        access_log off;
    }
}
EOF

print_success "فایل‌های تنظیمات ایجاد شدند"

# مرحله 6: بهینه‌سازی سیستم
print_status "مرحله 6: بهینه‌سازی سیستم..."

# تنظیمات kernel
cat >> /etc/sysctl.conf << 'EOF'
# Network optimizations
net.core.rmem_max = 16777216
net.core.wmem_max = 16777216
net.ipv4.tcp_rmem = 4096 65536 16777216
net.ipv4.tcp_wmem = 4096 65536 16777216
net.core.netdev_max_backlog = 5000
net.ipv4.tcp_congestion_control = bbr

# File system optimizations
fs.file-max = 2097152
vm.swappiness = 10
vm.dirty_ratio = 15
vm.dirty_background_ratio = 5
EOF

sysctl -p

# تنظیمات Docker
cat > /etc/docker/daemon.json << 'EOF'
{
    "log-driver": "json-file",
    "log-opts": {
        "max-size": "10m",
        "max-file": "3"
    },
    "storage-driver": "overlay2",
    "live-restore": true,
    "userland-proxy": false,
    "experimental": false,
    "metrics-addr": "0.0.0.0:9323",
    "default-ulimits": {
        "memlock": {
            "Hard": -1,
            "Name": "memlock",
            "Soft": -1
        }
    }
}
EOF

systemctl restart docker

print_success "سیستم بهینه‌سازی شد"

# مرحله 7: راه‌اندازی اپلیکیشن
print_status "مرحله 7: راه‌اندازی اپلیکیشن..."

# ساخت Docker images
print_status "ساخت Docker images..."
# استفاده از فایل‌های اصلاح شده
cp Dockerfile.fixed Dockerfile
cp requirements.fixed.txt requirements.txt
docker-compose build --no-cache

# راه‌اندازی سرویس‌ها
print_status "راه‌اندازی سرویس‌ها..."
docker-compose up -d

# انتظار برای راه‌اندازی
print_status "انتظار برای راه‌اندازی سرویس‌ها..."
sleep 30

print_success "اپلیکیشن راه‌اندازی شد"

# مرحله 8: ایجاد اسکریپت‌های مدیریتی
print_status "مرحله 8: ایجاد اسکریپت‌های مدیریتی..."

# اسکریپت مدیریت
cat > /root/manage.sh << 'EOF'
#!/bin/bash

APP_DIR="/root/application"
COMPOSE_FILE="$APP_DIR/docker-compose.yaml"

case "$1" in
    start)
        echo "Starting Asia Salman application..."
        cd $APP_DIR
        docker-compose up -d
        echo "Application started successfully!"
        ;;
    stop)
        echo "Stopping Asia Salman application..."
        cd $APP_DIR
        docker-compose down
        echo "Application stopped successfully!"
        ;;
    restart)
        echo "Restarting Asia Salman application..."
        cd $APP_DIR
        docker-compose restart
        echo "Application restarted successfully!"
        ;;
    status)
        echo "Checking application status..."
        cd $APP_DIR
        docker-compose ps
        echo ""
        echo "Health check:"
        curl -f http://192.168.1.4:8081/health 2>/dev/null && echo "✅ Application is healthy" || echo "❌ Application is not responding"
        ;;
    logs)
        echo "Showing application logs..."
        cd $APP_DIR
        docker-compose logs -f
        ;;
    update)
        echo "Updating application..."
        cd $APP_DIR
        git pull
        docker-compose build --no-cache
        docker-compose up -d
        echo "Application updated successfully!"
        ;;
    backup)
        echo "Creating backup..."
        cd $APP_DIR
        ./maintenance.sh
        echo "Backup completed!"
        ;;
    clean)
        echo "Cleaning up..."
        cd $APP_DIR
        docker system prune -f
        docker volume prune -f
        echo "Cleanup completed!"
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status|logs|update|backup|clean}"
        echo ""
        echo "Commands:"
        echo "  start    - Start the application"
        echo "  stop     - Stop the application"
        echo "  restart  - Restart the application"
        echo "  status   - Check application status"
        echo "  logs     - Show application logs"
        echo "  update   - Update application from Git"
        echo "  backup   - Create database backup"
        echo "  clean    - Clean up Docker resources"
        exit 1
        ;;
esac
EOF

chmod +x /root/manage.sh

# اسکریپت نگهداری
cat > /root/maintenance.sh << 'EOF'
#!/bin/bash

# پاک کردن لاگ‌های قدیمی
find /root/application/logs -name "*.log" -mtime +7 -delete 2>/dev/null || true

# پاک کردن Docker images غیرضروری
docker system prune -f

# پشتیبان‌گیری از دیتابیس
cd /root/application
if [ -f "instance/asia_salman.db" ]; then
    timestamp=$(date +%Y%m%d_%H%M%S)
    backup_path="backups/asia_salman_${timestamp}.db"
    mkdir -p backups
    cp instance/asia_salman.db "$backup_path"
    echo "Database backed up to $backup_path"
fi

# حذف پشتیبان‌های قدیمی (بیش از 30 روز)
find /root/application/backups -name "*.db" -mtime +30 -delete 2>/dev/null || true

echo "Maintenance completed at $(date)"
EOF

chmod +x /root/maintenance.sh

# اسکریپت مانیتورینگ
cat > /root/monitor.sh << 'EOF'
#!/bin/bash

echo "=== Asia Salman Server Status ==="
echo "Date: $(date)"
echo ""

echo "=== System Resources ==="
echo "CPU Usage:"
top -bn1 | grep "Cpu(s)" | awk '{print $2}' | awk -F'%' '{print $1}'
echo ""

echo "Memory Usage:"
free -h
echo ""

echo "Disk Usage:"
df -h
echo ""

echo "=== Docker Status ==="
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
echo ""

echo "=== Application Health ==="
curl -s http://192.168.1.4:8081/health | python3 -m json.tool 2>/dev/null || echo "Application not responding"
echo ""

echo "=== Network Connections ==="
netstat -tulpn | grep -E ":(80|443|8081|2222)"
echo ""

echo "=== Firewall Status ==="
ufw status
EOF

chmod +x /root/monitor.sh

# تنظیم cron jobs
echo "0 2 * * * /root/maintenance.sh >> /var/log/maintenance.log 2>&1" | crontab -

print_success "اسکریپت‌های مدیریتی ایجاد شدند"

# مرحله 9: تست نهایی
print_status "مرحله 9: تست نهایی..."

# بررسی وضعیت
print_status "بررسی وضعیت اپلیکیشن..."
sleep 10

# تست سلامت
if curl -f http://192.168.1.4:8081/health >/dev/null 2>&1; then
    print_success "✅ اپلیکیشن با موفقیت راه‌اندازی شد!"
else
    print_warning "⚠️ اپلیکیشن هنوز آماده نیست. لطفاً چند دقیقه صبر کنید."
fi

# نمایش وضعیت
echo ""
echo "=== وضعیت نهایی ==="
/root/manage.sh status

echo ""
echo "=== اطلاعات دسترسی ==="
echo "🌐 آدرس اپلیکیشن: http://192.168.1.4:8081"
echo "🔧 اسکریپت مدیریت: /root/manage.sh"
echo "📊 مانیتورینگ: /root/monitor.sh"
echo "🔄 نگهداری: /root/maintenance.sh"

echo ""
echo "=== دستورات مفید ==="
echo "بررسی وضعیت: /root/manage.sh status"
echo "مشاهده لاگ‌ها: /root/manage.sh logs"
echo "راه‌اندازی مجدد: /root/manage.sh restart"
echo "به‌روزرسانی: /root/manage.sh update"

print_success "🎉 راه‌اندازی کامل شد!"
print_status "برای دسترسی به اپلیکیشن، آدرس http://192.168.1.4:8081 را در مرورگر باز کنید."
