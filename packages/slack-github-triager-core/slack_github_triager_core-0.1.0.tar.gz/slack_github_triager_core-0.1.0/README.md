# slack-github-triager-core

Reads Slack messages in channels, identifies GitHub PR links, checks their status, and optionally reacts or sends summaries.

## Installation

```bash
uv add slack-github-triager-core
```

## Usage

```python
from slack_github_triager_core.slack_client import SlackRequestClient, get_slack_tokens
from slack_github_triager_core.processing import triage, ReactionConfiguration

# Create Slack client with bot token
client = SlackRequestClient(
    subdomain="your-workspace",
    token="xoxb-your-bot-token",
    enterprise_token="",
    cookie="",
    use_bot=True,
)

# Or with user session (requires d_cookie from browser)
token, enterprise_token = get_slack_tokens(
    subdomain="your-workspace",
    d_cookie="your-d-cookie-from-browser"
)
client = SlackRequestClient(
    subdomain="your-workspace",
    token=token,
    enterprise_token=enterprise_token,
    cookie="your-d-cookie-from-browser",
    use_bot=False,
)

# Configure reaction emojis for PR status
reaction_config = ReactionConfiguration(
    bot_approved="white_check_mark",
    bot_considers_approved={"approved", "lgtm", "ship-it"},
    bot_commented="speech_balloon",
    bot_considers_commented={"commented", "feedback"},
    bot_merged="merged",
    bot_considers_merged={"merged", "shipit"},
    bot_confused="thinking_face",
)

# Run triage on channels
triage(
    client=client,
    slack_subdomain="your-workspace",
    reaction_configuration=reaction_config,
    channel_ids=("C1234567890", "C0987654321"),
    days=7,
    allow_channel_messages=True,
    allow_reactions=True,
    summary_dm_user_id=("U1234567890",),
)
```

This will:
- Scan the last 7 days of messages in the specified channels
- Find GitHub PR links and check their status
- React to messages with appropriate emojis based on PR status
- Send summary DMs to specified users with PRs needing attention
