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

# Test DELETE row API endpoint
url_test = f"{api_url}/api/v1/data-tables/{table_id}/rows/243"
req = urllib.request.Request(url_test, headers=headers, method="DELETE")
try:
    with urllib.request.urlopen(req) as resp:
        print("DELETE row 243 response:", resp.read().decode())
except urllib.error.HTTPError as e:
    print(f"DELETE row 243 failed: {e.code} {e.reason}: {e.read().decode()}")
