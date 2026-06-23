# action-ref retrieval-provenance conformance vectors — v1

Per-chunk retrieval provenance under `action-ref-v1`, for RAG / document pipelines (legal review, due diligence, regulatory compliance). The retriever receipt carries a `retrieved_chunks` array — each entry a span (`doc_id`, `chunk_id`, `page`, `bbox`, `text`) plus a `source_hash`. The provenance rides **inside the signed receipt**; `action_ref` stays component-level and is unchanged.

A conformant trace lets an independent verifier map **every generator claim back to a specific span in a specific document** — the defensibility test for regulated AI pipelines. Each fail-closed vector is a way that property breaks.

**Spec:** `draft-giskard-aeoess-action-ref` · `docs/spec/action-ref.md`
**Canonicalization:** RFC 8785 (JCS)

## Derivations

```
action_ref  = "sha256:" + hex(SHA-256(JCS({agent_id, action_type, scope, timestamp})))   # component-level
source_hash = "sha256:" + hex(SHA-256(JCS({bbox, chunk_id, doc_id, page, text})))         # per-chunk span
```

## Vectors

| Vector | Result | Error code | What it shows |
|--------|--------|------------|---------------|
| `conformant_per_chunk_trace` | pass | — | Every chunk has a JCS-canonical `source_hash`; every claim cites a present `chunk_id`. The trace recomputes for a third party |
| `tampered_span_mismatch` | fail-closed | `SOURCE_HASH_MISMATCH` | Span text altered after signing (30→90 days); embedded hash recomputes under neither JCS nor colon-join — content tampering |
| `noncanonical_colon_join` | fail-closed | `NONCANONICAL_DERIVATION` | `source_hash` derived by colon-joining fields instead of JCS; recomputes under colon-join but not JCS, so honest implementations diverge and the trace is not portable |
| `unanchored_generator_claim` | fail-closed | `UNANCHORED_CLAIM` | Generator cites `chunk_id` absent from the retriever receipt — a claim with no traceable provenance |

## Why byte-determinism is the point

The "trace this claim to this span" check only holds for a verifier who recomputes **independently** — an auditor, a regulator, opposing counsel. If `source_hash` is derived by string concatenation, two honest implementations canonicalizing the same span produce different bytes and different hashes, and the trace stops being reproducible. JCS (RFC 8785) over the span object is what makes the hash evidence rather than a value only its author can reproduce. `noncanonical_colon_join` exists to make that failure explicit and machine-checkable.

## Verification

```
python3 verify.py
```

Stdlib only, deterministic (no wall-clock, no randomness, no network). Exit `0` if all vectors pass. The runner recomputes each `source_hash` under both JCS and the colon-joined form, so it can distinguish a non-canonical derivation from genuine content tampering.

A conformant verifier **MUST**:
1. Recompute every `source_hash` over the presented span under JCS before trusting a chunk.
2. Reject with `NONCANONICAL_DERIVATION` if the hash only recomputes under a non-JCS form.
3. Reject with `SOURCE_HASH_MISMATCH` if it recomputes under no form (content altered).
4. Reject with `UNANCHORED_CLAIM` if a generator claim cites a `chunk_id` not present in the retriever receipt.
