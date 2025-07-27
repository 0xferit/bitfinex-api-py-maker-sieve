"""
Basic usage examples for bitfinex-api-py-postonly-wrapper
"""

import os

from bfx_postonly import PostOnlyClient, PostOnlyError

# Initialize client
client = PostOnlyClient(
    api_key=os.getenv("BFX_API_KEY", ""), api_secret=os.getenv("BFX_API_SECRET", "")
)

# Method 1: Direct API calls (must include flags=4096)
try:
    # This will pass validation
    client.rest.auth.submit_order(
        type="EXCHANGE LIMIT",
        symbol="tBTCUSD",
        amount=0.001,
        price=30000.0,
        flags=4096,  # POST_ONLY flag
    )
    print("Order submitted successfully with POST_ONLY flag")
except PostOnlyError as e:
    print(f"Validation failed: {e}")

# Method 2: Direct API calls without POST_ONLY flag (will fail)
try:
    client.rest.auth.submit_order(
        type="EXCHANGE LIMIT",
        symbol="tBTCUSD",
        amount=0.001,
        price=30000.0,
        # Missing flags=4096 - this will be rejected
    )
except PostOnlyError as e:
    print(f"Expected error: {e}")

# Method 3: Convenience methods (also require POST_ONLY flag)
try:
    client.submit_limit_order(
        "tBTCUSD",
        0.001,
        30000.0,
        flags=4096,  # Must include POST_ONLY flag
    )
    print("Order submitted via convenience method")
except PostOnlyError as e:
    print(f"Validation failed: {e}")

# Method 4: Convenience method without POST_ONLY flag (will fail)
try:
    client.submit_limit_order("tBTCUSD", 0.001, 30000.0)  # No flags
except PostOnlyError as e:
    print(f"Expected error: {e}")
