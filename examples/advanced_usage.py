"""
Advanced usage examples and market-making strategies
"""

import os
import asyncio
import time
from typing import List, Dict, Any
from bfx_postonly import PostOnlyClient
from bfx_postonly.utils import combine_flags


class SimpleMarketMaker:
    """
    A simple market-making bot using the POST-ONLY wrapper
    """
    
    def __init__(self, symbol: str = "tBTCUSD", spread: float = 0.01):
        """
        Initialize the market maker
        
        Args:
            symbol: Trading pair to make markets for
            spread: Spread percentage (0.01 = 1%)
        """
        self.symbol = symbol
        self.spread = spread
        self.client = PostOnlyClient(
            api_key=os.getenv("BFX_API_KEY"),
            api_secret=os.getenv("BFX_API_SECRET")
        )
        self.active_orders: Dict[str, Any] = {}
        
    def calculate_order_prices(self, mid_price: float, order_size: float) -> tuple:
        """
        Calculate bid and ask prices with spread
        
        Args:
            mid_price: Current mid price
            order_size: Size of orders to place
            
        Returns:
            Tuple of (bid_price, ask_price, bid_amount, ask_amount)
        """
        half_spread = self.spread / 2
        bid_price = mid_price * (1 - half_spread)
        ask_price = mid_price * (1 + half_spread)
        
        return bid_price, ask_price, order_size, -order_size
    
    def place_orders(self, mid_price: float, order_size: float = 0.001):
        """
        Place bid and ask orders around the mid price
        
        Args:
            mid_price: Current mid price
            order_size: Size of each order
        """
        bid_price, ask_price, bid_amount, ask_amount = self.calculate_order_prices(
            mid_price, order_size
        )
        
        try:
            # Place bid order (buy)
            bid_notification = self.client.submit_limit_order(
                symbol=self.symbol,
                amount=bid_amount,
                price=bid_price,
                flags=combine_flags("POST_ONLY", "HIDDEN")  # Hidden POST_ONLY order
            )
            
            if bid_notification.status == "SUCCESS":
                bid_order = bid_notification.data
                self.active_orders[bid_order.id] = {
                    'type': 'bid',
                    'order': bid_order,
                    'timestamp': time.time()
                }
                print(f"Placed bid: {bid_amount} @ {bid_price}")
            
            # Place ask order (sell)
            ask_notification = self.client.submit_limit_order(
                symbol=self.symbol,
                amount=ask_amount,
                price=ask_price,
                flags=combine_flags("POST_ONLY", "HIDDEN")  # Hidden POST_ONLY order
            )
            
            if ask_notification.status == "SUCCESS":
                ask_order = ask_notification.data
                self.active_orders[ask_order.id] = {
                    'type': 'ask',
                    'order': ask_order,
                    'timestamp': time.time()
                }
                print(f"Placed ask: {ask_amount} @ {ask_price}")
                
        except Exception as e:
            print(f"Error placing orders: {e}")
    
    def cancel_old_orders(self, max_age_seconds: int = 300):
        """
        Cancel orders older than specified age
        
        Args:
            max_age_seconds: Maximum age of orders in seconds
        """
        current_time = time.time()
        orders_to_cancel = []
        
        for order_id, order_info in self.active_orders.items():
            age = current_time - order_info['timestamp']
            if age > max_age_seconds:
                orders_to_cancel.append(order_id)
        
        for order_id in orders_to_cancel:
            try:
                # Cancel the order
                self.client.rest.auth.cancel_order(id=order_id)
                print(f"Cancelled old order: {order_id}")
                del self.active_orders[order_id]
            except Exception as e:
                print(f"Error cancelling order {order_id}: {e}")


async def websocket_market_maker():
    """
    Market maker using WebSocket for real-time updates
    """
    client = PostOnlyClient(
        api_key=os.getenv("BFX_API_KEY"),
        api_secret=os.getenv("BFX_API_SECRET")
    )
    
    symbol = "tBTCUSD"
    current_ticker = None
    orders_placed = False
    
    @client.wss.on("authenticated")
    async def on_authenticated(data):
        print(f"Authenticated as user {data['userId']}")
        # Subscribe to ticker updates
        await client.wss.subscribe("ticker", symbol=symbol)
    
    @client.wss.on("ticker_update")
    async def on_ticker_update(subscription, ticker):
        nonlocal current_ticker, orders_placed
        current_ticker = ticker
        
        # Simple strategy: place orders when we get the first ticker
        if not orders_placed:
            mid_price = (ticker.bid + ticker.ask) / 2
            
            try:
                # Place a small buy order below market
                await client.submit_limit_order_async(
                    symbol=symbol,
                    amount=0.001,  # Buy 0.001 BTC
                    price=mid_price * 0.995  # 0.5% below mid
                )
                
                # Place a small sell order above market
                await client.submit_limit_order_async(
                    symbol=symbol,
                    amount=-0.001,  # Sell 0.001 BTC
                    price=mid_price * 1.005  # 0.5% above mid
                )
                
                orders_placed = True
                print(f"Placed market making orders around {mid_price}")
                
            except Exception as e:
                print(f"Error placing orders: {e}")
    
    @client.wss.on("order_new")
    def on_order_new(order):
        print(f"New order: {order.symbol} - {order.amount} @ {order.price}")
    
    @client.wss.on("order_update")
    def on_order_update(order):
        print(f"Order update: {order.id} - Status: {order.status}")
    
    @client.wss.on("execution")
    def on_execution(execution):
        print(f"Execution: {execution.symbol} - {execution.exec_amount} @ {execution.exec_price}")
        # When an order is filled, we could place a new one
    
    # Run the client
    client.wss.run()


