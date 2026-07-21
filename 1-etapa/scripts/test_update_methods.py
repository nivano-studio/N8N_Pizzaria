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

methods_to_test = [
    ("PUT", f"/api/v1/data-tables/{table_id}/rows/1", {"price": "15"}),
    ("POST", f"/api/v1/data-tables/{table_id}/rows/1", {"price": "15"}),
    ("POST", f"/api/v1/data-tables/{table_id}/rows/upsert", [{"name": "CALABRESA - Brotinha", "price": "15"}]),
    ("POST", f"/api/v1/data-tables/{table_id}/rows", [{"id": 1, "price": "15"}]),
    ("PUT", f"/api/v1/data-tables/{table_id}/rows", [{"id": 1, "price": "15"}]),
]

for method, endpoint, payload in methods_to_test:
    url = f"{api_url}{endpoint}"
    req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            print(f"SUCCESS {method} {endpoint} -> {resp.read().decode()[:100]}")
    except urllib.error.HTTPError as e:
        print(f"FAILED {method} {endpoint} -> {e.code} {e.reason}: {e.read().decode()[:100]}")
