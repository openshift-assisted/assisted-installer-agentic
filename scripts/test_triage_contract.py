"""Contract tests for the triage-mgmt-issues status definitions.

The aggregate status must satisfy:
  - ``complete``: every selected issue is either graded or intentionally
    skipped (``ai-triage-skip``).  A run where every issue has a complexity
    score or a skip label is complete.
  - ``partial``: at least one issue remains ungraded *without* a skip label.
    Intentionally skipped issues do not force ``partial``.

Skipped issues are counted as ``ungraded`` for the count invariant
(``selected = graded + ungraded``), but they satisfy completion.
"""

import re
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SKILL_MD = (
    REPO_ROOT
    / "plugins"
    / "assisted-installer-workflows"
    / "skills"
    / "triage-mgmt-issues"
    / "SKILL.md"
)
REPORT_CONTRACT = (
    REPO_ROOT
    / "plugins"
    / "assisted-installer-workflows"
    / "skills"
    / "triage-mgmt-issues"
    / "references"
    / "report-contract.md"
)

STATUS_RE = re.compile(
    r"^- `(complete|partial)`:\s*(.+?)(?=\n- `|\n\n|\Z)",
    re.MULTILINE | re.DOTALL,
)


def _status_definitions(text):
  """Return a dict mapping status name to its normalized definition text."""
  return {
      match.group(1): " ".join(match.group(2).split())
      for match in STATUS_RE.finditer(text)
  }


class TriageStatusContractTests(unittest.TestCase):
  """Ensure the complete/partial definitions encode score-or-skip semantics."""

  def setUp(self):
    self.skill_text = SKILL_MD.read_text(encoding="utf-8")
    self.contract_text = REPORT_CONTRACT.read_text(encoding="utf-8")
    self.skill_defs = _status_definitions(self.skill_text)

  # -- complete must allow intentional skips --

  def test_complete_allows_skipped_issues_in_skill(self):
    """SKILL.md ``complete`` must accept graded-or-skipped, not grade-only."""
    definition = self.skill_defs.get("complete", "")
    self.assertIn("skipped", definition.lower(),
        "``complete`` must mention intentionally skipped issues")
    self.assertNotIn("valid grade", definition.lower(),
        "``complete`` must not require a valid grade for every issue")

  def test_complete_allows_skipped_issues_in_contract(self):
    """report-contract.md must also accept graded-or-skipped for complete."""
    normalized = " ".join(self.contract_text.split())
    self.assertTrue(
        re.search(r"`complete`.*graded.*skipped", normalized),
        "report-contract.md ``complete`` must accept skipped issues")

  # -- partial must distinguish skip-labeled from non-skip ungraded --

  def test_partial_excludes_skip_labeled_in_skill(self):
    """SKILL.md ``partial`` must not apply to issues with a skip label."""
    definition = self.skill_defs.get("partial", "")
    self.assertIn("skip label", definition.lower(),
        "``partial`` must mention skip labels to avoid ambiguity")

  def test_partial_excludes_skip_labeled_in_contract(self):
    """report-contract.md ``partial`` must exclude skip-labeled issues."""
    self.assertIn("without a skip label", self.contract_text,
        "report-contract.md must clarify that ``partial`` excludes skip-labeled issues")

  # -- count invariant preserved --

  def test_skipped_counted_as_ungraded(self):
    """Skipped issues must be counted as ungraded for the invariant."""
    self.assertIn("Skipped issues are counted as `ungraded`",
        self.contract_text,
        "report-contract.md must preserve the skipped-as-ungraded invariant")

  # -- JQL excludes previously labeled issues --

  def test_jql_excludes_skip_label(self):
    """The canonical JQL must exclude ai-triage-skip to prevent re-selection."""
    self.assertIn("ai-triage-skip", self.skill_text,
        "JQL must exclude ai-triage-skip")


if __name__ == "__main__":
  unittest.main()
