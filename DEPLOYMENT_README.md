# Asia Salman Flask Application - Docker Deployment Guide

## 🚀 Production Deployment on Linux Server

This guide provides comprehensive instructions for deploying the Asia Salman Flask application on a Linux server using Docker and Docker Compose.

## 📋 Prerequisites

### System Requirements
- **OS**: Ubuntu 20.04+ / CentOS 8+ / Debian 11+
- **RAM**: Minimum 2GB, Recommended 4GB+
- **Storage**: Minimum 10GB free space
- **CPU**: 2+ cores recommended

### Software Requirements
- Docker 20.10+
- Docker Compose 2.0+
- Git
- curl

## 🔧 Installation Steps

### 1. Install Docker and Docker Compose

#### Ubuntu/Debian:
```bash
# Update package index
sudo apt update

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add user to docker group
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Logout and login again to apply group changes
```

#### CentOS/RHEL:
```bash
# Install Docker
sudo yum install -y yum-utils
sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
sudo yum install -y docker-ce docker-ce-cli containerd.io

# Start Docker service
sudo systemctl start docker
sudo systemctl enable docker

# Add user to docker group
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### 2. Clone and Setup Application

```bash
# Clone the repository
git clone <your-repository-url>
cd asiasalman

# Make deployment script executable
chmod +x scripts/deploy.sh
chmod +x scripts/backup.sh

# Copy environment configuration
cp env.example .env

# Edit environment variables
nano .env
```

### 3. Configure Environment Variables

Edit the `.env` file with your production settings:

```bash
# Essential settings
SECRET_KEY=your-super-secret-key-here
FLASK_ENV=production
DOMAIN_NAME=your-domain.com

# Database settings
SQLALCHEMY_DATABASE_URI=sqlite:///asia_salman.db

# Redis settings
REDIS_URL=redis://redis:6379/0

# Email settings (optional)
MAIL_SERVER=smtp.gmail.com
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password

# Tadbir API settings
TADBIR_API_URL=https://your-tadbir-api.com
TADBIR_USERNAME=your-username
TADBIR_PASSWORD=your-password
```

### 4. Deploy Application

```bash
# Run deployment script
./scripts/deploy.sh deploy
```

The deployment script will:
- Check prerequisites
- Create necessary directories
- Build Docker images
- Start all services
- Run database migrations
- Perform health checks

## 🐳 Docker Services

The application consists of the following services:

### Web Application (`web`)
- **Port**: 8000 (internal)
- **Image**: Built from Dockerfile
- **Health Check**: `/health` endpoint
- **Resources**: 1GB RAM limit, 1 CPU limit

### Redis Cache (`redis`)
- **Port**: 6379
- **Image**: redis:7-alpine
- **Purpose**: Session storage and caching
- **Resources**: 256MB RAM limit

### Nginx Reverse Proxy (`nginx`)
- **Ports**: 80 (HTTP), 443 (HTTPS)
- **Image**: nginx:alpine
- **Purpose**: Static file serving and load balancing
- **Features**: Rate limiting, security headers, SSL termination

## 📊 Monitoring and Health Checks

### Health Check Endpoints
- **Main Health Check**: `http://your-domain.com/health`
- **Readiness Check**: `http://your-domain.com/health/ready`
- **Liveness Check**: `http://your-domain.com/health/live`

### Service Status
```bash
# Check service status
./scripts/deploy.sh status

# View logs
./scripts/deploy.sh logs

# Check health
curl http://localhost/health
```

## 🔒 Security Features

### Built-in Security Measures
- **Non-root containers**: All services run as non-root users
- **Security headers**: X-Frame-Options, X-Content-Type-Options, etc.
- **Rate limiting**: API endpoints protected against abuse
- **File upload restrictions**: Secure file handling
- **SSL/TLS ready**: HTTPS configuration available

### Firewall Configuration
```bash
# Allow HTTP and HTTPS
sudo ufw allow 80
sudo ufw allow 443

# Allow SSH (if needed)
sudo ufw allow 22

# Enable firewall
sudo ufw enable
```

