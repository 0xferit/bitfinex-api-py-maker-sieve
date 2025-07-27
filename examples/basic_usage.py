"""
Basic usage example for POST-ONLY wrapper
"""

import os
from bfx_postonly import PostOnlyClient, PostOnlyError

# Initialize client
client = PostOnlyClient(
    api_key=os.getenv("BFX_API_KEY"),
    api_secret=os.getenv("BFX_API_SECRET")
)

try:
    # Method 1: Direct API call (requires explicit POST_ONLY flag)
    order = client.rest.auth.submit_order(
        type="EXCHANGE LIMIT",
        symbol="tBTCUSD",
        amount=0.001,
        price=30000.0,
        flags=4096  # POST_ONLY flag required
    )
    print(f"Order submitted: {order}")

except PostOnlyError as e:
    print(f"Order rejected: {e}")

try:
    # Method 2: Convenience method (automatically adds POST_ONLY flag)
    order = client.submit_limit_order("tBTCUSD", 0.001, 30000.0)
    print(f"Order submitted: {order}")

except PostOnlyError as e:
    print(f"Order rejected: {e}")

# This will raise PostOnlyError
try:
    client.rest.auth.submit_order(
        type="EXCHANGE MARKET", symbol="tBTCUSD", amount=0.001
    )
except PostOnlyError as e:
    print(f"Market order blocked: {e}")
