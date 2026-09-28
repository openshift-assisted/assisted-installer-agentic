# Contributing

Follow [AGENTS.md](AGENTS.md) for applicable repository-local guidance.
See the [plugin guide](docs/plugins.md) for the distinction between shared skills
and workflows.

## Authoring skills

Place distributed skills at `plugins/<plugin>/skills/<name>/SKILL.md`, with
optional `references/`, `scripts/`, and `assets/` alongside it. Use `name` and
`description` frontmatter; do not add a repository-specific skill version.

Every skill must document:

- Required inputs and prerequisites.
- Read-only discovery and external capabilities.
- Returned results and optional file output.
- Approval checkpoints before remote mutations.
- Result statuses and stopping conditions.

Keep canonical instructions independent of harness-specific syntax. Workflows
use shared skills through public contracts and normal discovery and invocation,
without private installation paths or on-disk handoffs. A named skill is required,
including in delegated work: load and use it, or stop the dependent step and
report its unavailability. Do not substitute another skill or reimplement it.

## Packaging and releases

- Keep plugin Markdown links and symlink targets inside their plugin. Repository
  documentation may link across plugins.
- Register every plugin exactly once at its canonical path in both marketplace
  catalogs. Its Claude and Codex manifests must agree on name and version.
- Declare required shared-plugin dependencies in the Claude manifest; do not
  invent unsupported dependency fields for Codex.
- When releasing distributed skill behavior changes, update the plugin manifests
  and marketplace release metadata. Plugins may have independent versions.

## Local contributor skills

Keep repository-local skills in `.agents/skills/<name>/`, outside distributed
plugins and marketplace catalogs. Expose each to Claude with a relative directory
symlink at `.claude/skills/<name>` pointing to `../../.agents/skills/<name>`.
Keep one canonical source; local guidance may link across the repository.

## Validation

Before submitting changes, run the checks through
[Skipper](https://github.com/stratoscale/skipper):

```bash
skipper make validate
skipper make test
```

See the [validation guide](docs/validation.md) for tool purposes, configuration,
and coverage limits. Validation tooling is not required to use the plugins.
