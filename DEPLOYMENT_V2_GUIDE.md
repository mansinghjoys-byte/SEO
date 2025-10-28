# Enhanced Deployment Script v2.0 - User Guide

## 🆕 What's New in v2.0

### Interactive Redis Configuration
- **User Prompts**: Ask whether to use existing Redis or install new instance
- **Port Selection**: Let user choose Redis port (handles conflicts automatically)
- **Password Support**: Optional Redis password authentication
- **Custom Connections**: Support for remote Redis instances
- **Multiple Instances**: Can run multiple Redis instances on different ports

### Enhanced Error Handling
- **Graceful Failures**: Script doesn't exit on first error
- **Detailed Logging**: All actions logged to timestamped file
- **Port Conflict Detection**: Automatically detects and handles port conflicts
- **Service Verification**: Verifies each service starts correctly
- **Rollback Support**: Stops services if deployment fails

### Edge Cases Handled
1. ✅ Redis already running on desired port
2. ✅ Port conflicts with other services
3. ✅ Existing deployment directory
4. ✅ MongoDB container not running
5. ✅ Missing commands (with helpful install hints)
6. ✅ Failed service starts (with detailed logs)
7. ✅ Network connectivity issues
8. ✅ Dependency installation failures

---

## 📋 Prerequisites

### Required Software
- Ubuntu 20.04+ (or compatible Linux)
- Git
- Node.js 16+ and npm (or yarn)
- Python 3.8+
- Nginx
- Docker (with MongoDB container)

### MongoDB Container Must Be Running
```bash
docker ps | grep rankforgedb
```

Expected: Container `rankforgedb` on port 27018

---

## 🚀 Usage

### Basic Usage (Recommended)

```bash
sudo ./deploy_production_v2.sh
```

The script will:
1. Ask questions about Redis configuration
2. Guide you through each step
3. Handle errors gracefully
4. Provide detailed feedback

### Sample Interaction

```
╔════════════════════════════════════════════════════════════════╗
║     RankForge SEO Platform - Production Deployment v2.0       ║
╚════════════════════════════════════════════════════════════════╝

Deployment log: /tmp/rankforge_deploy_20250127_120000.log

==> Running pre-flight checks...
✓ Running with root privileges
✓ git is installed
✓ node is installed
✓ npm is installed
✓ python3 is installed
✓ nginx is installed
✓ docker is installed
✓ All required commands are available

==> Step 1: Fetching code from GitHub...
Directory /var/www/rankforge already exists
Pull latest changes from GitHub? [Y/n]: y
✓ Repository updated

╔════════════════════════════════════════════════════════════════╗
║                    Redis Configuration                         ║
╚════════════════════════════════════════════════════════════════╝

ℹ RankForge requires Redis for background job processing

✓ Redis is already installed
==> Checking for running Redis instances...
ℹ Redis detected on port 6379

Redis Setup Options:

Detected running Redis on port(s): 6379

  1) Use existing Redis instance
  2) Install new Redis instance on different port
  3) Configure custom Redis connection

Select option (1-3) [1]: 
```

---

## 🔧 Redis Configuration Options

### Option 1: Use Existing Redis

**When to use**: Redis already running on your server

**What it does**:
- Detects running Redis instances
- Tests connection
- Uses existing Redis for RankForge

**Prompts**:
```
Select option (1-3) [1]: 1
Enter Redis port [6379]: <enter>
✓ Connected to Redis on localhost:6379
```

---

### Option 2: Install New Redis Instance

**When to use**: Want dedicated Redis for RankForge

**What it does**:
- Installs Redis if not present
- Creates custom configuration
- Sets up systemd service
- Configures on specified port

**Prompts**:
```
Select option (1-3) [1]: 2
Enter port for Redis [6379]: 6380
✓ Port 6380 is available
Enable Redis password? [y/N]: y
Enter password: MySecurePassword123
✓ Redis installed
✓ Config created at /etc/redis/redis_6380.conf
✓ Redis service started
✓ Redis responding to PING
```

**Configuration**:
- Config file: `/etc/redis/redis_<port>.conf`
- Data directory: `/var/lib/redis_<port>`
- Log file: `/var/log/redis/redis_<port>.log`
- Systemd service: `redis_<port>.service`
- Memory limit: 512MB
- Eviction policy: allkeys-lru
- Persistence: Disabled (for performance)

---

### Option 3: Custom Redis Connection

**When to use**: Using remote Redis server or special setup

**What it does**:
- Connects to user-specified Redis host/port
- Supports password authentication
- Tests connection before proceeding

**Prompts**:
```
Select option (1-3) [1]: 3
Enter Redis host [localhost]: redis.example.com
Enter Redis port [6379]: 6380
Requires password? [y/N]: y
Enter password: MySecurePassword123
==> Testing connection...
✓ Connected to Redis
```

---

## 🛡️ Error Handling Examples

### Example 1: Port Conflict

```
Enter port for Redis [6379]: 6379
✗ Port 6379 is already in use by: redis-server 1234
Try another port? [Y/n]: y
Enter alternative port [6380]: 6380
✓ Port 6380 is available
```

### Example 2: MongoDB Container Not Running

```
==> Step 3: Checking MongoDB...
✗ MongoDB container (rankforgedb) is NOT running
ℹ Start it with: docker start rankforgedb
Try to start MongoDB container now? [Y/n]: y
✓ MongoDB container started
✓ MongoDB connection successful
```

### Example 3: Service Start Failure

```
==> Step 6: Setting up systemd services...
✗ Backend failed to start

● rankforge-backend.service - RankForge Backend API
   Loaded: loaded
   Active: failed (Result: exit-code)
   
✗ Deployment failed. Check logs at: /tmp/rankforge_deploy_20250127_120000.log
```

