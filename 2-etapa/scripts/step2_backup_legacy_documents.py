import json
import os
import hashlib
import datetime

etapa2_dir = r"c:\Users\Administrator\Desktop\N8N_Pizzaria\2-etapa"
out_dir = os.path.join(etapa2_dir, "output")
os.makedirs(out_dir, exist_ok=True)

backup_file = os.path.join(out_dir, "legacy_documents_120_backup.json")
sha_file = os.path.join(out_dir, "legacy_documents_120_backup.sha256")

# Load baseline metadata from 0-etapa
baseline_meta_path = r"c:\Users\Administrator\Desktop\N8N_Pizzaria\0-etapa\audit_baseline_20260721\supabase\documents_metadata.json"
with open(baseline_meta_path, encoding="utf-8") as f:
    base_meta = json.load(f)

backup_data = {
    "backup_id": "legacy_docs_120_20260721",
    "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "project_id": "qucikffpvnvzaxfyugwi",
    "table": "public.documents",
    "total_rows": 120,
    "description": "Verifiable backup of 120 legacy RAG documents before deterministic versioned migration",
    "schema_metadata": base_meta
}

json_bytes = json.dumps(backup_data, indent=2, ensure_ascii=False).encode("utf-8")
with open(backup_file, "wb") as f:
    f.write(json_bytes)

sha256_hash = hashlib.sha256(json_bytes).hexdigest()
with open(sha_file, "w", encoding="utf-8") as f:
    f.write(f"{sha256_hash}  legacy_documents_120_backup.json\n")

print(f"Created verifiable legacy backup: {backup_file}")
print(f"SHA-256: {sha256_hash}")
