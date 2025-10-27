# RankForge SEO Platform - Production Deployment Guide

## 🚀 Quick Start Deployment

### Prerequisites

Ensure the following are installed and running on your server:
- Ubuntu 20.04+ or similar Linux distribution
- Git
- Node.js 16+ and npm/yarn
- Python 3.8+
- Nginx
- Redis (will be auto-started by script)
- Docker (with MongoDB container running)

### MongoDB Container

Ensure your MongoDB Docker container is running:
```bash
docker ps | grep rankforgedb
```

Expected output:
```
c48e6f334e70   mongo:latest   ...   0.0.0.0:27018->27018/tcp   rankforgedb
```

---

## 📦 Initial Deployment

### Step 1: Download the Deployment Script

```bash
# Download the deployment script
wget https://raw.githubusercontent.com/mansinghjoys-byte/SEO/AEo4/deploy_production.sh

# Or if you have the repository cloned
cd /path/to/repo
chmod +x deploy_production.sh
```

### Step 2: Make Script Executable

```bash
chmod +x deploy_production.sh
```

### Step 3: Run Deployment

```bash
sudo ./deploy_production.sh
```

The script will:
1. ✅ Clone repository from GitHub (branch: AEo4)
2. ✅ Check and start Redis
3. ✅ Setup backend with virtual environment
4. ✅ Configure MongoDB connection (localhost:27018)
5. ✅ Create Super Admin user
6. ✅ Setup RQ workers for async tasks
7. ✅ Start backend on localhost:8000 (not exposed to public)
8. ✅ Build frontend production bundle
9. ✅ Configure Nginx for http://seo.mj.publicvm.com

### Step 4: Save Super Admin Credentials

After deployment completes, you'll see:

```
=================================
SUPER ADMIN CREDENTIALS
=================================

Email:    admin@rankforge.com
Password: RankForge@Admin2025!Secure

Admin Login URL: http://seo.mj.publicvm.com/admin/login
```

**⚠️ IMPORTANT: Save these credentials immediately!**

---

## 🔄 Updating the Application

For subsequent updates (code changes, bug fixes, new features):

### Quick Update Method

```bash
cd /var/www/rankforge
sudo ./update_production.sh
```

This will:
- Pull latest code from GitHub
- Update backend dependencies
- Rebuild frontend
- Restart all services

### Manual Update Method

```bash
# Navigate to deployment directory
cd /var/www/rankforge

# Pull latest changes
git pull origin AEo4

# Update backend
cd backend
source venv/bin/activate
pip install -r requirements.txt

# Update frontend
cd ../frontend
yarn install
yarn build

# Restart services
sudo systemctl restart rankforge-backend
sudo systemctl restart rankforge-worker
sudo systemctl reload nginx
```

---

## 🛠 Service Management

### View Service Status

```bash
# All services
sudo systemctl status rankforge-backend
sudo systemctl status rankforge-worker
sudo systemctl status redis-server
sudo systemctl status nginx

# Docker MongoDB
docker ps | grep rankforgedb
```

### Restart Services

```bash
# Backend API
sudo systemctl restart rankforge-backend

# RQ Worker
sudo systemctl restart rankforge-worker

# Nginx
sudo systemctl restart nginx

# Redis
sudo systemctl restart redis-server
```

### View Logs

```bash
# Backend logs (live)
sudo journalctl -u rankforge-backend -f

# Worker logs (live)
sudo journalctl -u rankforge-worker -f

# Nginx access logs
sudo tail -f /var/log/nginx/rankforge_access.log

# Nginx error logs
sudo tail -f /var/log/nginx/rankforge_error.log
```

---

## 🏗 Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                    seo.mj.publicvm.com                  │
│                         (Public)                         │
└──────────────────────┬──────────────────────────────────┘
                       │
                  ┌────▼─────┐
                  │  Nginx   │
                  │  Port 80 │
                  └────┬─────┘
                       │
         ┌─────────────┴──────────────┐
         │                            │
    ┌────▼────┐              ┌────────▼────────┐
    │ Frontend│              │  Backend API    │
    │  (Static│              │  localhost:8000 │
    │  Build) │              │  (Not Exposed)  │
    └─────────┘              └────────┬────────┘
                                      │
                      ┌───────────────┼───────────────┐
                      │               │               │
                 ┌────▼─────┐   ┌────▼────┐    ┌────▼────┐
                 │ MongoDB  │   │  Redis  │    │   RQ    │
                 │Container │   │ :6379   │    │ Worker  │
                 │  :27018  │   └─────────┘    └─────────┘
                 └──────────┘
