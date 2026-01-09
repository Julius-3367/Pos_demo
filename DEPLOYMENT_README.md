# 🚀 Server Deployment Files

This folder contains everything you need to deploy the Kenya Pharmacy System to your Ubuntu server at **75.119.141.141:8070**

## 📁 Files Overview

### 1. **SERVER_DEPLOYMENT_STEPS.md** ⭐ START HERE
**What:** Step-by-step instructions for deploying to your server  
**When to use:** First time deployment or when having issues  
**Contains:** Detailed commands and troubleshooting for each step

### 2. **server_diagnostic.sh** 
**What:** Comprehensive diagnostic script  
**When to use:** To identify what's wrong on the server  
**How to use:**
```bash
# Upload to server
scp server_diagnostic.sh user@75.119.141.141:/tmp/
# Run on server
ssh user@75.119.141.141
sudo /tmp/server_diagnostic.sh
```

### 3. **quick_troubleshoot.sh**
**What:** Quick check script  
**When to use:** Fast status check  
**How to use:**
```bash
# On server
sudo /tmp/quick_troubleshoot.sh
```

### 4. **odoo18_server.conf**
**What:** Odoo configuration template for your server  
**When to use:** Setting up Odoo configuration  
**How to use:**
```bash
# Copy to server
scp odoo18_server.conf user@75.119.141.141:/tmp/
# Install on server
sudo cp /tmp/odoo18_server.conf /etc/odoo/odoo.conf
# Edit passwords
sudo nano /etc/odoo/odoo.conf
```

### 5. **DEPLOYMENT_GUIDE.md**
**What:** Complete deployment reference guide  
**When to use:** For detailed configuration options  
**Contains:** Nginx config, systemd service, SSL setup, etc.

### 6. **CSRF_FIX_GUIDE.md**
**What:** Browser cache issue fixes  
**When to use:** Getting CSRF errors after deployment  
**Quick fix:** Press Ctrl+Shift+R in browser

## 🎯 Quick Start - Deploy in 5 Steps

### Step 1: Upload Diagnostic Script
```bash
# From your local machine
scp server_diagnostic.sh user@75.119.141.141:/tmp/
```

### Step 2: Connect and Run Diagnostic
```bash
ssh user@75.119.141.141
sudo chmod +x /tmp/server_diagnostic.sh
sudo /tmp/server_diagnostic.sh
```

### Step 3: Read the Output
The diagnostic will tell you what's wrong:
- ✓ = Working correctly
- ✗ = Problem found
- ⚠ = Warning/needs attention

### Step 4: Follow the Fix
Based on diagnostic output, follow the fixes in **SERVER_DEPLOYMENT_STEPS.md**

### Step 5: Test Access
```bash
# From server
curl http://127.0.0.1:8070/web

# From browser
http://75.119.141.141:8070
```

## 🔧 Common Issues Quick Reference

| Issue | File to Check | Quick Fix |
|-------|--------------|-----------|
| "What's the error?" | Run `server_diagnostic.sh` | Identifies the problem |
| Odoo not running | SERVER_DEPLOYMENT_STEPS.md § Scenario A | `sudo systemctl start odoo` |
| Wrong port | SERVER_DEPLOYMENT_STEPS.md § Scenario B | Change http_port in config |
| Module not found | SERVER_DEPLOYMENT_STEPS.md § Scenario C | Check addons_path, clone repo |
| Database error | SERVER_DEPLOYMENT_STEPS.md § Scenario E | Create db user, set password |
| CSRF errors | CSRF_FIX_GUIDE.md | Press Ctrl+Shift+R |
| Can't access from browser | Check firewall | `sudo ufw allow 8070/tcp` |

## 📋 Deployment Checklist

Before you start, make sure you have:

- [ ] SSH access to 75.119.141.141
- [ ] Sudo/root privileges on the server
- [ ] Odoo 18 installed on the server
- [ ] PostgreSQL installed and running
- [ ] GitHub repository URL with your code
- [ ] Database credentials

## 🆘 Still Having Issues?

1. **Run the diagnostic:**
   ```bash
   sudo /tmp/server_diagnostic.sh > diagnostic.txt
   ```

2. **Get the logs:**
   ```bash
   sudo journalctl -u odoo -n 100 > logs.txt
   ```

3. **Check config:**
   ```bash
   cat /etc/odoo/odoo.conf > config.txt
   ```

4. **Share these 3 files** along with the exact error message you see

## 📞 Support Information

- **Server IP:** 75.119.141.141
- **Odoo Port:** 8070 (18.0)
- **Existing Port:** 8069 (17.0)
- **Module Name:** pos_demo
- **Database:** pharmacy_kenya

## 🎓 Understanding the Deployment

```
GitHub Repo → Server → Odoo Config → Database → Browser
     │            │          │            │          │
     └──clone────>│          │            │          │
                  └─addons───>│            │          │
                              └──connects─>│          │
                                           └─serves──>│
```

**Key Point:** The code from GitHub needs to be in the `addons_path` configured in Odoo's config file.

## 🔐 Security Reminders

- Change default passwords in `odoo18_server.conf`
- Use strong database passwords
- Change admin_passwd (master password)
- Set up firewall rules
- Consider using Nginx reverse proxy
- Enable HTTPS for production

## 📚 Additional Resources

- **Odoo Documentation:** https://www.odoo.com/documentation/18.0/
- **Ubuntu Server Guide:** https://ubuntu.com/server/docs
- **PostgreSQL Docs:** https://www.postgresql.org/docs/

---

**Last Updated:** January 8, 2026  
**For:** Kenya Pharmacy System Deployment  
**Server:** 75.119.141.141:8070
