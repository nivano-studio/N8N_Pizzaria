import json
import os
import urllib.request
import urllib.parse

mcp_config_path = r"C:\Users\Administrator\.gemini\config\mcp_config.json"
mcp_config = json.load(open(mcp_config_path, encoding="utf-8"))
n8n_env = mcp_config.get("mcpServers", {}).get("n8n-mcp", {}).get("env", {})

api_url = n8n_env.get("N8N_API_URL", "https://n8n-donarosa.nivanostudio.com.br").rstrip("/")
api_key = n8n_env.get("N8N_API_KEY", "")

headers = {
    "X-N8N-API-KEY": api_key,
    "User-Agent": "Mozilla/5.0"
}

dev_tables = [
    {"name": "products__DEV_DONA_ROSA_20260721", "id": "yEPAXmN9AQQMn8IU"},
    {"name": "customers__DEV_DONA_ROSA_20260721", "id": "DacGOSDHaMAFF3Zq"},
    {"name": "invoices__DEV_DONA_ROSA_20260721", "id": "0iESK6xkLcCfCNUu"}
]

meta_output = {}

for dt in dev_tables:
    t_id = dt["id"]
    t_name = dt["name"]
    
    req_t = urllib.request.Request(f"{api_url}/api/v1/data-tables/{t_id}", headers=headers)
    with urllib.request.urlopen(req_t) as resp:
        t_detail = json.loads(resp.read().decode())
        if "data" in t_detail and isinstance(t_detail["data"], dict):
            t_detail = t_detail["data"]
            
    all_rows = []
    cursor = None
    while True:
        url = f"{api_url}/api/v1/data-tables/{t_id}/rows?limit=100"
        if cursor:
            url += f"&cursor={urllib.parse.quote(str(cursor))}"
        req_count = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req_count) as resp:
            resp_json = json.loads(resp.read().decode())
            data_field = resp_json.get("data", resp_json)
            if isinstance(data_field, dict):
                rows = data_field.get("rows", [])
            elif isinstance(data_field, list):
                rows = data_field
            else:
                rows = []
            
            cursor = resp_json.get("nextCursor") or (data_field.get("nextCursor") if isinstance(data_field, dict) else None)
            all_rows.extend(rows)
            if not cursor:
                break

    columns_schema = []
    for col in t_detail.get("columns", []):
        columns_schema.append({
            "id": col.get("id"),
            "name": col.get("name"),
            "type": col.get("type"),
            "index": col.get("index")
        })

    meta_output[t_name] = {
        "id": t_id,
        "name": t_name,
        "projectId": t_detail.get("projectId", "mNx2JLqnsOgn6t6X"),
        "rowCount": len(all_rows),
        "createdAt": t_detail.get("createdAt"),
        "updatedAt": t_detail.get("updatedAt"),
        "schema": columns_schema
    }

print("=== DEV DATA TABLES METADATA ===")
print(json.dumps(meta_output, indent=2))

out_dir = r"c:\Users\Administrator\Desktop\N8N_Pizzaria\0-etapa\audit_baseline_20260721"
os.makedirs(out_dir, exist_ok=True)
out_file = os.path.join(out_dir, "dev_datatables_meta.json")

with open(out_file, "w", encoding="utf-8") as f:
    json.dump(meta_output, f, indent=2, ensure_ascii=False)

print(f"\nSaved metadata to {out_file}")
