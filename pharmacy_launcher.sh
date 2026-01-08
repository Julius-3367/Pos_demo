#!/bin/bash
################################################################################
# KENYA PHARMACY SYSTEM - EASY LAUNCHER
# Quick start script with health checks
################################################################################

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ODOO_DIR="/opt/odoo/odoo"
DATABASE="pharmacy_kenya"
PORT="8069"
LOG_FILE="$HOME/odoo_pharmacy.log"
ERROR_LOG="$HOME/odoo_error.log"
PID_FILE="$HOME/.odoo_pharmacy.pid"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo "================================================================================"
echo "🇰🇪 KENYA PHARMACY SYSTEM - LAUNCHER"
echo "================================================================================"
echo ""

# Function to check if Odoo is running
check_odoo_running() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p $PID > /dev/null 2>&1; then
            return 0
        else
            rm -f "$PID_FILE"
            return 1
        fi
    fi
    return 1
}

# Function to check PostgreSQL
check_postgres() {
    echo -n "Checking PostgreSQL... "
    if systemctl is-active --quiet postgresql 2>/dev/null || pgrep -x postgres > /dev/null; then
        echo -e "${GREEN}✓ Running${NC}"
        return 0
    else
        echo -e "${RED}✗ Not running${NC}"
        echo "  Starting PostgreSQL..."
        sudo systemctl start postgresql 2>/dev/null || sudo service postgresql start 2>/dev/null
        sleep 2
        if systemctl is-active --quiet postgresql 2>/dev/null || pgrep -x postgres > /dev/null; then
            echo -e "  ${GREEN}✓ PostgreSQL started${NC}"
            return 0
        else
            echo -e "  ${RED}✗ Failed to start PostgreSQL${NC}"
            return 1
        fi
    fi
}

# Function to check if port is available
check_port() {
    echo -n "Checking port $PORT... "
    if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo -e "${YELLOW}⚠ Port in use${NC}"
        return 1
    else
        echo -e "${GREEN}✓ Available${NC}"
        return 0
    fi
}

# Function to check database
check_database() {
    echo -n "Checking database '$DATABASE'... "
    if sudo -u postgres psql -lqt 2>/dev/null | cut -d \| -f 1 | grep -qw "$DATABASE"; then
        echo -e "${GREEN}✓ Exists${NC}"
        return 0
    else
        echo -e "${RED}✗ Not found${NC}"
        return 1
    fi
}

# Function to start Odoo
start_odoo() {
    echo ""
    echo "🚀 Starting Kenya Pharmacy System..."
    echo "────────────────────────────────────────────────────────────────────────────"
    
    # Check prerequisites
    if ! check_postgres; then
        echo -e "${RED}Cannot start: PostgreSQL not available${NC}"
        exit 1
    fi
    
    if ! check_database; then
        echo -e "${RED}Cannot start: Database '$DATABASE' not found${NC}"
        echo "  Create database first or use correct database name"
        exit 1
    fi
    
    # Check if already running
    if check_odoo_running; then
        echo -e "${YELLOW}⚠ Odoo is already running (PID: $(cat $PID_FILE))${NC}"
        echo ""
        show_status
        exit 0
    fi
    
    # Kill any existing Odoo processes
    echo "Cleaning up any stale processes..."
    pkill -9 -f "odoo-bin.*pharmacy_kenya" 2>/dev/null
    pkill -9 -f "odoo-bin.*$DATABASE" 2>/dev/null
    sleep 1
    
    # Check port again
    if ! check_port; then
        echo -e "${YELLOW}Waiting for port to be released...${NC}"
        sleep 3
        if ! check_port; then
            PID_ON_PORT=$(lsof -ti:$PORT)
            echo -e "${RED}Port $PORT still in use by process $PID_ON_PORT${NC}"
            read -p "Kill process on port $PORT? (y/n) " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                kill -9 $PID_ON_PORT
                sleep 2
            else
                exit 1
            fi
        fi
    fi
    
    # Start Odoo
    echo "Starting Odoo server..."
    cd "$ODOO_DIR"
    
    nohup python3 odoo-bin \
        --addons-path=addons,addons/custom \
        -d "$DATABASE" \
        --http-port=$PORT \
        --log-level=info \
        > "$LOG_FILE" 2> "$ERROR_LOG" &
    
    ODOO_PID=$!
    echo $ODOO_PID > "$PID_FILE"
    
    echo -e "Process started with PID: ${BLUE}$ODOO_PID${NC}"
    echo ""
    
    # Wait for Odoo to start
    echo -n "Waiting for Odoo to initialize"
    for i in {1..30}; do
        sleep 1
        echo -n "."
        if curl -s http://localhost:$PORT/web/database/selector > /dev/null 2>&1; then
            echo ""
            echo -e "${GREEN}✓ Odoo started successfully!${NC}"
            echo ""
            show_status
            return 0
        fi
    done
    
    echo ""
    echo -e "${RED}✗ Odoo failed to start within 30 seconds${NC}"
    echo "Check logs:"
    echo "  tail -f $ERROR_LOG"
    return 1
}

