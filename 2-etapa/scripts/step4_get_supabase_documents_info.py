import json
import urllib.request

mcp_config_path = r"C:\Users\Administrator\.gemini\config\mcp_config.json"
mcp_config = json.load(open(mcp_config_path, encoding="utf-8"))
n8n_env = mcp_config.get("mcpServers", {}).get("n8n-mcp", {}).get("env", {})

api_url = n8n_env.get("N8N_API_URL", "https://n8n-donarosa.nivanostudio.com.br").rstrip("/")
api_key = n8n_env.get("N8N_API_KEY", "")

headers = {"X-N8N-API-KEY": api_key, "Content-Type": "application/json", "User-Agent": "Mozilla/5.0"}
wf_id = "NdproODtUwjO9ZZ5"

# Fetch full workflow JSON
url_get = f"{api_url}/api/v1/workflows/{wf_id}"
req_g = urllib.request.Request(url_get, headers=headers)
with urllib.request.urlopen(req_g) as resp:
    wf = json.loads(resp.read().decode())

nodes = wf["nodes"]
connections = wf["connections"]

# Check if GetDocumentsCount node exists
count_node = next((n for n in nodes if n["name"] == "GetDocumentsCount"), None)
if not count_node:
    count_node = {
        "id": "e7771234-5678-90ab-cdef-supabasegetdoc",
        "name": "GetDocumentsCount",
        "type": "n8n-nodes-base.supabase",
        "typeVersion": 1,
        "position": [2176, 400],
        "disabled": False,
        "credentials": {
            "supabaseApi": {
                "id": "2ryqvQ3GSZue40Nu",
                "name": "SupaNivanoDonaRosa"
            }
        },
        "parameters": {
            "operation": "getAll",
            "tableId": "documents",
            "returnAll": True
        }
    }
    nodes.append(count_node)

connections["Webhook Trigger"] = {
    "main": [
        [
            {"node": "Config", "type": "main", "index": 0},
            {"node": "GetDocumentsCount", "type": "main", "index": 0}
        ]
    ]
}

payload = {
    "name": wf["name"],
    "nodes": nodes,
    "connections": connections,
    "settings": wf.get("settings", {})
}

url_put = f"{api_url}/api/v1/workflows/{wf_id}"
req_p = urllib.request.Request(url_put, data=json.dumps(payload).encode("utf-8"), headers=headers, method="PUT")
with urllib.request.urlopen(req_p) as resp:
    res = json.loads(resp.read().decode())
    print(f"Updated '{res.get('name')}' with GetDocumentsCount node!")
