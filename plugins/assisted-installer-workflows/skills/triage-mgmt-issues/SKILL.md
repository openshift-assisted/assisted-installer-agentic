---
name: triage-mgmt-issues
description: Grade unassigned bugs in the MGMT Jira project in To Do or New status by applying jira-triage-complexity to each issue.
---

# Triage MGMT Issues

## Inputs and prerequisites

Require Jira read access and access to `jira-triage-complexity` from
`assisted-installer-skills`. Load its public contract and the
[workflow report contract](references/report-contract.md). Block if unavailable.

The invoker supplies authenticated Jira read access and handles the choice of
client, provider-specific query syntax, and pagination mechanics. This workflow
defines the canonical JQL, required evidence, ordering, and completeness checks;
it must not prescribe a Jira client or embed provider-specific commands. Use
the supplied capability and return `blocked` if it cannot satisfy those checks.

Optional inputs: repository context, local report path, and maximum issues
(default all). Limits must be positive and must be integers. "Stop after N issues"
limits assessments, not the query.

## Retrieve the issue set

1. Verify access to the `MGMT` project and search with this exact JQL:

   ```jql
   project = MGMT AND issuetype = Bug AND assignee IS EMPTY AND status IN ("To Do", "New") AND labels NOT IN (ai-triage-complexity-1, ai-triage-complexity-2, ai-triage-complexity-3, ai-triage-complexity-4, ai-triage-complexity-5, ai-triage-complexity-6, ai-triage-complexity-7, ai-triage-complexity-8, ai-triage-complexity-9, ai-triage-complexity-10, ai-triage-confidence-high, ai-triage-confidence-medium, ai-triage-confidence-low) ORDER BY key ASC
   ```

2. Complete pagination even for limited assessments, deduplicating by key while
   preserving query order. Retain issue payloads, sources, and report metadata.
   On retrieval failure or uncertain completeness, return `blocked` with discovered
   keys and the error; dispatch nothing.
3. Freeze the first N keys when limited, otherwise all keys. Never replace failed
   assessments or poll for new work. Successful retrieval with no matches returns
   `empty`. Selection covers caller-visible issues during retrieval, not a snapshot.

## Grade each issue

For each selected issue, grade it using `jira-triage-complexity` from
`assisted-installer-skills`. Pass the issue payload, sources, repository
context, and the per-issue result contract. Each invocation must:

- Load and use `jira-triage-complexity` for that issue only.
- Follow the skill's rubric and contract, fetching additional context only
  when needed.
- Include a `label` field in the per-issue entry: `ai-triage-complexity-N`
  where N is the integer complexity score from the rubric. Set `label` to
  null for ungraded issues.
- Include a `confidence_label` field in the per-issue entry:
  `ai-triage-confidence-{confidence}` where `{confidence}` is the confidence
  value from the grading result (`high`, `medium`, or `low`). Set
  `confidence_label` to null for ungraded issues.
- Not select issues, delegate, write files, mutate Jira or source, or run
  tests.
- Return `{skill_used, result, error}` with the skill's unchanged JSON result;
  report loading failure instead of improvising a grade.

Validate issue identity, required-skill use, and the shared result contract
for each completed assessment. Check loading/invocation traces when available;
absent traces mean unverified, not missing skill use. Without traces, accept
an explicit declaration and disclose this verification limit in the summary.
Known non-use, missing declarations, malformed responses, and execution
failures are ungraded. Preserve valid results; never retry automatically,
substitute skills, or grade in the parent.

## Labeling

The report includes `label` and `confidence_label` fields in each per-issue
entry. The invoker is responsible for applying labels to Jira issues and
removing any stale `ai-triage-complexity-*` and `ai-triage-confidence-*`
labels from previous runs before applying the new ones.

## Output and stopping conditions

Return the aggregate report and optionally save its JSON to the requested local
path. This is the only permitted write; Jira/source remain read-only and no tests
are run.

- `complete`: enumeration finished and every selected issue has a valid grade.
- `partial`: at least one issue was graded and at least one remains ungraded.
- `blocked`: a prerequisite or enumeration failed, or no selected issue could be graded.
- `empty`: enumeration finished with zero matches; no issues were graded.

Stop on prerequisite failure; otherwise finish the frozen queue and report all
outcomes.
