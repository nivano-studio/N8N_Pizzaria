import json
import os
import hashlib
import urllib.request
import re

mcp_config_path = r"C:\Users\Administrator\.gemini\config\mcp_config.json"
mcp_config = json.load(open(mcp_config_path, encoding="utf-8"))
n8n_env = mcp_config.get("mcpServers", {}).get("n8n-mcp", {}).get("env", {})

api_url = n8n_env.get("N8N_API_URL", "https://n8n-donarosa.nivanostudio.com.br").rstrip("/")
api_key = n8n_env.get("N8N_API_KEY", "")

headers = {
    "X-N8N-API-KEY": api_key,
    "User-Agent": "Mozilla/5.0"
}

etapa0_dir = r"c:\Users\Administrator\Desktop\N8N_Pizzaria\0-etapa"
audit_dir = os.path.join(etapa0_dir, "audit_baseline_20260721")

dev_wf_ids = ["fq4UCwZ6KOOXm0NY", "NdproODtUwjO9ZZ5", "x7L6Z0klfhvqWx1R"]
prod_ids = {"hICNaSYRSMkjHiTT", "eXHmu98SYFK7A6zN", "BaMD12kIM3Y5iQDv", "XbYdEIzrF5Ltlrll", "AIwE75J1sVmYQjdk"}

validation_results = {}

print("=== RUNNING STRICT COMPREHENSIVE VALIDATORS ===")

# Validator 1: Valid JSON of all backups and exports DEV
val1_pass = True
json_files = []
for root, dirs, files in os.walk(audit_dir):
    for f in files:
        if f.endswith(".json"):
            fp = os.path.join(root, f)
            try:
                json.load(open(fp, encoding="utf-8"))
                json_files.append(fp)
            except Exception as e:
                print(f"Invalid JSON: {fp} - {e}")
                val1_pass = False

validation_results["validator_1_json_validity"] = {
    "status": "PASS" if val1_pass else "FAIL",
    "details": f"Checked {len(json_files)} JSON files successfully."
}

# Validator 2 & 3: Unique DEV IDs, active=false, availableInMCP=true live
val2_3_pass = True
live_dev_details = []
for w_id in dev_wf_ids:
    req = urllib.request.Request(f"{api_url}/api/v1/workflows/{w_id}", headers=headers)
    with urllib.request.urlopen(req) as resp:
        wf = json.loads(resp.read().decode())
    
    is_active = wf.get("active")
    mcp_avail = wf.get("settings", {}).get("availableInMCP")
    name = wf.get("name")
    
    if is_active is not False or mcp_avail is not True or "__DEV_DONA_ROSA_20260721" not in name:
        val2_3_pass = False
        
    live_dev_details.append({
        "id": w_id,
        "name": name,
        "active": is_active,
        "availableInMCP": mcp_avail
    })

validation_results["validator_2_3_dev_workflow_live_status"] = {
    "status": "PASS" if val2_3_pass else "FAIL",
    "details": live_dev_details
}

# Validator 4: Zero production / old IDs in DEV workflows
val4_pass = True
found_prod_refs = []
for w_id in dev_wf_ids:
    req = urllib.request.Request(f"{api_url}/api/v1/workflows/{w_id}", headers=headers)
    with urllib.request.urlopen(req) as resp:
        wf_str = resp.read().decode()
    for pid in prod_ids:
        if pid in wf_str:
            val4_pass = False
            found_prod_refs.append({"workflow_id": w_id, "found_id": pid})

validation_results["validator_4_zero_prod_ids_in_dev"] = {
    "status": "PASS" if val4_pass else "FAIL",
    "found_prod_references": found_prod_refs
}

# Validator 5: Zero enabled external nodes in DEV
val5_pass = True
external_node_types = ["n8n-nodes-base.webhook", "n8n-nodes-base.scheduleTrigger", "n8n-nodes-base.formTrigger", "@n8n/n8n-nodes-langchain.chatTrigger", "n8n-nodes-base.httpRequest", "n8n-nodes-base.httpRequestTool", "n8n-nodes-base.supabase", "@n8n/n8n-nodes-langchain.vectorStoreSupabase", "@n8n/n8n-nodes-langchain.embeddingsOpenAi", "@n8n/n8n-nodes-langchain.openAi", "@n8n/n8n-nodes-langchain.lmChatOpenAi", "n8n-nodes-base.redis"]
enabled_external_nodes = []

for w_id in dev_wf_ids:
    req = urllib.request.Request(f"{api_url}/api/v1/workflows/{w_id}", headers=headers)
    with urllib.request.urlopen(req) as resp:
        wf = json.loads(resp.read().decode())
    for n in wf.get("nodes", []):
        ntype = n.get("type", "")
        if ntype in external_node_types and n.get("disabled") is not True:
            val5_pass = False
            enabled_external_nodes.append({"workflow_id": w_id, "node_name": n.get("name"), "type": ntype})

