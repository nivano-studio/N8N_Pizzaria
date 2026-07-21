import json
import urllib.request
import urllib.parse

mcp_config_path = r"C:\Users\Administrator\.gemini\config\mcp_config.json"
mcp_config = json.load(open(mcp_config_path, encoding="utf-8"))
n8n_env = mcp_config.get("mcpServers", {}).get("n8n-mcp", {}).get("env", {})

api_url = n8n_env.get("N8N_API_URL", "https://n8n-donarosa.nivanostudio.com.br").rstrip("/")
api_key = n8n_env.get("N8N_API_KEY", "")

headers = {"X-N8N-API-KEY": api_key, "Content-Type": "application/json", "User-Agent": "Mozilla/5.0"}
wf_id = "NdproODtUwjO9ZZ5"

# Fetch full workflow JSON first
url_get = f"{api_url}/api/v1/workflows/{wf_id}"
req_g = urllib.request.Request(url_get, headers=headers)
with urllib.request.urlopen(req_g) as resp:
    wf = json.loads(resp.read().decode())

# Update nodes
for node in wf["nodes"]:
    if node["name"] == "Config":
        node["parameters"] = {
            "assignments": {
                "assignments": [
                    {"id": "file_name_assign", "name": "file_name", "value": "product_restaurant_list", "type": "string"},
                    {"id": "source_version_assign", "name": "source_version", "value": "={{ 'v_' + $now.format('yyyyMMdd_HHmmss') }}", "type": "string"},
                    {"id": "catalog_hash_assign", "name": "catalog_hash", "value": "13981aaf83a38c7f1a810e4242b216bccd426bd003da75dd2e89c4e3b581bac8", "type": "string"},
                    {"id": "run_id_assign", "name": "run_id", "value": "={{ 'run_' + $now.format('yyyyMMdd_HHmmss') + '_13981aaf' }}", "type": "string"}
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
    elif node["name"] == "Supabase Vector Store/Hybrid":
        node["disabled"] = False
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
            "filterString": "=metadata->>file_name=eq.{{ $('Config').first().json.file_name }}&metadata->>source_version=neq.{{ $('Config').first().json.source_version }}"
        }

# Set clean connections dictionary
wf["connections"] = {
    "Config": {
        "main": [[{"node": "GetAllProduts", "type": "main", "index": 0}]]
    },
    "GetAllProduts": {
        "main": [[{"node": "BlockList", "type": "main", "index": 0}]]
    },
    "BlockList": {
        "main": [[{"node": "Split Out", "type": "main", "index": 0}]]
    },
    "Split Out": {
        "main": [[{"node": "ConvertToMarkdown", "type": "main", "index": 0}]]
    },
    "ConvertToMarkdown": {
        "main": [[{"node": "Aggregate", "type": "main", "index": 0}]]
    },
    "Aggregate": {
        "main": [[{"node": "JoinArray", "type": "main", "index": 0}]]
    },
    "JoinArray": {
        "main": [[{"node": "Supabase Vector Store/Hybrid", "type": "main", "index": 0}]]
    },
    "Supabase Vector Store/Hybrid": {
        "main": [[{"node": "DeleteFilesSupabase", "type": "main", "index": 0}]]
    },
    "Schedule Trigger": {
        "main": [[{"node": "Config", "type": "main", "index": 0}]]
    },
    "When clicking ‘Execute workflow’": {
        "main": [[{"node": "Config", "type": "main", "index": 0}]]
    },
    "Default Data Loader": {
        "ai_document": [[{"node": "Supabase Vector Store/Hybrid", "type": "ai_document", "index": 0}]]
    },
    "Recursive Character Text Splitter": {
        "ai_textSplitter": [[{"node": "Default Data Loader", "type": "ai_textSplitter", "index": 0}]]
    },
    "Embeddings OpenAI1": {
        "ai_embedding": [[{"node": "Supabase Vector Store/Hybrid", "type": "ai_embedding", "index": 0}]]
    }
}

# Update workflow via PUT /api/v1/workflows/{id}
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
    print(f"Workflow '{res.get('name')}' updated live! Node count: {len(res.get('nodes', []))}")
