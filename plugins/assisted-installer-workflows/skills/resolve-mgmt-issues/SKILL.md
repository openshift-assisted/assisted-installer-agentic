---
name: resolve-mgmt-issues
description: Use when selecting high-confidence, low-complexity MGMT Jira bugs for user-approved resolution through external SDLC skills or workflows.
---

# Resolve MGMT Issues

## Inputs and prerequisites

- `N`: maximum candidates, default `3`; reject non-positive or non-integer input
  before querying. This limits selection, not retrieval.
- Optional: repository context, preferred external software development lifecycle
  (SDLC) skill or workflow, and local report path.
- Require authenticated Jira search and issue retrieval through the invoker's
  available capabilities. Implementation also requires an external SDLC skill;
  its absence does not block read-only selection.

Own selection, approval, sequencing, and reporting. Use existing triage labels;
external SDLC skills own implementation and validation.

## Retrieve and rank candidates

Search the `MGMT` project with this exact JQL:

```jql
project = MGMT AND issuetype = Bug AND assignee IS EMPTY AND status IN ("To Do", "New") AND labels = "ai-triage-confidence-high" AND labels IN ("ai-triage-complexity-1", "ai-triage-complexity-2") ORDER BY priority DESC, key ASC
```

See the [Jira field reference](https://confluence.atlassian.com/jirasoftware/advanced-searching-fields-reference-1528533189.html)
for query syntax. Complete pagination and deduplicate by key, preserving query
order across pages. Retrieval failure or uncertain completeness returns `blocked`
with the error and discovered keys; select nothing from incomplete results.

Exclude and report conflicting complexity labels without changing them. Group
complexity 1 before 2, preserving Jira's priority-descending, key-ascending order
within each group; do not sort priority names or IDs yourself. Freeze the first
N candidates, or all if fewer qualify. Selection covers caller-visible issues
during retrieval, not a snapshot.

## Present candidates and obtain approval

Read selected issues and relevant context to identify the requested fixes and
repositories. Discover appropriate external SDLC skills through the host, honoring
any caller-named skill. Report missing prerequisites; ask the user to choose if
multiple skills fit and repository guidance does not resolve the choice.

Present a numbered table of issue links, requested fixes, complexity, Jira
priority, repositories, and proposed SDLC skills or blockers. Include match,
exclusion, and selection counts; explain that complexity takes precedence.

Ask which issues the calling user approves: keys, row numbers, all, or none.
Record exact approved keys; clarify ambiguous answers and get explicit approval
for any additional issue. Wait for approval; silence is not consent.
Return `awaiting_approval` if a response is unavailable, or `declined` for none.

Approval covers implementation and opening a PR for each approved issue under
existing session permissions. Preserve external skills' approval checkpoints
and prior authorization without repeating approvals. Selection alone does not
authorize Jira updates, merging, or deployment.

## Implement the approved issues

Process approved issues in displayed order. Refresh each before starting: skip
and report issues that no longer qualify or have conflicting complexity labels;
obtain renewed approval if the requested fix has materially changed.

Load and invoke the chosen SDLC skill or workflow using its public contract.
Pass the issue key/URL, current context, repository, approved scope, authorization,
and constraints. Require it to follow repository instructions, isolate changes
per issue, implement the fix, validate it, open a PR, and verify passing CI on the
latest PR revision before reporting completion. Require it to inspect CI failures,
resolve them within the approved scope, and recheck CI after fixes; report blockers
it cannot resolve. Require the PR link in its results; a `complete` status is
sufficient confirmation of passing CI, without returning CI results as evidence.
Missing or failed skill loading/invocation blocks that issue; do not substitute
a named skill or implement its procedure yourself.

Wait for results; invocation alone is not success. Preserve partial work, continue
independent approved issues, and stop work dependent on failed prerequisites.
Do not automatically retry invocations, replace candidates, or poll for more work.

## Output and stopping conditions

Return the query/completeness, N, counts, ranked candidates, approved keys, and
per-issue outcomes; optionally save to the requested local path. Include issue
links, skills used, changes/artifacts, PR links, validation evidence, and
blockers, skips, or pending approvals. Mark unapproved issues `not_approved`.
Distinguish a produced fix from Jira closure.

- `empty`: complete search found no matches.
- `awaiting_approval`: a user choice or approval is pending; retain completed work.
- `declined`: no presented issues were approved.
- `complete`: every approved issue is implemented and validated, with a PR opened
  and passing CI on its latest revision, with no work pending. Pending, failed,
  or unverified CI does not qualify as complete.
- `partial`: some approved issues completed; others were skipped, blocked, or failed.
- `blocked`: invalid input, incomplete retrieval, no rankable candidates, or no
  approved issue could complete.

Use `awaiting_approval` over `partial` or `blocked` while a user decision is pending.
