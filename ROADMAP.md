<!-- Master copy of the written roadmap since 23 Nov 2026 (exported from an earlier draft document, which is now a historical copy). The competency, project and comparison tables are generated from data/*.json by tools/docgen.py. -->

# NTI + DEBI Unified Roadmap — Cloud Security track

Nov 23, 2026

## Bottom line

Doc 19 (G8) sets the entry role: junior DevOps/cloud engineer or Python backend. My first draft's **DevSecOps engineer on AWS as the first job is too early**: DevSecOps titles in Egyptian postings ask for 3–6 years (doc 19 §H). Specialize toward DevSecOps, with cloud security engineer as the destination after 1–2 years.

- **Use NTI for building, DEBI for security fundamentals.** NTI's 420 h are a DevOps curriculum (doc 19 §C). DEBI supplies the security core NTI lacks. AWS security services (CloudTrail, GuardDuty, Config, SCPs) are in neither, so they're the independent part of the plan, built in project PS-7.
- **107 competencies, one ID scheme.** IDs reuse doc 06 (NET, LNX, CTR, CI, CLD and so on), so the records keep working. New IDs cover the cloud-security part. The interactive HTML companion (Phase 8) uses the same IDs and order.
- **Projects follow doc 19 §G.** PS-1 to PS-5 harden, pipeline, deploy, Terraform and monitor the graduation project. PS-7 adds the cloud-security baseline and detection after NTI.
- **Certs:** SAA-C03 now (decided). SCS-C03 after PS-7, about Q4 2027. NSE 4 only if DEBI funds the exam (G15 amended), and Security+ stays deferred (G14).
- **Remaining uncertainty:** DEBI's assigned course list. Every DEBI course reference is marked unverified until it's published.

## Source check

The two PDFs are one-page roadmap.sh exports (DevSecOps for NTI, Cyber Security for DEBI), not course documents. The Study Plan Project fills most of the gap for NTI, but not for DEBI.

| Fact | Status | Source |
| --- | --- | --- |
| Topics on each map | Verified | The two PDFs |
| NTI module hours: Linux + Bash 35, Git 7, Python 22, Docker 21, Kubernetes 49, AWS 49, Terraform 21, Ansible 14, CI/CD + practice project 28, Agile & DevSecOps 14, Monitoring 7, OpenStack 21 | Verified | Doc 19 §C |
| NTI Linux material quality: 5.5/10, supplemented by the doc 20 guide | Verified | Doc 20 |
| NTI: 17 Oct 2026 to mid-Feb 2027, Sat–Wed 9:00–16:00; discounted AWS and Kubernetes vouchers | Verified | Study Plan doc 17 §1 |
| Which CI/CD tool NTI uses; whether NTI allows your own app for the capstone | **Unknown** | Asked in doc 19 §G |
| DEBI: about 1 year, from 21 Nov 2026 (study from 27 Nov), ends with a project; Fri+Sat every other weekend; 3 h/day expected; assigned courses first; AWS courses don't count | Verified | Doc 19 G2–G10 |
| DEBI's assigned courses (likely the Google Cybersecurity Certificate, Fortinet, CCNA material) | **Unverified** | Past DEBI students (doc 19 §C) |

Every "Google course N" reference below is a likely DEBI assignment, not a confirmed one.

## Phase 1 — Each roadmap on its own

NTI's map is a builder's security map that runs straight to senior topics. DEBI's map is a SOC and blue-team generalist foundation that only touches cloud at concept level.

|  | NTI (DevSecOps map) | DEBI (Cyber Security map) |
| --- | --- | --- |
| Objective | Put security controls into the software and infrastructure lifecycle | A broad security generalist: IT fundamentals, defense, operations, some offense |
| Subjects | Languages, Bash/PowerShell; CIA, authn/authz, OWASP Top 10, encryption; firewalls, VLANs, ACLs, segmentation, DNS/HTTP/TLS; secure coding (SQLi, XSS, input validation); SIEM and log analysis; Burp, Nmap, Wireshark; STRIDE, PASTA, attack-surface mapping; IAM, least privilege, RBAC; SOAR, automated patching; Nessus, OpenVAS, Qualys; CSPM, KMS; Docker, Kubernetes, image scanning; defense in depth, zero trust, secure API design, multi-region, IDS/IPS, DDoS, zoning; hashing, PKI, cert lifecycle; IR lifecycle, forensics, EDR; SBOMs, pipeline hardening, dependency risk; SOC 2, ISO 27001, NIST | Hardware, OS (Windows, Linux, macOS), office suites; OSI, subnetting, CIDR, protocols and ports, topologies, NAS/SAN; virtualization; CLI network tools; Kerberos, LDAP, RADIUS, SSO; zero trust, kill chain, ATT&CK, Diamond Model; IR process; hardening, IDS/IPS, EDR, DLP; SIEM, SOAR, event logs, syslog, netflow, pcaps; secure protocols, wireless security; attack catalogue (phishing to pass-the-hash); forensics tools; ISO, NIST, CIS, CSF, RMF; cloud concepts (models, IaaS/PaaS/SaaS, IaC, serverless, AWS/GCP/Azure); Python, Go, JS, C++, Bash, PowerShell; certs list; CTF platforms |
| Assumed prerequisites | DevOps core (Linux, Git, CI/CD, IaC). The map points to the DevOps roadmap for these | None: it starts at computer hardware |
| Labs and assessments | Not in the material | Not in the material. CTF platforms are named: TryHackMe, HackTheBox, VulnHub, picoCTF |
| Certs named | None | Beginner: A+, Linux+, Network+, CCNA, Security+. Advanced: CEH, CISA, CISM, GSEC, GPEN, GWAPT, OSCP, CREST, CISSP |
| Depth (my read of the layout) | Top half is junior level. Bottom half (multi-region security, large-scale identity, PKI failover, risk quantification) is senior or architect level | Wide and shallow. Networking and the attack catalogue are the deepest branches; cloud is one box of "understand the concept" |
| Below your level (skip) | Learn a programming language | Hardware, office suites, iCloud/Google Suite, programming branch |

**Cloud-security gaps in both maps:**

- No named AWS service: CloudTrail, GuardDuty, Security Hub, Config, Organizations/SCPs, VPC design, WAF.
- No Terraform and no policy-as-code (Checkov, OPA).
- No specific CI/CD tool, and no SAST/DAST/SCA/secrets-scanning tools by name.
- Secrets management only as "KMS".
- Kubernetes security beyond a single node on the map.
- No cloud detection engineering, and no cloud incident response such as leaked-key playbooks.
- Git appears in neither.

## Phase 2 — Overlap and gap matrix

NTI is a full DevOps curriculum (420 h) with thin security. DEBI supplies the security fundamentals NTI lacks. Neither teaches AWS security services, so that part is independent work. Of 22 areas: 6 duplicate, 7 complementary, 7 NTI-exclusive, 1 DEBI-exclusive, 1 missing from both.

NTI hours are from doc 19 §C. DEBI entries marked "unverified" depend on the assigned course list, which hasn't been published.

| Area | NTI | DEBI | Class | Lead | What to do |
| --- | --- | --- | --- | --- | --- |
| Linux and OS | Linux + Bash 35 h (doc 19); map: Bash only | OS basics, permissions, hardening; Google course 4 (unverified) | Complementary | NTI | NTI for admin; DEBI only for hardening; skim DEBI's Linux course |
| Networking | Prerequisite (CCNA level), not taught; map: firewalls, VLANs, ACLs, DNS/HTTP/TLS | OSI, subnetting, NAT, ports, tools; Google course 3 (unverified) | Complementary (DEBI fills NTI's gap) | DEBI | DEBI content + Jeremy's IT Lab days; VPC side via SAA |
| Programming | Python 22 h | Python automation course (unverified) | Duplicate | Neither | Revision only; you already know Python |
| Git and CI/CD | Git 7 h; CI/CD + practice project 28 h | Absent | NTI exclusive | NTI | GitHub Actions in PS-2 |
| Docker | 21 h; map: image scanning | Virtualization only | NTI exclusive | NTI | Hardening + Trivy in PS-1 |
| Kubernetes | 49 h | Absent | NTI exclusive | NTI | PS-6 only if postings ask |
| Cloud fundamentals | AWS 49 h | Concept box only | Complementary (thin on DEBI) | NTI | NTI block + SAA prep |
| AWS services | AWS 49 h | Named as an environment; AWS courses don't count (G10) | NTI exclusive | NTI | SAA-C03; PS-3 |
| IaC | Terraform 21 h, Ansible 14 h | 'Understand IaC' only | NTI exclusive | NTI | PS-4 |
| IAM and identity | Map: IAM, least privilege, RBAC | Kerberos, LDAP, RADIUS, SSO, MFA | Complementary | DEBI theory → independent AWS depth | CSEC-1 in PS-7 |
| Network security | Map: firewalls, IDS/IPS, DDoS, zoning | Hardening, NIDS/NIPS, secure protocols, Fortinet (likely) | Duplicate | DEBI | Cloud version in CSEC-6 |
| Monitoring and logging | Monitoring 7 h (ops metrics) | Security logs, SIEM; Google course 6 (unverified) | Complementary | NTI ops / DEBI security | PS-5 then PS-7 |
| Vulnerability management | Map: Nessus, OpenVAS, Qualys, patching | Basics, Nmap | Complementary | NTI | VM-1 on your own VM |
| SecOps and IR | Map: IR lifecycle, forensics, EDR, SOAR | IR process, threat hunting, ATT&CK | Duplicate | DEBI | IR-1 runbook + tabletop |
| Application security | Map: OWASP, secure coding, Burp | Web attacks, OWASP | Duplicate (builder vs attacker) | NTI | APPSEC-1 on the grad project |
| DevSecOps practices | Agile & DevSecOps 14 h; map: SBOMs, supply chain | TryHackMe DevSecOps path (access, not assigned) | NTI exclusive | NTI | DSO-1, DSO-2 |
| Threat modeling | Map: STRIDE, PASTA | Kill chain, Diamond, ATT&CK | Complementary | NTI | TM-1 per README |
| Crypto and PKI | Map: hashing, PKI design, cert lifecycle | Hashing, salting, key exchange, PKI | Duplicate | DEBI basics | Applied in CSEC-5 |
| Governance | Map: SOC 2, ISO 27001, NIST | ISO, NIST, CIS, CSF, RMF | Duplicate | Either | Reference only; CIS mapping in PS-7 |
| Offensive security | Absent | Large branch; CTF platforms | DEBI exclusive | DEBI | Assigned rooms only; CSEC-9 for cloud attacks |
| OpenStack | 21 h | Absent | NTI exclusive | NTI | Attend; low value for you (doc 19) |
| Cloud security services (CloudTrail, GuardDuty, Config, Security Hub, SCPs) | Map: CSPM, KMS (names only) | Absent | Missing | Independent | PS-7 |

Overlap only costs you time twice in networking, Python, Linux, security operations and AppSec. In each, one program leads and the other's version is revision at most.

## Phase 3 — Career direction

**Recommendation: keep doc 19's plan.** Enter as a junior DevOps/cloud engineer (or Python backend), specialize as DevSecOps, and treat cloud security engineer as the destination after 1–2 years. I didn't keep cloud security just because you suggested it: it has almost no junior titles in Egypt. The access estimates below come from doc 19's posting check (14 Nov 2026), which is a sample, not a market count.

| Direction | Fit: NTI | Fit: DEBI | Fit: your backend | Entry-level access | Long-term path | Extra learning outside both programs |
| --- | --- | --- | --- | --- | --- | --- |
| **DevSecOps engineer** | Strong: it is the track | Medium: security theory | Strong: pipelines, code scanning, Django deploys | Medium. Often hired as junior DevOps with security duties | Senior DevSecOps, platform security, cloud security | Terraform, CI/CD tools, AWS depth |
| Cloud security engineer | Medium: cloud security boxes | Weak-medium: concepts only | Medium: automation and IaC | **Low.** Usually wants 2–3 years of cloud, ops or security work first | Cloud security architect | All of AWS security services, IAM depth, detection, IR |
| Cloud SecOps / detection engineer | Weak-medium: SIEM, IR | Strong: SOC, logs, IR | Medium: writing detections as code | Medium. SOC analyst roles are the usual door, and they're shift-based alert triage | Detection engineering, IR lead | CloudTrail/GuardDuty detection, query languages |
| Application security engineer | Medium: secure coding, OWASP | Medium: web attacks | **Strongest**: you've built Django APIs | Low-medium. Usually wants code-review or pentest experience | Product security | Code review practice, Burp depth, threat modeling at scale |
| Cloud infrastructure engineer | Strong: AWS, containers, IaC | Weak | Strong | **Highest** of the five | Platform or SRE; security is an optional later turn | Terraform, Kubernetes, networking depth |

**Why DevSecOps first:**

- It's the only direction both programs feed directly.
- It uses your backend history as an asset, not a sunk cost.
- Its daily work (IAM, IaC guardrails, pipeline controls, secure deploys) is the same skill set a cloud security engineer gets hired on. The move from one to the other is a title change on top of experience you'd already have.

**Strongest case against it:**

- In many Egyptian companies, "DevSecOps" is a DevOps job with a scanner bolted on. You could spend 2 years on pipelines and deploys with little real security work.
- If you'd rather guarantee security work from day one, **cloud SecOps via a SOC role** is the alternative. DEBI fits it better and SOC openings are more common, but the work is shift-based alert triage and it uses your backend skills least.
- **Cloud infrastructure engineer** is the safest door if getting hired fast matters most. The risk is drifting away from security.

The roadmap below keeps both of those open. The core stages are the same for all three, and only Stage 4 differs.

## Phase 4 — Unified roadmap

There are five stages, each closed by a gate that needs evidence. Finishing a course doesn't pass a gate. **Every competency has an ID.** The IDs reuse the Study Plan's doc 06 scheme (NET, LNX, PY, DB, WEB, GIT, TST, CI, CTR, SEC, APPSEC, WIN, CLD, OPS, COMM, DSA), so your records (doc 15) track the same rows. New IDs cover the cloud-security part: IAC, K8S, DSO, VM, NSEC, LOG, IR, TM, CSEC, JOB. The HTML dashboard uses exactly these IDs, in this order.

The split, counted by competencies: core (Stages 1–3) about 84%, specialization (Stage 4) about 9%, job readiness and revision about 7%. Core is above your 60–70% target because NTI's 420 h *is* the core while it runs. Doc 19 §F already replaced the old split for that reason.

Source legend: **NTI** leads · **DEBI** leads · **Independent** · **Shared** (both cover it; the Lead column in Phase 2 decides) · **Existing** (you already have it; claim it with evidence instead of re-studying). "Refresh" in the Competency column means partly existing, per doc 19 and the records.

### Stage 1 — Foundation

Now to Dec 2026 (NTI Linux block; DEBI start). **Gate 1: doc 06 F1 exit checks for NET and LNX pass unaided (URL walkthrough, 5 subnets in ~10 min, 3 broken-connectivity labs, fresh-VM Linux check).**

| ID | Competency | Source | Prerequisites | Learning objectives | Practical work | Evidence | Priority |
| --- | --- | --- | --- | --- | --- | --- | --- |
| NET-1 | OSI / TCP-IP layers and encapsulation (refresh) | DEBI | — | Place any protocol or device on the right layer; Explain encapsulation end to end | TryHackMe networking rooms through DEBI | Explain the layers for 2–3 min in English (COMM-1 style). | High |
| NET-2 | IPv4 addressing and subnetting | DEBI | NET-1 | Subnet quickly and correctly; Read CIDR blocks in AWS without a calculator | Packet Tracer labs | 5 networks subnetted in about 10 min (doc 06 F1 exit check). | High |
| NET-3 | Switching, routing, ARP and NAT | DEBI | NET-1 | Trace a packet across a LAN and through NAT; Read a routing table | Packet Tracer routing + NAT lab | Explain the private-subnet → NAT → internet path and back without notes. | High |
| NET-4 | DHCP and DNS (refresh) | DEBI | NET-1 | Explain DORA; Resolve a name by hand with dig +trace | dig +trace against a real domain | Walk through DHCP and DNS resolution for a URL cold; resolve a real domain with `dig +trace` and explain each hop. | Medium |
| NET-5 | TCP/UDP, HTTP and TLS (refresh) | Shared | NET-1 | Walk through 'what happens when I type a URL' in 5–8 min | curl -v against your own app | Scoped URL walkthrough (doc 06) in English. | High |
| NET-6 | Network tools | Shared | NET-3, NET-4 | Capture and filter traffic; Find which port a service listens on | Capture your app's TLS handshake | Annotated pcap of one request. | Medium |
| NET-7 | Layered connectivity troubleshooting | DEBI | NET-6, LNX-7 | Diagnose a broken connection and name the failing layer | 3 break-and-fix scenarios on your Linux VM | 3 broken-connectivity labs fixed, failing layer stated (doc 06 exit check). | High |
| LNX-1 | Filesystem, pipes, grep/find (refresh) | NTI | — | Search logs recursively and filter them | Bandit levels on bad days | Fresh-VM exit check: find and filter errors across `/var/log` recursively (`grep -ri`, `find`) without lookup. | High |
| LNX-2 | Users, groups and permissions (refresh) | NTI | LNX-1 | Set up users and groups with correct permissions | Doc 20 labs | Fresh-VM exit check, users/groups part. | High |
| LNX-3 | Processes and systemd services | NTI | LNX-1 | Write a unit for the grad project | Run the grad project under systemd | Broken unit fixed from logs (exit check). | High |
| LNX-4 | Packages, environment and PATH | NTI | LNX-1 | Install, pin and remove packages | Doc 20 labs | Exit check passes without lookup. | Medium |
| LNX-5 | Diagnose a failing service from logs | NTI | LNX-3 | Find why a service fails in minutes | Doc 20 incident scripts | Fix an injected service failure unaided using `systemctl status` and `journalctl -u`. | High |
| LNX-6 | SSH hardening | NTI | LNX-2 | Key-only SSH on a fresh VM | Harden your UTM VM | Key-only SSH set up in the exit check. | High |
| LNX-7 | Linux networking and firewall (refresh) | NTI | LNX-1, NET-3 | Open and close ports deliberately | ufw on your VM | Exit check: open, verify (`ss`) and close a port with `ufw` on a fresh VM without lookup. | Medium |
| LNX-8 | Bash scripting | NTI | LNX-1 | Write a 20-line shellcheck-clean script | Automate a backup of the grad project DB | Script passes shellcheck and runs from cron. | High |
| PY-1 | Python data model (have) | Existing | — | Explain mutability, references and copies with a REPL demo | — | Explain mutability, copies and `==` vs `is` cold, with a REPL demo. | Low |
| PY-2 | Built-in structures and their complexity (have) | Existing | — | Pick the right structure for a problem and state its complexity | — | State the complexity of list, dict and set operations and pick a structure for a given problem, cold. | Low |
| PY-3 | Iterators, generators, decorators, context managers (have) | Existing | — | Write a generator, a decorator and a context manager from memory | Log-parser CLI (doc 06 PY exit check) | The log-parser CLI uses a generator pipeline, a decorator and a context manager, and each choice is explained (doc 06). | Low |
| PY-4 | OOP in Python (have) | Existing | — | Choose inheritance or composition and justify it in your own code | — | Explain inheritance vs composition with your own code; write a dataclass with a custom dunder method. | Low |
| PY-5 | Exceptions and logging (have) | Existing | — | Handle and log errors deliberately | — | The log-parser CLI handles bad input with specific exceptions and logs through the `logging` module. | Low |
| PY-6 | Python concurrency model (have) | Existing | — | Explain the GIL and choose a concurrency model for a workload | — | Explain the GIL cold and justify threads, processes or asyncio for three given workloads. | Low |
| PY-7 | Environments and packaging (have) | Existing | — | Package a tool with pyproject and install it in a fresh venv | boto3 scripts inside PS-7 | The log-parser installs from its pyproject into a fresh venv and its 3 pytest tests pass (doc 06). | Low |
| DB-1 | Hand-written SQL (have) | Existing | — | Write joins, aggregates, CTEs and window functions by hand | — | 8 of 10 SQL problems on your own schema, unaided (doc 06 DB exit check). | Low |
| DB-2 | Schema design and normalization (have) | Existing | — | Justify the grad project's schema: keys, constraints, 3NF | — | Explain the grad project's schema choices and normalization cold. | Low |
| DB-3 | Indexes and query plans (have) | Existing | — | Speed up a slow query and explain the plan | — | A slow query sped up with an index, with `EXPLAIN ANALYZE` before and after explained (doc 06). | Low |
| DB-4 | Transactions and isolation (have) | Existing | — | Explain isolation anomalies with an example from the grad project | — | Explain isolation levels and their anomalies cold, with an example from the grad project. | Low |
| DB-5 | SQL vs NoSQL (have) | Existing | — | Explain when to pick SQL or NoSQL | — | A 3-minute SQL vs NoSQL answer using Redis as the example (doc 06). | Low |
| DB-6 | Redis (have) | Existing | — | Explain Redis's roles in the grad project and what survives a restart | — | Explain what happens to the grad project's Redis data on restart, and why. | Low |
| WEB-1 | HTTP in practice (have) | Existing | — | Explain idempotency, cookies, sessions and CORS | — | Explain idempotency, cookies and CORS cold, using requests from the grad project. | Medium |
| WEB-2 | Django request lifecycle (have) | Existing | — | Trace a request from URLconf to response | — | Trace one request through the grad project's code (doc 06 WEB exit check). | Medium |
| WEB-3 | Django ORM and N+1 (have) | Existing | — | Find and fix an N+1 query | — | An N+1 query found and fixed with `select_related`/`prefetch_related`, with query counts before and after. | Medium |
| WEB-4 | Django authentication (have) | Existing | — | Explain sessions vs tokens, CSRF and password hashing | — | Explain the grad project's authentication and CSRF protection cold. | Medium |
| WEB-5 | REST API design (have) | Existing | — | Design an endpoint's resources, status codes, pagination and versioning | — | Defend one grad-project endpoint's design: status codes, pagination, versioning. | Medium |
| WEB-6 | Python web deployment model (have) | Existing | — | Explain how a Django app is served in production | — | Explain how the grad project is served in production: workers, reverse proxy, static files. | Medium |
| WEB-7 | Reliable async tasks (Celery) (have) | Existing | — | Make a task idempotent with retries and backoff | Kill a Celery worker mid-task | Kill a worker mid-task and explain the outcome; implement an idempotent retry (doc 06). | Medium |
| WEB-8 | Capstone architecture (have) | Existing | — | Whiteboard the capstone with ownership boundaries | — | A 3-minute whiteboard of the capstone, including failure handling at the AI boundary (doc 06). | Medium |
| GIT-1 | Git's model (refresh) | NTI | — | Explain commits, branches, HEAD and the staging area | — | Draw the commit graph and HEAD for a given sequence of commands, cold. | High |
| GIT-2 | Branching, merge vs rebase, conflicts (refresh) | NTI | — | Resolve merge and rebase conflicts | Git disaster drills | Resolve a staged merge conflict and a rebase conflict, explaining each step. | High |
| GIT-3 | Undo and recover (refresh) | NTI | — | Recover from 5 Git disasters | Git disaster drills | Recover from 5 staged Git disasters and explain what each command did to the commit graph (about 45 min, doc 06). | High |
| GIT-4 | PR workflow and secrets hygiene (refresh) | NTI | — | Remove a committed secret properly | Git disaster drills | A committed fake secret removed from history and rotated; `.gitignore` and PR hygiene explained. | High |
| SEC-1 | Security principles | Shared | — | Explain each principle with an example from your project | TryHackMe Cyber Security 101 rooms | Part of the SEC exit check (30 questions at 80%+). | High |
| SEC-2 | Cryptography and PKI | Shared | SEC-1 | Explain which primitive fits which job | THM cryptography rooms | Explain TLS certificate validation cold. | Medium |
| SEC-3 | Attack types | DEBI | SEC-1 | Explain 10 attacks with detection and mitigation | THM rooms as assigned | 5 attacks explained with detection + mitigation (doc 06). | Medium |
| SEC-6 | Identity concepts | Shared | SEC-1 | Explain OIDC federation as used by GitHub Actions → AWS | Enable MFA everywhere you own | Explain an OIDC trust policy line by line. | High |

### Stage 2 — Cloud and DevOps Engineering

Dec 2026 to mid-Feb 2027 (NTI Docker, CI/CD, AWS, Terraform, K8s, monitoring). **Gate 2: project stages PS-1 to PS-5 committed and SAA-C03 passed.**

| ID | Competency | Source | Prerequisites | Learning objectives | Practical work | Evidence | Priority |
| --- | --- | --- | --- | --- | --- | --- | --- |
| CTR-1 | Dockerfile from a blank file (refresh) | NTI | LNX-1, LNX-4 | Write the grad project's Dockerfile from memory | PS-1 | Dockerfile rewritten from memory (PS-1). | High |
| CTR-2 | Hardened images | NTI | CTR-1 | Ship a minimal non-root image | PS-1 | PS-1 Dockerfile: multi-stage, non-root, healthcheck, pinned. | High |
| CTR-3 | Docker Compose (have) | Existing | CTR-1 | Keep using it as the local stack | — | Grad project runs with Compose. | Low |
| CTR-4 | Debug containers | NTI | CTR-3, NET-6 | Fix 3 broken Compose setups | 3 broken Compose setups | Doc 06 CTR exit check. | Medium |
| CTR-5 | Container internals | NTI | CTR-1, LNX-3 | Explain what isolates a container | — | 2-minute explanation in English. | Medium |
| CTR-6 | Image scanning and triage | NTI | CTR-2 | Triage scanner output, not just run it | PS-1 | Trivy report with top findings fixed or justified in the README. | High |
| K8S-1 | Kubernetes fundamentals | NTI | CTR-5 | Deploy the grad project to a local cluster | kind or k3s locally | The grad project runs on a local kind/k3s cluster with readiness and liveness probes and a Secret; torn down and redeployed unaided. | Medium |
| K8S-3 | Kubernetes delivery: Helm, Kustomize, GitOps | Independent | K8S-1, CI-3 | Argo CD keeps the local cluster in sync with Git | PS-6 | Argo CD syncs the grad project from Git into kind/k3s. | Low |
| TST-1 | Testing with pytest (refresh) | Independent | PY-3, PY-5, WEB-2 | Add tests that a pipeline can gate on | PS-2 | Tests run in PS-2's pipeline. | Medium |
| TST-2 | Integration testing | Independent | TST-1, DB-2 | Run integration tests against service containers in CI | PS-2 | PS-2's integration job catches a deliberately broken migration. | Medium |
| CI-1 | CI/CD concepts | NTI | GIT-1 | Explain each stage's purpose | — | 2-minute explanation. | High |
| CI-2 | GitHub Actions workflow | NTI | CI-1, TST-1 | Run the grad project's tests in CI | PS-2 | Green pipeline on the grad project. | High |
| CI-3 | Build and publish images in CI | NTI | CI-2, CTR-2 | Tagged image on every merge | PS-2 | Merge produces a tagged image. | High |
| CI-4 | CI secrets and branch protection | NTI | CI-2 | Protect main with required checks | PS-2 | A PR with a failing check cannot merge. | High |
| CI-5 | Release automation | Independent | CI-3, GIT-4 | Cut a tagged release from CI with a changelog | PS-2 | Tagged releases with a generated changelog; a /version endpoint returns the deployed version. | Medium |
| DSO-1 | Pipeline security gates | NTI | CI-2, CTR-6 | Choose and tune gates; explain each trade-off; Run an OWASP ZAP baseline scan against the staging app and triage its findings | PS-2: plant a vulnerable dependency and a fake secret | Pipeline blocks both planted issues; README explains each gate. | High |
| CLD-1 | Cloud concepts and cost control | NTI | NET-1 | Set a budget alarm before any lab | Budget alarm on your AWS account | Budget alarm exists; explain shared responsibility. | High |
| CLD-2 | AWS IAM basics | NTI | CLD-1, SEC-6 | Read and write a least-privilege policy | PS-3 | PS-3 uses roles only; no long-lived keys on the instance. | High |
| CLD-3 | VPC networking | NTI | CLD-1, NET-2, NET-3 | Build a two-tier VPC by hand once, then in Terraform | PS-3 | Explain the packet path private subnet → NAT → internet (doc 19 'can explain cold'). | High |
| NET-8 | Multi-tier network design | NTI | CLD-3 | Subnet a /16 for public/private/DB tiers and justify each rule | PS-3 network design | Doc 06 F3 check: /16 design with every rule justified. | High |
| CLD-4 | Deploy to compute | NTI | CLD-3, CTR-2, LNX-6 | Deploy and reach it securely | PS-3 | App running on AWS with a documented teardown. | High |
| CLD-5 | S3 and managed data | NTI | CLD-2, CLD-3, DB-1, DB-2 | Keep data private by design | PS-3 | DB not reachable from the internet; S3 public access blocked. | High |
| CLD-6 | CloudWatch logs, metrics, alarms | NTI | CLD-4 | Alarm on something you can trigger | PS-5 | An alarm you triggered on purpose. | Medium |
| CLD-7 | Explain architecture and cost | NTI | CLD-4, CLD-5 | 5-minute walkthrough | — | 5-minute architecture and cost walkthrough (doc 06 M3 check). | Medium |
| IAC-1 | Terraform core | NTI | CLD-3 | Describe PS-3 in Terraform | PS-4 | Whole PS-3 environment in Terraform. | High |
| IAC-2 | Terraform state and modules | NTI | IAC-1 | Destroy and re-apply cleanly | PS-4 | terraform destroy + apply works from a clean checkout. | High |
| CI-6 | Multi-environment promotion | Independent | IAC-2, CI-5 | Promote one image from dev to prod with config-only differences | PS-4 | Same image digest running in dev and prod; dev torn down to control cost. | Medium |
| IAC-3 | Ansible configuration management | NTI | LNX-6, LNX-8 | Harden a VM with a playbook | Turn the LNX hardening steps into a playbook | Playbook in a repo. | Low |
| LNX-9 | Resource triage | NTI | LNX-3 | Find what fills a disk | Doc 20 incident labs | Fix an injected resource problem. | Medium |
| OPS-1 | Logs, metrics, traces | NTI | LNX-5 | Emit structured logs from the grad project | PS-5 | Structured logs visible in CloudWatch or Grafana. | Medium |
| OPS-2 | Health checks, alerts, dashboard | NTI | OPS-1, CLD-6 | Alert on a real failure mode | PS-5 | One alert triggered on purpose. | Medium |
| OPS-3 | Diagnose from telemetry | NTI | OPS-2 | Diagnose without SSH | PS-5 | Injected failure found from telemetry (doc 06 M3 check). | Medium |
| OPS-4 | Automate an ops task | Independent | LNX-8 | Remove one manual step | Backup script from LNX-8 | Script in the repo, used by you. | Low |

### Stage 3 — Security Engineering

Mid-Feb to about Jun 2027 (DEBI becomes the main structure). **Gate 3: IR runbook + tabletop postmortem written; OWASP self-review of the grad project with 3+ real fixes; SEC exit check (30 questions at 80%+).**

| ID | Competency | Source | Prerequisites | Learning objectives | Practical work | Evidence | Priority |
| --- | --- | --- | --- | --- | --- | --- | --- |
| SEC-4 | Vulnerability, threat and risk | Shared | SEC-1 | Prioritize findings by risk, not count | Re-triage PS-1 Trivy findings with CVSS | Risk-ranked findings list for the grad project. | High |
| VM-1 | Vulnerability scanning practice | NTI | SEC-4, NET-6 | Run a full scan-to-fix cycle | Scan your own VM only | Scan-to-fix report. | Medium |
| SEC-5 | Security controls | DEBI | SEC-1, NET-3 | Pick the right control for a threat | THM rooms as assigned | SEC exit check. | High |
| NSEC-1 | FortiGate administration (NSE 4) | DEBI | SEC-5, NET-7 | Configure a FortiGate VM lab | FortiGate VM lab | Lab write-up with policies, NAT and VPN. | Low |
| SEC-7 | Detection and incident-response lifecycle | DEBI | SEC-5 | Walk an incident through all phases | THM IR rooms | SEC exit check; IR-1 runbook. | High |
| LOG-1 | Log analysis and SIEM practice | DEBI | SEC-7, LNX-5 | Triage an alert end to end | THM SOC rooms as assigned | Triage write-up of one investigated alert. | High |
| IR-1 | Incident-response practice | Shared | SEC-7 | Run one tabletop end to end | Tabletop: leaked access key | Runbook + postmortem in the repo. | High |
| SEC-8 | Governance and frameworks | Shared | SEC-1 | Map your controls to CIS | — | PS-7 README maps controls to CIS. | Low |
| WIN-1 | Windows fundamentals slice | DEBI | SEC-1 | Read the Windows Security log | — | Explain 3 security event IDs. | Low |
| TM-1 | Threat modeling | NTI | SEC-3, WEB-8 | One-page threat model per project stage | Grad project threat model | Threat model in the grad project README. | Medium |
| APPSEC-1 | Exploit then fix on your own app | Shared | SEC-3, WEB-1, WEB-4 | Exploit and fix each class on the grad project | Local copy of the grad project only | Committed OWASP self-review with 3+ real fixes (doc 06). | Medium |
| APPSEC-2 | Security review write-up | Independent | APPSEC-1 | Write findings a developer can act on | — | One review document in the repo. | Low |
| DSO-2 | Software supply chain | NTI | DSO-1 | Generate and read an SBOM | Add SBOM to PS-2 | SBOM artifact published by the pipeline. | Medium |

### Stage 4 — Cloud Security Specialization

About Apr to Sep 2027. **Gate 4: PS-7 detects 5 simulated attacks with tested detections; SCS-C03 booked.**

| ID | Competency | Source | Prerequisites | Learning objectives | Practical work | Evidence | Priority |
| --- | --- | --- | --- | --- | --- | --- | --- |
| CSEC-1 | AWS IAM depth | Independent | CLD-2, CI-4 | Explain why a request is allowed or denied | Switch PS-2 to OIDC; least-privilege deploy role | Deploy role with reasoning per statement in the README. | High |
| CSEC-2 | Multi-account governance | Independent | CSEC-1 | Write and test an SCP | PS-7 | SCP set with tests. | Medium |
| CSEC-3 | Audit logging and posture | Independent | CSEC-1, CLD-5 | Raise the CIS score and explain each fix | PS-7 | CIS score before and after. | High |
| CSEC-4 | Cloud threat detection | Independent | CSEC-3, LOG-1 | Write and test 5 detections | PS-7 | Detection repo with test evidence. | High |
| CSEC-5 | Data protection | Independent | CLD-5, SEC-2 | Explain a key policy | PS-3, PS-7 | Key policy with reasoning. | Medium |
| CSEC-6 | Network and edge protection | Independent | NET-8, SEC-5, NET-5 | Remove all unnecessary public exposure | PS-7 | Exposure diagram with every public path justified. | Medium |
| CSEC-7 | Cloud incident response | Independent | CSEC-4, IR-1 | Run the leaked-key playbook | PS-7 tabletop | Playbook + postmortem. | High |
| CSEC-8 | Policy as code | Independent | IAC-2, DSO-1 | Block an insecure Terraform change in CI | PS-4 | PR with an insecure resource blocked. | High |
| CSEC-9 | Cloud attack paths | Independent | CSEC-1, APPSEC-1 | Complete the labs and explain each fix | Lab accounts only | Write-ups with the defensive fix. | Medium |
| K8S-2 | Kubernetes security | Independent | K8S-1, SEC-5 | Harden a cluster and prove it | PS-6 | Before/after kube-bench results. | Low |

### Stage 5 — Portfolio and Job Readiness

Runs throughout; shown last because it collects the evidence. **Gate 5: both CV versions live; every finished project stage has a portfolio README; a full mock interview passed.**

| ID | Competency | Source | Prerequisites | Learning objectives | Practical work | Evidence | Priority |
| --- | --- | --- | --- | --- | --- | --- | --- |
| JOB-1 | Two CV versions | Independent | — | Keep both CVs current each month | — | Both CVs live. | High |
| JOB-2 | Portfolio READMEs | Independent | TM-1, CLD-7 | Every finished stage is CV-ready on its own | PS-1 to PS-7 READMEs | README per finished stage. | High |
| JOB-3 | Application pipeline | Independent | JOB-1 | Apply steadily to the right titles | — | Ticked application tasks (doc 19 K1). | High |
| COMM-1 | Explain any competency in English | Independent | — | Explain on demand | — | Spoken checks (doc 19 K4). | Medium |
| COMM-2 | STAR stories | Independent | — | 3 polished stories | — | 3 stories under 2 min each. | Medium |
| COMM-3 | Whiteboard the capstone | Independent | CLD-7, WEB-6, WEB-8 | Draw and defend the deployed system | — | 3-minute whiteboard passed in a mock. | High |
| DSA-1 | Algorithm problems (have) | Existing | — | Stay warm, not drill | — | Give the optimal approach and its complexity for a medium problem aloud, then code it. | Low |

If you switch direction at the Stage 4 decision point, the core stays the same. SecOps leans on LOG-1, IR-1 and CSEC-3/4/7. Cloud infrastructure leans on K8S-1, IAC-3 and OPS-3/4. Each competency's path tags are in the HTML's Career paths view.

## Phase 5 — Project progression

One app (your graduation project) is built up in layers, so each stage deploys onto the previous one. PS-1 to PS-5 are doc 19 §G's project stages 1–5, unchanged. PS-7 adds the cloud-security layer after NTI. Every stage must stand on its own and be CV-ready when it's done (doc 19).

**Cost rule before PS-3:** set the budget alarm (CLD-1). NAT gateways, an EKS control plane and GuardDuty after its trial are where lab bills come from. Run Kubernetes locally.

### PS-1 — Container hardening

_Doc 19 project stage 1 · 21 Nov – ~20 Dec 2026_

- **Competencies:** CTR-1, CTR-2, CTR-6
- **Architecture:** Grad project Dockerfile rewritten from memory: multi-stage, non-root, healthcheck, pinned base.
- **Steps:** Rewrite the Dockerfile cold → Run trivy image → Fix or justify top findings in the README
- **Security goal:** Minimal attack surface in what you ship.
- **Deliverables:** Dockerfile + Trivy triage in README.
- **Why it gets you hired:** Shows you can harden, not only containerize.

### PS-2 — CI with security gates

_Doc 19 project stage 2 · Dec 2026_

- **Competencies:** GIT-1–4, TST-1, TST-2, CI-1–5, DSO-1, DSO-2
- **Architecture:** GitHub Actions on push: tests, pip-audit, Bandit, gitleaks, Trivy; fail on high; SBOM added later (DSO-2).
- **Steps:** Tests in CI with Postgres/Redis service containers → Integration job → Add each gate → Protect main → Release automation (SemVer, changelog) → Plant a vulnerable dependency and a fake secret; show both blocked
- **Security goal:** Nothing reaches a deploy unscanned.
- **Deliverables:** One red and one green run; README explains each gate's trade-off.
- **Why it gets you hired:** The DevSecOps job description in one repo.

### PS-3 — AWS deployment

_Doc 19 project stage 3 · Jan 2027, during NTI's AWS block_

- **Competencies:** CLD-1–3, NET-8, CLD-4, CLD-5, CSEC-5
- **Architecture:** VPC with public/private subnets; app on EC2 or ECS; Postgres private; least-privilege security groups; secrets in SSM/Secrets Manager; budget alarm; documented teardown.
- **Steps:** Budget alarm → VPC by hand once → Twelve-Factor config review → Deploy the app → Move secrets to SSM → Write the teardown
- **Security goal:** Private data tier, no long-lived keys, controlled cost.
- **Deliverables:** Running app + architecture diagram + teardown doc.
- **Why it gets you hired:** Matches the AWS skills most Egyptian DevOps postings name.

### PS-4 — Terraform + policy as code

_Doc 19 project stage 4 · Jan – Feb 2027_

- **Competencies:** IAC-1, IAC-2, CI-6, CSEC-8
- **Architecture:** PS-3 environment fully in Terraform with remote state; Checkov in CI blocks insecure changes.
- **Steps:** Port PS-3 to Terraform → Remote state with locking → destroy + re-apply → Dev and prod from the same code → Checkov gate
- **Security goal:** Reproducible infra with guardrails before deploy.
- **Deliverables:** Terraform repo; a PR blocked by Checkov.
- **Why it gets you hired:** IaC is in nearly every DevOps posting.

### PS-5 — Monitoring

_Doc 19 project stage 5 · by mid-Feb 2027_

- **Competencies:** OPS-1–3, CLD-6
- **Architecture:** Structured logs + metrics + one alert (CloudWatch or Prometheus/Grafana), triggered on purpose.
- **Steps:** Structured logging → Dashboard → Alert → Inject a failure and find it from telemetry
- **Security goal:** Know when it breaks before users do.
- **Deliverables:** Dashboard screenshot, alert evidence.
- **Why it gets you hired:** Closes the ops loop interviewers ask about.

### PS-6 — Kubernetes

_Doc 19 project stage 6, optional · only if target postings ask_

- **Competencies:** K8S-1, K8S-3, K8S-2
- **Architecture:** kind or k3s locally; RBAC per namespace, Pod Security 'restricted', default-deny NetworkPolicies, Kyverno, Falco.
- **Steps:** Deploy the app with Helm or Kustomize → Argo CD sync from Git → Apply each control → Run kube-bench before and after
- **Security goal:** A cluster you can defend.
- **Deliverables:** Hardened cluster repo + kube-bench results.
- **Why it gets you hired:** Opens K8s-heavy roles; first thing to drop otherwise.

### PS-7 — Cloud security baseline + detection

_New, after NTI · about Apr – Sep 2027_

- **Competencies:** CSEC-1–4, CSEC-6, CSEC-7, IR-1, LOG-1, SEC-8
- **Architecture:** On top of PS-3/PS-4: CloudTrail to a locked bucket, Config, Security Hub (CIS), GuardDuty → EventBridge → alerts; 5 detections; leaked-key playbook.
- **Steps:** OIDC deploy role → Logging + posture → 5 detections as code → Simulate with Stratus Red Team → Tabletop + postmortem → One review by someone more experienced
- **Security goal:** Detect within minutes; contain with a written procedure.
- **Deliverables:** Detection repo with tests, runbook, postmortem, CIS before/after.
- **Why it gets you hired:** The bridge from DevSecOps to cloud security / SecOps roles.

### PS-8 — DEBI capstone

_DEBI final project · end of DEBI, about late 2027_

- **Competencies:** CSEC-4, CSEC-7, TM-1
- **Architecture:** PS-7 grown into a full detection lab, or a small posture scanner (Python + boto3). Subject to DEBI approval.
- **Steps:** Get the topic approved → Extend PS-7 → Present
- **Security goal:** One app, three uses: NTI capstone, DEBI project, CV (doc 19 §C).
- **Deliverables:** DEBI submission.
- **Why it gets you hired:** Turns a program requirement into portfolio evidence.

## Phase 6 — Certifications and resources

Only two certs fill an actual gap: SAA-C03 now, and SCS-C03 after the projects. Every other cert here depends on a specific job target.

| Cert | Gap it fills | Verdict | When |
| --- | --- | --- | --- |
| AWS Solutions Architect Associate (SAA-C03) | AWS services, which neither map names | **Keep** (decided, G16). $150 list; NTI's voucher discounts it. I found no announced retirement, but recheck the code before booking | 2–4 weeks after NTI's AWS block |
| [AWS Security Specialty (SCS-C03)](https://docs.aws.amazon.com/aws-certification/latest/examguides/security-specialty-03.html) | Proves the Stage 4 specialization | **Target.** It replaced SCS-C02 in Dec 2025, with 170 minutes, 65 questions and a $300 fee. [AWS](https://aws.amazon.com/certification/certified-security-specialty) notes candidates commonly hold SAA first | After PS-7, about Q4 2027 |
| CompTIA Security+ | HR filter. DEBI's content covers most of its syllabus | **Conditional.** Deferred (G14). $439 retail; SY0-801 launched 17 Nov 2026, and SY0-701 runs until 11 Jun 2027. Worth it for SOC roles, government work or Gulf postings that filter on it; low value for DevSecOps hiring | Revisit about May 2027, as already planned |
| Fortinet NSE 4 | Vendor firewall administration | **Conditional:** only if DEBI funds the exam itself or you target network-security roles (G15 amended 23 Nov 2026). It doesn't serve cloud security | G15 slot: Mar–May 2027 |
| CKA → CKS | Kubernetes depth | **Optional.** Only if your target postings demand Kubernetes. NTI's voucher lowers the cost | After PS-6 |
| Terraform Associate | IaC | **Skip.** The PS-4 repo proves more | — |
| CEH, OSCP, CISSP, CISA/CISM | Offense, or experience-gated | **Skip.** Off-path or not open to you yet | — |

**How each kind of knowledge is best learned:**

| Kind | Topics | Best resource |
| --- | --- | --- |
| Structured learning | AWS services (SAA), security fundamentals, IR theory | NTI sessions, DEBI's assigned Coursera and TryHackMe paths, AWS Skill Builder (free) |
| Hands-on practice | Terraform, IAM policies, pipelines, detections, hardening | Project stages PS-1 to PS-7; TryHackMe labs through DEBI |
| Focused reference or lab | CIS benchmarks, KMS, Kubernetes security controls, cloud attack paths | Official docs, flAWS/flAWS2, CloudGoat, Stratus Red Team (all free) |

Paid extras: none needed for this roadmap. If you did buy the TestDriven.io Django/Celery course, it serves Project 2's app side, not the security side.

## Phase 7 — Weekly execution

**Doc 19 §J governs the week; this roadmap changes what goes into the slots, not the slots.** The realistic ceiling while NTI runs is about 4.5–5 h a week outside NTI and DEBI weekends (doc 19 §F). The expected level is 3–4 h. The personal timetable isn't published in this file; the app's timetable view shows it only after it's unlocked.

| Slot type | What goes there from this roadmap |
| --- | --- |
| NTI days | Stage 1–2 competencies with NTI as source |
| Two short evening slots (about 45 min each) | One item: DEBI's assigned course, or a TryHackMe room matching the current NTI block. Test out first where you're "Existing" or "refresh" |
| One weekly project block (about 3 h) | The current project stage (PS-1 → PS-5). Independent competencies (TST-1, TST-2, CI-5, CI-6, CSEC-5, CSEC-8) are learned here, by building |
| DEBI in-person weekends | DEBI sessions |
| One light slot | Applications (JOB-3), plus an optional one-line note |

After NTI ends (mid-Feb 2027), DEBI becomes the main structure at 15–20 h, with projects PS-6/PS-7, NSE 4 if kept, and job search alongside. The post-NTI rebuild decides the split.

### Rules that stop double study

- **One competency, one lead source.** The other program's version of the same topic is revision only.
- **Test out before you sit through.** Existing and refresh items get the exit check first (doc 06 checks).
- **Evidence, not completion.** A competency is done when its Evidence cell exists. Records rule K1–K8 (doc 19 §K) still applies: ticks and commits are the record, and you write no notes.
- **Missed days don't roll over** (doc 18 rules X1, X4, X6–X8).

## Phase 8 — Interactive companion

**nti-debi-roadmap.html** is a single offline file that visualizes this roadmap and tracks progress. It is generated from the same data as the Phase 4 and 5 tables, so IDs, names, prerequisites and order match exactly.

- **Views:** a flowchart (competencies in dependency order, left to right, every prerequisite drawn as an arrow); a stage map (stages × domains); a Kanban board (Locked / Ready / In progress / Completed, drag to change status); a checklist with filters; the career-path decision point; the NTI vs DEBI matrix with NTI module hours; project progression; a certification timeline; and a dashboard with a skills radar by domain. Node headlines show the competency name; the ID sits in the detail panel, chips and checklist.
- **Each competency** opens a panel with: description, why it matters, objectives, prerequisites and what it unlocks, NTI and DEBI material, resources, labs, evidence and hours. Where the sources say nothing, the panel says "not stated in the source material" rather than guessing.
- **Progress:** Not started / In progress / Completed per competency, plus notes and evidence. A competency stays locked until its prerequisites are completed. Progress is stored in that browser's localStorage, with export, import and reset buttons.
- **Limits:** progress lives in one browser on one machine, so export it to move it. The Study Plan records (doc 15) remain the official source of truth (doc 14); the HTML is a personal tracker.

**Taken from devopsroadmap.io (v1.1):** TST-2 integration testing, CI-5 release automation, CI-6 multi-environment promotion, K8S-3 Helm/Kustomize and GitOps (optional), a Twelve-Factor review in PS-3, an experienced reviewer for PS-7, and the dashboard's skills radar. Its DevOps generalist sequence otherwise duplicates NTI, so it's a checklist for the project stages, not a third curriculum.

## Open questions before finalizing

The first two would change the matrix the most; get those first.

- [ ] **Which CI/CD tool NTI teaches**, and whether NTI accepts your own app for the capstone (module hours are now known from doc 19)
- [ ] **DEBI's instructor-assigned courses**: which Coursera and TryHackMe paths, in what order
- [ ] When NTI's AWS block runs, which sets the SAA date
- [ ] Can you test out of DEBI-assigned content you already know?
- [ ] Can DEBI's final project be AWS cloud security, given AWS courses don't count?
- [ ] NTI voucher terms: which exams, what discount, any deadline
