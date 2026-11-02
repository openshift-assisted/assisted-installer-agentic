---
name: resolve-mgmt-issues
description: Use when selecting high-confidence, low-complexity MGMT Jira bugs for user-approved resolution through external SDLC skills or workflows.
---

# Resolve MGMT Issues

## Introduction: approve a specific outcome

This workflow selects MGMT issues, proposes an outcome for each, and asks the user
to approve that specific outcome before taking action. The two possible work
outcomes are:

- **Implementation**: use the [implementation flow](references/implementation-flow.md)
  when the issue remains eligible and its requested fix is relevant.
- **Close as no longer relevant**: use the [close flow](references/close-flow.md)
  when evidence supports that the issue/request is no longer relevant.

Present the proposed outcome and its rationale with each issue, then record the
user's approval per issue and per outcome. A user may also explicitly decline all
work on a particular issue; that is a separate disposition, not an outcome
approval. Approval or silence about other issues never implies a decline. Before
acting, refresh each approved issue. If new information changes the appropriate
outcome, pause and get explicit approval for that new outcome; the previous
approval does not transfer between flows.

## Inputs and prerequisites

- `N`: maximum candidates, default `3`; reject non-positive or non-integer input
  before querying. This limits selection, not retrieval.
- Optional: repository context, preferred external software development lifecycle
  (SDLC) skill or workflow, and local report path.
- Require authenticated Jira search and issue retrieval through the invoker's
  available capabilities. Implementation requires an external SDLC skill; its
  absence does not block read-only selection. Approved closure requires Jira
  capability to assign an issue, add a comment, and transition it to a closed
  status. Applying an explicit decline requires Jira label-write capability.
  Missing write capability does not block read-only selection.

Own selection, outcome proposals, approval, sequencing, and aggregate reporting.
Use existing triage labels; external SDLC skills own implementation and
validation.

## Retrieve and rank candidates

Search the `MGMT` project with this exact JQL:

```jql
project = MGMT AND issuetype = Bug AND assignee IS EMPTY AND status IN ("To Do", "New") AND labels = "ai-triage-confidence-high" AND labels IN ("ai-triage-complexity-1", "ai-triage-complexity-2") AND labels NOT IN (ai-triage-skip) ORDER BY priority DESC, key ASC
```

