# 🚀 RankForge Deployment - Quick Reference Card

## One-Command Deploy (Automated)

```bash
# Copy files to server first, then run:
sudo bash deploy.sh
```

## Manual Deploy - Essential Commands

### 1. Install Dependencies (Ubuntu)
```bash
# System packages
sudo apt-get update && sudo apt-get install -y \
  python3.11 python3.11-venv nodejs yarn \
  mongodb-org redis-server nginx supervisor

# Start services
sudo systemctl start mongod redis-server nginx supervisor
sudo systemctl enable mongod redis-server nginx supervisor
```

### 2. Setup Application
```bash
# Backend
cd /home/rankforge/app/backend
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Frontend
cd /home/rankforge/app/frontend
yarn install
yarn build
```

### 3. Configure Supervisor

**Backend** (`/etc/supervisor/conf.d/rankforge-backend.conf`):
```ini
[program:rankforge-backend]
directory=/home/rankforge/app/backend
command=/home/rankforge/app/backend/venv/bin/uvicorn server:app --host 0.0.0.0 --port 8001
user=rankforge
autostart=true
autorestart=true
environment=PYTHONPATH="/home/rankforge/app/backend",MONGO_URL="mongodb://localhost:27017",REDIS_URL="redis://localhost:6379/0"
```

**Workers** (`/etc/supervisor/conf.d/rankforge-workers.conf`):
```ini
[program:rankforge-worker]
directory=/home/rankforge/app/backend
command=/home/rankforge/app/backend/venv/bin/rq worker high default low --url redis://localhost:6379/0
process_name=%(program_name)s-%(process_num)s
numprocs=4
user=rankforge
autostart=true
autorestart=true
environment=PYTHONPATH="/home/rankforge/app/backend",REDIS_URL="redis://localhost:6379/0"
```

```bash
sudo supervisorctl reread && sudo supervisorctl update
```

### 4. Configure Nginx

**File**: `/etc/nginx/sites-available/rankforge`
```nginx
# API
server {
    listen 80;
    server_name api.yourdomain.com;
    
    location / {
        proxy_pass http://127.0.0.1:8001;
        proxy_set_header Host $host;
    }
}

# Frontend
server {
    listen 80;
    server_name yourdomain.com;
    root /home/rankforge/app/frontend/build;
    
    location / {
        try_files $uri /index.html;
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/rankforge /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
```

### 5. SSL Setup
```bash
sudo apt-get install -y certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com -d api.yourdomain.com
```

---

## Daily Operations

### Start/Stop/Restart
```bash
# All services
sudo supervisorctl restart all
sudo supervisorctl stop all
sudo supervisorctl start all

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
# Backend
sudo tail -f /var/log/rankforge/backend.out.log
sudo tail -f /var/log/rankforge/backend.err.log

# Workers
sudo tail -f /var/log/rankforge/worker-0.out.log

# All logs
sudo tail -f /var/log/rankforge/*.log

# Nginx
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### Health Checks
```bash
# API health
curl http://localhost:8001/api/health

# Redis
redis-cli ping

# MongoDB
mongosh --eval "db.adminCommand('ping')"

# Check worker queues
redis-cli LLEN rq:queue:default

# Service status
sudo supervisorctl status
```

---

## RQ Worker Management

### Check Workers
```bash
# Active workers
redis-cli CLIENT LIST | grep worker

# Queue lengths
redis-cli LLEN rq:queue:high
redis-cli LLEN rq:queue:default
redis-cli LLEN rq:queue:low

# Failed jobs
redis-cli LLEN rq:queue:failed
```

### RQ Dashboard (Optional)
```bash
# Install
pip install rq-dashboard

# Run
rq-dashboard --redis-url redis://localhost:6379/0

# Access: http://localhost:9181
```

### Queue Jobs from Python
```python
from redis import Redis
from rq import Queue

redis_conn = Redis(host='localhost', port=6379)
queue = Queue('default', connection=redis_conn)

# Enqueue job
job = queue.enqueue('tasks.my_function', arg1, arg2)
print(f"Job ID: {job.id}")

# Check status
job.refresh()
print(f"Status: {job.get_status()}")
```

---

## Troubleshooting

### Backend Not Starting
```bash
# Check logs
sudo tail -100 /var/log/rankforge/backend.err.log

# Check port
sudo lsof -i :8001

# Restart
sudo supervisorctl restart rankforge-backend
```

### Workers Not Processing
```bash
# Check worker logs
sudo tail -100 /var/log/rankforge/worker-0.err.log

# Check Redis
redis-cli ping

# Check queues
redis-cli KEYS "rq:*"