## 🔄 Backup and Maintenance

### Automated Backups
```bash
# Run backup manually
docker-compose run --rm backup

# Schedule daily backups (add to crontab)
0 2 * * * cd /path/to/asiasalman && docker-compose run --rm backup
```

### Log Management
```bash
# View application logs
docker-compose logs -f web

# View nginx logs
docker-compose logs -f nginx

# Log rotation is configured automatically
```

### Database Maintenance
```bash
# Access database
docker-compose exec web python -c "
from app import app
from models import db
with app.app_context():
    # Your database operations here
    pass
"
```

## 🚀 Deployment Commands

### Basic Operations
```bash
# Deploy application
./scripts/deploy.sh deploy

# Stop services
./scripts/deploy.sh stop

# Start services
./scripts/deploy.sh start

# Restart services
./scripts/deploy.sh restart

# Rollback to previous version
./scripts/deploy.sh rollback
```

### Advanced Operations
```bash
# View service status
./scripts/deploy.sh status

# View logs
./scripts/deploy.sh logs

# Run with maintenance profile
docker-compose --profile maintenance up -d

# Run with backup profile
docker-compose --profile backup up -d
```

## 🔧 Troubleshooting

### Common Issues

#### 1. Port Already in Use
```bash
# Check what's using the port
sudo netstat -tulpn | grep :80

# Kill the process or change port in docker-compose.yaml
```

#### 2. Permission Issues
```bash
# Fix file permissions
sudo chown -R $USER:$USER .
chmod -R 755 .
```

#### 3. Database Connection Issues
```bash
# Check database file permissions
ls -la instance/

# Recreate database
docker-compose exec web python -c "
from app import app
from models import db
with app.app_context():
    db.create_all()
"
```

#### 4. Memory Issues
```bash
# Check memory usage
docker stats

# Increase memory limits in docker-compose.yaml
```

### Log Analysis
```bash
# Application errors
docker-compose logs web | grep ERROR

# Nginx errors
docker-compose logs nginx | grep error

# System resource usage
docker stats --no-stream
```

## 📈 Performance Optimization

### Production Optimizations
- **Multi-stage Docker build**: Reduced image size
- **Gunicorn with gevent**: High-performance WSGI server
- **Nginx caching**: Static file optimization
- **Redis caching**: Session and data caching
- **Connection pooling**: Database optimization

### Scaling
```bash
# Scale web service
docker-compose up -d --scale web=3

# Use load balancer for multiple instances
```

## 🔐 SSL/HTTPS Configuration

### Using Let's Encrypt (Recommended)
```bash
# Install certbot
sudo apt install certbot

# Get SSL certificate
sudo certbot certonly --standalone -d your-domain.com

# Copy certificates to ssl_certs directory
sudo cp /etc/letsencrypt/live/your-domain.com/fullchain.pem ssl_certs/cert.pem
sudo cp /etc/letsencrypt/live/your-domain.com/privkey.pem ssl_certs/key.pem

# Update nginx configuration for HTTPS
# Uncomment HTTPS server block in nginx/conf.d/default.conf
```

## 📞 Support

### Health Check Response Example
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "services": {
    "database": "healthy",
    "redis": "healthy"
  },
  "system": {
    "timestamp": "2024-01-01T12:00:00Z",
    "cpu_percent": 15.2,
    "memory_percent": 45.8,
    "disk_percent": 23.1
  }
}
```

### Monitoring Integration
- **Prometheus**: Metrics available at `/metrics`
- **Grafana**: Dashboard configuration available
- **AlertManager**: Health check integration

## 🎯 Production Checklist

- [ ] Environment variables configured
- [ ] SSL certificates installed
- [ ] Firewall configured
- [ ] Backup strategy implemented
- [ ] Monitoring setup
- [ ] Log rotation configured
- [ ] Health checks working
- [ ] Performance testing completed
- [ ] Security scan performed
- [ ] Documentation updated

---

**Note**: This deployment setup is optimized for production use with security, performance, and reliability in mind. Always test in a staging environment before deploying to production.
