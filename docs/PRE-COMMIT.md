# Pre-commit Hook

This project includes a pre-commit hook that runs the same checks as the CI pipeline locally before each commit. This helps catch issues early and saves time by preventing failed CI runs.

## What the Pre-commit Hook Does

The pre-commit hook runs the following checks in order:

1. **flake8 linting** - Checks code style and potential errors
2. **black formatting check** - Ensures code is properly formatted
3. **isort import sorting** - Verifies imports are properly sorted
4. **mypy type checking** - Performs static type analysis
5. **pytest tests** - Runs all tests with coverage reporting
6. **Security checks** - Runs safety and bandit (optional, won't fail commit)

## Installation

### Prerequisites

First, set up your development environment:

```bash
# Set up virtual environment and install dependencies
./scripts/setup-dev.sh
```

### Option 1: Using the Setup Script (Recommended)

```bash
# Run the setup script from the project root
./scripts/setup-precommit.sh
```

### Option 2: Manual Installation

```bash
# Copy the pre-commit hook to git hooks directory
cp scripts/pre-commit .git/hooks/pre-commit

# Make it executable
chmod +x .git/hooks/pre-commit
```

## Usage

Once installed, the pre-commit hook will automatically run every time you make a commit:

```bash
git add .
git commit -m "feat: add new feature"
```

If any checks fail, the commit will be blocked and you'll see detailed error messages explaining what needs to be fixed.

## Fixing Common Issues

### Code Formatting Issues

If black formatting check fails:

```bash
black bfx_postonly/ examples/
```

### Import Sorting Issues

If isort check fails:

```bash
isort bfx_postonly/ examples/
```

### Linting Issues

Fix flake8 issues by following the error messages. Common fixes include:
- Removing unused imports
- Fixing line length issues
- Adding missing docstrings

### Type Checking Issues

Fix mypy issues by:
- Adding proper type hints
- Importing missing types
- Fixing type mismatches

## Skipping the Hook (Not Recommended)

In emergency situations, you can skip the pre-commit hook:

```bash
git commit --no-verify -m "emergency: skip checks"
```

⚠️ **Warning**: Only use this when absolutely necessary, as it bypasses all quality checks.

## Troubleshooting

### Hook Not Running

1. Ensure the hook is executable: `chmod +x .git/hooks/pre-commit`
2. Verify the hook exists: `ls -la .git/hooks/pre-commit`
3. Check if you're in a git repository: `git status`

### Dependencies Not Found

The hook automatically installs development dependencies, but if you encounter issues:

```bash
pip install -e .[dev]
pip install safety bandit
```

### Performance Issues

If the hook is too slow, you can temporarily disable specific checks by commenting out sections in the hook file. However, this is not recommended for regular development.

## Configuration

The pre-commit hook uses the same configuration as the CI pipeline:

- **flake8**: Uses project's flake8 configuration
- **black**: Uses `pyproject.toml` configuration
- **isort**: Uses `pyproject.toml` configuration  
- **mypy**: Uses `pyproject.toml` configuration
- **pytest**: Uses `pyproject.toml` configuration

## Contributing

When contributing to this project:

1. Install the pre-commit hook using the setup script
2. Ensure all checks pass before submitting a pull request
3. If you need to modify the hook, update both `.git/hooks/pre-commit` and `scripts/pre-commit`

## Benefits

- **Faster feedback**: Catch issues immediately instead of waiting for CI
- **Reduced CI failures**: Prevent commits that would fail in CI
- **Consistent code quality**: Ensure all commits meet project standards
- **Time savings**: Avoid the cycle of commit → CI failure → fix → commit 