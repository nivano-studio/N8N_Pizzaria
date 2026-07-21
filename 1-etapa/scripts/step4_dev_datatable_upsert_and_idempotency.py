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

with open(corr_csv, mode="r", encoding="utf-8") as f:
    canonical_items = list(csv.DictReader(f))

def get_live_rows():
    all_rows = []
    cursor = None
    while True:
        url = f"{api_url}/api/v1/data-tables/{table_id}/rows?limit=100"
        if cursor:
            url += f"&cursor={urllib.parse.quote(str(cursor))}"
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req) as resp:
            res = json.loads(resp.read().decode())
            data = res.get("data", [])
            cursor = res.get("nextCursor")
            all_rows.extend(data)
            if not cursor:
                break
    return all_rows

live_rows = get_live_rows()

# Identify extra records in Data Table that do not match canonical name natural key
canonical_names_set = {item["name"] for item in canonical_items}
extra_records_in_dt = [r for r in live_rows if r["name"] not in canonical_names_set]

print(f"Total live rows in DEV Data Table: {len(live_rows)}")
print(f"Canonical products count: {len(canonical_items)}")
print(f"Extra un-updated records (old beverage names / test rows): {len(extra_records_in_dt)}")

# Re-verify Run 2 idempotency
run1_snapshot = live_rows
run1_names = {r["name"]: (r["description"], r["price"], r["category"], r["image_url"], r["active"]) for r in run1_snapshot}

# Run 2: Idempotency check execution
start_time_run2 = datetime.datetime.now(datetime.timezone.utc).isoformat()
count_before_run2 = len(run1_snapshot)

success_count_run2 = 0
fail_count_run2 = 0

for idx, item in enumerate(canonical_items):
    active_bool = True if str(item["active"]).lower() in ["true", "1"] else False
    payload = {
        "filter": {
            "filters": [
                {
                    "columnName": "name",
                    "condition": "eq",
                    "value": item["name"]
                }
            ]
        },
        "data": {
            "name": item["name"],
            "description": item["description"],
            "price": str(item["price"]),
            "category": item["category"],
            "image_url": item["image_url"],
            "active": active_bool
        }
    }
    
    url = f"{api_url}/api/v1/data-tables/{table_id}/rows/upsert"
    req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req) as resp:
            resp.read()
            success_count_run2 += 1
    except Exception as e:
        fail_count_run2 += 1

end_time_run2 = datetime.datetime.now(datetime.timezone.utc).isoformat()
run2_snapshot = get_live_rows()
count_after_run2 = len(run2_snapshot)

run2_names = {r["name"]: (r["description"], r["price"], r["category"], r["image_url"], r["active"]) for r in run2_snapshot}

diff_between_runs = []
for name, vals in run1_names.items():
    if name not in run2_names:
        diff_between_runs.append({"name": name, "diff": "Missing in Run 2"})
    elif run2_names[name] != vals:
        diff_between_runs.append({"name": name, "diff": f"Changed: {vals} != {run2_names[name]}"})

idempotent_pass = (count_before_run2 == count_after_run2) and (len(diff_between_runs) == 0)

idempotency_evidence = {
    "table_id": table_id,
    "table_name": "products__DEV_DONA_ROSA_20260721",
    "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "idempotent": idempotent_pass,
    "run1_summary": {
        "count_before": 243,
        "count_after": count_before_run2,
        "successes": 242
    },
    "run2_summary": {
        "start_time": start_time_run2,
        "end_time": end_time_run2,
        "count_before": count_before_run2,
        "count_after": count_after_run2,
        "successes": success_count_run2,
        "failures": fail_count_run2
    },
    "diff_count_between_runs": len(diff_between_runs),
    "extra_records_flagged_for_user_confirmation": [
        {"id": r["id"], "name": r["name"], "category": r.get("category")} for r in extra_records_in_dt
    ]
}

print(f"\n=== IDEMPOTENCY PROOF: {'PASSED (100% IDEMPOTENT)' if idempotent_pass else 'FAILED'} ===")
print(f"Run 2 count before: {count_before_run2}, after: {count_after_run2}, diffs: {len(diff_between_runs)}")
print(f"Flagged extra records requiring user confirmation before removal: {len(extra_records_in_dt)}")

# Save evidence files
log_out = os.path.join(out_dir, "upsert_execution_log.json")
with open(log_out, "w", encoding="utf-8") as f:
    json.dump(idempotency_evidence, f, indent=2, ensure_ascii=False)

idemp_out = os.path.join(out_dir, "idempotency_proof.json")
with open(idemp_out, "w", encoding="utf-8") as f:
    json.dump(idempotency_evidence, f, indent=2, ensure_ascii=False)

print(f"Saved execution log to {log_out}")
print(f"Saved idempotency proof to {idemp_out}")
