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

# Check if Webhook Trigger node already exists
webhook_node = next((n for n in nodes if n["name"] == "Webhook Trigger"), None)
if not webhook_node:
    webhook_node = {
        "id": "e98218a4-1234-4567-89ab-devwebhooknode",
        "name": "Webhook Trigger",
        "type": "n8n-nodes-base.webhook",
        "typeVersion": 2,
        "position": [1152, 380],
        "disabled": False,
        "parameters": {
            "httpMethod": "POST",
            "path": "dev-sync-rag",
            "options": {}
        }
    }
    nodes.append(webhook_node)

connections["Webhook Trigger"] = {
    "main": [[{"node": "Config", "type": "main", "index": 0}]]
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
    print(f"Added Webhook Trigger to '{res.get('name')}'! Total nodes: {len(res.get('nodes', []))}")
