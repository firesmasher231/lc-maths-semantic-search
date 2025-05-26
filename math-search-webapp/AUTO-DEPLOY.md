# Automatic Deployment Setup Guide

This guide shows you how to set up automatic deployment of your LC Mathematics Search application whenever you push code to GitHub.

## 🎯 Overview

You have **two options** for automatic deployment:

1. **🐳 Webhook-based Deployment** (Recommended) - Simple webhook server on your Oracle server
2. **⚡ GitHub Actions** - Uses GitHub's CI/CD infrastructure

---

## 🐳 Option 1: Webhook-based Deployment (Recommended)

This approach runs a small webhook server on your Oracle Cloud server that listens for GitHub push events.

### Quick Setup

```bash
# 1. Clone your repository to Oracle server
git clone https://github.com/your-username/your-repo.git lc-math-search
cd lc-math-search/math-search-webapp

# 2. Run the auto-deployment setup script
chmod +x setup-auto-deploy.sh
./setup-auto-deploy.sh
```

### Manual Setup Steps

#### 1. Install Dependencies

```bash
# Install Docker (if not already installed)
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Python Flask for webhook server
pip3 install flask --user
```

#### 2. Configure Webhook Server

```bash
# Make scripts executable
chmod +x webhook-deploy.py
chmod +x deploy.sh

# Generate a webhook secret (save this!)
WEBHOOK_SECRET=$(openssl rand -hex 32)
echo "Your webhook secret: $WEBHOOK_SECRET"
```

#### 3. Create Systemd Service

```bash
# Create service file
sudo nano /etc/systemd/system/lc-math-webhook.service
```

Add this content (replace paths and secret):

```ini
[Unit]
Description=LC Math Search Webhook Deployment Server
After=network.target

[Service]
Type=simple
User=ubuntu
Group=docker
WorkingDirectory=/home/ubuntu/lc-math-search/math-search-webapp
Environment=PATH=/usr/local/bin:/usr/bin:/bin
Environment=WEBHOOK_SECRET=your-webhook-secret-here
Environment=WEBHOOK_PORT=9000
ExecStart=/usr/bin/python3 webhook-deploy.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

#### 4. Start the Service

```bash
sudo systemctl daemon-reload
sudo systemctl enable lc-math-webhook
sudo systemctl start lc-math-webhook
sudo systemctl status lc-math-webhook
```

#### 5. Configure Firewall

```bash
# Allow webhook port
sudo ufw allow 9000/tcp

# Also configure Oracle Cloud Security Rules:
# - Source CIDR: 0.0.0.0/0
# - IP Protocol: TCP
# - Destination Port Range: 9000
```

#### 6. Add Webhook to GitHub

1. Go to your GitHub repository
2. Navigate to **Settings** → **Webhooks**
3. Click **Add webhook**
4. Configure:
   - **Payload URL**: `http://YOUR_SERVER_IP:9000/webhook`
   - **Content type**: `application/json`
   - **Secret**: Your webhook secret from step 2
   - **Events**: Select "Just the push event"
5. Click **Add webhook**

### Testing Webhook Deployment

```bash
# Test webhook health
curl http://localhost:9000/health

# Test manual deployment
curl -X POST http://localhost:9000/deploy

# View webhook logs
sudo journalctl -u lc-math-webhook -f

# Check application status
./deploy.sh status
```

---

## ⚡ Option 2: GitHub Actions

This approach uses GitHub's servers to deploy to your Oracle server via SSH.

### Setup Steps

#### 1. Generate SSH Key Pair

```bash
# On your local machine or Oracle server
ssh-keygen -t ed25519 -C "github-actions-deploy" -f ~/.ssh/github_deploy

# Copy public key to Oracle server
ssh-copy-id -i ~/.ssh/github_deploy.pub ubuntu@YOUR_SERVER_IP
```

#### 2. Add GitHub Secrets

In your GitHub repository, go to **Settings** → **Secrets and variables** → **Actions** and add:

- `SSH_PRIVATE_KEY`: Content of `~/.ssh/github_deploy` (private key)
- `SERVER_HOST`: Your Oracle server IP address
- `SSH_USER`: Your server username (usually `ubuntu`)
- `APP_PATH`: Path to your app (e.g., `/home/ubuntu/lc-math-search/math-search-webapp`)

