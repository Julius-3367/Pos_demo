# Deployment Guide - Kenya Pharmacy System

## Server Information
- **IP Address:** 75.119.141.141
- **Port:** 8070 (Odoo 18 - Pharmacy)
- **Existing:** Port 8069 (Odoo 17)
- **OS:** Ubuntu

## Pre-Deployment Checklist

### 1. Server Requirements
- [ ] PostgreSQL installed and running
- [ ] Python 3.10+ installed
- [ ] Odoo 18 dependencies installed
- [ ] Sufficient disk space (minimum 5GB free)
- [ ] Firewall configured to allow port 8070

### 2. Odoo Configuration (`/etc/odoo/odoo18.conf`)

```ini
[options]
# Server Settings
http_port = 8070
# Use different xmlrpc_port than Odoo 17
xmlrpc_port = 8072

# Database Settings
db_host = localhost
db_port = 5432
db_user = odoo18
db_password = YOUR_DB_PASSWORD
# Important: Different database than Odoo 17
list_db = False
dbfilter = ^pharmacy_.*$

# Paths
addons_path = /opt/odoo18/odoo/addons,/opt/odoo18/odoo/addons/custom
data_dir = /var/lib/odoo18

# Logging
logfile = /var/log/odoo18/odoo.log
log_level = info

# Performance
workers = 4
max_cron_threads = 2
limit_memory_hard = 2684354560
limit_memory_soft = 2147483648
limit_request = 8192
limit_time_cpu = 600
limit_time_real = 1200

# Security
proxy_mode = True
# If behind nginx/apache
xmlrpc_interface = 127.0.0.1
netrpc_interface = 127.0.0.1
```

### 3. Nginx/Apache Reverse Proxy Setup

#### Nginx Configuration
```nginx
# /etc/nginx/sites-available/pharmacy

upstream odoo18 {
    server 127.0.0.1:8070;
}

upstream odoo18-chat {
    server 127.0.0.1:8072;
}

server {
    listen 80;
    server_name 75.119.141.141 pharmacy.yourdomain.com;

    access_log /var/log/nginx/odoo18-access.log;
    error_log /var/log/nginx/odoo18-error.log;

    # Proxy settings
    proxy_read_timeout 720s;
    proxy_connect_timeout 720s;
    proxy_send_timeout 720s;
    proxy_set_header X-Forwarded-Host $host;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_set_header X-Real-IP $remote_addr;

    # Increase buffer sizes
    proxy_buffers 16 64k;
    proxy_buffer_size 128k;

    # Force timeouts if backend dies
    proxy_next_upstream error timeout invalid_header http_500 http_502 http_503;

    # Enable data compression
    gzip on;
    gzip_min_length 1100;
    gzip_types text/plain text/css text/js text/xml text/javascript application/javascript application/json application/xml;

    # Static files
    location ~* /web/static/ {
        proxy_cache_valid 200 90m;
        proxy_buffering on;
        expires 864000;
        proxy_pass http://odoo18;
    }

    # WebSocket support for live chat
    location /websocket {
        proxy_pass http://odoo18-chat;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header X-Forwarded-Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # Main application
    location / {
        proxy_redirect off;
        proxy_pass http://odoo18;
    }

    # Common static files
    location ~* .(js|css|png|jpg|jpeg|gif|ico)$ {
        expires 2d;
        proxy_pass http://odoo18;
        add_header Cache-Control "public, no-transform";
    }
}
```

### 4. Systemd Service Setup

Create `/etc/systemd/system/odoo18.service`:

```ini
[Unit]
Description=Odoo 18 Pharmacy System
Requires=postgresql.service
After=network.target postgresql.service

[Service]
Type=simple
SyslogIdentifier=odoo18
PermissionsStartOnly=true
User=odoo18
Group=odoo18
ExecStart=/opt/odoo18/venv/bin/python3 /opt/odoo18/odoo/odoo-bin -c /etc/odoo/odoo18.conf
StandardOutput=journal+console

[Install]
WantedBy=multi-user.target
```

### 5. Common Deployment Issues & Solutions

#### Issue 1: Module Not Found
**Error:** `Module pos_demo not found`
**Solution:**
```bash
# Verify addons path
grep addons_path /etc/odoo/odoo18.conf
# Should include: /opt/odoo18/odoo/addons/custom

# Check module exists
ls -la /opt/odoo18/odoo/addons/custom/pos_demo/

# Update module list in Odoo
# Settings > Technical > Modules > Update Apps List
```

#### Issue 2: Database Connection Failed
**Error:** `FATAL: password authentication failed`
**Solution:**
```bash
# Create dedicated database user
sudo -u postgres createuser -d -R -S odoo18
sudo -u postgres psql -c "ALTER USER odoo18 WITH PASSWORD 'strong_password';"

# Create database
sudo -u postgres createdb -O odoo18 pharmacy_kenya

# Update odoo18.conf with correct credentials
```

#### Issue 3: Permission Denied
**Error:** `Permission denied: '/var/lib/odoo18'`
**Solution:**
```bash
# Create directories with correct ownership
sudo mkdir -p /var/lib/odoo18
sudo mkdir -p /var/log/odoo18
sudo chown -R odoo18:odoo18 /var/lib/odoo18
sudo chown -R odoo18:odoo18 /var/log/odoo18
sudo chmod -R 755 /var/lib/odoo18
```

