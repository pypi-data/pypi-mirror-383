"""Tests for decorator classes."""

import pytest
from tnslack.decorators import block_set, processor


class TestBlockSetDecorator:
    """Test cases for block_set decorator."""

    def test_block_set_decorator_no_requirements(self):
        """Test block_set decorator with no required context."""
        @block_set()
        def test_block_set(context):
            return [{"type": "section", "text": {"type": "plain_text", "text": "test"}}]

        result = test_block_set({"any": "context"})
        assert len(result) == 1
        assert result[0]["type"] == "section"

    def test_block_set_decorator_with_requirements(self):
        """Test block_set decorator with required context."""
        @block_set(required_context=["user_id", "message"])
        def test_block_set(context):
            return [{"type": "section", "text": {"type": "plain_text", "text": context["message"]}}]

        # Should work with required context
        context = {"user_id": "U123", "message": "Hello"}
        result = test_block_set(context)
        assert result[0]["text"]["text"] == "Hello"

    def test_block_set_decorator_missing_required_context(self):
        """Test block_set decorator with missing required context."""
        @block_set(required_context=["user_id", "message"])
        def test_block_set(context):
            return [{"type": "section", "text": {"type": "plain_text", "text": context["message"]}}]

        # Should raise ValueError for missing context
        with pytest.raises(ValueError, match="context missing: user_id"):
            test_block_set({"message": "Hello"})

        with pytest.raises(ValueError, match="context missing: message"):
            test_block_set({"user_id": "U123"})

    def test_block_set_decorator_none_values(self):
        """Test block_set decorator with None values in context."""
        @block_set(required_context=["user_id"])
        def test_block_set(context):
            return [{"type": "section"}]

        # None values should trigger the missing context error
        with pytest.raises(ValueError, match="context missing: user_id"):
            test_block_set({"user_id": None})


class TestProcessorDecorator:
    """Test cases for processor decorator."""

    def test_processor_decorator_no_requirements(self):
        """Test processor decorator with no required context."""
        @processor()
        def test_processor(payload, context):
            return f"Processed {payload.get('type')} with {context.get('key')}"

        payload = {"type": "test_event"}
        context = {"key": "value"}
        result = test_processor(payload, context)
        assert result == "Processed test_event with value"

    def test_processor_decorator_with_requirements(self):
        """Test processor decorator with required context."""
        @processor(required_context=["access_token", "user_id"])
        def test_processor(payload, context):
            return f"User {context['user_id']} processed {payload['type']}"

        payload = {"type": "button_click"}
        context = {"access_token": "xoxb-token", "user_id": "U123"}
        result = test_processor(payload, context)
        assert result == "User U123 processed button_click"

    def test_processor_decorator_missing_required_context(self):
        """Test processor decorator with missing required context."""
        @processor(required_context=["access_token", "user_id"])
        def test_processor(payload, context):
            return "processed"

        payload = {"type": "test"}
        
        # Missing access_token
        with pytest.raises(ValueError, match="context missing: access_token"):
            test_processor(payload, {"user_id": "U123"})

        # Missing user_id  
        with pytest.raises(ValueError, match="context missing: user_id"):
            test_processor(payload, {"access_token": "token"})

    def test_processor_decorator_with_args_kwargs(self):
        """Test processor decorator with additional args and kwargs."""
        @processor(required_context=["user_id"])
        def test_processor(payload, context, extra_arg, extra_kwarg=None):
            return {
                "payload_type": payload["type"],
                "user": context["user_id"], 
                "extra_arg": extra_arg,
                "extra_kwarg": extra_kwarg
            }

        payload = {"type": "test"}
        context = {"user_id": "U123"}
        result = test_processor(payload, context, "arg_value", extra_kwarg="kwarg_value")
        
        assert result["payload_type"] == "test"
        assert result["user"] == "U123"
        assert result["extra_arg"] == "arg_value"
        assert result["extra_kwarg"] == "kwarg_value"

    def test_processor_decorator_none_values(self):
        """Test processor decorator with None values in context."""
        @processor(required_context=["required_key"])
        def test_processor(payload, context):
            return "processed"

        payload = {"type": "test"}
        
        # None values should trigger missing context error
        with pytest.raises(ValueError, match="context missing: required_key"):
            test_processor(payload, {"required_key": None})

    def test_processor_decorator_function_name_in_error(self):
        """Test that function name appears in error message."""
        @processor(required_context=["missing_key"])
        def my_custom_processor(payload, context):
            return "processed"

        payload = {"type": "test"}
        context = {}
        
        with pytest.raises(ValueError, match="context missing: missing_key, in my_custom_processor"):
            my_custom_processor(payload, context)

    def test_block_set_decorator_function_name_in_error(self):
        """Test that function name appears in block_set error message."""
        @block_set(required_context=["missing_key"])
        def my_custom_block_set(context):
            return []

        with pytest.raises(ValueError, match="context missing: missing_key, in my_custom_block_set"):
            my_custom_block_set({})