#### 3. GitHub Actions Workflow

The workflow file is already created at `.github/workflows/deploy.yml`. It will:

- Trigger on pushes to `main` or `master` branch
- SSH into your server
- Pull latest code
- Run deployment script
- Verify deployment

### Testing GitHub Actions

1. Push code to your main branch
2. Check the **Actions** tab in your GitHub repository
3. Monitor the deployment progress
4. Verify your application is updated

---

## 🔧 Configuration

### Environment Variables

Create a `.env` file in your application directory:

```bash
FLASK_ENV=production
FLASK_HOST=0.0.0.0
FLASK_PORT=5000
PAPERS_DIR=data/papers
WEBHOOK_SECRET=your-webhook-secret-here
WEBHOOK_PORT=9000
```

### Updating Python Version

The Dockerfile now uses **Python 3.12.8**. To update:

```bash
# The Docker image will automatically use Python 3.12.8
./deploy.sh update
```

---

## 📊 Monitoring

### Webhook Server Monitoring

```bash
# Check webhook service status
sudo systemctl status lc-math-webhook

# View real-time logs
sudo journalctl -u lc-math-webhook -f

# Check webhook health
curl http://localhost:9000/health
```

### Application Monitoring

```bash
# Check application status
./deploy.sh status

# View application logs
./deploy.sh logs

# Check if application is responding
curl http://localhost:5000/api/status
```

---

## 🔍 Troubleshooting

### Common Issues

#### Webhook Not Receiving Events

1. Check GitHub webhook delivery logs
2. Verify firewall allows port 9000
3. Check Oracle Cloud security rules
4. Verify webhook secret matches

#### Deployment Fails

```bash
# Check webhook logs
sudo journalctl -u lc-math-webhook -f

# Check Docker status
docker ps
docker-compose ps

# Manual deployment test
./deploy.sh deploy
```

#### Permission Issues

```bash
# Fix Docker permissions
sudo usermod -aG docker $USER
# Log out and back in

# Fix file permissions
chmod +x deploy.sh
chmod +x webhook-deploy.py
```

### Debug Commands

```bash
# Test webhook manually
curl -X POST http://localhost:9000/deploy

# Check webhook server is running
netstat -tlnp | grep 9000

# Test GitHub webhook delivery
# (Use GitHub webhook delivery logs)

# Check application health
curl http://localhost:5000/api/status
```

---

## 🚀 Deployment Flow

### Webhook-based Flow

1. You push code to GitHub
2. GitHub sends webhook to your server
3. Webhook server receives the event
4. Server pulls latest code
5. Docker container is rebuilt and restarted
6. Application is updated

### GitHub Actions Flow

1. You push code to GitHub
2. GitHub Actions workflow triggers
3. GitHub runner SSHs to your server
4. Latest code is pulled
5. Deployment script runs
6. Application is updated

---

## 🔒 Security Considerations

1. **Use strong webhook secrets** (32+ character random strings)
2. **Limit webhook to specific branches** (main/master only)
3. **Use SSH keys for GitHub Actions** (not passwords)
4. **Keep your server updated** with security patches
5. **Monitor deployment logs** for suspicious activity
6. **Use HTTPS** for production (with reverse proxy)

---

## 📈 Advanced Features

### Rollback Capability

```bash
# Keep previous Docker images for rollback
docker images | grep lc-math-search

# Rollback to previous version
docker tag lc-math-search:previous lc-math-search:latest
./deploy.sh restart
```

### Blue-Green Deployment

For zero-downtime deployments, consider:

1. Running multiple containers
2. Using a load balancer
3. Switching traffic between versions

### Monitoring Integration

- Add Prometheus metrics
- Set up Grafana dashboards
- Configure alerting for failed deployments

---

## 🎉 Success!

Once set up, your deployment workflow will be:

1. **Develop** your code locally
2. **Push** to GitHub
3. **Automatic deployment** happens
4. **Verify** your changes are live

Your LC Mathematics Search application will now automatically update whenever you push code to GitHub! 🚀
