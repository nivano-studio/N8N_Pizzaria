import os
import hashlib

base_dir = r"c:\Users\Administrator\Desktop\N8N_Pizzaria"
etapa0_dir = os.path.join(base_dir, "0-etapa")
audit_dir = os.path.join(etapa0_dir, "audit_baseline_20260721")
os.makedirs(audit_dir, exist_ok=True)

files_to_hash = []

for root, dirs, files in os.walk(base_dir):
    if ".git" in root or "node_modules" in root or ".gemini" in root:
        continue
    for file in files:
        if file == "checksums.sha256":
            continue
        full_path = os.path.join(root, file)
        rel_path = os.path.relpath(full_path, base_dir).replace("\\", "/")
        files_to_hash.append((full_path, rel_path))

files_to_hash.sort(key=lambda x: x[1])

checksum_file1 = os.path.join(audit_dir, "checksums.sha256")
checksum_file2 = os.path.join(base_dir, "audit_baseline_20260721", "checksums.sha256")

lines = []

for full_path, rel_path in files_to_hash:
    try:
        with open(full_path, "rb") as f:
            h = hashlib.sha256(f.read()).hexdigest()
        lines.append(f"{h}  {rel_path}")
    except Exception as e:
        print(f"Error hashing {rel_path}: {e}")

checksum_content = "\n".join(lines) + "\n"

with open(checksum_file1, "w", encoding="utf-8") as f:
    f.write(checksum_content)

if os.path.exists(os.path.dirname(checksum_file2)):
    with open(checksum_file2, "w", encoding="utf-8") as f:
        f.write(checksum_content)

print(f"Generated {len(lines)} checksum entries in {checksum_file1}")
