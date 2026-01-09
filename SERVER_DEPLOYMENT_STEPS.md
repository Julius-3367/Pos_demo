# Step-by-Step Server Deployment Instructions
# For: Kenya Pharmacy System on Ubuntu Server
# Server IP: 75.119.141.141
# Port: 8070 (Odoo 18) - Port 8069 has Odoo 17

## STEP 1: Connect to Your Server
```bash
ssh your_username@75.119.141.141
```

## STEP 2: Upload Diagnostic Script
```bash
# From your LOCAL machine (where this code is)
scp /opt/odoo/odoo/addons/custom/pos_demo/server_diagnostic.sh your_username@75.119.141.141:/tmp/
scp /opt/odoo/odoo/addons/custom/pos_demo/quick_troubleshoot.sh your_username@75.119.141.141:/tmp/

# On SERVER, make executable and run
ssh your_username@75.119.141.141
chmod +x /tmp/server_diagnostic.sh
sudo /tmp/server_diagnostic.sh
```

## STEP 3: Identify the Exact Error

**READ THE DIAGNOSTIC OUTPUT CAREFULLY**

Common scenarios and what to do:

### Scenario A: "Odoo is NOT running"
```bash
# Check if Odoo service exists
sudo systemctl list-units --type=service | grep odoo

# If service exists, start it
sudo systemctl start odoo
# or
sudo systemctl start odoo18

# Check status
sudo systemctl status odoo
```

### Scenario B: "Port 8070 is NOT in use"
```bash
# Check Odoo configuration
cat /etc/odoo/odoo.conf | grep http_port

# Should show: http_port = 8070
# If it shows 8069, you need to change it

# Edit config
sudo nano /etc/odoo/odoo.conf
# Change: http_port = 8070
# Save: Ctrl+O, Enter, Ctrl+X

# Restart Odoo
sudo systemctl restart odoo
```

### Scenario C: "Custom module directory NOT found"
```bash
# Check where Odoo expects addons
grep addons_path /etc/odoo/odoo.conf

# Example output: addons_path = /opt/odoo/odoo/addons,/opt/odoo/odoo/addons/custom

# Create custom directory if needed
sudo mkdir -p /opt/odoo/odoo/addons/custom

# Clone your GitHub repository
cd /opt/odoo/odoo/addons/custom
sudo git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git pos_demo

# Or if repo is the whole custom folder:
cd /opt/odoo/odoo/addons
sudo git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git custom

# Set permissions
sudo chown -R odoo:odoo /opt/odoo/odoo/addons/custom
```

### Scenario D: "PostgreSQL is NOT running"
```bash
# Start PostgreSQL
sudo systemctl start postgresql

# Enable auto-start
sudo systemctl enable postgresql

# Check status
sudo systemctl status postgresql
```

### Scenario E: "Database connection failed"
```bash
# Create database user for Odoo 18 (different from Odoo 17)
sudo -u postgres createuser -d -R -S odoo18
sudo -u postgres psql -c "ALTER USER odoo18 WITH PASSWORD 'your_password';"

# Create database
sudo -u postgres createdb -O odoo18 pharmacy_kenya

# Update Odoo config with correct credentials
sudo nano /etc/odoo/odoo.conf
# Set:
#   db_user = odoo18
#   db_password = your_password

# Restart Odoo
sudo systemctl restart odoo
```

## STEP 4: Check Odoo Configuration File

```bash
# View current config
cat /etc/odoo/odoo.conf

# MUST HAVE (minimum):
# [options]
# http_port = 8070
# addons_path = /opt/odoo/odoo/addons,/opt/odoo/odoo/addons/custom
# db_host = localhost
# db_port = 5432
# db_user = odoo18
# db_password = YOUR_PASSWORD
# logfile = /var/log/odoo/odoo.log

# Use the provided template
sudo cp /path/to/odoo18_server.conf /etc/odoo/odoo.conf
# Edit the password
sudo nano /etc/odoo/odoo.conf
```

## STEP 5: Ensure Module Files Are Present

```bash
# Check module exists
ls -la /opt/odoo/odoo/addons/custom/pos_demo/

# Should see:
# __init__.py
# __manifest__.py
# models/
# views/
# etc.

# If NOT there, clone from GitHub:
cd /opt/odoo/odoo/addons/custom
sudo git clone YOUR_GITHUB_REPO_URL pos_demo

# Set correct permissions
sudo chown -R odoo:odoo /opt/odoo/odoo/addons/custom
```

## STEP 6: Restart Odoo and Check Logs

