# Assisted Installer Agentic development

The [development skill](SKILL.md) guides plugin placement, concise skill authoring,
and successful `make validate` and `make test` runs before commits. It is local to
this repository and excluded from distributed plugins.

The canonical source is in `.agents/skills/`; Claude discovers the same skill
through a relative symlink in `.claude/skills/`.

Example:

```text
Use $assisted-installer-agentic-development to add a new skill to this repository.
```
