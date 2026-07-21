import json
import urllib.request
import urllib.parse
import urllib.error
import csv

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

all_rows = get_all_live_rows()
print(f"Total live rows: {len(all_rows)}")

corr_csv = r"c:\Users\Administrator\Desktop\N8N_Pizzaria\1-etapa\output\products.corrected.csv"
with open(corr_csv, encoding="utf-8") as f:
    corr_names = {r["name"] for r in csv.DictReader(f)}

extra_rows = [r for r in all_rows if r["name"] not in corr_names]
print(f"Total extra rows found: {len(extra_rows)}")

for r in extra_rows:
    print(f" - ID: {r['id']}, Name: '{r['name']}'")

if extra_rows:
    target_row = extra_rows[0]
    target_id = target_row["id"]
    target_name = target_row["name"]
    print(f"\nTesting DELETE on row id {target_id}: '{target_name}'")
    
    delete_tests = [
        ("POST", f"/api/v1/data-tables/{table_id}/rows/delete", {"filter": {"filters": [{"columnName": "name", "condition": "eq", "value": target_name}]}}),
        ("DELETE", f"/api/v1/data-tables/{table_id}/rows", {"filter": {"filters": [{"columnName": "name", "condition": "eq", "value": target_name}]}}),
        ("POST", f"/api/v1/data-tables/{table_id}/rows/delete", {"ids": [target_id]}),
        ("DELETE", f"/api/v1/data-tables/{table_id}/rows", {"ids": [target_id]}),
        ("DELETE", f"/api/v1/data-tables/{table_id}/rows?filter=%7B%22name%22%3A%22{urllib.parse.quote(target_name)}%22%7D", None),
    ]
    
    for method, endpoint, payload in delete_tests:
        url = f"{api_url}{endpoint}"
        data_bytes = json.dumps(payload).encode("utf-8") if payload is not None else None
        req = urllib.request.Request(url, data=data_bytes, headers=headers, method=method)
        try:
            with urllib.request.urlopen(req) as resp:
                print(f"SUCCESS {method} {endpoint} -> {resp.read().decode()}")
                break
        except urllib.error.HTTPError as e:
            print(f"FAILED {method} {endpoint} -> {e.code} {e.reason}: {e.read().decode()[:150]}")
