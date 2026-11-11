"""Small two-plugin repository fixture for structural and isolation tests."""

import json
from pathlib import Path


def write_json(path: Path, data: dict) -> None:
  path.parent.mkdir(parents=True, exist_ok=True)
  path.write_text(json.dumps(data), encoding="utf-8")


def create_repo(root: Path) -> None:
  claude_entries = []
  codex_entries = []
  for name in ("workflow", "shared"):
    plugin = root / "plugins" / name
    for harness in (".claude-plugin", ".codex-plugin"):
      manifest = {"name": name, "version": "0.1.0"}
      if harness == ".codex-plugin":
        manifest["skills"] = "./skills/"
      elif name == "workflow":
        manifest["dependencies"] = ["shared"]
      write_json(plugin / harness / "plugin.json", manifest)
    skill = plugin / "skills" / f"{name}-skill"
    (skill / "references").mkdir(parents=True)
    (skill / "SKILL.md").write_text(
      f"---\nname: {name}-skill\ndescription: Example skill.\n---\n"
      "\n[Guide](references/guide.md)\n", encoding="utf-8",
    )
    (skill / "references" / "guide.md").write_text("# Guide\n", encoding="utf-8")
    claude_entries.append({"name": name, "source": f"./plugins/{name}"})
    codex_entries.append({
      "name": name,
      "source": {"source": "local", "path": f"./plugins/{name}"},
      "policy": {"installation": "AVAILABLE", "authentication": "ON_INSTALL"},
      "category": "Developer Tools",
    })
  write_json(root / ".claude-plugin" / "marketplace.json", {
    "name": "sample", "plugins": claude_entries,
  })
  write_json(root / ".agents" / "plugins" / "marketplace.json", {
    "name": "sample", "interface": {"displayName": "Sample"}, "plugins": codex_entries,
  })
  write_json(root / "package.json", {
    "name": "sample-repo", "version": "0.1.0",
    "pi": {"skills": ["./plugins/*/skills"], "extensions": []},
  })
  (root / "README.md").write_text(
    "# Repository\n\n[Workflow](plugins/workflow/skills/workflow-skill/SKILL.md)\n",
    encoding="utf-8",
  )
