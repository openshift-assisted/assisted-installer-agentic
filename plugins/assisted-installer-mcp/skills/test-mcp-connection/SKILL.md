---
name: test-mcp-connection
description: Use when verifying that MCP servers bundled with the assisted-installer-mcp plugin connect and respond to tool calls.
---

# Test MCP connection

Verify the plugin's MCP integration before relying on it. The check is
read-only: it connects to the bundled test server and calls its echo tool. It
does not touch team systems or external data.

## Prerequisites

- The `assisted-installer-mcp` plugin is installed and enabled.
- `python3` is available on `PATH`.
- The `test` server appears connected in the host's MCP server list, for
  example as `plugin:assisted-installer-mcp:test` in Claude Code or listed by
  `codex mcp list`.

## Procedure

1. Confirm the `test` server is connected. If it is missing or failed to
   start, stop and report the server name and the error shown.
2. Call the server's `echo` tool with a short message.
3. Confirm the tool returns the sent message.

## Result

Report PASS when the server is connected and the echo tool returns the sent
message. Report FAIL with the observed error otherwise, and stop. Do not
attempt repairs or retries beyond the host's own server restart behavior.

The test server is a placeholder for production servers planned in this
plugin. It is a local stdio process with no network access and defines no
capabilities beyond the echo tool. Connection files are host-specific:
Claude Code reads `.mcp.json` and Codex reads the portable `plugin.json` and
`mcp.json` manifests; keep the server entries in them equivalent.
