import json
import os

wf_path = r"C:\Users\Administrator\.gemini\antigravity-ide\brain\fda907d5-5169-44de-a045-c9886974c4ea\.system_generated\steps\925\output.txt"
with open(wf_path, encoding="utf-8") as f:
    wf_raw = json.load(f)

wf_data = wf_raw.get("data", wf_raw)

nodes = wf_data.get("nodes", [])

# 1. Update Config node
for node in nodes:
    if node["name"] == "Config":
        node["parameters"] = {
            "assignments": {
                "assignments": [
                    {
                        "id": "file_name_assign",
                        "name": "file_name",
                        "value": "product_restaurant_list",
                        "type": "string"
                    },
                    {
                        "id": "source_version_assign",
                        "name": "source_version",
                        "value": "={{ 'v_' + $now.format('yyyyMMdd_HHmmss') }}",
                        "type": "string"
                    },
                    {
                        "id": "catalog_hash_assign",
                        "name": "catalog_hash",
                        "value": "13981aaf83a38c7f1a810e4242b216bccd426bd003da75dd2e89c4e3b581bac8",
                        "type": "string"
                    },
                    {
                        "id": "run_id_assign",
                        "name": "run_id",
                        "value": "={{ 'run_' + $now.format('yyyyMMdd_HHmmss') + '_13981aaf' }}",
                        "type": "string"
                    }
                ]
            },
            "options": {}
        }

# 2. Update Embeddings OpenAI1 node
for node in nodes:
    if node["name"] == "Embeddings OpenAI1":
        node["parameters"] = {
            "model": "text-embedding-3-large",
            "options": {
                "dimensions": 1536
            }
        }
        node["disabled"] = False

# 3. Update Supabase Vector Store/Hybrid node
for node in nodes:
    if node["name"] == "Supabase Vector Store/Hybrid":
        node["disabled"] = False

# 4. Update Default Data Loader node to include source_version, catalog_hash, run_id
for node in nodes:
    if node["name"] == "Default Data Loader":
        node["parameters"] = {
            "jsonMode": "expressionData",
            "jsonData": "={{ $('JoinArray').first().json.all_text }}",
            "textSplittingMode": "custom",
            "options": {
                "metadata": {
                    "metadataValues": [
                        {
                            "name": "file_name",
                            "value": "={{ $('Config').first().json.file_name }}"
                        },
                        {
                            "name": "source_version",
                            "value": "={{ $('Config').first().json.source_version }}"
                        },
                        {
                            "name": "catalog_hash",
                            "value": "={{ $('Config').first().json.catalog_hash }}"
                        },
                        {
                            "name": "run_id",
                            "value": "={{ $('Config').first().json.run_id }}"
                        }
                    ]
                }
            }
        }

# 5. Update DeleteFilesSupabase node to run AFTER Supabase Vector Store/Hybrid and filter old versions
for node in nodes:
    if node["name"] == "DeleteFilesSupabase":
        node["parameters"] = {
            "operation": "delete",
            "tableId": "documents",
            "filterType": "string",
            "filterString": "=metadata->>file_name=eq.{{ $('Config').first().json.file_name }}&metadata->>source_version=neq.{{ $('Config').first().json.source_version }}"
        }
        node["disabled"] = False

# 6. Re-wire connections for Zero-Downtime Cutover
new_connections = {
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

updated_wf = {
    "name": "ToolsProductsDataTableToRag__DEV_DONA_ROSA_20260721",
    "nodes": nodes,
    "connections": new_connections,
    "settings": {
        "executionOrder": "v1",
        "availableInMCP": True
    }
}

out_reconfig = r"c:\Users\Administrator\Desktop\N8N_Pizzaria\2-etapa\output\reconfigured_workflow_dev.json"
with open(out_reconfig, "w", encoding="utf-8") as f:
    json.dump(updated_wf, f, indent=2, ensure_ascii=False)

print(f"Saved updated workflow JSON to {out_reconfig}")
