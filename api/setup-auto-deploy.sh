#!/bin/bash

# LC Mathematics Search - Auto-Deployment Setup Script
# This script sets up automatic deployment from GitHub pushes

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Configuration
WEBHOOK_SECRET=""
WEBHOOK_PORT="9000"
APP_PATH="/home/ubuntu/lc-math-search/math-search-webapp"
SERVICE_USER="ubuntu"

echo "🚀 LC Mathematics Search - Auto-Deployment Setup"
echo "=================================================="
echo ""

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   print_error "This script should not be run as root. Please run as your regular user."
   exit 1
fi

# Get configuration from user
read -p "Enter your GitHub webhook secret (generate a random string): " WEBHOOK_SECRET
if [[ -z "$WEBHOOK_SECRET" ]]; then
    print_error "Webhook secret is required!"
    exit 1
fi

read -p "Enter webhook port (default: 9000): " input_port
WEBHOOK_PORT=${input_port:-9000}

read -p "Enter application path (default: $APP_PATH): " input_path
APP_PATH=${input_path:-$APP_PATH}

read -p "Enter service user (default: $SERVICE_USER): " input_user
SERVICE_USER=${input_user:-$SERVICE_USER}

echo ""
print_status "Configuration:"
print_status "  Webhook Port: $WEBHOOK_PORT"
print_status "  App Path: $APP_PATH"
print_status "  Service User: $SERVICE_USER"
print_status "  Webhook Secret: [HIDDEN]"
echo ""

# Confirm setup
read -p "Continue with setup? (y/N): " confirm
if [[ ! "$confirm" =~ ^[Yy]$ ]]; then
    print_warning "Setup cancelled."
    exit 0
fi

# Install dependencies
print_status "Installing Python dependencies for webhook server..."
pip3 install flask --user

# Make webhook script executable
print_status "Making webhook script executable..."
chmod +x webhook-deploy.py

# Create systemd service file
print_status "Creating systemd service file..."
sudo tee /etc/systemd/system/lc-math-webhook.service > /dev/null << EOF
[Unit]
Description=LC Math Search Webhook Deployment Server
After=network.target

[Service]
Type=simple
User=$SERVICE_USER
Group=docker
WorkingDirectory=$APP_PATH
Environment=PATH=/usr/local/bin:/usr/bin:/bin
Environment=WEBHOOK_SECRET=$WEBHOOK_SECRET
Environment=WEBHOOK_PORT=$WEBHOOK_PORT
ExecStart=/usr/bin/python3 webhook-deploy.py
Restart=always
RestartSec=10

# Security settings
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ReadWritePaths=$APP_PATH
ProtectHome=true

[Install]
WantedBy=multi-user.target
EOF

# Enable and start the service
print_status "Enabling and starting webhook service..."
sudo systemctl daemon-reload
sudo systemctl enable lc-math-webhook
sudo systemctl start lc-math-webhook

# Check service status
sleep 2
if sudo systemctl is-active --quiet lc-math-webhook; then
    print_success "Webhook service is running!"
else
    print_error "Webhook service failed to start. Check logs with: sudo journalctl -u lc-math-webhook -f"
    exit 1
fi

# Configure firewall
print_status "Configuring firewall..."
if command -v ufw &> /dev/null; then
    sudo ufw allow $WEBHOOK_PORT/tcp
    print_success "Firewall rule added for port $WEBHOOK_PORT"
else
    print_warning "UFW not found. Please manually open port $WEBHOOK_PORT in your firewall."
fi

# Get server IP
SERVER_IP=$(curl -s ifconfig.me || curl -s ipinfo.io/ip || echo "YOUR_SERVER_IP")

print_success "Auto-deployment setup complete!"
echo ""
print_status "Next steps:"
echo "1. Add this webhook URL to your GitHub repository:"
echo "   http://$SERVER_IP:$WEBHOOK_PORT/webhook"
echo ""
echo "2. In your GitHub repository settings:"
echo "   - Go to Settings > Webhooks"
echo "   - Click 'Add webhook'"
echo "   - Payload URL: http://$SERVER_IP:$WEBHOOK_PORT/webhook"
echo "   - Content type: application/json"
echo "   - Secret: $WEBHOOK_SECRET"
echo "   - Events: Just the push event"
echo ""
echo "3. Make sure your Oracle Cloud security rules allow inbound traffic on port $WEBHOOK_PORT"
echo ""
print_status "Useful commands:"
echo "  Check webhook service status: sudo systemctl status lc-math-webhook"
echo "  View webhook logs: sudo journalctl -u lc-math-webhook -f"
echo "  Test webhook manually: curl -X POST http://localhost:$WEBHOOK_PORT/deploy"
echo "  Check webhook health: curl http://localhost:$WEBHOOK_PORT/health"
echo ""
print_warning "Remember to:"
print_warning "1. Add the webhook URL to your GitHub repository"
print_warning "2. Configure Oracle Cloud security rules for port $WEBHOOK_PORT"
print_warning "3. Test the deployment by pushing to your main/master branch" 