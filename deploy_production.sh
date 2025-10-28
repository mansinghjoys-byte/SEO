#!/bin/bash

################################################################################
# RankForge SEO Platform - Production Deployment Script
# Author: Deployment Automation
# Description: Complete deployment from GitHub to production
# Version: 2.0.0 - Enhanced with Redis configuration and error handling
################################################################################

# Don't exit on error - we'll handle errors manually for better control
set +e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# Configuration
REPO_URL="https://github.com/mansinghjoys-byte/SEO"
BRANCH="AEo4"
DEPLOY_DIR="/var/www/rankforge"
FRONTEND_BUILD_DIR="$DEPLOY_DIR/frontend/build"
BACKEND_DIR="$DEPLOY_DIR/backend"
FRONTEND_DOMAIN="seo.mj.publicvm.com"
BACKEND_PORT="8000"
MONGO_HOST="localhost"
MONGO_PORT="27018"
DB_NAME="seo_platform"

# Redis Configuration (will be set by user input)
REDIS_HOST="localhost"
REDIS_PORT=""
USE_EXISTING_REDIS=""
REDIS_PASSWORD=""
INSTALL_NEW_REDIS=""

# Super Admin Credentials
SUPER_ADMIN_EMAIL="admin@rankforge.com"
SUPER_ADMIN_PASSWORD="RankForge@Admin2025!Secure"

# Log file for this deployment
DEPLOY_LOG="/tmp/rankforge_deploy_$(date +%Y%m%d_%H%M%S).log"

################################################################################
# Helper Functions
################################################################################

