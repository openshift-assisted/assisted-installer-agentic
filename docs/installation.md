# Installation

Install `assisted-installer-skills` for individual capabilities. Install both
plugins to use workflows that depend on shared skills. See the
[plugin guide](plugins.md) for package roles and dependencies.
No build step or validation tooling is required to use the plugins.

Add the marketplace from Git, or use an existing local clone. If the repository
is private, your Git credentials must have read access.
For SSH authentication, substitute
`git@github.com:openshift-assisted/assisted-installer-agentic.git` for the HTTPS URL.

## Claude Code

Run these commands inside a Claude Code session. Add the remote marketplace:

```text
/plugin marketplace add https://github.com/openshift-assisted/assisted-installer-agentic.git
```

Or add a local clone:

```text
/plugin marketplace add /path/to/assisted-installer-agentic
```

Then install the plugins:

```text
/plugin install assisted-installer-skills@assisted-installer
/plugin install assisted-installer-workflows@assisted-installer
```

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
`assisted-installer`. Start a new chat before using the installed skills.
See the official [marketplace commands](https://developers.openai.com/plugins/build/plugins#add-a-marketplace-from-the-cli)
and [Codex plugin browser instructions](https://developers.openai.com/learn/developers-codex-plugin).

## Marketplace details

The repository has native marketplace catalogs for both hosts:
[`.claude-plugin/marketplace.json`](../.claude-plugin/marketplace.json) is the
Claude Code catalog and [`.agents/plugins/marketplace.json`](../.agents/plugins/marketplace.json)
is the Codex catalog. Both use the stable
marketplace name `assisted-installer` and expose both plugins under `plugins/`.
The workflows plugin declares the shared-skills plugin as a Claude dependency;
Codex users should install both plugins when a workflow requires shared skills.

If this path was previously registered under a different marketplace name,
remove the old configured name shown by `codex plugin marketplace list` before
adding the path again. Codex tracks configured marketplace sources by name, so
renaming the catalog does not migrate an existing local registration.

Each plugin carries both `.claude-plugin/plugin.json` and `.codex-plugin/plugin.json`
manifests.
