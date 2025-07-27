# Bitfinex API Python POST-ONLY Wrapper

A Python wrapper library for [bitfinex-api-py](https://github.com/0xferit/bitfinex-api-py) that enforces **POST_ONLY** flags on all limit orders to ensure safe market-making operations and prevent accidental taker orders.

## 🚀 Features

- **Automatic POST_ONLY Enforcement**: All limit orders automatically get the POST_ONLY flag (4096)
- **Decorator Pattern Implementation**: Clean, extensible architecture using decorators
- **Full API Compatibility**: Drop-in replacement for the original bitfinex-api-py client
- **Type Safety**: Full type hints and validation
- **Comprehensive Error Handling**: Clear exceptions for order violations
- **Both REST and WebSocket Support**: Works with both API interfaces
- **Market-Making Focused**: Designed specifically for safe market-making strategies

## 📦 Installation

```bash
pip install git+https://github.com/0xferit/bitfinex-api-py-postonly-wrapper.git
```

Or clone and install in development mode:

```bash
git clone https://github.com/0xferit/bitfinex-api-py-postonly-wrapper.git
cd bitfinex-api-py-postonly-wrapper
pip install -e .[dev]
```

## 🔧 Dependencies

This library depends on:
- [bitfinex-api-py (heartbeat branch)](https://github.com/0xferit/bitfinex-api-py/releases/tag/heartbeat)
- Python 3.8+

## 🏃‍♂️ Quick Start

### Basic Usage

```python
import os
from bfx_postonly import PostOnlyClient

# Initialize the client
client = PostOnlyClient(
    api_key=os.getenv("BFX_API_KEY"),
    api_secret=os.getenv("BFX_API_SECRET")
)

# Submit a limit order (automatically gets POST_ONLY flag)
notification = client.submit_limit_order(
    symbol="tBTCUSD",
    amount=0.001,  # Buy 0.001 BTC
    price=30000.0  # At $30,000
)

if notification.status == "SUCCESS":
    order = notification.data
    print(f"Order submitted: {order.id}")
```

### WebSocket Usage

```python
import asyncio
from bfx_postonly import PostOnlyClient

async def websocket_example():
    client = PostOnlyClient(
        api_key=os.getenv("BFX_API_KEY"),
        api_secret=os.getenv("BFX_API_SECRET")
    )
    
    @client.wss.on("authenticated")
    async def on_authenticated(data):
        # Submit order via WebSocket
        await client.submit_limit_order_async(
            symbol="tETHUSD",
            amount=-0.1,  # Sell 0.1 ETH
            price=2000.0  # At $2,000
        )
    
    @client.wss.on("order_new")
    def on_order_new(order):
        print(f"New order: {order.symbol} @ {order.price}")
    
    client.wss.run()

# Run the WebSocket client
asyncio.run(websocket_example())
```

## 🛡️ Safety Features

### Automatic POST_ONLY Enforcement

All limit orders automatically receive the POST_ONLY flag (4096), ensuring they:
- Never become taker orders
- Always provide liquidity to the order book
- Protect against adverse selection
- Prevent accidental market impact

### Order Type Validation

```python
# ✅ This works - limit orders are allowed
client.submit_limit_order(symbol="tBTCUSD", amount=0.001, price=30000.0)

# ❌ This raises PostOnlyViolationError - market orders are rejected
client.rest.auth.submit_order(type="EXCHANGE MARKET", symbol="tBTCUSD", amount=0.001)

# ❌ This raises InvalidOrderTypeError - stop orders are rejected  
client.rest.auth.submit_order(type="STOP", symbol="tBTCUSD", amount=0.001)
```

### Parameter Validation

```python
# ❌ These raise ValueError with descriptive messages
client.submit_limit_order("tBTCUSD", amount=0, price=30000)      # Zero amount
client.submit_limit_order("tBTCUSD", amount=0.001, price=0)      # Zero price
client.submit_limit_order("tBTCUSD", amount=0.001)              # Missing price
```

## 🎯 Advanced Usage

### Market Making Strategy

```python
from bfx_postonly import PostOnlyClient
from bfx_postonly.utils import combine_flags

client = PostOnlyClient(api_key="...", api_secret="...")

# Place hidden POST_ONLY orders
def place_market_making_orders(mid_price, spread=0.01):
    bid_price = mid_price * (1 - spread/2)
    ask_price = mid_price * (1 + spread/2)
    
    # Combine POST_ONLY with HIDDEN flag
    flags = combine_flags("POST_ONLY", "HIDDEN")
    
    # Place bid
    client.submit_limit_order(
        symbol="tBTCUSD",
        amount=0.001,
        price=bid_price,
        flags=flags
    )
    
    # Place ask
    client.submit_limit_order(
        symbol="tBTCUSD", 
        amount=-0.001,
        price=ask_price,
        flags=flags
    )
```

### Grid Trading

```python
def setup_grid(base_price, levels=5, spacing=0.005, size=0.001):
    """Setup a trading grid around base price"""
    
    # Buy orders below base price
    for i in range(1, levels + 1):
        price = base_price * (1 - spacing * i)
        client.submit_limit_order("tBTCUSD", size, price)
    
    # Sell orders above base price
    for i in range(1, levels + 1):
        price = base_price * (1 + spacing * i)
        client.submit_limit_order("tBTCUSD", -size, price)

setup_grid(30000.0)  # Setup grid around $30,000
```

### Error Handling

```python
from bfx_postonly.exceptions import PostOnlyViolationError, InvalidOrderTypeError

try:
    client.submit_limit_order("tBTCUSD", 0.001, 30000.0)
except PostOnlyViolationError as e:
    print(f"Order rejected for safety: {e}")
except InvalidOrderTypeError as e:
    print(f"Invalid order type: {e}")
except ValueError as e:
    print(f"Invalid parameters: {e}")
```

## 🔍 API Reference

### PostOnlyClient

Main client class that wraps the original Bitfinex client.

#### Methods

- `submit_limit_order(symbol, amount, price, **kwargs)` - Submit REST limit order
- `submit_limit_order_async(symbol, amount, price, **kwargs)` - Submit WebSocket limit order  
- `get_client_info()` - Get client configuration information

#### Properties

- `rest` - POST-ONLY wrapped REST client
- `wss` - POST-ONLY wrapped WebSocket client

### Utilities

```python
from bfx_postonly.utils import (
    is_limit_order,
    has_post_only_flag, 
    add_post_only_flag,
    combine_flags,
    get_bitfinex_flags
)

# Check if order type is a limit order
is_limit_order("EXCHANGE LIMIT")  # True
is_limit_order("MARKET")          # False

# Work with flags
flags = combine_flags("POST_ONLY", "HIDDEN", "REDUCE_ONLY")
has_post_only_flag(flags)  # True
```

### Decorators

```python
from bfx_postonly.decorators import post_only_enforcer, post_only_rest

# Decorate individual functions
@post_only_enforcer
def my_order_function(**kwargs):
    # Will automatically add POST_ONLY flag
    pass

# Decorate entire classes
@post_only_rest
class MyRESTClient:
    def submit_order(self, **kwargs):
        pass
```

## 🧪 Testing

Run the test suite:

```bash
# Install development dependencies
pip install -e .[dev]

# Run tests
pytest

# Run with coverage
pytest --cov=bfx_postonly

# Run specific test file
pytest tests/test_postonly.py -v
```

## 📁 Project Structure

```
bitfinex-api-py-postonly-wrapper/
├── bfx_postonly/              # Main package
│   ├── __init__.py           # Package exports
│   ├── client.py             # Main PostOnlyClient class
│   ├── decorators.py         # Decorator implementations
│   ├── exceptions.py         # Custom exceptions
│   └── utils.py             # Utility functions
├── examples/                 # Usage examples
│   ├── basic_usage.py       # Basic examples
│   └── advanced_usage.py    # Advanced strategies
├── tests/                   # Test suite
│   └── test_postonly.py    # Comprehensive tests
├── README.md               # This file
├── pyproject.toml         # Modern Python packaging
├── setup.py              # Legacy packaging support
└── requirements.txt      # Dependencies
```

## ⚙️ Configuration

### Environment Variables

Create a `.env` file (copy from `.env.example`):

```bash
# Required
BFX_API_KEY=your_api_key_here
BFX_API_SECRET=your_api_secret_here

# Optional
LOG_LEVEL=INFO
DEFAULT_SYMBOL=tBTCUSD
DEFAULT_ORDER_SIZE=0.001
DEFAULT_SPREAD=0.01
```

### Logging

```python
import logging
logging.basicConfig(level=logging.INFO)

# The wrapper logs all POST_ONLY order submissions
client.submit_limit_order("tBTCUSD", 0.001, 30000.0)
# INFO: Submitting POST_ONLY order: EXCHANGE LIMIT for tBTCUSD: amount=0.001, price=30000.0
```

## 🔒 Security Considerations

- **API Credentials**: Never commit API keys to version control
- **POST_ONLY Protection**: All limit orders are automatically protected
- **Order Validation**: Comprehensive parameter validation prevents errors
- **Error Isolation**: Wrapper errors don't crash the underlying client

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make changes and add tests
4. Run the test suite: `pytest`
5. Commit changes: `git commit -m 'Add amazing feature'`
6. Push to the branch: `git push origin feature/amazing-feature`
7. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

This software is for educational and research purposes. Use at your own risk. Always test thoroughly in a sandbox environment before using with real funds.

## 🙏 Acknowledgments

- [Bitfinex](https://www.bitfinex.com/) for providing the API
- [bitfinex-api-py](https://github.com/bitfinexcom/bitfinex-api-py) for the base client library
