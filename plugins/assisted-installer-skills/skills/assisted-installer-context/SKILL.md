---
name: assisted-installer-context
description: Use when triaging, debugging, developing, or reviewing Assisted Installer to identify relevant repositories, components, and deployment context.
---

# Assisted Installer context

Use this background to locate code and interpret the active task. Preserve that
task's output and authorization requirements; no separate report is needed.
Consult linked sources only when further detail is needed.

## Product goal

[Assisted Installer](https://github.com/openshift/assisted-service#about) simplifies
installing OpenShift on user-provided infrastructure, especially bare metal, through
host discovery, pre-installation validation, and guided configuration. It supports
single-node and highly available clusters with minimal infrastructure prerequisites.

## Deployment models

- **SaaS / Cloud:** Red Hat hosts the service at
  [console.redhat.com](https://console.redhat.com/openshift/assisted-installer/clusters)
  with UI and REST API access; the installed cluster runs on the user's infrastructure.
- **On-premises:** The [Infrastructure Operator](https://github.com/openshift/assisted-service/blob/master/docs/operator.md)
  runs on the customer's hub cluster through multicluster engine for Kubernetes
  (MCE), also included in Red Hat Advanced Cluster Management (ACM). Central
  Infrastructure Management (CIM) exposes console and Kubernetes resource interfaces.
  See the [CIM overview](https://github.com/stolostron/rhacm-docs/blob/2.17_stage/clusters/assisted_installer/ai_overview.adoc).

## Architecture and main codebases

In both models, hosts boot a discovery image; agents report inventory and
connectivity to the service, which validates configuration and coordinates
installation. Host-side components execute the work and report progress.
See the [installation flow](https://github.com/openshift/assisted-service#about).

| Codebase | Responsibility |
| --- | --- |
| [openshift/assisted-service](https://github.com/openshift/assisted-service) | Backend APIs, validation, installation orchestration, Kubernetes controllers, and Infrastructure Operator implementation. |
| [openshift/assisted-installer-agent](https://github.com/openshift/assisted-installer-agent) | Host discovery, inventory, connectivity checks, and execution of service-directed steps. |
| [openshift/assisted-installer](https://github.com/openshift/assisted-installer) | Host installation and cluster bootstrap/completion logic; this repository is one component of the product. |
| [openshift/assisted-image-service](https://github.com/openshift/assisted-image-service) | Customizes and serves CoreOS discovery images and boot artifacts. |
| [openshift-assisted/assisted-installer-ui](https://github.com/openshift-assisted/assisted-installer-ui) | User interface and shared UI components; start here for UI bugs, following evidence into backend code when needed. |
| [openshift/assisted-test-infra](https://github.com/openshift/assisted-test-infra) | Integration and end-to-end test infrastructure. |
