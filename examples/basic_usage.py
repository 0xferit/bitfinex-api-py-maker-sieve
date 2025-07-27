"""Basic usage examples for bitfinex-api-py-postonly-wrapper"""

import os

from bfx_postonly import PostOnlyClient, PostOnlyError

# Initialize client
client = PostOnlyClient(api_key=os.getenv("BFX_API_PAPER_KEY"), api_secret=os.getenv("BFX_API_PAPER_SECRET"))

# Example 1: Valid limit order with POST_ONLY flag
try:
    client.rest.auth.submit_order(
        type="EXCHANGE LIMIT",
        symbol="tBTCUSD",
        amount=0.001,
        price=30000.0,
        flags=4096,  # POST_ONLY flag required
    )
    print("✅ EXCHANGE LIMIT order with POST_ONLY flag - ALLOWED")
except PostOnlyError as e:
    print(f"❌ Error: {e}")

# Example 2: Valid STOP LIMIT order with POST_ONLY flag
try:
    client.rest.auth.submit_order(
        type="STOP LIMIT",
        symbol="tBTCUSD",
        amount=0.001,
        price=30000.0,
        price_aux_limit=29500.0,
        flags=4096,  # POST_ONLY flag required
    )
    print("✅ STOP LIMIT order with POST_ONLY flag - ALLOWED")
except PostOnlyError as e:
    print(f"❌ Error: {e}")

# Example 3: Limit order without POST_ONLY flag (REJECTED)
try:
    client.rest.auth.submit_order(
        type="EXCHANGE LIMIT",
        symbol="tBTCUSD",
        amount=0.001,
        price=30000.0,
        # Missing flags=4096 - this will be rejected
    )
except PostOnlyError as e:
    print(f"❌ Expected rejection - limit order without POST_ONLY: {e}")

# Example 4: Market order (REJECTED - not a limit order)
try:
    client.rest.auth.submit_order(
        type="EXCHANGE MARKET",
        symbol="tBTCUSD",
        amount=0.001,
        flags=4096,  # Even with POST_ONLY flag, market orders are rejected
    )
except PostOnlyError as e:
    print(f"❌ Expected rejection - market order not permitted: {e}")

# Example 5: STOP order (REJECTED - not a limit order)
try:
    client.rest.auth.submit_order(
        type="EXCHANGE STOP",
        symbol="tBTCUSD",
        amount=0.001,
        price=29000.0,
        flags=4096,  # Even with POST_ONLY flag, stop orders are rejected
    )
except PostOnlyError as e:
    print(f"❌ Expected rejection - stop order not permitted: {e}")

# Example 6: Using convenience method
try:
    client.submit_limit_order(
        "tBTCUSD",
        0.001,
        30000.0,
        flags=4096,  # Must include POST_ONLY flag
    )
    print("✅ Convenience method with POST_ONLY flag - ALLOWED")
except PostOnlyError as e:
    print(f"❌ Error: {e}")

print("\n📋 Summary:")
print("- Only LIMIT orders are permitted (LIMIT, EXCHANGE LIMIT, STOP LIMIT, EXCHANGE STOP LIMIT)")
print("- All limit orders MUST have POST_ONLY flag (4096)")
print("- MARKET, STOP, FOK, IOC orders are rejected")
print("- The wrapper acts as a surgical sieve for POST_ONLY limit orders only")
