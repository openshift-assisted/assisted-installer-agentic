import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

from test_support import create_repo, write_json
from validate import Validator


class StructureTests(unittest.TestCase):
  def setUp(self):
    temporary = tempfile.TemporaryDirectory()
    self.addCleanup(temporary.cleanup)
    self.root = Path(temporary.name)
    create_repo(self.root)
    self.skill = self.root / "plugins/workflow/skills/workflow-skill/SKILL.md"

  def validate(self, plugin=None):
    validator = Validator(self.root)
    with contextlib.redirect_stdout(io.StringIO()):
      result = validator.run(plugin)
    return result, validator.errors

  def test_valid_repository_and_root_documentation_links(self):
    result, errors = self.validate()
    self.assertEqual(result, 0, errors)

  def test_development_skill_can_reference_repository_without_registration(self):
    skill = self.root / ".agents/skills/review-contract"
    skill.mkdir(parents=True)
    (skill / "SKILL.md").write_text(
      "---\nname: review-contract\ndescription: Review instructions.\n---\n"
      "\n[Repository](../../../README.md)\n", encoding="utf-8",
    )
    aliases = self.root / ".claude/skills"
    aliases.mkdir(parents=True)
    (aliases / skill.name).symlink_to(f"../../.agents/skills/{skill.name}")
    result, errors = self.validate()
    self.assertEqual(result, 0, errors)

  def test_development_skill_missing_entrypoint_is_reported(self):
    (self.root / ".agents/skills/review-contract").mkdir(parents=True)
    result, errors = self.validate()
    self.assertEqual(result, 1)
    self.assertIn(".agents/skills/review-contract: missing SKILL.md", errors)
    result, errors = self.validate("workflow")
    self.assertEqual(result, 0, errors)

  def test_development_skill_names_and_readme_links_are_validated(self):
    skill = self.root / ".agents/skills/review-contract"
    skill.mkdir(parents=True)
    (skill / "SKILL.md").write_text(
      "---\nname: wrong\ndescription: Review instructions.\n---\n", encoding="utf-8",
    )
    (skill / "README.md").write_text(
      "# Review\n\n[Missing](missing.md)\n[Outside](../../../../outside.md)\n",
      encoding="utf-8",
    )
    result, errors = self.validate()
    self.assertEqual(result, 1)
    for message in ("name must be review-contract", "missing link target", "link escapes repository"):
      self.assertTrue(any(message in error for error in errors), errors)

  def test_development_and_plugin_skill_names_cannot_collide(self):
    skill = self.root / ".agents/skills/shared-skill"
    skill.mkdir(parents=True)
    (skill / "SKILL.md").write_text(
      "---\nname: shared-skill\ndescription: Review instructions.\n---\n", encoding="utf-8",
    )
    result, errors = self.validate()
    self.assertEqual(result, 1)
    self.assertTrue(any("duplicate skill name shared-skill" in error for error in errors), errors)

  def test_plugin_links_cannot_escape_to_sibling_or_root(self):
    original = self.skill.read_text(encoding="utf-8")
    links = (
      "[Other](../../../shared/skills/shared-skill/SKILL.md)",
      "[Root](../../../../README.md)",
      "[Other][dependency]\n\n[dependency]: ../../../shared/skills/shared-skill/SKILL.md",
      "[Root](%2E%2E/%2E%2E/%2E%2E/%2E%2E/README.md)",
    )
    for link in links:
      with self.subTest(link=link):
        self.skill.write_text(original + "\n" + link + "\n", encoding="utf-8")
        result, errors = self.validate("workflow")
        self.assertEqual(result, 1)
        self.assertTrue(any("link escapes plugin package" in error for error in errors), errors)

  def test_local_reference_links_and_encoded_filenames(self):
    guide = self.skill.parent / "references/extra guide.md"
    guide.write_text("# Extra\n", encoding="utf-8")
    with self.skill.open("a", encoding="utf-8") as output:
      output.write(
        '\n[Extra](references/extra%20guide.md#extra)\n'
        '[Angle](<references/extra guide.md>)\n'
        '[Named][extra]\n\n[extra]: references/extra%20guide.md "Extra guide"\n'
      )
    result, errors = self.validate()
    self.assertEqual(result, 0, errors)

  def test_symlinked_reference_cannot_escape_package(self):
    (self.skill.parent / "references/root.md").symlink_to(self.root / "README.md")
    with self.skill.open("a", encoding="utf-8") as output:
      output.write("\n[Root](references/root.md)\n")
    result, errors = self.validate()
    self.assertEqual(result, 1)
    self.assertTrue(any("link escapes plugin package" in error for error in errors), errors)

  def test_both_catalogs_require_every_plugin_exactly_once(self):
    for catalog in (".claude-plugin/marketplace.json", ".agents/plugins/marketplace.json"):
      path = self.root / catalog
      original = path.read_text(encoding="utf-8")
      for mutation in ("missing", "duplicate", "wrong-source"):
        with self.subTest(catalog=catalog, mutation=mutation):
          data = json.loads(original)
          if mutation == "missing":
            data["plugins"].pop()
          elif mutation == "duplicate":
            data["plugins"].append(data["plugins"][-1].copy())
          elif catalog.startswith(".claude"):
            data["plugins"][-1]["source"] = "./plugins/workflow"
          else:
            data["plugins"][-1]["source"]["path"] = "./plugins/workflow"
          write_json(path, data)
          result, errors = self.validate("workflow")
          self.assertEqual(result, 1, errors)
          expected = {
            "missing": "marketplace: missing plugin: shared",
            "duplicate": "duplicate plugin name: shared",
            "wrong-source": "plugin source must resolve to plugins/shared",
          }[mutation]
          self.assertTrue(any(expected in error for error in errors), errors)
          path.write_text(original, encoding="utf-8")

  def test_marketplace_names_must_match(self):
    path = self.root / ".agents/plugins/marketplace.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    data["name"] = "different"
    write_json(path, data)
    result, errors = self.validate()
    self.assertEqual(result, 1)
    self.assertIn("Claude and Codex marketplace names must match", errors)

  def test_manifest_identity_and_version_consistency(self):
    for harness in (".claude-plugin", ".codex-plugin"):
      path = self.root / "plugins/shared" / harness / "plugin.json"
      original = path.read_text(encoding="utf-8")
      for field, value, message in (
        ("name", "wrong", "name must be shared"),
        ("version", "0.2.0", "manifest versions must match"),
      ):
        with self.subTest(harness=harness, field=field):
          data = json.loads(original)
          data[field] = value
          write_json(path, data)
          result, errors = self.validate("workflow")
          self.assertEqual(result, 1)
          self.assertTrue(any(message in error for error in errors), errors)
          path.write_text(original, encoding="utf-8")


if __name__ == "__main__":
  unittest.main()
