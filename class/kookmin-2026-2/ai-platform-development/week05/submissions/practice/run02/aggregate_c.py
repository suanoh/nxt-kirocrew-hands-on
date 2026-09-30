# -*- coding: utf-8 -*-
"""Aggregate warehouse C into its intermediate JSON file.

Independent per-warehouse task (no dependency on A or B). Imports the shared
warehouse_lib module, reads practice/data/warehouse-c.md, computes warehouse
C's total and per-item quantities, and writes the intermediate file
submissions/practice/run02/warehouse-c.result.json (UTF-8).
"""

import os

import warehouse_lib

# Resolve paths relative to this script so it runs from any CWD.
HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))

SRC = os.path.join(REPO_ROOT, "practice", "data", "warehouse-c.md")
OUT = os.path.join(HERE, "warehouse-c.result.json")


def main():
    agg = warehouse_lib.save_intermediate(SRC, OUT)
    print("warehouse:", agg["warehouse"])
    print("total:", agg["total"])
    print("items:", agg["items"])
    print("wrote:", OUT)
    return agg


if __name__ == "__main__":
    main()
