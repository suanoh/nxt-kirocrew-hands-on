"""Integration/merge task -- the DAG join node.

integrate() depends on all three per-warehouse aggregation runs having
completed (intermediate_a.json, intermediate_b.json, intermediate_c.json).
It reads those three intermediate files and combines them into:

  - per_warehouse : {warehouse_id: total}          -- each warehouse's total
  - per_item      : {item: total_qty_across_all}   -- per-item aggregate totals
  - low_stock     : [{warehouse, item, qty}, ...]  -- combined low-stock list
  - warehouse_totals order and per_item order follow the order warehouses/items
    are first seen (a -> b -> c), keeping output deterministic.

low_stock_basis stays "warehouse_row": every low-stock entry comes straight
from an intermediate file's low_stock list, so each satisfies warehouse-row
qty < 5 by construction.

Runnable standalone:  python integrate.py
"""

import json
import os

WAREHOUSES = ["a", "b", "c"]
LOW_STOCK_BASIS = "warehouse_row"

HERE = os.path.dirname(os.path.abspath(__file__))


def _intermediate_path(wh_id):
    return os.path.join(HERE, "intermediate_{}.json".format(wh_id.lower()))


def _load_intermediate(wh_id):
    path = _intermediate_path(wh_id)
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def integrate():
    """Read the three intermediate files and merge them.

    Returns a dict with per-warehouse totals, per-item aggregate totals across
    all warehouses, and the combined low-stock list.
    """
    parts = {wid: _load_intermediate(wid) for wid in WAREHOUSES}

    # Per-warehouse totals (order: a, b, c).
    per_warehouse = {wid: parts[wid]["total"] for wid in WAREHOUSES}

    # Per-item aggregate totals across all warehouses (first-seen order).
    per_item = {}
    for wid in WAREHOUSES:
        for item, qty in parts[wid]["per_item"].items():
            per_item[item] = per_item.get(item, 0) + qty

    # Combined low-stock list, tagged with the owning warehouse.
    low_stock = []
    for wid in WAREHOUSES:
        for entry in parts[wid]["low_stock"]:
            low_stock.append(
                {
                    "warehouse": wid,
                    "item": entry["item"],
                    "qty": entry["qty"],
                }
            )

    return {
        "per_warehouse": per_warehouse,
        "per_item": per_item,
        "low_stock": low_stock,
        "low_stock_basis": LOW_STOCK_BASIS,
    }


SOURCE_FILES = ["warehouse-a.md", "warehouse-b.md", "warehouse-c.md"]
THRESHOLD = 5
RESULT_PATH = os.path.join(HERE, "result.json")


def build_result():
    """Shape the merged data into the result.json schema (practice/출력형식.md).

    Uses low_stock_basis == "warehouse_row", so each low-stock entry carries
    warehouse, item and quantity, taken straight from the per-warehouse
    intermediate files (each already satisfies warehouse-row qty < 5).
    """
    merged = integrate()

    warehouse_totals = {
        wid.upper(): merged["per_warehouse"][wid] for wid in WAREHOUSES
    }
    item_totals = dict(merged["per_item"])
    grand_total = sum(warehouse_totals.values())

    low_stock = [
        {
            "warehouse": entry["warehouse"].upper(),
            "item": entry["item"],
            "quantity": entry["qty"],
        }
        for entry in merged["low_stock"]
    ]

    return {
        "source_files": list(SOURCE_FILES),
        "warehouse_totals": warehouse_totals,
        "item_totals": item_totals,
        "grand_total": grand_total,
        "low_stock_basis": LOW_STOCK_BASIS,
        "threshold": THRESHOLD,
        "low_stock": low_stock,
    }


def write_result(path=RESULT_PATH):
    """Write result.json as UTF-8 directly in Python (avoids Korean corruption)."""
    result = build_result()
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(result, fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    return path


REPORT_PATH = os.path.join(HERE, "report.md")


def build_report():
    """Render the integrated result as a human-readable Markdown report.

    Contains per-warehouse totals, per-item aggregate quantities, and the
    low-stock list -- all sourced from result.json's shaped data.
    """
    result = build_result()

    lines = []
    lines.append("# 창고 A·B·C 재고 집계 리포트")
    lines.append("")
    lines.append("입력 파일: " + ", ".join("`{}`".format(f) for f in result["source_files"]))
    lines.append("")
    lines.append(
        "저재고 기준: 원본 창고 행(warehouse row) 수량 < {} "
        "(low_stock_basis = `{}`)".format(result["threshold"], result["low_stock_basis"])
    )
    lines.append("")

    # 창고별 합계
    lines.append("## 창고별 합계")
    lines.append("")
    lines.append("| 창고 | 합계 |")
    lines.append("| --- | ---: |")
    for wid, total in result["warehouse_totals"].items():
        lines.append("| {} | {} |".format(wid, total))
    lines.append("| **총합계** | **{}** |".format(result["grand_total"]))
    lines.append("")

    # 품목별 총수량
    lines.append("## 품목별 총수량")
    lines.append("")
    lines.append("| 품목 | 총수량 |")
    lines.append("| --- | ---: |")
    for item, qty in result["item_totals"].items():
        lines.append("| {} | {} |".format(item, qty))
    lines.append("")

    # 저재고 목록
    lines.append("## 저재고 목록 (수량 < {})".format(result["threshold"]))
    lines.append("")
    if result["low_stock"]:
        lines.append("| 창고 | 품목 | 수량 |")
        lines.append("| --- | --- | ---: |")
        for entry in result["low_stock"]:
            lines.append(
                "| {} | {} | {} |".format(
                    entry["warehouse"], entry["item"], entry["quantity"]
                )
            )
    else:
        lines.append("저재고 항목이 없습니다.")
    lines.append("")

    return "\n".join(lines)


def write_report(path=REPORT_PATH):
    """Write report.md as UTF-8 directly in Python (preserves Korean)."""
    report = build_report()
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(report)
    return path


if __name__ == "__main__":
    out = write_result()
    print("wrote {}".format(out))
    with open(out, "r", encoding="utf-8") as fh:
        print(fh.read())
    rpt = write_report()
    print("wrote {}".format(rpt))
