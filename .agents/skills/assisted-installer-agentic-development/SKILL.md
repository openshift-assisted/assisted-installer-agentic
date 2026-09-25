---
name: assisted-installer-agentic-development
description: Use when developing or modifying skills, workflows, and tooling in the assisted-installer-agentic repository.
---

# Assisted Installer Agentic development

Use the requested change and repository context as inputs. Follow `AGENTS.md`
and [CONTRIBUTING.md](../../../CONTRIBUTING.md).

## Choose the correct location

Before adding or changing a skill, verify its intended use against the selected
plugin:

- `assisted-installer-skills`: bounded capabilities usable independently, such as
  assessing one issue or investigating one CI job.
- `assisted-installer-workflows`: end-to-end orchestration that composes skills
  and owns task selection, sequencing, checkpoints, and aggregate results.
- `.agents/skills/`: development guidance for this repository, outside distributed
  plugins and marketplace catalogs. Add a matching relative directory symlink
  at `.claude/skills/<name>` pointing to `../../.agents/skills/<name>`.

Explain the placement briefly. Resolve a mismatch before creating or changing
the skill.

Keep shared skills independently usable with documented inputs, outputs, and
capability boundaries. Allow normal skill discovery, instruction loading, and
invocation; do not couple workflows to private installation paths or on-disk
handoffs.

When a workflow explicitly names a skill for a step, it must discover, load, and
use that skill for the step. Do not silently substitute another skill or
recreate its procedure. If the required skill is unavailable or ambiguous, stop
the dependent step and report the missing prerequisite. Delegated steps must
pass this requirement to the worker.

Keep shared skills in `assisted-installer-skills` and end-to-end orchestration
in `assisted-installer-workflows`. Declare required shared-plugin dependencies
in the Claude manifest; do not invent unsupported cross-plugin dependency
fields for Codex.

Keep plugin Markdown references relative and inside their plugin so they work
after installation. Refer to other plugins' skills through discovery and
invocation, not filesystem links. Repository documentation may link across
plugins.

## Write focused instructions

- Keep frontmatter descriptions concise and specific about purpose and triggers.
- Keep `SKILL.md` focused; move substantial detail into linked `references/*.md`
  files and state when to read them. Avoid duplicating guidance.
- Define inputs, outputs, capability boundaries, approval checkpoints, and stopping
  conditions. Do not imply additional permissions or remote writes.
- Prefer semantic capabilities over provider-specific commands. Keep packaged
  references inside their plugin; link relevant public documentation when
  available. See the [Agent Skills specification](https://agentskills.io/specification).

Treat external systems as capability providers. Describe semantic operations
first and use a provider-specific CLI only as a fallback. Preserve project
instructions from the target repository and discover its validation commands
instead of inventing them.

Behavioral changes to distributed skills should update the plugin and
marketplace release metadata when a new plugin release is intended.

## Validate before committing

When `plugins/` or `scripts/` have been modified, immediately before creating a
git commit run `skipper make validate` and `skipper make test` against the
final changes. These commands are not required for commits limited to other
paths, after individual edits, when no commit is being created, or merely
because a task is complete. Both commands MUST exit with status 0, with all
validation checks and tests passing. Inspect their output to confirm this. If
either fails, fix the issue and rerun the affected command before committing.
If either cannot run, report the exact command and error and stop without
committing. Commit only when requested. Return a concise summary of changes
and check results, or the blocker preventing completion.
