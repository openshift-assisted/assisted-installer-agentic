# Installation

Install `assisted-installer-skills` for individual capabilities. Install both
plugins to use workflows that depend on shared skills. Install
`assisted-installer-mcp` to connect bundled MCP servers; it is optional and
independent of the other plugins. See the
[plugin guide](plugins.md) for package roles and dependencies.
No build step or validation tooling is required to use the plugins.

Add the marketplace from Git, or use an existing local clone. If the repository
is private, your Git credentials must have read access.
For SSH authentication, substitute
`git@github.com:openshift-assisted/assisted-installer-agentic.git` for the HTTPS URL.
Pi instead installs the whole repository as a single package; see the
[Pi](#pi) section for per-plugin control.

## Claude Code

Run these commands inside a Claude Code session. Add the remote marketplace:

```text
/plugin marketplace add https://github.com/openshift-assisted/assisted-installer-agentic.git
```

Or add a local clone:

```text
/plugin marketplace add /path/to/assisted-installer-agentic
```

Then install the plugins you wish to use:

```text
/plugin install assisted-installer-skills@assisted-installer
/plugin install assisted-installer-workflows@assisted-installer
/plugin install assisted-installer-mcp@assisted-installer
```

The `assisted-installer-mcp` install is optional. Hosts activate its MCP
connections when the plugin loads, so install it only when those connections
are wanted.

See [Claude Code marketplace instructions](https://code.claude.com/docs/en/discover-plugins).

## Codex CLI

Run these commands in your terminal. Add the remote marketplace:

```bash
codex plugin marketplace add https://github.com/openshift-assisted/assisted-installer-agentic.git
```

Or add a local clone:

```bash
codex plugin marketplace add /path/to/assisted-installer-agentic
```

Start `codex` and enter `/plugins` to open the plugin browser. Install
`assisted-installer-skills` and, if needed, `assisted-installer-workflows` from
`assisted-installer`; optionally install `assisted-installer-mcp` for its MCP
connections. Start a new chat before using the installed skills.
See the official [marketplace commands](https://developers.openai.com/plugins/build/plugins#add-a-marketplace-from-the-cli)
and [Codex plugin browser instructions](https://developers.openai.com/learn/developers-codex-plugin).

## Pi

Run these commands in your terminal. Pi installs the whole repository as one
package, so every plugin's skills load together and per-plugin control uses
the resource toggles described below:

```bash
pi install git:github.com/openshift-assisted/assisted-installer-agentic.git
```

Or from a local clone:

```bash
pi install /path/to/assisted-installer-agentic
```

`pi update --extensions` reconciles the checkout with the configured Git ref
on later starts. To try the package without installing it, run
`pi -e /path/to/assisted-installer-agentic`. See the
[Pi package documentation](https://github.com/earendil-works/pi/blob/main/packages/coding-agent/docs/packages.md).

MCP connections stay opt-in. The `assisted-installer-mcp` extension registers
the servers from the plugin's `mcp.json` without connecting them. Enable one
for the current session with `/mcp`, or persistently by copying its entry
from the plugin's `mcp.json` into `~/.pi/agent/mcp.json`; an entry with the
same name takes precedence over the extension's registration.

To exclude a plugin's resources instead of skipping a plugin install, run
`pi config` and disable them, or narrow the package entry in
`~/.pi/agent/settings.json` (the source matches your `pi install` argument):

```json
{
  "packages": [
    {
      "source": "git:github.com/openshift-assisted/assisted-installer-agentic.git",
      "extensions": ["!plugins/assisted-installer-mcp/**"],
      "skills": ["!plugins/assisted-installer-mcp/skills/**"]
    }
  ]
}
```

## Marketplace details

The repository has native marketplace catalogs for both harnesses:
[`.claude-plugin/marketplace.json`](../.claude-plugin/marketplace.json) is the
Claude Code catalog and [`.agents/plugins/marketplace.json`](../.agents/plugins/marketplace.json)
is the Codex catalog. Both use the stable
marketplace name `assisted-installer` and expose all plugins under `plugins/`.
The workflows plugin declares the shared-skills plugin as a Claude dependency;
Codex users should install both plugins when a workflow requires shared skills.

If this path was previously registered under a different marketplace name,
remove the old configured name shown by `codex plugin marketplace list` before
adding the path again. Codex tracks configured marketplace sources by name, so
renaming the catalog does not migrate an existing local registration.

Each plugin carries both `.claude-plugin/plugin.json` and `.codex-plugin/plugin.json`
manifests. Pi uses the repository-root `package.json` instead of a marketplace
catalog; it points at the same plugin directories.
