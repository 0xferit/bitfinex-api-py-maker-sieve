"""
Test POST-ONLY validation wrapper.
Valid orders pass through, invalid orders blocked with PostOnlyError.
"""

import os
import pytest
from pathlib import Path

from bfx_postonly import PostOnlyClient, PostOnlyError


def load_credentials():
    """Load paper trading credentials from .env file"""
    env_file = Path(__file__).parent / '.env'
    if env_file.exists():
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line.startswith('BFX_API_PAPER_KEY='):
                    os.environ['BFX_API_PAPER_KEY'] = line.split('=', 1)[1]
                elif line.startswith('BFX_API_PAPER_SECRET='):
                    os.environ['BFX_API_PAPER_SECRET'] = line.split('=', 1)[1]
    
    api_key = os.getenv("BFX_API_PAPER_KEY")
    api_secret = os.getenv("BFX_API_PAPER_SECRET")
    
    return api_key, api_secret


def test_valid_orders_transmitted_untouched():
    """Valid orders with POST_ONLY flag pass through to API"""
    
    api_key, api_secret = load_credentials()
    if not api_key or not api_secret:
        pytest.skip("No paper trading credentials found in .env file")
    
    client = PostOnlyClient(
        api_key=api_key,
        api_secret=api_secret,
        rest_host="https://api-pub.bitfinex.com"
    )
    
    # Test 1: Valid limit order with POST_ONLY flag should pass through validation
    try:
        result = client.rest.auth.submit_order(
            type="EXCHANGE LIMIT",
            symbol="tBTCUSD",
            amount=0.001,
            price=200000.0,
            flags=4096  # POST_ONLY flag
        )
        # Should reach the API (may get API errors, but not wrapper errors)
        assert result is not None
        
    except Exception as e:
        # API errors are expected with paper trading, but wrapper should not interfere
        error_msg = str(e)
        assert "Only limit orders allowed" not in error_msg, "Wrapper should not reject valid limit orders"
        assert "POST_ONLY flag" not in error_msg, "Wrapper should not reject orders with POST_ONLY flag"
    
    # Test 2: Convenience method with POST_ONLY flag should work
    try:
        result = client.submit_limit_order("tBTCUSD", 0.001, 200000.0, flags=4096)
        # Should work - convenience method with POST_ONLY flag
        assert result is not None
        
    except Exception as e:
        # API errors expected, but not wrapper validation errors
        error_msg = str(e)
        assert "Only limit orders allowed" not in error_msg
        assert "POST_ONLY flag" not in error_msg


def test_invalid_orders_blocked_with_exceptions():
    """Invalid orders blocked with PostOnlyError"""
    
    api_key, api_secret = load_credentials()
    if not api_key or not api_secret:
        pytest.skip("No paper trading credentials found in .env file")
    
    client = PostOnlyClient(
        api_key=api_key,
        api_secret=api_secret,
        rest_host="https://api-pub.bitfinex.com"
    )
    
    # Test 1: Market orders should be blocked with PostOnlyError
    with pytest.raises(PostOnlyError, match="Only limit orders allowed"):
        client.rest.auth.submit_order(
            type="EXCHANGE MARKET",
            symbol="tBTCUSD",
            amount=0.001
        )
    
    # Test 2: Limit orders without POST_ONLY flag should be blocked
    with pytest.raises(PostOnlyError, match="POST_ONLY flag \\(4096\\) required"):
        client.rest.auth.submit_order(
            type="EXCHANGE LIMIT",
            symbol="tBTCUSD",
            amount=0.001,
            price=200000.0,
            flags=0  # No POST_ONLY flag
        )
    
    # Test 3: Other invalid order types should be blocked
    with pytest.raises(PostOnlyError, match="Only limit orders allowed"):
        client.rest.auth.submit_order(
            type="STOP",
            symbol="tBTCUSD",
            amount=0.001,
            price=200000.0
        )
    
    # Test 4: Convenience methods without POST_ONLY flag should also be blocked
    with pytest.raises(PostOnlyError, match="POST_ONLY flag \\(4096\\) required"):
        client.submit_limit_order("tBTCUSD", 0.001, 200000.0)  # No flags parameter