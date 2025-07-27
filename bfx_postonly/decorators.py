"""
Decorator functions for enforcing POST-ONLY behavior
"""

import functools
import inspect
from typing import Any, Callable, Dict, Union, Optional
from .exceptions import PostOnlyViolationError, InvalidOrderTypeError


def _validate_and_modify_order_params(**kwargs) -> Dict[str, Any]:
    """
    Validates and modifies order parameters to enforce POST_ONLY.
    
    Args:
        **kwargs: Order parameters
        
    Returns:
        Dict with modified parameters ensuring POST_ONLY is set
        
    Raises:
        PostOnlyViolationError: If order type is not suitable for POST_ONLY
        InvalidOrderTypeError: If order type is not supported
    """
    order_type = kwargs.get('type', '').upper()
    
    # Only allow LIMIT orders (EXCHANGE LIMIT, LIMIT)
    if 'LIMIT' not in order_type:
        raise InvalidOrderTypeError(
            f"Order type '{order_type}' is not supported. Only LIMIT orders are allowed."
        )
    
    # Check if it's a market order disguised as limit
    if 'MARKET' in order_type:
        raise InvalidOrderTypeError(
            f"Market orders are not allowed. Order type: '{order_type}'"
        )
    
    # Ensure POST_ONLY flag is set
    flags = kwargs.get('flags', 0)
    
    # Bitfinex POST_ONLY flag value is 4096 (0x1000)
    POST_ONLY_FLAG = 4096
    
    # If flags is already an integer, ensure POST_ONLY is included
    if isinstance(flags, int):
        if not (flags & POST_ONLY_FLAG):
            kwargs['flags'] = flags | POST_ONLY_FLAG
    else:
        # If flags is not set or is a different type, set it to POST_ONLY
        kwargs['flags'] = POST_ONLY_FLAG
    
    return kwargs


def post_only_enforcer(func: Callable) -> Callable:
    """
    Decorator that enforces POST_ONLY flag on order submission methods.
    
    This decorator intercepts calls to order submission functions and ensures
    that all limit orders have the POST_ONLY flag set, preventing them from
    becoming taker orders.
    
    Args:
        func: The function to decorate (should be an order submission method)
        
    Returns:
        Wrapped function with POST_ONLY enforcement
    """
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Check if this is an order submission call
        if 'submit_order' in func.__name__ or 'order' in func.__name__.lower():
            kwargs = _validate_and_modify_order_params(**kwargs)
        
        return func(*args, **kwargs)
    
    @functools.wraps(func)
    async def async_wrapper(*args, **kwargs):
        # Check if this is an order submission call
        if 'submit_order' in func.__name__ or 'order' in func.__name__.lower():
            kwargs = _validate_and_modify_order_params(**kwargs)
        
        return await func(*args, **kwargs)
    
    # Return the appropriate wrapper based on whether the function is async
    if inspect.iscoroutinefunction(func):
        return async_wrapper
    else:
        return wrapper


def post_only_rest(cls: type) -> type:
    """
    Class decorator that applies POST_ONLY enforcement to REST client methods.
    
    This decorator wraps all order-related methods in a REST client class
    to ensure POST_ONLY behavior.
    
    Args:
        cls: The REST client class to decorate
        
    Returns:
        Modified class with POST_ONLY enforcement
    """
    
    # Methods that should be wrapped for POST_ONLY enforcement
    order_methods = ['submit_order', 'update_order', 'cancel_order']
    
    for method_name in order_methods:
        if hasattr(cls, method_name):
            original_method = getattr(cls, method_name)
            wrapped_method = post_only_enforcer(original_method)
            setattr(cls, method_name, wrapped_method)
    
    return cls


def post_only_websocket(cls: type) -> type:
    """
    Class decorator that applies POST_ONLY enforcement to WebSocket client methods.
    
    This decorator wraps all order-related methods in a WebSocket client class
    to ensure POST_ONLY behavior.
    
    Args:
        cls: The WebSocket client class to decorate
        
    Returns:
        Modified class with POST_ONLY enforcement
    """
    
    # Methods that should be wrapped for POST_ONLY enforcement
    order_methods = ['submit_order', 'update_order', 'cancel_order']
    
    for method_name in order_methods:
        if hasattr(cls, method_name):
            original_method = getattr(cls, method_name)
            wrapped_method = post_only_enforcer(original_method)
            setattr(cls, method_name, wrapped_method)
    
    # Also check for inputs attribute (WebSocket client has inputs.submit_order)
    if hasattr(cls, 'inputs'):
        inputs_cls = getattr(cls, 'inputs')
        if inputs_cls and hasattr(inputs_cls, 'submit_order'):
            original_submit = getattr(inputs_cls, 'submit_order')
            wrapped_submit = post_only_enforcer(original_submit)
            setattr(inputs_cls, 'submit_order', wrapped_submit)
    
    return cls


class PostOnlyMethodWrapper:
    """
    A wrapper class that can be used to wrap individual methods or objects
    to enforce POST_ONLY behavior.
    """
    
    def __init__(self, wrapped_object: Any):
        """
        Initialize the wrapper with an object to wrap.
        
        Args:
            wrapped_object: The object (method, class instance, etc.) to wrap
        """
        self._wrapped = wrapped_object
    
    def __getattr__(self, name: str) -> Any:
        """
        Intercept attribute access to apply POST_ONLY enforcement.
        
        Args:
            name: Name of the attribute being accessed
            
        Returns:
            The attribute, potentially wrapped with POST_ONLY enforcement
        """
        attr = getattr(self._wrapped, name)
        
        # If it's an order-related method, wrap it
        if callable(attr) and ('order' in name.lower() or 'submit' in name.lower()):
            return post_only_enforcer(attr)
        
        return attr
    
    def __call__(self, *args, **kwargs):
        """
        If the wrapped object is callable, ensure POST_ONLY enforcement.
        """
        if callable(self._wrapped):
            # Check if this looks like an order submission
            if any('order' in str(arg).lower() for arg in args) or \
               any('order' in key.lower() for key in kwargs.keys()):
                kwargs = _validate_and_modify_order_params(**kwargs)
            
            return self._wrapped(*args, **kwargs)
        
        raise TypeError(f"'{type(self._wrapped).__name__}' object is not callable")
