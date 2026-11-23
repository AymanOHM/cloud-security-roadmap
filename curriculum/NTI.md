# NTI — Professional DevSecOps Engineer (Digital Egypt Youth HireReady)

Verified facts with sources, then what the roadmap.sh stand-in shows, then unknowns. The analysis of how NTI
fits the plan is in `../ROADMAP.md` (Phases 1–2). **Never add NTI course material to this repo** (NTI's terms
forbid publishing it): names, hours and the owner's own words only.

## Verified
| Fact | Source |
|---|---|
| Track: Professional DevSecOps Engineer (code D004), National Telecommunication Institute, Digital Egypt Youth HireReady initiative, at Smart Village | NTI curriculum page, pasted 16 Oct 2026 (Study Plan doc 17 §1) |
| Starts Sat 17 Oct 2026; 3 months on site + 1 month on-the-job training at a partner company (120 h); ~7 training hours a day, 5 days a week; ends ~mid-Feb 2027 | NTI HireReady FAQ; doc 17 §1 |
| **Part 1, technical (294 h):** Linux + Bash 35 · Git 7 · Python 22 · Agile & DevSecOps 14 · Docker 21 · Kubernetes 49 · AWS 49 · OpenStack 21 · Terraform 21 · Ansible 14 · Monitoring 7 · CI/CD & DevSecOps pipeline 28, plus a practice project ("secure end-to-end DevSecOps pipeline for a sample application") | NTI curriculum page (doc 17 §1) |
| **Part 2, career development (126 h):** Business English 35 · soft skills 42 · project management 14 · essential workplace skills 35, with a capstone presentation (6 h) | NTI curriculum page (doc 17 §1) |
| Listed prerequisite: CCNA-level networking (not taught) | NTI curriculum page |
| Attendance ≥75%; scores exist (pass threshold not published) | NTI terms (doc 17 §1) |
| Course materials may not be posted online | NTI terms (doc 17 §1) |
| Percentage-discount exam vouchers for several certifications incl. AWS and Kubernetes (% and expiry unknown) | Study Plan doc 17 §1 (19 Oct 2026) |
| The NTI page names SAA-C02 (retired); the current exam is SAA-C03 | doc 17 §1 |
| Linux Administration 1 material reviewed: 5.5/10, study selectively (guide in a Google Doc) | Study Plan doc 20 |
| Soft-skills phase ran first; Linux block started ~mid-Nov 2026 (not confirmed by a handoff) | records, doc 20 |

Machine-readable hours: `../data/roadmap.json` → `ntiHours`, `ntiPart2Hours`.

## The roadmap.sh stand-in
`private/sources/roadmap-sh-devsecops.pdf` (roadmap.sh "DevSecOps" map) was supplied as "the NTI roadmap". It is
a public topic map, not NTI's syllabus. It assumes the DevOps core is learned elsewhere and runs from junior
topics (OWASP, secure coding, SIEM, IAM, Docker/K8s image scanning) to senior ones (multi-region security,
PKI failover, risk quantification). Its topic list is summarised in `../ROADMAP.md` Phase 1; the
`nti` field of each competency cites it as "NTI map: … (verified, roadmap PDF)".

## Unknown (open questions)
- Per-module content, labs, assessments and order beyond names and hours.
- Which CI/CD tool NTI teaches.
- Whether the owner's own app can be the NTI capstone; capstone rules.
- Voucher discount % and expiry.
- How the company-training employer is assigned.
