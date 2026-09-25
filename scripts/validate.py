#!/usr/bin/env python3
"""Validate isolated agent skill packages."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path
from urllib.parse import unquote, urlsplit


NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
FRONTMATTER_RE = re.compile(r"\A---\n(.*?)\n---(?:\n|\Z)", re.DOTALL)
LINK_RE = re.compile(r"!?\[[^]]*\]\((<[^>]+>|[^)\s]+)(?:\s+[^)]*)?\)")
REFERENCE_RE = re.compile(r"^ {0,3}\[[^]\n]+\]:\s*(<[^>]+>|\S+)", re.MULTILINE)


class Validator:
    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.errors: list[str] = []
        self.claude_marketplace_name: str | None = None
        self.claude_marketplace_plugins: set[str] = set()
        self.codex_marketplace_name: str | None = None
        self.codex_marketplace_plugins: set[str] = set()

    def error(self, message: str) -> None:
        self.errors.append(message)

    def frontmatter(self, path: Path) -> dict[str, str] | None:
        text = path.read_text(encoding="utf-8")
        match = FRONTMATTER_RE.match(text)
        if not match:
            self.error(f"{path.relative_to(self.repo_root)}: missing YAML frontmatter")
            return None

        fields: dict[str, str] = {}
        for line in match.group(1).splitlines():
            if ":" not in line or line.startswith((" ", "\t")):
                continue
            key, value = line.split(":", 1)
            fields[key.strip()] = value.strip().strip("'\"")
        for required in ("name", "description"):
            if not fields.get(required):
                self.error(f"{path.relative_to(self.repo_root)}: missing frontmatter {required}")
        return fields

    def validate_links(self, path: Path, package_root: Path | None = None) -> None:
        text = path.read_text(encoding="utf-8")
        boundary = (package_root or self.repo_root).resolve()
        for target in LINK_RE.findall(text) + REFERENCE_RE.findall(text):
            target = target.strip("<>")
            parsed = urlsplit(target)
            if parsed.scheme in ("http", "https", "mailto") or target.startswith("#"):
                continue
            target_path = unquote(parsed.path)
            if not target_path:
                continue
            resolved = (path.parent / target_path).resolve()
            try:
                resolved.relative_to(boundary)
            except ValueError:
                scope = "plugin package" if package_root else "repository"
                self.error(f"{path.relative_to(self.repo_root)}: link escapes {scope}: {target}")
                continue
            if not resolved.exists():
                self.error(f"{path.relative_to(self.repo_root)}: missing link target: {target}")

    def validate_markdown(self, path: Path, package_root: Path | None = None) -> None:
        text = path.read_text(encoding="utf-8")
        if re.search(r"(?:/home/|/Users/|/tmp/|/var/)", text):
            self.error(f"{path.relative_to(self.repo_root)}: contains an absolute local path")
        self.validate_links(path, package_root)

    def validate_skill(self, skill_dir: Path) -> dict[str, str] | None:
        skill = skill_dir / "SKILL.md"
        if not skill.is_file():
            self.error(f"{skill_dir.relative_to(self.repo_root)}: missing SKILL.md")
            return None
        fields = self.frontmatter(skill)
        if fields:
            if fields.get("name") != skill_dir.name:
                self.error(f"{skill.relative_to(self.repo_root)}: name must be {skill_dir.name}")
            if not NAME_RE.fullmatch(fields.get("name", "")):
                self.error(f"{skill.relative_to(self.repo_root)}: invalid skill name")
        return fields

    def validate_plugin_manifest(self, plugin: Path, plugin_names: set[str] | None = None) -> None:
        versions: set[str] = set()
        for manifest_path in (
            plugin / ".claude-plugin" / "plugin.json",
            plugin / ".codex-plugin" / "plugin.json",
        ):
            if not manifest_path.is_file():
                self.error(f"{plugin.relative_to(self.repo_root)}: missing {manifest_path.parent.name}/plugin.json")
                continue
            try:
                data = json.loads(manifest_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError as error:
                self.error(f"{manifest_path.relative_to(self.repo_root)}: invalid JSON: {error}")
                continue
            if not isinstance(data, dict):
                self.error(f"{manifest_path.relative_to(self.repo_root)}: manifest must be an object")
                continue
            if data.get("name") != plugin.name:
                self.error(f"{manifest_path.relative_to(self.repo_root)}: name must be {plugin.name}")
            if not re.fullmatch(r"\d+\.\d+\.\d+", str(data.get("version", ""))):
                self.error(f"{manifest_path.relative_to(self.repo_root)}: invalid semantic version")
            else:
                versions.add(data["version"])
            if manifest_path.parent.name == ".claude-plugin":
                dependencies = data.get("dependencies", [])
                if not isinstance(dependencies, list):
                    self.error(f"{manifest_path.relative_to(self.repo_root)}: dependencies must be a list")
                    continue
                for dependency in dependencies:
                    if isinstance(dependency, str):
                        dependency_name = dependency
                        dependency_marketplace = None
                    elif isinstance(dependency, dict):
                        dependency_name = dependency.get("name")
                        dependency_marketplace = dependency.get("marketplace")
                    else:
                        self.error(
                            f"{manifest_path.relative_to(self.repo_root)}: dependency must be a name or object"
                        )
                        continue
                    if not isinstance(dependency_name, str) or not NAME_RE.fullmatch(dependency_name):
                        self.error(
                            f"{manifest_path.relative_to(self.repo_root)}: invalid dependency name"
                        )
                        continue
                    local_dependency = dependency_marketplace in (None, self.claude_marketplace_name)
                    if local_dependency and dependency_name == plugin.name:
                        self.error(
                            f"{manifest_path.relative_to(self.repo_root)}: plugin cannot depend on itself"
                        )
                    if plugin_names is None:
                        continue  # An isolated plugin has no marketplace to resolve against.
                    if local_dependency and dependency_name not in plugin_names:
                        self.error(
                            f"{manifest_path.relative_to(self.repo_root)}: missing local dependency: {dependency_name}"
                        )
                    elif local_dependency and dependency_name not in self.claude_marketplace_plugins:
                        self.error(
                            f"{manifest_path.relative_to(self.repo_root)}: dependency not registered in Claude marketplace: {dependency_name}"
                        )
        if len(versions) > 1:
            self.error(f"{plugin.relative_to(self.repo_root)}: Claude and Codex manifest versions must match")

    def validate_plugin_contents(self, plugin: Path) -> list[Path]:
        skills_root = plugin / "skills"
        if not skills_root.is_dir():
            self.error(f"{plugin.relative_to(self.repo_root)}: missing skills directory")
            return []
        skill_dirs = sorted(path for path in skills_root.iterdir() if path.is_dir())
        for skill in skill_dirs:
            self.validate_skill(skill)
        for markdown in plugin.rglob("*.md"):
            self.validate_markdown(markdown, package_root=plugin)
        return skill_dirs

    def validate_marketplace(self) -> None:
        self.claude_marketplace_name = None
        self.claude_marketplace_plugins = set()
        marketplace = self.repo_root / ".claude-plugin" / "marketplace.json"
        if not marketplace.is_file():
            self.error("missing .claude-plugin/marketplace.json")
            return
        try:
            data = json.loads(marketplace.read_text(encoding="utf-8"))
        except json.JSONDecodeError as error:
            self.error(f"{marketplace.relative_to(self.repo_root)}: invalid JSON: {error}")
            return
        if not isinstance(data, dict):
            self.error(f"{marketplace.relative_to(self.repo_root)}: marketplace must be an object")
            return
        if not NAME_RE.fullmatch(str(data.get("name", ""))):
            self.error(f"{marketplace.relative_to(self.repo_root)}: invalid marketplace name")
        else:
            self.claude_marketplace_name = data["name"]
        plugins = data.get("plugins")
        if not isinstance(plugins, list) or not plugins:
            self.error(f"{marketplace.relative_to(self.repo_root)}: plugins must be a non-empty list")
            return
        seen: set[str] = set()
        for entry in plugins:
            if not isinstance(entry, dict):
                self.error(f"{marketplace.relative_to(self.repo_root)}: plugin entries must be objects")
                continue
            name = entry.get("name")
            if not isinstance(name, str) or not NAME_RE.fullmatch(name):
                self.error(f"{marketplace.relative_to(self.repo_root)}: invalid plugin name")
                continue
            if name in seen:
                self.error(f"{marketplace.relative_to(self.repo_root)}: duplicate plugin name: {name}")
                continue
            seen.add(name)
            source = entry.get("source")
            if not isinstance(source, str) or source.startswith(("/", "~")):
                self.error(f"{marketplace.relative_to(self.repo_root)}: plugin source must be relative")
                continue
            resolved = (self.repo_root / source).resolve()
            try:
                resolved.relative_to(self.repo_root.resolve())
            except ValueError:
                self.error(f"{marketplace.relative_to(self.repo_root)}: source escapes repository: {source}")
                continue
            if not resolved.is_dir():
                self.error(f"{marketplace.relative_to(self.repo_root)}: missing plugin source: {source}")
                continue
            if resolved != (self.repo_root / "plugins" / name).resolve():
                self.error(f"{marketplace.relative_to(self.repo_root)}: plugin source must resolve to plugins/{name}")
                continue
            self.claude_marketplace_plugins.add(name)

    def validate_codex_marketplace(self) -> None:
        self.codex_marketplace_name = None
        self.codex_marketplace_plugins = set()
        marketplace = self.repo_root / ".agents" / "plugins" / "marketplace.json"
        if not marketplace.is_file():
            self.error("missing .agents/plugins/marketplace.json")
            return
        try:
            data = json.loads(marketplace.read_text(encoding="utf-8"))
        except json.JSONDecodeError as error:
            self.error(f"{marketplace.relative_to(self.repo_root)}: invalid JSON: {error}")
            return
        if not isinstance(data, dict):
            self.error(f"{marketplace.relative_to(self.repo_root)}: marketplace must be an object")
            return
        if not NAME_RE.fullmatch(str(data.get("name", ""))):
            self.error(f"{marketplace.relative_to(self.repo_root)}: invalid marketplace name")
        else:
            self.codex_marketplace_name = data["name"]
        display_name = data.get("interface", {}).get("displayName") if isinstance(data.get("interface"), dict) else None
        if not isinstance(display_name, str) or not display_name.strip():
            self.error(f"{marketplace.relative_to(self.repo_root)}: missing interface.displayName")
        plugins = data.get("plugins")
        if not isinstance(plugins, list) or not plugins:
            self.error(f"{marketplace.relative_to(self.repo_root)}: plugins must be a non-empty list")
            return
        seen: set[str] = set()
        for entry in plugins:
            if not isinstance(entry, dict):
                self.error(f"{marketplace.relative_to(self.repo_root)}: plugin entries must be objects")
                continue
            name = entry.get("name")
            if not isinstance(name, str) or not NAME_RE.fullmatch(name):
                self.error(f"{marketplace.relative_to(self.repo_root)}: invalid plugin name")
                continue
            if name in seen:
                self.error(f"{marketplace.relative_to(self.repo_root)}: duplicate plugin name: {name}")
                continue
            seen.add(name)
            source = entry.get("source")
            if not isinstance(source, dict) or source.get("source") != "local":
                self.error(f"{marketplace.relative_to(self.repo_root)}: plugin source must be a local source object")
                continue
            source_path = source.get("path")
            if not isinstance(source_path, str) or not source_path.startswith("./"):
                self.error(f"{marketplace.relative_to(self.repo_root)}: local plugin source path must start with ./")
                continue
            resolved = (self.repo_root / source_path).resolve()
            try:
                resolved.relative_to(self.repo_root.resolve())
            except ValueError:
                self.error(f"{marketplace.relative_to(self.repo_root)}: source escapes repository: {source_path}")
                continue
            if not resolved.is_dir():
                self.error(f"{marketplace.relative_to(self.repo_root)}: missing plugin source: {source_path}")
                continue
            if resolved != (self.repo_root / "plugins" / name).resolve():
                self.error(f"{marketplace.relative_to(self.repo_root)}: plugin source must resolve to plugins/{name}")
                continue
            self.codex_marketplace_plugins.add(name)
            policy = entry.get("policy")
            if not isinstance(policy, dict):
                self.error(f"{marketplace.relative_to(self.repo_root)}: plugin policy must be an object")
            else:
                for field in ("installation", "authentication"):
                    if not isinstance(policy.get(field), str) or not policy[field].strip():
                        self.error(f"{marketplace.relative_to(self.repo_root)}: policy missing {field}")
            if not isinstance(entry.get("category"), str) or not entry["category"].strip():
                self.error(f"{marketplace.relative_to(self.repo_root)}: plugin entry missing category")

    def validate_development_skills(self) -> list[Path]:
        """Keep local skills canonical in .agents, with relative Claude aliases."""
        skills_root = self.repo_root / ".agents" / "skills"
        claude_root = self.repo_root / ".claude" / "skills"
        for root in (skills_root.parent, skills_root, claude_root.parent, claude_root):
            if root.is_symlink() or (root.exists() and not root.is_dir()):
                self.error(f"{root.relative_to(self.repo_root)}: must be a real directory")
                return []

        skills: dict[str, Path] = {}
        if skills_root.is_dir():
            for skill in sorted(skills_root.iterdir()):
                if skill.is_symlink() or (skill / "SKILL.md").is_symlink():
                    self.error(f"{skill.relative_to(self.repo_root)}: local skill source must not be a symlink")
                elif skill.is_dir():
                    skills[skill.name] = skill
                    self.validate_skill(skill)
                    for markdown in skill.rglob("*.md"):
                        self.validate_markdown(markdown)

        aliases = {path.name: path for path in claude_root.iterdir()} if claude_root.is_dir() else {}
        for name in sorted(skills.keys() | aliases.keys()):
            alias = claude_root / name
            label = alias.relative_to(self.repo_root)
            if not alias.is_symlink():
                self.error(f"{label}: must be a relative symlink to .agents/skills/{name}")
                continue
            if alias.readlink().is_absolute():
                self.error(f"{label}: Claude skill symlink must be relative")
                continue
            try:
                target = alias.resolve(strict=True)
            except (OSError, RuntimeError):
                self.error(f"{label}: broken or cyclic Claude skill symlink")
                continue
            if name not in skills or target != skills[name].resolve():
                self.error(f"{label}: must target the matching .agents/skills/{name} directory")

        # Ignore distributed plugins and do not follow Claude aliases.
        for directory, children, files in os.walk(self.repo_root, followlinks=False):
            root = Path(directory)
            children[:] = [name for name in children if name != ".git"]
            if root == self.repo_root:
                children[:] = [name for name in children if name != "plugins"]
            if "SKILL.md" in files and root.parent != skills_root:
                self.error(
                    f"{(root / 'SKILL.md').relative_to(self.repo_root)}: "
                    "local skills must live directly in .agents/skills/<name>"
                )
        return list(skills.values())

    def run(self, plugin_name: str | None = None) -> int:
        plugins_root = self.repo_root / "plugins"
        if not plugins_root.is_dir():
            self.error("missing plugins directory")
            plugins: list[Path] = []
        else:
            plugins = sorted(path for path in plugins_root.iterdir() if path.is_dir())
        all_plugin_names = {path.name for path in plugins}
        self.validate_marketplace()
        self.validate_codex_marketplace()
        if self.claude_marketplace_name != self.codex_marketplace_name:
            self.error("Claude and Codex marketplace names must match")
        for host, catalog in (
            ("Claude", self.claude_marketplace_plugins),
            ("Codex", self.codex_marketplace_plugins),
        ):
            for name in sorted(all_plugin_names - catalog):
                self.error(f"{host} marketplace: missing plugin: {name}")
            for name in sorted(catalog - all_plugin_names):
                self.error(f"{host} marketplace: unexpected plugin: {name}")
        for plugin in plugins:
            self.validate_plugin_manifest(plugin, all_plugin_names)
        if plugin_name:
            plugins = [path for path in plugins if path.name == plugin_name]
            if not plugins:
                self.error(f"plugin not found: {plugin_name}")

        all_skills: list[Path] = []
        for plugin in plugins:
            all_skills.extend(self.validate_plugin_contents(plugin))

        if not plugin_name:
            all_skills.extend(self.validate_development_skills())

        for markdown in self.repo_root.glob("*.md"):
            self.validate_markdown(markdown)

        names: dict[str, Path] = {}
        for skill in all_skills:
            skill = skill / "SKILL.md"
            if not skill.is_file():
                continue  # Already reported by validate_skill.
            fields = self.frontmatter(skill)
            if not fields or not fields.get("name"):
                continue
            previous = names.get(fields["name"])
            if previous:
                self.error(f"duplicate skill name {fields['name']}: {previous} and {skill}")
            names[fields["name"]] = skill

        if self.errors:
            for error in self.errors:
                print(f"ERROR: {error}")
            print(f"FAILED: {len(self.errors)} error(s)")
            return 1
        print(f"PASSED: validated {len(names)} skill(s)")
        return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--plugin")
    args = parser.parse_args()
    return Validator(args.repo_root.resolve()).run(args.plugin)


if __name__ == "__main__":
    sys.exit(main())
