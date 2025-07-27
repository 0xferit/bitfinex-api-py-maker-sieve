#!/bin/bash

# Development setup script for bitfinex-api-py-postonly-wrapper

set -e

echo "🔧 Setting up development environment..."

# Check if we're in a git repository
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo "❌ Error: Not in a git repository"
    echo "Please run this script from the root of your git repository"
    exit 1
fi

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is not installed or not in PATH"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install development dependencies
echo "📦 Installing development dependencies..."
pip install -e ".[dev]"

# Install additional security tools
echo "🔒 Installing security tools..."
pip install safety bandit

echo ""
echo "✅ Development environment setup complete!"
echo ""
echo "To activate the virtual environment in the future:"
echo "  source venv/bin/activate"
echo ""
echo "To install the pre-commit hook:"
echo "  ./scripts/setup-precommit.sh"
echo ""
echo "To run tests:"
echo "  pytest test_postonly.py"
echo ""
echo "To run linting:"
echo "  flake8 bfx_postonly/ examples/"
echo "  black --check bfx_postonly/ examples/"
echo "  isort --check-only bfx_postonly/ examples/"
echo "  mypy bfx_postonly/" 