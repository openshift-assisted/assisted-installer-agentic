# Assisted-service operator CI map

Operator-style assisted jobs (`*e2e-ai-operator*`, ZTP, CAPI, …) run
step-registry wrappers, but **most deploy logic lives in
`openshift/assisted-service`** under `deploy/operator/`. There are no local
clones here — download the repo tarball at the job’s commit/branch (see
[architecture-and-repos.md](architecture-and-repos.md)) before reading these paths.

## Key paths (assisted-service)

| Path | Role |
|------|------|
| `deploy/operator/deploy.sh` | Top-level disconnected/connected hub setup entry |
| `deploy/operator/setup_assisted_operator.sh` | Operator install, mirror ConfigMaps, registries for the hub |
| `deploy/operator/mirror_utils.sh` | `ocp_mirror_release`, catalog/image mirror helpers, registry helpers |
| `deploy/operator/utils.sh` | Shared wait helpers, image ref parsing (`get_image_repository_only`, …) |
| `deploy/operator/ztp/` | ZTP spoke flow (`deploy_spoke_cluster.sh`, CR templates) |
| `deploy/operator/capi/` | HyperShift/CAPI hosted-cluster flow (`deploy_capi_cluster.sh`) |
| `deploy/operator/common.sh` | Shared env defaults sourced by the above |

Step-registry `*-commands.sh` usually `scp`/untar the assisted-service tree onto
the packet/ofcir host and invoke these scripts with env from the ci-operator
test (`DISCONNECTED`, `IP_STACK`, `SPOKE_*`, …). Prefer the script from
`ci-operator-step-graph.json` when analyzing a failing job, then open the
matching `deploy/operator/...` files from the assisted-service tarball.

## Typical multi-stage phases (operator baremetalds)

Order varies by workflow; names are approximate:

1. **ofcir / packet** — acquire host (`ofcir-acquire`, `assisted-ofcir-setup`)
2. **devscripts setup** — hub OCP via metal3/dev-scripts (`baremetalds-devscripts-setup`)
3. **operator setup** — mirror (if disconnected) + deploy assisted operator (`assisted-baremetal-operator-setup`)
4. **test** — ZTP spoke, CAPI hosted cluster, etc. (`assisted-baremetal-operator-ztp`, `…-capi`, …)
5. **gather / ofcir-release** — post steps; gather always best-effort

When several steps fail, the **first non-gather** failure still wins (use the
provided `failing_steps` list). A failure in operator-setup means the test
step’s product path never ran — do not debug spoke/CAPI behavior from that run.

## Hub vs spoke vs day-2 guest

| Layer | What it is | Where logs usually are |
|-------|------------|------------------------|
| Provisioner / “packet” host | ofcir machine running libvirt + scripts | Step `build-log.txt`; `sosreport-*` in baremetalds or operator gather |
| Hub cluster | OCP from dev-scripts; assisted operator runs here | `gather-extra`, operator logs, hub journals if gather-extra has nodes |
| Spoke / hosted | Cluster created by ZTP or HyperShift CAPI | Test step log; assisted CRs; sometimes `capi/` / hive dumps |
| Bootstrap / worker / extraworker VMs | libvirt domains; may never join an API | `libvirt-logs.tar`; optional `sos/<host>/`; often **missing** guest journal in GCS |

Agent CR messages (validation IDs, progress stages) describe **assisted’s view**
of the host. They can lag or summarize a deeper node-local failure (ignition
fetch, firstboot pull, kubelet, disk). When CR state and empty serial logs
conflict, look for a gathered guest journal — or state that artifacts lack it.
