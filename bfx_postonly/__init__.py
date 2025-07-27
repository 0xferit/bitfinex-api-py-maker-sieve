"""
Bitfinex API Python POST-ONLY Wrapper

A decorator-based wrapper for bitfinex-api-py that enforces POST_ONLY flag on all limit orders
to ensure safe market-making operations and prevent accidental market orders.
"""

__version__ = "1.0.0"
__author__ = "0xferit"

from .client import PostOnlyClient
from .decorators import post_only_enforcer, post_only_rest, post_only_websocket
from .exceptions import PostOnlyViolationError, InvalidOrderTypeError

__all__ = [
    "PostOnlyClient",
    "post_only_enforcer", 
    "post_only_rest",
    "post_only_websocket",
    "PostOnlyViolationError",
    "InvalidOrderTypeError",
]
