---
name: assisted-installer-agentic-docs
description: Use when creating, editing, or reviewing markdown documentation in the assisted-installer-agentic repository.
---

# Assisted Installer Agentic documentation

Keep repository docs focused on repository purpose, top-level plugins,
packaging, installation, validation, and contribution. They must remain accurate
without updates when individual skills or workflows are added, removed, renamed,
or modified.

- Describe and link to plugins; do not list individual skills, counts, examples,
  or links that depend on a particular skill. Keep skill-specific behavior and
  contracts inside the owning plugin; do not present them as plugin-wide guarantees.
- Keep the README brief and link to details in [docs/](../../../docs/README.md).
  Keep authoring conventions in [CONTRIBUTING.md](../../../CONTRIBUTING.md).
  Repository governance may reference local contributor skills.
- Write concisely and link to existing explanations instead of duplicating them.
  Verify claims against repository configuration and link to official tool docs.

Before finishing, check that replacing the skills inside a plugin would not make
repository docs inaccurate or break their links. Update navigation and run
relevant Markdown and link checks under the repository's existing requirements.
