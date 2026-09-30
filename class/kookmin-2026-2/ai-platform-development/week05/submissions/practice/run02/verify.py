# -*- coding: utf-8 -*-
"""Verify run02 outputs against the task's acceptance criteria.

Recomputes the expected aggregation directly from the source markdown files
(practice/data/warehouse-*.md) using warehouse_lib, then asserts that every
produced artifact (intermediate files, result.json, report.md) is present and
consistent with 출력형식.md. Exits non-zero on the first failed assertion so
the pipeline fails loudly.
"""

import json
import os
import re
import sys

import warehouse_lib as wl

RUN_DIR = os.path.dirname(os.path.abspath(__file__))
# .../submissions/practice/run02 -> project root
PROJECT_ROOT = os.path.abspath(os.path.join(RUN_DIR, "..", "..", ".."))
DATA_DIR = os.path.join(PROJECT_ROOT, "practice", "data")
SPEC_PATH = os.path.join(PROJECT_ROOT, "practice", "출력형식.md")

WAREHOUSES = ["warehouse-a", "warehouse-b", "warehouse-c"]
THRESHOLD = 5

checks = []


def check(cond, msg):
    status = "PASS" if cond else "FAIL"
    checks.append((cond, msg))
    print(f"[{status}] {msg}")
    if not cond:
        raise AssertionError(msg)


def load(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


# 1. Recompute expected values from source of truth.
expected_wh = {}
for w in WAREHOUSES:
    md = os.path.join(DATA_DIR, f"{w}.md")
    check(os.path.isfile(md), f"source file exists: {md}")
    expected_wh[w] = wl.aggregate_warehouse(md)

expected_item_totals = {}
for w in WAREHOUSES:
    for item, qty in expected_wh[w]["items"].items():
        expected_item_totals[item] = expected_item_totals.get(item, 0) + qty
expected_low_stock = sorted(
    i for i, t in expected_item_totals.items() if t < THRESHOLD
)

# 2. run02/ contains calculation code, 3 intermediate files, result.json, report.md.
code_files = ["warehouse_lib.py", "aggregate_a.py", "aggregate_b.py",
              "aggregate_c.py", "integrate.py"]
for f in code_files:
    check(os.path.isfile(os.path.join(RUN_DIR, f)),
          f"calculation code present: {f}")

intermediate_paths = {
    w: os.path.join(RUN_DIR, f"{w}.result.json") for w in WAREHOUSES
}
for w, p in intermediate_paths.items():
    check(os.path.isfile(p), f"intermediate file present: {w}.result.json")

result_path = os.path.join(RUN_DIR, "result.json")
report_path = os.path.join(RUN_DIR, "report.md")
check(os.path.isfile(result_path), "result.json present")
check(os.path.isfile(report_path), "report.md present")

# 3. Each intermediate file holds that warehouse's total and per-item quantities.
for w, p in intermediate_paths.items():
    data = wl.load_json(p)
    check("total" in data and "items" in data,
          f"{w} intermediate has 'total' and 'items'")
    check(data["items"] == expected_wh[w]["items"],
          f"{w} intermediate items match source")
    check(data["total"] == expected_wh[w]["total"],
          f"{w} intermediate total matches source")
    check(data["total"] == sum(data["items"].values()),
          f"{w} total == sum(items)")

# 4. result.json conforms to spec.
result = wl.load_json(result_path)
for key in ["warehouses", "item_totals", "low_stock",
            "low_stock_basis", "threshold"]:
    check(key in result, f"result.json has top-level key '{key}'")

check(result["low_stock_basis"] == "item_total",
      "result.json low_stock_basis == 'item_total'")
check(result["threshold"] == 5, "result.json threshold == 5")

check(set(result["warehouses"].keys()) == set(WAREHOUSES),
      "result.json warehouses cover A, B, C")
for w in WAREHOUSES:
    rw = result["warehouses"][w]
    check(rw["items"] == expected_wh[w]["items"],
          f"result.json warehouses[{w}].items match source")
    check(rw["total"] == expected_wh[w]["total"],
          f"result.json warehouses[{w}].total match source")
    check(rw["total"] == sum(rw["items"].values()),
          f"result.json warehouses[{w}].total == sum(items)")

# 5. item_totals == sum across A, B, C.
check(result["item_totals"] == expected_item_totals,
      "result.json item_totals equal sum across A, B, C")
for item, total in result["item_totals"].items():
    s = sum(expected_wh[w]["items"].get(item, 0) for w in WAREHOUSES)
    check(total == s, f"item_total[{item}] == sum across warehouses ({s})")

# 6. low_stock is exactly the items with item_total < 5, sorted.
check(sorted(result["low_stock"]) == expected_low_stock,
      f"low_stock == items with item_total < 5 ({expected_low_stock})")
check(result["low_stock"] == expected_low_stock,
      "low_stock is sorted ascending")
for item in result["item_totals"]:
    in_low = item in result["low_stock"]
    should = result["item_totals"][item] < THRESHOLD
    check(in_low == should,
          f"{item} low-stock membership matches item_total < 5")

# 7. report.md conformance & invariants.
report = load(report_path)
check("item_total" in report and "threshold" in report.lower() or
      "임계값" in report,
      "report.md mentions low_stock_basis/threshold basis")
check("5" in report, "report.md states threshold value 5")
for w in WAREHOUSES:
    check(str(expected_wh[w]["total"]) in report,
          f"report.md contains {w} total {expected_wh[w]['total']}")
for item in expected_low_stock:
    check(re.search(rf"{re.escape(item)}\b", report) is not None,
          f"report.md lists low-stock item '{item}'")

# 8. Non-negative integer quantities everywhere.
for w in WAREHOUSES:
    for item, qty in result["warehouses"][w]["items"].items():
        check(isinstance(qty, int) and qty >= 0,
              f"{w}.{item} qty is non-negative int")
for item, qty in result["item_totals"].items():
    check(isinstance(qty, int) and qty >= 0,
          f"item_total[{item}] is non-negative int")

passed = sum(1 for c, _ in checks if c)
print(f"\nAll {passed} assertions PASSED.")
print(f"item_totals = {json.dumps(result['item_totals'], ensure_ascii=False)}")
print(f"low_stock   = {result['low_stock']}")
sys.exit(0)
