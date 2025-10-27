#!/bin/bash

################################################################################
# Service Health Check Script
# Checks all RankForge services and reports status
################################################################################

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo ""
echo "==================================="
echo "RANKFORGE SERVICE HEALTH CHECK"
echo "==================================="
echo ""

# Function to check service
check_service() {
    local service=$1
    local display_name=$2
    
    if systemctl is-active --quiet $service; then
        echo -e "${GREEN}✓${NC} $display_name: RUNNING"
        return 0
    else
        echo -e "${RED}✗${NC} $display_name: STOPPED"
        return 1
    fi
}

# Function to check HTTP endpoint
check_endpoint() {
    local url=$1
    local name=$2
    
    if curl -f -s $url > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} $name: RESPONDING"
        return 0
    else
        echo -e "${RED}✗${NC} $name: NOT RESPONDING"
        return 1
    fi
}

# Check system services
echo "System Services:"
echo "-----------------------------------"
check_service "nginx" "Nginx Web Server"
check_service "rankforge-backend" "Backend API"
check_service "rankforge-worker" "RQ Worker"
check_service "redis-server" "Redis" || check_service "redis" "Redis"

echo ""
echo "Docker Containers:"
echo "-----------------------------------"
if docker ps | grep -q rankforgedb; then
    echo -e "${GREEN}✓${NC} MongoDB Container: RUNNING"
else
    echo -e "${RED}✗${NC} MongoDB Container: STOPPED"
fi

echo ""
echo "HTTP Endpoints:"
echo "-----------------------------------"
check_endpoint "http://localhost:8000/api/health" "Backend Health Check"
check_endpoint "http://seo.mj.publicvm.com" "Frontend"

echo ""
echo "Redis Connection:"
echo "-----------------------------------"
if redis-cli ping > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} Redis: PONG received"
else
    echo -e "${RED}✗${NC} Redis: No response"
fi

echo ""
echo "MongoDB Connection:"
echo "-----------------------------------"
if docker exec rankforgedb mongosh --port 27018 --eval "db.adminCommand('ping')" > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} MongoDB: Connection successful"
else
    echo -e "${RED}✗${NC} MongoDB: Connection failed"
fi

echo ""
echo "==================================="
echo "PORT STATUS"
echo "==================================="
echo ""

# Check if ports are listening
check_port() {
    local port=$1
    local service=$2
    
    if netstat -tuln 2>/dev/null | grep -q ":$port " || ss -tuln 2>/dev/null | grep -q ":$port "; then
        echo -e "${GREEN}✓${NC} Port $port ($service): LISTENING"
    else
        echo -e "${RED}✗${NC} Port $port ($service): NOT LISTENING"
    fi
}

check_port "80" "Nginx"
check_port "8000" "Backend"
check_port "6379" "Redis"
check_port "27018" "MongoDB"

echo ""
echo "==================================="
echo "DISK SPACE"
echo "==================================="
echo ""
df -h / | tail -1 | awk '{print "Used: " $3 " / " $2 " (" $5 ")"}'

echo ""
echo "==================================="
echo "MEMORY USAGE"
echo "==================================="
echo ""
free -h | grep Mem | awk '{print "Used: " $3 " / " $2}'

echo ""
echo "==================================="
echo "RECENT ERRORS (Last 10)"
echo "==================================="
echo ""

echo "Backend Errors:"
sudo journalctl -u rankforge-backend --since "1 hour ago" | grep -i error | tail -5 || echo "No recent errors"

echo ""
echo "Worker Errors:"
sudo journalctl -u rankforge-worker --since "1 hour ago" | grep -i error | tail -5 || echo "No recent errors"

echo ""
echo "==================================="
echo "Health check completed!"
echo "==================================="
echo ""
