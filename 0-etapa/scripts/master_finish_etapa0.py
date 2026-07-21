import os
import sys
import json
import hashlib
import subprocess

etapa0_dir = r"c:\Users\Administrator\Desktop\N8N_Pizzaria\0-etapa"
audit_dir = os.path.join(etapa0_dir, "audit_baseline_20260721")
scripts_dir = os.path.join(etapa0_dir, "scripts")

print("=== STARTING MASTER SEQUENTIAL EXECUTION FOR ETAPA 0 ===")

# Step 1: Sanitize secrets
print("\n--- 1. Sanitizing Secrets ---")
subprocess.run([sys.executable, os.path.join(scripts_dir, "step1_sanitize_secrets_v2.py")], check=True)

# Step 2: Generate Supabase DDL and RPC SQL files
print("\n--- 2. Generating Supabase DDL & RPC SQL ---")
subprocess.run([sys.executable, os.path.join(scripts_dir, "step2_generate_supabase_ddl_and_rpc.py")], check=True)

# Step 3: Run comprehensive validators
print("\n--- 3. Running Comprehensive Validators ---")
subprocess.run([sys.executable, os.path.join(scripts_dir, "step8_9_validate_and_checksum.py")], check=True)

# Step 4: Generate ETAPA0_STATUS_FINAL.md
print("\n--- 4. Generating Final Status Report ---")
subprocess.run([sys.executable, os.path.join(scripts_dir, "step10_generate_final_status_report.py")], check=True)

# Step 5: Final Checksums Generation (AFTER report generation)
print("\n--- 5. Generating Final SHA-256 Checksums Manifest ---")
files_to_hash = []
for root, dirs, files in os.walk(etapa0_dir):
    if ".git" in root or "node_modules" in root or ".gemini" in root:
        continue
    for file in files:
        if file == "checksums.sha256":
            continue
        full_path = os.path.join(root, file)
        rel_path = os.path.relpath(full_path, etapa0_dir).replace("\\", "/")
        files_to_hash.append((full_path, rel_path))

files_to_hash.sort(key=lambda x: x[1])

checksum_file = os.path.join(audit_dir, "checksums.sha256")
lines = []
for full_path, rel_path in files_to_hash:
    with open(full_path, "rb") as f:
        h = hashlib.sha256(f.read()).hexdigest()
    lines.append(f"{h}  {rel_path}")

checksum_content = "\n".join(lines) + "\n"
with open(checksum_file, "w", encoding="utf-8") as f:
    f.write(checksum_content)

print(f"Generated {len(lines)} checksum entries in {checksum_file}")

# Step 6: Verify Checksums Manifest
print("\n--- 6. Verifying Checksums Manifest ---")
manifest_lines = open(checksum_file, encoding="utf-8").read().strip().split("\n")
missing_files = []
divergent_files = []

for line in manifest_lines:
    if not line.strip():
        continue
    parts = line.strip().split("  ", 1)
    if len(parts) != 2:
        continue
    expected_hash, rel_p = parts
    full_p = os.path.join(etapa0_dir, rel_p)
    if not os.path.exists(full_p):
        missing_files.append(rel_p)
    else:
        with open(full_p, "rb") as f:
            actual_hash = hashlib.sha256(f.read()).hexdigest()
        if actual_hash != expected_hash:
            divergent_files.append(rel_p)

print(f"Manifest Verification Result: Missing: {len(missing_files)}, Divergent: {len(divergent_files)}")
assert len(missing_files) == 0, f"Missing files found in manifest: {missing_files}"
assert len(divergent_files) == 0, f"Divergent files found in manifest: {divergent_files}"

print("\n=== MASTER SEQUENTIAL EXECUTION PASSED 100% CLEANLY ===")
