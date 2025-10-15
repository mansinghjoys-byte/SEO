#!/bin/bash
# RankForge Quick Deploy Script
# This script automates the deployment process

set -e

echo "🚀 RankForge Deployment Script"
echo "================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
   echo -e "${RED}Please run as root or with sudo${NC}"
   exit 1
fi

# Get actual user (in case running with sudo)
ACTUAL_USER=${SUDO_USER:-$USER}
APP_DIR="/home/$ACTUAL_USER/rankforge"

echo -e "${GREEN}Step 1: System Update${NC}"
apt-get update
apt-get upgrade -y

echo -e "${GREEN}Step 2: Installing Dependencies${NC}"
apt-get install -y software-properties-common curl wget git build-essential

# Python 3.11
echo "  Installing Python 3.11..."
add-apt-repository ppa:deadsnakes/ppa -y
apt-get update
apt-get install -y python3.11 python3.11-venv python3.11-dev python3-pip

# Node.js
echo "  Installing Node.js 18..."
curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
apt-get install -y nodejs

# Yarn
echo "  Installing Yarn..."
curl -sS https://dl.yarnpkg.com/debian/pubkey.gpg | apt-key add -
echo "deb https://dl.yarnpkg.com/debian/ stable main" > /etc/apt/sources.list.d/yarn.list
apt-get update
apt-get install -y yarn

# MongoDB
echo "  Installing MongoDB..."
curl -fsSL https://www.mongodb.org/static/pgp/server-6.0.asc | gpg --dearmor -o /usr/share/keyrings/mongodb-server-6.0.gpg
echo "deb [ arch=amd64,arm64 signed-by=/usr/share/keyrings/mongodb-server-6.0.gpg ] https://repo.mongodb.org/apt/ubuntu $(lsb_release -cs)/mongodb-org/6.0 multiverse" > /etc/apt/sources.list.d/mongodb-org-6.0.list
apt-get update
apt-get install -y mongodb-org

# Redis
echo "  Installing Redis..."
apt-get install -y redis-server

# Nginx
echo "  Installing Nginx..."
apt-get install -y nginx

# Supervisor
echo "  Installing Supervisor..."
apt-get install -y supervisor

echo -e "${GREEN}Step 3: Starting Services${NC}"
systemctl start mongod
systemctl enable mongod
systemctl start redis-server
systemctl enable redis-server
systemctl start nginx
systemctl enable nginx
systemctl start supervisor
systemctl enable supervisor

echo -e "${GREEN}Step 4: Configuring Redis${NC}"
cat > /etc/redis/redis.conf.append << EOF
supervised systemd
maxmemory 512mb
maxmemory-policy allkeys-lru
EOF
cat /etc/redis/redis.conf.append >> /etc/redis/redis.conf
rm /etc/redis/redis.conf.append
systemctl restart redis-server

echo -e "${GREEN}Step 5: Setting Up Application${NC}"
mkdir -p $APP_DIR
mkdir -p /var/log/rankforge
chown -R $ACTUAL_USER:$ACTUAL_USER $APP_DIR
chown -R $ACTUAL_USER:$ACTUAL_USER /var/log/rankforge

echo -e "${YELLOW}Application files should be in: $APP_DIR${NC}"
echo -e "${YELLOW}Expected structure:${NC}"
echo "  $APP_DIR/backend/"
echo "  $APP_DIR/frontend/"

if [ ! -d "$APP_DIR/backend" ] || [ ! -d "$APP_DIR/frontend" ]; then
    echo -e "${RED}ERROR: Application directories not found!${NC}"
    echo "Please copy your application files to $APP_DIR first"
    echo "Then run this script again"
    exit 1
fi

echo -e "${GREEN}Step 6: Backend Setup${NC}"
cd $APP_DIR/backend
sudo -u $ACTUAL_USER python3.11 -m venv venv
sudo -u $ACTUAL_USER $APP_DIR/backend/venv/bin/pip install --upgrade pip
sudo -u $ACTUAL_USER $APP_DIR/backend/venv/bin/pip install -r requirements.txt

echo -e "${GREEN}Step 7: Frontend Setup${NC}"
cd $APP_DIR/frontend
sudo -u $ACTUAL_USER yarn install
sudo -u $ACTUAL_USER yarn build

echo -e "${GREEN}Step 8: Supervisor Configuration${NC}"

# Backend
cat > /etc/supervisor/conf.d/rankforge-backend.conf << EOF
[program:rankforge-backend]
directory=$APP_DIR/backend
command=$APP_DIR/backend/venv/bin/uvicorn server:app --host 0.0.0.0 --port 8001 --workers 2
user=$ACTUAL_USER
autostart=true
autorestart=true
stopasgroup=true
killasgroup=true
stderr_logfile=/var/log/rankforge/backend.err.log
stdout_logfile=/var/log/rankforge/backend.out.log
environment=PYTHONPATH="$APP_DIR/backend",MONGO_URL="mongodb://localhost:27017",DB_NAME="seo_platform",REDIS_URL="redis://localhost:6379/0"
EOF

# Workers
cat > /etc/supervisor/conf.d/rankforge-workers.conf << EOF
[program:rankforge-worker]
directory=$APP_DIR/backend
command=$APP_DIR/backend/venv/bin/rq worker high default low --url redis://localhost:6379/0 --name worker-%(process_num)s
process_name=%(program_name)s-%(process_num)s
numprocs=4
user=$ACTUAL_USER
autostart=true
autorestart=true
stopasgroup=true
killasgroup=true
stderr_logfile=/var/log/rankforge/worker-%(process_num)s.err.log
stdout_logfile=/var/log/rankforge/worker-%(process_num)s.out.log
environment=PYTHONPATH="$APP_DIR/backend",MONGO_URL="mongodb://localhost:27017",DB_NAME="seo_platform",REDIS_URL="redis://localhost:6379/0"
EOF

supervisorctl reread
supervisorctl update

echo -e "${GREEN}Step 9: Creating MongoDB Indexes${NC}"
sudo -u $ACTUAL_USER mongosh seo_platform << 'MONGO_EOF'
db.sites.createIndex({ "user_id": 1, "site_id": 1 })
db.audits.createIndex({ "site_id": 1, "created_at": -1 })
db.llm_visibility_checks.createIndex({ "site_id": 1, "created_at": -1 })
db.agents.createIndex({ "user_id": 1, "agent_id": 1 })
db.chat_sessions.createIndex({ "agent_id": 1, "timestamp": -1 })
db.users.createIndex({ "email": 1 }, { unique: true })
print("Indexes created successfully")
MONGO_EOF

echo -e "${GREEN}Step 10: Firewall Configuration${NC}"
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw --force enable

echo ""
echo -e "${GREEN}═══════════════════════════════════════════${NC}"
echo -e "${GREEN}✅ Deployment Complete!${NC}"
echo -e "${GREEN}═══════════════════════════════════════════${NC}"
echo ""
echo "📊 Service Status:"
supervisorctl status
echo ""
echo "🔧 Next Steps:"
echo "  1. Configure your domain DNS to point to this server"
echo "  2. Set up Nginx for your domain (see DEPLOYMENT_GUIDE.md)"
echo "  3. Install SSL certificates with Certbot"
echo "  4. Update .env files with production values"
echo "  5. Test the application"
echo ""
echo "📝 Useful Commands:"
echo "  - View logs: sudo tail -f /var/log/rankforge/*.log"
echo "  - Restart: sudo supervisorctl restart all"
echo "  - Status: sudo supervisorctl status"
echo ""
echo "📖 Full guide: $APP_DIR/DEPLOYMENT_GUIDE.md"
echo ""
