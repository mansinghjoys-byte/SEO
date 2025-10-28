#!/bin/bash

################################################################################
# RankForge SEO Platform - Production Deployment Script v2.0
# Author: Deployment Automation
# Description: Complete deployment with interactive Redis configuration
# Version: 2.0.0 - Enhanced error handling and Redis setup
################################################################################

# Don't exit on error - we'll handle errors manually
set +e

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

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

# Redis Configuration (set by user)
REDIS_HOST="localhost"
REDIS_PORT=""
USE_EXISTING_REDIS=""
REDIS_PASSWORD=""
INSTALL_NEW_REDIS=""

# Super Admin Credentials
SUPER_ADMIN_EMAIL="admin@rankforge.com"
SUPER_ADMIN_PASSWORD="RankForge@Admin2025!Secure"

# Log file
DEPLOY_LOG="/tmp/rankforge_deploy_$(date +%Y%m%d_%H%M%S).log"

################################################################################
# Helper Functions
################################################################################

log_to_file() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$DEPLOY_LOG"
}

print_step() {
    echo -e "${BLUE}==>${NC} $1"
    log_to_file "STEP: $1"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
    log_to_file "SUCCESS: $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
    log_to_file "ERROR: $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
    log_to_file "WARNING: $1"
}

print_info() {
    echo -e "${CYAN}ℹ${NC} $1"
    log_to_file "INFO: $1"
}

print_bold() {
    echo -e "${BOLD}$1${NC}"
}

check_command() {
    if ! command -v $1 &> /dev/null; then
        return 1
    fi
    return 0
}

check_port_in_use() {
    local port=$1
    if netstat -tuln 2>/dev/null | grep -q ":$port " || ss -tuln 2>/dev/null | grep -q ":$port "; then
        return 0
    else
        return 1
    fi
}

get_port_process() {
    local port=$1
    lsof -i :$port 2>/dev/null | grep LISTEN | awk '{print $1, $2}' | head -1
}

prompt_yes_no() {
    local prompt="$1"
    local default="${2:-n}"
    local response
    
    if [ "$default" = "y" ]; then
        prompt="$prompt [Y/n]: "
    else
        prompt="$prompt [y/N]: "
    fi
    
    read -p "$prompt" response
    response=${response:-$default}
    
    if [[ "$response" =~ ^[Yy]$ ]]; then
        return 0
    else
        return 1
    fi
}

prompt_input() {
    local prompt="$1"
    local default="$2"
    local response
    
    if [ -n "$default" ]; then
        read -p "$prompt [$default]: " response
        response=${response:-$default}
    else
        read -p "$prompt: " response
    fi
    
    echo "$response"
}

validate_port() {
    local port=$1
    if [[ "$port" =~ ^[0-9]+$ ]] && [ "$port" -ge 1 ] && [ "$port" -le 65535 ]; then
        return 0
    else
        return 1
    fi
}

rollback() {
    print_error "Deployment failed. Check logs at: $DEPLOY_LOG"
    systemctl stop rankforge-backend 2>/dev/null || true
    systemctl stop rankforge-worker 2>/dev/null || true
    exit 1
}

################################################################################
# Pre-flight Checks
################################################################################

print_bold "╔════════════════════════════════════════════════════════════════╗"
print_bold "║     RankForge SEO Platform - Production Deployment v2.0       ║"
print_bold "╚════════════════════════════════════════════════════════════════╝"
echo ""

print_info "Deployment log: $DEPLOY_LOG"
echo ""

print_step "Running pre-flight checks..."

# Check root
if [[ $EUID -ne 0 ]]; then
   print_error "This script must be run as root or with sudo"
   exit 1
fi

print_success "Running with root privileges"

# Check required commands
MISSING_COMMANDS=()

print_info "Checking required commands..."
for cmd in git node npm python3 nginx docker; do
    if check_command $cmd; then
        print_success "$cmd is installed"
    else
        MISSING_COMMANDS+=("$cmd")
        print_error "$cmd is NOT installed"
    fi
done