# Restart workers
sudo supervisorctl restart rankforge-worker:*
```

### Nginx Issues
```bash
# Test config
sudo nginx -t

# Check logs
sudo tail -100 /var/log/nginx/error.log

# Reload
sudo systemctl reload nginx
```

### Redis Memory Full
```bash
# Check memory
redis-cli INFO memory

# Increase limit
sudo nano /etc/redis/redis.conf
# Set: maxmemory 1gb

sudo systemctl restart redis-server
```

---

## Database Maintenance

### Backup MongoDB
```bash
# Backup
mongodump --out=/backup/$(date +%Y%m%d) --db=seo_platform

# Restore
mongorestore --db=seo_platform /backup/20250114
```

### Create Indexes
```bash
mongosh seo_platform << 'EOF'
db.sites.createIndex({ "user_id": 1, "site_id": 1 })
db.audits.createIndex({ "site_id": 1, "created_at": -1 })
db.users.createIndex({ "email": 1 }, { unique: true })
EOF
```

---

## Update Deployment

```bash
# Update code
cd /home/rankforge/app
git pull

# Update backend
cd backend
source venv/bin/activate
pip install -r requirements.txt

# Update frontend
cd ../frontend
yarn install
yarn build

# Restart services
sudo supervisorctl restart all
```

---

## Monitoring

### System Resources
```bash
# Disk space
df -h

# Memory
free -h

# CPU
top

# Process list
ps aux | grep rankforge
```

### Application Metrics
```bash
# Request count (from Nginx logs)
sudo grep -c "GET" /var/log/nginx/access.log

# Error count
sudo grep -c "ERROR" /var/log/rankforge/*.log

# Worker job count (last hour)
sudo grep "Job OK" /var/log/rankforge/worker-*.log | grep "$(date +%Y-%m-%d %H)" | wc -l
```

---

## Environment Variables

**Backend** (`.env`):
```bash
MONGO_URL=mongodb://localhost:27017
DB_NAME=seo_platform
REDIS_URL=redis://localhost:6379/0
GROQ_API_KEY=your_key_here
SECRET_KEY=your_jwt_secret
ADMIN_EMAIL=admin@rankforge.com
ADMIN_PASSWORD=secure_password
```

**Frontend** (`.env`):
```bash
REACT_APP_BACKEND_URL=https://api.yourdomain.com/api
```

---

## Performance Tuning

### Redis
```bash
# /etc/redis/redis.conf
maxmemory 1gb
maxmemory-policy allkeys-lru
```

### MongoDB
```bash
# /etc/mongod.conf
net:
  maxIncomingConnections: 200
storage:
  wiredTiger:
    engineConfig:
      cacheSizeGB: 1
```

### Nginx
```bash
# /etc/nginx/nginx.conf
worker_processes auto;
worker_connections 1024;
keepalive_timeout 65;
client_max_body_size 50M;
```

### Supervisor Workers
```bash
# Adjust numprocs based on CPU cores
# /etc/supervisor/conf.d/rankforge-workers.conf
numprocs=4  # Change based on server capacity
```

---

## Security Checklist

- [ ] Change default admin password
- [ ] Set strong SECRET_KEY
- [ ] Enable MongoDB authentication
- [ ] Configure firewall (ufw)
- [ ] Install fail2ban
- [ ] Set up SSL certificates
- [ ] Regular backups scheduled
- [ ] Update system packages
- [ ] Secure Redis (bind to localhost)
- [ ] Review Nginx security headers

---

## Quick Deploy Checklist

1. [ ] Server provisioned (Ubuntu 20.04/22.04)
2. [ ] Domain DNS configured
3. [ ] Dependencies installed
4. [ ] Application files uploaded
5. [ ] Environment variables set
6. [ ] Supervisor configured
7. [ ] Nginx configured
8. [ ] SSL certificates installed
9. [ ] Services started
10. [ ] Health checks passed
11. [ ] Test endpoints working
12. [ ] Workers processing jobs
13. [ ] Backups scheduled
14. [ ] Monitoring set up

---

## Support Resources

- **Full Guide**: `/home/rankforge/app/DEPLOYMENT_GUIDE.md`
- **RQ Dashboard**: http://localhost:9181
- **Supervisor Docs**: http://supervisord.org
- **RQ Docs**: https://python-rq.org

---

**Emergency Restart Everything:**
```bash
sudo systemctl restart mongod redis-server nginx
sudo supervisorctl restart all
```

**Check Everything:**
```bash
sudo supervisorctl status
sudo systemctl status mongod redis-server nginx
curl http://localhost:8001/api/health
```

---

*Keep this card handy for quick reference during deployment and maintenance!*
