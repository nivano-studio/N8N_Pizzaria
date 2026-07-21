import json
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

table_id = "yEPAXmN9AQQMn8IU"

# Test PATCH /api/v1/data-tables/{tableId}/rows/{rowId}
payload = {
    "price": "15"
}

req = urllib.request.Request(f"{api_url}/api/v1/data-tables/{table_id}/rows/1", data=json.dumps(payload).encode("utf-8"), headers=headers, method="PATCH")
try:
    with urllib.request.urlopen(req) as resp:
        print("PATCH single row response:", resp.read().decode())
except Exception as e:
    print("PATCH single row failed:", e)

# Test PATCH /api/v1/data-tables/{tableId}/rows (batch update)
payload_batch = [
    {
        "id": 1,
        "price": "15"
    }
]
req_b = urllib.request.Request(f"{api_url}/api/v1/data-tables/{table_id}/rows", data=json.dumps(payload_batch).encode("utf-8"), headers=headers, method="PATCH")
try:
    with urllib.request.urlopen(req_b) as resp:
        print("PATCH batch rows response:", resp.read().decode())
except Exception as e:
    print("PATCH batch rows failed:", e)
