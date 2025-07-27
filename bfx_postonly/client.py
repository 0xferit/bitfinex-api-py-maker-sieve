"""
POST-ONLY validation wrapper for Bitfinex API.
Validates orders but never modifies them.
"""

from bfxapi import Client as BfxClient


class PostOnlyError(Exception):
    """Raised when orders don't meet POST_ONLY requirements"""
    pass


def validate_post_only(**kwargs):
    """Validate order has POST_ONLY flag (4096) and is EXCHANGE LIMIT type"""
    order_type = kwargs.get('type', '').upper()
    
    # Only allow limit orders
    if 'LIMIT' not in order_type or 'MARKET' in order_type:
        raise PostOnlyError(f"Only limit orders allowed, got: {order_type}")
    
    # Require POST_ONLY flag (4096) to be set
    flags = kwargs.get('flags', 0)
    if not (flags & 4096):
        raise PostOnlyError(f"POST_ONLY flag (4096) required but not set, got flags: {flags}")


class PostOnlyClient:
    """Bitfinex client that validates POST_ONLY requirements before transmission"""
    
    def __init__(self, api_key: str, api_secret: str, **kwargs):
        self._client = BfxClient(api_key=api_key, api_secret=api_secret, **kwargs)
        
        # Wrap REST submit_order with validation
        original_submit = self._client.rest.auth.submit_order
        def rest_submit(**params):
            validate_post_only(**params)
            return original_submit(**params)
        self._client.rest.auth.submit_order = rest_submit
        
        # Wrap WebSocket submit_order with validation if available
        if hasattr(self._client.wss, 'inputs') and hasattr(self._client.wss.inputs, 'submit_order'):
            original_wss_submit = self._client.wss.inputs.submit_order
            
            async def wss_submit(**params):
                validate_post_only(**params)
                return await original_wss_submit(**params)
            
            self._client.wss.inputs.submit_order = wss_submit
    
    @property
    def rest(self):
        return self._client.rest
    
    @property
    def wss(self):
        return self._client.wss
    
    def submit_limit_order(self, symbol: str, amount: float, price: float, **kwargs):
        """Submit limit order. Requires flags=4096 (POST_ONLY)"""
        return self.rest.auth.submit_order(
            type="EXCHANGE LIMIT",
            symbol=symbol,
            amount=amount,
            price=price,
            **kwargs
        )
    
    async def submit_limit_order_async(self, symbol: str, amount: float, price: float, **kwargs):
        """Submit limit order via WebSocket. Requires flags=4096 (POST_ONLY)"""
        return await self.wss.inputs.submit_order(
            type="EXCHANGE LIMIT",
            symbol=symbol,
            amount=amount,
            price=price,
            **kwargs
        )
    
    def __getattr__(self, name):
        return getattr(self._client, name)