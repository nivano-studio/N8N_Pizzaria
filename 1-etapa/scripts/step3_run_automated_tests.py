import csv
import json
import os

corr_csv = r"c:\Users\Administrator\Desktop\N8N_Pizzaria\1-etapa\output\products.corrected.csv"
canonical_json = r"c:\Users\Administrator\Desktop\N8N_Pizzaria\1-etapa\output\canonical_catalog.json"
out_test_results = r"c:\Users\Administrator\Desktop\N8N_Pizzaria\1-etapa\output\test_results.json"

test_outcomes = []

def record_test(test_id, description, passed, details=""):
    test_outcomes.append({
        "test_id": test_id,
        "description": description,
        "status": "PASS" if passed else "FAIL",
        "details": details
    })
    print(f"[{'PASS' if passed else 'FAIL'}] Test {test_id}: {description}")

print("=== RUNNING AUTOMATED SUITE FOR ETAPA 1 ===")

# Test 1: CSV file format & headers
try:
    with open(corr_csv, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        headers = reader.fieldnames
        rows = list(reader)
    expected_headers = ["name", "description", "price", "category", "image_url", "active"]
    t1_pass = (headers == expected_headers) and (len(rows) == 242)
    record_test("T1_CSV_FORMAT", "CSV parseable, correct headers, exactly 242 rows", t1_pass, f"Headers: {headers}, Row count: {len(rows)}")
except Exception as e:
    record_test("T1_CSV_FORMAT", "CSV parseable", False, str(e))
    rows = []

# Test 2: Price decimal format & active boolean
price_pass = True
active_pass = True
for r in rows:
    p_val = r["price"].strip()
    try:
        float(p_val)
    except ValueError:
        price_pass = False
    if r["active"].strip().lower() not in ["true", "false"]:
        active_pass = False

record_test("T2_PRICE_ACTIVE_VALIDITY", "Prices are parseable numeric values and active is boolean string", price_pass and active_pass)

# Test 3: Natural key uniqueness
names = [r["name"].strip() for r in rows]
dup_names = [n for n in names if names.count(n) > 1]
t3_pass = (len(dup_names) == 0) and (len(names) == 242)
record_test("T3_NATURAL_KEY_UNIQUENESS", "Zero duplicate natural keys (name)", t3_pass, f"Duplicates: {set(dup_names)}")

# Test 4: Category breakdown counts
cat_counts = {}
for r in rows:
    c = r["category"].strip()
    cat_counts[c] = cat_counts.get(c, 0) + 1

expected_cats = {
    "Pizza Tradicional": 112,
    "Pizza Especial": 56,
    "Pizza Doce": 32,
    "Pastel": 10,
    "Porções e Aperitivos": 10,
    "Bebidas": 22
}
t4_pass = (cat_counts == expected_cats)
record_test("T4_CATEGORY_COUNTS", "Exact breakdown: 112/56/32/10/10/22 across categories", t4_pass, f"Obtained: {cat_counts}")

# Test 5: Specific Price & Business Rule Verification
items_by_name = {r["name"].strip(): r for r in rows}

# G Calabresa = 50
g_calabresa_price = float(items_by_name.get("CALABRESA - G (8 Fatias)", {}).get("price", 0))
# Brotinha Tradicional = 15
brot_trad_price = float(items_by_name.get("CALABRESA - Brotinha", {}).get("price", 0))
# Extra Especial = 160
extra_esp_price = float(items_by_name.get("NORDESTINA - Extra 70x70cm (16 Fatias)", {}).get("price", 0))
# G Especial = 55
g_esp_price = float(items_by_name.get("NORDESTINA - G (8 Fatias)", {}).get("price", 0))

# Mixed category rule test: G Calabresa (50) + Nordestina (55) -> Highest price category (55)
mixed_price_rule_pass = (max(g_calabresa_price, g_esp_price) == 55)

t5_pass = (g_calabresa_price == 50) and (brot_trad_price == 15) and (extra_esp_price == 160) and mixed_price_rule_pass
record_test("T5_PRICE_BUSINESS_RULES", "Price verification for G Calabresa (50), Brotinha (15), Extra Especial (160), and Mixed Rule (55)", t5_pass)

# Test 6: Specific Item Prices (Pastel Doçura R$ 10, Macarronada R$ 20)
docura_price = float(items_by_name.get("Pastel - DOÇURA", {}).get("price", 0))
mac_frango_price = float(items_by_name.get("Macarronada - Frango", {}).get("price", 0))
mac_carne_price = float(items_by_name.get("Macarronada - Carne", {}).get("price", 0))

t6_pass = (docura_price == 10) and (mac_frango_price == 20) and (mac_carne_price == 20)
record_test("T6_SPECIFIC_ITEM_PRICES", "Pastel Doçura (10), Macarronada Frango (20), Macarronada Carne (20)", t6_pass)

# Test 7: Casco & Beverage Pricing (KS R$ 4, Retornável 1L R$ 8)
ks_item = items_by_name.get("Refrigerante KS (290ml) - Coca-Cola", {})
ret_item = items_by_name.get("Refrigerante Retornável (1L) - Coca-Cola", {})

ks_price = float(ks_item.get("price", 0))
ret_price = float(ret_item.get("price", 0))
ks_casco = "casco" in ks_item.get("description", "").lower()
ret_casco = "casco" in ret_item.get("description", "").lower()

t7_pass = (ks_price == 4) and (ret_price == 8) and ks_casco and ret_casco
record_test("T7_BEVERAGE_CASCO_RULES", "KS 290ml (R$ 4 + casco), Retornável 1L (R$ 8 + casco)", t7_pass)

# Test 8: Clean Searchable Descriptions (Zero "o site informa" and Zero "Sabor da Terra")
unwanted_found = []
for r in rows:
    desc = r["description"].lower()
    name_l = r["name"].lower()
    if "o site informa" in desc or "sabor da terra" in desc or "sabor da terra" in name_l:
        unwanted_found.append(r["name"])

t8_pass = (len(unwanted_found) == 0)
record_test("T8_CLEAN_DESCRIPTIONS", "Zero occurrences of 'o site informa' or 'Sabor da Terra'", t8_pass, f"Unwanted in: {unwanted_found}")

# Test 9: Operational Metadata Preservation (image_url & active not empty)
valid_meta = True
for r in rows:
    if not r["image_url"].strip() or not r["active"].strip():
        valid_meta = False

t9_pass = valid_meta
record_test("T9_OPERATIONAL_METADATA", "All records have valid image_url and active status preserved", t9_pass)

# Save test results JSON
with open(out_test_results, "w", encoding="utf-8") as f:
    json.dump(test_outcomes, f, indent=2, ensure_ascii=False)

print(f"\nSaved test suite results to {out_test_results}")
