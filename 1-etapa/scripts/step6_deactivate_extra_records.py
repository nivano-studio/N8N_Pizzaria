import json
import os
import csv
import urllib.request
import urllib.parse
import datetime

mcp_config_path = r"C:\Users\Administrator\.gemini\config\mcp_config.json"
mcp_config = json.load(open(mcp_config_path, encoding="utf-8"))
n8n_env = mcp_config.get("mcpServers", {}).get("n8n-mcp", {}).get("env", {})

api_url = n8n_env.get("N8N_API_URL", "https://n8n-donarosa.nivanostudio.com.br").rstrip("/")
api_key = n8n_env.get("N8N_API_KEY", "")

headers = {
    "X-N8N-API-KEY": api_key,
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0"
}

table_id = "yEPAXmN9AQQMn8IU"
corr_csv = r"c:\Users\Administrator\Desktop\N8N_Pizzaria\1-etapa\output\products.corrected.csv"
out_dir = r"c:\Users\Administrator\Desktop\N8N_Pizzaria\1-etapa\output"

with open(corr_csv, encoding="utf-8") as f:
    corr_items = list(csv.DictReader(f))
    corr_names = {r["name"] for r in corr_items}

def get_all_live_rows():
    all_rows = []
    cursor = None
    while True:
        url = f"{api_url}/api/v1/data-tables/{table_id}/rows?limit=100"
        if cursor:
            url += f"&cursor={urllib.parse.quote(str(cursor))}"
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req) as resp:
            res = json.loads(resp.read().decode())
            all_rows.extend(res.get("data", []))
            cursor = res.get("nextCursor")
            if not cursor:
                break
    return all_rows

live_rows = get_all_live_rows()
extra_rows = [r for r in live_rows if r["name"] not in corr_names]

print(f"Total live rows: {len(live_rows)}")
print(f"Found {len(extra_rows)} extra legacy rows to deactivate.")

deactivated_count = 0
for r in extra_rows:
    payload = {
        "filter": {
            "filters": [
                {
                    "columnName": "name",
                    "condition": "eq",
                    "value": r["name"]
                }
            ]
        },
        "data": {
            "name": r["name"],
            "description": f"[DESATIVADO LEGADO] {r.get('description', '')}",
            "price": str(r.get("price", "0")),
            "category": r.get("category", "Bebidas"),
            "image_url": r.get("image_url", ""),
            "active": False
        }
    }
    
    url = f"{api_url}/api/v1/data-tables/{table_id}/rows/upsert"
    req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req) as resp:
            resp.read()
            deactivated_count += 1
            print(f"Deactivated row '{r['name']}' (ID: {r['id']})")
    except Exception as e:
        print(f"Error deactivating '{r['name']}': {e}")

final_rows = get_all_live_rows()
active_rows = [r for r in final_rows if r.get("active") is True]
inactive_rows = [r for r in final_rows if r.get("active") is False]

print(f"\n--- VERIFICATION AFTER DEACTIVATION ---")
print(f"Total rows in Data Table DEV: {len(final_rows)}")
print(f"Active canonical rows (active == True): {len(active_rows)}")
print(f"Inactive legacy rows (active == False): {len(inactive_rows)}")

deactivation_log = {
    "table_id": table_id,
    "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "deactivated_requested_by_user": True,
    "total_rows": len(final_rows),
    "active_canonical_rows_count": len(active_rows),
    "inactive_legacy_rows_count": len(inactive_rows),
    "inactive_legacy_rows": [{"id": r["id"], "name": r["name"]} for r in inactive_rows]
}

out_log = os.path.join(out_dir, "extra_rows_deactivation_log.json")
with open(out_log, "w", encoding="utf-8") as f:
    json.dump(deactivation_log, f, indent=2, ensure_ascii=False)

print(f"Saved deactivation log to {out_log}")
