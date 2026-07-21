import os
import re
import json

base_dir = r"c:\Users\Administrator\Desktop\N8N_Pizzaria\0-etapa"

patterns = [
    (re.compile(r'sk-[a-zA-Z0-9T3BlbkFJ]{20,}'), '[REDACTED_SECRET]'),
    (re.compile(r'sk_live_[a-zA-Z0-9]{20,}'), '[REDACTED_SECRET]'),
    (re.compile(r'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9\.[a-zA-Z0-9_-]{30,}\.[a-zA-Z0-9_-]{30,}'), '[REDACTED_SECRET]'),
    (re.compile(r'Bearer\s+[a-zA-Z0-9_\-\.]{20,}'), 'Bearer [REDACTED_SECRET]'),
]

affected_files = []

def sanitize_content(content):
    modified = False
    for pat, repl in patterns:
        if pat.search(content):
            content = pat.sub(repl, content)
            modified = True
    return content, modified

print("=== STEP 5: SANITIZING SECRETS RECURSIVELY IN 0-ETAPA ===")

for root, dirs, files in os.walk(base_dir):
    for f in files:
        if f == "checksums.sha256":
            continue
        ext = os.path.splitext(f)[1].lower()
        if ext in [".json", ".md", ".py", ".ts", ".txt"]:
            f_path = os.path.join(root, f)
            try:
                with open(f_path, "r", encoding="utf-8") as file:
                    text = file.read()
                
                # If json, handle specific secret field names as well
                if ext == ".json":
                    try:
                        obj = json.loads(text)
                        def clean_obj(o):
                            if isinstance(o, dict):
                                return {k: "[REDACTED_SECRET]" if k in ["ElevenLabsAPI-KEY", "openia_api_key", "vector_store_id"] and isinstance(v, str) and not v.startswith("--SUA") else clean_obj(v) for k, v in o.items()}
                            elif isinstance(o, list):
                                return [clean_obj(item) for item in o]
                            elif isinstance(o, str):
                                v = o
                                for pat, repl in patterns:
                                    v = pat.sub(repl, v)
                                return v
                            else:
                                return o
                        cleaned = clean_obj(obj)
                        new_text = json.dumps(cleaned, indent=2, ensure_ascii=False)
                        if new_text != text:
                            with open(f_path, "w", encoding="utf-8") as out:
                                out.write(new_text)
                            rel_p = os.path.relpath(f_path, base_dir).replace("\\", "/")
                            affected_files.append(rel_p)
                            continue
                    except Exception:
                        pass
                        
                new_text, modified = sanitize_content(text)
                if modified:
                    with open(f_path, "w", encoding="utf-8") as out:
                        out.write(new_text)
                    rel_p = os.path.relpath(f_path, base_dir).replace("\\", "/")
                    affected_files.append(rel_p)
            except Exception as e:
                print(f"Error processing {f_path}: {e}")

print(f"Sanitization finished. Total affected files: {len(affected_files)}")
for f in sorted(set(affected_files)):
    print(f" - {f}")
