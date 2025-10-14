#!/bin/bash

# Server Setup Script for Notifio Deployment
# This script helps configure your server for automated deployment

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Notifio Server Setup Script${NC}"
echo "=================================="
echo

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    echo -e "${RED}❌ Please don't run this script as root${NC}"
    echo "Run as a regular user with sudo access"
    exit 1
fi

# Check if user has sudo access
if ! sudo -n true 2>/dev/null; then
    echo -e "${YELLOW}⚠️  User does not have passwordless sudo access${NC}"
    echo
    echo "To fix this, you need to:"
    echo "1. Run: sudo visudo"
    echo "2. Add this line at the end:"
    echo "   $USER ALL=(ALL) NOPASSWD:ALL"
    echo "3. Save and exit (Ctrl+X, then Y, then Enter in nano)"
    echo
    echo "After making this change, run this script again."
    exit 1
fi

echo -e "${GREEN}✅ User has passwordless sudo access${NC}"

# Update package list
echo -e "${BLUE}📦 Updating package list...${NC}"
sudo apt-get update

# Install required packages
echo -e "${BLUE}📦 Installing required packages...${NC}"
sudo apt-get install -y python3 python3-pip python3-venv curl wget git

# Create deployment directory
echo -e "${BLUE}📁 Creating deployment directory...${NC}"
sudo mkdir -p /opt/notifio
sudo chown $USER:$USER /opt/notifio

# Create systemd directory if it doesn't exist
sudo mkdir -p /etc/systemd/system

echo -e "${GREEN}✅ Server setup completed successfully!${NC}"
echo
echo "Your server is now ready for Notifio deployment."
echo "You can now run the GitHub Actions workflow to deploy Notifio."
echo
echo "Next steps:"
echo "1. Make sure your GitHub repository has the required secrets configured"
echo "2. Run the 'Deploy Notifio to Server' workflow from GitHub Actions"
echo "3. The deployment should now work without sudo password issues"
echo
echo -e "${YELLOW}Note: If you encounter any issues, check the GitHub Actions logs for detailed error messages.${NC}"
