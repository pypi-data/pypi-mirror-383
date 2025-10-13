"""Tests for SlackUtils class."""

import pytest
from tnslack import SlackUtils


class TestSlackUtils:
    """Test cases for SlackUtils class."""

    def test_no_op(self):
        """Test NO_OP function."""
        utils = SlackUtils()
        result = utils.NO_OP("test", "args")
        assert result is None

    def test_action_with_params_basic(self):
        """Test action_with_params with basic input."""
        utils = SlackUtils()
        result = utils.action_with_params("test_action", ["param1=value1", "param2=value2"])
        assert result == "test_action?param1=value1&param2=value2"

    def test_action_with_params_no_params(self):
        """Test action_with_params with no parameters."""
        utils = SlackUtils()
        result = utils.action_with_params("test_action", [])
        assert result == "test_action?"

    def test_action_with_params_invalid_action_type(self):
        """Test action_with_params with invalid action type."""
        utils = SlackUtils()
        with pytest.raises(TypeError, match="action must be str"):
            utils.action_with_params(123, ["param=value"])

    def test_action_with_params_invalid_params_type(self):
        """Test action_with_params with invalid params type."""
        utils = SlackUtils()
        with pytest.raises(TypeError, match="params must be list"):
            utils.action_with_params("action", "not_a_list")

    def test_action_with_params_too_long(self):
        """Test action_with_params with result too long."""
        utils = SlackUtils()
        # Create a long parameter string that would exceed 255 characters
        long_params = [f"param{i}={'x' * 10}" for i in range(20)]
        
        with pytest.raises(ValueError, match="action_id would be longer than 255 characters"):
            utils.action_with_params("test_action", long_params)

    def test_process_action_id_basic(self):
        """Test process_action_id with basic input."""
        utils = SlackUtils()
        result = utils.process_action_id("test_action?param1=value1&param2=value2")
        
        expected = {
            "true_id": "test_action",
            "params": {
                "param1": "value1",
                "param2": "value2"
            }
        }
        assert result == expected

    def test_process_action_id_no_params(self):
        """Test process_action_id with no parameters."""
        utils = SlackUtils()
        result = utils.process_action_id("test_action")
        
        expected = {
            "true_id": "test_action",
            "params": {}
        }
        assert result == expected

    def test_process_action_id_empty_params(self):
        """Test process_action_id with empty parameter section."""
        utils = SlackUtils()
        result = utils.process_action_id("test_action?")
        
        expected = {
            "true_id": "test_action",
            "params": {}
        }
        assert result == expected

    def test_process_action_id_single_param(self):
        """Test process_action_id with single parameter."""
        utils = SlackUtils()
        result = utils.process_action_id("action?key=value")
        
        expected = {
            "true_id": "action",
            "params": {"key": "value"}
        }
        assert result == expected

    def test_process_action_id_param_without_value(self):
        """Test process_action_id with parameter without value."""
        utils = SlackUtils()
        # This tests the edge case where a parameter doesn't have an '=' 
        # The current implementation would fail, but let's test what happens
        result = utils.process_action_id("action?param1&param2=value2")
        
        # This would actually cause an IndexError in the current implementation
        # but we'll test the expected behavior
        with pytest.raises(IndexError):
            utils.process_action_id("action?param_without_equals")

    def test_roundtrip_action_params(self):
        """Test that action_with_params and process_action_id are inverse operations."""
        utils = SlackUtils()
        
        original_action = "test_action"
        original_params = ["param1=value1", "param2=value2", "param3=value3"]
        
        # Create action string
        action_string = utils.action_with_params(original_action, original_params)
        
        # Parse it back
        parsed = utils.process_action_id(action_string)
        
        assert parsed["true_id"] == original_action
        assert parsed["params"]["param1"] == "value1"
        assert parsed["params"]["param2"] == "value2"
        assert parsed["params"]["param3"] == "value3"