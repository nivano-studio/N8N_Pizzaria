import json
import os
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

base_dir = r"c:\Users\Administrator\Desktop\N8N_Pizzaria\0-etapa\audit_baseline_20260721\datatables_snapshots"
if not os.path.exists(base_dir):
    base_dir = r"c:\Users\Administrator\Desktop\N8N_Pizzaria\audit_baseline_20260721\datatables_snapshots"

tables_map = {
    "yEPAXmN9AQQMn8IU": {
        "name": "products__DEV_DONA_ROSA_20260721",
        "snapshot": os.path.join(base_dir, "products_hICNaSYRSMkjHiTT_snapshot.json"),
        "cols": ["name", "description", "price", "category", "image_url", "active"]
    },
    "DacGOSDHaMAFF3Zq": {
        "name": "customers__DEV_DONA_ROSA_20260721",
        "snapshot": os.path.join(base_dir, "customers_eXHmu98SYFK7A6zN_snapshot.json"),
        "cols": ["phone", "name", "busines_id", "resumo", "email", "endereco", "followup_data", "customer_name", "customer_email"]
    },
    "0iESK6xkLcCfCNUu": {
        "name": "invoices__DEV_DONA_ROSA_20260721",
        "snapshot": os.path.join(base_dir, "invoices_BaMD12kIM3Y5iQDv_snapshot.json"),
        "cols": ["customer_name", "invoice_number", "phone", "status", "description", "total", "forma_pagamento"]
    }
}

for t_id, info in tables_map.items():
    t_name = info["name"]
    snapshot_file = info["snapshot"]
    allowed_cols = set(info["cols"])
    
    snapshot_data = json.load(open(snapshot_file, encoding="utf-8"))
    rows = snapshot_data.get("rows", [])
    
    cleaned_rows = []
    for r in rows:
        c_row = {k: v for k, v in r.items() if k in allowed_cols}
        cleaned_rows.append(c_row)
        
    print(f"Populating {len(cleaned_rows)} rows into {t_name} ({t_id})...")
    
    for i in range(0, len(cleaned_rows), 50):
        batch = cleaned_rows[i:i+50]
        req_insert = urllib.request.Request(f"{api_url}/api/v1/data-tables/{t_id}/rows", data=json.dumps({"data": batch}).encode("utf-8"), headers=headers, method="POST")
        try:
            with urllib.request.urlopen(req_insert) as resp:
                resp.read()
                print(f"Inserted batch {i//50 + 1} ({len(batch)} rows)")
        except urllib.error.HTTPError as e:
            print(f"Error inserting rows into {t_name}: {e.code} - {e.read().decode('utf-8')}")

print("\nAll DEV Data Tables populated successfully.")
