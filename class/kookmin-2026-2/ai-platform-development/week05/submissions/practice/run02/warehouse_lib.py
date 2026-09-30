# -*- coding: utf-8 -*-
"""Shared parser / aggregation module for the warehouse inventory pipeline.

Reusable by the three parallel per-warehouse aggregation tasks and the
integration task. Reads the markdown source files under practice/data/,
parses the item/quantity table, and writes per-warehouse intermediate JSON.

All JSON is written from Python with explicit UTF-8 + ensure_ascii=False to
avoid Korean mojibake (per user preference).
"""

import json
import os
import re


def warehouse_name(md_path):
    """Derive the canonical warehouse name (e.g. 'warehouse-a') from a path.

    Uses the file's base name without extension, matching the spec keys.
    """
    base = os.path.basename(md_path)
    return os.path.splitext(base)[0]


def parse_warehouse(md_path):
    """Parse a warehouse markdown file into a dict {item: qty}.

    Reads the pipe-delimited markdown table, skipping the header row and the
    `| --- | --- |` separator row. Only rows whose quantity cell is a
    non-negative integer are collected.
    """
    items = {}
    with open(md_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line.startswith("|"):
                continue
            # Split table row into cells, dropping the empty edges.
            cells = [c.strip() for c in line.strip("|").split("|")]
            if len(cells) < 2:
                continue
            item, qty = cells[0], cells[1]
            # Skip header row and separator row.
            if item.lower() == "item":
                continue
            if set(qty) <= set("-: "):
                continue
            if not re.fullmatch(r"\d+", qty):
                continue
            items[item] = items.get(item, 0) + int(qty)
    return items


def aggregate_warehouse(md_path):
    """Aggregate a single warehouse.

    Returns {'warehouse': name, 'total': int, 'items': {item: qty}}.
    'total' is the sum of all item quantities for this warehouse.
    """
    items = parse_warehouse(md_path)
    return {
        "warehouse": warehouse_name(md_path),
        "total": sum(items.values()),
        "items": items,
    }


def write_json(obj, out_path):
    """Write a JSON object to out_path as UTF-8 (no ASCII escaping)."""
    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
        f.write("\n")


def save_intermediate(md_path, out_path):
    """Aggregate one warehouse and save its intermediate JSON file.

    Returns the aggregation dict that was written.
    """
    agg = aggregate_warehouse(md_path)
    write_json(agg, out_path)
    return agg


def load_json(path):
    """Load a JSON file written by this module (UTF-8)."""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)
