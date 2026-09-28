# Plugins

The repository distributes two plugins through the `assisted-installer`
marketplace. Each plugin packages Markdown skills with supporting references;
its Claude and Codex manifests expose the same skill directory. Installation
uses those directories directly, without a build step. See the
[installation instructions](installation.md).

## Plugin roles

| Plugin | Purpose |
| --- | --- |
| [`assisted-installer-skills`](../plugins/assisted-installer-skills/) | Shared, bounded capabilities that can be used independently or composed by a workflow. |
| [`assisted-installer-workflows`](../plugins/assisted-installer-workflows/) | End-to-end orchestration that owns task selection, sequencing, checkpoints, and aggregate results. |

Browse each plugin directory or the host's plugin browser for its current
contents. Individual skill instructions and supporting references define their
own inputs, outputs, prerequisites, and execution boundaries.

## Package boundaries

Install both plugins when using a workflow that requires shared skills. The
[Claude workflow manifest](../plugins/assisted-installer-workflows/.claude-plugin/plugin.json)
declares that dependency; the
[Codex workflow manifest](../plugins/assisted-installer-workflows/.codex-plugin/plugin.json)
does not declare automatic dependency installation.

Shared skills remain independently usable. Workflows load required skills
through the host's discovery mechanism and stop dependent work if a required
skill is unavailable. References needed at runtime stay inside their plugin so
they remain usable after installation.

Repository-local contributor guidance is maintained separately from distributed
plugins. See [Contributing](../CONTRIBUTING.md) for placement and authoring rules.