print_step() {
    echo -e "${BLUE}==>${NC} $1"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

check_command() {
    if ! command -v $1 &> /dev/null; then
        print_error "$1 is not installed. Please install it first."
        exit 1
    fi
}

################################################################################
# Pre-flight Checks
################################################################################

print_step "Running pre-flight checks..."

# Check if running as root or with sudo
if [[ $EUID -ne 0 ]]; then
   print_error "This script must be run as root or with sudo"
   exit 1
fi

# Check required commands
check_command git
check_command node
check_command npm
check_command python3
check_command redis-server
check_command nginx
check_command docker

print_success "All required commands are available"

################################################################################
# 1. Clone/Update Repository
################################################################################

print_step "Step 1: Fetching code from GitHub..."

if [ -d "$DEPLOY_DIR" ]; then
    print_warning "Directory $DEPLOY_DIR already exists. Pulling latest changes..."
    cd "$DEPLOY_DIR"
    git fetch origin
    git checkout $BRANCH
    git pull origin $BRANCH
    print_success "Repository updated"
else
    print_step "Cloning repository..."
    mkdir -p $(dirname "$DEPLOY_DIR")
    git clone -b $BRANCH $REPO_URL $DEPLOY_DIR
    cd "$DEPLOY_DIR"
    print_success "Repository cloned"
fi

################################################################################
# 2. Check and Start Redis
################################################################################

print_step "Step 2: Checking Redis..."

if systemctl is-active --quiet redis-server; then
    print_success "Redis is already running"
elif systemctl is-active --quiet redis; then
    print_success "Redis is already running"
else
    print_step "Starting Redis..."
    systemctl start redis-server || systemctl start redis
    sleep 2
    
    if systemctl is-active --quiet redis-server || systemctl is-active --quiet redis; then
        print_success "Redis started successfully"
    else
        print_error "Failed to start Redis"
        exit 1
    fi
fi

# Enable Redis on boot
systemctl enable redis-server 2>/dev/null || systemctl enable redis 2>/dev/null

# Test Redis connection
if redis-cli ping > /dev/null 2>&1; then
    print_success "Redis is responding to PING"
else
    print_error "Redis is not responding"
    exit 1
fi

################################################################################
# 3. Setup Backend
################################################################################

print_step "Step 3: Setting up Backend..."

cd "$BACKEND_DIR"

# Create/Update .env file
print_step "Configuring backend environment..."
cat > .env << EOF
# Database Configuration
MONGO_URL="mongodb://${MONGO_HOST}:${MONGO_PORT}"
DB_NAME="${DB_NAME}"

# Server Configuration
BACKEND_PORT=${BACKEND_PORT}
CORS_ORIGINS="http://${FRONTEND_DOMAIN},https://${FRONTEND_DOMAIN}"

# Redis Configuration
REDIS_URL="redis://localhost:6379/0"

# JWT Configuration
JWT_SECRET="$(openssl rand -hex 32)"

# Super Admin Credentials
SUPER_ADMIN_EMAIL="${SUPER_ADMIN_EMAIL}"
SUPER_ADMIN_PASSWORD="${SUPER_ADMIN_PASSWORD}"

# API Keys (update these with real keys if needed)
GROQ_API_KEY="${GROQ_API_KEY:-}"
EMERGENT_LLM_KEY="${EMERGENT_LLM_KEY:-}"

# PayPal Configuration (update for production)
PAYPAL_CLIENT_ID="${PAYPAL_CLIENT_ID:-}"
PAYPAL_CLIENT_SECRET="${PAYPAL_CLIENT_SECRET:-}"
PAYPAL_MODE="live"

# Application URL
APP_URL="http://${FRONTEND_DOMAIN}"
EOF

print_success "Backend .env file created"

# Create Python virtual environment
if [ ! -d "venv" ]; then
    print_step "Creating Python virtual environment..."
    python3 -m venv venv
    print_success "Virtual environment created"
fi

# Activate virtual environment and install dependencies
print_step "Installing backend dependencies..."
source venv/bin/activate
pip install --upgrade pip > /dev/null 2>&1
pip install -r requirements.txt
print_success "Backend dependencies installed"

# Test MongoDB connection
print_step "Testing MongoDB connection..."
python3 << EOF
import pymongo
try:
    client = pymongo.MongoClient("mongodb://${MONGO_HOST}:${MONGO_PORT}", serverSelectionTimeoutMS=5000)
    client.server_info()
    print("MongoDB connection successful")
except Exception as e:
    print(f"MongoDB connection failed: {e}")
    exit(1)
EOF

if [ $? -eq 0 ]; then
    print_success "MongoDB connection verified"
else
    print_error "Cannot connect to MongoDB on ${MONGO_HOST}:${MONGO_PORT}"
    print_error "Please ensure Docker container 'rankforgedb' is running"
    exit 1
fi

################################################################################
# 4. Create Super Admin User
################################################################################

print_step "Step 4: Creating Super Admin user..."

cat > /tmp/create_admin.py << 'EOF'
import asyncio
import sys
import os
from motor.motor_asyncio import AsyncIOMotorClient
from passlib.context import CryptContext
from datetime import datetime, timezone
import uuid

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def create_admin():
    mongo_url = os.getenv('MONGO_URL', 'mongodb://localhost:27018')
    db_name = os.getenv('DB_NAME', 'seo_platform')
    admin_email = os.getenv('SUPER_ADMIN_EMAIL', 'admin@rankforge.com')
    admin_password = os.getenv('SUPER_ADMIN_PASSWORD', 'RankForge@Admin2025!Secure')
    
    try:
        client = AsyncIOMotorClient(mongo_url)
        db = client[db_name]
        
        # Check if admin already exists
        existing_admin = await db.users.find_one({'email': admin_email})
        
        if existing_admin:
            print(f"Super Admin already exists: {admin_email}")
            return
        
        # Create admin user
        hashed_password = pwd_context.hash(admin_password)
        admin_doc = {
            'user_id': str(uuid.uuid4()),
            'email': admin_email,
            'password': hashed_password,
            'full_name': 'Super Administrator',
            'is_admin': True,
            'credits': 999999,
            'plan': 'enterprise',
            'created_at': datetime.now(timezone.utc).isoformat()
        }
        
        await db.users.insert_one(admin_doc)
        print(f"Super Admin created successfully: {admin_email}")
        
        client.close()
    except Exception as e:
        print(f"Error creating admin: {e}")
        sys.exit(1)

if __name__ == '__main__':
    asyncio.run(create_admin())
EOF

# Run admin creation script
cd "$BACKEND_DIR"
source venv/bin/activate
export MONGO_URL="mongodb://${MONGO_HOST}:${MONGO_PORT}"
export DB_NAME="${DB_NAME}"
export SUPER_ADMIN_EMAIL="${SUPER_ADMIN_EMAIL}"
export SUPER_ADMIN_PASSWORD="${SUPER_ADMIN_PASSWORD}"

python3 /tmp/create_admin.py

if [ $? -eq 0 ]; then
    print_success "Super Admin setup complete"
else
    print_error "Failed to create Super Admin"
    exit 1
fi

rm /tmp/create_admin.py

################################################################################
# 5. Setup RQ Workers
################################################################################

print_step "Step 5: Setting up RQ Workers..."

# Create systemd service for RQ worker
cat > /etc/systemd/system/rankforge-worker.service << EOF
[Unit]
Description=RankForge RQ Worker
After=network.target redis.service

[Service]
Type=simple
User=root
WorkingDirectory=$BACKEND_DIR
Environment="PYTHONPATH=$BACKEND_DIR"
Environment="MONGO_URL=mongodb://${MONGO_HOST}:${MONGO_PORT}"
Environment="DB_NAME=${DB_NAME}"
Environment="REDIS_URL=redis://localhost:6379/0"
ExecStart=$BACKEND_DIR/venv/bin/python workers/worker.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd and enable worker
systemctl daemon-reload
systemctl enable rankforge-worker
systemctl restart rankforge-worker

sleep 2

if systemctl is-active --quiet rankforge-worker; then
    print_success "RQ Worker started successfully"
else
    print_error "Failed to start RQ Worker"
    systemctl status rankforge-worker
    exit 1
fi

################################################################################
# 6. Setup Backend Service
################################################################################

print_step "Step 6: Setting up Backend service..."

# Create systemd service for backend
cat > /etc/systemd/system/rankforge-backend.service << EOF
[Unit]
Description=RankForge Backend API
After=network.target mongodb.service redis.service

[Service]
Type=simple
User=root
WorkingDirectory=$BACKEND_DIR
Environment="PYTHONPATH=$BACKEND_DIR"
ExecStart=$BACKEND_DIR/venv/bin/uvicorn server:app --host 127.0.0.1 --port ${BACKEND_PORT} --workers 2
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd and enable backend
systemctl daemon-reload
systemctl enable rankforge-backend
systemctl restart rankforge-backend

sleep 3

if systemctl is-active --quiet rankforge-backend; then
    print_success "Backend started successfully on localhost:${BACKEND_PORT}"
else
    print_error "Failed to start Backend"
    systemctl status rankforge-backend
    exit 1
fi

# Test backend health
if curl -f http://localhost:${BACKEND_PORT}/api/health > /dev/null 2>&1; then
    print_success "Backend health check passed"
else
    print_warning "Backend health check failed (may still be starting up)"
fi

################################################################################
# 7. Build Frontend
################################################################################

print_step "Step 7: Building Frontend for production..."

cd "$DEPLOY_DIR/frontend"

# Create/Update frontend .env
cat > .env << EOF
REACT_APP_BACKEND_URL=http://${FRONTEND_DOMAIN}/api
REACT_APP_APP_NAME=RankForge SEO Platform
EOF

print_success "Frontend .env file created"

# Install dependencies
print_step "Installing frontend dependencies..."
if command -v yarn &> /dev/null; then
    yarn install
else
    npm install
fi
print_success "Frontend dependencies installed"

# Build for production
print_step "Creating production build..."
if command -v yarn &> /dev/null; then
    yarn build
else
    npm run build
fi

if [ -d "build" ]; then
    print_success "Frontend build completed"
else
    print_error "Frontend build failed"
    exit 1
fi

################################################################################
# 8. Configure Nginx
################################################################################

print_step "Step 8: Configuring Nginx..."

# Create Nginx configuration
cat > /etc/nginx/sites-available/rankforge << EOF
# RankForge SEO Platform - Nginx Configuration

# Backend API proxy (not exposed directly)
upstream rankforge_backend {
    server 127.0.0.1:${BACKEND_PORT};
    keepalive 32;
}

# Main server block
server {
    listen 80;
    server_name ${FRONTEND_DOMAIN};
    
    # Logging
    access_log /var/log/nginx/rankforge_access.log;
    error_log /var/log/nginx/rankforge_error.log;
    
    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    
    # API proxy to backend (localhost only, not exposed)
    location /api {
        proxy_pass http://rankforge_backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_cache_bypass \$http_upgrade;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    # Frontend static files
    location / {
        root $FRONTEND_BUILD_DIR;
        index index.html;
        try_files \$uri \$uri/ /index.html;
        
        # Cache static assets
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }
    
    # Deny access to hidden files
    location ~ /\. {
        deny all;
        access_log off;
        log_not_found off;
    }
}
EOF

# Enable site and test configuration
ln -sf /etc/nginx/sites-available/rankforge /etc/nginx/sites-enabled/

# Test Nginx configuration
nginx -t

if [ $? -eq 0 ]; then
    print_success "Nginx configuration is valid"
    systemctl reload nginx
    print_success "Nginx reloaded"
else
    print_error "Nginx configuration test failed"
    exit 1
fi

################################################################################
# 9. Final Checks and Summary
################################################################################

print_step "Step 9: Running final checks..."

# Check all services
echo ""
echo "==================================="
echo "SERVICE STATUS"
echo "==================================="

check_service() {
    if systemctl is-active --quiet $1; then
        echo -e "${GREEN}✓${NC} $1: RUNNING"
    else
        echo -e "${RED}✗${NC} $1: STOPPED"
    fi
}

check_service nginx
check_service rankforge-backend
check_service rankforge-worker
check_service redis-server || check_service redis

# Check Docker MongoDB
echo ""
if docker ps | grep -q rankforgedb; then
    print_success "MongoDB container (rankforgedb) is running"
else
    print_error "MongoDB container (rankforgedb) is not running"
fi

################################################################################
# Deployment Summary
################################################################################

echo ""
echo "==================================="
echo "DEPLOYMENT SUMMARY"
echo "==================================="
echo ""
echo -e "${GREEN}✓ Deployment completed successfully!${NC}"
echo ""
echo "📁 Deployment Directory: $DEPLOY_DIR"
echo "🌐 Frontend URL: http://${FRONTEND_DOMAIN}"
echo "🔧 Backend: localhost:${BACKEND_PORT} (not exposed to public)"
echo "💾 MongoDB: ${MONGO_HOST}:${MONGO_PORT}"
echo "🔴 Redis: localhost:6379"
echo ""
echo "==================================="
echo "SUPER ADMIN CREDENTIALS"
echo "==================================="
echo ""
echo -e "${YELLOW}⚠ IMPORTANT: Save these credentials securely!${NC}"
echo ""
echo -e "Email:    ${GREEN}${SUPER_ADMIN_EMAIL}${NC}"
echo -e "Password: ${GREEN}${SUPER_ADMIN_PASSWORD}${NC}"
echo ""
echo "Admin Login URL: http://${FRONTEND_DOMAIN}/admin/login"
echo ""
echo "==================================="
echo "USEFUL COMMANDS"
echo "==================================="
echo ""
echo "View backend logs:  sudo journalctl -u rankforge-backend -f"
echo "View worker logs:   sudo journalctl -u rankforge-worker -f"
echo "View nginx logs:    sudo tail -f /var/log/nginx/rankforge_*.log"
echo ""
echo "Restart backend:    sudo systemctl restart rankforge-backend"
echo "Restart worker:     sudo systemctl restart rankforge-worker"
echo "Restart nginx:      sudo systemctl restart nginx"
echo ""
echo "Check status:       sudo systemctl status rankforge-backend"
echo "                    sudo systemctl status rankforge-worker"
echo ""
echo "==================================="
echo ""
print_success "🚀 RankForge SEO Platform is now live!"
echo ""
