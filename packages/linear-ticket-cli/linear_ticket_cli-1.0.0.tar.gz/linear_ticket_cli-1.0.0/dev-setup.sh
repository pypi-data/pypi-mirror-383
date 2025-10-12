#!/bin/bash

# Linear Ticket Manager CLI - Development Setup Script
# This script helps contributors set up their development environment quickly

set -e  # Exit on any error

echo "🎫 Linear Ticket Manager CLI - Development Setup"
echo "================================================"
echo ""

# Check Python version
echo "📋 Checking Python version..."
python_version=$(python3 --version 2>/dev/null || echo "Python not found")
echo "Found: $python_version"

if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not found. Please install Python 3.7 or higher."
    exit 1
fi

# Create virtual environment
echo ""
echo "🔧 Setting up virtual environment..."
if [ -d "venv" ]; then
    echo "Virtual environment already exists, using existing one."
else
    echo "Creating new virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies and package
echo ""
echo "📦 Installing dependencies and package in development mode..."
pip install --upgrade pip
pip install -e .

echo ""
echo "✅ Development environment setup complete!"
echo ""
echo "🚀 Next steps:"
echo "1. Set up your Linear API token:"
echo "   export LINEAR_API_TOKEN=\"your_linear_api_token_here\""
echo "   # Or copy .env.example to .env and edit it"
echo ""
echo "2. Test the installation:"
echo "   linear --teams"
echo ""
echo "3. Start contributing:"
echo "   - Review CONTRIBUTING.md for detailed guidelines"
echo "   - Check out the examples/ directory for usage patterns"
echo "   - Run 'linear --help' for full command reference"
echo ""
echo "💡 To activate the virtual environment in future sessions:"
echo "   source venv/bin/activate"
echo ""
echo "Happy contributing! 🎉"