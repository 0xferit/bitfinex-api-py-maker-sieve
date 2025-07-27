"""
Sieve for Bitfinex API.
Sieves orders that are not LIMIT and POST_ONLY for safe market-making.
"""

from collections.abc import Callable
from typing import Any

from bfxapi import Client as BfxClient


class PostOnlyError(Exception):
    """Raised when an order violates POST_ONLY requirements or wrapper initialization fails."""


def validate_post_only(**kwargs: Any) -> None:
    """Only permit limit orders with POST_ONLY flag."""
    order_type = kwargs.get("type", "").upper()

    # Must be a limit order (contain "LIMIT")
    if "LIMIT" not in order_type:
        raise PostOnlyError(f"Only limit orders permitted, got: {order_type}")

    # Must have POST_ONLY flag
    flags = kwargs.get("flags", 0)
    post_only_flag = 4096
    if not (flags & post_only_flag):
        raise PostOnlyError(f"POST_ONLY flag ({post_only_flag}) required")


def wrap_with_validation(original: Callable[..., Any]) -> Callable[..., Any]:
    """Decorator to add POST_ONLY validation before calling the original method."""

    def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
        validate_post_only(**kwargs)
        return original(*args, **kwargs)

    async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
        validate_post_only(**kwargs)
        return await original(*args, **kwargs)

    # Return async or sync based on the original (assuming library methods are correctly typed)
    if hasattr(original, "__await__"):
        return async_wrapper
    return sync_wrapper


class PostOnlyClient:
    """
    Bitfinex client that enforces POST_ONLY on all orders.
    Validates orders but never modifies them.
    Assumes underlying bfxapi library provides REST and WebSocket submit_order methods.
    """

    def __init__(self, api_key: str | None = None, api_secret: str | None = None, **kwargs: Any):
        """Initialize with POST_ONLY validation wrapper."""
        self._client = BfxClient(api_key=api_key, api_secret=api_secret, **kwargs)

        # Wrap REST submit_order with validation
        if not (hasattr(self._client.rest, "auth") and hasattr(self._client.rest.auth, "submit_order")):
            raise PostOnlyError("REST submit_order method not found in bfxapi.rest.auth")

        self._client.rest.auth.submit_order = wrap_with_validation(self._client.rest.auth.submit_order)

        # Wrap WebSocket submit_order with validation (mandatory)
        if not (
            hasattr(self._client, "wss")
            and hasattr(self._client.wss, "inputs")
            and hasattr(self._client.wss.inputs, "submit_order")
        ):
            raise PostOnlyError("WebSocket submit_order method not found in bfxapi.wss.inputs")

        self._client.wss.inputs.submit_order = wrap_with_validation(self._client.wss.inputs.submit_order)

    @property
    def rest(self) -> Any:
        """Access wrapped REST client."""
        return self._client.rest

    @property
    def wss(self) -> Any:
        """Access wrapped WebSocket client."""
        return self._client.wss

    def submit_limit_order(self, symbol: str, amount: float, price: float, **kwargs: Any) -> Any:
        """Submit limit order via REST. Validates POST_ONLY flag is present."""
        return self.rest.auth.submit_order(type="EXCHANGE LIMIT", symbol=symbol, amount=amount, price=price, **kwargs)

    async def submit_limit_order_async(self, symbol: str, amount: float, price: float, **kwargs: Any) -> Any:
        """Submit limit order via WebSocket. Validates POST_ONLY flag is present."""
        return await self.wss.inputs.submit_order(
            type="EXCHANGE LIMIT", symbol=symbol, amount=amount, price=price, **kwargs
        )

    def __getattr__(self, name: str) -> Any:
        return getattr(self._client, name)
