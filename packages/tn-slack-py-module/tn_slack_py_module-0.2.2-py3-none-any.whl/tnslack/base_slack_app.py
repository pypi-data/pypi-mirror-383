"""Base SlackApp with shared functionality between sync and async implementations."""

import asyncio
import json
import logging
from typing import Any, Callable, Dict, List, Optional, Union
from urllib.parse import urlencode

from slack_sdk.signature import SignatureVerifier

from . import constants as slack_consts
from .block_builder import BlockBuilder
from .utils import SlackUtils

logger = logging.getLogger(__name__)


class BaseSlackApp:
    """Base class with shared functionality for sync and async Slack apps.
    
    This class provides common functionality that is shared between
    sync and async implementations to reduce code duplication.
    """
    
    SLACK_OAUTH_AUTHORIZE_ROOT = "https://slack.com/oauth/v2/authorize"

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        signing_secret: str,
        redirect_url: str = "",
        bot_scopes: Optional[List[str]] = None,
        user_scopes: Optional[List[str]] = None,
        error_webhook: Optional[str] = None,
    ):
        """Initialize BaseSlackApp with configuration.
        
        Args:
            client_id: Slack app client ID
            client_secret: Slack app client secret
            signing_secret: Slack app signing secret for request verification
            redirect_url: OAuth redirect URL
            bot_scopes: List of bot token scopes
            user_scopes: List of user token scopes  
            error_webhook: Optional webhook URL for error notifications
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.signing_secret = signing_secret
        self.redirect_url = redirect_url
        self.bot_scopes = bot_scopes or []
        self.user_scopes = user_scopes or []
        self.error_webhook = error_webhook
        
        # Initialize signature verifier
        self.signature_verifier = SignatureVerifier(signing_secret)
        
        # Route registries
        self.routes: Dict[str, Dict[str, Callable]] = {
            slack_consts.BLOCK_ACTIONS: {},
            slack_consts.BLOCK_SUGGESTION: {},
            slack_consts.VIEW_SUBMISSION: {},
            slack_consts.VIEW_CLOSED: {},
        }
        
        # Block set registry
        self.block_sets: Dict[str, Callable] = {}
        
        # Utils and builder instances
        self._utils = SlackUtils()
        self._block_builder = BlockBuilder()

    def authenticate_incoming_request(self, request_body: str, headers: Dict[str, str]) -> bool:
        """Authenticate incoming Slack request using signature verification.
        
        Args:
            request_body: Raw request body as string
            headers: Request headers dictionary
            
        Returns:
            True if request is authentic, False otherwise
            
        Raises:
            ValueError: If authentication fails
        """
        try:
            # Debug the signature verification process
            timestamp = headers.get("X-Slack-Request-Timestamp") or headers.get("x-slack-request-timestamp")
            signature = headers.get("X-Slack-Signature") or headers.get("x-slack-signature")
            
            import time
            current_time = int(time.time())
            time_diff = abs(current_time - int(timestamp)) if timestamp else 0
            
            logger.info(f"Signature verification debug:")
            logger.info(f"  Current time: {current_time}")
            logger.info(f"  Slack timestamp: {timestamp}")
            logger.info(f"  Time difference: {time_diff} seconds")
            logger.info(f"  Within 5min window: {time_diff <= 300}")
            logger.info(f"  Signature: {signature}")
            logger.info(f"  Body length: {len(request_body)}")
            
            # Use the SDK's built-in method that handles header normalization
            result = self.signature_verifier.is_valid_request(
                body=request_body,
                headers=headers
            )
            
            logger.info(f"  Verification result: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Authentication failed: {e}")
            logger.error(f"Headers: {headers}")
            logger.error(f"Body: {request_body}")
            return False

    def register_route(
        self, 
        route_type: str, 
        route_fn: Callable, 
        name: Optional[str] = None
    ) -> None:
        """Register interaction routes.
        
        Args:
            route_type: Type of route (block_actions, view_submission, etc.)
            route_fn: Function to handle the route
            name: Optional name for the route, defaults to function name
            
        Raises:
            ValueError: If route_type is invalid
        """
        if route_type not in self.routes:
            raise ValueError(
                f"Invalid Route Type, only {', '.join(self.routes.keys())} available"
            )
        
        name = name or route_fn.__name__
        self.routes[route_type][name] = route_fn

    def register_block_set(
        self, 
        block_set_fn: Callable, 
        name: Optional[str] = None
    ) -> None:
        """Register a block set function.
        
        Args:
            block_set_fn: Function that returns block set
            name: Optional name for the block set, defaults to function name
        """
        name = name or block_set_fn.__name__
        self.block_sets[name] = block_set_fn

    def route(self, route_type: str, name: Optional[str] = None, required_context: Optional[List[str]] = None):
        """Decorator to register a function as a route handler.
        
        Args:
            route_type: Type of route (block_actions, view_submission, etc.)
            name: Optional name for the route, defaults to function name
            required_context: List of keys to validate in context
            
        Returns:
            Decorator function
            
        Example:
            @app.route("block_actions", required_context=["access_token"])
            def handle_button(payload, context):
                return "Button clicked!"
        """
        def decorator(f: Callable) -> Callable:
            def wrapped_f(payload, context, *args, **kwargs):
                for prop in required_context or []:
                    if context.get(prop) is None:
                        raise ValueError(f"context missing: {prop}, in {f.__name__}")
                return f(payload, context, *args, **kwargs)

            route_name = name or f.__name__
            self.register_route(route_type, wrapped_f, route_name)
            return wrapped_f
        return decorator

    def get_block_set(
        self, 
        set_name: str, 
        context: Optional[Dict[str, Any]] = None, 
        *args, 
        **kwargs
    ) -> Any:
        """Get a registered block set.
        
        Args:
            set_name: Name of the block set
            context: Context dictionary to pass to block set function
            *args: Additional positional arguments
            **kwargs: Additional keyword arguments
            
        Returns:
            Result of block set function
            
        Raises:
            TypeError: If block set not found or not registered
        """
        try:
            return self.block_sets[set_name](context or {}, *args, **kwargs)
        except KeyError:
            raise TypeError(f"Block Set '{set_name}' not found or not registered")

    def workspace_install_link(
        self, 
        team_id: Optional[str] = None, 
        state: Optional[str] = None
    ) -> str:
        """Generate workspace installation link.
        
        Args:
            team_id: Optional team ID to pre-select workspace
            state: Optional state parameter for OAuth flow
            
        Returns:
            OAuth authorization URL for workspace installation
        """
        params = {
            "redirect_uri": self.redirect_url,
            "client_id": self.client_id,
            "scope": ",".join(self.bot_scopes),
        }
        
        if state:
            params["state"] = state
        if team_id:
            params["team_id"] = team_id
            
        return f"{self.SLACK_OAUTH_AUTHORIZE_ROOT}?{urlencode(params)}"

    def user_install_link(
        self, 
        team_id: Optional[str] = None, 
        state: Optional[str] = None
    ) -> str:
        """Generate user installation link.
        
        Args:
            team_id: Optional team ID to pre-select workspace
            state: Optional state parameter for OAuth flow
            
        Returns:
            OAuth authorization URL for user installation
        """
        params = {
            "redirect_uri": self.redirect_url,
            "client_id": self.client_id,
            "user_scope": ",".join(self.user_scopes),
        }
        
        if state:
            params["state"] = state
        if team_id:
            params["team_id"] = team_id
            
        return f"{self.SLACK_OAUTH_AUTHORIZE_ROOT}?{urlencode(params)}"

    @property
    def utils(self) -> SlackUtils:
        """Get SlackUtils instance."""
        return self._utils

    @property  
    def block_builder(self) -> BlockBuilder:
        """Get BlockBuilder instance."""
        return self._block_builder

    def _process_action_params(self, payload: Dict[str, Any]) -> tuple[str, Dict[str, Any]]:
        """Extract action ID and parameters from payload.
        
        Args:
            payload: Slack interaction payload
            
        Returns:
            Tuple of (action_id, action_params)
        """
        if not payload.get("actions"):
            return "", {}
            
        action_query_string = payload["actions"][0]["action_id"]
        processed_string = self._utils.process_action_id(action_query_string)
        action_id = processed_string.get("true_id")
        action_params = processed_string.get("params", {})
        
        # Special override for block_actions
        if action_params.get("__block_action"):
            action_id = action_params.get("__block_action")
            
        return action_id, action_params

    def _process_suggestion_params(self, payload: Dict[str, Any]) -> tuple[str, Dict[str, Any]]:
        """Extract action ID and parameters from suggestion payload.
        
        Args:
            payload: Slack suggestion payload
            
        Returns:
            Tuple of (action_id, action_params)
        """
        action_query_string = payload.get("action_id", "")
        processed_string = self._utils.process_action_id(action_query_string)
        action_id = processed_string.get("true_id")
        action_params = processed_string.get("params", {})
        
        return action_id, action_params

    def _process_view_params(self, payload: Dict[str, Any]) -> tuple[str, Dict[str, Any]]:
        """Extract callback ID and view context from view payload.
        
        Args:
            payload: Slack view payload
            
        Returns:
            Tuple of (callback_id, view_context)
        """
        view = payload.get("view", {})
        callback_id = view.get("callback_id", "")
        
        try:
            view_context = json.loads(view.get("private_metadata", "{}"))
        except json.JSONDecodeError:
            view_context = {}
            
        return callback_id, view_context

    def _handle_result(self, result: Any) -> Any:
        """Handle result from route handler, awaiting if coroutine.
        
        Args:
            result: Result from handler function
            
        Returns:
            Awaited result if coroutine, otherwise original result
        """
        if asyncio.iscoroutine(result):
            # This is a sync method, so we can't await here
            # Return the coroutine and let the caller handle it
            return result
        return result