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

# Add InspectSupabaseData Code node
inspect_code = """
const items = $input.all();
const docs = items.map(i => i.json);

const file_name_counts = {};
const version_counts = {};
const hash_counts = {};

docs.forEach(d => {
  const meta = d.metadata || {};
  const fn = meta.file_name || 'UNKNOWN_FILE';
  const ver = meta.source_version || 'UNKNOWN_VERSION';
  const hash = meta.catalog_hash || 'UNKNOWN_HASH';

  file_name_counts[fn] = (file_name_counts[fn] || 0) + 1;
  version_counts[ver] = (version_counts[ver] || 0) + 1;
  hash_counts[hash] = (hash_counts[hash] || 0) + 1;
});

return [{
  json: {
    total_documents: docs.length,
    file_name_counts,
    version_counts,
    hash_counts,
    sample_metadata: docs.length > 0 ? docs[0].metadata : null
  }
}];
"""

code_node = next((n for n in nodes if n["name"] == "InspectSupabaseData"), None)
if not code_node:
    code_node = {
        "id": "c8881234-5678-90ab-cdef-inspectcodenode",
        "name": "InspectSupabaseData",
        "type": "n8n-nodes-base.code",
        "typeVersion": 2,
        "position": [2432, 400],
        "disabled": False,
        "parameters": {
            "jsCode": inspect_code
        }
    }
    nodes.append(code_node)

connections["GetDocumentsCount"] = {
    "main": [[{"node": "InspectSupabaseData", "type": "main", "index": 0}]]
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
    print(f"Attached InspectSupabaseData node to '{res.get('name')}'!")
