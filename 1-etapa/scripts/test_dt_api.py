import json
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

table_id = "yEPAXmN9AQQMn8IU"

req_r = urllib.request.Request(f"{api_url}/api/v1/data-tables/{table_id}/rows?limit=3", headers=headers)
with urllib.request.urlopen(req_r) as resp:
    r_data = json.loads(resp.read().decode())
    rows = r_data.get("data", [])
    print("Sample row 0:", json.dumps(rows[0], indent=2))
