#!/bin/bash

# Server Deployment Diagnostic Script
# Run this on your Ubuntu server (75.119.141.141)

echo "=========================================="
echo "ODOO 18 DEPLOYMENT DIAGNOSTIC"
echo "=========================================="
echo ""

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Variables - UPDATE THESE FOR YOUR SERVER
ODOO_PORT=8070
ODOO_USER="odoo"
ODOO_HOME="/opt/odoo"
ODOO_CONF="/etc/odoo/odoo.conf"
CUSTOM_ADDONS="$ODOO_HOME/odoo/addons/custom/pos_demo"

echo "1️⃣  CHECKING SYSTEM RESOURCES"
echo "=========================================="
echo "Memory:"
free -h
echo ""
echo "Disk Space:"
df -h / /var /opt
echo ""

echo "2️⃣  CHECKING POSTGRESQL"
echo "=========================================="
if systemctl is-active --quiet postgresql; then
    echo -e "${GREEN}✓ PostgreSQL is running${NC}"
    sudo -u postgres psql -c "SELECT version();" 2>&1 | head -1
else
    echo -e "${RED}✗ PostgreSQL is NOT running${NC}"
fi
echo ""

echo "3️⃣  CHECKING ODOO SERVICE"
echo "=========================================="
if systemctl list-units --type=service | grep -q "odoo"; then
    ODOO_SERVICE=$(systemctl list-units --type=service | grep odoo | awk '{print $1}' | head -1)
    echo "Found service: $ODOO_SERVICE"
    
    if systemctl is-active --quiet $ODOO_SERVICE; then
        echo -e "${GREEN}✓ Odoo service is running${NC}"
        systemctl status $ODOO_SERVICE --no-pager | head -10
    else
        echo -e "${RED}✗ Odoo service is NOT running${NC}"
        echo "Checking why..."
        sudo journalctl -u $ODOO_SERVICE -n 20 --no-pager
    fi
else
    echo -e "${YELLOW}⚠ No Odoo systemd service found${NC}"
    echo "Checking for running Odoo processes..."
    ps aux | grep odoo-bin | grep -v grep || echo "No Odoo processes found"
fi
echo ""

echo "4️⃣  CHECKING PORT BINDING"
echo "=========================================="
if netstat -tlnp 2>/dev/null | grep -q ":$ODOO_PORT "; then
    echo -e "${GREEN}✓ Port $ODOO_PORT is in use${NC}"
    netstat -tlnp 2>/dev/null | grep ":$ODOO_PORT "
elif ss -tlnp 2>/dev/null | grep -q ":$ODOO_PORT "; then
    echo -e "${GREEN}✓ Port $ODOO_PORT is in use${NC}"
    ss -tlnp 2>/dev/null | grep ":$ODOO_PORT "
else
    echo -e "${RED}✗ Port $ODOO_PORT is NOT in use${NC}"
    echo "Port 8070 is not being listened to - Odoo might not be running"
fi
echo ""

echo "5️⃣  CHECKING FIREWALL"
echo "=========================================="
if command -v ufw &> /dev/null; then
    sudo ufw status | grep $ODOO_PORT || echo -e "${YELLOW}⚠ Port $ODOO_PORT not explicitly allowed${NC}"
else
    echo "UFW not installed, checking iptables..."
    sudo iptables -L -n | grep $ODOO_PORT || echo "No specific rules for port $ODOO_PORT"
fi
echo ""

echo "6️⃣  CHECKING ODOO CONFIGURATION"
echo "=========================================="
if [ -f "$ODOO_CONF" ]; then
    echo -e "${GREEN}✓ Config file exists: $ODOO_CONF${NC}"
    echo "Key settings:"
    grep -E "^(http_port|addons_path|db_host|db_user|logfile)" $ODOO_CONF 2>/dev/null || echo "Could not read config"
else
    echo -e "${RED}✗ Config file NOT found: $ODOO_CONF${NC}"
    echo "Looking for config files..."
    find /etc -name "*odoo*.conf" 2>/dev/null
fi
echo ""

