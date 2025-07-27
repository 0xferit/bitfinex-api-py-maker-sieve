# Bitfinex API Python POST-ONLY Wrapper

A lean validation wrapper for bitfinex-api-py that enforces POST_ONLY flag on all limit orders.

## Installation

```bash
# Install this package (includes required bitfinex-api-py dependency)
pip install bitfinex-api-py-postonly-wrapper
```

The required `bitfinex-api-py` dependency will be automatically installed from the git repository.

## Usage

```python
from bfx_postonly import PostOnlyClient, PostOnlyError

# Initialize client
client = PostOnlyClient(
    api_key="your_api_key",
    api_secret="your_api_secret"
)

# This will pass validation (includes POST_ONLY flag)
client.rest.auth.submit_order(
    type="EXCHANGE LIMIT",
    symbol="tBTCUSD", 
    amount=0.001,
    price=30000.0,
    flags=4096  # POST_ONLY flag required
)

# This will raise PostOnlyError (missing POST_ONLY flag)
try:
    client.rest.auth.submit_order(
        type="EXCHANGE LIMIT",
        symbol="tBTCUSD",
        amount=0.001, 
        price=30000.0
        # Missing flags=4096
    )
except PostOnlyError as e:
    print(f"Validation failed: {e}")
```

## Design Principles

- **No Order Modification**: Never modifies orders, only validates them
- **Pure Validation**: Checks for POST_ONLY compliance and raises errors for violations  
- **Fail Fast**: Immediately rejects non-compliant orders with clear error messages
- **Lean Implementation**: Minimal codebase focused on core validation requirements

## Requirements

- Python 3.13+
- https://github.com/0xferit/bitfinex-maker-kit