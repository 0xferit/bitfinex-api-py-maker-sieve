"""
Utility functions for the POST-ONLY wrapper
"""

from typing import Dict, Any, Union
import logging

# Set up logging
logger = logging.getLogger(__name__)


def is_limit_order(order_type: str) -> bool:
    """
    Check if an order type is a limit order.
    
    Args:
        order_type: The order type string (e.g., "EXCHANGE LIMIT", "LIMIT")
        
    Returns:
        True if it's a limit order, False otherwise
    """
    if not order_type:
        return False
    
    order_type_upper = order_type.upper()
    return 'LIMIT' in order_type_upper and 'MARKET' not in order_type_upper


def has_post_only_flag(flags: Union[int, None]) -> bool:
    """
    Check if the POST_ONLY flag is set in the flags parameter.
    
    Args:
        flags: The flags integer or None
        
    Returns:
        True if POST_ONLY flag is set, False otherwise
    """
    if flags is None:
        return False
    
    POST_ONLY_FLAG = 4096  # 0x1000
    return bool(flags & POST_ONLY_FLAG)


def add_post_only_flag(flags: Union[int, None] = None) -> int:
    """
    Add the POST_ONLY flag to existing flags.
    
    Args:
        flags: Existing flags integer or None
        
    Returns:
        Flags with POST_ONLY flag added
    """
    POST_ONLY_FLAG = 4096  # 0x1000
    
    if flags is None:
        return POST_ONLY_FLAG
    
    return flags | POST_ONLY_FLAG


def validate_order_parameters(params: Dict[str, Any]) -> None:
    """
    Validate that order parameters are suitable for POST_ONLY enforcement.
    
    Args:
        params: Dictionary of order parameters
        
    Raises:
        ValueError: If parameters are invalid
    """
    required_params = ['type', 'symbol', 'amount']
    
    for param in required_params:
        if param not in params:
            raise ValueError(f"Required parameter '{param}' is missing")
    
    # Validate order type
    if not is_limit_order(params['type']):
        raise ValueError(f"Invalid order type for POST_ONLY: {params['type']}")
    
    # Validate amount
    try:
        amount = float(params['amount'])
        if amount == 0:
            raise ValueError("Order amount cannot be zero")
    except (ValueError, TypeError):
        raise ValueError(f"Invalid amount: {params['amount']}")
    
    # For limit orders, price is required
    if 'price' not in params:
        raise ValueError("Price is required for limit orders")
    
    try:
        price = float(params['price'])
        if price <= 0:
            raise ValueError("Price must be positive")
    except (ValueError, TypeError):
        raise ValueError(f"Invalid price: {params['price']}")


def format_order_info(params: Dict[str, Any]) -> str:
    """
    Format order parameters into a readable string for logging.
    
    Args:
        params: Dictionary of order parameters
        
    Returns:
        Formatted string representation of the order
    """
    try:
        order_type = params.get('type', 'UNKNOWN')
        symbol = params.get('symbol', 'UNKNOWN')
        amount = params.get('amount', 'UNKNOWN')
        price = params.get('price', 'UNKNOWN')
        flags = params.get('flags', 0)
        
        post_only_status = "POST_ONLY" if has_post_only_flag(flags) else "NOT POST_ONLY"
        
        return (f"{order_type} order for {symbol}: "
                f"amount={amount}, price={price}, "
                f"flags={flags} ({post_only_status})")
    
    except Exception as e:
        logger.warning(f"Error formatting order info: {e}")
        return str(params)


def get_bitfinex_flags() -> Dict[str, int]:
    """
    Get a dictionary of known Bitfinex order flags.
    
    Returns:
        Dictionary mapping flag names to their integer values
    """
    return {
        'HIDDEN': 64,           # 0x40
        'CLOSE': 512,           # 0x200  
        'REDUCE_ONLY': 1024,    # 0x400
        'POST_ONLY': 4096,      # 0x1000
        'OCO': 16384,           # 0x4000
        'NO_VWR': 262144,       # 0x40000
    }


def combine_flags(*flag_names: str) -> int:
    """
    Combine multiple Bitfinex flags into a single integer.
    
    Args:
        *flag_names: Names of flags to combine
        
    Returns:
        Combined flags as integer
        
    Raises:
        ValueError: If an unknown flag name is provided
    """
    flags_dict = get_bitfinex_flags()
    combined = 0
    
    for flag_name in flag_names:
        flag_name_upper = flag_name.upper()
        if flag_name_upper not in flags_dict:
            raise ValueError(f"Unknown flag: {flag_name}")
        combined |= flags_dict[flag_name_upper]
    
    return combined
