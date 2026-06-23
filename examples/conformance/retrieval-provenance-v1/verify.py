#!/usr/bin/env python3
"""Conformance runner for retrieval-provenance-v1 vectors.

Per-chunk retrieval provenance under action-ref-v1: the retriever receipt carries
a retrieved_chunks array, each chunk a span (doc_id, chunk_id, page, bbox, text)
plus a source_hash. A conformant trace lets an independent verifier map every
generator claim back to a specific span. Each fail-closed vector breaks that
property and MUST be rejected with the correct error code.

Deterministic: stdlib only, no wall-clock, no randomness, no network.

Usage: python3 verify.py
Exit codes: 0 all vectors pass, 1 any failure.
"""

import hashlib
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
SPAN_FIELDS = ("bbox", "chunk_id", "doc_id", "page", "text")


def jcs(obj):
    return json.dumps(obj, separators=(",", ":"), sort_keys=True, ensure_ascii=False)


def sha256_hex(s):
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def span_of(chunk):
    return {k: chunk[k] for k in SPAN_FIELDS}


def source_hash_jcs(chunk):
    return "sha256:" + sha256_hex(jcs(span_of(chunk)))


def source_hash_colon(chunk):
    s = span_of(chunk)
    return "sha256:" + sha256_hex(
        "%s:%s:%s:%s:%s" % (s["doc_id"], s["chunk_id"], s["page"], s["bbox"], s["text"]))


def check_retrieval_provenance(vector):
    """Returns (ok, code). ok=True means the trace is verifiable end to end.

    Order of checks mirrors how a verifier fails closed:
      1. each chunk source_hash must recompute under JCS;
         if it recomputes under colon-join instead -> NONCANONICAL_DERIVATION;
         if under neither -> SOURCE_HASH_MISMATCH.
      2. every generator claim must cite a chunk_id present in the receipt
         -> UNANCHORED_CLAIM.
    """
    chunks = vector["receipt"].get("retrieved_chunks", [])
    present_ids = {c["chunk_id"] for c in chunks}

    for c in chunks:
        embedded = c["source_hash"]
        if embedded != source_hash_jcs(c):
            if embedded == source_hash_colon(c):
                return False, "NONCANONICAL_DERIVATION"
            return False, "SOURCE_HASH_MISMATCH"

    for claim in vector["generator_output"].get("claims", []):
        if claim.get("cited_chunk_id") not in present_ids:
            return False, "UNANCHORED_CLAIM"

    return True, "trace verifiable: every claim maps to a JCS-canonical span"


def main():
    fixture_path = HERE / "retrieval-provenance-v1.fixture.json"
    with open(fixture_path, encoding="utf-8") as f:
        fixture = json.load(f)

    failures = 0
    vectors = fixture["vectors"]

    for v in vectors:
        name = v["name"]
        ok, code = check_retrieval_provenance(v)
        expected = v["expected_result"]

        if expected == "pass":
            if ok:
                print("PASS  %-32s %s" % (name, code))
            else:
                failures += 1
                print("FAIL  %-32s verifier rejected conformant vector: %s" % (name, code))
        elif expected == "fail-closed":
            want = v["expected_error_code"]
            if ok:
                failures += 1
                print("FAIL  %-32s verifier accepted — expected fail-closed (%s)" % (name, want))
            elif code != want:
                failures += 1
                print("FAIL  %-32s wrong error code: got %s expected %s" % (name, code, want))
            else:
                print("PASS  %-32s fail-closed (%s)" % (name, code))
        else:
            failures += 1
            print("FAIL  %-32s unknown expected_result: %s" % (name, expected))

    print()
    if failures:
        print("%d check(s) failed" % failures)
        return 1
    print("all %d vectors pass" % len(vectors))
    return 0


if __name__ == "__main__":
    sys.exit(main())
