# CycleBot Web Interface

A web-based interface for interacting with Claude Code SDK through FastAPI and WebSockets.

## Features

- **Real-time communication**: WebSocket-based JSON-RPC protocol
- **Message type visualization**: Color-coded messages for different types:
  - Assistant messages (blue) - Claude's responses
  - User messages (yellow) - Tool responses
  - System messages (purple) - Configuration info
  - Result messages (green) - Completion summaries
  - Prompt messages (gray) - Your inputs
- **Tool usage display**: See when Claude uses tools and their inputs/outputs
- **Configurable options**: Control system prompts, max turns, permission modes, and allowed tools
- **Clean UI**: Built with plain web components, no frameworks required

## Quick Start

1. Install dependencies (if not already done):
   ```bash
   uv pip install -e ".[dev]"
   ```

2. Start the web server:
   ```bash
   python -m cyclebot.web
   ```

3. Open your browser to: http://localhost:8000

4. Enter a prompt and click "Run" (or press Ctrl+Enter / Cmd+Enter)

## Architecture

### Backend (FastAPI + WebSocket)
- **`src/cyclebot/web.py`**: FastAPI server with WebSocket endpoint
- Streams messages from Claude Code SDK to browser in real-time
- Implements JSON-RPC 2.0 protocol for request/response handling

### Frontend (Web Components)
- **`src/cyclebot/static/index.html`**: Main HTML page
- **`src/cyclebot/static/app.js`**: WebSocket client and JSON-RPC handler
- **`src/cyclebot/static/components/chat-log.js`**: Message display component
- **`src/cyclebot/static/components/prompt-input.js`**: Input form component

### Communication Protocol

Uses JSON-RPC 2.0 over WebSockets:

**Request (client → server)**:
```json
{
  "jsonrpc": "2.0",
  "method": "prompt",
  "params": {
    "content": "What is 2+2?",
    "options": {
      "max_turns": 5,
      "system_prompt": "You are a helpful assistant"
    }
  },
  "id": 1
}
```

**Notifications (server → client)** - streamed during execution:
```json
{
  "jsonrpc": "2.0",
  "method": "message",
  "params": {
    "type": "assistant",
    "data": {
      "turn": 1,
      "content": [
        {"type": "text", "text": "4"}
      ]
    }
  }
}
```

**Response (server → client)** - when completed:
```json
{
  "jsonrpc": "2.0",
  "result": {
    "turn_count": 1,
    "status": "completed"
  },
  "id": 1
}
```

## Message Types

The interface displays different message types with distinct colors:

- **Prompt** (Gray): Your input prompts
- **Assistant** (Blue): Claude's text responses and tool uses
- **User/Tool Response** (Yellow): Results from tool executions
- **System** (Purple): Session information and configuration
- **Result** (Green): Final summary with metrics (turns, duration, cost)
- **Error** (Red): Error messages

## Options

Click the "⚙️ Options" button to configure:

- **System Prompt**: Custom system instructions for Claude
- **Max Turns**: Maximum conversation turns (default: 10)
- **Permission Mode**: How to handle tool permissions (default/enabled/disabled)
- **Allowed Tools**: Comma-separated list of tool names to restrict usage

## Development

The web interface uses plain web components (no build step required):

- Modify components in `src/cyclebot/static/components/`
- Edit styles directly in component shadow DOMs
- Reload browser to see changes

To add new message types:
1. Update `handle_prompt()` in `web.py` to emit the new type
2. Add rendering logic in `chat-log.js` `renderMessage()` method
3. Add color scheme in chat-log component styles

## Running in Production

For production deployment:

```bash
uvicorn cyclebot.web:app --host 0.0.0.0 --port 8000 --workers 4
```

Consider:
- Using a reverse proxy (nginx, Caddy)
- Enabling HTTPS/WSS
- Adding authentication
- Rate limiting
- CORS configuration if serving from different domain
