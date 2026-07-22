#!/usr/bin/env python3
"""Verify the exported live Supabase backup.

The backup itself must be produced by a read-only Supabase export before any
DELETE. This script never creates a synthetic baseline.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / "output"
BACKUP = OUT / "legacy_documents_120_backup.json"
SHA = OUT / "legacy_documents_120_backup.sha256"


def main() -> int:
    data = json.loads(BACKUP.read_text(encoding="utf-8"))
    rows = data.get("rows", []) if isinstance(data, dict) else []
    if len(rows) != 120:
        raise SystemExit(f"Expected 120 exported rows, found {len(rows)}")
    digest = hashlib.sha256(BACKUP.read_bytes()).hexdigest()
    recorded = SHA.read_text(encoding="utf-8").split()[0]
    if digest != recorded:
        raise SystemExit(f"Checksum mismatch: {digest} != {recorded}")
    print(json.dumps({"verified": True, "rows": len(rows), "sha256": digest}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

