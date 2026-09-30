"""Shared parser for warehouse-*.md files.

Each warehouse file is a markdown document with a title heading and a single
markdown table of two columns: 품목 (item name) and 수량 (quantity), e.g.

    # 창고 A 재고

    | 품목 | 수량 |
    |---|---:|
    | mug | 12 |
    | bottle | 3 |

parse_warehouse(path) reads such a file, extracts each item row and returns a
dict with the warehouse id and a normalized list of {"item", "qty"} entries.
Runnable standalone for spot-checking:  python parser.py <path>
"""

import os
import re
import sys


def _warehouse_id_from_path(path):
    """Derive the warehouse id (e.g. 'a') from a warehouse-*.md filename."""
    name = os.path.basename(path)
    m = re.match(r"warehouse-([a-zA-Z0-9]+)\.md$", name)
    if m:
        return m.group(1).lower()
    # Fallback: strip extension and any 'warehouse-' prefix.
    stem = os.path.splitext(name)[0]
    return stem.replace("warehouse-", "").lower()


def _is_separator_row(cells):
    """A markdown separator row is made only of dashes/colons/spaces."""
    return all(re.fullmatch(r"[:\- ]+", c) is not None for c in cells) if cells else False


def parse_warehouse(path):
    """Read a warehouse markdown file and return its normalized contents.

    Returns:
        {
            "warehouse": "<id>",       # e.g. "a"
            "items": [                  # in file order
                {"item": "mug", "qty": 12},
                ...
            ],
        }
    """
    with open(path, "r", encoding="utf-8") as fh:
        lines = fh.readlines()

    wh_id = _warehouse_id_from_path(path)
    items = []
    header_seen = False

    for raw in lines:
        line = raw.strip()
        if not line.startswith("|"):
            continue

        # Split the markdown table row into cell values.
        cells = [c.strip() for c in line.strip("|").split("|")]

        # Skip the header row (품목 | 수량) and the separator row (|---|---:|).
        if _is_separator_row(cells):
            continue
        if not header_seen:
            header_seen = True
            continue

        if len(cells) < 2:
            continue

        item = cells[0]
        qty_text = cells[1]
        if not item:
            continue

        try:
            qty = int(qty_text)
        except ValueError:
            # Tolerate stray formatting; skip non-numeric quantity rows.
            continue

        items.append({"item": item, "qty": qty})

    return {"warehouse": wh_id, "items": items}


if __name__ == "__main__":
    if len(sys.argv) < 2:
        # Default to the sibling data directory for a quick spot-check.
        here = os.path.dirname(os.path.abspath(__file__))
        default = os.path.normpath(
            os.path.join(here, "..", "..", "..", "practice", "data", "warehouse-a.md")
        )
        targets = [default]
    else:
        targets = sys.argv[1:]

    import json

    for target in targets:
        result = parse_warehouse(target)
        print(json.dumps(result, ensure_ascii=False, indent=2))
