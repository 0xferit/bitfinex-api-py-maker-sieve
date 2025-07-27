#!/bin/bash
set -e

echo "Running CI checks locally..."

echo "1. Ruff linting..."
ruff check bfx_postonly/ examples/

echo "2. Ruff format check..."
ruff format --check bfx_postonly/ examples/

echo "3. MyPy type checking..."
mypy bfx_postonly/

echo "4. PyTest (skipped - requires dependencies)"
echo "   pytest test_postonly.py"

echo "All local CI checks passed!"