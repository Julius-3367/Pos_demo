# Server Commands Cheatsheet
# Quick reference for managing Odoo on 75.119.141.141:8070

## SERVICE MANAGEMENT

# Start Odoo
sudo systemctl start odoo

# Stop Odoo
sudo systemctl stop odoo

# Restart Odoo
sudo systemctl restart odoo

# Check status
sudo systemctl status odoo

# Enable auto-start on boot
sudo systemctl enable odoo

# Disable auto-start
sudo systemctl disable odoo

## LOGS & MONITORING

# View real-time logs
sudo journalctl -u odoo -f

# View last 50 lines
sudo journalctl -u odoo -n 50

# View log file (if configured)
sudo tail -f /var/log/odoo/odoo.log

# View last 100 errors
sudo journalctl -u odoo -n 100 | grep -i error

## CONFIGURATION

# Edit Odoo config
sudo nano /etc/odoo/odoo.conf

# View config
cat /etc/odoo/odoo.conf

# Test config (dry run)
sudo -u odoo /opt/odoo/venv/bin/python3 /opt/odoo/odoo/odoo-bin -c /etc/odoo/odoo.conf --test-enable --stop-after-init

# Reload systemd after config changes
sudo systemctl daemon-reload

## DATABASE OPERATIONS

# Connect to PostgreSQL
sudo -u postgres psql

# List databases
sudo -u postgres psql -l

# Create database
sudo -u postgres createdb -O odoo18 pharmacy_kenya

# Drop database
sudo -u postgres dropdb pharmacy_kenya

# Backup database
sudo -u postgres pg_dump pharmacy_kenya > backup_$(date +%Y%m%d).sql

# Restore database
sudo -u postgres psql pharmacy_kenya < backup.sql

# Create database user
sudo -u postgres createuser -d -R -S odoo18
sudo -u postgres psql -c "ALTER USER odoo18 WITH PASSWORD 'password';"

## PORT & NETWORK

# Check if port 8070 is in use
sudo netstat -tlnp | grep 8070
# or
sudo ss -tlnp | grep 8070

# Check what's using a port
sudo lsof -i :8070

# Kill process on port
sudo kill $(sudo lsof -t -i:8070)

# Test local connection
curl http://127.0.0.1:8070/web

# Test with full response
curl -I http://127.0.0.1:8070/web

## FIREWALL

# Check firewall status
sudo ufw status

# Allow port 8070
sudo ufw allow 8070/tcp

# Deny port
sudo ufw deny 8070/tcp

# Enable firewall
sudo ufw enable

# Disable firewall (testing only!)
sudo ufw disable

## FILE PERMISSIONS

# Fix ownership of custom addons
sudo chown -R odoo:odoo /opt/odoo/odoo/addons/custom

# Fix data directory permissions
sudo chown -R odoo:odoo /var/lib/odoo
sudo chmod -R 755 /var/lib/odoo

# Fix log directory permissions
sudo chown -R odoo:odoo /var/log/odoo
sudo chmod -R 755 /var/log/odoo

## MODULE MANAGEMENT

# Update module from GitHub
cd /opt/odoo/odoo/addons/custom/pos_demo
sudo -u odoo git pull origin main

# Install new module
# Do this through Odoo web interface:
# Apps → Update Apps List → Search → Install

# Upgrade module
# Do this through Odoo web interface:
# Apps → Search module → Upgrade

## PROCESS MANAGEMENT

# Find Odoo processes
ps aux | grep odoo-bin

# Kill all Odoo processes (emergency)
sudo pkill -f odoo-bin

# Count worker processes
ps aux | grep odoo-bin | wc -l

## SYSTEM RESOURCES

# Check memory usage
free -h

# Check disk space
df -h

# Check CPU usage
top -n 1

# Check Odoo's resource usage
ps aux | grep odoo

## DEBUGGING

# Start Odoo in debug mode (foreground)
sudo -u odoo /opt/odoo/venv/bin/python3 /opt/odoo/odoo/odoo-bin -c /etc/odoo/odoo.conf --log-level=debug

# Start with database update
sudo -u odoo /opt/odoo/venv/bin/python3 /opt/odoo/odoo/odoo-bin -c /etc/odoo/odoo.conf -u pos_demo -d pharmacy_kenya --stop-after-init

# Shell access to Odoo
sudo -u odoo /opt/odoo/venv/bin/python3 /opt/odoo/odoo/odoo-bin shell -c /etc/odoo/odoo.conf -d pharmacy_kenya

## NGINX (if using reverse proxy)

# Test nginx config
sudo nginx -t

# Reload nginx
sudo systemctl reload nginx

# Restart nginx
sudo systemctl restart nginx

# Check nginx status
sudo systemctl status nginx

# View nginx logs
sudo tail -f /var/log/nginx/error.log
sudo tail -f /var/log/nginx/access.log

## QUICK DIAGNOSTICS

# One-line health check
sudo systemctl is-active odoo && curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8070/web && echo " - Odoo is healthy" || echo " - Odoo has issues"

# Check all services
sudo systemctl status odoo postgresql nginx --no-pager

# Disk space alert
df -h | grep -E '^Filesystem|/$'

# Memory alert
free -h | grep Mem

## COMMON WORKFLOWS

# Deploy new code changes
cd /opt/odoo/odoo/addons/custom/pos_demo
sudo -u odoo git pull
sudo systemctl restart odoo
sudo journalctl -u odoo -f  # Watch logs

# Complete restart after changes
sudo systemctl stop odoo
sleep 3
sudo systemctl start odoo
sudo journalctl -u odoo -f

# Emergency recovery
sudo systemctl stop odoo
sudo pkill -9 -f odoo-bin
sudo systemctl start odoo

# Performance check
ps aux --sort=-%mem | head -10  # Top memory users
ps aux --sort=-%cpu | head -10  # Top CPU users

## BACKUP WORKFLOW

# Full backup
timestamp=$(date +%Y%m%d_%H%M%S)
sudo -u postgres pg_dump pharmacy_kenya > /tmp/backup_$timestamp.sql
tar -czf /tmp/filestore_$timestamp.tar.gz /var/lib/odoo/filestore/pharmacy_kenya
echo "Backup created: backup_$timestamp.sql and filestore_$timestamp.tar.gz"

# Quick backup
sudo -u postgres pg_dump pharmacy_kenya | gzip > pharmacy_kenya_$(date +%Y%m%d).sql.gz

## SECURITY

# Change Odoo admin password via command line
# (Login to Odoo web interface and use Settings → Users instead)

# Check for security updates
sudo apt update
sudo apt list --upgradable

# Update system
sudo apt update && sudo apt upgrade -y

## USEFUL ALIASES (add to ~/.bashrc)

# alias odoo-logs='sudo journalctl -u odoo -f'
# alias odoo-restart='sudo systemctl restart odoo'
# alias odoo-status='sudo systemctl status odoo'
# alias odoo-start='sudo systemctl start odoo'
# alias odoo-stop='sudo systemctl stop odoo'

---
Server: 75.119.141.141:8070
Last Updated: January 8, 2026