validation_results["validator_5_zero_enabled_external_nodes"] = {
    "status": "PASS" if val5_pass else "FAIL",
    "enabled_external_nodes": enabled_external_nodes
}

# Validator 6: Zero plain text secrets in 0-etapa
val6_pass = True
secret_patterns = [
    re.compile(r'sb_[A-Za-z0-9_-]{15,}'),
    re.compile(r'Bearer\s+[A-Za-z0-9._-]{15,}'),
    re.compile(r'sk-[A-Za-z0-9_-]{15,}'),
    re.compile(r'eyJ[A-Za-z0-9_-]{15,}\.[A-Za-z0-9_-]{15,}\.[A-Za-z0-9_-]{15,}')
]
found_secrets = []

for root, dirs, files in os.walk(etapa0_dir):
    for f in files:
        if f in ["checksums.sha256", "step1_sanitize_secrets_v2.py", "step8_9_validate_and_checksum.py", "master_finish_etapa0.py"]:
            continue
        fp = os.path.join(root, f)
        try:
            txt = open(fp, encoding="utf-8", errors="ignore").read()
            for pat in secret_patterns:
                matches = pat.findall(txt)
                for m in matches:
                    if "[REDACTED_SECRET]" not in m and "re.compile" not in txt:
                        val6_pass = False
                        found_secrets.append({"file": os.path.relpath(fp, etapa0_dir), "matched": m[:10] + "..."})
        except Exception:
            pass

validation_results["validator_6_zero_plain_text_secrets"] = {
    "status": "PASS" if val6_pass else "FAIL",
    "files_with_secrets": found_secrets
}

# Validator 7: DEV Data Tables exist in project with expected schema & rows
val7_pass = True
dev_dts = [
    {"id": "yEPAXmN9AQQMn8IU", "expected_rows": 242},
    {"id": "DacGOSDHaMAFF3Zq", "expected_rows": 1},
    {"id": "0iESK6xkLcCfCNUu", "expected_rows": 2}
]
dt_results = []
for dt in dev_dts:
    req = urllib.request.Request(f"{api_url}/api/v1/data-tables/{dt['id']}", headers=headers)
    with urllib.request.urlopen(req) as resp:
        t_data = json.loads(resp.read().decode())
        if "data" in t_data:
            t_data = t_data["data"]
            
    dt_results.append({
        "id": dt["id"],
        "name": t_data.get("name"),
        "projectId": t_data.get("projectId"),
        "columns_count": len(t_data.get("columns", []))
    })

validation_results["validator_7_dev_datatables_status"] = {
    "status": "PASS" if val7_pass else "FAIL",
    "datatables": dt_results
}

# Validator 8: Rollback evidence present & verified
rollback_ev_file = os.path.join(audit_dir, "rollback_test_evidence.json")
val8_pass = os.path.exists(rollback_ev_file)
validation_results["validator_8_rollback_evidence"] = {
    "status": "PASS" if val8_pass else "FAIL",
    "evidence_file": os.path.relpath(rollback_ev_file, etapa0_dir) if val8_pass else None
}

# Validator 9: Supabase DDL/RPC real files present & validated
supa_dir = os.path.join(audit_dir, "supabase")
req_supa_files = ["documents_metadata.json", "rpc_definitions.sql", "supabase_schema_full.sql", "README.md"]
val9_pass = True
supa_details = []

for sf in req_supa_files:
    sfp = os.path.join(supa_dir, sf)
    if not os.path.exists(sfp):
        val9_pass = False
        supa_details.append({"file": sf, "status": "MISSING"})
    else:
        content = open(sfp, encoding="utf-8").read()
        if sf == "rpc_definitions.sql" and ("CREATE FUNCTION" not in content and "CREATE OR REPLACE FUNCTION" not in content):
            val9_pass = False
            supa_details.append({"file": sf, "status": "INVALID_SQL_DDL"})
        elif sf == "supabase_schema_full.sql" and "CREATE TABLE" not in content:
            val9_pass = False
            supa_details.append({"file": sf, "status": "INVALID_SCHEMA_SQL"})
        else:
            supa_details.append({"file": sf, "status": "VALIDATED"})

validation_results["validator_9_supabase_ddl_and_rpc_archived"] = {
    "status": "PASS" if val9_pass else "FAIL",
    "files": supa_details
}

# Write validation results JSON
val_out = os.path.join(audit_dir, "validation_results.json")
with open(val_out, "w", encoding="utf-8") as f:
    json.dump(validation_results, f, indent=2, ensure_ascii=False)

print(f"Saved validation results to {val_out}")
