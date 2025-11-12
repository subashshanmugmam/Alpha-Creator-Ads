#!/bin/bash

# Alpha Creators Ads - Development Stop Script
# This script stops all development services

set -e

echo "🛑 Alpha Creators Ads - Stopping Development Environment"
echo "========================================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Get the script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

print_status "Project root: $PROJECT_ROOT"

# Stop Frontend
print_status "Stopping Frontend application..."
cd "$PROJECT_ROOT"
if [ -f frontend.pid ]; then
    FRONTEND_PID=$(cat frontend.pid)
    if ps -p $FRONTEND_PID > /dev/null; then
        kill $FRONTEND_PID
        print_success "Frontend stopped"
    else
        print_warning "Frontend process not found"
    fi
    rm frontend.pid
else
    print_warning "Frontend PID file not found"
fi

# Stop any remaining Node.js processes on port 5173
print_status "Stopping any remaining frontend processes..."
pkill -f "vite.*5173" || true

# Stop Backend
print_status "Stopping Backend API..."
if [ -f backend.pid ]; then
    BACKEND_PID=$(cat backend.pid)
    if ps -p $BACKEND_PID > /dev/null; then
        kill $BACKEND_PID
        print_success "Backend stopped"
    else
        print_warning "Backend process not found"
    fi
    rm backend.pid
else
    print_warning "Backend PID file not found"
fi

# Stop any remaining Python processes on port 8000
print_status "Stopping any remaining backend processes..."
pkill -f "uvicorn.*8000" || true

# Stop Database Services
print_status "Stopping Database services..."
cd "$PROJECT_ROOT/database"
docker-compose down

print_success "All database services stopped"

# Clean up log files
print_status "Cleaning up log files..."
cd "$PROJECT_ROOT/backend"
if [ -f backend.log ]; then
    rm backend.log
    print_success "Backend log cleaned"
fi

# Stop any remaining Docker containers
print_status "Stopping any remaining containers..."
docker stop $(docker ps -q --filter "name=alphaads") 2>/dev/null || true

# Show stopped services
echo ""
print_success "🎉 Alpha Creators Ads Development Environment Stopped!"
echo "======================================================"
echo ""
print_status "Stopped services:"
echo "  📱 Frontend Application (port 5173)"
echo "  ⚙️  Backend API (port 8000)"
echo "  🗄️ Database services (PostgreSQL, Redis, MongoDB, Neo4j, InfluxDB)"
echo ""
print_status "To start again, run: ./scripts/start-dev.sh"
echo ""