```bash
# Restart Odoo
sudo systemctl restart odoo

# Watch logs in real-time
sudo journalctl -u odoo -f

# Or check log file
sudo tail -f /var/log/odoo/odoo.log

# Look for:
# - "Modules loaded" (good)
# - "ERROR" or "Exception" (bad - note the error message)
```

## STEP 7: Test Access

```bash
# From server itself
curl http://127.0.0.1:8070/web

# Should return HTML (Odoo web page)

# From your local machine
curl http://75.119.141.141:8070/web

# Or open in browser:
# http://75.119.141.141:8070
```

## STEP 8: Check Firewall

```bash
# Check if port 8070 is allowed
sudo ufw status | grep 8070

# If not listed, allow it
sudo ufw allow 8070/tcp

# Reload firewall
sudo ufw reload
```

## STEP 9: Install/Activate Module in Odoo

1. Open browser: `http://75.119.141.141:8070`
2. Login with admin credentials
3. Go to **Apps** menu
4. Click **Update Apps List**
5. Search for **"pos_demo"** or **"Pharmacy"**
6. Click **Install** or **Activate**

## STEP 10: Common Errors and Solutions

### Error: "Module pos_demo not found"
**Solution:**
```bash
# Verify addons_path includes custom folder
grep addons_path /etc/odoo/odoo.conf

# Should be: addons_path = /opt/odoo/odoo/addons,/opt/odoo/odoo/addons/custom

# Verify module exists
ls /opt/odoo/odoo/addons/custom/pos_demo/__manifest__.py

# Restart Odoo
sudo systemctl restart odoo
```

### Error: "Address already in use"
**Solution:**
```bash
# Find what's using port 8070
sudo netstat -tlnp | grep 8070

# If it's old Odoo process, kill it
sudo kill <PID>

# Or change port in config to something else
sudo nano /etc/odoo/odoo.conf
# Set: http_port = 8071
```

### Error: "FATAL: password authentication failed"
**Solution:**
```bash
# Reset database user password
sudo -u postgres psql
ALTER USER odoo18 WITH PASSWORD 'new_password';
\q

# Update config file
sudo nano /etc/odoo/odoo.conf
# Set: db_password = new_password

# Restart
sudo systemctl restart odoo
```

### Error: "No module named 'odoo'"
**Solution:**
```bash
# Odoo not properly installed or wrong Python environment

# Check if odoo-bin exists
ls /opt/odoo/odoo/odoo-bin

# Check systemd service file
cat /etc/systemd/system/odoo.service

# Should point to correct odoo-bin location
```

## STEP 11: Migration from Localhost (Optional)

If you want to copy your database from localhost to server:

```bash
# On LOCALHOST - Export database
pg_dump -U odoo pharmacy_kenya > pharmacy_kenya.sql

# Transfer to server
scp pharmacy_kenya.sql your_username@75.119.141.141:/tmp/

# On SERVER - Import
sudo -u postgres psql
DROP DATABASE IF EXISTS pharmacy_kenya;
CREATE DATABASE pharmacy_kenya OWNER odoo18;
\q

sudo -u postgres psql pharmacy_kenya < /tmp/pharmacy_kenya.sql

# Update base URL
sudo -u postgres psql pharmacy_kenya
UPDATE ir_config_parameter SET value = 'http://75.119.141.141:8070' WHERE key = 'web.base.url';
\q

# Restart Odoo
sudo systemctl restart odoo
```

## STEP 12: Set Up Auto-Start

```bash
# Enable Odoo to start on boot
sudo systemctl enable odoo

# Verify
sudo systemctl is-enabled odoo
```

## Final Checklist

- [ ] Odoo service is running: `sudo systemctl status odoo`
- [ ] Port 8070 is listening: `sudo netstat -tlnp | grep 8070`
- [ ] Firewall allows port 8070: `sudo ufw status`
- [ ] Module files exist: `ls /opt/odoo/odoo/addons/custom/pos_demo/`
- [ ] Can access web interface: http://75.119.141.141:8070
- [ ] Can login to Odoo
- [ ] Module pos_demo is installed
- [ ] No errors in logs: `sudo journalctl -u odoo -n 50`

## Getting Help

If still having issues, collect this information:

1. **Diagnostic output:**
   ```bash
   sudo /tmp/server_diagnostic.sh > diagnostic_output.txt
   ```

2. **Last 100 log lines:**
   ```bash
   sudo journalctl -u odoo -n 100 > odoo_logs.txt
   ```

3. **Configuration:**
   ```bash
   cat /etc/odoo/odoo.conf > config.txt
   ```

4. **Exact error message** you see when trying to activate the module

Share these files for troubleshooting.

---

**Pro Tip:** Start simple! Get Odoo running first (even without your module), then add the module.
