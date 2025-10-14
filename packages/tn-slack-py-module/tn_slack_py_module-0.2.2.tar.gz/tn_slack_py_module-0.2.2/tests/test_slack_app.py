"""Tests for SlackApp class."""

import pytest
from unittest.mock import Mock, patch
from tnslack import SlackApp, constants as slack_consts


class TestSlackApp:
    """Test cases for SlackApp class."""

    def test_init(self, slack_app):
        """Test SlackApp initialization."""
        assert slack_app.client_id == "test_client_id"
        assert slack_app.client_secret == "test_client_secret"
        assert slack_app.signing_secret == "test_signing_secret"
        assert slack_app.redirect_url == "https://example.com/auth"
        assert slack_app.bot_scopes == ["chat:write", "commands"]
        assert slack_app.user_scopes == ["identify"]

    def test_register_route(self, slack_app):
        """Test route registration."""
        def test_handler(payload, params):
            return "test_response"

        slack_app.register_route(slack_consts.BLOCK_ACTIONS, test_handler, "test_route")
        assert "test_route" in slack_app.routes[slack_consts.BLOCK_ACTIONS]

    def test_register_route_invalid_type(self, slack_app):
        """Test registration with invalid route type."""
        def test_handler(payload, params):
            return "test_response"

        with pytest.raises(ValueError, match="Invalid Route Type"):
            slack_app.register_route("invalid_type", test_handler)

    def test_register_block_set(self, slack_app):
        """Test block set registration."""
        def test_block_set(context):
            return [{"type": "section", "text": {"type": "plain_text", "text": "test"}}]

        slack_app.register_block_set(test_block_set, "test_blocks")
        assert "test_blocks" in slack_app.block_sets

    def test_get_block_set(self, slack_app):
        """Test getting registered block set."""
        def test_block_set(context):
            return [{"type": "section", "text": {"type": "plain_text", "text": context.get("message", "default")}}]

        slack_app.register_block_set(test_block_set, "test_blocks")
        result = slack_app.get_block_set("test_blocks", {"message": "hello"})
        
        assert len(result) == 1
        assert result[0]["text"]["text"] == "hello"

    def test_get_block_set_not_found(self, slack_app):
        """Test getting non-existent block set."""
        with pytest.raises(TypeError, match="not found or not registered"):
            slack_app.get_block_set("nonexistent")

    def test_workspace_install_link(self, slack_app):
        """Test workspace installation link generation."""
        link = slack_app.workspace_install_link()
        assert "https://slack.com/oauth/v2/authorize" in link
        assert "client_id=test_client_id" in link
        assert "scope=chat%3Awrite%2Ccommands" in link

    def test_workspace_install_link_with_params(self, slack_app):
        """Test workspace install link with additional parameters.""" 
        link = slack_app.workspace_install_link(team_id="T123", state="test_state")
        assert "team_id=T123" in link
        assert "state=test_state" in link

    def test_user_install_link(self, slack_app):
        """Test user installation link generation."""
        link = slack_app.user_install_link()
        assert "https://slack.com/oauth/v2/authorize" in link
        assert "client_id=test_client_id" in link
        assert "user_scope=identify" in link

    def test_block_action_consumer(self, slack_app, sample_payload):
        """Test block action consumption and routing."""
        result_value = None
        
        def test_handler(payload, params):
            nonlocal result_value
            result_value = payload["actions"][0]["value"]
            return "handled"

        slack_app.register_route(slack_consts.BLOCK_ACTIONS, test_handler, "test_action")
        result = slack_app.slack_interaction_consumer(sample_payload)
        
        assert result == "handled"
        assert result_value == "test_value"

    def test_view_submission_consumer(self, slack_app, sample_view_payload):
        """Test view submission consumption and routing."""
        received_context = None
        
        def test_handler(payload, context):
            nonlocal received_context
            received_context = context
            return "view_handled"

        slack_app.register_route(slack_consts.VIEW_SUBMISSION, test_handler, "test_modal")
        result = slack_app.slack_interaction_consumer(sample_view_payload)
        
        assert result == "view_handled"
        assert received_context == {"key": "value"}

    def test_unknown_interaction_type(self, slack_app):
        """Test handling unknown interaction type."""
        payload = {"type": "unknown_type"}
        result = slack_app.slack_interaction_consumer(payload)
        # Should return result from NO_OP
        assert result is None

    @patch('tnslack.slack_app.WebClient')
    def test_exchange_code_for_token(self, mock_web_client_class, slack_app):
        """Test OAuth code exchange."""
        mock_client = Mock()
        mock_web_client_class.return_value = mock_client
        mock_response = Mock()
        mock_response.data = {"access_token": "xoxb-test-token"}
        mock_client.oauth_v2_access.return_value = mock_response

        result = slack_app.exchange_code_for_token("test_code")
        
        mock_client.oauth_v2_access.assert_called_once_with(
            client_id="test_client_id",
            client_secret="test_client_secret",
            code="test_code",
            redirect_uri="https://example.com/auth"
        )
        assert result == {"access_token": "xoxb-test-token"}

    @patch('tnslack.slack_app.WebClient')
    def test_send_channel_message(self, mock_web_client_class, slack_app):
        """Test sending channel message."""
        mock_client = Mock()
        mock_web_client_class.return_value = mock_client
        mock_response = Mock()
        mock_response.data = {"ok": True, "ts": "1234567890.123456"}
        mock_client.chat_postMessage.return_value = mock_response

        result = slack_app.send_channel_message(
            channel="#general",
            access_token="xoxb-test-token",
            text="Hello World",
            block_set=[{"type": "section", "text": {"type": "plain_text", "text": "Hello"}}]
        )
        
        mock_client.chat_postMessage.assert_called_once_with(
            channel="#general",
            text="Hello World",
            blocks=[{"type": "section", "text": {"type": "plain_text", "text": "Hello"}}]
        )
        assert result == {"ok": True, "ts": "1234567890.123456"}

    def test_authenticate_incoming_request(self, slack_app):
        """Test request authentication."""
        # Mock the signature verifier
        with patch.object(slack_app.signature_verifier, 'is_valid') as mock_is_valid:
            mock_is_valid.return_value = True
            
            headers = {
                "X-Slack-Request-Timestamp": "1531420618", 
                "X-Slack-Signature": "v0=test_signature"
            }
            
            result = slack_app.authenticate_incoming_request("test_body", headers)
            assert result is True
            
            mock_is_valid.assert_called_once_with(
                body="test_body",
                timestamp="1531420618",
                signature="v0=test_signature"
            )