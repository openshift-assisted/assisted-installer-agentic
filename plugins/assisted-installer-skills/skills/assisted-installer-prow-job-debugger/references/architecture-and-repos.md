# Architecture and GitHub repositories

## External documentation

| Topic | URL |
| ------- | ----- |
| CI Operator | [docs.ci.openshift.org/architecture/ci-operator](https://docs.ci.openshift.org/architecture/ci-operator/) |
| Multi-stage / step registry | [docs.ci.openshift.org/architecture/step-registry](https://docs.ci.openshift.org/architecture/step-registry/) |
| OpenShift CI docs (home) | [docs.ci.openshift.org](https://docs.ci.openshift.org/) |
| Release / CI config repo | [openshift/release](https://github.com/openshift/release) |
| Assisted test infra | [openshift/assisted-test-infra](https://github.com/openshift/assisted-test-infra) |
| Assisted service | [openshift/assisted-service](https://github.com/openshift/assisted-service) |
| Assisted installer | [openshift/assisted-installer](https://github.com/openshift/assisted-installer) |
| Metal3 dev scripts | [openshift-metal3/dev-scripts](https://github.com/openshift-metal3/dev-scripts) |
| HyperShift | [openshift/hypershift](https://github.com/openshift/hypershift) |
| Step registry browser | [steps.ci.openshift.org](https://steps.ci.openshift.org/) |

## Architecture

1. **openshift/release** — `ci-operator/config/openshift/<repo>/` defines tests (`tests[].as`), workflows, env; `ci-operator/step-registry/` holds step scripts; `ci-operator/jobs/` is generated (read-only for lookup).
2. **Prow** — Schedules the job; artifacts land in GCS (`test-platform-results` bucket).
3. **ci-operator** — Runs multi-stage tests: `pre` → `test` → `post` steps as containers; each step logs to `${ARTIFACT_DIR}`.
4. **Component repos** (e.g. assisted-test-infra) — Implementation invoked by step `*-commands.sh` scripts, not duplicated in release.

## Source code on GitHub

Resolve branch in this order:

1. **Branch from `job_name`** — for `openshift/release` and the component repo under test (e.g. `release-ocm-2.16`, `master`).
2. **Default branch from the table below** — for dependency repos (metal3, hypershift, …) or when the job branch is unclear.
3. **Never alternate `main` and `master`** for the same repo in one investigation — pick the table value or job branch and stick with it.

**URL template:** `https://raw.githubusercontent.com/<org>/<repo>/<branch>/<path>`

### Common GitHub repositories

Start from this table when mapping a prow job or step script to source. Do **not** probe random org/repo combinations — derive unknown paths from step-registry `*-commands.sh` `source()` lines first.

| GitHub repo | Default branch | Branch for CI jobs | Role / job name hint |
| ------------- | ---------------- | -------------------- | ---------------------- |
| `openshift/release` | `master` | **`job_name` branch** (e.g. `release-ocm-2.16`) | ci-operator config, step-registry |
| `openshift/assisted-service` | `master` | **`job_name` branch** | `assisted-service-...`, operator deploy scripts |
| `openshift/assisted-test-infra` | `master` | **`job_name` branch** | `assisted-test-infra-...`, bare-metal e2e |
| `openshift/assisted-installer` | `master` | **`job_name` branch** | `assisted-installer-...` |
| `openshift/assisted-image-service` | `master` | **`job_name` branch** | `assisted-image-service-...` |
| `openshift-metal3/dev-scripts` | `main` | `main` | Step `source()` only — **not** `openshift/dev-scripts` |
| `openshift/hypershift` | `main` | `main` | HyperShift / CAPI / ZTP operator tests |
| `openshift-assisted/cluster-api-provider-openshift-assisted` | `main` | `main` (or tag from step env) | CAPI provider agent workflows |
| `rh-ecosystem-edge/assisted-chat` | `main` | `main` | MCP / chat eval (`assisted-service-mcp`) |

**Examples:**

- Job `periodic-ci-openshift-assisted-service-release-ocm-2.16-...` → `openshift/release` and `openshift/assisted-service` on branch **`release-ocm-2.16`** (not `master`).
- Job `periodic-ci-openshift-assisted-test-infra-master-...` → component repos on **`master`** (not `main`).
- `deploy_capi_cluster.sh` sources metal3 scripts → `openshift-metal3/dev-scripts` on **`main`** only.

### Wrong guesses (avoid)

| Do not use | Use instead |
| ------------ | ------------- |
| `openshift/dev-scripts` | `openshift-metal3/dev-scripts` |
| `master` on `openshift/release` when `job_name` contains `release-ocm-2.16` | `release-ocm-2.16` |
| `main` on `openshift/assisted-service` when `job_name` contains `master` | `master` |
| `master` on `openshift-metal3/dev-scripts` or `openshift/hypershift` | `main` |
| Trying both `main` and `master` for the same repo | Default branch or `job_name` branch from table |
| Random `openshift/<name>` without a table entry or `source()` reference | Fetch step-registry `*-commands.sh` first |
