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

payloads = [
    {"filter": {"filters": [{"column": "name", "operator": "equals", "value": "CALABRESA - Brotinha"}]}, "data": [{"name": "CALABRESA - Brotinha", "price": "15"}]},
    {"filter": {"filters": [{"column": "name", "value": "CALABRESA - Brotinha"}]}, "data": [{"name": "CALABRESA - Brotinha", "price": "15"}]},
    {"filter": {"filters": {"name": "CALABRESA - Brotinha"}}, "data": [{"name": "CALABRESA - Brotinha", "price": "15"}]},
    {"filter": {"filters": ["name"]}, "data": [{"name": "CALABRESA - Brotinha", "price": "15"}]},
]

for idx, p in enumerate(payloads):
    url = f"{api_url}/api/v1/data-tables/{table_id}/rows/upsert"
    req = urllib.request.Request(url, data=json.dumps(p).encode("utf-8"), headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req) as resp:
            print(f"SUCCESS payload {idx} -> {resp.read().decode()}")
    except urllib.error.HTTPError as e:
        print(f"FAILED payload {idx} -> {e.code} {e.reason}: {e.read().decode()[:150]}")
