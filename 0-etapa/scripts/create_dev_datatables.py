import json
import os
import urllib.request
import urllib.parse

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

base_dir = r"c:\Users\Administrator\Desktop\N8N_Pizzaria\0-etapa\audit_baseline_20260721\datatables_snapshots"
if not os.path.exists(base_dir):
    base_dir = r"c:\Users\Administrator\Desktop\N8N_Pizzaria\audit_baseline_20260721\datatables_snapshots"

tables_to_create = [
    {
        "name": "products__DEV_DONA_ROSA_20260721",
        "columns": [
            {"name": "name", "type": "string"},
            {"name": "description", "type": "string"},
            {"name": "price", "type": "string"},
            {"name": "category", "type": "string"},
            {"name": "image_url", "type": "string"},
            {"name": "active", "type": "boolean"}
        ],
        "snapshot_file": os.path.join(base_dir, "products_hICNaSYRSMkjHiTT_snapshot.json")
    },
    {
        "name": "customers__DEV_DONA_ROSA_20260721",
        "columns": [
            {"name": "phone", "type": "string"},
            {"name": "name", "type": "string"},
            {"name": "busines_id", "type": "string"},
            {"name": "resumo", "type": "string"},
            {"name": "email", "type": "string"},
            {"name": "endereco", "type": "string"},
            {"name": "followup_data", "type": "string"},
            {"name": "customer_name", "type": "string"},
            {"name": "customer_email", "type": "string"}
        ],
        "snapshot_file": os.path.join(base_dir, "customers_eXHmu98SYFK7A6zN_snapshot.json")
    },
    {
        "name": "invoices__DEV_DONA_ROSA_20260721",
        "columns": [
            {"name": "customer_name", "type": "string"},
            {"name": "invoice_number", "type": "string"},
            {"name": "phone", "type": "string"},
            {"name": "status", "type": "string"},
            {"name": "description", "type": "string"},
            {"name": "total", "type": "string"},
            {"name": "forma_pagamento", "type": "string"}
        ],
        "snapshot_file": os.path.join(base_dir, "invoices_BaMD12kIM3Y5iQDv_snapshot.json")
    }
]

created_dev_tables = {}

req_tables = urllib.request.Request(f"{api_url}/api/v1/data-tables", headers=headers)
with urllib.request.urlopen(req_tables) as resp:
    existing_tables = json.loads(resp.read().decode("utf-8")).get("tables", [])

existing_by_name = {t["name"]: t["id"] for t in existing_tables}

for t in tables_to_create:
    t_name = t["name"]
    if t_name in existing_by_name:
        table_id = existing_by_name[t_name]
        print(f"Table {t_name} exists with ID: {table_id}")
    else:
        payload = {
            "name": t_name,
            "columns": t["columns"]
        }
        req_create = urllib.request.Request(f"{api_url}/api/v1/data-tables", data=json.dumps(payload).encode("utf-8"), headers=headers, method="POST")
        try:
            with urllib.request.urlopen(req_create) as resp:
                res_json = json.loads(resp.read().decode("utf-8"))
                table_id = res_json.get("id")
                print(f"Created table {t_name} with ID: {table_id}")
        except urllib.error.HTTPError as e:
            print(f"Error creating table {t_name}: {e.code} - {e.read().decode('utf-8')}")
            continue

    created_dev_tables[t_name] = table_id

    snapshot_data = json.load(open(t["snapshot_file"], encoding="utf-8"))
    rows = snapshot_data.get("rows", [])
    
    allowed_cols = {col["name"] for col in t["columns"]}
    cleaned_rows = []
    for r in rows:
        c_row = {k: v for k, v in r.items() if k in allowed_cols}
        cleaned_rows.append(c_row)
        
    print(f"Inserting {len(cleaned_rows)} rows into {t_name} ({table_id})...")
    
    for i in range(0, len(cleaned_rows), 50):
        batch = cleaned_rows[i:i+50]
        req_insert = urllib.request.Request(f"{api_url}/api/v1/data-tables/{table_id}/rows", data=json.dumps({"data": batch}).encode("utf-8"), headers=headers, method="POST")
        try:
            with urllib.request.urlopen(req_insert) as resp:
                resp.read()
        except urllib.error.HTTPError as e:
            print(f"Error inserting rows into {t_name}: {e.code} - {e.read().decode('utf-8')}")

print("\n=== DEV Data Tables Summary ===")
for k, v in created_dev_tables.items():
    print(f"{k}: {v}")

meta_out1 = r"c:\Users\Administrator\Desktop\N8N_Pizzaria\0-etapa\audit_baseline_20260721\dev_datatables_meta.json"
meta_out2 = r"c:\Users\Administrator\Desktop\N8N_Pizzaria\audit_baseline_20260721\dev_datatables_meta.json"

for meta_file in [meta_out1, meta_out2]:
    if os.path.exists(os.path.dirname(meta_file)):
        with open(meta_file, "w", encoding="utf-8") as f:
            json.dump(created_dev_tables, f, indent=2)

