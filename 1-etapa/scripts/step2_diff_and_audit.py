import csv
import json
import os

ref_csv = r"c:\Users\Administrator\Desktop\N8N_Pizzaria\.csv\products.csv"
corr_csv = r"c:\Users\Administrator\Desktop\N8N_Pizzaria\1-etapa\output\products.corrected.csv"

out_dir = r"c:\Users\Administrator\Desktop\N8N_Pizzaria\1-etapa\output"

with open(ref_csv, mode="r", encoding="utf-8-sig") as f:
    ref_rows = list(csv.DictReader(f))

with open(corr_csv, mode="r", encoding="utf-8") as f:
    corr_rows = list(csv.DictReader(f))

print(f"Reference CSV rows: {len(ref_rows)}")
print(f"Corrected CSV rows: {len(corr_rows)}")

diffs = []
field_changes_count = 0

old_bebida_map = {
    "Coca-Cola 2 Litros - Original": "Coca-Cola 2L - Original",
    "Coca-Cola 2 Litros - Zero": "Coca-Cola 2L - Zero",
    "Refrigerante 2 Litros - Guaraná Jesus": "Refrigerante 2L - Jesus",
    "Refrigerante 2 Litros - Guaraná": "Refrigerante 2L - Guaraná",
    "Refrigerante Retornável (1L) - Coca-Cola": "Refrigerante Retornável - Coca",
    "Refrigerante 1 Litro - Coca-Cola": "Refrigerante 1L - Coca",
    "Refrigerante 1 Litro - Coca-Cola Zero": "Refrigerante 1L - Coca Zero",
    "Refrigerante 1 Litro - Guaraná Jesus": "Refrigerante 1L - Jesus",
    "Refrigerante 1 Litro - Guaraná": "Refrigerante 1L - Guaraná",
    "Refrigerante Lata - Coca-Cola": "Refrigerante Lata - Coca",
    "Refrigerante Lata - Coca-Cola Zero": "Refrigerante Lata - Coca Zero",
    "Refrigerante Lata - Guaraná Jesus": "Refrigerante Lata - Jesus",
    "Refrigerante Lata - Guaraná": "Refrigerante Lata - Guaraná",
    "Refrigerante KS (290ml) - Coca-Cola": "KS - Coca"
}

ref_dict_by_name = {r["name"].strip(): r for r in ref_rows}

for corr in corr_rows:
    c_name = corr["name"].strip()
    ref_match = ref_dict_by_name.get(c_name)
    
    if not ref_match and c_name in old_bebida_map:
        ref_match = ref_dict_by_name.get(old_bebida_map[c_name])
        
    if not ref_match:
        diffs.append({
            "type": "NEW_UNMATCHED",
            "name_corrected": c_name,
            "name_reference": "N/A",
            "changes": [{"field": "all", "old": "N/A", "new": c_name, "reason": "No match found in reference"}]
        })
    else:
        row_diff = {
            "name_corrected": c_name,
            "name_reference": ref_match["name"],
            "changes": []
        }
        
        if c_name != ref_match["name"]:
            row_diff["changes"].append({
                "field": "name",
                "old": ref_match["name"],
                "new": c_name,
                "reason": "Restored full canonical name (brand, volume, packaging)"
            })
            
        if corr["description"].strip() != ref_match["description"].strip():
            row_diff["changes"].append({
                "field": "description",
                "old": ref_match["description"],
                "new": corr["description"],
                "reason": "Removed 'o site informa' / sanitized unverified claims"
            })
            
        if str(corr["price"]).strip() != str(ref_match["price"]).strip():
            row_diff["changes"].append({
                "field": "price",
                "old": ref_match["price"],
                "new": corr["price"],
                "reason": "Corrected price format/value"
            })
            
        if corr["category"].strip() != ref_match["category"].strip():
            row_diff["changes"].append({
                "field": "category",
                "old": ref_match["category"],
                "new": corr["category"],
                "reason": "Category adjustment"
            })
            
        if corr["image_url"].strip() != ref_match["image_url"].strip():
            row_diff["changes"].append({
                "field": "image_url",
                "old": ref_match["image_url"],
                "new": corr["image_url"],
                "reason": "Preserved operational asset URL"
            })
            
        if corr["active"].strip().lower() != ref_match["active"].strip().lower():
            row_diff["changes"].append({
                "field": "active",
                "old": ref_match["active"],
                "new": corr["active"],
                "reason": "Preserved operational active flag"
            })
            
        if row_diff["changes"]:
            field_changes_count += len(row_diff["changes"])
            diffs.append(row_diff)

print(f"\n--- AUDIT SUMMARY ---")
print(f"Total modified records: {len(diffs)}")
print(f"Total individual field changes: {field_changes_count}")

diff_json = os.path.join(out_dir, "catalog_diff_report.json")
with open(diff_json, "w", encoding="utf-8") as f:
    json.dump(diffs, f, indent=2, ensure_ascii=False)
print(f"Saved diff report to {diff_json}")

diff_md = os.path.join(out_dir, "catalog_diff_report.md")
md_lines = [
    "# Relatório de Divergências e Audit do Catálogo (Etapa 1)\n",
    f"- **Total de Registros Inspecionados:** {len(corr_rows)}",
    f"- **Registros com Alterações Comprovadas:** {len(diffs)}",
    f"- **Total de Campos Modificados:** {field_changes_count}\n",
    "## Detalhamento de Alterações por Registro\n"
]

for d in diffs:
    md_lines.append(f"### {d['name_corrected']}")
    if d['name_reference'] != d['name_corrected']:
        md_lines.append(f"- **Nome Original:** `{d['name_reference']}`")
    for change in d['changes']:
        md_lines.append(f"- **Campo `{change['field']}`:** `{change['old']}` ➔ `{change['new']}` *(Motivo: {change['reason']})*")
    md_lines.append("")

with open(diff_md, "w", encoding="utf-8") as f:
    f.write("\n".join(md_lines))
print(f"Saved diff report Markdown to {diff_md}")
