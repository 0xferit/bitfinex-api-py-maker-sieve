"""
Bitfinex API Python POST-ONLY Wrapper

A simple wrapper that enforces POST_ONLY flag on all limit orders.
"""

__version__ = "1.0.0"

from .client import PostOnlyClient, PostOnlyError

__all__ = ["PostOnlyClient", "PostOnlyError"]