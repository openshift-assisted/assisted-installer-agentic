import shutil
import tempfile
import unittest
from pathlib import Path

from validate import Validator


class DevelopmentSkillTests(unittest.TestCase):
  def setUp(self):
    temporary = tempfile.TemporaryDirectory()
    self.addCleanup(temporary.cleanup)
    self.root = Path(temporary.name)
    self.skill = self.root / ".agents/skills/development"
    self.skill.mkdir(parents=True)
    (self.skill / "SKILL.md").write_text(
      "---\nname: development\ndescription: Develop this repository.\n---\n",
      encoding="utf-8",
    )
    self.alias = self.root / ".claude/skills/development"
    self.alias.parent.mkdir(parents=True)
    self.alias.symlink_to("../../.agents/skills/development")

  def errors(self):
    validator = Validator(self.root)
    validator.validate_development_skills()
    return validator.errors

  def test_relative_alias_survives_checkout_relocation(self):
    moved = self.root / "relocated"
    moved.mkdir()
    for name in (".agents", ".claude"):
      (self.root / name).rename(moved / name)
    validator = Validator(moved)
    skills = validator.validate_development_skills()
    self.assertEqual(validator.errors, [])
    self.assertEqual(skills, [moved / ".agents/skills/development"])

  def test_missing_alias_is_rejected(self):
    self.alias.unlink()
    self.assertTrue(any("must be a relative symlink" in error for error in self.errors()))

  def test_invalid_alias_targets_are_rejected(self):
    cases = (
      (str(self.skill), "must be relative"),
      ("../../.agents/skills/missing", "broken or cyclic"),
      ("development", "broken or cyclic"),
      ("../../.agents", "must target the matching"),
      ("../../.agents/skills/development/SKILL.md", "must target the matching"),
      ("../../elsewhere", "must target the matching"),
    )
    (self.root / "elsewhere").mkdir()
    for target, message in cases:
      with self.subTest(target=target):
        self.alias.unlink()
        self.alias.symlink_to(target)
        self.assertTrue(any(message in error for error in self.errors()))

  def test_copied_claude_skill_is_rejected(self):
    self.alias.unlink()
    shutil.copytree(self.skill, self.alias)
    errors = self.errors()
    self.assertTrue(any("must be a relative symlink" in error for error in errors))
    self.assertTrue(any("local skills must live directly" in error for error in errors))

  def test_extra_alias_is_rejected(self):
    (self.alias.parent / "other-name").symlink_to("../../.agents/skills/development")
    self.assertTrue(any("must target the matching" in error for error in self.errors()))

  def test_local_sources_in_other_locations_are_rejected(self):
    for path in ("skills/other", "nested/.agents/skills/other", ".agents/skills/group/other"):
      with self.subTest(path=path):
        source = self.root / path
        source.mkdir(parents=True)
        (source / "SKILL.md").write_text("# Misplaced skill\n", encoding="utf-8")
        self.assertTrue(any(
          f"{path}/SKILL.md: local skills must live directly" in error
          for error in self.errors()
        ))

  def test_canonical_skill_cannot_be_a_symlink(self):
    self.skill.rename(self.root / "source")
    self.skill.symlink_to("../../source")
    self.assertTrue(any("source must not be a symlink" in error for error in self.errors()))

  def test_canonical_entrypoint_cannot_be_a_symlink(self):
    entrypoint = self.skill / "SKILL.md"
    entrypoint.rename(self.root / "instructions.md")
    entrypoint.symlink_to("../../../instructions.md")
    self.assertTrue(any("source must not be a symlink" in error for error in self.errors()))

  def test_distributed_plugin_skills_do_not_need_claude_aliases(self):
    plugin_skill = self.root / "plugins/example/skills/shared"
    plugin_skill.mkdir(parents=True)
    (plugin_skill / "SKILL.md").write_text("# Plugin skill\n", encoding="utf-8")
    self.assertEqual(self.errors(), [])

  def test_skill_roots_cannot_be_symlinks(self):
    for path in (".agents/skills", ".claude/skills"):
      with self.subTest(path=path):
        source = self.root / path
        moved = source.with_name("moved-skills")
        source.rename(moved)
        source.symlink_to("moved-skills")
        self.assertTrue(any("must be a real directory" in error for error in self.errors()))
        source.unlink()
        moved.rename(source)


if __name__ == "__main__":
  unittest.main()
