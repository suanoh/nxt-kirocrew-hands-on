# -*- coding: utf-8 -*-
"""Integration task for the warehouse inventory pipeline.

Depends on the three parallel per-warehouse aggregation tasks. Reads the three
intermediate files (warehouse-a/b/c.result.json), merges them into per-item
total quantities across all warehouses, determines low-stock items
(item_total < threshold), and writes result.json and report.md conforming to
practice/출력형식.md.

Invariants (per practice/출력형식.md):
  - low_stock_basis is always "item_total"
  - threshold is always 5
  - low_stock = items whose item_total < 5 (5 is NOT low stock)
  - item_totals[item] == sum over warehouses of that item's qty
  - warehouses[w].total == sum of warehouses[w].items values

JSON is written from Python with UTF-8 + ensure_ascii=False (per user pref).
"""

import os

from warehouse_lib import load_json, write_json

LOW_STOCK_BASIS = "item_total"
THRESHOLD = 5

HERE = os.path.dirname(os.path.abspath(__file__))

# The three per-warehouse intermediate files, in canonical order.
WAREHOUSE_KEYS = ["warehouse-a", "warehouse-b", "warehouse-c"]
INTERMEDIATE_FILES = {k: os.path.join(HERE, k + ".result.json") for k in WAREHOUSE_KEYS}

RESULT_JSON = os.path.join(HERE, "result.json")
REPORT_MD = os.path.join(HERE, "report.md")


def build_result():
    """Read the three intermediate files and build the result dict."""
    warehouses = {}
    item_totals = {}

    for key in WAREHOUSE_KEYS:
        agg = load_json(INTERMEDIATE_FILES[key])
        items = agg["items"]
        # Re-derive total from items to enforce invariant 5, rather than
        # trusting the stored value blindly.
        total = sum(items.values())
        assert total == agg["total"], (
            f"{key}: stored total {agg['total']} != sum of items {total}"
        )
        warehouses[key] = {"total": total, "items": items}
        for item, qty in items.items():
            item_totals[item] = item_totals.get(item, 0) + qty

    low_stock = sorted(
        item for item, total in item_totals.items() if total < THRESHOLD
    )

    return {
        "warehouses": warehouses,
        "item_totals": item_totals,
        "low_stock": low_stock,
        "low_stock_basis": LOW_STOCK_BASIS,
        "threshold": THRESHOLD,
    }


def build_report(result):
    """Build the human-readable report.md text from the result dict."""
    warehouses = result["warehouses"]
    item_totals = result["item_totals"]
    low_stock = result["low_stock"]

    lines = []
    # 2.1 제목 및 개요
    lines.append("# 창고 재고 집계 보고서")
    lines.append("")
    lines.append(
        "창고 A·B·C의 재고를 코드로 읽어 집계하고, 품목별 전체 합산 수량과 "
        "저재고 품목을 산출한 보고서다."
    )
    lines.append("")
    lines.append(
        f"- **저재고 판정 기준 (low_stock_basis)**: `{result['low_stock_basis']}` "
        "(창고 전체 합산 수량 기준)"
    )
    lines.append(
        f"- **임계값 (threshold)**: `{result['threshold']}` "
        f"(합산 수량이 {result['threshold']} 미만이면 저재고)"
    )
    lines.append("")

    # 2.2 창고별 총계
    lines.append("## 창고별 총계 (Per-warehouse totals)")
    lines.append("")
    lines.append("| 창고 | 총 수량 |")
    lines.append("|------|---------|")
    for key in WAREHOUSE_KEYS:
        lines.append(f"| {key} | {warehouses[key]['total']} |")
    lines.append("")

    # 2.3 품목별 총계 표
    lines.append("## 품목별 총계 (Per-item totals)")
    lines.append("")
    lines.append("| 품목 | 총 수량 |")
    lines.append("|------|---------|")
    for item in sorted(item_totals):
        lines.append(f"| {item} | {item_totals[item]} |")
    lines.append("")

    # 2.4 저재고 목록
    lines.append("## 저재고 목록 (Low-stock list)")
    lines.append("")
    lines.append(f"합산 수량이 {result['threshold']} 미만인 품목:")
    lines.append("")
    if low_stock:
        for item in low_stock:
            lines.append(f"- {item} ({item_totals[item]})")
    else:
        lines.append("- (없음)")
    lines.append("")

    # 2.5 기준 및 임계값
    lines.append("## 기준 및 임계값 (Basis and threshold)")
    lines.append("")
    lines.append(f"- `low_stock_basis`: `{result['low_stock_basis']}`")
    lines.append(f"- `threshold`: `{result['threshold']}`")
    lines.append("")

    return "\n".join(lines)


def main():
    result = build_result()
    write_json(result, RESULT_JSON)

    report = build_report(result)
    with open(REPORT_MD, "w", encoding="utf-8") as f:
        f.write(report)

    print("Wrote:", RESULT_JSON)
    print("Wrote:", REPORT_MD)
    print("item_totals:", result["item_totals"])
    print("low_stock:", result["low_stock"])


if __name__ == "__main__":
    main()
