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