#!/usr/bin/env python3
"""Verify captured live idempotency evidence.

This script deliberately does not synthesize execution results. Run the workflow
in n8n first, export output/idempotency_proof.json, then execute this verifier.
"""
from __future__ import annotations

import json
from pathlib import Path

EVIDENCE = Path(__file__).resolve().parents[1] / "output" / "idempotency_proof.json"


def main() -> int:
    if not EVIDENCE.exists():
        raise SystemExit(f"Missing live evidence file: {EVIDENCE}")
    data = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    if data.get("simulated") is True:
        raise SystemExit("Refusing simulated evidence")
    run1 = data.get("run1", {})
    run2 = data.get("run2", {})
    checks = [
        run1.get("status") == "success",
        run1.get("gate", {}).get("already_exists") is False,
        run2.get("status") == "success",
        run2.get("gate", {}).get("already_exists") is True,
        run2.get("skip_status") == "SKIPPED_ALREADY_EXISTS",
        run2.get("ingestion_branch_executed") is False,
        data.get("idempotency_passed") is True,
    ]
    if not all(checks):
        raise SystemExit("Live idempotency evidence is incomplete or failed")
    print(json.dumps({"verified": True, "evidence": str(EVIDENCE)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

