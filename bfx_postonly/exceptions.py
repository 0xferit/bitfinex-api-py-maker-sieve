"""
Custom exceptions for the POST-ONLY wrapper
"""


class PostOnlyViolationError(Exception):
    """
    Raised when a limit order is attempted without the POST_ONLY flag.
    
    This exception is thrown to prevent orders that could potentially
    become taker orders, ensuring all limit orders are maker-only.
    """
    pass


class InvalidOrderTypeError(Exception):
    """
    Raised when an unsupported order type is used.
    
    This wrapper is designed specifically for limit orders with POST_ONLY enforcement.
    """
    pass


class ConfigurationError(Exception):
    """
    Raised when there's an error in the wrapper configuration.
    """
    pass
