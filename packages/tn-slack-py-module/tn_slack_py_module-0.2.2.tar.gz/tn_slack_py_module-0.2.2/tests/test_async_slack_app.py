"""Tests for AsyncSlackApp class."""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from tnslack import AsyncSlackApp, constants as slack_consts


class TestAsyncSlackApp:
    """Test cases for AsyncSlackApp class."""

    @pytest.mark.asyncio
    async def test_async_slack_interaction_consumer(self, async_slack_app, sample_payload):
        """Test async interaction consumption."""
        result_value = None
        
        async def async_handler(payload, params):
            nonlocal result_value
            result_value = payload["actions"][0]["value"]
            return "async_handled"

        async_slack_app.register_route(slack_consts.BLOCK_ACTIONS, async_handler, "test_action")
        result = await async_slack_app.async_slack_interaction_consumer(sample_payload)
        
        assert result == "async_handled"
        assert result_value == "test_value"

    @pytest.mark.asyncio
    async def test_async_view_submission_consumer(self, async_slack_app, sample_view_payload):
        """Test async view submission consumption."""
        received_context = None
        
        async def async_view_handler(payload, context):
            nonlocal received_context
            received_context = context
            return "async_view_handled"

        async_slack_app.register_route(slack_consts.VIEW_SUBMISSION, async_view_handler, "test_modal")
        result = await async_slack_app.async_slack_interaction_consumer(sample_view_payload)
        
        assert result == "async_view_handled"
        assert received_context == {"key": "value"}

    @pytest.mark.asyncio
    async def test_sync_handler_in_async_consumer(self, async_slack_app, sample_payload):
        """Test that sync handlers work in async consumer."""
        def sync_handler(payload, params):
            return "sync_in_async"

        async_slack_app.register_route(slack_consts.BLOCK_ACTIONS, sync_handler, "test_action")
        result = await async_slack_app.async_slack_interaction_consumer(sample_payload)
        
        assert result == "sync_in_async"

    @pytest.mark.asyncio
    @patch('tnslack.async_slack_app.AsyncWebClient')
    async def test_async_exchange_code_for_token(self, mock_async_web_client_class, async_slack_app):
        """Test async OAuth code exchange."""
        mock_client = AsyncMock()
        mock_async_web_client_class.return_value = mock_client
        mock_response = Mock()
        mock_response.data = {"access_token": "xoxb-test-token"}
        mock_client.oauth_v2_access.return_value = mock_response

        result = await async_slack_app.async_exchange_code_for_token("test_code")
        
        mock_client.oauth_v2_access.assert_called_once_with(
            client_id="test_client_id",
            client_secret="test_client_secret", 
            code="test_code",
            redirect_uri="https://example.com/auth"
        )
        mock_client.close.assert_called_once()
        assert result == {"access_token": "xoxb-test-token"}

    @pytest.mark.asyncio
    async def test_async_send_channel_message(self, async_slack_app):
        """Test async channel message sending."""
        mock_client = AsyncMock()
        mock_response = Mock()
        mock_response.data = {"ok": True, "ts": "1234567890.123456"}
        mock_client.chat_postMessage.return_value = mock_response
        
        with patch.object(async_slack_app, 'get_async_web_client', return_value=mock_client):
            result = await async_slack_app.async_send_channel_message(
                channel="#general",
                access_token="xoxb-test-token", 
                text="Async Hello",
                block_set=[{"type": "section", "text": {"type": "plain_text", "text": "Hello"}}]
            )
        
        mock_client.chat_postMessage.assert_called_once_with(
            channel="#general",
            text="Async Hello",
            blocks=[{"type": "section", "text": {"type": "plain_text", "text": "Hello"}}]
        )
        assert result == {"ok": True, "ts": "1234567890.123456"}

    @pytest.mark.asyncio
    async def test_async_send_ephemeral_message(self, async_slack_app):
        """Test async ephemeral message sending."""
        mock_client = AsyncMock()
        mock_response = Mock()
        mock_response.data = {"ok": True}
        mock_client.chat_postEphemeral.return_value = mock_response
        
        with patch.object(async_slack_app, 'get_async_web_client', return_value=mock_client):
            result = await async_slack_app.async_send_ephemeral_message(
                channel="#general",
                access_token="xoxb-test-token",
                user_id="U123456",
                text="Secret message"
            )
        
        mock_client.chat_postEphemeral.assert_called_once_with(
            channel="#general",
            user="U123456",
            text="Secret message",
            blocks=[]
        )
        assert result == {"ok": True}

    @pytest.mark.asyncio
    async def test_async_open_modal_from_trigger(self, async_slack_app):
        """Test async modal opening."""
        mock_client = AsyncMock()
        mock_response = Mock()
        mock_response.data = {"ok": True, "view": {"id": "V123"}}
        mock_client.views_open.return_value = mock_response
        
        view = {
            "type": "modal",
            "title": {"type": "plain_text", "text": "Test Modal"}
        }
        
        with patch.object(async_slack_app, 'get_async_web_client', return_value=mock_client):
            result = await async_slack_app.async_open_modal_from_trigger(
                trigger_id="trigger_123",
                view=view,
                access_token="xoxb-test-token"
            )
        
        mock_client.views_open.assert_called_once_with(
            trigger_id="trigger_123",
            view=view
        )
        assert result == {"ok": True, "view": {"id": "V123"}}

    @pytest.mark.asyncio
    async def test_async_update_modal(self, async_slack_app):
        """Test async modal updating."""
        mock_client = AsyncMock()
        mock_response = Mock()
        mock_response.data = {"ok": True}
        mock_client.views_update.return_value = mock_response
        
        view = {"type": "modal", "title": {"type": "plain_text", "text": "Updated"}}
        
        with patch.object(async_slack_app, 'get_async_web_client', return_value=mock_client):
            result = await async_slack_app.async_update_modal(
                view_id="V123",
                view=view,
                access_token="xoxb-test-token",
                hash_val="hash123"
            )
        
        mock_client.views_update.assert_called_once_with(
            view_id="V123",
            view=view,
            hash="hash123"
        )
        assert result == {"ok": True}

    @pytest.mark.asyncio
    async def test_async_publish_home_view(self, async_slack_app):
        """Test async home view publishing."""
        mock_client = AsyncMock()
        mock_response = Mock()
        mock_response.data = {"ok": True}
        mock_client.views_publish.return_value = mock_response
        
        view = {"type": "home", "blocks": []}
        
        with patch.object(async_slack_app, 'get_async_web_client', return_value=mock_client):
            result = await async_slack_app.async_publish_home_view(
                user_id="U123456",
                view=view,
                access_token="xoxb-test-token"
            )
        
        mock_client.views_publish.assert_called_once_with(
            user_id="U123456",
            view=view
        )
        assert result == {"ok": True}

    @pytest.mark.asyncio
    async def test_async_update_message(self, async_slack_app):
        """Test async message updating."""
        mock_client = AsyncMock()
        mock_response = Mock()
        mock_response.data = {"ok": True, "ts": "1234567890.123456"}
        mock_client.chat_update.return_value = mock_response
        
        with patch.object(async_slack_app, 'get_async_web_client', return_value=mock_client):
            result = await async_slack_app.async_update_message(
                channel="#general",
                timestamp="1234567890.123456",
                access_token="xoxb-test-token",
                text="Updated message",
                block_set=[{"type": "section", "text": {"type": "plain_text", "text": "Updated"}}]
            )
        
        mock_client.chat_update.assert_called_once_with(
            channel="#general",
            ts="1234567890.123456",
            text="Updated message",
            blocks=[{"type": "section", "text": {"type": "plain_text", "text": "Updated"}}]
        )
        assert result == {"ok": True, "ts": "1234567890.123456"}

    @pytest.mark.asyncio
    async def test_async_get_user_info(self, async_slack_app):
        """Test async user info retrieval."""
        mock_client = AsyncMock()
        mock_response = Mock()
        mock_response.data = {"ok": True, "user": {"id": "U123456", "name": "testuser"}}
        mock_client.users_info.return_value = mock_response
        
        with patch.object(async_slack_app, 'get_async_web_client', return_value=mock_client):
            result = await async_slack_app.async_get_user_info(
                user_id="U123456",
                access_token="xoxb-test-token"
            )
        
        mock_client.users_info.assert_called_once_with(user="U123456")
        assert result == {"ok": True, "user": {"id": "U123456", "name": "testuser"}}

    @pytest.mark.asyncio
    async def test_async_open_conversation(self, async_slack_app):
        """Test async conversation opening."""
        mock_client = AsyncMock()
        mock_response = Mock()
        mock_response.data = {"ok": True, "channel": {"id": "D123456"}}
        mock_client.conversations_open.return_value = mock_response
        
        with patch.object(async_slack_app, 'get_async_web_client', return_value=mock_client):
            # Test with single user
            result = await async_slack_app.async_open_conversation(
                users="U123456",
                access_token="xoxb-test-token"
            )
        
        mock_client.conversations_open.assert_called_once_with(users="U123456")
        assert result == {"ok": True, "channel": {"id": "D123456"}}

    @pytest.mark.asyncio
    async def test_async_open_conversation_multiple_users(self, async_slack_app):
        """Test async conversation opening with multiple users."""
        mock_client = AsyncMock()
        mock_response = Mock()
        mock_response.data = {"ok": True, "channel": {"id": "G123456"}}
        mock_client.conversations_open.return_value = mock_response
        
        with patch.object(async_slack_app, 'get_async_web_client', return_value=mock_client):
            result = await async_slack_app.async_open_conversation(
                users=["U123456", "U789012"],
                access_token="xoxb-test-token"
            )
        
        mock_client.conversations_open.assert_called_once_with(users="U123456,U789012")
        assert result == {"ok": True, "channel": {"id": "G123456"}}

    @pytest.mark.asyncio
    async def test_get_async_web_client_caching(self, async_slack_app):
        """Test that async web clients are cached."""
        token = "xoxb-test-token"
        
        client1 = async_slack_app.get_async_web_client(token)
        client2 = async_slack_app.get_async_web_client(token)
        
        assert client1 is client2
        assert token in async_slack_app._async_clients

    @pytest.mark.asyncio
    async def test_close_async_clients(self, async_slack_app):
        """Test closing async clients."""
        # Create some mock clients
        mock_client1 = AsyncMock()
        mock_client2 = AsyncMock()
        
        async_slack_app._async_clients = {
            "token1": mock_client1,
            "token2": mock_client2
        }
        
        await async_slack_app.close_async_clients()
        
        mock_client1.close.assert_called_once()
        mock_client2.close.assert_called_once()
        assert len(async_slack_app._async_clients) == 0

    @pytest.mark.asyncio
    async def test_async_context_manager(self, async_slack_app):
        """Test async context manager functionality."""
        mock_client = AsyncMock()
        async_slack_app._async_clients = {"token": mock_client}
        
        async with async_slack_app as app:
            assert app is async_slack_app
        
        mock_client.close.assert_called_once()