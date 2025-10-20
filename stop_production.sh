#!/bin/bash

# CapCutAPI Production Server Stop Script

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
APP_NAME="CapCutAPI"
PID_FILE="/tmp/capcut_api.pid"

echo -e "${BLUE}=== Stopping $APP_NAME Production Server ===${NC}"

# Check if PID file exists
if [[ ! -f "$PID_FILE" ]]; then
    echo -e "${YELLOW}PID file not found. $APP_NAME may not be running.${NC}"
    echo -e "${BLUE}Checking for running Gunicorn processes...${NC}"

    # Look for Gunicorn processes
    GUNICORN_PIDS=$(pgrep -f "gunicorn.*capcut_server" || true)
    if [[ -n "$GUNICORN_PIDS" ]]; then
        echo -e "${YELLOW}Found Gunicorn processes: $GUNICORN_PIDS${NC}"
        echo -e "${YELLOW}Attempting to terminate them...${NC}"
        echo "$GUNICORN_PIDS" | xargs kill -TERM
        sleep 2
        echo "$GUNICORN_PIDS" | xargs kill -KILL 2>/dev/null || true
        echo -e "${GREEN}✓ Gunicorn processes terminated${NC}"
    else
        echo -e "${GREEN}✓ No Gunicorn processes found${NC}"
    fi
    exit 0
fi

# Read PID from file
PID=$(cat "$PID_FILE")

# Check if process is running
if ! ps -p "$PID" > /dev/null 2>&1; then
    echo -e "${YELLOW}Process with PID $PID is not running.${NC}"
    echo -e "${BLUE}Removing stale PID file...${NC}"
    rm -f "$PID_FILE"
    exit 0
fi

echo -e "${BLUE}Stopping $APP_NAME (PID: $PID)...${NC}"

# Send SIGTERM signal for graceful shutdown
kill -TERM "$PID"

# Wait for graceful shutdown
echo -e "${BLUE}Waiting for graceful shutdown...${NC}"
for i in {1..10}; do
    if ! ps -p "$PID" > /dev/null 2>&1; then
        echo -e "${GREEN}✓ $APP_NAME stopped gracefully${NC}"
        rm -f "$PID_FILE"
        exit 0
    fi
    echo -n "."
    sleep 1
done

# If still running, force kill
echo
echo -e "${YELLOW}Graceful shutdown timeout. Force killing...${NC}"
if kill -KILL "$PID" 2>/dev/null; then
    echo -e "${GREEN}✓ $APP_NAME force killed${NC}"
    rm -f "$PID_FILE"
else
    echo -e "${RED}✗ Failed to kill process $PID${NC}"
    exit 1
fi