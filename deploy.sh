#!/bin/bash

# JioSaavn Bot Deployment Script
# Created by Ashlynn

set -e

echo "🚀 JioSaavn Bot Deployment Script"
echo "=================================="

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

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    print_error "Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Set docker-compose command
if command -v docker-compose &> /dev/null; then
    DOCKER_COMPOSE_CMD="docker-compose"
else
    DOCKER_COMPOSE_CMD="docker compose"
fi

print_status "Using Docker Compose command: $DOCKER_COMPOSE_CMD"

# Check if .env file exists
if [ ! -f .env ]; then
    print_warning ".env file not found. Creating template..."
    cat > .env << EOF
# Telegram Bot Configuration
API_ID=your_api_id
API_HASH=your_api_hash
BOT_TOKEN=your_bot_token
OWNER_ID=your_telegram_user_id

# Database Configuration
DATABASE_URL=mongodb://admin:password@mongodb:27017/jiosaavn?authSource=admin

# Server Configuration
PORT=80

# MongoDB Configuration (for local development)
MONGO_USERNAME=admin
MONGO_PASSWORD=password
EOF
    print_warning "Please edit the .env file with your configuration before running again."
    print_status "You can get your API_ID and API_HASH from https://my.telegram.org"
    print_status "You can get your BOT_TOKEN from @BotFather on Telegram"
    print_status "You can get your OWNER_ID from @userinfobot on Telegram"
    exit 1
fi

# Source environment variables
source .env

# Validate required environment variables
REQUIRED_VARS=("API_ID" "API_HASH" "BOT_TOKEN" "OWNER_ID" "DATABASE_URL")
MISSING_VARS=()

for var in "${REQUIRED_VARS[@]}"; do
    if [ -z "${!var}" ] || [ "${!var}" = "your_${var,,}" ] || [ "${!var}" = "your_api_id" ] || [ "${!var}" = "your_api_hash" ] || [ "${!var}" = "your_bot_token" ] || [ "${!var}" = "your_telegram_user_id" ]; then
        MISSING_VARS+=($var)
    fi
done

if [ ${#MISSING_VARS[@]} -ne 0 ]; then
    print_error "The following environment variables are missing or have default values:"
    for var in "${MISSING_VARS[@]}"; do
        echo -e "  ${RED}✗${NC} $var"
    done
    print_status "Please update your .env file with the correct values."
    exit 1
fi

print_success "Environment validation passed!"

# Deployment mode selection
echo ""
echo "Select deployment mode:"
echo "1) Production (bot only)"
echo "2) Development (bot + local MongoDB)"
echo "3) Build only"
echo "4) Stop and remove containers"
echo "5) View logs"
echo "6) Restart bot"

read -p "Enter your choice (1-6): " choice

case $choice in
    1)
        print_status "Deploying in production mode..."
        $DOCKER_COMPOSE_CMD up -d --build jiosaavn-bot
        ;;
    2)
        print_status "Deploying in development mode with local MongoDB..."
        $DOCKER_COMPOSE_CMD --profile local up -d --build
        ;;
    3)
        print_status "Building Docker image..."
        $DOCKER_COMPOSE_CMD build
        ;;
    4)
        print_status "Stopping and removing containers..."
        $DOCKER_COMPOSE_CMD down
        print_success "Containers stopped and removed!"
        exit 0
        ;;
    5)
        print_status "Showing bot logs (press Ctrl+C to exit)..."
        $DOCKER_COMPOSE_CMD logs -f jiosaavn-bot
        exit 0
        ;;
    6)
        print_status "Restarting bot..."
        $DOCKER_COMPOSE_CMD restart jiosaavn-bot
        ;;
    *)
        print_error "Invalid choice. Exiting."
        exit 1
        ;;
esac

# Wait for services to start
print_status "Waiting for services to start..."
sleep 10

# Check if bot is running
if $DOCKER_COMPOSE_CMD ps | grep -q "jiosaavn-bot.*Up"; then
    print_success "🎉 JioSaavn Bot is running successfully!"
    
    # Display service information
    echo ""
    echo "📊 Service Information:"
    echo "======================="
    echo -e "Bot Status: ${GREEN}Running${NC}"
    echo -e "Web Interface: ${BLUE}http://localhost:${PORT:-80}${NC}"
    echo -e "API Endpoint: ${BLUE}http://localhost:${PORT:-80}/api/stats${NC}"
    
    if [ "$choice" = "2" ]; then
        echo -e "MongoDB: ${GREEN}Running${NC} (localhost:27017)"
    fi
    
    echo ""
    echo "📝 Useful Commands:"
    echo "==================="
    echo "View logs:          $DOCKER_COMPOSE_CMD logs -f jiosaavn-bot"
    echo "Stop bot:           $DOCKER_COMPOSE_CMD stop jiosaavn-bot"
    echo "Restart bot:        $DOCKER_COMPOSE_CMD restart jiosaavn-bot"
    echo "Update bot:         $DOCKER_COMPOSE_CMD up -d --build jiosaavn-bot"
    echo "Remove all:         $DOCKER_COMPOSE_CMD down"
    
    echo ""
    print_status "Check the web interface to see the beautiful dashboard!"
    
else
    print_error "Failed to start JioSaavn Bot. Check logs:"
    $DOCKER_COMPOSE_CMD logs jiosaavn-bot
    exit 1
fi

print_success "Deployment completed successfully! 🎉"
