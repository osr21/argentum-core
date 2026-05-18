# Guarantee Model: Mycelium Trails × SafeAgent × DashClaw

This document defines what each layer of the joint Mycelium × SafeAgent × DashClaw stack
proves — and what it does not prove — so that consumers can reason about guarantees without
misreading orthogonal properties as stacked dependencies.

## What a COMMITTED SafeAgent claim proves

- This action was claimed before execution
- A duplicate retry with the same `request_id` would have returned `SKIP`
- The exactly-once property held at the execution boundary

## What a COMMITTED SafeAgent claim does not prove

- That the action was recorded externally
- That the outcome is tamper-evident after the fact

## What a Mycelium TrailRecord proves

- This action occurred, with this hash, anchored at this block
- The record has not been modified since anchor time

## What a Mycelium TrailRecord does not prove

- That the action occurred exactly once

## Composing Layer 2 + Layer 4

Both guarantees together: a verifier who finds a `TrailRecord` **AND** a `COMMITTED` claim
for the same `action_ref` can assert the action ran **exactly once AND** the outcome is
tamper-evident. Neither guarantee requires the other — consumers can adopt either
independently based on their requirements.

## Trail status states

A `TrailRecord` carries a `trail_status` field with three terminal or transitional values:

| Status | Meaning | `tx_hash` | Verifiable externally? |
|--------|---------|-----------|----------------------|
| `COMMITTED` | Execution completed, on-chain anchor exists | non-null | Yes — via `tx_hash` |
| `PENDING` | External call started, outcome not yet verified | non-null | Follow-up — query `tx_hash` directly |
| `PENDING` (degraded) | Signer crashed before recovering verification reference | null | No — signer has nothing to hand off |
| `FAILED` | Terminal. Execution did not complete or post-execution receipt never arrived | null | Yes — absence of `tx_hash` |

`PENDING` has two named variants distinguished by `tx_hash`:

- **`PENDING/non-null`** — effect crossed the boundary, follow-up verification handle exists. The signer knows where to look; the next agent turn or operator can verify independently.
- **`PENDING/null`** (degraded) — effect may have crossed the boundary, but the signer crashed before recovering the reference. The honest record is "I started, I do not know if it landed, I have nothing to hand off." This is a different quality of not-knowing, not a different outcome.

### Crash-after-charge handling

For non-idempotent external systems (payments, regulated actions), the crash window between
the external call starting and the outcome being verified produces a `PENDING` record.
Resolution:

1. Pre-execution receipt emitted → `trail_status: PENDING`, `tx_hash: null` (degraded)
2. Verification reference recovered → `tx_hash` populated, status remains `PENDING/non-null`
3. Post-execution receipt arrives → status transitions to `COMMITTED`, `tx_hash` confirmed
4. If post-execution receipt does not arrive within TTL → status resolves to `FAILED`

No happy-path assumption is baked in. A `COMMITTED` record without a corresponding
post-execution receipt cannot exist.

### Verification reference

`tx_hash` is the follow-up verification reference. Any auditor can query the chain directly
using `tx_hash` without trusting the operator's logs or database. The on-chain anchor is
the single source of truth for terminal state.

A `PENDING/null` record is not a verification failure — it is an honest declaration that
the signer's knowledge ended before a handle could be recovered. The contract: the receipt
never lies about what the signer actually knew at signing time.

## Canonical key derivation

All three systems converge on the same linking key:

```
action_ref = SHA-256(
  agent_id.encode('utf-8') ||
  action_type.encode('utf-8') ||
  scope.encode('utf-8') ||
  timestamp_ms.to_bytes(8, 'big')
)
```

All four fields are required. `timestamp_ms` is millisecond-precision Unix time at claim time
(before execution), encoded as int64 big-endian.

### DashClaw field mapping

| Joint spec field | DashClaw field |
|-----------------|----------------|
| `agent_id` | `agent_id` |
| `action_type` | `action_type` |
| `scope` | `authorization_scope` |
| `action_ref` / `request_id` | `idempotency_key` (caller-computed) |
| `action_id` | DashClaw's local evidence/outcome row ID |

Callers compute `action_ref` externally and pass it as `idempotency_key`. DashClaw consumes
it opaquely; SafeAgent and Mycelium standardize the key. No runtime coupling required.

## References

- SafeAgent RFC: [`RFC_EXECUTION_GUARD.md`](https://github.com/azender1/SafeAgent/blob/main/RFC_EXECUTION_GUARD.md)
- Joint spec issue: [`giskard09/argentum-core#7`](https://github.com/giskard09/argentum-core/issues/7)
- DashClaw issue: [`ucsandman/DashClaw#105`](https://github.com/ucsandman/DashClaw/issues/105)

Co-authored-by: azender1 <azender1@users.noreply.github.com>
