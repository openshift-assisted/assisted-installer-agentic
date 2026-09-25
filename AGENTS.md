# AGENTS.md

This repository contains standalone agent skills. Skill instructions are
executable guidance, so changes require the same care as code changes.

## Repository layout

```text
plugins/
  assisted-installer-skills/
    .claude-plugin/plugin.json
    .codex-plugin/plugin.json
    skills/
      <skill>/SKILL.md              # shared, independently usable skill
  assisted-installer-workflows/
    .claude-plugin/plugin.json
    .codex-plugin/plugin.json
    skills/
      <skill>/SKILL.md              # discoverable workflow and contract
.agents/plugins/marketplace.json
.claude-plugin/marketplace.json
scripts/                     # deterministic validation and isolation tests
```

## Development and validation

Use the [repository development skill](.agents/skills/assisted-installer-agentic-development/SKILL.md)
for any modification to this repository.
