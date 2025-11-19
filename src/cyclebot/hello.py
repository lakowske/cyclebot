import anyio
from claude_code_sdk import (
    AssistantMessage,
    ClaudeCodeOptions,
    ResultMessage,
    SystemMessage,
    TextBlock,
    ToolResultBlock,
    ToolUseBlock,
    UserMessage,
    query,
)


async def greet(name: str) -> None:
    """Return a greeting message."""
    # Simple query
    async for message in query(prompt=f"Hello {name}"):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    print(block.text)


async def prompt(content: str, options: ClaudeCodeOptions = None) -> tuple[int, str | None]:
    """Send a prompt to Claude and print the response.  Return the turn count and session_id."""
    turn_count = 0
    session_id = None
    print(f"Prompt: {content}")
    async for message in query(prompt=content, options=options):
        if isinstance(message, AssistantMessage):
            turn_count += 1
            for block in message.content:
                if isinstance(block, TextBlock):
                    print(block.text)
                if isinstance(block, ToolUseBlock):
                    print("Tool used:")
                    print(f"Name: {block.name}")
                    print(f"Input: {block.input}")

        if isinstance(message, SystemMessage):
            session_id = message.data.get('session_id')
            print("System message:")
            print(f"Model: {message.data['model']}")
            print(f"Session ID: {session_id}")
            print(f"Current working directory: {message.data['cwd']}")
            print(f"Available tools: {message.data['tools']}")
            print(f"Permission mode: {message.data['permissionMode']}")

        if isinstance(message, UserMessage):
            print("User message:")
            for block in message.content:
                if isinstance(block, TextBlock):
                    print(block.text)
                if isinstance(block, ToolResultBlock):
                    print("Tool result:")
                    print(f"Content: {block.content}")
                    print(f"Error: {block.is_error}")

        if isinstance(message, ResultMessage):
            turn_count += 1
            print("Result:")
            print(f"Turns: {message.num_turns}")
            print(f"Duration API(ms): {message.duration_api_ms}")
            print(f"Duration total(ms): {message.duration_ms}")
            print(f"Error: {message.is_error}")
            print(f"Cost: {message.total_cost_usd}")

    return turn_count, session_id


def create_playwright_options() -> ClaudeCodeOptions:
    """Create ClaudeCodeOptions for Playwright browser automation.

    Note: This relies on the global MCP server being configured with the correct profile.
    Use `claude mcp` commands to configure the profile path.
    Example: claude mcp add --transport stdio playwright -s user -- npx -y @playwright/mcp@latest --browser chrome --user-data-dir /path/to/profile
    """
    # Don't create a custom MCP server - it doesn't shut down properly!
    # Instead, use the global MCP configuration and just control permissions

    return ClaudeCodeOptions(
        allowed_tools=[
            "mcp__playwright__*",  # Auto-approve Playwright tools
        ],
        disallowed_tools=[
            "Write",  # Block file writing
            "Edit",  # Block file editing
            "Bash",  # Block command execution
            "Read",  # Block file reading
            "Glob",  # Block file searching
            "Grep",  # Block content searching
        ],
        permission_mode="bypassPermissions",  # Required for non-interactive scripts
    )


async def tell_joke() -> None:
    """Tell a joke using Claude with system prompt."""
    # With options
    options = ClaudeCodeOptions(system_prompt="You are a helpful assistant", max_turns=1)

    async for message in query(prompt="Tell me a joke", options=options):
        print(message)


async def main() -> None:
    """Run the demo functions with dynamic profile selection."""
    # Use default "tradingview" profile (matches launch-chrome-profile.sh default)
    print("=== Using TradingView Profile ===")

    # Single prompt with all tasks - browser stays open for all of them
    options = create_playwright_options()
    turns, session_id = await prompt(
        """Please complete these tasks in sequence using the same browser session:

1. Navigate to https://www.tradingview.com/chart/obJz7jBz/ and take a snapshot of the 1 hour chart saved as screenshots/1H.png.
2. Navigate to https://www.tradingview.com/chart/gVH3aqxp/ and take a snapshot of the 30 minute chart saved as screenshots/30m.png.
3. Navigate to https://www.tradingview.com/chart/KXmakFlc/ and take a snapshot of the 15 minute chart saved as screenshots/15m.png.
4. Navigate to https://www.tradingview.com/chart/hCHhBALH/ and take a snapshot of the 5 minute chart saved as screenshots/5m.png.
        """,
        options=options,
    )
    print(f"Total turns taken: {turns}\n")
    print(f"Session ID: {session_id}\n")


    # Example 2: Use a different profile for another site
    # print("=== Using Different Profile ===")
    # other_options = create_playwright_options(profile_name="personal")
    # turns = await prompt(
    #     "Navigate to https://example.com",
    #     options=other_options,
    # )
    # print(f"Total turns taken: {turns}")

    # Test that Write is blocked (should fail)
    # turns = await prompt("Create a file ~/test.txt with the content 'Hello, world!'", options=options)
    # print(f"Total turns taken: {turns}")



anyio.run(main)
