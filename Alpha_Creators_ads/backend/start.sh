#!/bin/bash

# Alpha Creators Ads - Quick Start Script
# This script helps set up and run the backend system

set -e  # Exit on any error

echo "🚀 Alpha Creators Ads - Backend Setup"
echo "======================================"

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check if port is in use
port_in_use() {
    lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null 2>&1
}

# Check prerequisites
echo "📋 Checking prerequisites..."

if ! command_exists docker; then
    echo "❌ Docker is not installed. Please install Docker first."
    echo "   Visit: https://docs.docker.com/get-docker/"
    exit 1
fi

if ! command_exists docker-compose; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    echo "   Visit: https://docs.docker.com/compose/install/"
    exit 1
fi

echo "✅ Prerequisites check passed"

# Check if .env file exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env file with your API keys and configurations"
    echo "   Example: nano .env"
    echo ""
    echo "Required API keys:"
    echo "   - TWITTER_BEARER_TOKEN"
    echo "   - OPENAI_API_KEY or ANTHROPIC_API_KEY"
    echo "   - Other social media and advertising platform tokens"
    echo ""
    read -p "Press Enter to continue after updating .env file..."
fi

# Check for port conflicts
echo "🔍 Checking for port conflicts..."
PORTS=(5432 6379 27017 7474 7687 8000 8001 8086 9092)
CONFLICTS=()

for port in "${PORTS[@]}"; do
    if port_in_use $port; then
        CONFLICTS+=($port)
    fi
done

if [ ${#CONFLICTS[@]} -gt 0 ]; then
    echo "⚠️  Warning: The following ports are in use: ${CONFLICTS[*]}"
    echo "   This might cause conflicts with the services."
    read -p "Do you want to continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p logs data models monitoring/grafana monitoring/prometheus

# Start services based on user choice
echo "🛠️  Choose startup mode:"
echo "1) Full stack (all services including databases)"
echo "2) API only (requires external databases)" 
echo "3) Development mode (API + essential services)"

read -p "Enter choice (1-3): " -n 1 -r
echo

case $REPLY in
    1)
        echo "🚀 Starting full stack..."
        docker-compose up -d
        ;;
    2)
        echo "🚀 Starting API only..."
        docker-compose up -d api
        ;;
    3)
        echo "🚀 Starting development mode..."
        docker-compose up -d postgres redis mongo api
        ;;
    *)
        echo "❌ Invalid choice"
        exit 1
        ;;
esac

# Wait for services to start
echo "⏳ Waiting for services to start..."
sleep 10

# Check service health
echo "🏥 Checking service health..."

# Function to check if service is healthy
check_service() {
    local service=$1
    local url=$2
    local name=$3
    
    if curl -s -o /dev/null -w "%{http_code}" "$url" | grep -q "200\|404"; then
        echo "✅ $name is healthy"
        return 0
    else
        echo "❌ $name is not responding"
        return 1
    fi
}

# Check API health
if check_service "api" "http://localhost:8000/health" "API"; then
    API_HEALTHY=true
else
    API_HEALTHY=false
fi

# Show service status
echo ""
echo "🎯 Service Status:"
echo "=================="
docker-compose ps

echo ""
echo "🌐 Access URLs:"
echo "==============="
echo "API Documentation: http://localhost:8000/api/docs"
echo "API Health Check:  http://localhost:8000/health"
echo "Prometheus:        http://localhost:9090 (if started)"
echo "Grafana:          http://localhost:3000 (if started)"
echo "Neo4j Browser:    http://localhost:7474 (if started)"

if [ "$API_HEALTHY" = true ]; then
    echo ""
    echo "🎉 Setup completed successfully!"
    echo ""
    echo "Next steps:"
    echo "1. Visit http://localhost:8000/api/docs to explore the API"
    echo "2. Check logs: docker-compose logs -f api"
    echo "3. Monitor services: docker-compose ps"
    echo ""
    echo "To stop services: docker-compose down"
    echo "To view logs: docker-compose logs -f"
    echo "To restart: docker-compose restart"
else
    echo ""
    echo "⚠️  Setup completed but API is not healthy"
    echo "Check logs with: docker-compose logs api"
    echo ""
    echo "Common issues:"
    echo "- Missing or invalid API keys in .env file"
    echo "- Database connection issues"
    echo "- Port conflicts"
fi

echo ""
echo "📚 For more information:"
echo "- README.md for detailed documentation"
echo "- .env.example for configuration options"
echo "- docker-compose logs for troubleshooting"
