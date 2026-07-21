import json
import os
import copy
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
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

id_replacements = {
    "hICNaSYRSMkjHiTT": "yEPAXmN9AQQMn8IU",
    "eXHmu98SYFK7A6zN": "DacGOSDHaMAFF3Zq",
    "BaMD12kIM3Y5iQDv": "0iESK6xkLcCfCNUu",
    "XbYdEIzrF5Ltlrll": "DacGOSDHaMAFF3Zq",
    "AIwE75J1sVmYQjdk": "0iESK6xkLcCfCNUu",
}

name_replacements = {
    "products": "products__DEV_DONA_ROSA_20260721",
    "customers": "customers__DEV_DONA_ROSA_20260721",
    "invoices": "invoices__DEV_DONA_ROSA_20260721"
}

dev_meta = [
    {
        "name": "ImportPdfToTable__DEV_DONA_ROSA_20260721",
        "dev_id": "fq4UCwZ6KOOXm0NY",
        "backup_file": "ImportPdfToTable_vpPp34JIYrReJxM5_backup.json",
        "dev_out": "ImportPdfToTable__DEV_DONA_ROSA_20260721.json"
    },
    {
        "name": "ToolsProductsDataTableToRag__DEV_DONA_ROSA_20260721",
        "dev_id": "NdproODtUwjO9ZZ5",
        "backup_file": "ToolsProductsDataTableToRag_exIKvB9KjZy5AezC_backup.json",
        "dev_out": "ToolsProductsDataTableToRag__DEV_DONA_ROSA_20260721.json"
    },
    {
        "name": "EvolutionDeliveyRagHibridoDataTables-export__DEV_DONA_ROSA_20260721",
        "dev_id": "x7L6Z0klfhvqWx1R",
        "backup_file": "EvolutionDeliveyRagHibridoDataTables-export_XCZsECfv1SNrLN80_backup.json",
        "dev_out": "EvolutionDeliveyRagHibridoDataTables-export__DEV_DONA_ROSA_20260721.json"
    }
]

base_dir = r"c:\Users\Administrator\Desktop\N8N_Pizzaria\0-etapa\audit_baseline_20260721"

def recursive_replace(obj):
    if isinstance(obj, str):
        val = obj
        for old_id, new_id in id_replacements.items():
            val = val.replace(old_id, new_id)
        for old_name, new_name in name_replacements.items():
            if val == old_name:
                val = new_name
        return val
    elif isinstance(obj, dict):
        return {k: recursive_replace(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [recursive_replace(item) for item in obj]
    else:
        return obj

def sanitize_settings(settings):
    allowed_keys = {"executionOrder", "saveExecutionProgress", "saveManualExecutions", "saveDataErrorExecution", "saveDataSuccessExecution", "callerPolicy", "errorWorkflow", "availableInMCP"}
    return {k: v for k, v in settings.items() if k in allowed_keys}

def neutralize_node(node):
    node = recursive_replace(node)
    
    node_name = node.get("name", "")
    node_type = node.get("type", "")
    
    external_types = [
        "n8n-nodes-base.webhook",
        "n8n-nodes-base.scheduleTrigger",
        "n8n-nodes-base.formTrigger",
        "n8n-nodes-base.manualTrigger",
        "@n8n/n8n-nodes-langchain.chatTrigger",
        "n8n-nodes-base.httpRequest",
        "n8n-nodes-base.httpRequestTool",
        "n8n-nodes-base.supabase",
        "@n8n/n8n-nodes-langchain.vectorStoreSupabase",
        "@n8n/n8n-nodes-langchain.embeddingsOpenAi",
        "@n8n/n8n-nodes-langchain.openAi",
        "@n8n/n8n-nodes-langchain.lmChatOpenAi",
        "@n8n/n8n-nodes-langchain.agent",
        "@n8n/n8n-nodes-langchain.agentTool",
        "@n8n/n8n-nodes-langchain.memoryBufferWindow",
        "@n8n/n8n-nodes-langchain.toolCalculator",
        "n8n-nodes-base.redis"
    ]
    
    if node_type in external_types or "OpenAI" in node_name or "Evolution" in node_name or "ElevenLabs" in node_name or "Supabase" in node_name or "Redis" in node_name or "Whatsapp" in node_name:
        node["disabled"] = True
        
    if "parameters" in node and isinstance(node["parameters"], dict):
        params = node["parameters"]
        if "url" in params:
            params["url"] = "http://127.0.0.1:9999/disabled_dev_stub"

    return node

print("=== RECONFIGURING DEV EXPORTS AND NEUTRALIZING EXTERNAL NODES ===")

for wf in dev_meta:
    backup_path = os.path.join(base_dir, "backups", wf["backup_file"])
    wf_data = json.load(open(backup_path, encoding="utf-8"))
    
    dev_wf = copy.deepcopy(wf_data)
    dev_wf["id"] = wf["dev_id"]
    dev_wf["name"] = wf["name"]
    dev_wf["active"] = False
    
    settings = sanitize_settings(dev_wf.get("settings", {}))
    settings["availableInMCP"] = True
    settings["executionOrder"] = "v1"
    dev_wf["settings"] = settings
    
    neutralized_nodes = []
    for n in dev_wf.get("nodes", []):
        neutralized_nodes.append(neutralize_node(n))
        
    dev_wf["nodes"] = neutralized_nodes
    
    out_dev_path = os.path.join(base_dir, "dev_copies", wf["dev_out"])
    with open(out_dev_path, "w", encoding="utf-8") as f:
        json.dump(dev_wf, f, indent=2, ensure_ascii=False)
    print(f"Saved local DEV export: {out_dev_path}")
    
    payload = {
        "name": dev_wf["name"],
        "nodes": dev_wf["nodes"],
        "connections": dev_wf["connections"],
        "settings": dev_wf["settings"]
    }
    for n in payload["nodes"]:
        if "position" not in n or not n["position"]:
            n["position"] = [100, 100]
            
    req = urllib.request.Request(f"{api_url}/api/v1/workflows/{wf['dev_id']}", data=json.dumps(payload).encode("utf-8"), headers=headers, method="PUT")
    try:
        with urllib.request.urlopen(req) as resp:
            resp.read()
            print(f"Updated live DEV workflow: {wf['name']} (ID: {wf['dev_id']})")
    except urllib.error.HTTPError as e:
        print(f"Error updating {wf['name']}: {e.code} - {e.read().decode('utf-8')}")

print("\n=== RECONFIGURATION & NEUTRALIZATION COMPLETED ===")
