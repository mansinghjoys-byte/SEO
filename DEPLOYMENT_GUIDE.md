# 🚀 Complete Deployment Guide - RankForge on VM with Redis & RQ Workers

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Server Setup](#server-setup)
3. [Install Dependencies](#install-dependencies)
4. [Application Setup](#application-setup)
5. [Redis & RQ Workers Configuration](#redis--rq-workers-configuration)
6. [Supervisor Configuration](#supervisor-configuration)
7. [Nginx Setup](#nginx-setup)
8. [SSL Configuration](#ssl-configuration)
9. [Environment Variables](#environment-variables)
10. [Starting Services](#starting-services)
11. [Testing](#testing)
12. [Monitoring & Maintenance](#monitoring--maintenance)
13. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Server Requirements
- **OS**: Ubuntu 20.04 LTS or 22.04 LTS
- **RAM**: Minimum 4GB (8GB recommended for production)
- **CPU**: 2+ cores
- **Storage**: 20GB+ SSD
- **Network**: Public IP address
- **Domain**: Configured domain pointing to server IP

### What You'll Install
- Python 3.11+
- Node.js 18+ & Yarn
- MongoDB 6.0+
- Redis 7.0+
- Nginx
- Supervisor
- Certbot (for SSL)

---

## Step 1: Server Setup

### 1.1 Connect to Your VM
```bash
ssh root@your-server-ip
# or
ssh ubuntu@your-server-ip
```

### 1.2 Update System
```bash
sudo apt-get update
sudo apt-get upgrade -y
```

### 1.3 Create Application User
```bash
# Create user for running the app
sudo adduser rankforge --disabled-password --gecos ""

# Add to sudo group
sudo usermod -aG sudo rankforge

# Switch to app user
sudo su - rankforge
```

### 1.4 Set Up Firewall
```bash
# Allow SSH
sudo ufw allow 22/tcp

# Allow HTTP and HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Enable firewall
sudo ufw enable
```

---

## Step 2: Install Dependencies

### 2.1 Install Python 3.11
```bash
sudo apt-get install -y software-properties-common
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt-get update
sudo apt-get install -y python3.11 python3.11-venv python3.11-dev python3-pip
```

### 2.2 Install Node.js & Yarn
```bash
# Install Node.js 18.x
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Install Yarn
curl -sS https://dl.yarnpkg.com/debian/pubkey.gpg | sudo apt-key add -
echo "deb https://dl.yarnpkg.com/debian/ stable main" | sudo tee /etc/apt/sources.list.d/yarn.list
sudo apt-get update
sudo apt-get install -y yarn

# Verify installations
node --version  # Should be v18.x
yarn --version
```

### 2.3 Install MongoDB
```bash
# Import MongoDB public key
curl -fsSL https://www.mongodb.org/static/pgp/server-6.0.asc | sudo gpg --dearmor -o /usr/share/keyrings/mongodb-server-6.0.gpg

# Add MongoDB repository
echo "deb [ arch=amd64,arm64 signed-by=/usr/share/keyrings/mongodb-server-6.0.gpg ] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/6.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-6.0.list

# Install MongoDB
sudo apt-get update
sudo apt-get install -y mongodb-org

# Start MongoDB
sudo systemctl start mongod
sudo systemctl enable mongod

# Verify
sudo systemctl status mongod
```

### 2.4 Install Redis
```bash
# Install Redis
sudo apt-get install -y redis-server

# Configure Redis for production
sudo nano /etc/redis/redis.conf

# Make these changes:
# supervised systemd
# maxmemory 256mb
# maxmemory-policy allkeys-lru

# Start Redis
sudo systemctl start redis-server
sudo systemctl enable redis-server

# Verify
redis-cli ping  # Should return PONG
```

### 2.5 Install Nginx
```bash
sudo apt-get install -y nginx
sudo systemctl start nginx
sudo systemctl enable nginx
```

### 2.6 Install Supervisor
```bash
sudo apt-get install -y supervisor
sudo systemctl start supervisor
sudo systemctl enable supervisor
```

### 2.7 Install Additional Tools
```bash
sudo apt-get install -y git curl wget build-essential
```

---

## Step 3: Application Setup

### 3.1 Clone Repository
```bash
# Switch to app user
sudo su - rankforge

# Create app directory
mkdir -p /home/rankforge/app
cd /home/rankforge/app

# Clone your repository (or upload files)
# git clone https://github.com/your-repo/rankforge.git .

# Or if uploading files:
# Use scp or rsync to copy files to /home/rankforge/app/
```

### 3.2 Backend Setup
```bash
cd /home/rankforge/app/backend

# Create virtual environment
python3.11 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Verify installation
python -c "import fastapi; print('FastAPI:', fastapi.__version__)"
python -c "import redis; print('Redis:', redis.__version__)"
python -c "import rq; print('RQ:', rq.__version__)"
```

### 3.3 Frontend Setup
```bash
cd /home/rankforge/app/frontend

# Install dependencies
yarn install

# Build production bundle
yarn build

# This creates /home/rankforge/app/frontend/build
```

---

## Step 4: Redis & RQ Workers Configuration

### 4.1 Create RQ Worker Script
```bash
cd /home/rankforge/app/backend

# Create worker script
cat > start_worker.sh << 'EOF'
#!/bin/bash
# RQ Worker Start Script

# Activate virtual environment
source /home/rankforge/app/backend/venv/bin/activate

# Set environment variables
export PYTHONPATH=/home/rankforge/app/backend
export MONGO_URL=mongodb://localhost:27017
export DB_NAME=seo_platform
export REDIS_URL=redis://localhost:6379/0

# Start RQ worker
rq worker high default low --url redis://localhost:6379/0 --name worker-$(hostname)-$$
EOF

chmod +x start_worker.sh
```

### 4.2 Create Background Task Module
```bash
# Create tasks module for background jobs
cat > /home/rankforge/app/backend/tasks.py << 'EOF'
"""
Background Tasks using RQ (Redis Queue)
"""
from redis import Redis
from rq import Queue
from services.llm_visibility_service import LLMVisibilityService
from services.advanced_crawler import AdvancedSEOCrawler
from core.config import get_settings
import asyncio

settings = get_settings()

# Initialize Redis connection
redis_conn = Redis.from_url(settings.REDIS_URL)

# Create queues with different priorities
high_priority_queue = Queue('high', connection=redis_conn)
default_queue = Queue('default', connection=redis_conn)
low_priority_queue = Queue('low', connection=redis_conn)

# High Priority Tasks
def run_llm_visibility_check(site_id, user_id, competitors=None):
    """Background task for LLM visibility check"""
    try:
        service = LLMVisibilityService()
        result = asyncio.run(service.check_visibility(
            domain=f"site-{site_id}",
            competitors=competitors or []
        ))
        return {'success': True, 'result': result}
    except Exception as e:
        return {'success': False, 'error': str(e)}

# Default Priority Tasks
def run_deep_analysis(site_id, user_id):
    """Background task for deep SEO analysis"""
    try:
        crawler = AdvancedSEOCrawler()
        # Get site URL from database
        # Run analysis
        return {'success': True}
    except Exception as e:
        return {'success': False, 'error': str(e)}

# Low Priority Tasks
def cleanup_old_data(days=30):
    """Background task for data cleanup"""
    try:
        # Cleanup logic
        return {'success': True}
    except Exception as e:
        return {'success': False, 'error': str(e)}

# Helper functions to enqueue tasks
def enqueue_visibility_check(site_id, user_id, competitors=None):
    """Enqueue LLM visibility check (high priority)"""
    job = high_priority_queue.enqueue(
        run_llm_visibility_check,
        site_id,
        user_id,
        competitors,
        job_timeout='10m'
    )
    return job.id

def enqueue_deep_analysis(site_id, user_id):
    """Enqueue deep analysis (default priority)"""
    job = default_queue.enqueue(
        run_deep_analysis,
        site_id,
        user_id,
        job_timeout='15m'
    )
    return job.id

def enqueue_cleanup(days=30):
    """Enqueue cleanup (low priority)"""
    job = low_priority_queue.enqueue(
        cleanup_old_data,
        days,
        job_timeout='30m'
    )
    return job.id
EOF
```

### 4.3 Test RQ Worker
```bash
# In one terminal, start worker
cd /home/rankforge/app/backend
source venv/bin/activate
./start_worker.sh

# In another terminal, test enqueuing
python3 << 'EOF'
from redis import Redis
from rq import Queue

redis_conn = Redis(host='localhost', port=6379)
queue = Queue(connection=redis_conn)

# Test job
job = queue.enqueue('tasks.cleanup_old_data', days=30)
print(f"Job enqueued: {job.id}")
EOF

# Stop worker with Ctrl+C
```

---

## Step 5: Supervisor Configuration

### 5.1 Backend Supervisor Config
```bash
sudo nano /etc/supervisor/conf.d/rankforge-backend.conf
```

Add:
```ini
[program:rankforge-backend]
directory=/home/rankforge/app/backend
command=/home/rankforge/app/backend/venv/bin/uvicorn server:app --host 0.0.0.0 --port 8001 --workers 2
user=rankforge
autostart=true
autorestart=true
stopasgroup=true
killasgroup=true
stderr_logfile=/var/log/rankforge/backend.err.log
stdout_logfile=/var/log/rankforge/backend.out.log
environment=PYTHONPATH="/home/rankforge/app/backend",MONGO_URL="mongodb://localhost:27017",DB_NAME="seo_platform",REDIS_URL="redis://localhost:6379/0"
```

### 5.2 RQ Worker Supervisor Config (Multiple Workers)
```bash
sudo nano /etc/supervisor/conf.d/rankforge-workers.conf
```

Add:
```ini
[program:rankforge-worker]
directory=/home/rankforge/app/backend
command=/home/rankforge/app/backend/venv/bin/rq worker high default low --url redis://localhost:6379/0 --name worker-%(process_num)s
process_name=%(program_name)s-%(process_num)s
numprocs=4
user=rankforge
autostart=true
autorestart=true
stopasgroup=true
killasgroup=true
stderr_logfile=/var/log/rankforge/worker-%(process_num)s.err.log
stdout_logfile=/var/log/rankforge/worker-%(process_num)s.out.log
environment=PYTHONPATH="/home/rankforge/app/backend",MONGO_URL="mongodb://localhost:27017",DB_NAME="seo_platform",REDIS_URL="redis://localhost:6379/0"
```

This creates 4 RQ workers (worker-0, worker-1, worker-2, worker-3)

### 5.3 RQ Dashboard (Optional - for monitoring)
```bash
sudo nano /etc/supervisor/conf.d/rankforge-rq-dashboard.conf
```

Add:
```ini
[program:rankforge-rq-dashboard]
directory=/home/rankforge/app/backend
command=/home/rankforge/app/backend/venv/bin/rq-dashboard --redis-url redis://localhost:6379/0 --port 9181
user=rankforge
autostart=true
autorestart=true
stderr_logfile=/var/log/rankforge/rq-dashboard.err.log
stdout_logfile=/var/log/rankforge/rq-dashboard.out.log
```

Install rq-dashboard:
```bash
source /home/rankforge/app/backend/venv/bin/activate
pip install rq-dashboard
```

### 5.4 Create Log Directory
```bash
sudo mkdir -p /var/log/rankforge
sudo chown -R rankforge:rankforge /var/log/rankforge
```

### 5.5 Reload Supervisor
```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl status

# You should see:
# rankforge-backend         RUNNING
# rankforge-worker-0        RUNNING
# rankforge-worker-1        RUNNING
# rankforge-worker-2        RUNNING
# rankforge-worker-3        RUNNING
# rankforge-rq-dashboard    RUNNING (optional)
```

---

## Step 6: Nginx Setup

### 6.1 Create Nginx Configuration
```bash
sudo nano /etc/nginx/sites-available/rankforge
```

Add:
```nginx
# Backend API
server {
    listen 80;
    server_name api.yourdomain.com;

    client_max_body_size 50M;

    location / {
        proxy_pass http://127.0.0.1:8001;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        
        # Timeouts for long-running requests
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
}

# Frontend
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    root /home/rankforge/app/frontend/build;
    index index.html;

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 10240;
    gzip_proxied expired no-cache no-store private auth;
    gzip_types text/plain text/css text/xml text/javascript application/x-javascript application/xml+rss application/json;

    location / {
        try_files $uri $uri/ /index.html;
    }

    # Cache static assets
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}

# RQ Dashboard (Optional)
server {
    listen 80;
    server_name rq.yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:9181;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 6.2 Enable Site
```bash
# Create symlink
sudo ln -s /etc/nginx/sites-available/rankforge /etc/nginx/sites-enabled/

# Remove default site
sudo rm /etc/nginx/sites-enabled/default

# Test configuration
sudo nginx -t

# Reload Nginx
sudo systemctl reload nginx
```

---

## Step 7: SSL Configuration

### 7.1 Install Certbot
```bash
sudo apt-get install -y certbot python3-certbot-nginx
```

### 7.2 Obtain SSL Certificates
```bash
# For API subdomain
sudo certbot --nginx -d api.yourdomain.com

# For main domain
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# For RQ dashboard (optional)
sudo certbot --nginx -d rq.yourdomain.com

# Follow prompts and agree to terms
```

### 7.3 Auto-renewal Test
```bash
# Test renewal
sudo certbot renew --dry-run

# Certbot auto-renewal is set up via systemd timer
sudo systemctl status certbot.timer
```

---

## Step 8: Environment Variables

### 8.1 Create Backend .env File
```bash
nano /home/rankforge/app/backend/.env
```

Add:
```bash
# Database
MONGO_URL=mongodb://localhost:27017
DB_NAME=seo_platform

# Redis
REDIS_URL=redis://localhost:6379/0

# API Keys
GROQ_API_KEY=your_groq_api_key_here

# Security
SECRET_KEY=your-super-secret-jwt-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Admin Credentials
ADMIN_EMAIL=admin@rankforge.com
ADMIN_PASSWORD=RankForge@Admin2025!Secure

# Environment
ENVIRONMENT=production
```

### 8.2 Create Frontend .env File
```bash
nano /home/rankforge/app/frontend/.env
```

Add:
```bash
REACT_APP_BACKEND_URL=https://api.yourdomain.com/api
REACT_APP_ENVIRONMENT=production
```

### 8.3 Rebuild Frontend with Production URLs
```bash
cd /home/rankforge/app/frontend
yarn build
```

### 8.4 Update Supervisor Environment Variables
```bash
# If you need to change env vars, update supervisor configs
sudo nano /etc/supervisor/conf.d/rankforge-backend.conf
sudo nano /etc/supervisor/conf.d/rankforge-workers.conf

# Then restart
sudo supervisorctl restart all
```

---

## Step 9: Starting Services

### 9.1 Start All Services
```bash
# Start/Restart MongoDB
sudo systemctl restart mongod

# Start/Restart Redis
sudo systemctl restart redis-server

# Restart Supervisor programs
sudo supervisorctl restart all

# Check status
sudo supervisorctl status

# Expected output:
# rankforge-backend         RUNNING   pid 1234, uptime 0:00:05
# rankforge-worker-0        RUNNING   pid 1235, uptime 0:00:05
# rankforge-worker-1        RUNNING   pid 1236, uptime 0:00:05
# rankforge-worker-2        RUNNING   pid 1237, uptime 0:00:05
# rankforge-worker-3        RUNNING   pid 1238, uptime 0:00:05
```

### 9.2 Verify Services
```bash
# Check backend
curl http://localhost:8001/api/health
# Should return: {"status":"healthy"}

# Check Redis
redis-cli ping
# Should return: PONG

# Check MongoDB
mongosh --eval "db.adminCommand('ping')"
# Should return: { ok: 1 }

# Check RQ workers
redis-cli LLEN rq:queue:default
# Should return: 0 (no pending jobs)

# Check Nginx
sudo systemctl status nginx

# Test public URLs
curl https://api.yourdomain.com/api/health
curl https://yourdomain.com
```

---

## Step 10: Testing

### 10.1 Test Backend API
```bash
# Test health endpoint
curl https://api.yourdomain.com/api/health

# Test user registration
curl -X POST https://api.yourdomain.com/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPassword123",
    "full_name": "Test User"
  }'

# Test login
curl -X POST https://api.yourdomain.com/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPassword123"
  }'
```

### 10.2 Test RQ Workers
```bash
# Create test task
python3 << 'EOF'
from redis import Redis
from rq import Queue

redis_conn = Redis(host='localhost', port=6379)
queue = Queue('default', connection=redis_conn)

# Enqueue test job
def test_job():
    import time
    time.sleep(5)
    return "Job completed successfully!"

job = queue.enqueue(test_job)
print(f"Job ID: {job.id}")
print(f"Job Status: {job.get_status()}")
EOF

# Check job was processed
# Wait 5 seconds, then check logs
sudo tail -f /var/log/rankforge/worker-0.out.log
```

### 10.3 Test Frontend
```bash
# Visit in browser
# https://yourdomain.com

# Should see React app loading
# Test login, registration, site creation
```

---

## Step 11: Monitoring & Maintenance

### 11.1 Log Monitoring
```bash
# Backend logs
sudo tail -f /var/log/rankforge/backend.out.log
sudo tail -f /var/log/rankforge/backend.err.log

# Worker logs
sudo tail -f /var/log/rankforge/worker-0.out.log
sudo tail -f /var/log/rankforge/worker-1.out.log

# Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# All RankForge logs
sudo tail -f /var/log/rankforge/*.log
```

### 11.2 RQ Dashboard Access
```bash
# Visit: https://rq.yourdomain.com
# Monitor:
# - Active workers
# - Queued jobs
# - Failed jobs
# - Job statistics
```

### 11.3 System Monitoring
```bash
# Check disk space
df -h

# Check memory
free -h

# Check Redis memory
redis-cli INFO memory

# Check MongoDB status
mongosh --eval "db.serverStatus()"

# Check process status
sudo supervisorctl status
```

### 11.4 Database Backup
```bash
# Create backup script
cat > /home/rankforge/backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR=/home/rankforge/backups
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup MongoDB
mongodump --out=$BACKUP_DIR/mongo_$DATE --db=seo_platform

# Compress
tar -czf $BACKUP_DIR/backup_$DATE.tar.gz $BACKUP_DIR/mongo_$DATE

# Remove old backups (keep last 7 days)
find $BACKUP_DIR -name "backup_*.tar.gz" -mtime +7 -delete
find $BACKUP_DIR -name "mongo_*" -type d -mtime +7 -exec rm -rf {} +

echo "Backup completed: $BACKUP_DIR/backup_$DATE.tar.gz"
EOF

chmod +x /home/rankforge/backup.sh

# Set up daily backup cron job
crontab -e
# Add: 0 2 * * * /home/rankforge/backup.sh >> /var/log/rankforge/backup.log 2>&1
```

### 11.5 Update Deployment Script
```bash
cat > /home/rankforge/update.sh << 'EOF'
#!/bin/bash
# Update deployment script

set -e

echo "🔄 Starting update..."

# Pull latest code
cd /home/rankforge/app
# git pull origin main

# Update backend
cd /home/rankforge/app/backend
source venv/bin/activate
pip install -r requirements.txt

# Update frontend
cd /home/rankforge/app/frontend
yarn install
yarn build

# Restart services
sudo supervisorctl restart all

echo "✅ Update completed!"
EOF

chmod +x /home/rankforge/update.sh
```

---

## Step 12: Troubleshooting

### 12.1 Backend Not Starting
```bash
# Check logs
sudo tail -100 /var/log/rankforge/backend.err.log

# Common issues:
# 1. Port already in use
sudo lsof -i :8001

# 2. Environment variables not set
# Check supervisor config

# 3. Dependencies missing
cd /home/rankforge/app/backend
source venv/bin/activate
pip install -r requirements.txt

# Restart
sudo supervisorctl restart rankforge-backend
```

### 12.2 Workers Not Processing Jobs
```bash
# Check worker logs
sudo tail -100 /var/log/rankforge/worker-0.err.log

# Check Redis connection
redis-cli ping

# Check queue status
redis-cli LLEN rq:queue:high
redis-cli LLEN rq:queue:default
redis-cli LLEN rq:queue:low

# Check failed jobs
redis-cli LLEN rq:queue:failed

# Restart workers
sudo supervisorctl restart rankforge-worker:*
```

### 12.3 Frontend Not Loading
```bash
# Check Nginx configuration
sudo nginx -t

# Check Nginx logs
sudo tail -100 /var/log/nginx/error.log

# Verify build exists
ls -la /home/rankforge/app/frontend/build

# Rebuild frontend
cd /home/rankforge/app/frontend
yarn build

# Reload Nginx
sudo systemctl reload nginx
```

### 12.4 Redis Memory Issues
```bash
# Check Redis memory
redis-cli INFO memory

# Flush if needed (WARNING: clears all data)
redis-cli FLUSHALL

# Increase maxmemory
sudo nano /etc/redis/redis.conf
# Set: maxmemory 512mb

sudo systemctl restart redis-server
```

### 12.5 MongoDB Connection Issues
```bash
# Check MongoDB status
sudo systemctl status mongod

# Check logs
sudo tail -100 /var/log/mongodb/mongod.log

# Restart MongoDB
sudo systemctl restart mongod
```

---

## Step 13: Performance Optimization

### 13.1 Redis Configuration
```bash
sudo nano /etc/redis/redis.conf

# Recommended settings for production:
maxmemory 1gb
maxmemory-policy allkeys-lru
save 900 1
save 300 10
save 60 10000
tcp-backlog 511
timeout 0
tcp-keepalive 300
```

### 13.2 MongoDB Indexing
```bash
mongosh seo_platform << 'EOF'
// Create indexes for performance
db.sites.createIndex({ "user_id": 1, "site_id": 1 })
db.audits.createIndex({ "site_id": 1, "created_at": -1 })
db.llm_visibility_checks.createIndex({ "site_id": 1, "created_at": -1 })
db.agents.createIndex({ "user_id": 1, "agent_id": 1 })
db.chat_sessions.createIndex({ "agent_id": 1, "timestamp": -1 })
db.users.createIndex({ "email": 1 }, { unique: true })

// Verify indexes
db.sites.getIndexes()
EOF
```

### 13.3 Nginx Caching
```bash
sudo nano /etc/nginx/nginx.conf

# Add inside http block:
http {
    # Cache settings
    proxy_cache_path /var/cache/nginx levels=1:2 keys_zone=api_cache:10m max_size=1g inactive=60m;
    proxy_cache_key "$scheme$request_method$host$request_uri";
}
```

---

## Step 14: Security Hardening

### 14.1 Fail2ban Setup
```bash
# Install fail2ban
sudo apt-get install -y fail2ban

# Configure for Nginx
sudo nano /etc/fail2ban/jail.local

# Add:
[nginx-http-auth]
enabled = true
port = http,https
logpath = /var/log/nginx/error.log

[nginx-botsearch]
enabled = true
port = http,https
logpath = /var/log/nginx/access.log

sudo systemctl restart fail2ban
```

### 14.2 Secure MongoDB
```bash
# Enable authentication
sudo nano /etc/mongod.conf

# Add:
security:
  authorization: enabled

# Create admin user
mongosh << 'EOF'
use admin
db.createUser({
  user: "admin",
  pwd: "StrongPasswordHere",
  roles: [ { role: "userAdminAnyDatabase", db: "admin" } ]
})

use seo_platform
db.createUser({
  user: "rankforge",
  pwd: "AnotherStrongPassword",
  roles: [ { role: "readWrite", db: "seo_platform" } ]
})
EOF

# Update connection string
# MONGO_URL=mongodb://rankforge:AnotherStrongPassword@localhost:27017/seo_platform
```

---

## Quick Reference Commands

### Start/Stop Services
```bash
# Supervisor
sudo supervisorctl start all
sudo supervisorctl stop all
sudo supervisorctl restart all
sudo supervisorctl status

# Individual services
sudo supervisorctl restart rankforge-backend
sudo supervisorctl restart rankforge-worker:*

# System services
sudo systemctl restart nginx
sudo systemctl restart mongod
sudo systemctl restart redis-server
```

### View Logs
```bash
# Real-time logs
sudo tail -f /var/log/rankforge/backend.out.log
sudo tail -f /var/log/rankforge/worker-0.out.log

# Last 100 lines
sudo tail -100 /var/log/rankforge/backend.err.log

# Search logs
sudo grep "ERROR" /var/log/rankforge/*.log
```

### Check Service Health
```bash
# API health
curl https://api.yourdomain.com/api/health

# Redis
redis-cli ping

# MongoDB
mongosh --eval "db.adminCommand('ping')"

# Worker queues
redis-cli LLEN rq:queue:default
```

---

## Deployment Checklist

Before going live:

- [ ] All services running (backend, workers, nginx, redis, mongodb)
- [ ] SSL certificates installed and auto-renewal working
- [ ] Environment variables configured correctly
- [ ] Database indexes created
- [ ] Firewall rules configured
- [ ] Log rotation set up
- [ ] Backup script scheduled
- [ ] Monitoring configured
- [ ] Domain DNS pointing to server
- [ ] Admin credentials changed from defaults
- [ ] API keys set in .env
- [ ] Test all critical endpoints
- [ ] Test RQ workers processing jobs
- [ ] Frontend loading correctly
- [ ] Admin dashboard accessible

---

## Support & Resources

### Useful Links
- FastAPI Docs: https://fastapi.tiangolo.com/
- RQ Docs: https://python-rq.org/
- Redis Docs: https://redis.io/docs/
- MongoDB Docs: https://www.mongodb.com/docs/
- Nginx Docs: https://nginx.org/en/docs/
- Supervisor Docs: http://supervisord.org/

### Monitoring Tools
- RQ Dashboard: https://rq.yourdomain.com
- MongoDB Compass: https://www.mongodb.com/products/compass
- Redis Insight: https://redis.com/redis-enterprise/redis-insight/

---

**Deployment Guide Complete! 🚀**

Your RankForge application should now be running in production with:
- ✅ Backend API on HTTPS
- ✅ Frontend on HTTPS  
- ✅ Redis running
- ✅ 4 RQ workers processing background jobs
- ✅ MongoDB with proper indexes
- ✅ SSL certificates
- ✅ Process monitoring with Supervisor
- ✅ Log management
- ✅ Backup automation

**Need Help?** Check the troubleshooting section or review service logs.
