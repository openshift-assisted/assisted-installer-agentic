# Assisted Installer Agentic

Portable, reusable agentic workflows and shared skills for local coding
harnesses and hosted agent platforms.

The repository keeps skill instructions in plain Markdown. Its marketplace
catalogs expose the plugin directories directly; no build or packaging step is
required for installation.

## Included plugins

- [`assisted-installer-skills`](plugins/assisted-installer-skills/) contains
  shared, independently usable skills.
- [`assisted-installer-workflows`](plugins/assisted-installer-workflows/)
  contains interactive, multi-step workflows and depends on shared skills when
  needed.

## Installation

See the [installation guide](docs/installation.md) for Claude Code and Codex,
using either the Git marketplace or a local clone.

## Documentation

See [docs/](docs/README.md) for installation, the plugin guide, and an overview of validation tools.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development dependencies, validation
instructions, and plugin conventions.
