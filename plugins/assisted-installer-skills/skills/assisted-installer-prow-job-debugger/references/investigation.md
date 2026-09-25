# Investigation procedure details

## Multiple failing steps

When several steps are marked failed:

1. **Skip gather steps** as the failure under investigation. Names matching `*gather*` (e.g. `gather-extra`, `gather-must-gather`, `assisted-baremetal-operator-gather`, `baremetalds-devscripts-gather`, `assisted-common-gather`, `ofcir-gather`) often fail because the cluster was already broken or post steps always run after a test failure. Do **not** spend time explaining why the gather step itself failed. You may still **read** gather `artifacts/` when digging into a symptom from an earlier step.
2. **Start with the first failing step** in the multi-stage flow (`pre` → `test` → `post`), ignoring gather steps. That is usually the real break.
3. **Stop if that step yields a terminal cause** — do not walk every later failed step. Only move to the next non-gather failure if the first one's logs are inconclusive or only a symptom you cannot deepen further.

## Earlier steps that look successful (false positives)

If you cannot find a terminal root cause, or the apparent root cause seems to be a **symptom of an earlier failure**, check the **earlier steps** in the workflow (`pre` → `test`). They may be marked successful because of a **false positive** result (the step exited 0 even though the underlying setup was already broken or incomplete). Read those earlier steps' `build-log.txt` (and their `artifacts/` if present) for soft failures, ignored errors, or conditions that only surface in a later step.

## Dig until the root cause is terminal

A step log that says "installation failed", "nodes never became Ready", "pod not ready", or "operator deploy failed" is usually a **symptom**, not a root cause. Keep investigating **why** that component failed until further digging no longer changes the explanation.

### Keep digging (symptoms)

Treat these as prompts to open gather / component logs, not as conclusions:

| Symptom in step log | Continue into |
|---------------------|---------------|
| Masters / workers never came up, bootstrap incomplete, install timed out waiting for nodes | `gather-extra/artifacts/nodes/*/journal` (and audit); sosreports under operator/devscripts gather; machine / BareMetalHost status if present |
| A pod / deployment never became Ready | That pod's logs in `gather-extra/artifacts/pods/` (`<ns>_<pod>_<container>.log`); events; operator gather logs for the same component |
| Operator / CSV / subscription stuck | Operator gather (`assisted-baremetal-operator-gather`), OLM events, CSV/subscription JSON, related pod logs |
| Cluster operators degraded | `clusteroperators.json`, operator pod logs under `pods/`, node journals if the CO points at a node problem |

Ask "why did *this* fail?" one more layer: if nodes are down → read journals; if a container crash-loops → read its logs and previous logs; if an operator is Degraded → read that operator's pod logs and events. Repeat until the answer is terminal or artifacts are exhausted.

### Stop here (terminal causes)

Stop when the evidence already names a concrete, actionable failure mechanism — further logs would only restate the same fact. Examples:

- Image pull / registry **authentication** or **authorization** required (pull denied, 401/403, missing pull secret)
- Explicit misconfiguration with a clear error (bad URL, missing required env, wrong namespace)
- Quota / capacity / ofcir acquire failure with a definitive error
- A single decisive fatal in the deployment script that fully explains the outcome (e.g. registry auth blocked the image pull the script needed)
- **Static checks/linters** (`verify-deps`, `verify-generated-code`, `lint`): The failure is simply that generated code or dependencies are out of sync. Do not trace Makefiles or generation scripts; just conclude that the PR author needs to run the generation tool locally (e.g., `make generate` or `go mod tidy`) and commit the results.

**Do not** conclude with only "2 of 3 masters never came up" or "pod X was not Ready" — those need the deeper layer above. **Do** conclude with "masters never came up **because** journal shows …" or "operator deploy failed **because** the image registry required authentication and the pull failed".

If gather artifacts are missing or journals are empty, say what you could not check and stop — do not invent a deeper cause.

If digging the failing step still yields only a symptom (or no terminal cause), also check **earlier successful steps** for false positives.

## Triage checklist

Copy and track:

```text
- [ ] Parse URL → prow job name, repo, branch, test-as
- [ ] Use provided `failing_steps` from the run prompt (do not rediscover via step-graph listing unless the list is missing or inconsistent)
- [ ] List `artifacts/<test-as>/` — RED ALERT if applicable (ofcir-only / job still running)
- [ ] If multiple failures: skip gather steps; start with the **first failing non-gather** step; stop later steps once a terminal cause is found
- [ ] Read that step's `artifacts/<test-as>/<step>/build-log.txt` (and that step's `artifacts/` if present)
- [ ] Dig past symptoms (nodes/pods/operators not ready) into journals, pod logs, events — see Dig until the root cause is terminal (use gather `artifacts/` as evidence, do not triage why gather itself failed)
- [ ] If no terminal cause (or only a symptom of an earlier failure): check earlier steps that look successful — they may be false positives
- [ ] Map step → *-commands.sh in step-registry
- [ ] Read test definition env/workflow in ci-operator config
- [ ] Trace step scripts and component code on GitHub at the job commit SHA
- [ ] If the failing host never joined the API: check libvirt-logs + whether guest journal exists under operator-gather `sos/`; if not, say GCS may be insufficient (see Artifact coverage gaps)
```

### RED ALERT — stop deep triage

Under `artifacts/<test-as>/`, if the **only** step directories are `ipi-install-rbac` and names matching `*ofcir*` (e.g. `ofcir-acquire`, `assisted-ofcir-setup`):

- The job likely **never acquired a test cluster** (ofcir/packet path), **or the job is still running** (incomplete post/test steps).
- Do not treat missing assisted-service or install logs as a product bug yet.
- Check `finished.json` and whether `build-log.txt` shows the job still active; suggest re-checking artifacts later or inspecting ofcir-acquire / setup step logs only.
