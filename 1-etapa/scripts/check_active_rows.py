import json
import urllib.request
import urllib.parse

mcp_config_path = r"C:\Users\Administrator\.gemini\config\mcp_config.json"
mcp_config = json.load(open(mcp_config_path, encoding="utf-8"))
n8n_env = mcp_config.get("mcpServers", {}).get("n8n-mcp", {}).get("env", {})

api_url = n8n_env.get("N8N_API_URL", "https://n8n-donarosa.nivanostudio.com.br").rstrip("/")
api_key = n8n_env.get("N8N_API_KEY", "")

headers = {"X-N8N-API-KEY": api_key, "Content-Type": "application/json", "User-Agent": "Mozilla/5.0"}
table_id = "yEPAXmN9AQQMn8IU"

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

active_rows = [r for r in all_rows if r.get("active") is True]
print(f"Total active rows: {len(active_rows)}")

active_names = [r["name"] for r in active_rows]
dups = [n for n in set(active_names) if active_names.count(n) > 1]
print(f"Duplicate names among active rows: {dups}")

for d in dups:
    matching = [r for r in active_rows if r["name"] == d]
    print(f"Duplicate '{d}': IDs = {[m['id'] for m in matching]}")
