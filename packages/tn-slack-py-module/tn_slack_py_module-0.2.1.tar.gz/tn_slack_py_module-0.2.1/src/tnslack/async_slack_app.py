"""Async SlackApp implementation with full async/await support."""

import asyncio
import logging
from typing import Any, Dict, List, Optional, Union

from slack_sdk.web.async_client import AsyncWebClient
from slack_sdk.errors import SlackApiError

from .base_slack_app import BaseSlackApp
from . import constants as slack_consts

logger = logging.getLogger(__name__)


class AsyncSlackApp(BaseSlackApp):
    """Async version of SlackApp with full async/await support.
    
    Extends the base SlackApp class to provide async methods for all
    API operations and route handling. Inherits all sync methods and
    adds async variants.
    """

    def __init__(self, *args, **kwargs):
        """Initialize AsyncSlackApp with same arguments as BaseSlackApp."""
        super().__init__(*args, **kwargs)
        self._async_clients: Dict[str, AsyncWebClient] = {}

    def get_async_web_client(self, token: str) -> AsyncWebClient:
        """Get or create an async WebClient instance.
        
        Args:
            token: Bot or user token
            
        Returns:
            Configured AsyncWebClient instance
        """
        if token not in self._async_clients:
            self._async_clients[token] = AsyncWebClient(token=token)
        return self._async_clients[token]

    async def async_slack_interaction_consumer(self, payload: Dict[str, Any]) -> Any:
        """Async version of slack_interaction_consumer.
        
        Args:
            payload: Slack interaction payload
            
        Returns:
            Result from async route handler or NO_OP
        """
        interaction_type = payload.get("type")
        
        if interaction_type == slack_consts.BLOCK_ACTIONS:
            return await self._async_block_action_consumer(payload)
        elif interaction_type == slack_consts.BLOCK_SUGGESTION:
            return await self._async_block_suggestion_consumer(payload)
        elif interaction_type == slack_consts.VIEW_SUBMISSION:
            return await self._async_view_submission_consumer(payload)
        elif interaction_type == slack_consts.VIEW_CLOSED:
            return await self._async_view_closed_consumer(payload)
        else:
            # If handler is async, await it, otherwise call it normally
            result = self._utils.NO_OP(payload)
            return await result if asyncio.iscoroutine(result) else result

    async def _async_block_action_consumer(self, payload: Dict[str, Any]) -> Any:
        """Async process block action and route to handler."""
        if not payload.get("actions"):
            result = self._utils.NO_OP(payload)
            return await result if asyncio.iscoroutine(result) else result
            
        action_id, action_params = self._process_action_params(payload)
        handler = self.routes[slack_consts.BLOCK_ACTIONS].get(action_id, self._utils.NO_OP)
        result = handler(payload, action_params)
        return await result if asyncio.iscoroutine(result) else result

    async def _async_block_suggestion_consumer(self, payload: Dict[str, Any]) -> Any:
        """Async process block suggestion and route to handler."""
        action_id, action_params = self._process_suggestion_params(payload)
        handler = self.routes[slack_consts.BLOCK_SUGGESTION].get(action_id, self._utils.NO_OP)
        result = handler(payload, action_params)
        return await result if asyncio.iscoroutine(result) else result

    async def _async_view_submission_consumer(self, payload: Dict[str, Any]) -> Any:
        """Async process view submission and route to handler."""
        callback_id, view_context = self._process_view_params(payload)
        handler = self.routes[slack_consts.VIEW_SUBMISSION].get(callback_id, self._utils.NO_OP)
        result = handler(payload, view_context)
        return await result if asyncio.iscoroutine(result) else result

    async def _async_view_closed_consumer(self, payload: Dict[str, Any]) -> Any:
        """Async process view closed and route to handler."""
        view = payload.get("view", {})
        callback_id = view.get("callback_id", "")
        
        handler = self.routes[slack_consts.VIEW_CLOSED].get(callback_id, self._utils.NO_OP)
        result = handler(payload, view)
        return await result if asyncio.iscoroutine(result) else result

    async def async_exchange_code_for_token(self, code: str) -> Dict[str, Any]:
        """Async exchange OAuth code for access token.
        
        Args:
            code: OAuth authorization code
            
        Returns:
            OAuth access response data
            
        Raises:
            SlackApiError: If OAuth exchange fails
        """
        client = AsyncWebClient()
        try:
            response = await client.oauth_v2_access(
                client_id=self.client_id,
                client_secret=self.client_secret,
                code=code,
                redirect_uri=self.redirect_url
            )
            return response.data
        except SlackApiError as e:
            logger.error(f"OAuth exchange failed: {e}")
            raise
        finally:
            await client.close()

    async def async_send_channel_message(
        self, 
        channel: str, 
        access_token: str, 
        text: str = "Slack Message", 
        block_set: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """Async send message to channel.
        
        Args:
            channel: Channel ID or name
            access_token: Bot token
            text: Message text
            block_set: Optional list of blocks
            
        Returns:
            API response data
        """
        client = self.get_async_web_client(access_token)
        try:
            response = await client.chat_postMessage(
                channel=channel,
                text=text,
                blocks=block_set or []
            )
            return response.data
        except SlackApiError as e:
            logger.error(f"Failed to send message: {e}")
            raise

    async def async_send_ephemeral_message(
        self, 
        channel: str, 
        access_token: str, 
        user_id: str,
        text: str = "Slack Message", 
        block_set: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """Async send ephemeral message to user in channel.
        
        Args:
            channel: Channel ID or name
            access_token: Bot token
            user_id: User ID to send message to
            text: Message text
            block_set: Optional list of blocks
            
        Returns:
            API response data
        """
        client = self.get_async_web_client(access_token)
        try:
            response = await client.chat_postEphemeral(
                channel=channel,
                user=user_id,
                text=text,
                blocks=block_set or []
            )
            return response.data
        except SlackApiError as e:
            logger.error(f"Failed to send ephemeral message: {e}")
            raise

    async def async_open_modal_from_trigger(
        self, 
        trigger_id: str, 
        view: Dict[str, Any], 
        access_token: str
    ) -> Dict[str, Any]:
        """Async open modal from trigger ID.
        
        Args:
            trigger_id: Trigger ID from interaction
            view: Modal view definition
            access_token: Bot token
            
        Returns:
            API response data
        """
        client = self.get_async_web_client(access_token)
        try:
            response = await client.views_open(
                trigger_id=trigger_id,
                view=view
            )
            return response.data
        except SlackApiError as e:
            logger.error(f"Failed to open modal: {e}")
            raise

    async def async_update_modal(
        self, 
        view_id: str, 
        view: Dict[str, Any], 
        access_token: str,
        hash_val: Optional[str] = None
    ) -> Dict[str, Any]:
        """Async update an existing modal view.
        
        Args:
            view_id: View ID to update
            view: Updated view definition
            access_token: Bot token
            hash_val: Optional hash for race condition prevention
            
        Returns:
            API response data
        """
        client = self.get_async_web_client(access_token)
        try:
            kwargs = {"view_id": view_id, "view": view}
            if hash_val:
                kwargs["hash"] = hash_val
                
            response = await client.views_update(**kwargs)
            return response.data
        except SlackApiError as e:
            logger.error(f"Failed to update modal: {e}")
            raise

    async def async_publish_home_view(
        self, 
        user_id: str, 
        view: Dict[str, Any], 
        access_token: str
    ) -> Dict[str, Any]:
        """Async publish view to user's home tab.
        
        Args:
            user_id: User ID to publish to
            view: Home view definition
            access_token: Bot token
            
        Returns:
            API response data
        """
        client = self.get_async_web_client(access_token)
        try:
            response = await client.views_publish(
                user_id=user_id,
                view=view
            )
            return response.data
        except SlackApiError as e:
            logger.error(f"Failed to publish home view: {e}")
            raise

    async def async_update_message(
        self, 
        channel: str, 
        timestamp: str, 
        access_token: str,
        text: Optional[str] = None,
        block_set: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """Async update an existing message.
        
        Args:
            channel: Channel ID where message was posted
            timestamp: Message timestamp to update
            access_token: Bot token
            text: Updated message text
            block_set: Updated blocks
            
        Returns:
            API response data
        """
        client = self.get_async_web_client(access_token)
        try:
            kwargs = {"channel": channel, "ts": timestamp}
            if text:
                kwargs["text"] = text
            if block_set:
                kwargs["blocks"] = block_set
                
            response = await client.chat_update(**kwargs)
            return response.data
        except SlackApiError as e:
            logger.error(f"Failed to update message: {e}")
            raise

    async def async_get_user_info(
        self, 
        user_id: str, 
        access_token: str
    ) -> Dict[str, Any]:
        """Async get user information.
        
        Args:
            user_id: User ID to get info for
            access_token: Bot token
            
        Returns:
            User info data
        """
        client = self.get_async_web_client(access_token)
        try:
            response = await client.users_info(user=user_id)
            return response.data
        except SlackApiError as e:
            logger.error(f"Failed to get user info: {e}")
            raise

    async def async_open_conversation(
        self, 
        users: Union[str, List[str]], 
        access_token: str
    ) -> Dict[str, Any]:
        """Async open a conversation (DM or group).
        
        Args:
            users: User ID or list of user IDs
            access_token: Bot token
            
        Returns:
            Conversation info data
        """
        client = self.get_async_web_client(access_token)
        try:
            if isinstance(users, list):
                users_param = ",".join(users)
            else:
                users_param = users
                
            response = await client.conversations_open(users=users_param)
            return response.data
        except SlackApiError as e:
            logger.error(f"Failed to open conversation: {e}")
            raise

    async def close_async_clients(self) -> None:
        """Close all async client connections."""
        for client in self._async_clients.values():
            await client.close()
        self._async_clients.clear()

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, _exc_type, _exc_val, _exc_tb) -> None:
        """Async context manager exit."""
        await self.close_async_clients()