# Bitfinex POST-ONLY Wrapper

**79 lines of code.** Validates POST_ONLY flags on Bitfinex limit orders. Tiny package = easy verification.

## Install & Use

```bash
pip install git+https://github.com/0xferit/bitfinex-api-py-postonly-wrapper.git
```

```python
from bfx_postonly import PostOnlyClient, PostOnlyError

client = PostOnlyClient(api_key="...", api_secret="...")

# Method 1: Direct API (requires explicit flags=4096)
client.rest.auth.submit_order(
    type="EXCHANGE LIMIT", 
    symbol="tBTCUSD", 
    amount=0.001, 
    price=30000.0,
    flags=4096
)

# Method 2: Convenience method (auto-adds POST_ONLY flag)
client.submit_limit_order("tBTCUSD", 0.001, 30000.0)

# Invalid: raises PostOnlyError
client.rest.auth.submit_order(type="EXCHANGE MARKET", symbol="tBTCUSD", amount=0.001)
```

## How It Works

Wraps bitfinex-api-py and validates orders before transmission:
- Requires `EXCHANGE LIMIT` type
- Requires `flags=4096` (POST_ONLY) for direct API calls
- Convenience methods automatically add POST_ONLY flag
- Blocks market orders

**Validation-only** - orders pass through untouched if valid.

**Python 3.13+ required**

## Development

### Pre-commit Hook

This project includes a pre-commit hook that runs the same checks as the CI pipeline locally. This helps catch issues early and saves time by preventing failed CI runs.

To set up the development environment and install the pre-commit hook:

```bash
# Set up virtual environment and install dependencies
./scripts/setup-dev.sh

# Install the pre-commit hook
./scripts/setup-precommit.sh
```

The hook will automatically run:
- flake8 linting
- black code formatting
- isort import sorting  
- mypy type checking
- pytest tests with coverage
- security checks (safety, bandit)

For detailed documentation, see [docs/PRE-COMMIT.md](docs/PRE-COMMIT.md).