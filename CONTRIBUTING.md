# Contributing

## Skill structure

Each plugin is a self-contained directory under `plugins/`:

```text
plugin-name/
  .claude-plugin/plugin.json
  .codex-plugin/plugin.json
  skills/
    skill-name/
      SKILL.md
      references/                  # optional supporting material
      scripts/                     # optional deterministic helpers
      assets/                      # optional generated-output assets
```

Each skill is an immediate child of `skills/` so Codex and Claude can discover
it from the marketplace without generated wrappers.

`assisted-installer-skills` contains reusable, independently usable skills.
`assisted-installer-workflows` contains end-to-end orchestration. A workflow
uses shared skills through their documented public contracts and normal harness
discovery, instruction loading, and invocation. Avoid private installation paths
and on-disk handoffs. A skill explicitly named for a workflow step is
required: use it, including in delegated work, or stop that step and report why
it is unavailable. Do not silently substitute a different skill or reimplement
its instructions. Required shared-plugin dependencies are declared in the Claude
manifest; do not add undocumented dependency fields to the Codex manifest.

Do not add harness-specific syntax to canonical skill instructions. The
plugin manifests and marketplace catalogs provide the harness integration.

Keep plugin Markdown links inside their plugin, including reference-style
links and symlink targets. Repository documentation can link across plugins.
Both marketplace catalogs must register every directory under `plugins/` exactly
once at its canonical path. Each plugin's Claude and Codex manifests must agree
on name and version; different plugins may have independent versions.

## Development skill

The repository-local [development skill](.agents/skills/assisted-installer-agentic-development/README.md)
guides plugin placement, concise authoring, and successful validation before
commits. It is excluded from distributed plugins and marketplace catalogs.

Keep local skill sources in `.agents/skills/<name>/` and expose each to Claude
with a relative directory symlink at `.claude/skills/<name>` pointing to
`../../.agents/skills/<name>`. Do not duplicate sources in harness directories.
See [Claude's skill locations](https://code.claude.com/docs/en/skills#choose-where-skills-load).

Development-skill references may link across the repository. Full validation
checks their canonical location, Claude symlinks, frontmatter, names, and Markdown
links; plugin-only validation and isolation tests remain scoped to distributed
plugins.

## Skill contract

Every skill must document:

- Required inputs and prerequisites.
- Read-only discovery and external capabilities.
- Returned results and any optional file output.
- Approval checkpoints before remote mutations.
- A useful result status and a stopping condition.

## Versioning

Skill frontmatter uses the standard `name` and `description` metadata; do not
add a repository-specific skill version. Changes to distributed skill behavior
should update the plugin manifest and marketplace release metadata when a new
plugin release is intended.

## Development dependencies

Run the checks through [Skipper](https://github.com/stratoscale/skipper):

```bash
skipper make validate
skipper make test
```

Skipper and the packaged development tooling are not required to use the plugins.

## Checks

Run before submitting changes:

```bash
skipper make validate
skipper make test
```

`skipper make validate` runs the Python validator for frontmatter, names, plugin-local
link boundaries, matching manifests, catalog coverage, and local Claude dependency
registration. It then runs markdownlint-cli2 with `.markdownlint-cli2.yaml` for
Markdown formatting, Lychee with `.lychee.toml` for local Markdown links, and
Skillsaw with `.skillsaw.yaml` for static skill, plugin, content, and security
checks. Lychee checks local paths and external URL availability. The lint CI job
uses the same configurations and Markdown glob.

`skipper make test` runs regression tests for the Python validator, including validation
of the current repository. It also copies each plugin into a temporary directory
to validate its manifests, skills, and references independently of the checkout.
Dependencies remain separate plugins and must be installed by the
consuming harness. Marketplace installation uses plugin directories directly.

These structural checks do not establish harness compatibility or skill behavior.
Skillsaw is an additional static-quality check; it does not replace the Python
validator or establish harness compatibility or skill behavior.