echo "7️⃣  CHECKING CUSTOM MODULE"
echo "=========================================="
if [ -d "$CUSTOM_ADDONS" ]; then
    echo -e "${GREEN}✓ Custom module directory exists${NC}"
    echo "Path: $CUSTOM_ADDONS"
    echo "Contents:"
    ls -lah $CUSTOM_ADDONS | head -10
    
    # Check manifest
    if [ -f "$CUSTOM_ADDONS/__manifest__.py" ]; then
        echo -e "${GREEN}✓ __manifest__.py exists${NC}"
    else
        echo -e "${RED}✗ __manifest__.py NOT found${NC}"
    fi
    
    # Check permissions
    echo "Permissions:"
    ls -ld $CUSTOM_ADDONS
else
    echo -e "${RED}✗ Custom module directory NOT found: $CUSTOM_ADDONS${NC}"
    echo "Searching for pos_demo..."
    find /opt -name "pos_demo" -type d 2>/dev/null
fi
echo ""

echo "8️⃣  CHECKING PYTHON ENVIRONMENT"
echo "=========================================="
PYTHON_BIN=$(which python3)
echo "Python: $PYTHON_BIN"
$PYTHON_BIN --version

echo "Checking for Odoo installation..."
if [ -f "$ODOO_HOME/odoo/odoo-bin" ]; then
    echo -e "${GREEN}✓ odoo-bin found at $ODOO_HOME/odoo/odoo-bin${NC}"
else
    echo -e "${YELLOW}⚠ odoo-bin not found at expected location${NC}"
    echo "Searching..."
    find /opt -name "odoo-bin" 2>/dev/null | head -3
fi
echo ""

echo "9️⃣  CHECKING LOGS"
echo "=========================================="
if [ -f "/var/log/odoo/odoo.log" ]; then
    echo "Last 10 lines of /var/log/odoo/odoo.log:"
    tail -10 /var/log/odoo/odoo.log
elif [ -f "/var/log/odoo18/odoo.log" ]; then
    echo "Last 10 lines of /var/log/odoo18/odoo.log:"
    tail -10 /var/log/odoo18/odoo.log
else
    echo -e "${YELLOW}⚠ Standard log file not found${NC}"
    echo "Checking journalctl..."
    sudo journalctl -u odoo* -n 10 --no-pager 2>/dev/null || echo "No journal entries found"
fi
echo ""

echo "🔟  CONNECTIVITY TEST"
echo "=========================================="
echo "Testing local connection to port $ODOO_PORT..."
if timeout 2 bash -c "cat < /dev/null > /dev/tcp/127.0.0.1/$ODOO_PORT" 2>/dev/null; then
    echo -e "${GREEN}✓ Can connect to localhost:$ODOO_PORT${NC}"
else
    echo -e "${RED}✗ Cannot connect to localhost:$ODOO_PORT${NC}"
fi

echo "Testing external connection..."
curl -s -I http://127.0.0.1:$ODOO_PORT/web 2>&1 | head -5 || echo "Connection failed"
echo ""

echo "=========================================="
echo "DIAGNOSTIC SUMMARY"
echo "=========================================="
echo ""
echo "🔍 Next Steps Based on Results:"
echo ""
echo "If PostgreSQL is NOT running:"
echo "  sudo systemctl start postgresql"
echo ""
echo "If Odoo service is NOT running:"
echo "  sudo systemctl start odoo"
echo "  sudo journalctl -u odoo -f  # Watch logs"
echo ""
echo "If port is NOT in use:"
echo "  Check Odoo configuration and restart"
echo "  sudo systemctl restart odoo"
echo ""
echo "If module NOT found:"
echo "  cd /opt/odoo/odoo/addons"
echo "  sudo git clone YOUR_GITHUB_REPO custom"
echo "  sudo chown -R odoo:odoo custom"
echo ""
echo "If firewall blocking:"
echo "  sudo ufw allow $ODOO_PORT/tcp"
echo ""
echo "=========================================="
echo "SHARE THE OUTPUT ABOVE FOR HELP"
echo "=========================================="
