"""
POST-ONLY validation wrapper for Bitfinex API.
Validates orders but never modifies them.
"""

import logging
from typing import Any

from bfxapi import Client as BfxClient

logger = logging.getLogger(__name__)


class PostOnlyError(Exception):
    """Raised when an order violates POST_ONLY requirements."""

    pass


def validate_post_only(**kwargs: Any) -> None:
    """Validate order has POST_ONLY flag (4096) and is EXCHANGE LIMIT type"""
    order_type = kwargs.get("type")
    if not isinstance(order_type, str):
        raise PostOnlyError("Order type must be a string")

    if order_type != "EXCHANGE LIMIT":
        raise PostOnlyError(f"Only EXCHANGE LIMIT orders allowed, got: {order_type}")

    flags = kwargs.get("flags", 0)
    if not isinstance(flags, int):
        raise PostOnlyError("Flags must be an integer")

    post_only_flag = 4096
    if not (flags & post_only_flag):
        raise PostOnlyError(f"POST_ONLY flag ({post_only_flag}) required")


class PostOnlyClient:
    """
    Bitfinex client that enforces POST_ONLY on all orders.
    Validates orders but never modifies them.
    """

    def __init__(
        self, api_key: str | None = None, api_secret: str | None = None, **kwargs: Any
    ):
        """Initialize with POST_ONLY validation wrapper"""
        self._client = BfxClient(api_key=api_key, api_secret=api_secret, **kwargs)

        # Safely wrap REST submit_order with validation
        try:
            if not hasattr(self._client.rest, "auth") or not hasattr(
                self._client.rest.auth, "submit_order"
            ):
                raise AttributeError("REST submit_order method not found")

            original_submit = self._client.rest.auth.submit_order

            def rest_submit(*args: Any, **kwargs: Any) -> Any:
                validate_post_only(**kwargs)
                return original_submit(*args, **kwargs)

            # Use setattr to avoid mypy method assignment error
            setattr(self._client.rest.auth, "submit_order", rest_submit)
            logger.info("Successfully wrapped REST submit_order method")

        except Exception as e:
            logger.error(f"Failed to wrap REST submit_order: {e}")
            raise PostOnlyError(f"Failed to initialize REST wrapper: {e}") from e

        # Safely wrap WebSocket submit_order with validation if available
        self._wss_available = False
        try:
            if (
                hasattr(self._client, "wss")
                and hasattr(self._client.wss, "inputs")
                and hasattr(self._client.wss.inputs, "submit_order")
            ):
                original_wss_submit = self._client.wss.inputs.submit_order

                async def wss_submit(*args: Any, **kwargs: Any) -> Any:
                    validate_post_only(**kwargs)
                    return await original_wss_submit(*args, **kwargs)

                # Use setattr to avoid mypy method assignment error
                setattr(self._client.wss.inputs, "submit_order", wss_submit)
                self._wss_available = True
                logger.info("Successfully wrapped WebSocket submit_order method")
            else:
                logger.warning("WebSocket submit_order method not available")

        except Exception as e:
            logger.warning(f"Failed to wrap WebSocket submit_order: {e}")
            # Don't raise error for WebSocket - it's optional

    @property
    def rest(self) -> Any:
        """Access wrapped REST client"""
        return self._client.rest

    @property
    def wss(self) -> Any:
        """Access wrapped WebSocket client"""
        return self._client.wss

    def submit_limit_order(
        self, symbol: str, amount: float, price: float, **kwargs: Any
    ) -> Any:
        """Submit limit order. Validates POST_ONLY flag is present"""
        # Validate inputs
        if not isinstance(symbol, str) or not symbol.strip():
            raise PostOnlyError("Symbol must be a non-empty string")
        if not isinstance(amount, int | float) or amount == 0:
            raise PostOnlyError("Amount must be a non-zero number")
        if not isinstance(price, int | float) or price <= 0:
            raise PostOnlyError("Price must be a positive number")

        return self.rest.auth.submit_order(
            type="EXCHANGE LIMIT", symbol=symbol, amount=amount, price=price, **kwargs
        )

    async def submit_limit_order_async(
        self, symbol: str, amount: float, price: float, **kwargs: Any
    ) -> Any:
        """Submit limit order via WebSocket. Validates POST_ONLY flag is present"""
        if not self._wss_available:
            raise AttributeError("WebSocket submit_order not available")

        # Validate inputs
        if not isinstance(symbol, str) or not symbol.strip():
            raise PostOnlyError("Symbol must be a non-empty string")
        if not isinstance(amount, int | float) or amount == 0:
            raise PostOnlyError("Amount must be a non-zero number")
        if not isinstance(price, int | float) or price <= 0:
            raise PostOnlyError("Price must be a positive number")

        return await self.wss.inputs.submit_order(
            type="EXCHANGE LIMIT", symbol=symbol, amount=amount, price=price, **kwargs
        )

    def __getattr__(self, name: str) -> Any:
        return getattr(self._client, name)
