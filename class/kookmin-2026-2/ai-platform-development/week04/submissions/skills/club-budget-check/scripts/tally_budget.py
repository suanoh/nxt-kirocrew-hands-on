# -*- coding: utf-8 -*-
"""club-budget-check: 참가신청·회계·구매계획 CSV를 규정 근거대로 집계한다.

정원은 --capacity로 주입(변경 승인서 반영 시 180). 원본 CSV는 수정하지 않는다.
CSV는 UTF-8로 직접 읽고, JSON도 ensure_ascii=False로 직접 저장한다(한글 모지케 방지).
"""
import argparse
import csv
import json
import os
from collections import Counter

BASE_BAL = {"학교지원금": 0, "동아리회비": 800000}
FUND_APPROVED_UNPAID = 500000  # APPROVAL-FUND-04 잔여(미입금) — 현금 미포함


def read_csv(path):
    with open(path, encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def tally(data_dir, capacity):
    P = read_csv(os.path.join(data_dir, "참가신청.csv"))
    A = read_csv(os.path.join(data_dir, "회계내역.csv"))
    Q = read_csv(os.path.join(data_dir, "구매계획.csv"))

    e04 = [r for r in P if r["행사_ID"] == "E04"]
    st = Counter(r["신청상태"] for r in e04)
    conf = [r for r in e04 if r["신청상태"] == "확정"]
    n_conf, n_wait, n_cancel = len(conf), st.get("대기", 0), st.get("취소", 0)
    hwa = sum(1 for r in conf if r["인화체험"] == "신청")
    food = sum(1 for r in conf if r["식음료"] == "신청")

    funds = sorted(set(r["재원"] for r in A))
    bal = {k: BASE_BAL.get(k, 0) for k in funds}
    for r in A:
        amt = int(r["금액"])
        if r["유형"] in ("수입", "환불입금"):
            bal[r["재원"]] += amt
        elif r["유형"] in ("지출", "환불지급"):
            bal[r["재원"]] -= amt

    e04a = [r for r in A if r["행사_ID"] == "E04"]
    net = {}
    for r in e04a:
        amt = int(r["금액"])
        net.setdefault(r["재원"], 0)
        if r["유형"] == "지출":
            net[r["재원"]] += amt
        elif r["유형"] == "환불지급":
            net[r["재원"]] += amt
        elif r["유형"] == "환불입금":
            net[r["재원"]] -= amt

    def plan_for(n):
        pf = {}
        for r in Q:
            qty = n * int(r["계수"]) if r["수량기준"] == "참가자" else int(r["계수"])
            pf[r["예정재원"]] = pf.get(r["예정재원"], 0) + qty * int(r["단가"])
        return pf

    scenarios = {}
    for label, n in [("확정140", n_conf), ("정원(승인)", capacity)]:
        pf = plan_for(n)
        scenarios[label] = {
            "인원": n,
            "예정": pf,
            "현금대비": {k: bal.get(k, 0) - pf.get(k, 0) for k in ("학교지원금", "동아리회비")},
        }

    return {
        "정원_승인": capacity,
        "참가신청": {"총건": len(e04), "확정": n_conf, "대기": n_wait, "취소": n_cancel,
                     "확정중_인화체험": hwa, "확정중_식음료": food, "확정+대기": n_conf + n_wait},
        "회계": {"현재잔액": bal, "E04_순지출": net, "미입금_승인잔여_현금미포함": FUND_APPROVED_UNPAID},
        "구매계획_시나리오": scenarios,
    }


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True)
    ap.add_argument("--capacity", type=int, default=160)
    ap.add_argument("--json", default="")
    a = ap.parse_args()
    result = tally(a.data, a.capacity)
    text = json.dumps(result, ensure_ascii=False, indent=2)
    print(text)
    if a.json:
        os.makedirs(os.path.dirname(a.json), exist_ok=True)
        with open(a.json, "w", encoding="utf-8") as f:
            f.write(text)
        print("WROTE", a.json)
