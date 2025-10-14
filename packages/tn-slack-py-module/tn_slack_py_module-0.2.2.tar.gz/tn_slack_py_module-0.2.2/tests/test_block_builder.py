"""Tests for BlockBuilder class."""

import pytest
import uuid
from tnslack import BlockBuilder


class TestBlockBuilder:
    """Test cases for BlockBuilder class."""

    def test_simple_context_block(self, block_builder):
        """Test simple context block creation."""
        block = block_builder.simple_context_block("Test context", "plain_text")
        
        assert block["type"] == "context"
        assert len(block["elements"]) == 1
        assert block["elements"][0]["type"] == "plain_text"
        assert block["elements"][0]["text"] == "Test context"
        assert "block_id" in block

    def test_simple_context_block_with_block_id(self, block_builder):
        """Test context block with custom block ID."""
        block = block_builder.simple_context_block("Test", block_id="custom_id")
        assert block["block_id"] == "custom_id"

    def test_many_context_block(self, block_builder):
        """Test multi-value context block."""
        values = ["First", "Second", "Third"]
        block = block_builder.many_context_block(values)
        
        assert block["type"] == "context"
        assert len(block["elements"]) == 3
        assert block["elements"][0]["text"] == "First"
        assert block["elements"][1]["text"] == "Second"
        assert block["elements"][2]["text"] == "Third"

    def test_many_context_block_invalid_input(self, block_builder):
        """Test many_context_block with invalid input."""
        with pytest.raises(TypeError, match="Values must be a list"):
            block_builder.many_context_block("not a list")

    def test_custom_context_block(self, block_builder):
        """Test custom context block with text blocks."""
        elements = [
            {"type": "plain_text", "text": "Plain text"},
            {"type": "mrkdwn", "text": "*Bold text*"}
        ]
        block = block_builder.custom_context_block(elements)
        
        assert block["type"] == "context"
        assert block["elements"] == elements

    def test_text_block(self, block_builder):
        """Test text block creation."""
        text_block = block_builder.text_block("Hello World", "mrkdwn")
        
        assert text_block["type"] == "mrkdwn"
        assert text_block["text"] == "Hello World"

    def test_input_block_basic(self, block_builder):
        """Test basic input block creation."""
        block = block_builder.input_block("Enter your name")
        
        assert block["type"] == "input"
        assert block["label"]["text"] == "Enter your name"
        assert block["element"]["type"] == "plain_text_input"
        assert block["element"]["action_id"] == "plain_input"
        assert block["optional"] is True

    def test_input_block_with_options(self, block_builder):
        """Test input block with all options."""
        block = block_builder.input_block(
            label="Description",
            initial_value="Initial text",
            placeholder="Enter description...",
            multiline=True,
            min_length=10,
            max_length=500,
            optional=False,
            action_id="description_input"
        )
        
        assert block["element"]["multiline"] is True
        assert block["element"]["initial_value"] == "Initial text"
        assert block["element"]["placeholder"]["text"] == "Enter description..."
        assert block["element"]["min_length"] == 10
        assert block["element"]["max_length"] == 500
        assert block["optional"] is False
        assert block["element"]["action_id"] == "description_input"

    def test_simple_section_block(self, block_builder):
        """Test simple section block."""
        block = block_builder.simple_section_block("Section text", "mrkdwn")
        
        assert block["type"] == "section"
        assert block["text"]["type"] == "mrkdwn"
        assert block["text"]["text"] == "Section text"

    def test_option(self, block_builder):
        """Test option creation."""
        option = block_builder.option("Display Text", "option_value")
        
        assert option["text"]["type"] == "plain_text"
        assert option["text"]["text"] == "Display Text"
        assert option["value"] == "option_value"

    def test_divider_block(self, block_builder):
        """Test divider block."""
        block = block_builder.divider_block()
        assert block == {"type": "divider"}

    def test_header_block(self, block_builder):
        """Test header block."""
        block = block_builder.header_block("Header Text")
        
        assert block["type"] == "header"
        assert block["text"]["type"] == "plain_text"
        assert block["text"]["text"] == "Header Text"

    def test_static_select_block(self, block_builder):
        """Test static select block."""
        options = [
            block_builder.option("Option 1", "value1"),
            block_builder.option("Option 2", "value2")
        ]
        block = block_builder.static_select_block("Choose option", options)
        
        assert block["type"] == "section"
        assert block["text"]["text"] == "Choose option"
        assert block["accessory"]["type"] == "static_select"
        assert len(block["accessory"]["options"]) == 2

    def test_static_select_block_with_initial(self, block_builder):
        """Test static select with initial option."""
        options = [block_builder.option("Option 1", "value1")]
        initial = block_builder.option("Option 1", "value1")
        
        block = block_builder.static_select_block(
            "Choose option", 
            options, 
            initial_option=initial,
            action_id="select_action"
        )
        
        assert block["accessory"]["initial_option"] == initial
        assert block["accessory"]["action_id"] == "select_action"

    def test_simple_button_block(self, block_builder):
        """Test button creation."""
        button = block_builder.simple_button_block("Click Me", "button_value")
        
        assert button["type"] == "button"
        assert button["text"]["text"] == "Click Me"
        assert button["value"] == "button_value"
        assert "action_id" in button

    def test_simple_button_block_with_style(self, block_builder):
        """Test button with style and URL."""
        button = block_builder.simple_button_block(
            "Visit Site", 
            "visit_value",
            url="https://example.com",
            style="primary",
            action_id="visit_button"
        )
        
        assert button["style"] == "primary"
        assert button["url"] == "https://example.com" 
        assert button["action_id"] == "visit_button"

    def test_actions_block(self, block_builder):
        """Test actions block with elements."""
        button1 = block_builder.simple_button_block("Button 1", "value1")
        button2 = block_builder.simple_button_block("Button 2", "value2")
        
        block = block_builder.actions_block([button1, button2])
        
        assert block["type"] == "actions"
        assert len(block["elements"]) == 2
        assert block["elements"][0] == button1
        assert block["elements"][1] == button2

    def test_actions_block_empty(self, block_builder):
        """Test actions block with no elements."""
        block = block_builder.actions_block([])
        assert block is None

    def test_actions_block_too_many_elements(self, block_builder):
        """Test actions block with too many elements."""
        buttons = [
            block_builder.simple_button_block(f"Button {i}", f"value{i}")
            for i in range(6)
        ]
        block = block_builder.actions_block(buttons)
        assert block is None

    def test_section_with_accessory_block(self, block_builder):
        """Test section with accessory."""
        button = block_builder.simple_button_block("Action", "action_value")
        block = block_builder.section_with_accessory_block("Section text", button)
        
        assert block["type"] == "section"
        assert block["text"]["text"] == "Section text"
        assert block["accessory"] == button

    def test_section_with_button_block(self, block_builder):
        """Test section with button helper."""
        block = block_builder.section_with_button_block(
            "Click", "click_value", "Section with button", style="danger"
        )
        
        assert block["type"] == "section"
        assert block["text"]["text"] == "Section with button"
        assert block["accessory"]["type"] == "button"
        assert block["accessory"]["style"] == "danger"

    def test_simple_image_block(self, block_builder):
        """Test image block."""
        block = block_builder.simple_image_block(
            "https://example.com/image.jpg",
            "Sample image"
        )
        
        assert block["type"] == "image"
        assert block["image_url"] == "https://example.com/image.jpg"
        assert block["alt_text"] == "Sample image"

    def test_datepicker_block(self, block_builder):
        """Test datepicker block."""
        block = block_builder.datepicker_block(
            initial_date="2024-01-15",
            action_id="date_select",
            label="Pick a date"
        )
        
        assert block["type"] == "section"
        assert block["text"]["text"] == "Pick a date"
        assert block["accessory"]["type"] == "datepicker"
        assert block["accessory"]["initial_date"] == "2024-01-15"
        assert block["accessory"]["action_id"] == "date_select"