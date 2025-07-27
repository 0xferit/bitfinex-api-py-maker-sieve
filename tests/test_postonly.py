"""Test suite for the POST-ONLY wrapper"""

from unittest.mock import Mock, patch

import pytest

from bfx_postonly import (
    PostOnlyClient,
    PostOnlyError,
    is_limit_order,
    validate_post_only,
)


class TestLimitOrderDetection:
    """Test is_limit_order function"""

    def test_is_limit_order_success(self):
        """Test limit order detection"""
        assert is_limit_order("LIMIT")
        assert is_limit_order("EXCHANGE LIMIT")
        assert is_limit_order("STOP LIMIT")
        assert is_limit_order("EXCHANGE STOP LIMIT")
        assert is_limit_order("limit")  # case insensitive
        assert is_limit_order("exchange limit")  # case insensitive

    def test_is_limit_order_failure(self):
        """Test non-limit order detection"""
        assert not is_limit_order("MARKET")
        assert not is_limit_order("EXCHANGE MARKET")
        assert not is_limit_order("STOP")
        assert not is_limit_order("EXCHANGE STOP")
        assert not is_limit_order("FOK")
        assert not is_limit_order("IOC")
        assert not is_limit_order("")


class TestValidation:
    """Test validation functions"""

    def test_validate_post_only_success(self):
        """Test successful POST_ONLY validation on limit orders"""
        # Valid limit orders with POST_ONLY flag
        validate_post_only(type="EXCHANGE LIMIT", flags=4096)
        validate_post_only(type="LIMIT", flags=4096)
        validate_post_only(type="STOP LIMIT", flags=4096)
        validate_post_only(type="EXCHANGE STOP LIMIT", flags=4096)

    def test_validate_post_only_rejects_non_limit_orders(self):
        """Test validation rejects non-limit orders"""
        with pytest.raises(PostOnlyError, match="Only limit orders permitted"):
            validate_post_only(type="EXCHANGE MARKET", flags=4096)

        with pytest.raises(PostOnlyError, match="Only limit orders permitted"):
            validate_post_only(type="MARKET", flags=4096)

        with pytest.raises(PostOnlyError, match="Only limit orders permitted"):
            validate_post_only(type="STOP", flags=4096)

        with pytest.raises(PostOnlyError, match="Only limit orders permitted"):
            validate_post_only(type="FOK", flags=4096)

    def test_validate_post_only_missing_flag(self):
        """Test validation rejects limit orders without POST_ONLY flag"""
        with pytest.raises(PostOnlyError, match="POST_ONLY flag \\(4096\\) required"):
            validate_post_only(type="EXCHANGE LIMIT", flags=0)

        with pytest.raises(PostOnlyError, match="POST_ONLY flag \\(4096\\) required"):
            validate_post_only(type="LIMIT", flags=64)  # Only HIDDEN flag

    def test_validate_post_only_combined_flags(self):
        """Test validation accepts POST_ONLY combined with other flags"""
        # POST_ONLY + HIDDEN
        validate_post_only(type="EXCHANGE LIMIT", flags=4096 | 64)

        # POST_ONLY + REDUCE_ONLY
        validate_post_only(type="LIMIT", flags=4096 | 1024)


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
    def test_submit_limit_order_passes_through(self, mock_bfx_client):
        """Test convenience method passes parameters through and validates"""
        mock_client_instance = Mock()
        mock_rest = Mock()
        mock_rest.auth = Mock()

        # Create a mock that tracks calls
        original_submit = Mock(return_value="success")
        mock_rest.auth.submit_order = original_submit

        mock_client_instance.rest = mock_rest
        mock_client_instance.wss = Mock()
        mock_bfx_client.return_value = mock_client_instance

        client = PostOnlyClient(api_key="test", api_secret="test")

        # Valid convenience method call should work
        result = client.submit_limit_order("tBTCUSD", 0.001, 30000.0, flags=4096)

        # Verify the underlying method was called and returned the expected result
        assert result == "success"
        original_submit.assert_called_once()

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

        # Valid limit order with POST_ONLY flag should pass
        client.rest.auth.submit_order(
            type="EXCHANGE LIMIT",
            symbol="tBTCUSD",
            amount=0.001,
            price=30000.0,
            flags=4096,
        )

        # Invalid limit order without POST_ONLY flag should fail
        with pytest.raises(PostOnlyError):
            client.rest.auth.submit_order(
                type="EXCHANGE LIMIT",
                symbol="tBTCUSD",
                amount=0.001,
                price=30000.0,
                flags=0,
            )

        # Non-limit orders should be rejected
        with pytest.raises(PostOnlyError):
            client.rest.auth.submit_order(
                type="EXCHANGE MARKET",
                symbol="tBTCUSD",
                amount=0.001,
                flags=4096,
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

        # This should work - valid limit order with POST_ONLY flag
        client.rest.auth.submit_order(
            type="EXCHANGE LIMIT",
            symbol="tBTCUSD",
            amount=0.001,
            price=30000.0,
            flags=4096,
        )

        # This should fail - limit order without POST_ONLY flag
        with pytest.raises(PostOnlyError):
            client.rest.auth.submit_order(
                type="EXCHANGE LIMIT", symbol="tBTCUSD", amount=0.001, price=30000.0
            )

        # This should fail - non-limit order
        with pytest.raises(PostOnlyError):
            client.rest.auth.submit_order(
                type="EXCHANGE MARKET", symbol="tBTCUSD", amount=0.001, flags=4096
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

        # Valid WebSocket limit order should work
        await client.wss.inputs.submit_order(
            type="EXCHANGE LIMIT",
            symbol="tETHUSD",
            amount=0.1,
            price=2000.0,
            flags=4096,
        )

        # Invalid WebSocket order should fail - non-limit type
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
