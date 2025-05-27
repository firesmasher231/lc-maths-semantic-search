# LC Mathematics Search - Deployment Guide

This guide covers two deployment approaches for your Oracle Cloud server with code-server.

## 🐳 Recommended: Docker Deployment

### Prerequisites

```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Log out and back in for group changes to take effect
```

### Quick Deployment

```bash
# Clone the repository
git clone <your-repo-url> lc-math-search
cd lc-math-search/math-search-webapp

# Make deployment script executable
chmod +x deploy.sh

# Deploy the application
./deploy.sh deploy
```

### Manual Docker Commands

```bash
# Build and start
docker-compose up -d --build

# View logs
docker-compose logs -f

# Stop application
docker-compose down

# Restart
docker-compose restart
```

### Deployment Script Commands

```bash
./deploy.sh deploy    # First time deployment
./deploy.sh start     # Start existing application
./deploy.sh stop      # Stop application
./deploy.sh restart   # Restart application
./deploy.sh logs      # View logs
./deploy.sh status    # Check status
./deploy.sh update    # Update to latest version
```

### Adding PDF Papers

```bash
# Copy your PDF papers to the data/papers directory
cp /path/to/your/papers/*.pdf ./data/papers/

# Restart the application to process new papers
./deploy.sh restart
```

### Accessing the Application

- **Local**: http://localhost:5000
- **External**: http://your-oracle-server-ip:5000

### Port Configuration

To change the port, edit `docker-compose.yml`:

```yaml
ports:
  - "8080:5000" # Change 8080 to your desired port
```

---

## 📁 Alternative: Git-Based Deployment

### Prerequisites

```bash
# Install Python 3.11+
sudo apt update
sudo apt install python3.11 python3.11-pip python3.11-venv

# Install system dependencies
sudo apt install gcc g++ curl
```

### Deployment Steps

```bash
# Clone repository
git clone <your-repo-url> lc-math-search
cd lc-math-search/math-search-webapp

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create data directory and copy papers
mkdir -p data/papers
cp /path/to/your/papers/*.pdf ./data/papers/

# Run the application
python app.py
```

### Running as a Service (systemd)

Create `/etc/systemd/system/lc-math-search.service`:

```ini
[Unit]
Description=LC Mathematics Search Application
After=network.target

[Service]
Type=simple
User=your-username
WorkingDirectory=/path/to/lc-math-search/math-search-webapp
Environment=PATH=/path/to/lc-math-search/math-search-webapp/venv/bin
ExecStart=/path/to/lc-math-search/math-search-webapp/venv/bin/python app.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable lc-math-search
sudo systemctl start lc-math-search
sudo systemctl status lc-math-search
```

### Auto-sync with Git

Create a cron job for automatic updates:

```bash
# Edit crontab
crontab -e

# Add this line to check for updates every hour
0 * * * * cd /path/to/lc-math-search && git pull && sudo systemctl restart lc-math-search
```

---

## 🔧 Configuration

### Environment Variables

Create `.env` file:

```bash
FLASK_ENV=production
FLASK_HOST=0.0.0.0
FLASK_PORT=5000
PAPERS_DIR=data/papers
```

### Firewall Configuration

```bash
# Allow port 5000 (or your chosen port)
sudo ufw allow 5000
sudo ufw reload
```

### Oracle Cloud Security Rules

Add ingress rule in Oracle Cloud Console:

- **Source CIDR**: 0.0.0.0/0
- **IP Protocol**: TCP
- **Destination Port Range**: 5000

---

## 📊 Monitoring & Maintenance

### Health Checks

```bash
# Check application health
curl http://localhost:5000/api/status

# Docker health check
docker-compose ps
```

### Log Management

```bash
# Docker logs
docker-compose logs -f --tail=100

# System service logs
sudo journalctl -u lc-math-search -f
```

### Backup Strategy

```bash
# Backup papers and any processed data
tar -czf backup-$(date +%Y%m%d).tar.gz data/

# Backup to cloud storage (example with rclone)
rclone copy backup-$(date +%Y%m%d).tar.gz remote:backups/
```

---

## 🚀 Performance Optimization

### For Production Use

1. **Use a reverse proxy** (nginx/Apache)
2. **Enable HTTPS** with Let's Encrypt
3. **Set up monitoring** (Prometheus/Grafana)
4. **Configure log rotation**
5. **Set up automated backups**

### Nginx Reverse Proxy Example

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

---

## 🔍 Troubleshooting

### Common Issues

1. **Port already in use**: Change port in docker-compose.yml
2. **Permission denied**: Check file permissions and user groups
3. **Out of memory**: Increase server memory or optimize model loading
4. **PDF processing fails**: Check PDF file permissions and formats

### Debug Mode

```bash
# Enable debug logging
export FLASK_DEBUG=1
python app.py
```

---

## 📈 Scaling Considerations

For high-traffic scenarios:

1. **Load balancer** with multiple instances
2. **Redis cache** for search results
3. **Database** for metadata storage
4. **CDN** for static assets
5. **Container orchestration** (Kubernetes)

---

## 🔄 Update Process

### Docker Deployment

```bash
./deploy.sh update
```

### Git Deployment

```bash
git pull
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart lc-math-search
```
