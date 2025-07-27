#!/usr/bin/env python3
"""
Development and maintenance scripts for the POST-ONLY wrapper
"""

import os
import sys
import subprocess
import argparse


def run_command(cmd, description=""):
    """Run a shell command and handle errors"""
    if description:
        print(f"\n🔄 {description}")
    
    print(f"Running: {cmd}")
    result = subprocess.run(cmd, shell=True)
    
    if result.returncode != 0:
        print(f"❌ Command failed with exit code {result.returncode}")
        sys.exit(1)
    else:
        print(f"✅ {description or 'Command'} completed successfully")


def setup_dev_environment():
    """Setup development environment"""
    print("🚀 Setting up development environment...")
    
    # Install in development mode with all dependencies
    run_command("pip install -e .[dev]", "Installing package in development mode")
    
    # Copy environment template
    if not os.path.exists(".env"):
        run_command("cp .env.example .env", "Creating .env file from template")
        print("📝 Please edit .env with your API credentials")
    
    print("\n✨ Development environment setup complete!")
    print("📝 Don't forget to:")
    print("   1. Edit .env with your Bitfinex API credentials")
    print("   2. Run 'python scripts/dev.py test' to verify installation")


def run_tests():
    """Run the test suite"""
    print("🧪 Running test suite...")
    run_command("pytest tests/ -v --tb=short", "Running tests")


def run_tests_with_coverage():
    """Run tests with coverage report"""
    print("📊 Running tests with coverage...")
    run_command("pytest tests/ --cov=bfx_postonly --cov-report=html --cov-report=term", 
                "Running tests with coverage")
    print("📁 Coverage report generated in htmlcov/index.html")


def format_code():
    """Format code with black and isort"""
    print("🎨 Formatting code...")
    run_command("black bfx_postonly/ examples/ tests/", "Formatting with black")
    run_command("isort bfx_postonly/ examples/ tests/", "Sorting imports with isort")


def lint_code():
    """Lint code with flake8 and mypy"""
    print("🔍 Linting code...")
    run_command("flake8 bfx_postonly/ examples/ tests/", "Linting with flake8")
    run_command("mypy bfx_postonly/", "Type checking with mypy")


def check_code():
    """Run all code quality checks"""
    print("🔧 Running all code quality checks...")
    format_code()
    lint_code()
    run_tests()


def build_package():
    """Build the package for distribution"""
    print("📦 Building package...")
    run_command("python -m build", "Building package")
    print("📁 Built packages are in dist/")


def clean():
    """Clean build artifacts and cache files"""
    print("🧹 Cleaning build artifacts...")
    
    # Remove common build/cache directories
    dirs_to_remove = [
        "__pycache__",
        ".pytest_cache", 
        ".mypy_cache",
        "build",
        "dist",
        "*.egg-info",
        ".coverage",
        "htmlcov"
    ]
    
    for pattern in dirs_to_remove:
        run_command(f"find . -name '{pattern}' -type d -exec rm -rf {{}} + 2>/dev/null || true",
                   f"Removing {pattern}")
        run_command(f"find . -name '{pattern}' -type f -delete 2>/dev/null || true",
                   f"Removing {pattern} files")


def install_pre_commit():
    """Install pre-commit hooks"""
    print("🪝 Installing pre-commit hooks...")
    run_command("pre-commit install", "Installing pre-commit hooks")


def run_examples():
    """Run example scripts"""
    print("📋 Running examples...")
    
    # Check if .env exists
    if not os.path.exists(".env"):
        print("❌ .env file not found. Please create it from .env.example and add your API credentials")
        return
    
    print("🔧 Running basic usage example...")
    run_command("python examples/basic_usage.py", "Running basic usage example")


def main():
    """Main CLI interface"""
    parser = argparse.ArgumentParser(description="Development scripts for bitfinex-api-py-postonly-wrapper")
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Setup command
    subparsers.add_parser("setup", help="Setup development environment")
    
    # Test commands
    subparsers.add_parser("test", help="Run tests")
    subparsers.add_parser("test-cov", help="Run tests with coverage")
    
    # Code quality commands
    subparsers.add_parser("format", help="Format code with black and isort")
    subparsers.add_parser("lint", help="Lint code with flake8 and mypy")
    subparsers.add_parser("check", help="Run all code quality checks")
    
    # Build commands
    subparsers.add_parser("build", help="Build package for distribution")
    subparsers.add_parser("clean", help="Clean build artifacts")
    
    # Utility commands
    subparsers.add_parser("pre-commit", help="Install pre-commit hooks")
    subparsers.add_parser("examples", help="Run example scripts")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Command dispatch
    commands = {
        "setup": setup_dev_environment,
        "test": run_tests,
        "test-cov": run_tests_with_coverage,
        "format": format_code,
        "lint": lint_code,
        "check": check_code,
        "build": build_package,
        "clean": clean,
        "pre-commit": install_pre_commit,
        "examples": run_examples,
    }
    
    if args.command in commands:
        commands[args.command]()
    else:
        print(f"Unknown command: {args.command}")
        parser.print_help()


if __name__ == "__main__":
    main()