if [ ${#MISSING_COMMANDS[@]} -gt 0 ]; then
    print_error "Missing required commands: ${MISSING_COMMANDS[*]}"
    print_info "Install them before running this script"
    exit 1
fi

if ! command -v yarn &> /dev/null; then
    print_warning "yarn not found, will use npm instead"
fi

print_success "All required commands are available"
echo ""

################################################################################
# 1. Clone/Update Repository
################################################################################

print_step "Step 1: Fetching code from GitHub..."

if [ -d "$DEPLOY_DIR" ]; then
    print_warning "Directory $DEPLOY_DIR already exists"
    
    if prompt_yes_no "Pull latest changes from GitHub?" "y"; then
        cd "$DEPLOY_DIR"
        git fetch origin 2>&1 | tee -a "$DEPLOY_LOG"
        git checkout $BRANCH 2>&1 | tee -a "$DEPLOY_LOG"
        git pull origin $BRANCH 2>&1 | tee -a "$DEPLOY_LOG"
        
        if [ $? -eq 0 ]; then
            print_success "Repository updated"
        else
            print_error "Failed to update repository"
            exit 1
        fi
    else
        print_info "Using existing code"
    fi
else
    print_step "Cloning repository..."
    mkdir -p $(dirname "$DEPLOY_DIR")
    git clone -b $BRANCH $REPO_URL $DEPLOY_DIR 2>&1 | tee -a "$DEPLOY_LOG"
    
    if [ $? -eq 0 ] && [ -d "$DEPLOY_DIR" ]; then
        cd "$DEPLOY_DIR"
        print_success "Repository cloned"
    else
        print_error "Failed to clone repository"
        exit 1
    fi
fi

echo ""

################################################################################
# 2. Redis Configuration (Interactive)
################################################################################

print_bold "╔════════════════════════════════════════════════════════════════╗"
print_bold "║                    Redis Configuration                         ║"
print_bold "╚════════════════════════════════════════════════════════════════╝"
echo ""

print_info "RankForge requires Redis for background job processing"
echo ""

# Check if Redis is installed
REDIS_INSTALLED=false
if command -v redis-server &> /dev/null || command -v redis-cli &> /dev/null; then
    REDIS_INSTALLED=true
    print_success "Redis is already installed"
else
    print_warning "Redis is not installed"
fi

# Check for running Redis instances
print_step "Checking for running Redis instances..."
RUNNING_REDIS_PORTS=()

for port in 6379 6380 6381 6382; do
    if check_port_in_use $port; then
        if timeout 2 redis-cli -p $port ping &>/dev/null; then
            RUNNING_REDIS_PORTS+=($port)
            print_info "Redis detected on port $port"
        fi
    fi
done

# Interactive Redis setup
echo ""
print_bold "Redis Setup Options:"
echo ""

if [ ${#RUNNING_REDIS_PORTS[@]} -gt 0 ]; then
    echo "Detected running Redis on port(s): ${RUNNING_REDIS_PORTS[*]}"
    echo ""
    echo "  1) Use existing Redis instance"
    echo "  2) Install new Redis instance on different port"
    echo "  3) Configure custom Redis connection"
    echo ""
    
    REDIS_CHOICE=$(prompt_input "Select option (1-3)" "1")
else
    echo "No running Redis instances detected."
    echo ""
    echo "  1) Install new Redis instance (recommended)"
    echo "  2) Configure custom Redis connection"
    echo ""
    
    REDIS_CHOICE=$(prompt_input "Select option (1-2)" "1")
    
    # Adjust for consistency
    if [ "$REDIS_CHOICE" = "2" ]; then
        REDIS_CHOICE="3"
    else
        REDIS_CHOICE="2"
    fi
fi

echo ""

case $REDIS_CHOICE in
    1)
        # Use existing Redis
        if [ ${#RUNNING_REDIS_PORTS[@]} -eq 1 ]; then
            REDIS_PORT=${RUNNING_REDIS_PORTS[0]}
            print_info "Using Redis on port $REDIS_PORT"
        else
            REDIS_PORT=$(prompt_input "Enter Redis port" "${RUNNING_REDIS_PORTS[0]}")
            
            if ! validate_port "$REDIS_PORT"; then
                print_error "Invalid port"
                exit 1
            fi
        fi
        
        USE_EXISTING_REDIS="yes"
        REDIS_HOST="localhost"
        
        # Test connection
        if timeout 2 redis-cli -h $REDIS_HOST -p $REDIS_PORT ping &>/dev/null; then
            print_success "Connected to Redis on $REDIS_HOST:$REDIS_PORT"
        else
            print_error "Cannot connect to Redis"
            exit 1
        fi
        ;;
        
    2)
        # Install new Redis
        print_step "Installing new Redis instance..."
        
        REDIS_PORT=$(prompt_input "Enter port for Redis" "6379")
        
        if ! validate_port "$REDIS_PORT"; then
            print_error "Invalid port"
            exit 1
        fi
        
        # Check port availability
        if check_port_in_use $REDIS_PORT; then
            PROCESS_INFO=$(get_port_process $REDIS_PORT)
            print_error "Port $REDIS_PORT in use by: $PROCESS_INFO"
            
            if prompt_yes_no "Try another port?" "y"; then
                REDIS_PORT=$(prompt_input "Enter alternative port" "6380")
                
                if ! validate_port "$REDIS_PORT" || check_port_in_use $REDIS_PORT; then
                    print_error "Port unavailable"
                    exit 1
                fi
            else
                exit 1
            fi
        fi
        
        print_success "Port $REDIS_PORT is available"
        
        # Password
        if prompt_yes_no "Enable Redis password?" "n"; then
            REDIS_PASSWORD=$(prompt_input "Enter password" "")
        fi
        
        # Install Redis
        if [ "$REDIS_INSTALLED" = false ]; then
            print_step "Installing Redis..."
            apt-get update > /dev/null 2>&1
            apt-get install -y redis-server redis-tools > /dev/null 2>&1
            
            if [ $? -eq 0 ]; then
                print_success "Redis installed"
                REDIS_INSTALLED=true
            else
                print_error "Failed to install Redis"
                exit 1
            fi
        fi
        
        INSTALL_NEW_REDIS="yes"
        USE_EXISTING_REDIS="no"
        REDIS_HOST="localhost"
        ;;
        
    3)
        # Custom connection
        print_info "Configure custom Redis connection"
        
        REDIS_HOST=$(prompt_input "Enter Redis host" "localhost")
        REDIS_PORT=$(prompt_input "Enter Redis port" "6379")
        
        if ! validate_port "$REDIS_PORT"; then
            print_error "Invalid port"
            exit 1
        fi
        
        if prompt_yes_no "Requires password?" "n"; then
            REDIS_PASSWORD=$(prompt_input "Enter password" "")
        fi
        
        # Test connection
        print_step "Testing connection..."
        if [ -n "$REDIS_PASSWORD" ]; then
            TEST_CMD="redis-cli -h $REDIS_HOST -p $REDIS_PORT -a $REDIS_PASSWORD ping"
        else
            TEST_CMD="redis-cli -h $REDIS_HOST -p $REDIS_PORT ping"
        fi
        
        if timeout 5 $TEST_CMD &>/dev/null; then
            print_success "Connected to Redis"
        else
            print_error "Cannot connect to $REDIS_HOST:$REDIS_PORT"
            exit 1
        fi
        
        USE_EXISTING_REDIS="yes"
        ;;
        
    *)
        print_error "Invalid option"
        exit 1
        ;;
esac

# Display configuration
echo ""
print_bold "Redis Configuration:"
echo "  Host: $REDIS_HOST"
echo "  Port: $REDIS_PORT"
if [ -n "$REDIS_PASSWORD" ]; then
    echo "  Password: ******* (protected)"
else
    echo "  Password: (none)"
fi
echo ""

if ! prompt_yes_no "Proceed with this configuration?" "y"; then
    print_warning "Deployment cancelled"
    exit 0
fi

echo ""

################################################################################
# 2b. Configure New Redis Instance
################################################################################

if [ "$INSTALL_NEW_REDIS" = "yes" ]; then
    print_step "Configuring Redis instance..."
    
    REDIS_CONF="/etc/redis/redis_${REDIS_PORT}.conf"
    
    # Stop conflicting services
    systemctl stop redis-server 2>/dev/null || true
    systemctl stop redis 2>/dev/null || true
    
    # Create directories
    mkdir -p /etc/redis
    mkdir -p /var/lib/redis_${REDIS_PORT}
    mkdir -p /var/log/redis
    mkdir -p /var/run/redis
    
    # Create config
    cat > $REDIS_CONF << EOF
bind 127.0.0.1 ::1
port ${REDIS_PORT}
daemonize no
supervised systemd
pidfile /var/run/redis/redis_${REDIS_PORT}.pid
logfile /var/log/redis/redis_${REDIS_PORT}.log
dir /var/lib/redis_${REDIS_PORT}
save ""
maxmemory 512mb
maxmemory-policy allkeys-lru
EOF

    if [ -n "$REDIS_PASSWORD" ]; then
        echo "requirepass $REDIS_PASSWORD" >> $REDIS_CONF
    fi
    
    print_success "Config created at $REDIS_CONF"
    
    # Create systemd service
    cat > /etc/systemd/system/redis_${REDIS_PORT}.service << EOF
[Unit]
Description=Redis (Port ${REDIS_PORT})
After=network.target

[Service]
Type=notify
User=redis
Group=redis
ExecStart=/usr/bin/redis-server /etc/redis/redis_${REDIS_PORT}.conf
Restart=always

[Install]
WantedBy=multi-user.target
EOF

    # Create redis user
    if ! id redis &>/dev/null; then
        useradd -r -s /bin/false redis
    fi
    
    # Set permissions
    chown -R redis:redis /var/lib/redis_${REDIS_PORT}
    chown -R redis:redis /var/log/redis
    chown redis:redis /var/run/redis
    
    # Start Redis
    systemctl daemon-reload
    systemctl enable redis_${REDIS_PORT}
    systemctl start redis_${REDIS_PORT}
    
    sleep 3
    
    # Verify
    if systemctl is-active --quiet redis_${REDIS_PORT}; then
        print_success "Redis service started"
        
        TEST_PING=false
        if [ -n "$REDIS_PASSWORD" ]; then
            timeout 2 redis-cli -p $REDIS_PORT -a $REDIS_PASSWORD ping &>/dev/null && TEST_PING=true
        else
            timeout 2 redis-cli -p $REDIS_PORT ping &>/dev/null && TEST_PING=true
        fi
        
        if [ "$TEST_PING" = true ]; then
            print_success "Redis responding to PING"
        else
            print_error "Redis not responding"
            systemctl status redis_${REDIS_PORT}
            exit 1
        fi
    else
        print_error "Failed to start Redis"
        systemctl status redis_${REDIS_PORT}
        exit 1
    fi
fi

echo ""

################################################################################
# 3. Check MongoDB
################################################################################

print_step "Step 3: Checking MongoDB..."

if docker ps | grep -q rankforgedb; then
    print_success "MongoDB container (rankforgedb) is running"
else
    print_error "MongoDB container (rankforgedb) is NOT running"
    print_info "Start it with: docker start rankforgedb"
    
    if prompt_yes_no "Try to start MongoDB container now?" "y"; then
        docker start rankforgedb
        sleep 3
        
        if docker ps | grep -q rankforgedb; then
            print_success "MongoDB container started"
        else
            print_error "Failed to start MongoDB"
            exit 1
        fi
    else
        exit 1
    fi
fi

# Test MongoDB connection
print_step "Testing MongoDB connection..."
docker exec rankforgedb mongosh --port $MONGO_PORT --eval "db.adminCommand('ping')" &>/dev/null

if [ $? -eq 0 ]; then
    print_success "MongoDB connection successful"
else
    print_error "Cannot connect to MongoDB on port $MONGO_PORT"
    exit 1
fi

echo ""

################################################################################
# 4. Setup Backend
################################################################################

print_step "Step 4: Setting up Backend..."

cd "$BACKEND_DIR"

# Build Redis URL
if [ -n "$REDIS_PASSWORD" ]; then
    REDIS_URL="redis://:${REDIS_PASSWORD}@${REDIS_HOST}:${REDIS_PORT}/0"
else
    REDIS_URL="redis://${REDIS_HOST}:${REDIS_PORT}/0"
fi

# Create .env
print_step "Configuring backend..."
cat > .env << EOF
MONGO_URL="mongodb://${MONGO_HOST}:${MONGO_PORT}"
DB_NAME="${DB_NAME}"
BACKEND_PORT=${BACKEND_PORT}
CORS_ORIGINS="http://${FRONTEND_DOMAIN},https://${FRONTEND_DOMAIN}"
REDIS_URL="${REDIS_URL}"
JWT_SECRET="$(openssl rand -hex 32)"
SUPER_ADMIN_EMAIL="${SUPER_ADMIN_EMAIL}"
SUPER_ADMIN_PASSWORD="${SUPER_ADMIN_PASSWORD}"
GROQ_API_KEY="${GROQ_API_KEY:-}"
EMERGENT_LLM_KEY="${EMERGENT_LLM_KEY:-}"
PAYPAL_CLIENT_ID="${PAYPAL_CLIENT_ID:-}"
PAYPAL_CLIENT_SECRET="${PAYPAL_CLIENT_SECRET:-}"
PAYPAL_MODE="live"
APP_URL="http://${FRONTEND_DOMAIN}"
EOF

print_success "Backend .env created"

# Python virtual environment
if [ ! -d "venv" ]; then
    print_step "Creating Python virtual environment..."
    python3 -m venv venv
    print_success "Virtual environment created"
fi

# Install dependencies
print_step "Installing backend dependencies (this may take a while)..."
source venv/bin/activate
pip install --upgrade pip > /dev/null 2>&1
pip install -r requirements.txt 2>&1 | tee -a "$DEPLOY_LOG"

if [ ${PIPESTATUS[0]} -eq 0 ]; then
    print_success "Dependencies installed"
else
    print_error "Failed to install dependencies"
    print_info "Check log: $DEPLOY_LOG"
    exit 1
fi

echo ""

################################################################################
# 5. Create Super Admin
################################################################################

print_step "Step 5: Creating Super Admin..."

cat > /tmp/create_admin.py << 'EOFPYTHON'
import asyncio
import sys
import os
from motor.motor_asyncio import AsyncIOMotorClient
from passlib.context import CryptContext
from datetime import datetime, timezone
import uuid

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def create_admin():
    mongo_url = os.getenv('MONGO_URL')
    db_name = os.getenv('DB_NAME')
    admin_email = os.getenv('SUPER_ADMIN_EMAIL')
    admin_password = os.getenv('SUPER_ADMIN_PASSWORD')
    
    try:
        client = AsyncIOMotorClient(mongo_url)
        db = client[db_name]
        
        existing = await db.users.find_one({'email': admin_email})
        
        if existing:
            print(f"Super Admin already exists: {admin_email}")
            return
        
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
        print(f"Super Admin created: {admin_email}")
        
        client.close()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    asyncio.run(create_admin())
EOFPYTHON

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

echo ""

################################################################################
# 6. Setup Services
################################################################################

print_step "Step 6: Setting up systemd services..."

# RQ Worker service
cat > /etc/systemd/system/rankforge-worker.service << EOF
[Unit]
Description=RankForge RQ Worker
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=$BACKEND_DIR
Environment="PYTHONPATH=$BACKEND_DIR"
ExecStart=$BACKEND_DIR/venv/bin/python workers/worker.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Backend service
cat > /etc/systemd/system/rankforge-backend.service << EOF
[Unit]
Description=RankForge Backend API
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=$BACKEND_DIR
ExecStart=$BACKEND_DIR/venv/bin/uvicorn server:app --host 127.0.0.1 --port ${BACKEND_PORT} --workers 2
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable rankforge-worker
systemctl enable rankforge-backend
systemctl restart rankforge-worker
systemctl restart rankforge-backend

sleep 3

# Verify services
BACKEND_OK=false
WORKER_OK=false

if systemctl is-active --quiet rankforge-backend; then
    print_success "Backend started"
    BACKEND_OK=true
else
    print_error "Backend failed to start"
    systemctl status rankforge-backend
fi

if systemctl is-active --quiet rankforge-worker; then
    print_success "Worker started"
    WORKER_OK=true
else
    print_error "Worker failed to start"
    systemctl status rankforge-worker
fi

if [ "$BACKEND_OK" = false ] || [ "$WORKER_OK" = false ]; then
    print_error "Some services failed to start"
    exit 1
fi

echo ""

################################################################################
# 7. Build Frontend
################################################################################

print_step "Step 7: Building Frontend..."

cd "$DEPLOY_DIR/frontend"

# Create .env
cat > .env << EOF
REACT_APP_BACKEND_URL=http://${FRONTEND_DOMAIN}/api
REACT_APP_APP_NAME=RankForge SEO Platform
EOF

print_success "Frontend .env created"

# Install and build
print_step "Installing frontend dependencies..."

if command -v yarn &> /dev/null; then
    yarn install 2>&1 | tee -a "$DEPLOY_LOG"
    if [ ${PIPESTATUS[0]} -eq 0 ]; then
        print_success "Dependencies installed"
        print_step "Building production bundle..."
        yarn build 2>&1 | tee -a "$DEPLOY_LOG"
    else
        print_error "Yarn install failed"
        exit 1
    fi
else
    npm install 2>&1 | tee -a "$DEPLOY_LOG"
    if [ ${PIPESTATUS[0]} -eq 0 ]; then
        print_success "Dependencies installed"
        print_step "Building production bundle..."
        npm run build 2>&1 | tee -a "$DEPLOY_LOG"
    else
        print_error "npm install failed"
        exit 1
    fi
fi

if [ -d "build" ]; then
    print_success "Frontend build completed"
else
    print_error "Frontend build failed"
    exit 1
fi

echo ""

################################################################################
# 8. Configure Nginx
################################################################################

print_step "Step 8: Configuring Nginx..."

cat > /etc/nginx/sites-available/rankforge << EOF
upstream rankforge_backend {
    server 127.0.0.1:${BACKEND_PORT};
    keepalive 32;
}

server {
    listen 80;
    server_name ${FRONTEND_DOMAIN};
    
    access_log /var/log/nginx/rankforge_access.log;
    error_log /var/log/nginx/rankforge_error.log;
    
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    
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
    
    location / {
        root $FRONTEND_BUILD_DIR;
        index index.html;
        try_files \$uri \$uri/ /index.html;
        
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }
    
    location ~ /\. {
        deny all;
    }
}
EOF

ln -sf /etc/nginx/sites-available/rankforge /etc/nginx/sites-enabled/

nginx -t

if [ $? -eq 0 ]; then
    print_success "Nginx config valid"
    systemctl reload nginx
    print_success "Nginx reloaded"
else
    print_error "Nginx config test failed"
    exit 1
fi

echo ""

################################################################################
# Final Summary
################################################################################

print_bold "╔════════════════════════════════════════════════════════════════╗"
print_bold "║            DEPLOYMENT COMPLETED SUCCESSFULLY                   ║"
print_bold "╚════════════════════════════════════════════════════════════════╝"
echo ""

print_bold "SERVICES STATUS:"
systemctl is-active --quiet rankforge-backend && echo -e "${GREEN}✓${NC} Backend: RUNNING" || echo -e "${RED}✗${NC} Backend: STOPPED"
systemctl is-active --quiet rankforge-worker && echo -e "${GREEN}✓${NC} Worker: RUNNING" || echo -e "${RED}✗${NC} Worker: STOPPED"
systemctl is-active --quiet nginx && echo -e "${GREEN}✓${NC} Nginx: RUNNING" || echo -e "${RED}✗${NC} Nginx: STOPPED"

if [ "$INSTALL_NEW_REDIS" = "yes" ]; then
    systemctl is-active --quiet redis_${REDIS_PORT} && echo -e "${GREEN}✓${NC} Redis: RUNNING (port $REDIS_PORT)" || echo -e "${RED}✗${NC} Redis: STOPPED"
else
    echo -e "${GREEN}✓${NC} Redis: Using existing (port $REDIS_PORT)"
fi

docker ps | grep -q rankforgedb && echo -e "${GREEN}✓${NC} MongoDB: RUNNING" || echo -e "${RED}✗${NC} MongoDB: STOPPED"

echo ""
print_bold "DEPLOYMENT INFO:"
echo "  Directory: $DEPLOY_DIR"
echo "  Frontend: http://${FRONTEND_DOMAIN}"
echo "  Backend: localhost:${BACKEND_PORT} (internal)"
echo "  MongoDB: ${MONGO_HOST}:${MONGO_PORT}"
echo "  Redis: ${REDIS_HOST}:${REDIS_PORT}"
echo "  Log: $DEPLOY_LOG"
echo ""

print_bold "SUPER ADMIN CREDENTIALS:"
echo ""
print_warning "⚠ SAVE THESE CREDENTIALS SECURELY!"
echo ""
echo -e "  Email:    ${GREEN}${SUPER_ADMIN_EMAIL}${NC}"
echo -e "  Password: ${GREEN}${SUPER_ADMIN_PASSWORD}${NC}"
echo ""
echo "  Admin URL: http://${FRONTEND_DOMAIN}/admin/login"
echo ""

print_bold "USEFUL COMMANDS:"
echo "  Backend logs:  sudo journalctl -u rankforge-backend -f"
echo "  Worker logs:   sudo journalctl -u rankforge-worker -f"
echo "  Restart:       sudo systemctl restart rankforge-backend"
echo ""

print_success "🚀 RankForge SEO Platform is now live!"
echo ""
