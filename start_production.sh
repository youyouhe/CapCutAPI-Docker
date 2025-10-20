#!/bin/bash

# CapCutAPI Production Server Startup Script

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
APP_NAME="CapCutAPI"
APP_MODULE="capcut_server:app"
GUNICORN_CONFIG="gunicorn_config.py"
PID_FILE="/tmp/capcut_api.pid"
LOG_DIR="/var/log/capcut_api"
LOG_FILE="$LOG_DIR/access.log"
ERROR_LOG_FILE="$LOG_DIR/error.log"

echo -e "${BLUE}=== CapCutAPI Production Server Startup ===${NC}"

# Check if running as root for system operations
if [[ $EUID -eq 0 ]]; then
   echo -e "${YELLOW}Running as root. Will create system directories if needed.${NC}"
   SYSTEM_INSTALL=true
else
   echo -e "${YELLOW}Running as regular user. Using user directories.${NC}"
   SYSTEM_INSTALL=false
   LOG_DIR="$HOME/logs/capcut_api"
   LOG_FILE="$LOG_DIR/access.log"
   ERROR_LOG_FILE="$LOG_DIR/error.log"
fi

# Create log directory
mkdir -p "$LOG_DIR"

# Check if required files exist
if [[ ! -f "capcut_server.py" ]]; then
    echo -e "${RED}Error: capcut_server.py not found!${NC}"
    exit 1
fi

if [[ ! -f "$GUNICORN_CONFIG" ]]; then
    echo -e "${RED}Error: $GUNICORN_CONFIG not found!${NC}"
    exit 1
fi

# Check if already running
if [[ -f "$PID_FILE" ]]; then
    PID=$(cat "$PID_FILE")
    if ps -p "$PID" > /dev/null 2>&1; then
        echo -e "${YELLOW}$APP_NAME is already running (PID: $PID)${NC}"
        echo -e "${BLUE}To stop the server, run: ./stop_production.sh${NC}"
        exit 0
    else
        echo -e "${YELLOW}Stale PID file found. Removing...${NC}"
        rm -f "$PID_FILE"
    fi
fi

# Function to start the server
start_server() {
    echo -e "${GREEN}Starting $APP_NAME production server...${NC}"
    echo -e "${BLUE}Configuration:${NC}"
    echo -e "  - Module: $APP_MODULE"
    echo -e "  - Config: $GUNICORN_CONFIG"
    echo -e "  - PID File: $PID_FILE"
    echo -e "  - Access Log: $LOG_FILE"
    echo -e "  - Error Log: $ERROR_LOG_FILE"
    echo

    # Start Gunicorn
    exec gunicorn \
        --config "$GUNICORN_CONFIG" \
        --pid "$PID_FILE" \
        --access-logfile "$LOG_FILE" \
        --error-logfile "$ERROR_LOG_FILE" \
        --daemon \
        "$APP_MODULE"
}

# Function to start in foreground (for debugging)
start_foreground() {
    echo -e "${GREEN}Starting $APP_NAME in foreground mode...${NC}"
    echo -e "${YELLOW}Press Ctrl+C to stop${NC}"
    echo

    # Start Gunicorn in foreground
    exec gunicorn \
        --config "$GUNICORN_CONFIG" \
        --access-logfile "-" \
        --error-logfile "-" \
        "$APP_MODULE"
}

# Check command line arguments
if [[ "${1:-}" == "--foreground" || "${1:-}" == "-f" ]]; then
    start_foreground
else
    start_server

    # Wait a moment and check if server started successfully
    sleep 2

    if [[ -f "$PID_FILE" ]]; then
        PID=$(cat "$PID_FILE")
        if ps -p "$PID" > /dev/null 2>&1; then
            echo -e "${GREEN}✓ $APP_NAME started successfully!${NC}"
            echo -e "${GREEN}✓ PID: $PID${NC}"
            echo -e "${GREEN}✓ Server running on: http://0.0.0.0:9002${NC}"
            echo
            echo -e "${BLUE}Useful commands:${NC}"
            echo -e "  - Check status: ps aux | grep gunicorn"
            echo -e "  - View logs: tail -f $LOG_FILE"
            echo -e "  - View errors: tail -f $ERROR_LOG_FILE"
            echo -e "  - Stop server: ./stop_production.sh"
            echo -e "  - Restart: ./restart_production.sh"
        else
            echo -e "${RED}✗ Failed to start $APP_NAME!${NC}"
            echo -e "${RED}Check the error log: $ERROR_LOG_FILE${NC}"
            exit 1
        fi
    else
        echo -e "${RED}✗ Failed to create PID file!${NC}"
        echo -e "${RED}Check the error log: $ERROR_LOG_FILE${NC}"
        exit 1
    fi
fi