# Function to stop Odoo
stop_odoo() {
    echo ""
    echo "🛑 Stopping Kenya Pharmacy System..."
    echo "────────────────────────────────────────────────────────────────────────────"
    
    if check_odoo_running; then
        PID=$(cat "$PID_FILE")
        echo "Stopping Odoo (PID: $PID)..."
        kill -TERM $PID 2>/dev/null
        
        # Wait for graceful shutdown
        echo -n "Waiting for graceful shutdown"
        for i in {1..10}; do
            if ! ps -p $PID > /dev/null 2>&1; then
                echo ""
                echo -e "${GREEN}✓ Odoo stopped successfully${NC}"
                rm -f "$PID_FILE"
                return 0
            fi
            sleep 1
            echo -n "."
        done
        
        # Force kill if still running
        echo ""
        echo "Force stopping..."
        kill -9 $PID 2>/dev/null
        rm -f "$PID_FILE"
        echo -e "${GREEN}✓ Odoo stopped (forced)${NC}"
    else
        echo -e "${YELLOW}⚠ Odoo is not running${NC}"
    fi
    
    # Clean up any remaining processes
    pkill -9 -f "odoo-bin.*pharmacy_kenya" 2>/dev/null
    pkill -9 -f "odoo-bin.*$DATABASE" 2>/dev/null
    
    echo ""
}

# Function to restart Odoo
restart_odoo() {
    echo ""
    echo "🔄 Restarting Kenya Pharmacy System..."
    echo "────────────────────────────────────────────────────────────────────────────"
    stop_odoo
    sleep 2
    start_odoo
}

# Function to show status
show_status() {
    echo "════════════════════════════════════════════════════════════════════════════"
    echo "📊 SYSTEM STATUS"
    echo "════════════════════════════════════════════════════════════════════════════"
    
    # Odoo status
    echo -n "Odoo Service: "
    if check_odoo_running; then
        PID=$(cat "$PID_FILE")
        echo -e "${GREEN}✓ Running${NC} (PID: $PID)"
    else
        echo -e "${RED}✗ Stopped${NC}"
    fi
    
    # PostgreSQL status
    echo -n "PostgreSQL: "
    if systemctl is-active --quiet postgresql 2>/dev/null || pgrep -x postgres > /dev/null; then
        echo -e "${GREEN}✓ Running${NC}"
    else
        echo -e "${RED}✗ Stopped${NC}"
    fi
    
    # Database status
    echo -n "Database: "
    if check_database; then
        DB_SIZE=$(sudo -u postgres psql -t -c "SELECT pg_size_pretty(pg_database_size('$DATABASE'));" 2>/dev/null | xargs)
        echo -e "${GREEN}✓ $DATABASE${NC} ($DB_SIZE)"
    else
        echo -e "${RED}✗ Not found${NC}"
    fi
    
    # Port status
    echo -n "Port $PORT: "
    if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo -e "${GREEN}✓ In use${NC}"
    else
        echo -e "${YELLOW}○ Available${NC}"
    fi
    
    echo ""
    echo "────────────────────────────────────────────────────────────────────────────"
    
    if check_odoo_running; then
        echo "🌐 ACCESS:"
        echo "  URL: http://localhost:$PORT"
        echo "  Database: $DATABASE"
        echo "  Admin: admin / admin"
        echo "  Cashiers: [username] / cashier123"
        echo ""
        echo "📱 QUICK ACCESS:"
        echo "  Main: http://localhost:$PORT/web"
        echo "  POS: http://localhost:$PORT/pos/web"
        echo ""
        echo "📝 LOGS:"
        echo "  Main: tail -f $LOG_FILE"
        echo "  Errors: tail -f $ERROR_LOG"
    else
        echo "💡 TIP: Run '$0 start' to start the system"
    fi
    
    echo "════════════════════════════════════════════════════════════════════════════"
}

# Function to show logs
show_logs() {
    if [ ! -f "$LOG_FILE" ]; then
        echo "No logs found at $LOG_FILE"
        exit 1
    fi
    
    echo "Showing last 50 lines of log (Ctrl+C to exit):"
    echo "────────────────────────────────────────────────────────────────────────────"
    tail -50 "$LOG_FILE"
    echo ""
    echo "For live logs, run: tail -f $LOG_FILE"
}

# Function to run health check
health_check() {
    echo ""
    echo "🏥 Running Health Check..."
    echo "────────────────────────────────────────────────────────────────────────────"
    
    python3 "$SCRIPT_DIR/health_check.py"
}

# Main menu
case "${1:-}" in
    start)
        start_odoo
        ;;
    stop)
        stop_odoo
        ;;
    restart)
        restart_odoo
        ;;
    status)
        show_status
        ;;
    logs)
        show_logs
        ;;
    health)
        health_check
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status|logs|health}"
        echo ""
        echo "Commands:"
        echo "  start   - Start the Kenya Pharmacy System"
        echo "  stop    - Stop the system"
        echo "  restart - Restart the system"
        echo "  status  - Show system status"
        echo "  logs    - Show recent logs"
        echo "  health  - Run comprehensive health check"
        echo ""
        echo "Current status:"
        show_status
        exit 1
        ;;
esac