View detailed logs:
```bash
cat /tmp/rankforge_deploy_20250127_120000.log
```

---

## 📊 Configuration Summary

At the end of setup, you'll see:

```
╔════════════════════════════════════════════════════════════════╗
║            DEPLOYMENT COMPLETED SUCCESSFULLY                   ║
╚════════════════════════════════════════════════════════════════╝

SERVICES STATUS:
✓ Backend: RUNNING
✓ Worker: RUNNING
✓ Nginx: RUNNING
✓ Redis: RUNNING (port 6380)
✓ MongoDB: RUNNING

DEPLOYMENT INFO:
  Directory: /var/www/rankforge
  Frontend: http://seo.mj.publicvm.com
  Backend: localhost:8000 (internal)
  MongoDB: localhost:27018
  Redis: localhost:6380
  Log: /tmp/rankforge_deploy_20250127_120000.log

SUPER ADMIN CREDENTIALS:

⚠ SAVE THESE CREDENTIALS SECURELY!

  Email:    admin@rankforge.com
  Password: RankForge@Admin2025!Secure

  Admin URL: http://seo.mj.publicvm.com/admin/login

USEFUL COMMANDS:
  Backend logs:  sudo journalctl -u rankforge-backend -f
  Worker logs:   sudo journalctl -u rankforge-worker -f
  Restart:       sudo systemctl restart rankforge-backend

🚀 RankForge SEO Platform is now live!
```

---

## 🔍 Troubleshooting

### Check Deployment Log

Every deployment creates a detailed log:
```bash
# Find latest log
ls -lt /tmp/rankforge_deploy_*.log | head -1

# View log
cat /tmp/rankforge_deploy_20250127_120000.log
```

### Verify Redis

```bash
# If using default Redis
redis-cli ping

# If using custom port
redis-cli -p 6380 ping

# If using password
redis-cli -p 6380 -a YourPassword ping

# Check systemd service
systemctl status redis_6380
journalctl -u redis_6380 -n 50
```

### Verify Services

```bash
# Check all services
systemctl status rankforge-backend
systemctl status rankforge-worker
systemctl status nginx

# View logs
sudo journalctl -u rankforge-backend -f
sudo journalctl -u rankforge-worker -f
```

### Common Issues

**Issue**: "Port already in use"
```bash
# Find what's using the port
sudo lsof -i :6379

# Kill the process or choose different port
```

**Issue**: "Cannot connect to MongoDB"
```bash
# Check if container is running
docker ps | grep rankforgedb

# Start container
docker start rankforgedb

# Check port
docker port rankforgedb
```

**Issue**: "Backend not responding"
```bash
# Check backend logs
sudo journalctl -u rankforge-backend -n 100

# Test backend directly
curl http://localhost:8000/api/health

# Restart backend
sudo systemctl restart rankforge-backend
```

---

## 🔄 Re-running Deployment

If deployment fails, you can:

1. **Fix the issue** (e.g., start MongoDB, free up port)
2. **Re-run the script**:
   ```bash
   sudo ./deploy_production_v2.sh
   ```

The script will:
- Detect existing installation
- Offer to update from GitHub
- Use existing Redis or reconfigure
- Skip already completed steps

---

## 🆚 Comparison: v1.0 vs v2.0

| Feature | v1.0 | v2.0 |
|---------|------|------|
| Redis Setup | Automatic | Interactive with options |
| Port Selection | Fixed (6379) | User selectable |
| Error Handling | Exit on error | Graceful with rollback |
| Logging | Basic | Detailed with timestamps |
| Port Conflicts | Fails | Detects and offers alternatives |
| Multiple Redis | No | Yes, multiple instances |
| Custom Redis | No | Yes, remote connections |
| Service Verification | Basic | Comprehensive |
| MongoDB Check | Assumes running | Offers to start |
| Progress Feedback | Minimal | Detailed with colors |

---

## 📁 Generated Files

### Configuration Files
- `/etc/redis/redis_<port>.conf` - Redis configuration
- `/app/backend/.env` - Backend environment variables
- `/app/frontend/.env` - Frontend environment variables
- `/etc/nginx/sites-available/rankforge` - Nginx configuration

### Service Files
- `/etc/systemd/system/redis_<port>.service` - Redis service
- `/etc/systemd/system/rankforge-backend.service` - Backend service
- `/etc/systemd/system/rankforge-worker.service` - Worker service

### Log Files
- `/tmp/rankforge_deploy_*.log` - Deployment log
- `/var/log/redis/redis_<port>.log` - Redis logs
- `/var/log/nginx/rankforge_*.log` - Nginx logs

---

## 🎯 Best Practices

### Before Deployment
1. ✅ Ensure MongoDB container is running
2. ✅ Check available ports (if installing new Redis)
3. ✅ Have GitHub credentials ready
4. ✅ Note any existing Redis instances

### During Deployment
1. ✅ Read prompts carefully
2. ✅ Choose appropriate Redis option
3. ✅ Save Super Admin credentials immediately
4. ✅ Note the deployment log location

### After Deployment
1. ✅ Test frontend: http://seo.mj.publicvm.com
2. ✅ Test admin login
3. ✅ Verify all services running
4. ✅ Save deployment log
5. ✅ Document Redis configuration

---

## 📞 Getting Help

If issues persist:

1. **Check deployment log**: `/tmp/rankforge_deploy_*.log`
2. **Review service logs**: `journalctl -u <service-name>`
3. **Verify prerequisites**: All required software installed
4. **Test connectivity**: MongoDB, Redis accessible
5. **Check ports**: No conflicts on required ports

---

**Script Version**: 2.0.0  
**Last Updated**: January 2025  
**Compatibility**: Ubuntu 20.04+, Debian 10+
