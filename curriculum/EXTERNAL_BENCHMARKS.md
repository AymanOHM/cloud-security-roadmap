# External benchmarks

## roadmap.sh (inputs)
The DevSecOps and Cyber Security maps (PDFs in `private/sources/`) stood in for the NTI and DEBI roadmaps. See
`NTI.md` and `DEBI.md`. roadmap.sh content is © roadmap.sh; don't republish the PDFs.

## devopsroadmap.io — Dynamic DevOps Roadmap (compared 23 Nov 2026)
Free, open-source DevOps learning path (DevOps Hive, CC BY-SA 4.0): Getting Started → Foundations (Modules 1–7)
→ more hands-on projects → interview preparation → career growth. One project, HiveBox, is built across
Modules 1–6; Module 7 is a self-driven capstone done with someone more experienced. Security is limited to
software supply chain in Module 6; cloud is an overview in Module 4, then Terraform, Kubernetes, Helm/Kustomize,
GitOps with Argo CD.

**Verdict:** a useful checklist for the project stages, not a third curriculum. Its sequence duplicates NTI;
this roadmap is stronger on security and AWS and on evidence gates.

**Adopted in data v1.1:**
| Item | Where |
|---|---|
| Integration testing | TST-2, PS-2 |
| Release automation (SemVer, Conventional Commits, changelog) | CI-5, PS-2 |
| Multi-environment promotion (dev → prod, config-only differences) | CI-6, PS-4 |
| Helm/Kustomize + GitOps (Argo CD), optional | K8S-3, PS-6 |
| Twelve-Factor config review | PS-3 step |
| Review by someone more experienced | PS-7 step |
| Skills radar | App dashboard |

Sources: https://devopsroadmap.io/ · https://dynamic-devops-roadmap-io.pages.dev/foundations/module-07
