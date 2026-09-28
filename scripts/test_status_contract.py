"""Regression tests for the triage-mgmt-issues aggregate status contract.

The aggregate status must satisfy:
  - ``complete`` only when every selected issue has a valid grade.
  - ``partial`` when at least one issue is graded and at least one is ungraded.
  - Skipped issues (``ai-triage-skip``) are counted as ``ungraded``.

A previous change allowed ``complete`` when issues were intentionally skipped,
which caused runs with 5 graded and 1 skipped issue to report ``complete``
instead of ``partial``.  These tests prevent that regression.
"""

import re
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = (
    REPO_ROOT
    / "plugins"
    / "assisted-installer-workflows"
    / "skills"
    / "triage-mgmt-issues"
)
SKILL_MD = WORKFLOW / "SKILL.md"
REPORT_CONTRACT = WORKFLOW / "references" / "report-contract.md"


class StatusContractTests(unittest.TestCase):
    """Ensure status definitions prevent skipped issues from counting as complete."""

    def setUp(self):
        self.skill_text = SKILL_MD.read_text(encoding="utf-8")
        self.contract_text = REPORT_CONTRACT.read_text(encoding="utf-8")

    # ------------------------------------------------------------------
    # SKILL.md status definitions
    # ------------------------------------------------------------------

    def test_complete_requires_valid_grade_in_skill(self):
        """``complete`` in SKILL.md must require every issue to have a valid grade."""
        match = re.search(
            r"^- `complete`:\s*(.+?)(?:\n- `|$)",
            self.skill_text,
            re.MULTILINE | re.DOTALL,
        )
        self.assertIsNotNone(match, "missing ``complete`` definition in SKILL.md")
        definition = " ".join(match.group(1).split())
        self.assertNotIn(
            "skipped",
            definition.lower(),
            "``complete`` must not count skipped issues as complete",
        )
        self.assertIn(
            "valid grade",
            definition.lower(),
            "``complete`` must require a valid grade for every selected issue",
        )

    def test_partial_covers_any_ungraded_in_skill(self):
        """``partial`` must apply when any issue is ungraded, including skipped."""
        match = re.search(
            r"^- `partial`:\s*(.+?)(?:\n- `|$)",
            self.skill_text,
            re.MULTILINE | re.DOTALL,
        )
        self.assertIsNotNone(match, "missing ``partial`` definition in SKILL.md")
        definition = " ".join(match.group(1).split())
        self.assertIn("ungraded", definition.lower())
        self.assertNotIn(
            "without a skip label",
            definition.lower(),
            "``partial`` must not exclude skipped issues from ungraded count",
        )

    # ------------------------------------------------------------------
    # report-contract.md consistency
    # ------------------------------------------------------------------

    def test_contract_does_not_equate_skipped_with_complete(self):
        """report-contract.md must not override SKILL.md by treating skips as complete."""
        self.assertNotRegex(
            self.contract_text,
            r"complete.*when.*skipped",
            "report-contract.md must not allow skipped issues to satisfy ``complete``",
        )

    def test_skipped_counted_as_ungraded_in_contract(self):
        """report-contract.md must count skipped issues as ungraded."""
        self.assertIn(
            "Skipped issues are counted as `ungraded`",
            self.contract_text,
        )

    # ------------------------------------------------------------------
    # Regression scenario: 5 graded + 1 skipped
    # ------------------------------------------------------------------

    def test_five_graded_one_skipped_is_not_complete(self):
        """Contract must classify 5 graded + 1 skipped (ungraded) as ``partial``.

        The ``complete`` definition must require *every* selected issue to have
        a valid grade.  A run with ``selected=6, graded=5, ungraded=1`` must
        never be ``complete`` regardless of skip labels.
        """
        match = re.search(
            r"^- `complete`:\s*(.+?)(?:\n- `|$)",
            self.skill_text,
            re.MULTILINE | re.DOTALL,
        )
        self.assertIsNotNone(match)
        definition = " ".join(match.group(1).split())
        # The word "every" (or "all") combined with "valid grade" means
        # any ungraded issue (including skipped) prevents ``complete``.
        self.assertTrue(
            "every" in definition.lower() or "all" in definition.lower(),
            "``complete`` must require *every* selected issue to have a valid grade",
        )
        self.assertIn("valid grade", definition.lower())
        # Skipped issues must not be mentioned as an alternative.
        for phrase in ("or skipped", "or intentionally skipped", "skip"):
            self.assertNotIn(
                phrase,
                definition.lower(),
                f"``complete`` definition must not contain '{phrase}'",
            )


if __name__ == "__main__":
    unittest.main()
