import os
import re
import json

base_dir = r"c:\Users\Administrator\Desktop\N8N_Pizzaria\0-etapa"

secret_patterns = [
    (re.compile(r'sb_[A-Za-z0-9_-]{15,}'), '[REDACTED_SECRET]'),
    (re.compile(r'sb_publishable_[A-Za-z0-9_-]{15,}'), '[REDACTED_SECRET]'),
    (re.compile(r'Bearer\s+[A-Za-z0-9._-]{15,}'), 'Bearer [REDACTED_SECRET]'),
    (re.compile(r'sk-[A-Za-z0-9_-]{15,}'), '[REDACTED_SECRET]'),
    (re.compile(r'sk_live_[A-Za-z0-9_-]{15,}'), '[REDACTED_SECRET]'),
    (re.compile(r'eyJ[A-Za-z0-9_-]{15,}\.[A-Za-z0-9_-]{15,}\.[A-Za-z0-9_-]{15,}'), '[REDACTED_SECRET]'),
]

affected_files = []

def sanitize_str(s):
    val = s
    for pat, repl in secret_patterns:
        val = pat.sub(repl, val)
    return val

def sanitize_json_obj(obj):
    if isinstance(obj, dict):
        new_dict = {}
        for k, v in obj.items():
            if k in ["ElevenLabsAPI-KEY", "openia_api_key", "vector_store_id"] and isinstance(v, str) and not v.startswith("[REDACTED"):
                new_dict[k] = "[REDACTED_SECRET]"
            else:
                new_dict[k] = sanitize_json_obj(v)
        return new_dict
    elif isinstance(obj, list):
        return [sanitize_json_obj(item) for item in obj]
    elif isinstance(obj, str):
        return sanitize_str(obj)
    else:
        return obj

print("=== STEP 1: SANITIZING SECRETS COMPREHENSIVELY IN 0-ETAPA ===")

for root, dirs, files in os.walk(base_dir):
    for f in files:
        if f == "checksums.sha256":
            continue
        ext = os.path.splitext(f)[1].lower()
        if ext in [".json", ".md", ".py", ".ts", ".txt", ".sql"]:
            f_path = os.path.join(root, f)
            try:
                with open(f_path, "r", encoding="utf-8") as file:
                    content = file.read()
                
                if ext == ".json":
                    try:
                        data = json.loads(content)
                        sanitized_data = sanitize_json_obj(data)
                        new_content = json.dumps(sanitized_data, indent=2, ensure_ascii=False)
                    except Exception:
                        new_content, _ = sanitize_str(content)
                else:
                    new_content = sanitize_str(content)
                    
                if new_content != content:
                    with open(f_path, "w", encoding="utf-8") as out:
                        out.write(new_content)
                    rel_p = os.path.relpath(f_path, base_dir).replace("\\", "/")
                    affected_files.append(rel_p)
            except Exception as e:
                print(f"Error processing {f_path}: {e}")

print(f"Sanitization complete. Total affected files: {len(affected_files)}")
for f in sorted(set(affected_files)):
    print(f" - {f}")