def portfolio_rebalancing_example():
    """
    Example of using POST_ONLY orders for portfolio rebalancing
    """
    client = PostOnlyClient(
        api_key=os.getenv("BFX_API_KEY"),
        api_secret=os.getenv("BFX_API_SECRET")
    )
    
    # Define target portfolio weights
    target_portfolio = {
        "tBTCUSD": 0.6,   # 60% BTC
        "tETHUSD": 0.3,   # 30% ETH
        "tLTCUSD": 0.1    # 10% LTC
    }
    
    # Simulated current portfolio (you'd get this from your actual positions)
    current_portfolio = {
        "tBTCUSD": 0.7,   # Currently 70% BTC
        "tETHUSD": 0.2,   # Currently 20% ETH
        "tLTCUSD": 0.1    # Currently 10% LTC
    }
    
    # Calculate rebalancing trades
    rebalancing_trades = {}
    for symbol in target_portfolio:
        target_weight = target_portfolio[symbol]
        current_weight = current_portfolio.get(symbol, 0)
        weight_diff = target_weight - current_weight
        rebalancing_trades[symbol] = weight_diff
    
    print("Rebalancing trades needed:")
    for symbol, weight_diff in rebalancing_trades.items():
        if abs(weight_diff) > 0.01:  # Only rebalance if difference > 1%
            print(f"{symbol}: {weight_diff:+.2%}")
            
            # In a real implementation, you'd:
            # 1. Get current prices
            # 2. Calculate actual amounts to trade
            # 3. Place POST_ONLY limit orders slightly away from market
            # 4. Monitor fills and adjust as needed


def grid_trading_example():
    """
    Example of a grid trading strategy using POST_ONLY orders
    """
    client = PostOnlyClient(
        api_key=os.getenv("BFX_API_KEY"),
        api_secret=os.getenv("BFX_API_SECRET")
    )
    
    symbol = "tBTCUSD"
    base_price = 30000.0  # Center price for the grid
    grid_spacing = 0.005  # 0.5% spacing between grid levels
    grid_size = 0.001     # Amount per grid level
    num_levels = 5        # Number of levels above and below
    
    print(f"Setting up grid around {base_price} with {num_levels} levels")
    
    # Place buy orders below base price
    for i in range(1, num_levels + 1):
        price = base_price * (1 - grid_spacing * i)
        try:
            notification = client.submit_limit_order(
                symbol=symbol,
                amount=grid_size,  # Buy order
                price=price
            )
            if notification.status == "SUCCESS":
                print(f"Grid buy level {i}: {grid_size} @ {price}")
        except Exception as e:
            print(f"Error placing buy grid level {i}: {e}")
    
    # Place sell orders above base price  
    for i in range(1, num_levels + 1):
        price = base_price * (1 + grid_spacing * i)
        try:
            notification = client.submit_limit_order(
                symbol=symbol,
                amount=-grid_size,  # Sell order
                price=price
            )
            if notification.status == "SUCCESS":
                print(f"Grid sell level {i}: {-grid_size} @ {price}")
        except Exception as e:
            print(f"Error placing sell grid level {i}: {e}")


if __name__ == "__main__":
    print("=== Simple Market Maker Example ===")
    mm = SimpleMarketMaker()
    # mm.place_orders(30000.0)  # Uncomment to place actual orders
    
    print("\n=== Portfolio Rebalancing Example ===")
    portfolio_rebalancing_example()
    
    print("\n=== Grid Trading Example ===")
    # grid_trading_example()  # Uncomment to place actual orders
    
    print("\n=== WebSocket Market Maker Example ===")
    print("(Uncomment the line below to run WebSocket market maker)")
    # asyncio.run(websocket_market_maker())
