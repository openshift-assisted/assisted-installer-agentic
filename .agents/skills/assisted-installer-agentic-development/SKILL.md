---
name: assisted-installer-agentic-development
description: Develop and maintain skills, workflows, and tooling in the assisted-installer-agentic repository.
---

# Assisted Installer Agentic development

Use the requested change and repository context as inputs. Follow `AGENTS.md`
and [CONTRIBUTING.md](../../../CONTRIBUTING.md).

## Choose the correct location

Before adding a skill, verify its intended use against the selected plugin:

- `assisted-installer-skills`: bounded capabilities usable independently, such as
  assessing one issue or investigating one CI job.
- `assisted-installer-workflows`: end-to-end orchestration that composes skills
  and owns task selection, sequencing, checkpoints, and aggregate results.
- `.agents/skills/`: development guidance for this repository, outside distributed
  plugins and marketplace catalogs. Add a matching relative directory symlink
  at `.claude/skills/<name>` pointing to `../../.agents/skills/<name>`.

Explain the placement briefly. Resolve a mismatch before creating the skill;
workflows must discover and invoke required skills through their public contracts.

## Write focused instructions

- Keep frontmatter descriptions concise and specific about purpose and triggers.
- Keep `SKILL.md` focused; move substantial detail into linked `references/*.md`
  files and state when to read them. Avoid duplicating guidance.
- Define inputs, outputs, capability boundaries, approval checkpoints, and stopping
  conditions. Do not imply additional permissions or remote writes.
- Prefer semantic capabilities over provider-specific commands. Keep packaged
  references relative and inside their plugin; link relevant public documentation
  when available. See the [Agent Skills specification](https://agentskills.io/specification).

## Validate before committing

Before every commit, run `make validate` and `make test` on the final changes.
Both commands MUST exit with status 0, with all validation checks and tests passing.
Inspect their output to confirm this. If either fails or cannot run, report the exact
command and error and stop without committing. Commit only when requested. Return a concise
summary of changes and check results, or the blocker preventing completion.
