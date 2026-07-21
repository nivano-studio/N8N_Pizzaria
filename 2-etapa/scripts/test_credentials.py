import os
import json

print("Checking environment variables...")
supabase_url = os.environ.get("SUPABASE_URL")
supabase_key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or os.environ.get("SUPABASE_KEY")
openai_key = os.environ.get("OPENAI_API_KEY")

print("SUPABASE_URL in env:", "Found" if supabase_url else "Not found")
print("SUPABASE_KEY in env:", "Found" if supabase_key else "Not found")
print("OPENAI_API_KEY in env:", "Found" if openai_key else "Not found")

# Check if there are credential references in baseline metadata
baseline_meta = r"c:\Users\Administrator\Desktop\N8N_Pizzaria\0-etapa\audit_baseline_20260721\supabase\documents_metadata.json"
if os.path.exists(baseline_meta):
    with open(baseline_meta, encoding="utf-8") as f:
        meta = json.load(f)
        print(f"Loaded documents metadata baseline: {len(meta)} items")
