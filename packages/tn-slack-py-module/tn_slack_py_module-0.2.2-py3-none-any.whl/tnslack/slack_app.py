"""Modern SlackApp implementation with type hints and official Slack SDK integration."""

import asyncio
import hashlib
import hmac
import json
import logging
import math
from datetime import datetime, timedelta
from typing import Any, Callable, Dict, List, Optional, Union

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

from . import constants as slack_consts
from .base_slack_app import BaseSlackApp

logger = logging.getLogger(__name__)


class SlackApp(BaseSlackApp):
    """Modern Slack app with router pattern and official SDK integration.
    
    This class provides a simplified interface for building Slack apps with:
    - Route-based interaction handling
    - Block set management
    - OAuth flow support
    - Type-safe API methods
    """

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
        """Initialize SlackApp with configuration.
        
        Args:
            client_id: Slack app client ID
            client_secret: Slack app client secret
            signing_secret: Slack app signing secret for request verification
            redirect_url: OAuth redirect URL
            bot_scopes: List of bot token scopes
            user_scopes: List of user token scopes  
            error_webhook: Optional webhook URL for error notifications
        """
        super().__init__(
            client_id=client_id,
            client_secret=client_secret,
            signing_secret=signing_secret,
            redirect_url=redirect_url,
            bot_scopes=bot_scopes,
            user_scopes=user_scopes,
            error_webhook=error_webhook
        )


    def get_web_client(self, token: str) -> WebClient:
        """Get a configured WebClient instance.
        
        Args:
            token: Bot or user token
            
        Returns:
            Configured WebClient instance
        """
        return WebClient(token=token)





    def slack_interaction_consumer(self, payload: Dict[str, Any]) -> Any:
        """Process Slack interaction payload and route to appropriate handler.
        
        Args:
            payload: Slack interaction payload
            
        Returns:
            Result from route handler or NO_OP
        """
        interaction_type = payload.get("type")
        
        if interaction_type == slack_consts.BLOCK_ACTIONS:
            return self._block_action_consumer(payload)
        elif interaction_type == slack_consts.BLOCK_SUGGESTION:
            return self._block_suggestion_consumer(payload)
        elif interaction_type == slack_consts.VIEW_SUBMISSION:
            return self._view_submission_consumer(payload)
        elif interaction_type == slack_consts.VIEW_CLOSED:
            return self._view_closed_consumer(payload)
        else:
            return self._utils.NO_OP(payload)

    def _block_action_consumer(self, payload: Dict[str, Any]) -> Any:
        """Process block action and route to handler."""
        if not payload.get("actions"):
            return self._utils.NO_OP(payload)
            
        action_id, action_params = self._process_action_params(payload)
        handler = self.routes[slack_consts.BLOCK_ACTIONS].get(action_id, self._utils.NO_OP)
        return handler(payload, action_params)

    def _block_suggestion_consumer(self, payload: Dict[str, Any]) -> Any:
        """Process block suggestion and route to handler."""
        action_id, action_params = self._process_suggestion_params(payload)
        handler = self.routes[slack_consts.BLOCK_SUGGESTION].get(action_id, self._utils.NO_OP)
        return handler(payload, action_params)

    def _view_submission_consumer(self, payload: Dict[str, Any]) -> Any:
        """Process view submission and route to handler."""
        callback_id, view_context = self._process_view_params(payload)
        handler = self.routes[slack_consts.VIEW_SUBMISSION].get(callback_id, self._utils.NO_OP)
        return handler(payload, view_context)

    def _view_closed_consumer(self, payload: Dict[str, Any]) -> Any:
        """Process view closed and route to handler."""
        view = payload.get("view", {})
        callback_id = view.get("callback_id", "")
        
        handler = self.routes[slack_consts.VIEW_CLOSED].get(callback_id, self._utils.NO_OP)
        return handler(payload, view)



    def exchange_code_for_token(self, code: str) -> Dict[str, Any]:
        """Exchange OAuth code for access token.
        
        Args:
            code: OAuth authorization code
            
        Returns:
            OAuth access response data
            
        Raises:
            SlackApiError: If OAuth exchange fails
        """
        client = WebClient()
        try:
            response = client.oauth_v2_access(
                client_id=self.client_id,
                client_secret=self.client_secret,
                code=code,
                redirect_uri=self.redirect_url
            )
            return response.data
        except SlackApiError as e:
            logger.error(f"OAuth exchange failed: {e}")
            raise


    # Legacy methods for backward compatibility
    def send_channel_message(
        self, 
        channel: str, 
        access_token: str, 
        text: str = "Slack Message", 
        block_set: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """Send message to channel using legacy API.
        
        Args:
            channel: Channel ID or name
            access_token: Bot token
            text: Message text
            block_set: Optional list of blocks
            
        Returns:
            API response data
        """
        client = WebClient(token=access_token)
        try:
            response = client.chat_postMessage(
                channel=channel,
                text=text,
                blocks=block_set or []
            )
            return response.data
        except SlackApiError as e:
            logger.error(f"Failed to send message: {e}")
            raise

    def open_modal_from_trigger(
        self, 
        trigger_id: str, 
        view: Dict[str, Any], 
        access_token: str
    ) -> Dict[str, Any]:
        """Open modal from trigger ID.
        
        Args:
            trigger_id: Trigger ID from interaction
            view: Modal view definition
            access_token: Bot token
            
        Returns:
            API response data
        """
        client = WebClient(token=access_token)
        try:
            response = client.views_open(
                trigger_id=trigger_id,
                view=view
            )
            return response.data
        except SlackApiError as e:
            logger.error(f"Failed to open modal: {e}")
            raise

    def update_modal(
        self, 
        view_id: str, 
        view: Dict[str, Any], 
        access_token: str,
        hash_val: Optional[str] = None
    ) -> Dict[str, Any]:
        """Update an existing modal view.
        
        Args:
            view_id: View ID to update
            view: Updated view definition
            access_token: Bot token
            hash_val: Optional hash for race condition prevention
            
        Returns:
            API response data
        """
        client = WebClient(token=access_token)
        try:
            kwargs = {"view_id": view_id, "view": view}
            if hash_val:
                kwargs["hash"] = hash_val
                
            response = client.views_update(**kwargs)
            return response.data
        except SlackApiError as e:
            logger.error(f"Failed to update modal: {e}")
            raise

    def publish_home_view(
        self, 
        user_id: str, 
        view: Dict[str, Any], 
        access_token: str
    ) -> Dict[str, Any]:
        """Publish view to user's home tab.
        
        Args:
            user_id: User ID to publish to
            view: Home view definition
            access_token: Bot token
            
        Returns:
            API response data
        """
        client = WebClient(token=access_token)
        try:
            response = client.views_publish(
                user_id=user_id,
                view=view
            )
            return response.data
        except SlackApiError as e:
            logger.error(f"Failed to publish home view: {e}")
            raise

    def update_message(
        self, 
        channel: str, 
        timestamp: str, 
        access_token: str,
        text: Optional[str] = None,
        block_set: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """Update an existing message.
        
        Args:
            channel: Channel ID where message was posted
            timestamp: Message timestamp to update
            access_token: Bot token
            text: Updated message text
            block_set: Updated blocks
            
        Returns:
            API response data
        """
        client = WebClient(token=access_token)
        try:
            kwargs = {"channel": channel, "ts": timestamp}
            if text:
                kwargs["text"] = text
            if block_set:
                kwargs["blocks"] = block_set
                
            response = client.chat_update(**kwargs)
            return response.data
        except SlackApiError as e:
            logger.error(f"Failed to update message: {e}")
            raise

    def send_ephemeral_message(
        self, 
        channel: str, 
        access_token: str, 
        user_id: str,
        text: str = "Slack Message", 
        block_set: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """Send ephemeral message to user in channel.
        
        Args:
            channel: Channel ID or name
            access_token: Bot token
            user_id: User ID to send message to
            text: Message text
            block_set: Optional list of blocks
            
        Returns:
            API response data
        """
        client = WebClient(token=access_token)
        try:
            response = client.chat_postEphemeral(
                channel=channel,
                user=user_id,
                text=text,
                blocks=block_set or []
            )
            return response.data
        except SlackApiError as e:
            logger.error(f"Failed to send ephemeral message: {e}")
            raise

    def get_user_info(
        self, 
        user_id: str, 
        access_token: str
    ) -> Dict[str, Any]:
        """Get user information.
        
        Args:
            user_id: User ID to get info for
            access_token: Bot token
            
        Returns:
            User info data
        """
        client = WebClient(token=access_token)
        try:
            response = client.users_info(user=user_id)
            return response.data
        except SlackApiError as e:
            logger.error(f"Failed to get user info: {e}")
            raise

    def open_conversation(
        self, 
        users: Union[str, List[str]], 
        access_token: str
    ) -> Dict[str, Any]:
        """Open a conversation (DM or group).
        
        Args:
            users: User ID or list of user IDs
            access_token: Bot token
            
        Returns:
            Conversation info data
        """
        client = WebClient(token=access_token)
        try:
            if isinstance(users, list):
                users_param = ",".join(users)
            else:
                users_param = users
                
            response = client.conversations_open(users=users_param)
            return response.data
        except SlackApiError as e:
            logger.error(f"Failed to open conversation: {e}")
            raise