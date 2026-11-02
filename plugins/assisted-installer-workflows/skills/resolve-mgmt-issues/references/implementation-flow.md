# Implementation flow

Use this flow only for an issue whose explicitly approved outcome is
`implement`, and whose eligibility and requested scope still match the proposal
shown to the user. If the refresh shows that the issue no longer qualifies, the
fix is no longer relevant, or the approved scope materially changed, stop and
return to the base workflow to obtain explicit approval for the new outcome or
scope. Do not switch to the [close flow](close-flow.md) under implementation
approval.

## Confirm approval and Jira state

Verify that the issue-to-outcome record explicitly approves `implement`. This
approval authorizes assigning the issue to the approving user's Jira account,
transitioning it to `In Progress`, implementing the approved scope, and opening a
PR under existing session permissions. It does not authorize merging or
deployment. If the requested fix has materially changed since approval, present
the changed scope and obtain renewed implementation approval before proceeding.
A pending decision returns `awaiting_approval`; do not treat silence as consent.

Before invoking the external SDLC skill, assign the issue to the approving user's
Jira account and transition it to `In Progress`. Do not guess the approver's Jira
identity or use another account. Verify both updates succeeded before starting
implementation. If the approver's identity, Jira write access, or a valid status
transition is unavailable, or either update fails, do not start implementation.
Report the issue as `blocked` and disclose any update that succeeded before the
failure.

## Invoke the SDLC skill

Load and invoke the chosen SDLC skill or workflow using its public contract. Pass
the issue key/URL, current context, repository, approved scope, authorization,
and constraints. Require it to:

- Follow repository instructions and isolate changes per issue.
- Implement the approved fix and validate it.
- Open a PR and verify passing CI on the latest PR revision before reporting
  completion.
- Inspect CI failures, resolve them within the approved scope, and recheck CI
  after fixes; report blockers it cannot resolve.

Require the PR link in its results. A `complete` status is sufficient
confirmation of passing CI; CI results need not be returned as evidence. Missing
or failed skill loading/invocation blocks that issue. Do not substitute a named
skill or implement its procedure yourself.

Wait for results; invocation alone is not success. Preserve partial work,
continue independent approved issues, and stop work dependent on failed
prerequisites. Do not automatically retry invocations, replace candidates, or
poll for more work. Return the per-issue outcome to the base workflow for its
aggregate report.
