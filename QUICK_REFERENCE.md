# 🚀 RankForge SEO Platform - Quick Reference Card

## 📋 Super Admin Credentials

```
Email:    admin@rankforge.com
Password: RankForge@Admin2025!Secure
URL:      http://seo.mj.publicvm.com/admin/login
```

## 🌐 URLs

| Service | URL | Access |
|---------|-----|--------|
| Frontend | http://seo.mj.publicvm.com | Public |
| Admin Panel | http://seo.mj.publicvm.com/admin/login | Public |
| API (proxied) | http://seo.mj.publicvm.com/api | Public |
| Backend Direct | http://localhost:8000 | Internal Only |
| Backend Health | http://localhost:8000/api/health | Internal Only |

## 🗄️ Database

| Service | Connection | Access |
|---------|-----------|--------|
| MongoDB | mongodb://localhost:27018 | Internal Only |
| Database Name | seo_platform | - |
| Docker Container | rankforgedb | - |
| Redis | redis://localhost:6379 | Internal Only |

## 🛠️ Essential Commands

### Deployment
```bash
# Initial deployment
sudo ./deploy_production.sh

# Update deployment
sudo ./update_production.sh

# Health check
sudo ./health_check.sh
```

### Service Management
```bash
# Start services
sudo systemctl start rankforge-backend
sudo systemctl start rankforge-worker

# Stop services
sudo systemctl stop rankforge-backend
sudo systemctl stop rankforge-worker

# Restart services
sudo systemctl restart rankforge-backend
sudo systemctl restart rankforge-worker
sudo systemctl reload nginx

# Check status
sudo systemctl status rankforge-backend
sudo systemctl status rankforge-worker
```

### Logs
```bash
# Live backend logs
sudo journalctl -u rankforge-backend -f

# Live worker logs
sudo journalctl -u rankforge-worker -f

# Nginx access logs
sudo tail -f /var/log/nginx/rankforge_access.log

# Nginx error logs
sudo tail -f /var/log/nginx/rankforge_error.log

# Last 50 lines of backend logs
sudo journalctl -u rankforge-backend -n 50
```

### Docker MongoDB
```bash
# Check container status
docker ps | grep rankforgedb

# Start container
docker start rankforgedb

# Stop container
docker stop rankforgedb

# MongoDB shell
docker exec -it rankforgedb mongosh --port 27018

# Check MongoDB connection
docker exec rankforgedb mongosh --port 27018 --eval "db.adminCommand('ping')"
```

### Redis
```bash
# Test Redis
redis-cli ping

# View Redis info
redis-cli info

# Monitor Redis
redis-cli monitor
```

## 📁 Important Paths

| Item | Path |
|------|------|
| Deployment Directory | /var/www/rankforge |
| Backend Code | /var/www/rankforge/backend |
| Frontend Code | /var/www/rankforge/frontend |
| Frontend Build | /var/www/rankforge/frontend/build |
| Backend .env | /var/www/rankforge/backend/.env |
| Frontend .env | /var/www/rankforge/frontend/.env |
| Nginx Config | /etc/nginx/sites-available/rankforge |
| Backend Service | /etc/systemd/system/rankforge-backend.service |
| Worker Service | /etc/systemd/system/rankforge-worker.service |

## 🔧 Troubleshooting Quick Fixes

### Backend Won't Start
```bash
# Check logs
sudo journalctl -u rankforge-backend -n 50

# Check if port is in use
sudo lsof -i :8000

# Restart service
sudo systemctl restart rankforge-backend
```

### Frontend Not Loading
```bash
# Check Nginx
sudo nginx -t
sudo systemctl restart nginx

# Rebuild frontend
cd /var/www/rankforge/frontend
yarn build
```

### MongoDB Connection Issues
```bash
# Check container
docker ps | grep rankforgedb

# Start if stopped
docker start rankforgedb

# Test connection
docker exec rankforgedb mongosh --port 27018 --eval "db.adminCommand('ping')"
```

### Worker Not Processing
```bash
# Check worker logs
sudo journalctl -u rankforge-worker -n 50

# Restart worker
sudo systemctl restart rankforge-worker

# Check Redis
redis-cli ping
```

## 🔄 Update Procedure

```bash
# 1. Navigate to deployment directory
cd /var/www/rankforge

# 2. Pull latest code
git pull origin AEo4

# 3. Update backend
cd backend
source venv/bin/activate
pip install -r requirements.txt

# 4. Rebuild frontend
cd ../frontend
yarn install
yarn build

# 5. Restart services
sudo systemctl restart rankforge-backend
sudo systemctl restart rankforge-worker
sudo systemctl reload nginx
```

## 🏥 Health Check

Run comprehensive health check:
```bash
sudo /var/www/rankforge/health_check.sh
```

Quick checks:
```bash
# All services status
sudo systemctl status rankforge-backend rankforge-worker nginx redis-server

# Backend health
curl http://localhost:8000/api/health

# Frontend access
curl -I http://seo.mj.publicvm.com
```

## 📊 Monitoring

### Check Service Logs
```bash
# Backend
sudo journalctl -u rankforge-backend --since "1 hour ago" | grep -i error

# Worker
sudo journalctl -u rankforge-worker --since "1 hour ago" | grep -i error
```

### System Resources
```bash
# CPU and Memory
htop

# Disk space
df -h

# Port usage
sudo netstat -tuln | grep -E '(8000|27018|6379)'
```

## 🚨 Emergency Rollback

```bash
cd /var/www/rankforge

# View commit history
git log --oneline

# Rollback to specific commit
git checkout <commit-hash>

# Rebuild and restart
sudo ./update_production.sh
```

## 📞 Support Contacts

- GitHub Repository: https://github.com/mansinghjoys-byte/SEO
- Branch: AEo4
- Documentation: /var/www/rankforge/DEPLOYMENT_GUIDE.md

---

**Print this card and keep it handy for quick reference!**
