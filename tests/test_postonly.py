"""Test suite for the POST-ONLY wrapper"""

from unittest.mock import Mock, patch

import pytest

from bfx_postonly import PostOnlyClient, PostOnlyError, validate_post_only


class TestValidation:
    """Test validation functions"""

    def test_validate_post_only_success(self):
        """Test successful POST_ONLY validation"""
        # Valid order with POST_ONLY flag
        validate_post_only(
            type="EXCHANGE LIMIT",
            symbol="tBTCUSD",
            amount=0.001,
            price=30000.0,
            flags=4096,  # POST_ONLY flag
        )

    def test_validate_post_only_invalid_type(self):
        """Test validation rejects non-EXCHANGE LIMIT orders"""
        with pytest.raises(PostOnlyError, match="Only EXCHANGE LIMIT orders allowed"):
            validate_post_only(type="EXCHANGE MARKET", flags=4096)

        with pytest.raises(PostOnlyError, match="Only EXCHANGE LIMIT orders allowed"):
            validate_post_only(type="LIMIT", flags=4096)

    def test_validate_post_only_missing_flag(self):
        """Test validation rejects orders without POST_ONLY flag"""
        with pytest.raises(PostOnlyError, match="POST_ONLY flag \\(4096\\) required"):
            validate_post_only(type="EXCHANGE LIMIT", flags=0)

        with pytest.raises(PostOnlyError, match="POST_ONLY flag \\(4096\\) required"):
            validate_post_only(type="EXCHANGE LIMIT", flags=64)  # Only HIDDEN flag

    def test_validate_post_only_combined_flags(self):
        """Test validation accepts POST_ONLY combined with other flags"""
        # POST_ONLY + HIDDEN
        validate_post_only(type="EXCHANGE LIMIT", flags=4096 | 64)

        # POST_ONLY + REDUCE_ONLY
        validate_post_only(type="EXCHANGE LIMIT", flags=4096 | 1024)

    def test_validate_post_only_invalid_inputs(self):
        """Test validation rejects invalid input types"""
        with pytest.raises(PostOnlyError, match="Order type must be a string"):
            validate_post_only(type=None, flags=4096)

        with pytest.raises(PostOnlyError, match="Flags must be an integer"):
            validate_post_only(type="EXCHANGE LIMIT", flags="4096")


class TestPostOnlyClient:
    """Test the main PostOnlyClient class"""

    @patch("bfx_postonly.client.BfxClient")
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
        client = PostOnlyClient(api_key="test_key", api_secret="test_secret")

        # Verify initialization
        assert client.rest is not None
        assert client.wss is not None

    @patch("bfx_postonly.client.BfxClient")
    def test_submit_limit_order_validation(self, mock_bfx_client):
        """Test limit order validation in helper method"""
        mock_client_instance = Mock()
        mock_rest = Mock()
        mock_rest.auth = Mock()
        mock_client_instance.rest = mock_rest
        mock_client_instance.wss = Mock()
        mock_bfx_client.return_value = mock_client_instance

        client = PostOnlyClient(api_key="test", api_secret="test")

        # Test invalid inputs are caught by helper method
        with pytest.raises(PostOnlyError, match="Symbol must be a non-empty string"):
            client.submit_limit_order("", 0.001, 30000.0)

        with pytest.raises(PostOnlyError, match="Amount must be a non-zero number"):
            client.submit_limit_order("tBTCUSD", 0, 30000.0)

        with pytest.raises(PostOnlyError, match="Price must be a positive number"):
            client.submit_limit_order("tBTCUSD", 0.001, 0)

    @patch("bfx_postonly.client.BfxClient")
    def test_rest_submit_order_wrapper(self, mock_bfx_client):
        """Test that REST submit_order validates POST_ONLY"""
        mock_client_instance = Mock()
        mock_rest = Mock()
        mock_rest.auth = Mock()
        mock_rest.auth.submit_order = Mock()
        mock_client_instance.rest = mock_rest
        mock_client_instance.wss = Mock()
        mock_bfx_client.return_value = mock_client_instance

        client = PostOnlyClient(api_key="test", api_secret="test")

        # Valid order with POST_ONLY flag should pass
        client.rest.auth.submit_order(
            type="EXCHANGE LIMIT",
            symbol="tBTCUSD",
            amount=0.001,
            price=30000.0,
            flags=4096,
        )

        # Invalid order without POST_ONLY flag should fail
        with pytest.raises(PostOnlyError):
            client.rest.auth.submit_order(
                type="EXCHANGE LIMIT",
                symbol="tBTCUSD",
                amount=0.001,
                price=30000.0,
                flags=0,
            )


class TestIntegration:
    """Integration tests that test the complete flow"""

    @patch("bfx_postonly.client.BfxClient")
    def test_end_to_end_validation(self, mock_bfx_client):
        """Test end-to-end validation flow"""
        mock_client_instance = Mock()
        mock_rest = Mock()
        mock_rest.auth = Mock()

        # Mock successful response
        mock_response = Mock()
        mock_response.status = "SUCCESS"
        mock_rest.auth.submit_order.return_value = mock_response

        mock_client_instance.rest = mock_rest
        mock_client_instance.wss = Mock()
        mock_bfx_client.return_value = mock_client_instance

        client = PostOnlyClient(api_key="test", api_secret="test")

        # This should work - valid order with POST_ONLY flag
        client.rest.auth.submit_order(
            type="EXCHANGE LIMIT",
            symbol="tBTCUSD",
            amount=0.001,
            price=30000.0,
            flags=4096,
        )

        # This should fail - no POST_ONLY flag
        with pytest.raises(PostOnlyError):
            client.rest.auth.submit_order(
                type="EXCHANGE LIMIT", symbol="tBTCUSD", amount=0.001, price=30000.0
            )

    @pytest.mark.asyncio
    @patch("bfx_postonly.client.BfxClient")
    async def test_websocket_validation(self, mock_bfx_client):
        """Test WebSocket validation flow"""
        mock_client_instance = Mock()
        mock_rest = Mock()
        mock_rest.auth = Mock()
        mock_client_instance.rest = mock_rest

        # Mock WebSocket
        mock_wss = Mock()
        mock_inputs = Mock()

        async def mock_submit(**kwargs):
            return None

        mock_inputs.submit_order = mock_submit
        mock_wss.inputs = mock_inputs
        mock_client_instance.wss = mock_wss

        mock_bfx_client.return_value = mock_client_instance

        client = PostOnlyClient(api_key="test", api_secret="test")

        # Valid WebSocket order should work
        await client.wss.inputs.submit_order(
            type="EXCHANGE LIMIT",
            symbol="tETHUSD",
            amount=0.1,
            price=2000.0,
            flags=4096,
        )

        # Invalid WebSocket order should fail
        with pytest.raises(PostOnlyError):
            await client.wss.inputs.submit_order(
                type="EXCHANGE MARKET",
                symbol="tETHUSD",
                amount=0.1,
                price=2000.0,
                flags=4096,
            )


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])