See the [Jira field reference](https://confluence.atlassian.com/jirasoftware/advanced-searching-fields-reference-1528533189.html)
for query syntax. Complete pagination and deduplicate by key, preserving query
order across pages. Retrieval failure or uncertain completeness returns `blocked`
with the error and discovered keys; select nothing from incomplete results.

Issues labeled `ai-triage-skip` are excluded by the JQL. Exclude and report
conflicting complexity labels without changing them. Group complexity 1 before
2, preserving Jira's priority-descending, key-ascending order within each group;
do not sort priority names or IDs yourself. Freeze the first
N candidates, or all if fewer qualify. Selection covers caller-visible issues
during retrieval, not a snapshot.

## Assess issues and propose outcomes

Read the selected issues, relevant context, and current Jira state before
presenting them. Discover appropriate external SDLC skills through the host,
honoring any caller-named skill. Report missing prerequisites; ask the user to
choose if multiple skills fit and repository guidance does not resolve the
choice.

For each issue, propose one outcome:

- **Implementation** if the issue still qualifies and the requested fix remains
  relevant. State the requested scope, repository, and proposed SDLC skill or
  blocker.
- **Close as no longer relevant** if the issue no longer qualifies or available
  context shows that the requested fix is outdated or irrelevant. State the
  specific qualification change or evidence and give a concrete closure
  rationale. An eligibility mismatch alone does not prove irrelevance. If the
  evidence does not support a closure rationale, ask the user to clarify or
  report the issue as blocked; do not invent a reason or propose an unsupported
  closure.

Present a numbered table with issue links, requested fixes, complexity, Jira
priority, repositories, proposed outcome and rationale, and proposed SDLC skills
or blockers. Include match, exclusion, and selection counts; explain that
complexity takes precedence.

## Obtain outcome-specific approval

Ask the calling user which proposed outcomes they approve, by issue key or row
number, and which specific issues they explicitly decline all work on. A decline
must identify issue keys/rows or explicitly say to decline work on all listed
issues. Record approvals as exact issue-to-outcome mappings (`implement` or
`close_as_irrelevant`) and record explicit work declines separately. `all` in
the approval request approves each row's proposed outcome, not both outcomes;
`none` approves no outcomes and does not itself decline any issue. If the user
requests an outcome different from the proposal, clarify the rationale and
obtain explicit approval for that specific outcome.

An issue omitted from either response, or approval of other issues, is not an
explicit decline. An issue cannot be both approved for an outcome and explicitly
declined; clarify conflicting responses before acting. If the user rejects a
proposed outcome but it is unclear whether they want another outcome or no work
at all, clarify. Do not relabel an issue unless the user specifically declines
work on it. Clarify ambiguous
answers and get explicit approval for any additional issue. Silence is not
consent. Return `awaiting_approval` if a response is unavailable. Process any
explicit declines before returning `declined` when no outcomes are approved;
mark issues without an approved outcome `not_approved` unless explicitly
declined.

An approval for one outcome never authorizes the other. The corresponding flow
reference defines the actions authorized by each outcome. Preserve external
skills' approval checkpoints and prior authorization without repeating
approvals. Selection alone does not authorize Jira updates, merging, or
deployment.

## Apply explicit declines

For each issue the user explicitly declines further work on, remove every
existing label whose name starts with `ai-triage-`, then add `ai-triage-skip`.
Preserve all labels that do not start with that prefix. This label change is
authorized by the user's explicit decline; do not apply it to unmentioned or
merely unapproved issues. Verify the resulting labels and report the change.
If Jira label-write access is unavailable or any update fails, report the issue
as `blocked` and disclose any label changes that succeeded. Do not report the
relabeling as complete unless all prior `ai-triage-*` labels are removed and
`ai-triage-skip` is present.

## Route approved outcomes

Process approved issues in displayed order. Refresh each before making external
changes. If its current state and context still support the approved outcome,
load and follow the corresponding [implementation flow](references/implementation-flow.md)
or [close flow](references/close-flow.md). If new information changes which
outcome is appropriate, stop and present the evidence to the user for explicit
approval of the new outcome; do not silently switch flows or act under the old
approval. Do not replace candidates.

## Output and stopping conditions

Return the query/completeness, N, counts, ranked candidates, approved
issue-to-outcome mappings, and per-issue outcomes; optionally save to the
requested local path. Include issue links, proposed and approved outcomes,
explicit declines, confirmed Jira assignees, statuses and labels, skills used,
changes/artifacts, PR links, validation evidence, closure rationale and comment
confirmation, and blockers or pending approvals. Mark explicit work declines as
`explicitly_declined`, distinguish them from `not_approved`, and report the
verified label change. Distinguish a produced fix from Jira closure.

- `empty`: complete search found no matches.
- `awaiting_approval`: an outcome choice or approval is pending; retain completed
  work.
- `declined`: no presented issue outcome was approved, and any explicit work
  declines were relabeled successfully. If no work was explicitly declined, no
  label change is required. Report all decline and label-update results.
- `complete`: every approved implementation has been validated, with a PR opened
  and passing CI on its latest revision; every approved closure has its assignee,
  closed status, and explanatory comment verified; and every explicit decline
  has its `ai-triage-*` labels replaced with `ai-triage-skip`. No work or
  decision is pending. Pending, failed, or unverified CI does not qualify as
  complete.
- `partial`: at least one approved outcome or explicit decline reached a
  verified result and another did not, or a changed outcome was declined and no
  user decision is pending.
- `blocked`: invalid input, incomplete retrieval, no rankable candidates, or
  required prerequisites/remote operations prevented every approved outcome or
  explicit decline from reaching a verified result. If no work outcome was
  approved and an explicit decline could not be relabeled, use `blocked` rather
  than `declined`.

Use `awaiting_approval` over `partial` or `blocked` while a user decision is pending.
