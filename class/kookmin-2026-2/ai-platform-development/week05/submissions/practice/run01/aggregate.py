"""Per-warehouse aggregation task (a parallel-capable DAG node).

aggregate_warehouse(wh_id) reads practice/data/warehouse-<wh_id>.md via the
shared parser, computes:
  - total     : sum of all item quantities in that warehouse
  - per_item  : quantity per item (item order preserved from the source file)
  - low_stock : items whose warehouse-row qty is < 5 (low_stock_basis = warehouse_row)

...and writes the result to a warehouse-specific intermediate file
(intermediate_<wh_id>.json) in this run01/ directory.

Each invocation is fully self-contained: aggregate_warehouse('a'),
aggregate_warehouse('b') and aggregate_warehouse('c') share no state and can
run in any order or in parallel.

Runnable standalone:  python aggregate.py a b c
"""

import json
import os
import sys

import parser

LOW_STOCK_THRESHOLD = 5  # low stock = warehouse row qty strictly less than 5
LOW_STOCK_BASIS = "warehouse_row"

HERE = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.normpath(
    os.path.join(HERE, "..", "..", "..", "practice", "data")
)


def _data_path(wh_id):
    return os.path.join(DATA_DIR, "warehouse-{}.md".format(wh_id.lower()))


def _intermediate_path(wh_id):
    return os.path.join(HERE, "intermediate_{}.json".format(wh_id.lower()))


def aggregate_warehouse(wh_id):
    """Aggregate a single warehouse and persist its intermediate JSON.

    Returns the aggregation dict that was written to disk.
    """
    wh_id = wh_id.lower()
    parsed = parser.parse_warehouse(_data_path(wh_id))
    items = parsed["items"]

    total = sum(entry["qty"] for entry in items)

    per_item = {}
    for entry in items:
        # Sum in case an item appears on more than one row within the warehouse.
        per_item[entry["item"]] = per_item.get(entry["item"], 0) + entry["qty"]

    low_stock = [
        {"item": entry["item"], "qty": entry["qty"]}
        for entry in items
        if entry["qty"] < LOW_STOCK_THRESHOLD
    ]

    result = {
        "warehouse": wh_id,
        "total": total,
        "per_item": per_item,
        "low_stock": low_stock,
        "low_stock_basis": LOW_STOCK_BASIS,
    }

    out_path = _intermediate_path(wh_id)
    with open(out_path, "w", encoding="utf-8") as fh:
        json.dump(result, fh, ensure_ascii=False, indent=2)

    return result


if __name__ == "__main__":
    targets = sys.argv[1:] or ["a", "b", "c"]
    for wid in targets:
        res = aggregate_warehouse(wid)
        print(json.dumps(res, ensure_ascii=False, indent=2))
