"""DAG orchestrator entrypoint for the warehouse inventory pipeline.

Wiring (a directed acyclic graph):

    aggregate('a') ─┐
    aggregate('b') ─┼──▶ integrate ──▶ result.json ──▶ report.md
    aggregate('c') ─┘

The three aggregate nodes are mutually independent -- they share no state and
read distinct source files -- so they are dispatched concurrently via a thread
pool. The integrate node has an explicit dependency on all three completing;
result.json and report.md are the terminal write nodes fed by the integrated
data.

Run end-to-end (reproduces every intermediate and final artifact):

    python pipeline.py
"""

import json
import os
import sys
from concurrent.futures import ThreadPoolExecutor

import aggregate
import integrate

WAREHOUSES = ["a", "b", "c"]

HERE = os.path.dirname(os.path.abspath(__file__))


def run_aggregations(warehouses=WAREHOUSES, parallel=True):
    """Run the independent per-warehouse aggregate nodes.

    Because the nodes are independent DAG leaves, they run in parallel by
    default. Returns {warehouse_id: aggregation_dict}.
    """
    if parallel:
        with ThreadPoolExecutor(max_workers=len(warehouses)) as pool:
            futures = {
                wid: pool.submit(aggregate.aggregate_warehouse, wid)
                for wid in warehouses
            }
            return {wid: fut.result() for wid, fut in futures.items()}
    return {wid: aggregate.aggregate_warehouse(wid) for wid in warehouses}


def run(parallel=True):
    """Execute the full DAG in dependency order.

    1. aggregate A, B, C   (parallel leaves -> intermediate_<id>.json)
    2. integrate           (join node, depends on all three)
    3. result.json         (terminal write node)
    4. report.md           (terminal write node)

    Returns a summary dict of the produced artifacts and paths.
    """
    # --- Level 0: independent aggregate leaves (parallel) ---
    aggregations = run_aggregations(parallel=parallel)

    # --- Level 1: integrate join (depends on all three aggregates) ---
    merged = integrate.integrate()

    # --- Level 2: terminal artifacts (depend on integrate) ---
    result_path = integrate.write_result()
    report_path = integrate.write_report()

    return {
        "aggregations": aggregations,
        "merged": merged,
        "result_json": result_path,
        "report_md": report_path,
        "intermediates": [
            os.path.join(HERE, "intermediate_{}.json".format(wid))
            for wid in WAREHOUSES
        ],
    }


def main():
    parallel = "--serial" not in sys.argv[1:]
    summary = run(parallel=parallel)

    print("DAG complete ({} aggregation).".format(
        "parallel" if parallel else "serial"
    ))
    for wid in WAREHOUSES:
        print("  aggregate {}: intermediate_{}.json".format(wid.upper(), wid))
    print("  integrate  -> merged {} warehouses".format(
        len(summary["merged"]["per_warehouse"])
    ))
    print("  wrote {}".format(summary["result_json"]))
    print("  wrote {}".format(summary["report_md"]))

    with open(summary["result_json"], "r", encoding="utf-8") as fh:
        print("\nresult.json:")
        print(fh.read())


if __name__ == "__main__":
    main()
