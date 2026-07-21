import json
import csv
import hashlib
import os
import datetime

corr_csv = r"c:\Users\Administrator\Desktop\N8N_Pizzaria\1-etapa\output\products.corrected.csv"
out_dir = r"c:\Users\Administrator\Desktop\N8N_Pizzaria\2-etapa\output"
os.makedirs(out_dir, exist_ok=True)

with open(corr_csv, mode="r", encoding="utf-8") as f:
    items = list(csv.DictReader(f))

# Sort items deterministically by category then name
items_sorted = sorted(items, key=lambda x: (x["category"], x["name"]))

# Compute catalog_hash SHA-256
canonical_repr = json.dumps(items_sorted, ensure_ascii=False, sort_keys=True)
catalog_hash = hashlib.sha256(canonical_repr.encode("utf-8")).hexdigest()

timestamp_str = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%d_%H%M%S")
source_version = f"v_{timestamp_str}"
run_id = f"run_{timestamp_str}_{catalog_hash[:8]}"

print(f"Loaded {len(items)} canonical products.")
print(f"Computed SHA-256 Catalog Hash: {catalog_hash}")
print(f"Generated Source Version: {source_version}")
print(f"Generated Run ID: {run_id}")

config_payload = {
    "file_name": "product_restaurant_list",
    "source_version": source_version,
    "catalog_hash": catalog_hash,
    "run_id": run_id,
    "total_products": len(items),
    "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat()
}

config_out = os.path.join(out_dir, "ingest_config.json")
with open(config_out, "w", encoding="utf-8") as f:
    json.dump(config_payload, f, indent=2, ensure_ascii=False)

print(f"Saved ingest config to {config_out}")
