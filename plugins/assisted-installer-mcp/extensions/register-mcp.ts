/**
 * Registers the assisted-installer-mcp plugin's MCP servers with Pi.
 *
 * Pi installs this repository as a single package, so the per-plugin install
 * choice other hosts offer is preserved by registering every server disabled.
 * Enable a server with /mcp, or override it in ~/.pi/agent/mcp.json.
 *
 * Server entries come from the plugin's portable mcp.json manifest, which
 * other hosts read as well; keep them equivalent.
 */
import { readFileSync } from "node:fs";
import { dirname, isAbsolute, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";

const PLUGIN_ROOT = resolve(dirname(fileURLToPath(import.meta.url)), "..");

type ServerEntry = {
	command?: unknown;
	args?: unknown;
	env?: unknown;
	cwd?: unknown;
	url?: unknown;
	headers?: unknown;
	description?: unknown;
	timeout?: unknown;
	enabled?: unknown;
};

type McpManifest = {
	mcpServers?: Record<string, ServerEntry>;
};

function isRecord(value: unknown): value is Record<string, unknown> {
	return typeof value === "object" && value !== null && !Array.isArray(value);
}

function readManifest(): McpManifest {
	return JSON.parse(
		readFileSync(resolve(PLUGIN_ROOT, "mcp.json"), "utf8"),
	) as McpManifest;
}

function buildConfig(entry: ServerEntry): Record<string, unknown> {
	const config: Record<string, unknown> = {};
	if (typeof entry.url === "string") {
		config.url = entry.url;
		if (isRecord(entry.headers)) {
			config.headers = entry.headers;
		}
	} else if (typeof entry.command === "string") {
		config.command = entry.command;
		if (Array.isArray(entry.args)) {
			config.args = entry.args;
		}
		if (isRecord(entry.env)) {
			config.env = entry.env;
		}
		const cwd = typeof entry.cwd === "string" ? entry.cwd : ".";
		config.cwd = isAbsolute(cwd) ? cwd : resolve(PLUGIN_ROOT, cwd);
	}
	if (typeof entry.description === "string") {
		config.description = entry.description;
	}
	if (typeof entry.timeout === "number") {
		config.timeout = entry.timeout;
	}
	config.enabled = entry.enabled === true;
	return config;
}

export default function (pi: ExtensionAPI): void {
	let manifest: McpManifest;
	try {
		manifest = readManifest();
	} catch (error) {
		const reason = error instanceof Error ? error.message : String(error);
		pi.on("session_start", async (_event, ctx) => {
			ctx.ui.notify(
				`assisted-installer-mcp: cannot read mcp.json: ${reason}`,
				"error",
			);
		});
		return;
	}

	for (const [name, entry] of Object.entries(manifest.mcpServers ?? {})) {
		pi.registerMcpServer(name, buildConfig(entry));
	}
}
