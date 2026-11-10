#!/usr/bin/env python3
"""Minimal MCP stdio server used to verify plugin MCP wiring.

Implements enough of the Model Context Protocol over newline-delimited
JSON-RPC on stdin/stdout to let a host connect, list tools, and call one.
Uses only the Python standard library so the plugin needs no build step.
"""

from __future__ import annotations

import json
import sys

SERVER_INFO = {"name": "assisted-installer-mcp-test", "version": "0.1.0"}
DEFAULT_PROTOCOL_VERSION = "2024-11-05"

TOOLS = [
    {
        "name": "echo",
        "description": "Return the provided message, proving the server responds.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "message": {
                    "type": "string",
                    "description": "Text to return.",
                }
            },
            "required": ["message"],
        },
    }
]


def send(payload: dict) -> None:
    sys.stdout.write(json.dumps(payload) + "\n")
    sys.stdout.flush()


def reply(request_id, result: dict) -> None:
    send({"jsonrpc": "2.0", "id": request_id, "result": result})


def fail(request_id, code: int, message: str) -> None:
    send({"jsonrpc": "2.0", "id": request_id, "error": {"code": code, "message": message}})


def handle(message: dict) -> None:
    method = message.get("method")
    request_id = message.get("id")

    if method == "initialize":
        version = message.get("params", {}).get("protocolVersion", DEFAULT_PROTOCOL_VERSION)
        reply(request_id, {"protocolVersion": version, "capabilities": {"tools": {}}, "serverInfo": SERVER_INFO})
    elif method == "ping":
        reply(request_id, {})
    elif method == "tools/list":
        reply(request_id, {"tools": TOOLS})
    elif method == "tools/call":
        arguments = message.get("params", {}).get("arguments", {})
        text = "echo: " + str(arguments.get("message", ""))
        reply(request_id, {"content": [{"type": "text", "text": text}], "isError": False})
    elif request_id is not None:
        fail(request_id, -32601, "Method not found: " + str(method))
    # Notifications carry no id and need no response.


def main() -> None:
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            message = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(message, dict):
            handle(message)


if __name__ == "__main__":
    main()
