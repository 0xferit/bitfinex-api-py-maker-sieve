"""
Main client wrapper that enforces POST-ONLY behavior
"""

import logging
from typing import Any, Optional, Dict, Union
from bfxapi import Client as BfxClient, REST_HOST, WSS_HOST
from bfxapi.types import Notification, Order

from .decorators import PostOnlyMethodWrapper, post_only_enforcer
from .exceptions import PostOnlyViolationError, ConfigurationError
from .utils import (
    validate_order_parameters, 
    format_order_info, 
    add_post_only_flag,
    is_limit_order
)

# Set up logging
logger = logging.getLogger(__name__)


class PostOnlyRESTWrapper:
    """
    Wrapper for the REST client that enforces POST_ONLY on all limit orders.
    """
    
    def __init__(self, rest_client: Any):
        """
        Initialize the REST wrapper.
        
        Args:
            rest_client: The original REST client instance
        """
        self._rest_client = rest_client
        self._original_submit_order = rest_client.auth.submit_order
        
        # Replace the submit_order method with our wrapped version
        rest_client.auth.submit_order = self._wrapped_submit_order
    
    def _wrapped_submit_order(self, **kwargs) -> Notification[Order]:
        """
        Wrapped submit_order method that enforces POST_ONLY.
        
        Args:
            **kwargs: Order parameters
            
        Returns:
            Notification containing the order result
            
        Raises:
            PostOnlyViolationError: If order cannot be made POST_ONLY
        """
        # Validate parameters
        validate_order_parameters(kwargs)
        
        # Ensure POST_ONLY flag is set for limit orders
        if is_limit_order(kwargs.get('type', '')):
            kwargs['flags'] = add_post_only_flag(kwargs.get('flags'))
            logger.info(f"Submitting POST_ONLY order: {format_order_info(kwargs)}")
        else:
            raise PostOnlyViolationError(
                f"Order type '{kwargs.get('type')}' is not supported. Only limit orders are allowed."
            )
        
        # Call the original method
        return self._original_submit_order(**kwargs)
    
    def __getattr__(self, name: str) -> Any:
        """
        Delegate all other attributes to the original REST client.
        """
        return getattr(self._rest_client, name)


class PostOnlyWebSocketWrapper:
    """
    Wrapper for the WebSocket client that enforces POST_ONLY on all limit orders.
    """
    
    def __init__(self, wss_client: Any):
        """
        Initialize the WebSocket wrapper.
        
        Args:
            wss_client: The original WebSocket client instance
        """
        self._wss_client = wss_client
        
        # Wrap the inputs.submit_order method if it exists
        if hasattr(wss_client, 'inputs') and hasattr(wss_client.inputs, 'submit_order'):
            self._original_submit_order = wss_client.inputs.submit_order
            wss_client.inputs.submit_order = self._wrapped_submit_order
    
    async def _wrapped_submit_order(self, **kwargs) -> None:
        """
        Wrapped submit_order method that enforces POST_ONLY.
        
        Args:
            **kwargs: Order parameters
            
        Raises:
            PostOnlyViolationError: If order cannot be made POST_ONLY
        """
        # Validate parameters
        validate_order_parameters(kwargs)
        
        # Ensure POST_ONLY flag is set for limit orders
        if is_limit_order(kwargs.get('type', '')):
            kwargs['flags'] = add_post_only_flag(kwargs.get('flags'))
            logger.info(f"Submitting POST_ONLY order via WebSocket: {format_order_info(kwargs)}")
        else:
            raise PostOnlyViolationError(
                f"Order type '{kwargs.get('type')}' is not supported. Only limit orders are allowed."
            )
        
        # Call the original method
        return await self._original_submit_order(**kwargs)
    
    def __getattr__(self, name: str) -> Any:
        """
        Delegate all other attributes to the original WebSocket client.
        """
        return getattr(self._wss_client, name)


