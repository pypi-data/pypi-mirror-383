"""Modern BlockBuilder with type hints and improved API."""

import uuid
from typing import Any, Dict, List, Optional

# Type aliases for better readability
Block = Dict[str, Any]
TextBlock = Dict[str, str]
Option = Dict[str, Any]


class BlockBuilder:
    """Modern BlockBuilder for creating Slack Block Kit components with type safety."""

    @staticmethod
    def simple_context_block(
        value: str, 
        text_type: str = "plain_text", 
        block_id: Optional[str] = None
    ) -> Block:
        """Create a simple single value context block - metadata style.

        Args:
            value: Text value for the context
            text_type: Text type ("plain_text" or "mrkdwn")
            block_id: Block ID, auto-generated if not provided

        Returns:
            Context block dictionary
        """
        if not block_id:
            block_id = str(uuid.uuid4())
            
        return {
            "type": "context",
            "elements": [{"type": text_type, "text": value}],
            "block_id": block_id,
        }

    @staticmethod
    def many_context_block(
        values: List[str], 
        text_type: str = "plain_text", 
        block_id: Optional[str] = None
    ) -> Block:
        """Create a multi-value context block - metadata style.

        Args:
            values: List of text values
            text_type: Text type applied to all values ("plain_text" or "mrkdwn")
            block_id: Block ID, auto-generated if not provided

        Returns:
            Context block dictionary

        Raises:
            TypeError: If values is not a list
        """
        if not isinstance(values, list):
            raise TypeError(
                f"Values must be a list, got {type(values)}. "
                "Use simple_context_block for single values."
            )
            
        if not block_id:
            block_id = str(uuid.uuid4())
            
        elements = [{"type": text_type, "text": val} for val in values]
        return {
            "type": "context",
            "elements": elements,
            "block_id": block_id,
        }

    @staticmethod
    def custom_context_block(
        elements: List[TextBlock], 
        block_id: Optional[str] = None
    ) -> Block:
        """Create a customizable multi-context block with custom text blocks.

        Args:
            elements: List of text block dictionaries with 'type' and 'text' keys
            block_id: Block ID, auto-generated if not provided

        Returns:
            Context block dictionary

        Raises:
            TypeError: If elements is not a list
        """
        if not isinstance(elements, list):
            raise TypeError("Elements must be a list of text blocks")
            
        if not block_id:
            block_id = str(uuid.uuid4())
            
        return {
            "type": "context",
            "elements": elements,
            "block_id": block_id,
        }

    @staticmethod
    def text_block(value: str, text_type: str = "plain_text") -> TextBlock:
        """Create a text block object.

        Args:
            value: Text content
            text_type: Text type ("plain_text" or "mrkdwn")

        Returns:
            Text block dictionary
        """
        return {"type": text_type, "text": value}

    @staticmethod
    def input_block(
        label: str,
        initial_value: Optional[str] = None,
        placeholder: Optional[str] = None,
        multiline: bool = False,
        placeholder_type: str = "plain_text",
        action_id: str = "plain_input",
        block_id: Optional[str] = None,
        label_type: str = "plain_text",
        min_length: Optional[int] = None,
        max_length: Optional[int] = None,
        optional: bool = True,
    ) -> Block:
        """Create a text input block.

        Args:
            label: Label text for the input
            initial_value: Initial value for the input
            placeholder: Placeholder text
            multiline: Whether to use multiline text area
            placeholder_type: Type for placeholder text
            action_id: Action ID for the input
            block_id: Block ID, auto-generated if not provided
            label_type: Type for label text
            min_length: Minimum input length
            max_length: Maximum input length
            optional: Whether the input is optional

        Returns:
            Input block dictionary
        """
        if not block_id:
            block_id = str(uuid.uuid4())
            
        obj = {
            "type": "input",
            "block_id": block_id,
            "label": {"type": label_type, "text": label},
            "optional": optional,
            "element": {
                "type": "plain_text_input",
                "action_id": action_id,
                "multiline": multiline,
            },
        }
        
        if placeholder:
            obj["element"]["placeholder"] = BlockBuilder.text_block(placeholder, placeholder_type)
            
        if max_length is not None:
            obj["element"]["max_length"] = max_length
            
        if min_length is not None:
            obj["element"]["min_length"] = min_length
            
        if initial_value is not None:
            obj["element"]["initial_value"] = str(initial_value)
            
        return obj

    @staticmethod
    def simple_section_block(
        value: str, 
        text_type: str = "plain_text", 
        block_id: Optional[str] = None
    ) -> Block:
        """Create a simple section block with text.

        Args:
            value: Text content
            text_type: Text type ("plain_text" or "mrkdwn")
            block_id: Block ID, auto-generated if not provided

        Returns:
            Section block dictionary
        """
        if not block_id:
            block_id = str(uuid.uuid4())
            
        return {
            "type": "section",
            "text": {"type": text_type, "text": value},
            "block_id": block_id,
        }

    @staticmethod
    def simple_section_multiple_block(
        text_blocks: List[TextBlock], 
        block_id: Optional[str] = None
    ) -> Block:
        """Create a section block with multiple text fields.

        Args:
            text_blocks: List of text block objects
            block_id: Block ID, auto-generated if not provided

        Returns:
            Section block dictionary
        """
        if not block_id:
            block_id = str(uuid.uuid4())
            
        return {
            "type": "section", 
            "fields": text_blocks, 
            "block_id": block_id
        }

    @staticmethod
    def option(text: str, value: str) -> Option:
        """Create an option object for select menus.

        Args:
            text: Display text for the option
            value: Value for the option

        Returns:
            Option dictionary
        """
        return {
            "text": {"type": "plain_text", "text": text},
            "value": value,
        }

    @staticmethod
    def divider_block() -> Block:
        """Create a divider block.

        Returns:
            Divider block dictionary
        """
        return {"type": "divider"}

    @staticmethod
    def header_block(text: str, block_id: Optional[str] = None) -> Block:
        """Create a header block.

        Args:
            text: Header text
            block_id: Block ID, auto-generated if not provided

        Returns:
            Header block dictionary
        """
        if not block_id:
            block_id = str(uuid.uuid4())
            
        return {
            "type": "header",
            "text": {"type": "plain_text", "text": text},
            "block_id": block_id,
        }

    @staticmethod
    def static_select_block(
        label: str,
        options: List[Option],
        action_id: Optional[str] = None,
        initial_option: Optional[Option] = None,
        placeholder: str = "Select",
        block_id: Optional[str] = None,
    ) -> Block:
        """Create a static select block.

        Args:
            label: Label text for the select
            options: List of option objects
            action_id: Action ID for the select
            initial_option: Initially selected option
            placeholder: Placeholder text
            block_id: Block ID, auto-generated if not provided

        Returns:
            Section block with static select accessory
        """
        if not block_id:
            block_id = str(uuid.uuid4())
            
        block = {
            "type": "section",
            "text": {"type": "mrkdwn", "text": label},
            "block_id": block_id,
            "accessory": {
                "type": "static_select",
                "placeholder": {"type": "plain_text", "text": placeholder},
                "options": options,
            },
        }
        
        if initial_option:
            block["accessory"]["initial_option"] = initial_option
        if action_id:
            block["accessory"]["action_id"] = action_id
            
        return block

    @staticmethod
    def simple_button_block(
        label: str, 
        value: str, 
        url: Optional[str] = None, 
        style: Optional[str] = None, 
        confirm: bool = False, 
        action_id: Optional[str] = None
    ) -> Block:
        """Create a button element.

        Args:
            label: Button text
            value: Button value passed in payload
            url: Optional URL for link button
            style: Button style ("default", "primary", or "danger")
            confirm: Whether to show confirmation dialog
            action_id: Action ID, auto-generated if not provided

        Returns:
            Button element dictionary
        """
        block = {
            "type": "button",
            "text": {"type": "plain_text", "text": label},
            "value": value,
            "action_id": action_id or str(uuid.uuid4()),
        }
        
        if style:
            block["style"] = style
        if url:
            block["url"] = url
            
        return block

    @staticmethod
    def actions_block(
        elements: List[Block], 
        block_id: Optional[str] = None
    ) -> Optional[Block]:
        """Create an actions block with interactive elements.

        Args:
            elements: List of interactive elements (max 5)
            block_id: Block ID, auto-generated if not provided

        Returns:
            Actions block dictionary or None if invalid

        Note:
            Returns None if no elements or more than 5 elements provided
        """
        if not elements or len(elements) > 5:
            return None
            
        if not block_id:
            block_id = str(uuid.uuid4())
            
        return {
            "type": "actions", 
            "block_id": block_id, 
            "elements": elements
        }

    @staticmethod
    def section_with_accessory_block(
        section_text: str,
        accessory: Block,
        text_type: str = "mrkdwn",
        block_id: Optional[str] = None,
    ) -> Block:
        """Create a section block with an accessory element.

        Args:
            section_text: Text for the section
            accessory: Accessory element (button, select, etc.)
            text_type: Text type for section text
            block_id: Block ID, auto-generated if not provided

        Returns:
            Section block with accessory
        """
        if not block_id:
            block_id = str(uuid.uuid4())
            
        return {
            "type": "section",
            "text": {"type": text_type, "text": section_text},
            "block_id": block_id,
            "accessory": accessory,
        }

    @staticmethod
    def section_with_button_block(
        button_label: str,
        button_value: str,
        section_text: str,
        text_type: str = "mrkdwn",
        block_id: Optional[str] = None,
        url: Optional[str] = None,
        style: Optional[str] = None,
        confirm: bool = False,
        action_id: Optional[str] = None,
    ) -> Block:
        """Create a section block with a button accessory.

        Args:
            button_label: Button text
            button_value: Button value
            section_text: Section text
            text_type: Text type for section
            block_id: Block ID, auto-generated if not provided
            url: Optional button URL
            style: Button style
            confirm: Show confirmation dialog
            action_id: Button action ID

        Returns:
            Section block with button accessory
        """
        button = BlockBuilder.simple_button_block(
            button_label, button_value, url, style, confirm, action_id
        )
        return BlockBuilder.section_with_accessory_block(
            section_text, button, text_type, block_id
        )

    @staticmethod
    def simple_image_block(url: str, alt_text: str) -> Block:
        """Create an image block.

        Args:
            url: Image URL (max 3000 characters)
            alt_text: Alt text for image (max 2000 characters)

        Returns:
            Image block dictionary
        """
        return {
            "type": "image",
            "image_url": url,
            "alt_text": alt_text,
        }

    @staticmethod
    def datepicker_block(
        initial_date: Optional[str] = None,
        action_id: Optional[str] = None,
        block_id: Optional[str] = None,
        label: str = "Select Date",
        placeholder: str = "Select a date",
    ) -> Block:
        """Create a datepicker block.

        Args:
            initial_date: Initial date in YYYY-MM-DD format
            action_id: Action ID for the datepicker
            block_id: Block ID, auto-generated if not provided
            label: Label text
            placeholder: Placeholder text

        Returns:
            Section block with datepicker accessory
        """
        if not block_id:
            block_id = str(uuid.uuid4())
            
        block = {
            "type": "section",
            "text": {"type": "mrkdwn", "text": label},
            "block_id": block_id,
            "accessory": {
                "type": "datepicker",
                "placeholder": {"type": "plain_text", "text": placeholder},
            },
        }
        
        if initial_date:
            block["accessory"]["initial_date"] = initial_date
        if action_id:
            block["accessory"]["action_id"] = action_id
            
        return block