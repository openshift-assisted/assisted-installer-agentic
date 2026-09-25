# Report format

Always use this structure. Do not state a root cause without evidence from artifacts.

For **release-only** analysis (no failing run), use the same sections but omit **Root cause** unless discussing a known failure; under **Configuration** document the full workflow chain, env vars, triggers (presubmit/postsubmit/periodic), and links to step scripts.

```markdown
## Job
- URL, prow job name, repo/branch, test-as, result (from `finished.json`)
- Commit SHA (`refs.base_sha` or `refs.pulls[0].sha`) and PR link if presubmit (from `finished.json`)

## Configuration
- Config path, workflow, cluster_profile, notable env

## Failure summary
- Failed steps (from `ci-operator-step-graph.json`, or "none — prepare phase" if substeps missing)
- Primary failing step (first non-gather in flow), exit condition, likely layer: infra (ofcir/acquire) | deploy (pre) | test | gather (post)
- Note if later / gather failures were skipped after a terminal cause

## Root cause (required when a bug is identified)
Explain what broke in plain language — not only which step failed.
The conclusion must be a **terminal** cause (mechanism), not a symptom like "nodes never came up" or "pod not Ready". If the first finding is a symptom, the Reasoning section must show the next layer of log evidence (journals, pod logs, events) that answers *why*.

### Conclusion
- One-sentence verdict: what failed **and why** (terminal mechanism). Reject conclusions that only restate wait/timeout/not-Ready symptoms.

### Reasoning
Numbered chain from observation → inference → conclusion. Include:
- Which artifact paths were read and in what order (including gather journals / pod logs when the symptom required them)
- How the failing step maps to config/workflow/source
- Why alternative causes were ruled out (or what remains uncertain)
- Explicit note if digging stopped because the cause is terminal (e.g. registry auth) or because artifacts were missing

### Evidence
For each supporting log, cite the **artifact path** (relative to the job root or GCS URL) and quote the **relevant lines only** — not whole files.

Use fenced code blocks with the important lines visible; prefix non-essential context with `# ...` or truncate with `...` on its own line. **Bold** or mark the single line(s) that directly prove the conclusion.

Example:

`artifacts/<test-as>/assisted-baremetal-test/build-log.txt`
\`\`\`
...
**TASK [Run test] ***********************************************
**fatal: [primary]: FAILED! => {"msg": "non-zero return code", "rc": 1}**
...
\`\`\`

If multiple logs support the same conclusion (step log + gathered service log), include each with its path.

## Next steps
- Concrete fixes, files to change, or follow-up checks.

**Actionable remediations only.** Do not write vague guidance like "cherry-pick the fix from master" or "apply the AUTHFILE patch" without identifying *which* change.

When recommending a **cherry-pick**, **backport**, or **port of an existing fix**, you **must** include all of the following that you can obtain (fetch GitHub compare/blame/commits/PR pages or raw history as needed before writing Next steps):

1. **Source commit SHA** (full or unambiguous short SHA) on the fixed branch
2. **Source PR** (number + URL) when the fix landed via a pull request
3. **Exact file path(s)** and the function/symbol/hunk to change
4. **Source branch** (where the fix already exists) and **target branch** (where to apply it)
5. **One-line summary** of what the commit changes (so a human can verify the right commit)

If you cannot find the commit/PR after a reasonable search, say so explicitly and give the closest evidence you have (e.g. file path + diff of working vs broken branch) instead of inventing a cherry-pick instruction.

Bad (insufficient):
- Cherry-pick the `AUTHFILE` patch for `hypershift_cli` from `master` to `release-ocm-2.13`.

Good:
- Cherry-pick `abc1234` ([openshift/assisted-service#12345](https://github.com/openshift/assisted-service/pull/12345)) from `master` onto `release-ocm-2.13` — updates `deploy/operator/capi/deploy_capi_cluster.sh` `hypershift_cli` to pass `--authfile ${AUTHFILE}` to `podman run`.
```

## Bug reporting rule (mandatory)

When triage identifies a **bug** (regression, misconfiguration, product defect, infra flake with identifiable mechanism — not merely "job failed"):

1. **Explain the bug** — what behavior was expected vs what happened.
2. **Show your reasoning** — the numbered chain in **Reasoning** above; no unsupported leaps.
3. **Cite log evidence** — at least one quoted excerpt per claim, with paths and highlighted decisive lines.

If the root cause is **not** proven (RED ALERT, missing gather, inconclusive logs), say so explicitly under **Failure summary** and do **not** invent a bug section — list what evidence is missing instead.

## Examples

### Presubmit URL → test name

URL:

`.../pr-logs/pull/openshift_assisted-test-infra/2810/pull-ci-openshift-assisted-test-infra-master-e2e-metal-assisted-external-4-22/2057040220838170624/`

| Field | Value |
| ------- | ------- |
| Prow job | `pull-ci-openshift-assisted-test-infra-master-e2e-metal-assisted-external-4-22` |
| Test `as` | `e2e-metal-assisted-external-4-22` |
| Artifacts dir | `artifacts/e2e-metal-assisted-external-4-22/` |
| Workflow | `assisted-ofcir-baremetal` (`PLATFORM=external`, `OPENSHIFT_VERSION=4.22`) |

### Periodic job name

`periodic-ci-openshift-assisted-test-infra-master-e2e-metal-assisted-4-22-periodic` → test `as`: `e2e-metal-assisted-4-22-periodic`, branch `master`, repo `assisted-test-infra`.
