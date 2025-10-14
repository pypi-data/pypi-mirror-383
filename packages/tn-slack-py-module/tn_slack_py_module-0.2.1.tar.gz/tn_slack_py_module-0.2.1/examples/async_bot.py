#!/usr/bin/env python3
"""
Async TNSlack Bot Example

This example demonstrates:
- Using AsyncSlackApp for full async/await support
- Async route handlers
- Concurrent API calls
- FastAPI integration for async web framework
"""

import asyncio
import json
import os
from typing import Dict, Any

from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import JSONResponse, HTMLResponse

from tnslack import AsyncSlackApp, BlockBuilder, constants as slack_consts

# Initialize FastAPI app
fastapi_app = FastAPI(title="TNSlack Async Bot")

# Initialize async TNSlack app
slack_app = AsyncSlackApp(
    client_id=os.environ["SLACK_CLIENT_ID"],
    client_secret=os.environ["SLACK_CLIENT_SECRET"],
    signing_secret=os.environ["SLACK_SIGNING_SECRET"],
    redirect_url=os.environ.get("SLACK_REDIRECT_URL", "http://localhost:8000/oauth/callback"),
    bot_scopes=["chat:write", "users:read", "channels:read"],
    user_scopes=[]
)

# Initialize BlockBuilder
builder = BlockBuilder()

# Store tokens in memory (use database in production)
app_tokens: Dict[str, Dict[str, Any]] = {}


# Async route handlers
async def handle_user_info_button(payload: Dict[str, Any], params: Dict[str, Any]) -> Dict[str, Any]:
    """Handle user info button - demonstrates async API calls."""
    user_id = payload["user"]["id"]
    team_id = payload["team"]["id"]
    
    # Get bot token for this team
    if team_id not in app_tokens:
        return {"text": "Bot not properly installed for this team"}
    
    bot_token = app_tokens[team_id]["bot_token"]
    
    try:
        # Fetch user info asynchronously
        user_info = await slack_app.async_get_user_info(user_id, bot_token)
        user_data = user_info["user"]
        
        # Create response blocks
        blocks = [
            builder.header_block(f"User Info: {user_data.get('real_name', 'Unknown')}"),
            builder.simple_section_block(f"**Display Name:** {user_data.get('display_name') or 'Not set'}"),
            builder.simple_section_block(f"**Email:** {user_data.get('profile', {}).get('email', 'Not available')}"),
            builder.simple_section_block(f"**Title:** {user_data.get('profile', {}).get('title', 'Not set')}"),
            builder.simple_section_block(f"**Status:** {'Active' if not user_data.get('deleted') else 'Deactivated'}"),
            builder.divider_block(),
            builder.actions_block([
                builder.simple_button_block(
                    "Refresh Info",
                    "refresh_user_info",
                    action_id="user_info_button",
                    style="primary"
                ),
                builder.simple_button_block(
                    "Back to Menu",
                    "back_to_menu",
                    action_id="main_menu_button"
                )
            ])
        ]
        
        return {
            "replace_original": True,
            "blocks": blocks
        }
        
    except Exception as e:
        print(f"Error fetching user info: {e}")
        return {
            "replace_original": True,
            "blocks": [
                builder.simple_section_block("❌ Error fetching user information"),
                builder.simple_section_block(f"Error: {str(e)}")
            ]
        }


async def handle_concurrent_demo(payload: Dict[str, Any], params: Dict[str, Any]) -> Dict[str, Any]:
    """Demonstrate concurrent async operations."""
    team_id = payload["team"]["id"]
    user_id = payload["user"]["id"]
    
    if team_id not in app_tokens:
        return {"text": "Bot not properly installed for this team"}
    
    bot_token = app_tokens[team_id]["bot_token"]
    
    try:
        # Perform multiple async operations concurrently
        tasks = [
            slack_app.async_get_user_info(user_id, bot_token),
            # You could add more concurrent operations here
            # slack_app.async_get_conversations_list(bot_token),
            # etc.
        ]
        
        # Wait for all operations to complete
        results = await asyncio.gather(*tasks, return_exceptions=True)
        user_info_result = results[0]
        
        if isinstance(user_info_result, Exception):
            raise user_info_result
        
        user_data = user_info_result["user"]
        
        blocks = [
            builder.header_block("Concurrent Operations Demo ⚡"),
            builder.simple_section_block("These operations were performed concurrently:"),
            builder.simple_section_block(f"✅ Fetched user info for {user_data.get('real_name')}"),
            builder.simple_section_block("✅ Other async operations completed"),
            builder.simple_section_block("*This demonstrates the power of async/await!*"),
            builder.divider_block(),
            builder.actions_block([
                builder.simple_button_block(
                    "Run Again",
                    "run_concurrent_demo",
                    action_id="concurrent_demo_button",
                    style="primary"
                ),
                builder.simple_button_block(
                    "Back to Menu",
                    "back_to_menu",
                    action_id="main_menu_button"
                )
            ])
        ]
        
        return {
            "replace_original": True,
            "blocks": blocks
        }
        
    except Exception as e:
        return {
            "replace_original": True,
            "blocks": [
                builder.simple_section_block("❌ Error in concurrent demo"),
                builder.simple_section_block(f"Error: {str(e)}")
            ]
        }


