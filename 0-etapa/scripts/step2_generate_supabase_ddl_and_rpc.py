"""Validate Supabase evidence collected from the live database.

This step deliberately never invents or overwrites DDL. Refresh evidence with
the Supabase MCP, then place the reviewed files under audit_baseline_20260721/
supabase before executing this validator.
"""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SUPABASE = ROOT / "audit_baseline_20260721" / "supabase"

REQUIRED = {
    "documents_schema.sql": ("extensions.vector(1536)", "extensions.vector_ip_ops", "ENABLE ROW LEVEL SECURITY"),
    "rpc_definitions.sql": ("public.hybrid_search", "public.match_documents", "SECURITY INVOKER", "SET search_path = public, extensions"),
    "supabase_schema_full.sql": ("CREATE TABLE public.documents", "public.match_documents", "extensions.vector_ip_ops"),
    "documents_metadata.json": ('"rows": 120', '"rls_enabled": true'),
    "catalog_evidence.json": ("match_documents", "hybrid_search"),
    "migration_20260721_rag_compatibility.sql": ("match_documents", "SET search_path = public, extensions"),
}


def main() -> None:
    missing_or_invalid: list[str] = []
    for filename, markers in REQUIRED.items():
        path = SUPABASE / filename
        if not path.exists():
            missing_or_invalid.append(f"missing: {filename}")
            continue
        content = path.read_text(encoding="utf-8")
        for marker in markers:
            if marker not in content:
                missing_or_invalid.append(f"{filename}: missing marker {marker!r}")

    if missing_or_invalid:
        raise SystemExit("Supabase evidence invalid:\n- " + "\n- ".join(missing_or_invalid))

    print("Supabase live evidence validated; no DDL was generated or overwritten.")


if __name__ == "__main__":
    main()
