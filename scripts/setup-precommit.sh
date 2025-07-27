#!/bin/bash

# Setup script for pre-commit hook

set -e

echo "🔧 Setting up pre-commit hook for bitfinex-api-py-postonly-wrapper..."

# Check if we're in a git repository
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo "❌ Error: Not in a git repository"
    echo "Please run this script from the root of your git repository"
    exit 1
fi

# Check if the pre-commit hook already exists
if [ -f .git/hooks/pre-commit ]; then
    echo "⚠️  Pre-commit hook already exists"
    read -p "Do you want to overwrite it? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Setup cancelled"
        exit 0
    fi
fi

# Copy the pre-commit hook
cp scripts/pre-commit .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit

echo "✅ Pre-commit hook installed successfully!"
echo ""
echo "The pre-commit hook will now run the following checks before each commit:"
echo "  • flake8 linting"
echo "  • black code formatting"
echo "  • isort import sorting"
echo "  • mypy type checking"
echo "  • pytest tests with coverage"
echo "  • safety and bandit security checks"
echo ""
echo "To test the hook, try making a commit:"
echo "  git add . && git commit -m 'test: test pre-commit hook'"
echo ""
echo "To skip the hook for a specific commit (not recommended):"
echo "  git commit --no-verify -m 'your message'" 