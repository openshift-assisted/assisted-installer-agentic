# Close flow

Use this flow only for an issue whose explicitly approved outcome is
`close_as_irrelevant`. The base workflow presents the closure rationale and
records approval for this specific outcome before this flow makes any Jira
changes. If closure has not been explicitly approved, return to the base workflow
for outcome-specific approval; implementation approval is not sufficient.

## Confirm approval and closure rationale

Verify that the issue-to-outcome record explicitly approves
`close_as_irrelevant` and that the user approved the rationale presented for the
issue. This approval authorizes assigning the issue to the closure approver,
transitioning it to a closed status, and adding a comment with the approved
rationale. Refresh the Jira state and context before making changes. If new
information changes the rationale or makes another outcome appropriate, stop
and return to the base workflow for explicit approval of the revised outcome.
Do not treat an eligibility mismatch alone as proof that the issue is irrelevant,
and do not invent a closure reason.

## Close approved issues

For each issue with confirmed closure approval:

1. Assign it to the user who approved closure. Do not guess the user's Jira
   identity or assign it to another account.
2. Transition it to a closed status using a valid Jira transition. If it is
   already closed, verify and retain its closed status rather than attempting a
   redundant transition.
3. Add a Jira comment explaining the concrete reason the issue is no longer
   relevant and why it is being closed. Base the explanation on the issue
   context and the rationale approved by the user.
4. Verify the approver is the assignee, the issue is closed, and the comment is
   present before reporting `closed_as_irrelevant`.

If the approver's Jira identity or write access is unavailable, or the issue is
not already closed and no valid closing transition is available, or any update
fails, report the closure as `blocked` and disclose every update that succeeded.
Do not report closure as complete unless the assignee, closed status, and
explanatory comment are all confirmed. Return the per-issue outcome to the base
workflow for its aggregate report.
