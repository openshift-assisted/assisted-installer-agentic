# GCS URLs, config resolution, and job artifacts

## Parse a GCS artifact URL

### URL shape

```text
https://gcsweb-ci.apps.ci.l2s4.p1.openshiftapps.com/gcs/test-platform-results/
  {pr-logs|logs}/.../<prow-job-name>/<build-id>/
```

- **Presubmit**: `pr-logs/pull/<org>_<repo>/<pr>/<prow-job-name>/<build-id>/`
- **Periodic**: `logs/.../<prow-job-name>/<build-id>/` (path varies; job name segment is still identifiable)
- **Postsubmit / branch**: often `logs/...` with `branch-ci-openshift-...` job names

### Prow job name → repo, branch, test `as`

Job names follow:

```text
{pull|periodic|branch|postsubmit}-ci-openshift-<repo>-<branch>-<test-as>
```

**Example** (user-provided presubmit URL):

- URL job segment: `pull-ci-openshift-assisted-test-infra-master-e2e-metal-assisted-external-4-22`
- **repo**: `assisted-test-infra`
- **branch**: `master`
- **test `as`**: `e2e-metal-assisted-external-4-22` (matches `tests[].as` in config)

Config file: `ci-operator/config/openshift/assisted-test-infra/openshift-assisted-test-infra-master.yaml`

Artifacts for multi-stage tests: `artifacts/<test-as>/` (not the full prow job name).

### Parsing steps

1. Take the path segment immediately before the numeric **build-id** → full prow job name.
2. Strip prefix: `pull-ci-openshift-`, `periodic-ci-openshift-`, `branch-ci-openshift-`, or `postsubmit-ci-openshift-`.
3. Split remainder: known config files are `openshift-<repo>-<branch>.yaml` under `ci-operator/config/openshift/<repo>/`. Match the longest prefix `\<repo\>-\<branch\>` that corresponds to an existing config file; the suffix is **test `as`**.
4. Confirm with `rg 'as: <test-as>' ci-operator/config/openshift/<repo>/` or `rg 'name: <full-job-name>' ci-operator/jobs/`.

If parsing is ambiguous, grep the full job name in `ci-operator/jobs/`.

## Resolve workflow and steps

Use this for GCS triage **and** when the user asks to analyze a test in openshift/release without a job URL.

