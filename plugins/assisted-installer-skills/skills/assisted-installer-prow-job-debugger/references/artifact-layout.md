# Artifact layout and coverage gaps

```text
<job-root>/
  build-log.txt          # overall job / ci-operator entry
  finished.json          # pass/fail, duration, git refs (base_sha / pulls[].sha)
  artifacts/
    ci-operator-step-graph.json   # step graph; use to list failed steps
    <test-as>/           # multi-stage test namespace artifacts
      <step-name>/
        build-log.txt    # step container log (always start here per step)
        artifacts/       # optional; step-specific dumps when present
      # --- gather / post steps below are optional; none are guaranteed ---
      assisted-baremetal-operator-gather/   # when assisted-service is deployed as an operator
        artifacts/       # operator + related CR/log dumps (see below)
      baremetalds-devscripts-gather/        # when metal3/dev-scripts is part of the deployment
        artifacts/       # sosreports, libvirt, proxy logs (see below)
      gather-extra/                         # OpenShift cluster resource dump
        artifacts/       # pods/, nodes/, events, JSON resource lists (see below)
      gather-must-gather/                   # basic must-gather
        artifacts/       # often must-gather.tar (+ HTML helpers)
      assisted-common-gather/               # assisted test-infra post-gather (if present)
        artifacts/       # remote cluster + assisted-service logs
```

**Important:** No gather directory is present on every job. Always start with
`artifacts/<test-as>/<step-name>/build-log.txt`, then open that step's
`artifacts/` (if any). Use gather trees only when they exist for the run.

Step logs: `artifacts/<test-as>/<step-name>/build-log.txt`.

## `assisted-baremetal-operator-gather/artifacts/`

Present when assisted-service is deployed as an operator. Holds operator
deployment state and related component dumps. Typical contents:

| Path / file | Contents |
| ------------- | ---------- |
| `assisted-service.log`, `assisted-image-service.log`, `infrastructure-operator.log` | Core assisted operator / service container logs |
| `assisted-service-operator-catalog.log`, `assisted-service-operator-subscription.log`, `oc_install_plan.log` | OLM install path (catalog, subscription, install plan) |
| `oc_get_pods.yaml`, `oc_get_deployments.yaml`, `oc_get_nodes.yaml`, `oc_get_replicasets.yaml` | Cluster object dumps at gather time |
| `oc_get_events.log`, `oc_get_all.log`, `oc_cluster_info.log` | Events and high-level cluster info |
| `capi/` | Cluster API / HyperShift CRs (`cluster/`, `agentcluster/`, `agentmachine/`, `hostedcluster/`, `nodepool/`, …) plus `hypershift.log` / pod YAML when CAPI is in play |
| `hive/` | Hive operator and controller logs (`hive-operator.log`, `hive-controller-manager.log`, events) |
| `hypershift/` | HyperShift-side assisted logs and `hub_cluster/` (may be empty if that path was unused) |
| `libvirt-qemu/`, `sos/` | Host/libvirt snippets (e.g. `virtual_hosts.json`) |
| `sosreport-*.tar.xz` | Host sosreports when collected |

Use this tree for operator install failures, OLM subscription problems, and
CAPI/Hive/HyperShift object state on operator-based jobs.

Also commonly present on operator gather (when the script dumped them):

| Path / file | Contents |
| ------------- | ---------- |
| `agents/*.yaml`, `baremetalhosts/*.yaml`, `infraenvs/*.yaml` | Assisted CR snapshots at gather time |
| `sos/virtual_hosts.json` | DHCP name → address map for VMs the gather attempted to reach |
| `sos/<host>/journal.log` (optional) | Guest journal **only if** gather’s in-job SSH + copy succeeded for that host |

**Caveats:** Guest sos/journal collection during the job is best-effort (gather
SSH/`scp`/`toolbox` often fail). Host names are discovered from libvirt DHCP leases with a
`master\|worker` grep — that **includes** names like `extraworker-*` by
substring, but success is not guaranteed. CR YAML under `capi/` may be
**empty placeholders** (`_.yaml`, size 0) if the test destroyed the hosted
cluster before gather — trust the test step `build-log.txt` for whether HCP
ever became Ready, not the empty gather files.

## `baremetalds-devscripts-gather/artifacts/`

