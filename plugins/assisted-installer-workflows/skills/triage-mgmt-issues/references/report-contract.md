# Workflow report contract

## Per-issue result

Each issue assessment returns one JSON object:

- `skill_used`: `assisted-installer-skills/jira-triage-complexity` when loaded and
  used, otherwise null. This is a logical identity, not an installation path.
- `result`: the shared skill's unchanged JSON result, including valid blocked
  results; null when loading or execution fails before producing a result.
- `error`: explanation when no result is available, otherwise null. A blocked
  result already explains its blocker in `rationale`.

The wrapper belongs to this workflow; do not add its fields to the shared skill's
JSON. A declaration is not independent execution proof. If traces are unavailable,
disclose that required-skill use is reported rather than independently verified
in the aggregate summary.

## Aggregate report

Return a brief Markdown summary table (issue link, grade, confidence, outcome)
and a JSON object containing the fields below. Save the JSON only if requested.

| Field | Value |
| --- | --- |
| `status` | `complete`, `partial`, `blocked`, or `empty`. |
| `project` | Resolved ID, key (`MGMT`), name, and known URL; null if unresolved. |
| `query` | Exact JQL from `SKILL.md`; null if search was not started. |
| `retrieval` | Object with `started_at`, `finished_at`, `complete`, and `error`. Timestamps describe the read window, not a snapshot. |
| `selection` | Object with `limit` (requested maximum or null for all) and `total_matches` (deduplicated count after complete enumeration, otherwise null). |
| `selected_keys` | Unique selected issue keys; during failed enumeration, only the keys discovered so far. |
| `counts` | Object with integer `selected`, `graded`, and `ungraded` counts. |
| `issues` | One entry per selected key, in key order, using the fields below. |
| `blockers` | Run-level errors or missing prerequisites; empty array otherwise. |
| `report_file` | Object with requested `path` or null, `status` (`not_requested`, `written`, or `failed`), and `error` or null. |

Record retrieval start/end times, project identity, and the exact query during
enumeration. Preserve unknown metadata as null rather than inventing values.

Each issue entry contains:

- `issue_key`, `issue_url`, `summary`: selection metadata; unknown values are null.
- `skill_used`: reported skill identity, or null if unavailable.
- `outcome`: `graded` or `ungraded`.
- `label`: the Jira label to apply, formatted as `ai-triage-complexity-N` where N
  is the integer complexity score, or null if the issue was not graded.
- `confidence_label`: the Jira label to apply, formatted as
  `ai-triage-confidence-{confidence}` where `{confidence}` is `high` or
  `medium`, or null if the issue was not graded or was skipped.
- `skip_label`: `ai-triage-skip` when the issue must be skipped, otherwise
  null. An issue is skipped when any of the following applies: (1) the agent
  lacks permission to view relevant links or information required for the
  assessment, (2) the issue description is missing or too vague to assess,
  (3) the grading result has low confidence, or (4) the agent cannot produce
  a defensible complexity score on the current run (including a blocked
  result, a malformed or missing result, or an execution failure). When
  `skip_label` is set, `label` and `confidence_label` must be null.
- `skip_reason`: a concise explanation of which skip criterion applied, or
  null when `skip_label` is null. Required when `skip_label` is set.
- `result`: validated, unchanged JSON returned by `jira-triage-complexity`, or null
  if no valid result was obtained. A valid blocked result is retained as ungraded.
  Skipped entries retain the shared result or error for auditability.
- `error`: reason for an ungraded outcome, or null when graded.

Require `selected = graded + ungraded = length(selected_keys) = length(issues)`.
Skipped issues are counted as `ungraded`; the invariant is preserved.
Counts describe selected issues, not all project matches when a limit applies or
retrieval is incomplete. A successful limited run can be `complete` even when
additional matches were not selected. No matches imply
`empty` only after successful retrieval. A prerequisite failure before retrieval
has zero counts and `blocked` status. Preserve discovered keys as ungraded if
enumeration fails; do not invent records for keys the provider never returned.

The canonical JQL in `SKILL.md` excludes `ai-triage-skip`, so issues that
receive a skip label are not selected by future runs.

Write failures change only `report_file`. Always return grades and errors to the
caller even when the optional file cannot be written.
