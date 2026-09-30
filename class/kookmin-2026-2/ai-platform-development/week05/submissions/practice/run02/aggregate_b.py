# -*- coding: utf-8 -*-
"""Aggregate warehouse B into an intermediate JSON file.

Independent of warehouses A and C (parallel DAG node). Imports the shared
warehouse_lib module, reads practice/data/warehouse-b.md, computes warehouse
B's total and per-item quantities, and writes the intermediate file
submissions/practice/run02/warehouse-b.result.json (UTF-8, no ASCII escaping).
"""

import os

import warehouse_lib

# Resolve paths relative to the project root, independent of the caller's CWD.
HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))

SRC = os.path.join(PROJECT_ROOT, "practice", "data", "warehouse-b.md")
OUT = os.path.join(HERE, "warehouse-b.result.json")


def main():
    agg = warehouse_lib.save_intermediate(SRC, OUT)
    print("warehouse:", agg["warehouse"])
    print("total:", agg["total"])
    print("items:", agg["items"])
    print("wrote:", OUT)
    return agg


if __name__ == "__main__":
    main()
