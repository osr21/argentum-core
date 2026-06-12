# wallet-binding-v1 conformance vectors

Seven vectors (6 REJECT, 1 PASS) covering the wallet-binding architecture failure modes.

Spec: [`docs/spec/decision-binding-ref-v1.0.md`](../../docs/spec/decision-binding-ref-v1.0.md)

| # | Name | Expected | Failure mode |
|---|------|----------|-------------|
| 1 | replay-unbound | REJECT | `REPLAY_UNBOUND` |
| 2 | payload-drift | REJECT | `PAYLOAD_DRIFT` |
| 3 | non-canonical-encoding | REJECT | `NON_CANONICAL_ENCODING` |
| 4 | signer-mismatch | REJECT | `SIGNER_MISMATCH` |
| 5 | decision-unbounded | REJECT | `DECISION_UNBOUNDED` |
| 6 | cross-framework-pass | **PASS** | — |
| 7 | session-expired | REJECT | `SESSION_EXPIRED` |
