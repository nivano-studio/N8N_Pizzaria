import json
import os
import copy
import urllib.request

mcp_config_path = r"C:\Users\Administrator\.gemini\config\mcp_config.json"
mcp_config = json.load(open(mcp_config_path, encoding="utf-8"))
n8n_env = mcp_config.get("mcpServers", {}).get("n8n-mcp", {}).get("env", {})

api_url = n8n_env.get("N8N_API_URL", "https://n8n-donarosa.nivanostudio.com.br").rstrip("/")
api_key = n8n_env.get("N8N_API_KEY", "")

headers = {
    "X-N8N-API-KEY": api_key,
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

dt_map = {
    "hICNaSYRSMkjHiTT": "yEPAXmN9AQQMn8IU",
    "eXHmu98SYFK7A6zN": "DacGOSDHaMAFF3Zq",
    "BaMD12kIM3Y5iQDv": "0iESK6xkLcCfCNUu",
}

dt_name_map = {
    "products": "products__DEV_DONA_ROSA_20260721",
    "customers": "customers__DEV_DONA_ROSA_20260721",
    "invoices": "invoices__DEV_DONA_ROSA_20260721"
}

dev_wf_meta = [
    {
        "name": "ImportPdfToTable__DEV_DONA_ROSA_20260721",
        "dev_id": "fq4UCwZ6KOOXm0NY",
        "prod_id": "vpPp34JIYrReJxM5",
        "backup_file": "ImportPdfToTable_vpPp34JIYrReJxM5_backup.json",
        "dev_out": "ImportPdfToTable__DEV_DONA_ROSA_20260721.json"
    },
    {
        "name": "ToolsProductsDataTableToRag__DEV_DONA_ROSA_20260721",
        "dev_id": "NdproODtUwjO9ZZ5",
        "prod_id": "exIKvB9KjZy5AezC",
        "backup_file": "ToolsProductsDataTableToRag_exIKvB9KjZy5AezC_backup.json",
        "dev_out": "ToolsProductsDataTableToRag__DEV_DONA_ROSA_20260721.json"
    },
    {
        "name": "EvolutionDeliveyRagHibridoDataTables-export__DEV_DONA_ROSA_20260721",
        "dev_id": "x7L6Z0klfhvqWx1R",
        "prod_id": "XCZsECfv1SNrLN80",
        "backup_file": "EvolutionDeliveyRagHibridoDataTables-export_XCZsECfv1SNrLN80_backup.json",
        "dev_out": "EvolutionDeliveyRagHibridoDataTables-export__DEV_DONA_ROSA_20260721.json"
    }
]

base_dir1 = r"c:\Users\Administrator\Desktop\N8N_Pizzaria\0-etapa\audit_baseline_20260721"
base_dir2 = r"c:\Users\Administrator\Desktop\N8N_Pizzaria\audit_baseline_20260721"

def replace_in_obj(obj):
    if isinstance(obj, str):
        val = obj
        for p_id, d_id in dt_map.items():
            val = val.replace(p_id, d_id)
        for p_name, d_name in dt_name_map.items():
            if val == p_name:
                val = d_name
        return val
    elif isinstance(obj, dict):
        return {k: replace_in_obj(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [replace_in_obj(elem) for elem in obj]
    else:
        return obj

def sanitize_and_neutralize_node(node):
    node = replace_in_obj(node)
    
    node_name = node.get("name", "")
    node_type = node.get("type", "")
    
    external_types = [
        "n8n-nodes-base.webhook",
        "n8n-nodes-base.scheduleTrigger",
        "n8n-nodes-base.formTrigger",
        "@n8n/n8n-nodes-langchain.chatTrigger",
        "n8n-nodes-base.httpRequest",
        "n8n-nodes-base.httpRequestTool",
        "n8n-nodes-base.supabase",
        "@n8n/n8n-nodes-langchain.vectorStoreSupabase",
        "@n8n/n8n-nodes-langchain.embeddingsOpenAi",
        "@n8n/n8n-nodes-langchain.openAi",
        "n8n-nodes-base.redis"
    ]
    
    if node_type in external_types:
        node["disabled"] = True
        
    if "parameters" in node and isinstance(node["parameters"], dict):
        params = node["parameters"]
        if "url" in params:
            params["url"] = "http://127.0.0.1:9999/disabled_dev_stub"

    return node

for wf_meta in dev_wf_meta:
    backup_path = os.path.join(base_dir1, "backups", wf_meta["backup_file"])
    if not os.path.exists(backup_path):
        backup_path = os.path.join(base_dir2, "backups", wf_meta["backup_file"])
        
    wf_data = json.load(open(backup_path, encoding="utf-8"))
    
    dev_wf = copy.deepcopy(wf_data)
    dev_wf["id"] = wf_meta["dev_id"]
    dev_wf["name"] = wf_meta["name"]
    dev_wf["active"] = False
    
    cleaned_nodes = []
    for n in dev_wf.get("nodes", []):
        cleaned_nodes.append(sanitize_and_neutralize_node(n))
        
    dev_wf["nodes"] = cleaned_nodes
    
    # Save DEV JSON locally
    for b_dir in [base_dir1, base_dir2]:
        out_path = os.path.join(b_dir, "dev_copies", wf_meta["dev_out"])
        if os.path.exists(os.path.dirname(out_path)):
            with open(out_path, "w", encoding="utf-8") as f:
                json.dump(dev_wf, f, indent=2, ensure_ascii=False)
                
    # Update live DEV workflow
    payload = {
        "name": dev_wf["name"],
        "nodes": dev_wf["nodes"],
        "connections": dev_wf["connections"],
        "settings": {"executionOrder": "v1"}
    }
    for n in payload["nodes"]:
        if "position" not in n or not n["position"]:
            n["position"] = [100, 100]
            
    req = urllib.request.Request(f"{api_url}/api/v1/workflows/{wf_meta['dev_id']}", data=json.dumps(payload).encode("utf-8"), headers=headers, method="PUT")
    try:
        with urllib.request.urlopen(req) as resp:
            resp.read()
            print(f"Successfully updated live DEV workflow {wf_meta['name']} (ID: {wf_meta['dev_id']})")
    except urllib.error.HTTPError as e:
        print(f"Error updating DEV workflow {wf_meta['name']}: {e.code} - {e.read().decode('utf-8')}")

print("All DEV workflows reconfigured and deployed successfully.")
