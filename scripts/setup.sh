#!/bin/bash

echo "========================================="
echo "Agent Framework + Generative UI Setup"
echo "========================================="
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "Error: Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "Error: Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Create .env files from examples
echo "Creating environment files..."
if [ ! -f backend/.env ]; then
    cp backend/.env.example backend/.env
    echo "✓ Created backend/.env"
fi

if [ ! -f frontend/.env.local ]; then
    cp frontend/.env.local.example frontend/.env.local
    echo "✓ Created frontend/.env.local"
fi

# Build and start services
echo ""
echo "Building and starting services..."
docker-compose up -d --build

# Wait for Ollama to be ready
echo ""
echo "Waiting for Ollama to be ready..."
sleep 10

# Pull Ollama model
echo ""
echo "Pulling Ollama model (this may take a while)..."
docker exec agentframework-ollama ollama pull qwen2.5:latest

echo ""
echo "========================================="
echo "Setup complete!"
echo "========================================="
echo ""
echo "Services:"
echo "  - Frontend: http://localhost:3000"
echo "  - Backend API: http://localhost:8000"
echo "  - API Docs: http://localhost:8000/docs"
echo "  - Ollama: http://localhost:11434"
echo ""
echo "To view logs:"
echo "  docker-compose logs -f"
echo ""
echo "To stop services:"
echo "  docker-compose down"
echo ""
