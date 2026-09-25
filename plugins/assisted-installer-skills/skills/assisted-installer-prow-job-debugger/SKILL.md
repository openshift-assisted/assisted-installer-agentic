---
name: assisted-installer-prow-job-debugger
description: Use when triaging OpenShift Assisted Installer Prow/ci-operator job failures.
---

# Analyze OpenShift Prow Test Logs

## When to use

- User pastes a **GCS artifact URL** (e.g. `https://gcsweb-ci.apps.ci.l2s4.p1.openshiftapps.com/gcs/test-platform-results/...`)
- User asks to **debug** a failing OpenShift CI / Prow job
- User asks to **analyze any test** in [openshift/release](https://github.com/openshift/release) — by test `as` name, prow job name, config path, or repo/branch
- User asks for the **workflow or steps** of a job or test in openshift/release

For release-only analysis (no artifact URL), resolve the test in `ci-operator/config/`, walk workflows/steps in `ci-operator/step-registry/`, and explain what the test does. If a GCS URL is also provided, combine config walk-through with artifact triage.

Do **not** use in-cluster debugging (`oc get prowjob`, ci-operator pods). Stay on artifacts and repo config unless the user only wants static config analysis.

## Architecture (short)

1. **openshift/release** — test definitions and step-registry
2. **Prow** — schedules jobs; artifacts land in GCS
3. **ci-operator** — multi-stage `pre` → `test` → `post`; logs under `${ARTIFACT_DIR}`
4. **Component repos** — implementation invoked by step scripts

Load [architecture-and-repos.md](references/architecture-and-repos.md) for the GitHub repo/branch table and external docs.

## Investigation order

1. Parse `job_name` → repo, branch, test `as` — see [gcs-and-config.md](references/gcs-and-config.md).
2. List failed steps from `ci-operator-step-graph.json`; pick the **first failing non-gather step** — see [investigation.md](references/investigation.md).
3. Guess the GCS path: `artifacts/<test-as>/<failing-step>/build-log.txt`. With a job variant (e.g. `edge`), try `artifacts/<variant>-<test-as>/...` first.
4. Only if that path fails (404 / HTML index): call `list_artifacts` **once** on `artifacts/` to recover the real `<test-as>` name.
5. Get the failing step's bash script from `artifacts/ci-operator-step-graph.json` (do not guess GitHub paths when the graph is available) — see [gcs-and-config.md](references/gcs-and-config.md).
6. Component repo scripts referenced by the step (same branch) — prefer a repo tarball over many single-file curls. Use [architecture-and-repos.md](references/architecture-and-repos.md) for branch rules.
7. Dig past symptoms into component logs until you have a **terminal** root cause — see [investigation.md](references/investigation.md). Use [artifact-layout.md](references/artifact-layout.md) as the path map. For operator-style jobs, also load [assisted-operator.md](references/assisted-operator.md).

Avoid probing multiple guessed GitHub URLs for configs or step scripts. Always extract the script from `ci-operator-step-graph.json` when you have a job URL.

## Report

Always structure the answer per [report-format.md](references/report-format.md). Do not state a root cause without artifact evidence. When a bug is identified, explain it, show reasoning, and quote decisive log lines.

## Reference index

Load these on demand via the relative links below (paths are relative to this skill directory so they resolve when the skill is installed from git into a cloud agent). Do not load every file up front — open only what the current investigation step needs.

| File | When to load | What you get |
|------|--------------|--------------|
| [gcs-and-config.md](references/gcs-and-config.md) | Steps 1 and 5; also when resolving a test with no GCS URL, reading `finished.json`, or extracting a step’s bash script from the step graph | URL → repo/branch/test-as parsing; workflow/`ref` walk in openshift/release; `finished.json` fields; jq to list failed steps and dump `<test-as>-commands` scripts |
| [investigation.md](references/investigation.md) | Steps 2 and 7; whenever several steps failed, the first finding looks like a symptom, or only ofcir/rbac dirs exist | Which failure to triage first; skip-gather rules; false-positive earlier steps; symptom→log table and terminal-cause stop list; triage checklist; RED ALERT |
| [architecture-and-repos.md](references/architecture-and-repos.md) | Step 6; when choosing a GitHub org/repo/branch or raw URL for component source | Repo/branch lookup table, wrong-guess table, external CI docs |
| [artifact-layout.md](references/artifact-layout.md) | Step 7; when you need a concrete path under `artifacts/` (gather trees, journals, pods, sos, libvirt) | Artifact directory map; per-gather contents and caveats; what GCS often lacks |
| [assisted-operator.md](references/assisted-operator.md) | Step 7 for `*e2e-ai-operator*`, ZTP, CAPI, or other operator-style jobs | `deploy/operator/` script map; multi-stage phases; hub vs spoke vs day-2 guest log locations |
| [report-format.md](references/report-format.md) | Before writing the final answer | Required report sections, bug-reporting rule, cherry-pick evidence requirements, URL→test-as examples |
