#!/bin/bash

# CapCutAPI Production Server Restart Script

set -euo pipefail

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== Restarting CapCutAPI Production Server ===${NC}"

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Stop the server
echo -e "${BLUE}Stopping current server...${NC}"
"$SCRIPT_DIR/stop_production.sh"

# Wait a moment
sleep 1

# Start the server
echo -e "${BLUE}Starting server...${NC}"
"$SCRIPT_DIR/start_production.sh"

echo -e "${GREEN}✓ CapCutAPI restarted successfully!${NC}"