Present when [dev-scripts](https://github.com/openshift-metal3/dev-scripts) is
used as part of the deployment (baremetalds / metal3 path). Typical contents:

| Path / file | Contents |
| ------------- | ---------- |
| `sosreport-*.tar.xz` (+ `.sha256`) | Host sosreports from the CI / provisioner hosts |
| `libvirt-logs.tar` (or `.tar.gz`) | Libvirt domain / qemu console and serial logs |
| `squid-logs-*.tar` | Proxy (squid) logs from the disconnected / mirrored path when a proxy was used |

Use this for provisioner-host, libvirt VM, and disconnected-proxy issues when
dev-scripts brought up the environment.

**Caveats:**

- `libvirt-logs.tar` holds `*serial0.log` / qemu logs for masters, workers, and
  `extraworker-*`. After the live ISO / agent phase, **installed ostree boots
  often leave serial silent after GRUB** — do not treat an empty post-GRUB
  serial as proof the guest never progressed; look for a guest journal under
  operator-gather `sos/<host>/` (when present) or infer progress from Agent/BMH
  and the test step log.
- The gather script builds a node IP list (masters, workers, extraworkers) but
  **exits early without in-job SSH journal collection when the hub install
  succeeded** (`installer-status.txt == 0`), expecting other gather steps to
  cover the API cluster. Extraworker / day-2 guests that never joined that API
  are easy to miss in GCS.

## `gather-extra/artifacts/`

OpenShift cluster resource dump (not assisted-specific). Rich source for
cluster-wide state after a failure. Typical layout:

| Path | Contents |
| ------ | ---------- |
| `pods/` | Per-container logs named `<ns>_<pod>_<container>.log` (and `*_previous.log` for restarted containers) — **primary place for all pod logs** |
| `nodes/<node-name>/` | Per-node host data: `journal`, `audit`, `heap`, `lsmod` |
| `events.json` | Cluster events |
| `pods.json`, `deployments.json`, `nodes.json`, `namespaces.json`, … | Full JSON listings of common resources |
| `clusteroperators.json`, `clusterversion.json`, `machines.json`, … | OpenShift operator / machine API state |
| `clusterserviceversions.json`, `subscriptions.json` | OLM state |
| `inspect/` | `oc adm inspect`-style tree (`namespaces/`, `cluster-scoped-resources/`) |
| `oc_cmds/` | Text dumps of common `oc get` outputs by resource kind |
| `junit/` | Symptom / analysis junit XML when generated |
| `audit_logs/`, `network/`, `metrics/`, `tcpdump/`, `conntrackdump/` | Optional deeper networking / audit captures |

Prefer `pods/` for application log triage and `nodes/*/journal` for node-level
systemd / kubelet failures. **Do not fetch journal logs for every single node** (e.g. master-0, master-1, master-2). Pick one node as a representative sample first. Fetching all node logs exhausts tool calls.

**Caveat:** `gather-extra` covers the **OpenShift API cluster the step could
reach** (usually the hub). It does **not** automatically include journals or
`/etc` from VMs that never became nodes (bootstrap, failed workers,
extraworkers / day-2 hosts still outside the cluster).

## `gather-must-gather/artifacts/`

Basic must-gather output. Often includes:

| Path / file | Contents |
| ------------- | ---------- |
| `must-gather.tar` | Packed must-gather; may contain per-host data including journal |
| `camgi.html`, `event-filter.html` | HTML helpers for browsing gather / events |
| `install-status.txt`, `junit_install.xml` | Install status summaries when present |

Extract `must-gather.tar` when gather-extra is missing or when you need the
standard must-gather host/journal layout.

## Assisted test-infra gather

When `assisted-common-gather` ran, nested `assisted-common-gather/artifacts/`
contains assisted-installer / test-infra cluster logs (sosreport, terraform,
`make download_*` output). See
`ci-operator/step-registry/assisted/common/gather/assisted-common-gather-commands.sh`.

## Artifact coverage gaps

Use this when the step log and gather CR dumps are inconclusive. These gaps
apply across assisted baremetalds / operator jobs, not one failure mode.
This environment is **post-run only** (job artifacts in GCS / GitHub source) —
do not assume interactive access to the CI host or guest VMs.

### Often present in GCS

- Per-step `build-log.txt` (including xtrace from deploy scripts)
- Provisioner sosreport + squid logs (disconnected)
- Libvirt qemu/serial logs for all domains
- Assisted CR YAML (Agent, BMH, InfraEnv, …) when operator-gather ran
- Hub pod logs / node journals via `gather-extra` when the hub API is up

### Often absent or misleading in GCS

| Need | Why it is missing / weak |
| ------ | --------------------------- |
| Guest `journalctl` after ostree install | Serial quiet after GRUB; gather’s in-job SSH journal collect is best-effort or skipped when hub install OK |
| Guest `/etc` (e.g. `registries.conf`, kubelet/CRI config) | Not a standard artifact; only inside a successful guest sos from gather |
| Extraworker / day-2 host that never became a node | Outside hub `gather-extra`; easy to miss if operator-gather’s in-job SSH failed |
| Live HCP / NodePool / Machine objects on green CAPI runs | Test may destroy the hosted cluster before gather → empty `capi/*.yaml` |
| Proof a VM “did nothing” from serial alone | Empty post-GRUB serial ≠ hung firmware; check Agent/BMH and any gathered guest journal |

When guest-local evidence is missing from GCS, say so explicitly and narrow
conclusions to what the step logs and gathered CRs support. Do not invent
guest-journal conclusions from serial GRUB screens alone.
