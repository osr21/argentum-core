# Mycelium Trails — Regulatory Compliance Mapping

**Version:** 1.1 — 2026-05-16 — Approved for due diligence  
**Prepared by:** Legal, Rama

---

## Legal Notice

This document is informational. It does not constitute legal advice or a guarantee
of regulatory compliance. Recipients should obtain independent legal advice regarding
requirements applicable to their jurisdiction and activities. Rama assumes no
liability for decisions made based on this document without independent verification.

## Trademark Notice

"Mycelium Trails" and "Rama" are descriptive service and company names. Neither is
currently registered as a trademark with USPTO, EUIPO, or UKIPO.

---

## What Mycelium Trails Is

Mycelium Trails is an immutable audit-trail system for AI agent activity. Every
action executed by an agent produces a signed record anchored to an external surface
outside the operator's control — making the record tamper-evident after the fact.
The result is an evidence trail auditable by third parties without depending on the
operator's infrastructure.

## What Problem It Solves

AI systems operating in regulated environments produce internal logs. The problem
is that those logs live in the operator's own infrastructure: they can be rewritten,
deleted, or reconstructed before an audit. Mycelium Trails closes that gap: the hash
of each evidence record is written to an external append-only surface at execution
time. After that point, any modification to the record is detectable by an
independent auditor — without access to the operator's runtime or any prior trust in it.

## Why Operator-Signed Receipts Are Not Enough

Several audit-trail systems for AI agents generate receipts that are signed by the operating platform itself. This is the structural gap: if the signer and the operator are the same entity, a receipt proves that *someone with the operator's key* attested to an event — not that the event occurred, not that the record has not been rewritten, and not that the operator is telling the truth. Offline verification means trusting the operator.

EU AI Act Art. 12 requires that logs be available to the *competent national authority*, which implies independent verification — the authority cannot depend on the operator's infrastructure or key material to assess whether a high-risk system behaved as documented. FCA SYSC 9.1 similarly requires records "sufficient for the FCA to supervise compliance," which presupposes that the FCA can verify record integrity without relying on the firm's own attestation.

Mycelium Trails separates the verifier from the operator by design: the action_ref is derived client-side (SHA-256 over a JCS-canonical preimage), and the hash is anchored on a public blockchain before the record is submitted. A regulator, counterparty, or auditor verifies by recomputing the hash from the preimage fields and confirming the on-chain anchor — no operator key, no operator infrastructure, no operator trust required.

## Technical Guarantee — Scope and Limits

**What Mycelium Trails proves:** that the evidence record existed, unmodified, at
the time of anchoring. An external verifier can confirm this without accessing the
operator's systems.

**What Mycelium Trails does not prove:** that the record's content was accurate at
the time of writing. The guarantee is tamper-evidence, not content correctness. This
distinction matters in contexts where the regulator evaluates both log integrity and
the truthfulness of what was recorded.

---

## Regulatory Mapping

| Framework | Relevant Requirement | How Mycelium Trails Addresses It | Legal Status |
|-----------|---------------------|----------------------------------|-------------|
| **EU AI Act Art. 12** (effective 2 Aug 2026) | Automatic logging of high-risk AI system operation, retained to enable supervision by the competent national authority. | Each agent action produces a record with a signed, externally-anchored hash. The record is auditable by the competent authority without operator access. *Note: Art. 12 requires automatic logging; tamper-evidence is a necessary but not sufficient condition for full compliance. See Note (1).* | **[LEGAL-OK]** Mycelium "supports" Art. 12 — does not "satisfy" it alone. |
| **SOC 2 CC7.x** (Change Management / Incident Response) | Detection of unauthorized changes to system components and integrity evidence in audit reviews. | External anchoring enables detection of any post-write modification to the evidence record. The auditor runs independent verification without relying on the operator. | **[LEGAL-OK]** |
| **ISO 27001 A.12.4** (Logging and Monitoring) | Protection of event logs against modification or unauthorized access. | Records cannot be altered without the system detecting a discrepancy on verification. Protection is structural — does not depend on the operator's internal access controls. | **[LEGAL-OK]** |
| **FCA SYSC 9.1** (Recordkeeping — UK financial services) | Retention of records sufficient for the FCA to supervise compliance, for the applicable period. | Mycelium generates records the FCA can verify independently. However, "sufficiency" under SYSC 9.1 also encompasses content and retention period. The system covers integrity but does not define retention policy — that must be configured by the operator per the financial instrument. See Note (2). | **[REVIEW]** Retention policy is operator responsibility. |
| **Basel III / BCBS 239** (Risk Data Aggregation) | Auditable data lineage, verifiable by the regulator independently of the reporting firm. | The evidence trail covers who executed what action, when, and with what outcome. External anchoring allows the regulator to verify lineage without depending on the reporting bank's infrastructure. | **[LEGAL-OK]** |

---

## Notes

### (1) EU AI Act Art. 12 — "supports" vs "satisfies"

Article 12.1 requires that the system "automatically record events" and that those
records be "sufficient to identify the reasons for the outputs of the system."
Mycelium Trails guarantees that existing records cannot be altered — but it does not
determine what is recorded or at what granularity. Full Art. 12 compliance also
requires: (a) the operator configures logging at adequate granularity, and (b) records
contain the fields the article enumerates.

Mycelium Trails **supports** Art. 12 on the integrity and independent-audit component.
It does not **satisfy** the article alone.

**Recommendation:** In all external communications, use "supports compliance with" or
"supports adherence to" — never "satisfies" or "ensures compliance." The difference
is material before a regulator.

### (2) FCA SYSC 9.1 — Retention Policy

SYSC 9.1 establishes retention periods that vary by financial instrument type
(e.g. 5 years for most MiFID II instruments). Mycelium Trails guarantees record
integrity but does not define or manage retention policy. The operator must explicitly
configure how long anchored records are retained and in which backend. Without a
documented retention policy, an FCA audit may question compliance even if records
are intact.

This is an operator configuration gap, not an architecture gap. For UK financial
services clients, retention policy is an implementation conversation, not a product
limitation.

---

## Current Status

- [argentum-core](https://github.com/giskard09/argentum-core) specification published, including 4 live conformance fixtures verifiable at `https://argentum-api.rgiskard.xyz/trails/verify`
- AGT EvidenceAnchor integration: PR [microsoft/agent-governance-toolkit#2415](https://github.com/microsoft/agent-governance-toolkit/pull/2415) open for review
- action_ref derivation (JCS RFC 8785 + SHA-256) cross-validated by three independent implementations

---

## Executive Summary

| | |
|---|---|
| Frameworks reviewed | 5 |
| **[LEGAL-OK]** | 4 |
| **[REVIEW]** | 1 (FCA SYSC 9.1 — retention policy is operator configuration, not a product gap) |
| EU AI Act language | Approved with precision note: "supports" not "satisfies" |
| Approved for | Due diligence with compliance officers (banking, insurance, regulated enterprise) |

---

*For questions about this mapping, open an issue in [argentum-core](https://github.com/giskard09/argentum-core/issues).*
