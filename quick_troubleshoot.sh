#!/bin/bash

# Quick Deployment Troubleshooter
# Upload this file to your server and run it

echo "================================================"
echo "KENYA PHARMACY - DEPLOYMENT TROUBLESHOOTER"
echo "Server: 75.119.141.141:8070"
echo "================================================"
echo ""

# Check 1: Is the code there?
echo "✓ Step 1: Checking if code is deployed..."
if [ -d "/opt/odoo/odoo/addons/custom/pos_demo" ]; then
    echo "  ✓ Module code found"
else
    echo "  ✗ Module code NOT found!"
    echo "  Run: cd /opt/odoo/odoo/addons && git clone YOUR_GITHUB_REPO custom"
    exit 1
fi

# Check 2: Is Odoo running?
echo ""
echo "✓ Step 2: Checking if Odoo is running..."
if pgrep -f "odoo-bin" > /dev/null; then
    echo "  ✓ Odoo process is running"
    PID=$(pgrep -f "odoo-bin")
    echo "  PID: $PID"
else
    echo "  ✗ Odoo is NOT running!"
    echo "  Run: sudo systemctl start odoo"
    exit 1
fi

# Check 3: Is port 8070 listening?
echo ""
echo "✓ Step 3: Checking port 8070..."
if netstat -tln 2>/dev/null | grep -q ":8070 " || ss -tln 2>/dev/null | grep -q ":8070 "; then
    echo "  ✓ Port 8070 is listening"
else
    echo "  ✗ Port 8070 is NOT listening!"
    echo "  Check Odoo config: grep http_port /etc/odoo/odoo.conf"
    exit 1
fi

# Check 4: Can we connect?
echo ""
echo "✓ Step 4: Testing HTTP connection..."
if curl -s -f http://127.0.0.1:8070/web > /dev/null 2>&1; then
    echo "  ✓ Odoo is responding on port 8070"
else
    echo "  ✗ Odoo is not responding properly"
    echo "  Check logs: sudo journalctl -u odoo -n 50"
fi

# Check 5: Recent errors?
echo ""
echo "✓ Step 5: Checking for recent errors..."
if [ -f "/var/log/odoo/odoo.log" ]; then
    ERRORS=$(tail -100 /var/log/odoo/odoo.log | grep -i "error\|exception\|traceback" | wc -l)
    if [ $ERRORS -gt 0 ]; then
        echo "  ⚠ Found $ERRORS error lines in last 100 log entries"
        echo "  Recent errors:"
        tail -100 /var/log/odoo/odoo.log | grep -i "error\|exception" | tail -5
    else
        echo "  ✓ No recent errors in logs"
    fi
else
    echo "  ⚠ Log file not found at standard location"
fi

echo ""
echo "================================================"
echo "QUICK COMMANDS TO TRY:"
echo "================================================"
echo ""
echo "1. View real-time logs:"
echo "   sudo journalctl -u odoo -f"
echo ""
echo "2. Restart Odoo:"
echo "   sudo systemctl restart odoo"
echo ""
echo "3. Check Odoo status:"
echo "   sudo systemctl status odoo"
echo ""
echo "4. Test access:"
echo "   curl http://127.0.0.1:8070/web"
echo ""
echo "5. Update module:"
echo "   # Login to Odoo web interface"
echo "   # Go to Apps menu"
echo "   # Update Apps List"
echo "   # Search for 'pos_demo'"
echo "   # Click Install/Upgrade"
echo ""
echo "================================================"
echo "COMMON ISSUES & FIXES:"
echo "================================================"
echo ""
echo "Issue: Module not found"
echo "Fix: Ensure addons_path includes custom folder"
echo "  grep addons_path /etc/odoo/odoo.conf"
echo ""
echo "Issue: Database error"
echo "Fix: Ensure database user has permissions"
echo "  sudo -u postgres psql -c \"CREATE USER odoo WITH PASSWORD 'password';\""
echo "  sudo -u postgres psql -c \"ALTER USER odoo CREATEDB;\""
echo ""
echo "Issue: Permission denied"
echo "Fix: Set correct ownership"
echo "  sudo chown -R odoo:odoo /opt/odoo/odoo/addons/custom"
echo ""
echo "Issue: Port conflict"
echo "Fix: Check if another service uses 8070"
echo "  sudo netstat -tlnp | grep 8070"
echo ""
echo "================================================"