async def handle_main_menu(payload: Dict[str, Any], params: Dict[str, Any]) -> Dict[str, Any]:
    """Show main menu with async options."""
    blocks = [
        builder.header_block("TNSlack Async Bot Menu 🚀"),
        builder.simple_section_block("Choose an async operation to demonstrate:"),
        builder.actions_block([
            builder.simple_button_block(
                "Get User Info",
                "get_user_info",
                action_id="user_info_button",
                style="primary"
            ),
            builder.simple_button_block(
                "Concurrent Demo",
                "concurrent_demo",
                action_id="concurrent_demo_button"
            )
        ])
    ]
    
    return {
        "replace_original": True,
        "blocks": blocks
    }


# Register async route handlers
slack_app.register_route(slack_consts.BLOCK_ACTIONS, handle_main_menu, "main_menu_button")
slack_app.register_route(slack_consts.BLOCK_ACTIONS, handle_user_info_button, "user_info_button")
slack_app.register_route(slack_consts.BLOCK_ACTIONS, handle_concurrent_demo, "concurrent_demo_button")


@fastapi_app.get("/", response_class=HTMLResponse)
async def home():
    """Home page with installation link."""
    install_url = slack_app.workspace_install_link()
    return f"""
    <html>
        <head><title>TNSlack Async Bot</title></head>
        <body>
            <h1>TNSlack Async Bot Example 🚀</h1>
            <p>This demonstrates TNSlack's async capabilities.</p>
            <p><a href="{install_url}">Install to Slack</a></p>
        </body>
    </html>
    """


@fastapi_app.get("/oauth/callback")
async def oauth_callback(code: str = None, error: str = None):
    """Handle OAuth callback from Slack."""
    if error:
        raise HTTPException(status_code=400, detail=f"OAuth Error: {error}")
    
    if not code:
        raise HTTPException(status_code=400, detail="Missing authorization code")
    
    try:
        # Exchange code for tokens asynchronously
        token_response = await slack_app.async_exchange_code_for_token(code)
        
        # Store tokens
        team_id = token_response["team"]["id"]
        app_tokens[team_id] = {
            "bot_token": token_response["access_token"],
            "user_token": token_response.get("authed_user", {}).get("access_token"),
            "team_id": team_id,
            "team_name": token_response["team"]["name"]
        }
        
        # Send welcome message asynchronously
        welcome_blocks = [
            builder.header_block("Welcome to TNSlack Async Bot! ⚡"),
            builder.simple_section_block(
                "This bot demonstrates async/await capabilities. Click below to explore!"
            ),
            builder.actions_block([
                builder.simple_button_block(
                    "Start Demo",
                    "start_demo",
                    action_id="main_menu_button",
                    style="primary"
                )
            ])
        ]
        
        # Try to post welcome message
        try:
            await slack_app.async_send_channel_message(
                channel="#general",
                access_token=token_response["access_token"],
                text="TNSlack Async Bot has been installed!",
                block_set=welcome_blocks
            )
        except Exception as e:
            print(f"Could not post to #general: {e}")
        
        return HTMLResponse("""
        <html>
            <body>
                <h1>Installation Successful! ✅</h1>
                <p>TNSlack Async Bot has been installed to your workspace.</p>
                <p>Go to your Slack workspace and look for the welcome message!</p>
            </body>
        </html>
        """)
        
    except Exception as e:
        print(f"OAuth error: {e}")
        raise HTTPException(status_code=500, detail=f"Installation failed: {str(e)}")


@fastapi_app.post("/slack/events")
async def slack_events(request: Request):
    """Handle Slack events and interactions."""
    # Get request body
    body = await request.body()
    request_body = body.decode("utf-8")
    
    # Verify request signature
    if not slack_app.authenticate_incoming_request(request_body, dict(request.headers)):
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    # Parse request
    if request.headers.get("content-type") == "application/json":
        data = await request.json()
        # Handle URL verification challenge
        if data.get("type") == "url_verification":
            return JSONResponse({"challenge": data["challenge"]})
    else:
        # Handle interactive components
        form_data = await request.form()
        if "payload" in form_data:
            payload = json.loads(form_data["payload"])
            # Process interaction asynchronously
            response = await slack_app.async_slack_interaction_consumer(payload)
            return JSONResponse(response or {})
    
    return JSONResponse({"status": "ok"})


@fastapi_app.on_event("startup")
async def startup_event():
    """Startup event handler."""
    print("Starting TNSlack Async Bot...")
    print("Make sure to configure your Slack app's Request URLs:")
    print("- Interactivity: http://your-domain.com/slack/events")
    print("- OAuth Redirect URL: http://your-domain.com/oauth/callback")


@fastapi_app.on_event("shutdown")
async def shutdown_event():
    """Shutdown event handler."""
    print("Shutting down TNSlack Async Bot...")
    # Close all async clients
    await slack_app.close_async_clients()


if __name__ == "__main__":
    import uvicorn
    
    # Check required environment variables
    required_vars = ["SLACK_CLIENT_ID", "SLACK_CLIENT_SECRET", "SLACK_SIGNING_SECRET"]
    missing_vars = [var for var in required_vars if not os.environ.get(var)]
    
    if missing_vars:
        print(f"Missing required environment variables: {', '.join(missing_vars)}")
        print("Please set these variables before running the bot.")
        exit(1)
    
    # Run with uvicorn
    uvicorn.run(fastapi_app, host="0.0.0.0", port=8000)