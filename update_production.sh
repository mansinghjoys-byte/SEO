#!/bin/bash

################################################################################
# RankForge SEO Platform - Quick Update Script
# Description: Quick deployment update without full setup
################################################################################

set -e

# Color codes
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

DEPLOY_DIR="/var/www/rankforge"
BRANCH="AEo4"

echo -e "${BLUE}==>${NC} Updating RankForge SEO Platform..."

# Pull latest changes
cd "$DEPLOY_DIR"
git fetch origin
git checkout $BRANCH
git pull origin $BRANCH
echo -e "${GREEN}✓${NC} Code updated"

# Update backend
cd "$DEPLOY_DIR/backend"
source venv/bin/activate
pip install -r requirements.txt -q
echo -e "${GREEN}✓${NC} Backend dependencies updated"

# Update frontend
cd "$DEPLOY_DIR/frontend"
if command -v yarn &> /dev/null; then
    yarn install
    yarn build
else
    npm install
    npm run build
fi
echo -e "${GREEN}✓${NC} Frontend rebuilt"

# Restart services
sudo systemctl restart rankforge-backend
sudo systemctl restart rankforge-worker
sudo systemctl reload nginx
echo -e "${GREEN}✓${NC} Services restarted"

echo ""
echo -e "${GREEN}✓${NC} Update completed successfully!"
echo ""
echo "Check status with: sudo systemctl status rankforge-backend"
