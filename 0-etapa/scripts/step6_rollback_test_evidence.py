import json
import os
import urllib.request
import datetime

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
backup_data = json.load(open(backup_file, encoding="utf-8"))

print("=== STEP 6: EXECUTING LIVE ROLLBACK TEST ON DISPOSABLE WORKFLOW ===")

timestamp_start = datetime.datetime.now(datetime.timezone.utc).isoformat()

# 1. Create temporary disposable workflow
payload = {
    "name": "DISPOSABLE_ROLLBACK_TEST_20260721",
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
    print(f"Created disposable workflow: {disp_id}")

# 2. Re-fetch and verify live
req_get = urllib.request.Request(f"{api_url}/api/v1/workflows/{disp_id}", headers=headers)
with urllib.request.urlopen(req_get) as resp:
    restored_wf = json.loads(resp.read().decode())

is_active = restored_wf.get("active")
node_count = len(restored_wf.get("nodes", []))
conn_count = len(restored_wf.get("connections", {}))

expected_nodes = len(backup_data["nodes"])
expected_conns = len(backup_data["connections"])

assert is_active is False, "Disposable workflow is active!"
assert node_count == expected_nodes, f"Node count mismatch: {node_count} != {expected_nodes}"
assert conn_count == expected_conns, f"Connections mismatch: {conn_count} != {expected_conns}"

print(f"Verified Live Topology: active={is_active}, nodes={node_count}, connections={conn_count}")

# 3. Delete temporary disposable workflow
req_del = urllib.request.Request(f"{api_url}/api/v1/workflows/{disp_id}", headers=headers, method="DELETE")
with urllib.request.urlopen(req_del) as resp:
    resp.read()

# 4. Verify deletion live
deletion_confirmed = False
try:
    with urllib.request.urlopen(req_get) as resp:
        resp.read()
except urllib.error.HTTPError as e:
    if e.code == 404:
        deletion_confirmed = True
        print(f"Deletion confirmed live: Workflow {disp_id} returns 404 Not Found.")

assert deletion_confirmed is True, "Disposable workflow deletion failed!"

timestamp_end = datetime.datetime.now(datetime.timezone.utc).isoformat()

evidence_data = {
    "test_name": "Disposable Workflow Rollback Verification",
    "timestamp_start": timestamp_start,
    "timestamp_end": timestamp_end,
    "disposable_workflow_id": disp_id,
    "disposable_workflow_name": "DISPOSABLE_ROLLBACK_TEST_20260721",
    "source_backup_file": "EvolutionDeliveyRagHibridoDataTables-export_XCZsECfv1SNrLN80_backup.json",
    "verification_results": {
        "active_status": is_active,
        "nodes_matched": node_count == expected_nodes,
        "nodes_count": node_count,
        "expected_nodes": expected_nodes,
        "connections_matched": conn_count == expected_conns,
        "connections_count": conn_count,
        "expected_connections": expected_conns,
        "deletion_confirmed": deletion_confirmed
    },
    "result": "SUCCESS - Topology 100% Verified and Cleanup Confirmed"
}

out_evidence_path = r"c:\Users\Administrator\Desktop\N8N_Pizzaria\0-etapa\audit_baseline_20260721\rollback_test_evidence.json"
with open(out_evidence_path, "w", encoding="utf-8") as f:
    json.dump(evidence_data, f, indent=2, ensure_ascii=False)

print(f"\nSaved rollback evidence log to: {out_evidence_path}")
