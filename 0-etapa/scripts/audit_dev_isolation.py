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
    "User-Agent": "Mozilla/5.0"
}

prod_dt_ids = {"hICNaSYRSMkjHiTT", "eXHmu98SYFK7A6zN", "BaMD12kIM3Y5iQDv"}
dev_dt_ids = {"yEPAXmN9AQQMn8IU", "DacGOSDHaMAFF3Zq", "0iESK6xkLcCfCNUu"}

dev_wf_ids = ["fq4UCwZ6KOOXm0NY", "NdproODtUwjO9ZZ5", "x7L6Z0klfhvqWx1R"]

print("=== AUDITING LIVE DEV WORKFLOW ISOLATION ===")

for w_id in dev_wf_ids:
    url = f"{api_url}/api/v1/workflows/{w_id}"
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req) as resp:
        wf = json.loads(resp.read().decode())
        
    wf_name = wf["name"]
    is_active = wf["active"]
    nodes = wf["nodes"]
    
    print(f"\nAudit Workflow: {wf_name} (ID: {w_id})")
    assert is_active is False, f"FAIL: DEV Workflow {wf_name} is active!"
    print("[PASS] active == False")
    
    found_prod_dt = []
    found_dev_dt = []
    disabled_count = 0
    
    for n in nodes:
        if n.get("disabled") is True:
            disabled_count += 1
        n_str = json.dumps(n)
        for p_id in prod_dt_ids:
            if p_id in n_str:
                found_prod_dt.append((n["name"], p_id))
        for d_id in dev_dt_ids:
            if d_id in n_str:
                found_dev_dt.append((n["name"], d_id))
                
    assert len(found_prod_dt) == 0, f"FAIL: Production Data Table IDs found in DEV workflow: {found_prod_dt}"
    print(f"[PASS] 0 Production Data Table references found.")
    print(f"[PASS] DEV Data Table references verified: {len(found_dev_dt)} nodes ({[x[0] for x in found_dev_dt]})")
    print(f"[PASS] Disabled / Isolated nodes count: {disabled_count}")

print("\n=== ALL ISOLATION AUDITS PASSED CLEANLY ===")
