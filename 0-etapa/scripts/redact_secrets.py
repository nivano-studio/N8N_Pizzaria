import json
import os
import re

dirs_to_sanitize = [
    r"c:\Users\Administrator\Desktop\N8N_Pizzaria\0-etapa\audit_baseline_20260721",
    r"c:\Users\Administrator\Desktop\N8N_Pizzaria\audit_baseline_20260721"
]

secret_patterns = [
    re.compile(r'sk-[a-zA-Z0-9T3BlbkFJ]{20,}'), # OpenAI secret key
    re.compile(r'sk_live_[a-zA-Z0-9]{20,}'),
    re.compile(r'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9\.[a-zA-Z0-9_-]{30,}\.[a-zA-Z0-9_-]{30,}'), # JWT / Supabase anon/service role key
]

def sanitize_obj(obj):
    if isinstance(obj, str):
        val = obj
        for pat in secret_patterns:
            val = pat.sub("[REDACTED_SECRET]", val)
        return val
    elif isinstance(obj, dict):
        new_dict = {}
        for k, v in obj.items():
            if k in ["ElevenLabsAPI-KEY", "openia_api_key", "vector_store_id"] and isinstance(v, str) and not v.startswith("--SUA"):
                new_dict[k] = "[REDACTED_SECRET]"
            else:
                new_dict[k] = sanitize_obj(v)
        return new_dict
    elif isinstance(obj, list):
        return [sanitize_obj(elem) for elem in obj]
    else:
        return obj

sanitized_files = 0

for base_dir in dirs_to_sanitize:
    if not os.path.exists(base_dir):
        continue
    for root, dirs, files in os.walk(base_dir):
        for f_name in files:
            if f_name.endswith(".json"):
                f_path = os.path.join(root, f_name)
                try:
                    data = json.load(open(f_path, encoding="utf-8"))
                    sanitized_data = sanitize_obj(data)
                    with open(f_path, "w", encoding="utf-8") as out_f:
                        json.dump(sanitized_data, out_f, indent=2, ensure_ascii=False)
                    sanitized_files += 1
                except Exception as e:
                    print(f"Error sanitizing {f_path}: {e}")

print(f"Sanitized {sanitized_files} JSON files across audit directories.")
