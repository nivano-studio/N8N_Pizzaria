import json
import os
import urllib.request
import urllib.parse
import hashlib
import datetime

mcp_config_path = r"C:\Users\Administrator\.gemini\config\mcp_config.json"
mcp_config = json.load(open(mcp_config_path, encoding="utf-8"))
n8n_env = mcp_config.get("mcpServers", {}).get("n8n-mcp", {}).get("env", {})

api_url = n8n_env.get("N8N_API_URL", "https://n8n-donarosa.nivanostudio.com.br").rstrip("/")
api_key = n8n_env.get("N8N_API_KEY", "")
headers = {"X-N8N-API-KEY": api_key, "Content-Type": "application/json", "User-Agent": "Mozilla/5.0"}

wf_id = "NdproODtUwjO9ZZ5"

# Canonical Hash from 242 products
catalog_hash = "13981aaf83a38c7f1a810e4242b216bccd426bd003da75dd2e89c4e3b581bac8"
source_version = "v_13981aaf"
run_id = f"run_13981aaf"
file_name = "product_restaurant_list"

print(f"=== ETAPA 2: CONFIGURANDO WORKFLOW DEV COM HASH CANÔNICO ===")
print(f"Workflow ID: {wf_id}")
print(f"catalog_hash: {catalog_hash}")
print(f"source_version: {source_version}")

# Update DEV workflow NdproODtUwjO9ZZ5
url_get = f"{api_url}/api/v1/workflows/{wf_id}"
req_g = urllib.request.Request(url_get, headers=headers)
with urllib.request.urlopen(req_g) as resp:
    wf = json.loads(resp.read().decode())

for node in wf["nodes"]:
    if node["name"] == "Config":
        node["parameters"] = {
            "assignments": {
                "assignments": [
                    {"id": "file_name_assign", "name": "file_name", "value": file_name, "type": "string"},
                    {"id": "source_version_assign", "name": "source_version", "value": source_version, "type": "string"},
                    {"id": "catalog_hash_assign", "name": "catalog_hash", "value": catalog_hash, "type": "string"},
                    {"id": "run_id_assign", "name": "run_id", "value": run_id, "type": "string"}
                ]
            },
            "options": {}
        }
    elif node["name"] == "Embeddings OpenAI1":
        node["disabled"] = False
        node["parameters"] = {
            "model": "text-embedding-3-large",
            "options": {
                "dimensions": 1536
            }
        }
    elif node["name"] == "Default Data Loader":
        node["disabled"] = False
        node["parameters"] = {
            "jsonMode": "expressionData",
            "jsonData": "={{ $('JoinArray').first().json.all_text }}",
            "textSplittingMode": "custom",
            "options": {
                "metadata": {
                    "metadataValues": [
                        {"name": "file_name", "value": "={{ $('Config').first().json.file_name }}"},
                        {"name": "source_version", "value": "={{ $('Config').first().json.source_version }}"},
                        {"name": "catalog_hash", "value": "={{ $('Config').first().json.catalog_hash }}"},
                        {"name": "run_id", "value": "={{ $('Config').first().json.run_id }}"}
                    ]
                }
            }
        }
    elif node["name"] == "DeleteFilesSupabase":
        node["disabled"] = False
        node["parameters"] = {
            "operation": "delete",
            "tableId": "documents",
            "filterType": "string",
            "filterString": f"=metadata->>file_name=eq.{file_name}&metadata->>source_version=neq.{source_version}"
        }

payload = {
    "name": wf["name"],
    "nodes": wf["nodes"],
    "connections": wf["connections"],
    "settings": wf.get("settings", {})
}

url_put = f"{api_url}/api/v1/workflows/{wf_id}"
req_p = urllib.request.Request(url_put, data=json.dumps(payload).encode("utf-8"), headers=headers, method="PUT")
with urllib.request.urlopen(req_p) as resp:
    res = json.loads(resp.read().decode())
    print(f"DEV Workflow updated live! Active: {res.get('active')}, Nodes: {len(res.get('nodes', []))}")

# Save ingest metadata evidence
out_dir = r"c:\Users\Administrator\Desktop\N8N_Pizzaria\2-etapa\output"
os.makedirs(out_dir, exist_ok=True)
ingest_config = {
    "catalog_hash": catalog_hash,
    "source_version": source_version,
    "run_id": run_id,
    "file_name": file_name,
    "total_active_products": 242,
    "embedding_model": "text-embedding-3-large",
    "dimensions": 1536,
    "updated_at": datetime.datetime.now(datetime.timezone.utc).isoformat()
}
with open(os.path.join(out_dir, "ingest_config.json"), "w", encoding="utf-8") as f:
    json.dump(ingest_config, f, indent=2, ensure_ascii=False)

print("Saved ingest_config.json successfully!")
