#!/usr/bin/env python3
"""Z-QEA receipt verifier v2.0.0 — seal check + post-quantum signature check.

Two layers verified (see zqea_pq.py):
  1. selo_sha3_256  — SHA3-256 canonical seal recomputation (v1-compatible).
  2. assinatura_pq  — ML-DSA-44 (FIPS 204) signature against the public key
                      embedded in the receipt. Receipts without it are
                      reported as LEGACY_V1 (v1 receipts still pass the seal
                      check; use --strict-pq to require the PQ layer).
When the entropy block is present, its provenance (IBM Quantum job id,
backend, pool hash) is displayed so the receipt's quantum origin is auditable.

Exit codes: 0 = verified, 1 = broken/invalid, 2 = usage.
"""
import sys, os, json, hashlib
from zqea_pq import verify_signature, canonical

def verify(receipt):
    if not isinstance(receipt, dict):
        return False, None, "receipt is not a JSON object"
    declared = receipt.get("selo_sha3_256")
    if not declared:
        return False, None, "receipt has no selo_sha3_256"
    payload = {k: v for k, v in receipt.items() if k != "selo_sha3_256"}
    recomputed = hashlib.sha3_256(canonical(payload).encode()).hexdigest()
    return declared == recomputed, recomputed, "ok" if declared == recomputed else "seal mismatch"

def main():
    if len(sys.argv) < 2:
        print("usage: zqea_verify.py <receipt.json> [--strict-pq]")
        return 2
    strict = "--strict-pq" in sys.argv[3:] if len(sys.argv) > 2 else False
    try:
        receipt = json.load(open(sys.argv[1]))
    except Exception as e:
        print("Z-QEA: RECEIPT MALFORMED —", e)
        return 1
    ok, recomputed, why = verify(receipt)
    pq_status, pq_detail = verify_signature(receipt)
    ent = receipt.get("entropia_quantica") or {}
    print("camada 1 — selo SHA3-256:")
    print("  selo declarado  :", receipt.get("selo_sha3_256"))
    print("  selo recalculado:", recomputed)
    print("  ", "SELO ÍNTEGRO" if ok else "SELO ROMPIDO (%s)" % why)
    print("camada 2 — assinatura pós-quântica:")
    print("  ", pq_status, "-", pq_detail)
    if ent.get("job_id"):
        print("entropia quântica atestada: job", ent.get("job_id"), "(", ent.get("backend"), ") | pool", str(ent.get("pool_sha3_256"))[:16] + "…")
    overall = ok and (pq_status == "PQ_OK" or (pq_status == "LEGACY_V1" and not strict))
    if pq_status == "LEGACY_V1" and not strict:
        print("Z-QEA: VERIFICADO (v1 legado — sem assinatura pós-quântica)")
    else:
        print("Z-QEA: VERIFICADO — selo íntegro + ML-DSA-44 válido" if overall else "Z-QEA: RECUSADO — %s / %s" % (why, pq_detail))
    out = os.environ.get("GITHUB_OUTPUT")
    if out:
        with open(out, "a") as f:
            f.write("status=" + ("VERIFICADO" if overall else "RECUSADO") + "\n")
            f.write("pq=" + pq_status + "\n")
            f.write("seal=" + str(recomputed) + "\n")
    return 0 if overall else 1

if __name__ == "__main__":
    sys.exit(main())
