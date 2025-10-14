"""TNSlack - A modern Slack app builder for Python.

This package provides a router-based architecture for building Slack apps
with modern Python practices including type hints, async support, and 
integration with the official Slack SDK.
"""

from typing import TYPE_CHECKING

from .block_builder import BlockBuilder
from .constants import (
    BLOCK_ACTIONS,
    BLOCK_SUGGESTION,
    EVENT_URL_VERIFICATION,
    SLACK_ERROR,
    VIEW_CLOSED,
    VIEW_SUBMISSION,
)
from .decorators import block_set, processor
from .exceptions import (
    ApiRateLimitExceeded,
    InvalidAccessToken,
    InvalidArgumentsException,
    InvalidBlocksException,
    InvalidBlocksFormatException,
    InvalidUser,
    SlackAppException,
    TokenExpired,
    UnHandeledBlocksException,
)
from .slack_app import SlackApp
from .async_slack_app import AsyncSlackApp
from .utils import SlackUtils

if TYPE_CHECKING:
    from typing import Any

__version__ = "0.2.0"
__author__ = "Pari"
__email__ = "pari@threeleafcoder.com"

__all__ = [
    # Main classes
    "SlackApp",
    "AsyncSlackApp",
    "BlockBuilder", 
    "SlackUtils",
    # Constants
    "BLOCK_ACTIONS",
    "BLOCK_SUGGESTION",
    "VIEW_SUBMISSION",
    "VIEW_CLOSED",
    "EVENT_URL_VERIFICATION",
    "SLACK_ERROR",
    # Decorators
    "block_set",
    "processor",
    # Exceptions
    "SlackAppException",
    "TokenExpired",
    "ApiRateLimitExceeded",
    "InvalidBlocksException",
    "InvalidBlocksFormatException", 
    "UnHandeledBlocksException",
    "InvalidArgumentsException",
    "InvalidAccessToken",
    "InvalidUser",
]