1. Open `ci-operator/config/openshift/<repo>/openshift-<repo>-<branch>.yaml` (or the path the user gave).
2. Find `tests:` entry where `as:` equals **test `as`** (search: `rg '^\s+as: <name>' ci-operator/config/openshift/<repo>/`).
3. Read `steps:` — `workflow:`, inline `pre`/`test`/`post`, `cluster_profile`, `env`.
4. For `workflow: <name>`, open `ci-operator/step-registry/**/<name>-workflow.yaml` (search: `rg 'as: <name>' ci-operator/step-registry`).
5. Follow `ref:` / `chain:` into `*-ref.yaml` and `*-commands.sh`.
6. For assisted jobs, trace scripts to [assisted-test-infra](https://github.com/openshift/assisted-test-infra) and product code to [assisted-service](https://github.com/openshift/assisted-service) on GitHub at the job's commit SHA.

Browse registry: [steps.ci.openshift.org](https://steps.ci.openshift.org/)

## Fetch job artifacts and config

- **Job logs** — fetch from the prow/gcsweb `job_url` (e.g. `build-log.txt`, `ci-operator-step-graph.json`).
- **Prefer exact paths** — use [artifact-layout.md](artifact-layout.md) as your map.
- **`list_artifacts` is recovery-only** — use it once on `artifacts/` when a guessed `<test-as>` path fails. Do **not** use it to crawl `gather-*`, `pods/`, or CAPI subdirectories level by level. If Evidence already names a file under gather artifacts, fetch that path directly.
- **CI config and source** — fetch from GitHub (`openshift/release` and component repos). Nothing is available from local clones.
- Prefer reading small logs and JSON directly rather than bulk-downloading the whole artifact tree.
- Top-level job files: `build-log.txt`, `finished.json`, `podinfo.json`, `prowjob.json`.

## Job revision and result (`finished.json`)

Fetch `<job-url>/finished.json` when you need the **commit or revision** the job ran against, plus overall pass/fail and timing:

```bash
curl -s "<job-url>/finished.json" | jq .
```

Key fields under `refs`:

| Field | Use |
|-------|-----|
| `refs.org`, `refs.repo` | Component repository tested |
| `refs.base_ref` | Branch (e.g. `master`, `release-4.22`) |
| `refs.base_sha` | Commit SHA on the branch — **periodic**, **postsubmit**, **branch-ci** |
| `refs.base_link` | GitHub link to `base_sha` |
| `refs.pulls[]` | Present on **presubmit** — PR number, head `sha`, `link` |

Useful extracts:

```bash
# Pass/fail
curl -s "<job-url>/finished.json" | jq -r '.status // .state'

# Branch commit (periodic / postsubmit / branch-ci)
curl -s "<job-url>/finished.json" | jq -r '"\(.refs.org)/\(.refs.repo)@\(.refs.base_ref) \(.refs.base_sha)"'

# PR head commit (presubmit)
curl -s "<job-url>/finished.json" | jq -r '.refs.pulls[0] | "\(.link) \(.sha)"'
```

Include the SHA (and PR link if presubmit) in the **Job** section of your report.

## Identify failed steps and extract scripts

Use `ci-operator-step-graph.json` to get the names of failed steps and extract the exact bash scripts without guessing GitHub paths.

**Extracting the bash script for a step:**

Once you know the failing step name (e.g. `assisted-common-setup-prepare`), extract its script from the `<test-as>-commands` ConfigMap in `ci-operator-step-graph.json`. Each `.data` key is a step name; the value is the bash script CI ran:

```bash
curl -s "<job-url>/artifacts/ci-operator-step-graph.json" | \
  jq -r '.[] | .manifests[]? | select(.kind == "ConfigMap" and (.metadata.name | endswith("-commands"))) | .data["<step-name>"] // empty'
```

**Example** (presubmit `e2e-metal-assisted-ha-kube-api-5-0`, step `assisted-common-setup-prepare`):

```bash
curl -s "https://gcs.ci.openshift.org/gcs/test-platform-results-public/pr-logs/pull/openshift_assisted-test-infra/2827/pull-ci-openshift-assisted-test-infra-backplane-5.0-e2e-metal-assisted-ha-kube-api-5-0/2103433697532317696/artifacts/ci-operator-step-graph.json" | \
  jq -r '.[] | .manifests[]? | select(.kind == "ConfigMap" and (.metadata.name | endswith("-commands"))) | .data["assisted-common-setup-prepare"] // empty'
```

Output starts with:

```bash
#!/bin/bash

set -o nounset
set -o errexit
set -o pipefail

echo "************ assisted common setup prepare command ************"
...
```

This prints the exact bash script executed by CI for that step. **Always use this method to read the step's code when analyzing a failing job**, instead of trying to find the `*-commands.sh` file in the GitHub `step-registry`.

**Example: list failed step names** (periodic assisted-test-infra job):

```bash
curl -s "https://gcsweb-ci.apps.ci.l2s4.p1.openshiftapps.com/gcs/test-platform-results/logs/periodic-ci-openshift-assisted-test-infra-master-e2e-metal-assisted-kube-api-late-binding-sno-4-22-periodic/2062738748046577664/artifacts/ci-operator-step-graph.json" | \
  jq -r '[.[] | select(.failed == true) | .substeps[]? | select(.failed == true) | .manifests[] | .metadata.labels."ci.openshift.io/metadata.step" // empty] | join(", ")'
```

Output:

```text
assisted-common-post-install
```

Then read `artifacts/e2e-metal-assisted-kube-api-late-binding-sno-4-22-periodic/assisted-common-post-install/build-log.txt`.

**Interpretation:**

- If the query returns step names, list them all in the report, then triage the **first failing non-gather step** in workflow order (see [investigation.md](investigation.md)). Open `artifacts/<test-as>/<step-name>/build-log.txt` for that step first.
- If gather steps appear in the failed list alongside earlier failures, skip analyzing those gather step failures; use their `artifacts/` only as evidence for earlier symptoms.
- If the first non-gather failure gives a **terminal** root cause, skip the rest of the failed steps.
- The `substeps` field is **not mandatory**. When a failed top-level entry has no `substeps`, the job most likely failed in the **prepare phase** (before multi-stage steps ran). In that case, state that no step names are available from the graph and triage `build-log.txt` at the job root instead.
- When reporting, always include the failed step list from this query (or explicitly note that step names are missing because the failure occurred in prepare).
