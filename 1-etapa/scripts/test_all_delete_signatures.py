import json
import urllib.request
import urllib.error

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

table_id = "yEPAXmN9AQQMn8IU"
row_id = 228 # 'Coca-Cola 2L - Original'

candidates = [
    ("DELETE", f"/api/v1/data-tables/{table_id}/rows?ids=228", None),
    ("DELETE", f"/api/v1/data-tables/{table_id}/rows?id=228", None),
    ("POST", f"/api/v1/data-tables/{table_id}/rows/delete", {"ids": [228]}),
    ("POST", f"/api/v1/data-tables/{table_id}/rows/delete", {"filter": {"filters": [{"columnName": "name", "condition": "eq", "value": "Coca-Cola 2L - Original"}]}}),
    ("POST", f"/api/v1/data-tables/{table_id}/rows/remove", {"ids": [228]}),
    ("POST", f"/api/v1/data-tables/{table_id}/rows/batch-delete", {"ids": [228]}),
    ("DELETE", f"/api/v1/data-tables/{table_id}/row/228", None),
    ("DELETE", f"/api/v1/data-tables/{table_id}/rows", {"ids": [228]}),
]

for method, endpoint, payload in candidates:
    url = f"{api_url}{endpoint}"
    data_bytes = json.dumps(payload).encode("utf-8") if payload is not None else None
    req = urllib.request.Request(url, data=data_bytes, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            print(f"SUCCESS {method} {endpoint} -> {resp.read().decode()}")
    except urllib.error.HTTPError as e:
        print(f"FAILED {method} {endpoint} -> {e.code} {e.reason}: {e.read().decode()[:120]}")
