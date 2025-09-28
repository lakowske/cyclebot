import anyio
from claude_code_sdk import AssistantMessage, ClaudeCodeOptions, TextBlock, query


async def greet(name: str) -> None:
    """Return a greeting message."""
    # Simple query
    async for message in query(prompt=f"Hello {name}"):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    print(block.text)


async def prompt(content: str) -> None:
    """Send a prompt to Claude and print the response."""
    async for message in query(prompt=content):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    print(block.text)


async def tell_joke() -> None:
    """Tell a joke using Claude with system prompt."""
    # With options
    options = ClaudeCodeOptions(system_prompt="You are a helpful assistant", max_turns=1)

    async for message in query(prompt="Tell me a joke", options=options):
        print(message)


async def main() -> None:
    """Run the demo functions."""
    await tell_joke()
    await greet("Seth")
    await prompt("Write instructions for entering a trance state.")


anyio.run(main)