#### Issue 4: Port Already in Use
**Error:** `Address already in use: 8070`
**Solution:**
```bash
# Check what's using the port
sudo netstat -tlnp | grep 8070
# or
sudo lsof -i :8070

# Kill the process if needed
sudo kill <PID>
```

#### Issue 5: Missing Python Dependencies
**Error:** `ModuleNotFoundError: No module named 'X'`
**Solution:**
```bash
# Activate virtual environment
source /opt/odoo18/venv/bin/activate

# Install requirements
pip3 install -r /opt/odoo18/odoo/requirements.txt

# Common additional dependencies
pip3 install phonenumbers qrcode
```

#### Issue 6: CSRF/Session Issues
**Solution:**
```bash
# Update odoo18.conf
# Add these parameters:
session_cookie_secure = False
session_cookie_httponly = True
session_cookie_samesite = Lax

# Restart Odoo
sudo systemctl restart odoo18
```

### 6. Firewall Configuration

```bash
# Allow port 8070 (direct access)
sudo ufw allow 8070/tcp

# Or allow only nginx (recommended)
sudo ufw allow 'Nginx Full'

# Check firewall status
sudo ufw status
```

### 7. Deployment Commands

```bash
# 1. Clone repository on server
cd /opt/odoo18/odoo/addons
sudo git clone https://github.com/yourusername/yourrepo.git custom

# 2. Set correct permissions
sudo chown -R odoo18:odoo18 /opt/odoo18/odoo/addons/custom

# 3. Restart Odoo
sudo systemctl restart odoo18

# 4. Check status
sudo systemctl status odoo18

# 5. Check logs
sudo tail -f /var/log/odoo18/odoo.log
```

### 8. Database Migration (from localhost to server)

```bash
# On localhost - Export database
pg_dump -U odoo -h localhost pharmacy_kenya > pharmacy_kenya_backup.sql

# Transfer to server
scp pharmacy_kenya_backup.sql user@75.119.141.141:/tmp/

# On server - Import database
sudo -u postgres createdb -O odoo18 pharmacy_kenya
sudo -u postgres psql pharmacy_kenya < /tmp/pharmacy_kenya_backup.sql

# Update base URL in database
sudo -u postgres psql pharmacy_kenya
UPDATE ir_config_parameter SET value = 'http://75.119.141.141:8070' WHERE key = 'web.base.url';
\q
```

### 9. SSL Certificate (Optional but Recommended)

```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx

# Get certificate (if you have domain name)
sudo certbot --nginx -d pharmacy.yourdomain.com

# Auto-renewal
sudo certbot renew --dry-run
```

### 10. Monitoring & Logs

```bash
# View real-time logs
sudo journalctl -u odoo18 -f

# View nginx logs
sudo tail -f /var/log/nginx/odoo18-error.log

# Check service status
sudo systemctl status odoo18
sudo systemctl status postgresql
sudo systemctl status nginx
```

## Quick Deployment Script

Save as `deploy.sh`:

```bash
#!/bin/bash

echo "🚀 Deploying Kenya Pharmacy System..."

# Variables
ODOO_USER="odoo18"
ODOO_HOME="/opt/odoo18"
CUSTOM_ADDONS="$ODOO_HOME/odoo/addons/custom"

# Pull latest changes
echo "📥 Pulling latest changes..."
cd $CUSTOM_ADDONS/pos_demo
sudo -u $ODOO_USER git pull origin main

# Set permissions
echo "🔒 Setting permissions..."
sudo chown -R $ODOO_USER:$ODOO_USER $CUSTOM_ADDONS

# Restart Odoo
echo "🔄 Restarting Odoo..."
sudo systemctl restart odoo18

# Wait for startup
echo "⏳ Waiting for Odoo to start..."
sleep 10

# Check status
echo "📊 Checking status..."
sudo systemctl status odoo18 --no-pager

echo "✅ Deployment complete!"
echo "🌐 Access at: http://75.119.141.141:8070"
```

## Troubleshooting Commands

```bash
# Check if Odoo is running
ps aux | grep odoo

# Check port binding
sudo netstat -tlnp | grep 8070

# Test database connection
sudo -u odoo18 psql -h localhost -U odoo18 -d pharmacy_kenya -c "SELECT 1;"

# Check Odoo configuration
sudo -u odoo18 /opt/odoo18/venv/bin/python3 /opt/odoo18/odoo/odoo-bin -c /etc/odoo/odoo18.conf --test-enable --stop-after-init

# View last 100 log lines
sudo journalctl -u odoo18 -n 100
```

## Post-Deployment Checklist

- [ ] Odoo accessible at http://75.119.141.141:8070
- [ ] Can login with admin credentials
- [ ] pos_demo module is installed and activated
- [ ] Can create products, prescriptions
- [ ] POS interface loads correctly
- [ ] Reports generate without CSRF errors
- [ ] Database backups scheduled
- [ ] SSL certificate installed (if using domain)
- [ ] Monitoring setup (optional)

## Support

If you encounter errors, collect this information:
1. Error message (exact text)
2. Odoo logs: `sudo journalctl -u odoo18 -n 100`
3. Nginx logs (if applicable): `sudo tail -100 /var/log/nginx/odoo18-error.log`
4. System info: `free -h && df -h`

---

**Last Updated:** January 8, 2026
