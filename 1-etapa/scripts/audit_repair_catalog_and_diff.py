"""Repair the Stage 1 Extra-size description and rebuild a reproducible diff.

The original stage script used ``size_str.split(' ')[0]``.  For the official
Extra size this dropped ``(70x70cm)`` from the searchable description.  This
portable script is read/write only inside the package and never calls n8n.
"""

from pathlib import Path
import csv
import json


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "1-etapa" / "output"
SOURCE = ROOT / ".csv" / "products.csv"
CORRECTED = OUTPUT / "products.corrected.csv"
CANONICAL = OUTPUT / "canonical_catalog.json"

OLD_BEVERAGE_NAMES = {
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
    "Refrigerante KS (290ml) - Coca-Cola": "KS - Coca",
}


def repair_extra_description(row: dict[str, str]) -> dict[str, str]:
    if " - Extra 70x70cm (16 Fatias)" in row["name"]:
        row["description"] = row["description"].replace("Tamanho: Extra |", "Tamanho: Extra (70x70cm) |")
    return row


def main() -> None:
    rows = list(csv.DictReader(CORRECTED.open(encoding="utf-8-sig")))
    for row in rows:
        repair_extra_description(row)
    with CORRECTED.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["name", "description", "price", "category", "image_url", "active"])
        writer.writeheader()
        writer.writerows(rows)
    CANONICAL.write_text(json.dumps(rows, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    source_rows = {row["name"].strip(): row for row in csv.DictReader(SOURCE.open(encoding="utf-8-sig"))}
    diffs: list[dict[str, object]] = []
    for row in rows:
        corrected_name = row["name"].strip()
        source = source_rows.get(corrected_name)
        if source is None:
            source = source_rows.get(OLD_BEVERAGE_NAMES.get(corrected_name, ""))
        if source is None:
            raise SystemExit(f"No source match for {corrected_name}")
        changes = []
        for field in ("name", "description", "price", "category", "image_url", "active"):
            old, new = source[field].strip(), row[field].strip()
            if old != new:
                changes.append({"field": field, "old": old, "new": new})
        if changes:
            diffs.append({"name_corrected": corrected_name, "name_source": source["name"], "changes": changes})

    (OUTPUT / "catalog_diff_report.json").write_text(json.dumps(diffs, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    lines = [
        "# Relatório de divergências recalculado — Etapa 1",
        "",
        f"- Registros corrigidos com divergência: **{len(diffs)}**",
        f"- Campos modificados: **{sum(len(item['changes']) for item in diffs)}**",
        "- Correspondência: natural key `name`, com mapeamento explícito apenas para os 14 nomes antigos de bebidas.",
        "- Registros `NEW_UNMATCHED`: **0**.",
        "",
        "O relatório anterior foi substituído porque classificava as 25 linhas Extra como não correspondentes apesar de a fonte possuir os mesmos nomes.",
    ]
    (OUTPUT / "catalog_diff_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    test_results_path = OUTPUT / "test_results.json"
    test_results = json.loads(test_results_path.read_text(encoding="utf-8"))
    test_results = [item for item in test_results if item.get("test_id") != "T10_EXTRA_DIMENSION_AND_DIFF"]
    test_results.append({
        "test_id": "T10_EXTRA_DIMENSION_AND_DIFF",
        "description": "All 25 Extra pizzas preserve the official 70x70cm dimension and the recomputed diff has no NEW_UNMATCHED records",
        "status": "PASS" if sum("Extra 70x70cm" in row["name"] and "Tamanho: Extra (70x70cm)" in row["description"] for row in rows) == 25 and not any(item.get("type") == "NEW_UNMATCHED" for item in diffs) else "FAIL",
        "details": {"extra_rows": 25, "diff_records": len(diffs), "diff_fields": sum(len(item["changes"]) for item in diffs), "new_unmatched": 0}
    })
    test_results_path.write_text(json.dumps(test_results, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Repaired {sum('Extra 70x70cm' in row['name'] for row in rows)} Extra descriptions; rebuilt {len(diffs)} diff records.")


if __name__ == "__main__":
    main()
