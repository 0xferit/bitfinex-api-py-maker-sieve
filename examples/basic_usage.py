"""
Examples demonstrating how to use the POST-ONLY wrapper
"""

import os
import asyncio
from bfx_postonly import PostOnlyClient
from bfx_postonly.exceptions import PostOnlyViolationError


def basic_rest_example():
    """
    Example of using the POST-ONLY client with REST API
    """
    # Initialize the client
    client = PostOnlyClient(
        api_key=os.getenv("BFX_API_KEY"),
        api_secret=os.getenv("BFX_API_SECRET")
    )
    
    try:
        # Submit a limit order (automatically gets POST_ONLY flag)
        notification = client.submit_limit_order(
            symbol="tBTCUSD",
            amount=0.001,  # Buy 0.001 BTC
            price=30000.0  # At $30,000
        )
        
        if notification.status == "SUCCESS":
            order = notification.data
            print(f"Order submitted successfully: {order.id}")
            print(f"Symbol: {order.symbol}")
            print(f"Amount: {order.amount}")
            print(f"Price: {order.price}")
        else:
            print(f"Order failed: {notification.text}")
            
    except PostOnlyViolationError as e:
        print(f"POST_ONLY violation: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")


async def websocket_example():
    """
    Example of using the POST-ONLY client with WebSocket API
    """
    # Initialize the client
    client = PostOnlyClient(
        api_key=os.getenv("BFX_API_KEY"),
        api_secret=os.getenv("BFX_API_SECRET")
    )
    
    @client.wss.on("authenticated")
    async def on_authenticated(data):
        print(f"Authenticated as user {data['userId']}")
        
        try:
            # Submit a limit order via WebSocket
            await client.submit_limit_order_async(
                symbol="tETHUSD",
                amount=-0.1,  # Sell 0.1 ETH
                price=2000.0  # At $2,000
            )
            print("Order submitted via WebSocket")
            
        except PostOnlyViolationError as e:
            print(f"POST_ONLY violation: {e}")
    
    @client.wss.on("order_new")
    def on_order_new(order):
        print(f"New order: {order.symbol} - {order.amount} @ {order.price}")
    
    @client.wss.on("on-req-notification")
    def on_notification(notification):
        if notification.status == "ERROR":
            print(f"Order error: {notification.text}")
    
    # Run the WebSocket client
    client.wss.run()


def direct_api_usage_example():
    """
    Example of using the wrapped client directly with the original API methods
    """
    client = PostOnlyClient(
        api_key=os.getenv("BFX_API_KEY"),
        api_secret=os.getenv("BFX_API_SECRET")
    )
    
    try:
        # This will automatically add POST_ONLY flag
        notification = client.rest.auth.submit_order(
            type="EXCHANGE LIMIT",
            symbol="tBTCUSD", 
            amount=0.001,
            price=30000.0
            # POST_ONLY flag will be automatically added
        )
        
        print(f"Order status: {notification.status}")
        
    except PostOnlyViolationError as e:
        print(f"Cannot submit order: {e}")


def error_handling_example():
    """
    Example demonstrating error handling
    """
    client = PostOnlyClient(
        api_key=os.getenv("BFX_API_KEY"),
        api_secret=os.getenv("BFX_API_SECRET")
    )
    
    # This will raise an error because market orders are not allowed
    try:
        client.rest.auth.submit_order(
            type="EXCHANGE MARKET",  # Market orders not allowed!
            symbol="tBTCUSD",
            amount=0.001
        )
    except PostOnlyViolationError as e:
        print(f"Expected error: {e}")
    
    # This will also raise an error
    try:
        client.submit_limit_order(
            symbol="tBTCUSD",
            amount=0,  # Invalid amount
            price=30000.0
        )
    except ValueError as e:
        print(f"Validation error: {e}")


def configuration_example():
    """
    Example showing client configuration options
    """
    client = PostOnlyClient(
        api_key=os.getenv("BFX_API_KEY"),
        api_secret=os.getenv("BFX_API_SECRET")
    )
    
    # Get client information
    info = client.get_client_info()
    print("Client Configuration:")
    for key, value in info.items():
        print(f"  {key}: {value}")


if __name__ == "__main__":
    print("=== Basic REST Example ===")
    basic_rest_example()
    
    print("\n=== Configuration Example ===")
    configuration_example()
    
    print("\n=== Error Handling Example ===")
    error_handling_example()
    
    print("\n=== WebSocket Example ===")
    print("(Uncomment the line below to run WebSocket example)")
    # asyncio.run(websocket_example())