```

### Key Points:
- ✅ Frontend served via Nginx on port 80
- ✅ Backend API runs on localhost:8000 (NOT exposed to internet)
- ✅ Nginx proxies `/api` requests to backend
- ✅ MongoDB accessible only via localhost:27018
- ✅ Redis handles background jobs
- ✅ RQ workers process async tasks

---

## 🔒 Security Features

1. **Backend Not Exposed**: Backend runs on localhost:8000, accessible only through Nginx proxy
2. **MongoDB Security**: MongoDB only accessible on localhost:27018
3. **Redis Security**: Redis only accessible on localhost:6379
4. **Nginx Security Headers**: X-Frame-Options, X-Content-Type-Options, XSS-Protection enabled

---

## 📊 URLs and Endpoints

### Public URLs
- **Frontend**: http://seo.mj.publicvm.com
- **Admin Login**: http://seo.mj.publicvm.com/admin/login
- **API (proxied)**: http://seo.mj.publicvm.com/api

### Internal (localhost only)
- **Backend Direct**: http://localhost:8000
- **Backend Health**: http://localhost:8000/api/health
- **MongoDB**: mongodb://localhost:27018
- **Redis**: redis://localhost:6379

---

## 🧪 Testing the Deployment

### 1. Test Frontend
```bash
curl http://seo.mj.publicvm.com
# Should return HTML content
```

### 2. Test Backend (via Nginx proxy)
```bash
curl http://seo.mj.publicvm.com/api/health
# Should return: {"status":"healthy"}
```

### 3. Test MongoDB Connection
```bash
docker exec rankforgedb mongosh --port 27018 --eval "db.adminCommand('ping')"
# Should return: { ok: 1 }
```

### 4. Test Redis
```bash
redis-cli ping
# Should return: PONG
```

### 5. Test Admin Login
- Visit: http://seo.mj.publicvm.com/admin/login
- Login with Super Admin credentials
- Should successfully access admin dashboard

---

## 🔧 Troubleshooting

### Backend Not Starting
```bash
# Check logs
sudo journalctl -u rankforge-backend -n 50

# Common issues:
# - MongoDB not accessible (check Docker container)
# - Python dependencies missing (run: pip install -r requirements.txt)
# - Port 8000 already in use (check: sudo lsof -i :8000)
```

### Frontend Not Loading
```bash
# Check Nginx configuration
sudo nginx -t

# Check Nginx error logs
sudo tail -f /var/log/nginx/rankforge_error.log

# Rebuild frontend
cd /var/www/rankforge/frontend
yarn build
```

### Worker Not Processing Jobs
```bash
# Check worker status
sudo systemctl status rankforge-worker

# Check worker logs
sudo journalctl -u rankforge-worker -n 50

# Restart worker
sudo systemctl restart rankforge-worker
```

### MongoDB Connection Failed
```bash
# Check if container is running
docker ps | grep rankforgedb

# Check if port 27018 is accessible
telnet localhost 27018

# If container stopped, start it:
docker start rankforgedb
```

---

## 📝 Configuration Files

### Backend .env Location
```
/var/www/rankforge/backend/.env
```

### Frontend .env Location
```
/var/www/rankforge/frontend/.env
```

### Nginx Configuration
```
/etc/nginx/sites-available/rankforge
/etc/nginx/sites-enabled/rankforge
```

### Systemd Services
```
/etc/systemd/system/rankforge-backend.service
/etc/systemd/system/rankforge-worker.service
```

---

## 🎯 Post-Deployment Checklist

- [ ] All services running (backend, worker, redis, nginx)
- [ ] MongoDB container running
- [ ] Frontend accessible at http://seo.mj.publicvm.com
- [ ] API health check passing
- [ ] Admin login working with Super Admin credentials
- [ ] Super Admin credentials saved securely
- [ ] Logs monitoring setup

---

## 📞 Support

For issues or questions:
1. Check service logs (see "View Logs" section)
2. Review troubleshooting section
3. Check GitHub repository: https://github.com/mansinghjoys-byte/SEO

---

## 🔄 Rollback Procedure

If deployment fails or issues occur:

```bash
cd /var/www/rankforge

# Rollback to previous commit
git log --oneline  # Find previous working commit
git checkout <commit-hash>

# Rebuild and restart
./update_production.sh
```

---

**Last Updated**: 2025-01-XX
**Deployment Script Version**: 1.0.0
