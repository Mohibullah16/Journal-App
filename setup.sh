#!/bin/bash

# Journal App Setup Script
# This script helps you get started quickly

echo "🚀 Journal App Setup"
echo "===================="
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    echo "   Visit: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is installed
if ! docker compose version &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

echo "✅ Docker and Docker Compose are installed"
echo ""

# Check if .env exists, if not create from example
if [ ! -f .env ]; then
    if [ -f .env.example ]; then
        echo "📝 Creating .env file from template..."
        cp .env.example .env
        echo "✅ .env file created!"
        echo ""
        echo "⚠️  IMPORTANT: For production, please update the following in .env:"
        echo "   - SECRET_KEY: Change to a secure random key"
        echo "   - MONGO_INITDB_ROOT_PASSWORD: Change to a strong password"
        echo ""
    else
        echo "⚠️  No .env or .env.example found. Using default values from docker-compose.yml"
        echo ""
    fi
else
    echo "✅ .env file already exists"
    echo ""
fi

# Ask user if they want to start the application
read -p "📦 Do you want to build and start the application now? (y/n) " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "🐳 Building Docker images..."
    docker compose build
    
    echo ""
    echo "🚀 Starting services..."
    docker compose up -d
    
    echo ""
    echo "⏳ Waiting for services to be ready..."
    sleep 10
    
    echo ""
    echo "📊 Container status:"
    docker compose ps
    
    echo ""
    echo "✅ Setup complete!"
    echo ""
    echo "🌐 Your Journal App is running at: http://localhost:8000"
    echo ""
    echo "📝 Useful commands:"
    echo "   - View logs:        docker compose logs -f"
    echo "   - Stop services:    docker compose down"
    echo "   - Restart services: docker compose restart"
    echo "   - View status:      docker compose ps"
    echo ""
else
    echo ""
    echo "⏭️  Skipping application start."
    echo ""
    echo "To start manually, run:"
    echo "   docker compose up -d"
    echo ""
fi

echo "📚 For more information, check README.md and INSTALLATION_GUIDE.md"
