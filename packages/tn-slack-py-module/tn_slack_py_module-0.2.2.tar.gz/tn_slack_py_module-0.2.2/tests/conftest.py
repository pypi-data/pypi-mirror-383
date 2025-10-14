"""Pytest configuration and fixtures."""

import pytest
from unittest.mock import Mock, patch
from tnslack import SlackApp, AsyncSlackApp, BlockBuilder


@pytest.fixture
def slack_app():
    """Create a SlackApp instance for testing."""
    return SlackApp(
        client_id="test_client_id",
        client_secret="test_client_secret", 
        signing_secret="test_signing_secret",
        redirect_url="https://example.com/auth",
        bot_scopes=["chat:write", "commands"],
        user_scopes=["identify"]
    )


@pytest.fixture
def async_slack_app():
    """Create an AsyncSlackApp instance for testing."""
    return AsyncSlackApp(
        client_id="test_client_id",
        client_secret="test_client_secret",
        signing_secret="test_signing_secret",
        redirect_url="https://example.com/auth",
        bot_scopes=["chat:write", "commands"],
        user_scopes=["identify"]
    )


@pytest.fixture
def block_builder():
    """Create a BlockBuilder instance for testing."""
    return BlockBuilder()


@pytest.fixture
def sample_payload():
    """Sample Slack interaction payload."""
    return {
        "type": "block_actions",
        "user": {"id": "U123456"},
        "team": {"id": "T123456"},
        "actions": [{
            "action_id": "test_action",
            "type": "button",
            "value": "test_value"
        }],
        "trigger_id": "trigger_123"
    }


@pytest.fixture
def sample_view_payload():
    """Sample view submission payload."""
    return {
        "type": "view_submission", 
        "user": {"id": "U123456"},
        "view": {
            "callback_id": "test_modal",
            "private_metadata": '{"key": "value"}',
            "state": {"values": {}}
        }
    }


@pytest.fixture
def mock_web_client():
    """Mock WebClient for testing."""
    with patch('tnslack.slack_app.WebClient') as mock:
        yield mock


@pytest.fixture  
def mock_async_web_client():
    """Mock AsyncWebClient for testing."""
    with patch('tnslack.async_slack_app.AsyncWebClient') as mock:
        yield mock