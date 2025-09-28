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


async def prompt(content: str, options: ClaudeCodeOptions = None) -> int:
    """Send a prompt to Claude and print the response.  Return the turn count."""
    turn_count = 0
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
            print("System message:")
            print(f"Model: {message.data['model']}")
            print(f"Session ID: {message.data['session_id']}")
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

    return turn_count


async def tell_joke() -> None:
    """Tell a joke using Claude with system prompt."""
    # With options
    options = ClaudeCodeOptions(system_prompt="You are a helpful assistant", max_turns=1)

    async for message in query(prompt="Tell me a joke", options=options):
        print(message)


async def main() -> None:
    """Run the demo functions."""
    options = ClaudeCodeOptions(allowed_tools=["mcp__sethtime__get_current_time"], permission_mode="default")
    turns = await prompt("Tell me the current time.", options=options)
    print(f"Total turns taken: {turns}")
    turns = await prompt("Give me a file tree of the current directory.", options=options)
    print(f"Total turns taken: {turns}")


anyio.run(main)
