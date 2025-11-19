"""FastAPI web server for cyclebot with WebSocket and JSON-RPC support."""

import json
from pathlib import Path
from typing import Any, Optional, Union

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
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel


class JSONRPCRequest(BaseModel):
    """JSON-RPC 2.0 request model."""

    jsonrpc: str = "2.0"
    method: str
    params: Optional[dict[str, Any]] = None
    id: Optional[Union[int, str]] = None


class JSONRPCResponse(BaseModel):
    """JSON-RPC 2.0 response model."""

    jsonrpc: str = "2.0"
    result: Optional[Any] = None
    error: Optional[dict[str, Any]] = None
    id: Optional[Union[int, str]] = None


app = FastAPI(title="CycleBot Web Interface")

# Get the static directory path
STATIC_DIR = Path(__file__).parent / "static"

# Mount static files
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/", response_class=HTMLResponse)  # type: ignore[misc]
async def get_index() -> str:
    """Serve the main HTML page."""
    index_path = STATIC_DIR / "index.html"
    with index_path.open() as f:
        return f.read()


@app.websocket("/ws")  # type: ignore[misc]
async def websocket_endpoint(websocket: WebSocket) -> None:
    """WebSocket endpoint for JSON-RPC communication."""
    await websocket.accept()

    try:
        while True:
            # Receive JSON-RPC request
            data = await websocket.receive_text()
            request_data = json.loads(data)

            # Parse request
            try:
                rpc_request = JSONRPCRequest(**request_data)
            except Exception as e:
                # Send error response
                error_response = JSONRPCResponse(
                    error={"code": -32700, "message": "Parse error", "data": str(e)},
                    id=request_data.get("id"),
                )
                await websocket.send_text(error_response.model_dump_json())
                continue

            # Handle methods
            if rpc_request.method == "prompt":
                await handle_prompt(websocket, rpc_request)
            else:
                # Method not found
                error_response = JSONRPCResponse(
                    error={"code": -32601, "message": "Method not found"},
                    id=rpc_request.id,
                )
                await websocket.send_text(error_response.model_dump_json())

    except WebSocketDisconnect:
        print("Client disconnected")


async def handle_prompt(websocket: WebSocket, rpc_request: JSONRPCRequest) -> None:
    """Handle prompt method by streaming messages back to client."""
    if not rpc_request.params or "content" not in rpc_request.params:
        error_response = JSONRPCResponse(
            error={"code": -32602, "message": "Invalid params: 'content' required"},
            id=rpc_request.id,
        )
        await websocket.send_text(error_response.model_dump_json())
        return

    content = rpc_request.params["content"]
    options_dict = rpc_request.params.get("options", {})

    # Build options
    options = None
    if options_dict:
        options = ClaudeCodeOptions(**options_dict)

    turn_count = 0

    try:
        async for message in query(prompt=content, options=options):
            msg_data: dict[str, Any] = {"type": "unknown", "data": {}}

            if isinstance(message, AssistantMessage):
                turn_count += 1
                msg_data = {
                    "type": "assistant",
                    "data": {
                        "turn": turn_count,
                        "content": [],
                    },
                }
                for block in message.content:
                    if isinstance(block, TextBlock):
                        msg_data["data"]["content"].append({"type": "text", "text": block.text})
                    elif isinstance(block, ToolUseBlock):
                        msg_data["data"]["content"].append(
                            {
                                "type": "tool_use",
                                "name": block.name,
                                "input": block.input,
                            }
                        )

            elif isinstance(message, SystemMessage):
                msg_data = {
                    "type": "system",
                    "data": {
                        "model": message.data.get("model"),
                        "session_id": message.data.get("session_id"),
                        "cwd": message.data.get("cwd"),
                        "tools": message.data.get("tools"),
                        "permission_mode": message.data.get("permissionMode"),
                    },
                }

            elif isinstance(message, UserMessage):
                msg_data = {
                    "type": "user",
                    "data": {
                        "content": [],
                    },
                }
                for block in message.content:
                    if isinstance(block, TextBlock):
                        msg_data["data"]["content"].append({"type": "text", "text": block.text})
                    elif isinstance(block, ToolResultBlock):
                        msg_data["data"]["content"].append(
                            {
                                "type": "tool_result",
                                "content": block.content,
                                "is_error": block.is_error,
                            }
                        )

            elif isinstance(message, ResultMessage):
                turn_count += 1
                msg_data = {
                    "type": "result",
                    "data": {
                        "num_turns": message.num_turns,
                        "duration_api_ms": message.duration_api_ms,
                        "duration_ms": message.duration_ms,
                        "is_error": message.is_error,
                        "total_cost_usd": message.total_cost_usd,
                    },
                }

            # Send message as JSON-RPC notification
            notification = {"jsonrpc": "2.0", "method": "message", "params": msg_data}
            await websocket.send_text(json.dumps(notification))

        # Send final response
        final_response = JSONRPCResponse(
            result={"turn_count": turn_count, "status": "completed"},
            id=rpc_request.id,
        )
        await websocket.send_text(final_response.model_dump_json())

    except Exception as e:
        error_response = JSONRPCResponse(
            error={"code": -32000, "message": "Internal error", "data": str(e)},
            id=rpc_request.id,
        )
        await websocket.send_text(error_response.model_dump_json())


def main() -> None:
    """Run the FastAPI server."""
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)  # noqa: S104


if __name__ == "__main__":
    main()
