import json
import os
import urllib.request

mcp_config_path = r"C:\Users\Administrator\.gemini\config\mcp_config.json"
mcp_config = json.load(open(mcp_config_path, encoding="utf-8"))
n8n_env = mcp_config.get("mcpServers", {}).get("n8n-mcp", {}).get("env", {})

api_url = n8n_env.get("N8N_API_URL", "https://n8n-donarosa.nivanostudio.com.br").rstrip("/")
api_key = n8n_env.get("N8N_API_KEY", "")
headers = {"X-N8N-API-KEY": api_key, "Content-Type": "application/json", "User-Agent": "Mozilla/5.0"}

wf_id = "x7L6Z0klfhvqWx1R"

url_get = f"{api_url}/api/v1/workflows/{wf_id}"
req_g = urllib.request.Request(url_get, headers=headers)
with urllib.request.urlopen(req_g) as resp:
    wf = json.loads(resp.read().decode())

out_dir = r"c:\Users\Administrator\Desktop\N8N_Pizzaria\3-etapa\output"
os.makedirs(out_dir, exist_ok=True)

# Save pre-edit snapshot
with open(os.path.join(out_dir, "wf_main_dev_pre_edit_snapshot.json"), "w", encoding="utf-8") as f:
    json.dump(wf, f, indent=2, ensure_ascii=False)

print(f"Fetched workflow '{wf['name']}' (ID: {wf['id']}). Saved pre-edit snapshot!")
print(f"Total nodes: {len(wf['nodes'])}, Total connections: {len(wf['connections'])}")

# Target nodes to inspect:
target_names = [
    "Atendente AI", "AgentCaixa", "OpenAI3", "search_restaurante_data",
    "UpdateCustomer", "UpdateAddRascunho", "UpdateAddInvoice",
    "CustomerData", "CustomerData2", "GetInvoices1", "GetInvoices2"
]

found_nodes = {n["name"]: n for n in wf["nodes"] if n["name"] in target_names}
for name in target_names:
    if name in found_nodes:
        n = found_nodes[name]
        print(f"Found [{name}] (Type: {n['type']}, ID: {n['id']})")
        if "parameters" in n:
            params_keys = list(n["parameters"].keys())
            print(f"  Parameters: {params_keys[:5]}")
    else:
        print(f"WARNING: Node [{name}] NOT found!")