class PostOnlyClient:
    """
    Main client wrapper that enforces POST_ONLY behavior on all limit orders.
    
    This class wraps the standard Bitfinex API client and ensures that all limit orders
    are submitted with the POST_ONLY flag, preventing them from becoming taker orders.
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        api_secret: Optional[str] = None,
        rest_host: str = REST_HOST,
        wss_host: str = WSS_HOST,
        **kwargs
    ):
        """
        Initialize the POST-ONLY client.
        
        Args:
            api_key: Bitfinex API key
            api_secret: Bitfinex API secret
            rest_host: REST API host URL
            wss_host: WebSocket API host URL
            **kwargs: Additional arguments passed to the underlying client
        """
        self._api_key = api_key
        self._api_secret = api_secret
        self._rest_host = rest_host
        self._wss_host = wss_host
        
        # Initialize the underlying Bitfinex client
        try:
            self._client = BfxClient(
                api_key=api_key,
                api_secret=api_secret,
                rest_host=rest_host,
                wss_host=wss_host,
                **kwargs
            )
        except Exception as e:
            raise ConfigurationError(f"Failed to initialize Bitfinex client: {e}")
        
        # Wrap the REST and WebSocket clients
        self._rest_wrapper = PostOnlyRESTWrapper(self._client.rest)
        self._wss_wrapper = PostOnlyWebSocketWrapper(self._client.wss)
        
        logger.info("PostOnlyClient initialized successfully")
    
    @property
    def rest(self) -> PostOnlyRESTWrapper:
        """
        Get the POST-ONLY wrapped REST client.
        
        Returns:
            Wrapped REST client with POST_ONLY enforcement
        """
        return self._rest_wrapper
    
    @property
    def wss(self) -> PostOnlyWebSocketWrapper:
        """
        Get the POST-ONLY wrapped WebSocket client.
        
        Returns:
            Wrapped WebSocket client with POST_ONLY enforcement
        """
        return self._wss_wrapper
    
    def submit_limit_order(
        self,
        symbol: str,
        amount: float,
        price: float,
        order_type: str = "EXCHANGE LIMIT",
        **kwargs
    ) -> Notification[Order]:
        """
        Submit a limit order with POST_ONLY enforcement.
        
        This is a convenience method that ensures the order is a limit order
        and has the POST_ONLY flag set.
        
        Args:
            symbol: Trading pair symbol (e.g., "tBTCUSD")
            amount: Order amount (positive for buy, negative for sell)
            price: Limit price
            order_type: Order type (defaults to "EXCHANGE LIMIT")
            **kwargs: Additional order parameters
            
        Returns:
            Notification containing the order result
            
        Raises:
            PostOnlyViolationError: If the order cannot be made POST_ONLY
        """
        # Prepare order parameters
        order_params = {
            'type': order_type,
            'symbol': symbol,
            'amount': amount,
            'price': price,
            **kwargs
        }
        
        # Submit via REST client
        return self.rest.auth.submit_order(**order_params)
    
    async def submit_limit_order_async(
        self,
        symbol: str,
        amount: float,
        price: float,
        order_type: str = "EXCHANGE LIMIT",
        **kwargs
    ) -> None:
        """
        Submit a limit order asynchronously with POST_ONLY enforcement.
        
        Args:
            symbol: Trading pair symbol (e.g., "tBTCUSD")
            amount: Order amount (positive for buy, negative for sell)
            price: Limit price
            order_type: Order type (defaults to "EXCHANGE LIMIT")
            **kwargs: Additional order parameters
            
        Raises:
            PostOnlyViolationError: If the order cannot be made POST_ONLY
        """
        # Prepare order parameters
        order_params = {
            'type': order_type,
            'symbol': symbol,
            'amount': amount,
            'price': price,
            **kwargs
        }
        
        # Submit via WebSocket client
        await self.wss.inputs.submit_order(**order_params)
    
    def get_client_info(self) -> Dict[str, Any]:
        """
        Get information about the client configuration.
        
        Returns:
            Dictionary containing client configuration info
        """
        return {
            'api_key_set': bool(self._api_key),
            'rest_host': self._rest_host,
            'wss_host': self._wss_host,
            'post_only_enforced': True,
            'wrapper_version': '1.0.0'
        }
    
    def __getattr__(self, name: str) -> Any:
        """
        Delegate other attributes to the underlying client.
        
        Args:
            name: Attribute name
            
        Returns:
            The requested attribute from the underlying client
        """
        return getattr(self._client, name)
