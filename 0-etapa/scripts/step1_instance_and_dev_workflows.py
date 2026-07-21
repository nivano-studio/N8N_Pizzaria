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
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

print("=== STEP 1: INSTANCE & LIVE DEV WORKFLOW CONFIRMATION ===")

# 1. Health Check
req_health = urllib.request.Request(f"{api_url}/healthz", headers={"User-Agent": "Mozilla/5.0"})
try:
    with urllib.request.urlopen(req_health) as resp:
        health_status = resp.status
        print(f"Healthz check: {health_status} OK")
except Exception as e:
    print(f"Healthz check response: {e}")

# 2. Get User & Project info
req_user = urllib.request.Request(f"{api_url}/api/v1/users/me", headers=headers)
user_info = {}
try:
    with urllib.request.urlopen(req_user) as resp:
        user_info = json.loads(resp.read().decode())
        print(f"User: {user_info.get('email')} (ID: {user_info.get('id')})")
except Exception as e:
    print(f"User info: {e}")

# 3. Workflows verification & availableInMCP update
dev_wfs = [
    {"name": "ImportPdfToTable__DEV_DONA_ROSA_20260721", "id": "fq4UCwZ6KOOXm0NY"},
    {"name": "ToolsProductsDataTableToRag__DEV_DONA_ROSA_20260721", "id": "NdproODtUwjO9ZZ5"},
    {"name": "EvolutionDeliveyRagHibridoDataTables-export__DEV_DONA_ROSA_20260721", "id": "x7L6Z0klfhvqWx1R"}
]

confirmed_dev_wfs = []

for dev in dev_wfs:
    w_id = dev["id"]
    req_wf = urllib.request.Request(f"{api_url}/api/v1/workflows/{w_id}", headers=headers)
    with urllib.request.urlopen(req_wf) as resp:
        wf_data = json.loads(resp.read().decode())
        
    assert wf_data["id"] == w_id, f"ID mismatch for {dev['name']}"
    assert wf_data["name"] == dev["name"], f"Name mismatch for {dev['name']}"
    assert wf_data["active"] is False, f"{dev['name']} is active!"
    
    # Update settings to ensure availableInMCP is true
    settings = wf_data.get("settings", {})
    settings["availableInMCP"] = True
    settings["executionOrder"] = "v1"
    
    payload = {
        "name": wf_data["name"],
        "nodes": wf_data["nodes"],
        "connections": wf_data["connections"],
        "settings": settings
    }
    
    for n in payload["nodes"]:
        if "position" not in n or not n["position"]:
            n["position"] = [100, 100]
            
    req_update = urllib.request.Request(f"{api_url}/api/v1/workflows/{w_id}", data=json.dumps(payload).encode("utf-8"), headers=headers, method="PUT")
    with urllib.request.urlopen(req_update) as resp:
        updated_wf = json.loads(resp.read().decode())
        
    # Re-verify live
    with urllib.request.urlopen(req_wf) as resp:
        reverified_wf = json.loads(resp.read().decode())
        
    mcp_avail = reverified_wf.get("settings", {}).get("availableInMCP")
    print(f"Confirmed DEV Workflow: {reverified_wf['name']} | ID: {reverified_wf['id']} | active: {reverified_wf['active']} | availableInMCP: {mcp_avail} | Nodes: {len(reverified_wf['nodes'])}")
    
    confirmed_dev_wfs.append({
        "name": reverified_wf["name"],
        "id": reverified_wf["id"],
        "active": reverified_wf["active"],
        "availableInMCP": mcp_avail,
        "versionId": reverified_wf.get("versionId"),
        "activeVersionId": reverified_wf.get("activeVersionId"),
        "updatedAt": reverified_wf.get("updatedAt"),
        "nodeCount": len(reverified_wf["nodes"]),
        "connectionCount": len(reverified_wf.get("connections", {}))
    })

print("\n=== STEP 1 CONFIRMED SUCCESSFULLY ===")
