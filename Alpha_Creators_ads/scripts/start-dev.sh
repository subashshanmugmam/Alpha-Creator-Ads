#!/bin/bash

# Alpha Creators Ads - Development Startup Script
# This script starts all components in development mode

set -e

echo "🚀 Alpha Creators Ads - Starting Development Environment"
echo "========================================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
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

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    print_error "Docker is not running. Please start Docker first."
    exit 1
fi

# Check if Docker Compose is available
if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Get the script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

print_status "Project root: $PROJECT_ROOT"

# Step 1: Start Database Services
print_status "Step 1: Starting Database Services..."
cd "$PROJECT_ROOT/database"

if [ ! -f .env ]; then
    print_warning "Database .env file not found. Creating from template..."
    cp .env.example .env
    print_warning "Please edit database/.env with your secure passwords before production use!"
fi

# Start databases in the background
docker-compose up -d

# Wait for databases to be ready
print_status "Waiting for databases to be ready..."
sleep 10

# Check database health
print_status "Checking database health..."
for i in {1..30}; do
    if docker-compose exec -T postgres pg_isready -U alphaads_user -d alphaads > /dev/null 2>&1; then
        print_success "PostgreSQL is ready"
        break
    fi
    if [ $i -eq 30 ]; then
        print_error "PostgreSQL failed to start within 30 attempts"
        exit 1
    fi
    sleep 2
done

for i in {1..30}; do
    if docker-compose exec -T redis redis-cli ping > /dev/null 2>&1; then
        print_success "Redis is ready"
        break
    fi
    if [ $i -eq 30 ]; then
        print_error "Redis failed to start within 30 attempts"
        exit 1
    fi
    sleep 2
done

print_success "Database services are running!"

# Step 2: Start Backend API
print_status "Step 2: Starting Backend API..."
cd "$PROJECT_ROOT/backend"

if [ ! -f .env ]; then
    print_warning "Backend .env file not found. Creating from template..."
    cp .env.example .env
    print_warning "Please edit backend/.env with your API keys!"
fi

# Check if Python virtual environment exists
if [ ! -d "venv" ]; then
    print_status "Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment and install dependencies
print_status "Installing Python dependencies..."
source venv/bin/activate
pip install -r requirements.txt > /dev/null 2>&1

# Start backend in the background
print_status "Starting FastAPI backend server..."
nohup uvicorn main:app --host 0.0.0.0 --port 8000 --reload > backend.log 2>&1 &
BACKEND_PID=$!

# Wait for backend to be ready
print_status "Waiting for backend to be ready..."
for i in {1..30}; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        print_success "Backend API is ready"
        break
    fi
    if [ $i -eq 30 ]; then
        print_error "Backend failed to start within 30 attempts"
        print_error "Check backend.log for errors"
        exit 1
    fi
    sleep 2
done

# Step 3: Start Frontend Application
print_status "Step 3: Starting Frontend Application..."
cd "$PROJECT_ROOT/frontend"

if [ ! -f .env ]; then
    print_warning "Frontend .env file not found. Creating from template..."
    cp .env.example .env
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    print_error "Node.js is not installed. Please install Node.js 18+ first."
    exit 1
fi

# Install dependencies if node_modules doesn't exist
if [ ! -d "node_modules" ]; then
    print_status "Installing Node.js dependencies..."
    npm install
fi

# Start frontend development server
print_status "Starting Frontend development server..."
npm run dev &
FRONTEND_PID=$!

# Wait for frontend to be ready
print_status "Waiting for frontend to be ready..."
for i in {1..30}; do
    if curl -s http://localhost:5173 > /dev/null 2>&1; then
        print_success "Frontend application is ready"
        break
    fi
    if [ $i -eq 30 ]; then
        print_error "Frontend failed to start within 30 attempts"
        exit 1
    fi
    sleep 2
done

# Success message
echo ""
echo "🎉 Alpha Creators Ads Development Environment Started Successfully!"
echo "=================================================================="
echo ""
echo "📱 Frontend Application:    http://localhost:5173"
echo "⚙️  Backend API:             http://localhost:8000"
echo "📚 API Documentation:       http://localhost:8000/api/docs"
echo "🗄️ PostgreSQL Admin:        http://localhost:5050"
echo "🗄️ MongoDB Admin:           http://localhost:8081"
echo "🕸️ Neo4j Browser:           http://localhost:7474"
echo "📊 InfluxDB:                http://localhost:8086"
echo "🔍 Redis Insight:           http://localhost:8001"
echo ""
echo "🛑 To stop all services, run: ./scripts/stop-dev.sh"
echo ""

# Save process IDs for cleanup
echo $BACKEND_PID > backend.pid
echo $FRONTEND_PID > frontend.pid

print_success "All services are running! Happy coding! 🚀"
