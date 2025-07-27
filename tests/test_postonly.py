"""
Test suite for the POST-ONLY wrapper
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import asyncio

from bfx_postonly import PostOnlyClient
from bfx_postonly.decorators import post_only_enforcer, _validate_and_modify_order_params
from bfx_postonly.exceptions import PostOnlyViolationError, InvalidOrderTypeError
from bfx_postonly.utils import (
    is_limit_order, 
    has_post_only_flag, 
    add_post_only_flag,
    validate_order_parameters,
    combine_flags,
    get_bitfinex_flags
)


class TestUtils:
    """Test utility functions"""
    
    def test_is_limit_order(self):
        """Test limit order detection"""
        assert is_limit_order("EXCHANGE LIMIT") == True
        assert is_limit_order("LIMIT") == True
        assert is_limit_order("EXCHANGE MARKET") == False
        assert is_limit_order("MARKET") == False
        assert is_limit_order("STOP") == False
        assert is_limit_order("") == False
        assert is_limit_order(None) == False
    
    def test_has_post_only_flag(self):
        """Test POST_ONLY flag detection"""
        POST_ONLY_FLAG = 4096
        
        assert has_post_only_flag(POST_ONLY_FLAG) == True
        assert has_post_only_flag(POST_ONLY_FLAG | 64) == True  # POST_ONLY + HIDDEN
        assert has_post_only_flag(64) == False  # Just HIDDEN
        assert has_post_only_flag(0) == False
        assert has_post_only_flag(None) == False
    
    def test_add_post_only_flag(self):
        """Test adding POST_ONLY flag"""
        POST_ONLY_FLAG = 4096
        
        assert add_post_only_flag() == POST_ONLY_FLAG
        assert add_post_only_flag(None) == POST_ONLY_FLAG
        assert add_post_only_flag(0) == POST_ONLY_FLAG
        assert add_post_only_flag(64) == POST_ONLY_FLAG | 64  # HIDDEN + POST_ONLY
    
    def test_validate_order_parameters(self):
        """Test order parameter validation"""
        # Valid parameters
        valid_params = {
            'type': 'EXCHANGE LIMIT',
            'symbol': 'tBTCUSD',
            'amount': 0.001,
            'price': 30000.0
        }
        validate_order_parameters(valid_params)  # Should not raise
        
        # Missing required parameter
        with pytest.raises(ValueError, match="Required parameter 'type' is missing"):
            validate_order_parameters({})
        
        # Invalid order type
        with pytest.raises(ValueError, match="Invalid order type"):
            invalid_params = valid_params.copy()
            invalid_params['type'] = 'MARKET'
            validate_order_parameters(invalid_params)
        
        # Invalid amount
        with pytest.raises(ValueError, match="Order amount cannot be zero"):
            invalid_params = valid_params.copy()
            invalid_params['amount'] = 0
            validate_order_parameters(invalid_params)
        
        # Missing price
        with pytest.raises(ValueError, match="Price is required"):
            invalid_params = valid_params.copy()
            del invalid_params['price']
            validate_order_parameters(invalid_params)
    
    def test_get_bitfinex_flags(self):
        """Test Bitfinex flags dictionary"""
        flags = get_bitfinex_flags()
        assert flags['POST_ONLY'] == 4096
        assert flags['HIDDEN'] == 64
        assert flags['REDUCE_ONLY'] == 1024
    
    def test_combine_flags(self):
        """Test flag combination"""
        assert combine_flags('POST_ONLY') == 4096
        assert combine_flags('HIDDEN', 'POST_ONLY') == 64 | 4096
        
        with pytest.raises(ValueError, match="Unknown flag"):
            combine_flags('INVALID_FLAG')


class TestDecorators:
    """Test decorator functions"""
    
    def test_validate_and_modify_order_params(self):
        """Test parameter validation and modification"""
        # Valid limit order
        params = {
            'type': 'EXCHANGE LIMIT',
            'symbol': 'tBTCUSD',
            'amount': 0.001,
            'price': 30000.0
        }
        result = _validate_and_modify_order_params(**params)
        assert has_post_only_flag(result['flags']) == True
        
        # Market order should raise exception
        with pytest.raises(InvalidOrderTypeError):
            _validate_and_modify_order_params(type='EXCHANGE MARKET')
        
        # Non-limit order should raise exception
        with pytest.raises(InvalidOrderTypeError):
            _validate_and_modify_order_params(type='STOP')
    
    def test_post_only_enforcer_sync(self):
        """Test POST_ONLY enforcer decorator for sync functions"""
        
        @post_only_enforcer
        def mock_submit_order(**kwargs):
            return kwargs
        
        # Should add POST_ONLY flag to limit orders
        result = mock_submit_order(
            type='EXCHANGE LIMIT',
            symbol='tBTCUSD',
            amount=0.001,
            price=30000.0
        )
        assert has_post_only_flag(result['flags']) == True
        
        # Should reject market orders
        with pytest.raises(InvalidOrderTypeError):
            mock_submit_order(type='EXCHANGE MARKET')
    
    @pytest.mark.asyncio
    async def test_post_only_enforcer_async(self):
        """Test POST_ONLY enforcer decorator for async functions"""
        
        @post_only_enforcer
        async def mock_submit_order_async(**kwargs):
            return kwargs
        
        # Should add POST_ONLY flag to limit orders
        result = await mock_submit_order_async(
            type='EXCHANGE LIMIT',
            symbol='tBTCUSD',
            amount=0.001,
            price=30000.0
        )
        assert has_post_only_flag(result['flags']) == True


class TestPostOnlyClient:
    """Test the main PostOnlyClient class"""
    
    @patch('bfx_postonly.client.BfxClient')
    def test_client_initialization(self, mock_bfx_client):
        """Test client initialization"""
        mock_client_instance = Mock()
        mock_bfx_client.return_value = mock_client_instance
        
        # Create mock REST and WebSocket clients
        mock_rest = Mock()
        mock_rest.auth = Mock()
        mock_rest.auth.submit_order = Mock()
        
        mock_wss = Mock()
        mock_wss.inputs = Mock()
        mock_wss.inputs.submit_order = Mock()
        
        mock_client_instance.rest = mock_rest
        mock_client_instance.wss = mock_wss
        
        # Initialize PostOnlyClient
        client = PostOnlyClient(
            api_key="test_key",
            api_secret="test_secret"
        )
        
        # Verify initialization
        assert client._api_key == "test_key"
        assert client._api_secret == "test_secret"
        assert client.rest is not None
        assert client.wss is not None
    
    @patch('bfx_postonly.client.BfxClient')
    def test_submit_limit_order(self, mock_bfx_client):
        """Test limit order submission"""
        # Setup mocks
        mock_client_instance = Mock()
        mock_rest = Mock()
        mock_rest.auth = Mock()
        
        # Mock successful order response
        mock_notification = Mock()
        mock_notification.status = "SUCCESS"
        mock_order = Mock()
        mock_order.id = "123456"
        mock_order.symbol = "tBTCUSD"
        mock_notification.data = mock_order
        
        mock_rest.auth.submit_order.return_value = mock_notification
        mock_client_instance.rest = mock_rest
        mock_bfx_client.return_value = mock_client_instance
        
        # Create client and submit order
        client = PostOnlyClient(api_key="test", api_secret="test")
        
        # The REST wrapper will modify the submit_order method
        # So we need to mock it properly
        client._rest_wrapper._original_submit_order = Mock(return_value=mock_notification)
        
        result = client.submit_limit_order(
            symbol="tBTCUSD",
            amount=0.001,
            price=30000.0
        )
        
        assert result.status == "SUCCESS"
    
    @patch('bfx_postonly.client.BfxClient')
    def test_invalid_order_rejection(self, mock_bfx_client):
        """Test that invalid orders are rejected"""
        mock_client_instance = Mock()
        mock_rest = Mock()
        mock_rest.auth = Mock()
        mock_client_instance.rest = mock_rest
        
        mock_wss = Mock()
        mock_wss.inputs = Mock()
        mock_client_instance.wss = mock_wss
        
        mock_bfx_client.return_value = mock_client_instance
        
        client = PostOnlyClient(api_key="test", api_secret="test")
        
        # Test invalid amount
        with pytest.raises(ValueError):
            client.submit_limit_order(
                symbol="tBTCUSD",
                amount=0,  # Invalid amount
                price=30000.0
            )
        
        # Test missing price
        with pytest.raises(ValueError):
            client.submit_limit_order(
                symbol="tBTCUSD",
                amount=0.001,
                price=0  # Invalid price
            )
    
    def test_get_client_info(self):
        """Test client info method"""
        with patch('bfx_postonly.client.BfxClient'):
            client = PostOnlyClient(api_key="test", api_secret="test")
            info = client.get_client_info()
            
            assert info['api_key_set'] == True
            assert info['post_only_enforced'] == True
            assert 'wrapper_version' in info


class TestIntegration:
    """Integration tests that test the complete flow"""
    
    @patch('bfx_postonly.client.BfxClient')
    def test_rest_order_flow(self, mock_bfx_client):
        """Test complete REST order submission flow"""
        # Setup comprehensive mocks
        mock_client_instance = Mock()
        mock_rest = Mock()
        mock_auth = Mock()
        
        # Mock the submit_order method to capture parameters
        submitted_params = {}
        def capture_submit_order(**kwargs):
            submitted_params.update(kwargs)
            mock_notification = Mock()
            mock_notification.status = "SUCCESS"
            mock_order = Mock()
            mock_order.id = "12345"
            mock_order.symbol = kwargs.get('symbol', 'tBTCUSD')
            mock_order.amount = kwargs.get('amount', 0.001)
            mock_order.price = kwargs.get('price', 30000.0)
            mock_notification.data = mock_order
            return mock_notification
        
        mock_auth.submit_order = Mock(side_effect=capture_submit_order)
        mock_rest.auth = mock_auth
        mock_client_instance.rest = mock_rest
        
        # Mock WebSocket client
        mock_wss = Mock()
        mock_wss.inputs = Mock()
        mock_client_instance.wss = mock_wss
        
        mock_bfx_client.return_value = mock_client_instance
        
        # Create client and submit order
        client = PostOnlyClient(api_key="test", api_secret="test")
        
        result = client.submit_limit_order(
            symbol="tBTCUSD",
            amount=0.001,
            price=30000.0
        )
        
        # Verify the order was submitted with POST_ONLY flag
        assert result.status == "SUCCESS"
        assert has_post_only_flag(submitted_params.get('flags', 0)) == True
        assert submitted_params['type'] == 'EXCHANGE LIMIT'
        assert submitted_params['symbol'] == 'tBTCUSD'
        assert submitted_params['amount'] == 0.001
        assert submitted_params['price'] == 30000.0
    
    @pytest.mark.asyncio
    @patch('bfx_postonly.client.BfxClient')
    async def test_websocket_order_flow(self, mock_bfx_client):
        """Test complete WebSocket order submission flow"""
        # Setup mocks
        mock_client_instance = Mock()
        mock_rest = Mock()
        mock_rest.auth = Mock()
        mock_client_instance.rest = mock_rest
        
        # Mock WebSocket with inputs
        mock_wss = Mock()
        mock_inputs = Mock()
        
        # Mock async submit_order
        submitted_params = {}
        async def capture_submit_order(**kwargs):
            submitted_params.update(kwargs)
            return None
        
        mock_inputs.submit_order = Mock(side_effect=capture_submit_order)
        mock_wss.inputs = mock_inputs
        mock_client_instance.wss = mock_wss
        
        mock_bfx_client.return_value = mock_client_instance
        
        # Create client and submit order
        client = PostOnlyClient(api_key="test", api_secret="test")
        
        await client.submit_limit_order_async(
            symbol="tETHUSD",
            amount=-0.1,
            price=2000.0
        )
        
        # Verify the order was submitted with POST_ONLY flag
        assert has_post_only_flag(submitted_params.get('flags', 0)) == True
        assert submitted_params['type'] == 'EXCHANGE LIMIT'
        assert submitted_params['symbol'] == 'tETHUSD'
        assert submitted_params['amount'] == -0.1
        assert submitted_params['price'] == 2000.0


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])
