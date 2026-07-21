import json
import urllib.request

mcp_config_path = r"C:\Users\Administrator\.gemini\config\mcp_config.json"
mcp_config = json.load(open(mcp_config_path, encoding="utf-8"))
n8n_env = mcp_config.get("mcpServers", {}).get("n8n-mcp", {}).get("env", {})

api_url = n8n_env.get("N8N_API_URL", "https://n8n-donarosa.nivanostudio.com.br").rstrip("/")
api_key = n8n_env.get("N8N_API_KEY", "")

headers = {"X-N8N-API-KEY": api_key, "Content-Type": "application/json", "User-Agent": "Mozilla/5.0"}
table_id = "yEPAXmN9AQQMn8IU"

payload = {
    "filter": {
        "filters": [
            {
                "columnName": "id",
                "condition": "eq",
                "value": 243
            }
        ]
    },
    "data": {
        "active": False,
        "description": "[DESATIVADO_TESTE_API]"
    }
}

url = f"{api_url}/api/v1/data-tables/{table_id}/rows/upsert"
req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers, method="POST")
with urllib.request.urlopen(req) as resp:
    print("Deactivated row ID 243:", resp.read().decode())
