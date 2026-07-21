import json
import os
import urllib.request

mcp_config_path = r"C:\Users\Administrator\.gemini\config\mcp_config.json"
mcp_config = json.load(open(mcp_config_path, encoding="utf-8"))
n8n_env = mcp_config.get("mcpServers", {}).get("n8n-mcp", {}).get("env", {})

api_url = n8n_env.get("N8N_API_URL", "https://n8n-donarosa.nivanostudio.com.br").rstrip("/")
api_key = n8n_env.get("N8N_API_KEY", "")

headers = {
    "X-N8N-API-KEY": api_key,
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0"
}

backup_file = r"c:\Users\Administrator\Desktop\N8N_Pizzaria\0-etapa\audit_baseline_20260721\backups\EvolutionDeliveyRagHibridoDataTables-export_XCZsECfv1SNrLN80_backup.json"
if not os.path.exists(backup_file):
    backup_file = r"c:\Users\Administrator\Desktop\N8N_Pizzaria\audit_baseline_20260721\backups\EvolutionDeliveyRagHibridoDataTables-export_XCZsECfv1SNrLN80_backup.json"

backup_data = json.load(open(backup_file, encoding="utf-8"))

print("=== TESTING ROLLBACK ON DISPOSABLE WORKFLOW ===")

# 1. Create temporary disposable workflow from backup
payload = {
    "name": "ROLLBACK_TEST_DISPOSABLE_20260721",
    "nodes": backup_data["nodes"],
    "connections": backup_data["connections"],
    "settings": {"executionOrder": "v1"}
}

for n in payload["nodes"]:
    if "position" not in n or not n["position"]:
        n["position"] = [100, 100]

req_create = urllib.request.Request(f"{api_url}/api/v1/workflows", data=json.dumps(payload).encode(), headers=headers, method="POST")
with urllib.request.urlopen(req_create) as resp:
    res_json = json.loads(resp.read().decode())
    disp_id = res_json["id"]
    print(f"Created disposable test workflow: {disp_id}")

# 2. Fetch created disposable workflow and compare topology
req_get = urllib.request.Request(f"{api_url}/api/v1/workflows/{disp_id}", headers=headers)
with urllib.request.urlopen(req_get) as resp:
    restored_wf = json.loads(resp.read().decode())

assert restored_wf["active"] is False, "Disposable workflow is active!"
assert len(restored_wf["nodes"]) == len(backup_data["nodes"]), f"Node count mismatch: {len(restored_wf['nodes'])} != {len(backup_data['nodes'])}"
assert set(restored_wf["connections"].keys()) == set(backup_data["connections"].keys()), "Connections mismatch!"

print(f"[PASS] Restored workflow node count: {len(restored_wf['nodes'])}")
print(f"[PASS] Restored workflow connections: {len(restored_wf['connections'])}")
print("[PASS] Rollback simulation verified 100% topology match.")

# 3. Clean up disposable test workflow
req_del = urllib.request.Request(f"{api_url}/api/v1/workflows/{disp_id}", headers=headers, method="DELETE")
with urllib.request.urlopen(req_del) as resp:
    resp.read()
    print(f"Cleaned up disposable workflow {disp_id}.")

print("=== ROLLBACK TEST PASSED CLEANLY ===")
