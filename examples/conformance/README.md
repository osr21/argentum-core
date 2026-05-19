# Conformance Fixtures — Mycelium Trail Status States

Four fixtures covering every `trail_status` state defined in [`docs/spec/guarantee-model.md`](../../docs/spec/guarantee-model.md).

## Purpose

Cross-validation baseline for external implementors (Nobulex/Gogani, SafeAgent, DashClaw). Any system that emits or consumes TrailRecords can byte-match these fixtures against its own output.

## Fixtures

| File | Status | `tx_hash` | Externally verifiable? |
|------|--------|-----------|----------------------|
| `committed.fixture.json` | `COMMITTED` | non-null (real Base tx) | Yes — via tx_hash on-chain |
| `pending-non-null.fixture.json` | `PENDING` | non-null | Follow-up — query tx_hash |
| `pending-null.fixture.json` | `PENDING` (degraded) | null | No — signer lost reference |
| `failed.fixture.json` | `FAILED` | null | Yes — absence of anchor confirmed |

## action_ref derivation

```
preimage  = JCS(RFC 8785) of {"action_type", "agent_id", "scope", "timestamp"}
            — keys in lexicographic order, no whitespace, UTF-8
action_ref = SHA-256(preimage) → lowercase hex (64 chars)
```

All preimage fields are in each fixture under `trail_record.preimage` and the
verbatim JCS payload under `trail_record.jcs_payload`. Any party can recompute
independently without trusting the emitting system.

## Verify against live endpoint

Each fixture has a `_verify.by_action_ref` curl command executable against the public API:

```
https://argentum-api.rgiskard.xyz/trails/verify?agent_id=<id>&action_ref=<ref>
```

The COMMITTED fixture uses a real Base mainnet anchor — independently verifiable at basescan.org.

## COMMITTED tx_hash

`0x7fd0a8ededd1feb65ab37b3324218a0386dbf124174cf122bffc40717c057b84` — pioneer-agent-001 Oasis payment, Base mainnet 2026-04-13.

## Spec references

- [`docs/spec/guarantee-model.md`](../../docs/spec/guarantee-model.md) — state definitions
- [`docs/spec/action-ref.md`](../../docs/spec/action-ref.md) — derivation algorithm
