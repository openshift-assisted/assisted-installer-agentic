---
name: jira-triage-complexity
description: Use when assessing exactly one Jira issue and assigning an evidence-based implementation complexity rating from 1 to 10, with confidence, reasoning, and sources.
---

# Jira Triage Complexity

## Inputs

- Exactly one Jira issue key, issue URL, or supplied issue record identifying
  one issue. A supplied record may include comments, links, and repository context.
- Optional access to relevant repositories and an optional local output path.

For multiple issues, boards, filters, queries, or conflicting issue identities,
return `blocked` and request one issue. Batch selection and subagent dispatch
belong to the calling workflow; do not perform either here.

## Assessment

1. Use supplied issue evidence when sufficient. Otherwise fetch the identified
   issue and relevant comments or links through an available Jira capability;
   use a CLI fallback only when its syntax and authentication are known. Linked
   issues provide context; do not grade them separately. If the caller forbids
   fetching, assess only the supplied evidence.
2. Establish the requested change, acceptance criteria, affected components,
   design work, risks, and likely validation. Inspect relevant repository
   guidance and code when available and useful; repository access is optional.
3. Apply the [scoring rubric](references/scoring-rubric.md). Distinguish observed
   facts from inference and cite sources. Missing information reduces confidence
   or prevents grading; it does not automatically increase complexity.
4. Return one JSON result using the [report contract](references/report-schema.md).
   Write it locally only if an output path was supplied. If writing fails,
   return the result with the delivery error; preserve the assessment status.

## Boundaries and completion

Jira and source access are read-only. Do not edit issues or source, run tests,
implement the task, or poll for updates. A rating grants no implementation or
mutation authority. The only permitted write is the requested local report.

- `complete`: one issue has a supported integer rating from 1 to 10, including
  a provisional rating when assumptions are explicit and confidence is low.
- `blocked`: input, access, or evidence prevents grading. Return a null score
  and confidence, explain the blocker, and identify the smallest clarification
  or missing capability. Do not guess or expand the scope to work around it.
