#!/usr/bin/env python3
"""
Basic TNSlack Bot Example

This example demonstrates:
- Setting up a basic Slack app
- Handling button interactions
- Using the BlockBuilder for UI components
- OAuth flow implementation
"""

import json
import os
from flask import Flask, request, jsonify

from tnslack import SlackApp, BlockBuilder, constants as slack_consts

# Initialize Flask app
flask_app = Flask(__name__)

# Initialize TNSlack app
slack_app = SlackApp(
    client_id=os.environ["SLACK_CLIENT_ID"],
    client_secret=os.environ["SLACK_CLIENT_SECRET"],
    signing_secret=os.environ["SLACK_SIGNING_SECRET"],
    redirect_url=os.environ.get("SLACK_REDIRECT_URL", "http://localhost:5000/oauth/callback"),
    bot_scopes=["chat:write", "commands", "app_mentions:read"],
    user_scopes=[]
)

# Initialize BlockBuilder
builder = BlockBuilder()

# Store tokens in memory (use database in production)
app_tokens = {}


# Route handlers
def handle_hello_button(payload, params):
    """Handle hello button clicks."""
    user_name = payload["user"]["name"]
    
    blocks = [
        builder.simple_section_block(f"Hello {user_name}! 👋"),
        builder.simple_section_block("Thanks for clicking the button!"),
        builder.actions_block([
            builder.simple_button_block(
                "Click Again", 
                "hello_again",
                action_id="hello_button",
                style="primary"
            ),
            builder.simple_button_block(
                "Show Profile", 
                "show_profile",
                action_id="profile_button"
            )
        ])
    ]
    
    return {
        "replace_original": True,
        "blocks": blocks
    }


def handle_profile_button(payload, params):
    """Handle profile button clicks."""
    user = payload["user"]
    
    blocks = [
        builder.header_block("User Profile"),
        builder.simple_section_block(f"**Name:** {user.get('name', 'Unknown')}"),
        builder.simple_section_block(f"**ID:** {user['id']}"),
        builder.simple_section_block(f"**Team:** {payload['team']['id']}"),
        builder.divider_block(),
        builder.actions_block([
            builder.simple_button_block(
                "Back",
                "back_to_hello", 
                action_id="hello_button"
            )
        ])
    ]
    
    return {
        "replace_original": True,
        "blocks": blocks
    }


# Register route handlers
slack_app.register_route(slack_consts.BLOCK_ACTIONS, handle_hello_button, "hello_button")
slack_app.register_route(slack_consts.BLOCK_ACTIONS, handle_profile_button, "profile_button")


@flask_app.route("/", methods=["GET"])
def home():
    """Home page with installation link."""
    install_url = slack_app.workspace_install_link()
    return f"""
    <h1>TNSlack Basic Bot Example</h1>
    <p>This is a demonstration of TNSlack's capabilities.</p>
    <p><a href="{install_url}">Install to Slack</a></p>
    """


@flask_app.route("/oauth/callback", methods=["GET"])
def oauth_callback():
    """Handle OAuth callback from Slack."""
    code = request.args.get("code")
    error = request.args.get("error")
    
    if error:
        return f"OAuth Error: {error}", 400
    
    if not code:
        return "Missing authorization code", 400
    
    try:
        # Exchange code for tokens
        token_response = slack_app.exchange_code_for_token(code)
        
        # Store tokens (use database in production)
        team_id = token_response["team"]["id"]
        app_tokens[team_id] = {
            "bot_token": token_response["access_token"],
            "user_token": token_response.get("authed_user", {}).get("access_token"),
            "team_id": team_id,
            "team_name": token_response["team"]["name"]
        }
        
        # Send welcome message
        welcome_blocks = [
            builder.header_block("Welcome to TNSlack Bot! 🎉"),
            builder.simple_section_block(
                "Thanks for installing! Click the button below to get started."
            ),
            builder.actions_block([
                builder.simple_button_block(
                    "Say Hello",
                    "hello_clicked",
                    action_id="hello_button",
                    style="primary"
                )
            ])
        ]
        
        # Post to general channel (if bot has permission)
        try:
            slack_app.send_channel_message(
                channel="#general",
                access_token=token_response["access_token"],
                text="TNSlack Bot has been installed!",
                block_set=welcome_blocks
            )
        except Exception as e:
            print(f"Could not post to #general: {e}")
        
        return """
        <h1>Installation Successful!</h1>
        <p>TNSlack Bot has been installed to your workspace.</p>
        <p>Go to your Slack workspace and look for the welcome message!</p>
        """
        
    except Exception as e:
        print(f"OAuth error: {e}")
        return f"Installation failed: {str(e)}", 500


@flask_app.route("/slack/events", methods=["POST"])
def slack_events():
    """Handle Slack events and interactions."""
    # Verify request signature
    request_body = request.get_data(as_text=True)
    if not slack_app.authenticate_incoming_request(request_body, dict(request.headers)):
        return "Unauthorized", 401
    
    # Handle URL verification challenge
    if request.json and request.json.get("type") == "url_verification":
        return jsonify({"challenge": request.json["challenge"]})
    
    # Handle interactive components
    if "payload" in request.form:
        payload = json.loads(request.form["payload"])
        response = slack_app.slack_interaction_consumer(payload)
        return jsonify(response or {})
    
    # Handle other events
    return jsonify({"status": "ok"})


@flask_app.route("/slack/commands", methods=["POST"])
def slack_commands():
    """Handle slash commands."""
    # Verify request signature
    request_body = request.get_data(as_text=True)
    if not slack_app.authenticate_incoming_request(request_body, dict(request.headers)):
        return "Unauthorized", 401
    
    command = request.form.get("command")
    user_id = request.form.get("user_id")
    team_id = request.form.get("team_id")
    
    if command == "/tnslack-demo":
        blocks = [
            builder.header_block("TNSlack Demo Command"),
            builder.simple_section_block("This command was handled by TNSlack!"),
            builder.actions_block([
                builder.simple_button_block(
                    "Interactive Button",
                    "demo_clicked", 
                    action_id="hello_button",
                    style="primary"
                )
            ])
        ]
        
        return jsonify({
            "response_type": "ephemeral",
            "blocks": blocks
        })
    
    return jsonify({
        "response_type": "ephemeral", 
        "text": f"Unknown command: {command}"
    })


if __name__ == "__main__":
    # Check required environment variables
    required_vars = ["SLACK_CLIENT_ID", "SLACK_CLIENT_SECRET", "SLACK_SIGNING_SECRET"]
    missing_vars = [var for var in required_vars if not os.environ.get(var)]
    
    if missing_vars:
        print(f"Missing required environment variables: {', '.join(missing_vars)}")
        print("Please set these variables before running the bot.")
        exit(1)
    
    print("Starting TNSlack Basic Bot...")
    print("Make sure to configure your Slack app's Request URLs:")
    print("- Interactivity: http://your-domain.com/slack/events")
    print("- Slash Commands: http://your-domain.com/slack/commands") 
    print("- OAuth Redirect URL: http://your-domain.com/oauth/callback")
    
    flask_app.run(debug=True, port=5000)