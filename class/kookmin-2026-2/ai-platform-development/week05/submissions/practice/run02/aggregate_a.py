# -*- coding: utf-8 -*-
"""Aggregate warehouse A into an intermediate JSON file.

Independent of warehouses B and C. Imports the shared warehouse_lib module,
reads practice/data/warehouse-a.md, computes warehouse A's total and per-item
quantities, and writes submissions/practice/run02/warehouse-a.result.json
(UTF-8, no ASCII escaping).
"""

import os

import warehouse_lib

# Resolve paths relative to this file so the script runs from any CWD.
HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))

SRC = os.path.join(REPO_ROOT, "practice", "data", "warehouse-a.md")
OUT = os.path.join(HERE, "warehouse-a.result.json")


def main():
    agg = warehouse_lib.save_intermediate(SRC, OUT)
    print("warehouse:", agg["warehouse"])
    print("total:", agg["total"])
    print("items:", agg["items"])
    print("wrote:", OUT)


if __name__ == "__main__":
    main()
