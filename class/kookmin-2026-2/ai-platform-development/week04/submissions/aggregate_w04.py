# -*- coding: utf-8 -*-
"""
빛담 동아리 W04 데이터 집계
근거 문서:
  - CLUB-01 (운영 규칙): 제1조 확정=구매 기본 인원, 제3조 대기자 미리 합산 금지, 제4조 원본 보존
  - ACCOUNT-01 (회계 집계 기준): 제1조 기초 잔액, 제2조 부호, 제3조 잔액/E04 순지출, 제5조 구매계획 산식
  - MEMO-04 (운영회의 메모): 승인 정원 160, 180 변경 미승인

원본 CSV는 읽기 전용으로만 사용한다(수정하지 않음). CLUB-01 제4조.
"""
import csv
import json
import os
from collections import Counter, defaultdict

DATA_DIR = r"C:\Users\LOTTE\Downloads\nxt-kirocrew-hands-on\class\kookmin-2026-2\ai-platform-development\week04\data"
OUT_DIR  = r"C:\Users\LOTTE\Downloads\nxt-kirocrew-hands-on\class\kookmin-2026-2\ai-platform-development\week04\submissions"

# ACCOUNT-01 제1조: 기초 잔액 (2026-07-01 직전)
OPENING = {"학교지원금": 0, "동아리회비": 800000}
# ACCOUNT-01 제2조: 부호 (수입/환불입금 +, 지출/환불지급 -)
SIGN = {"수입": +1, "환불입금": +1, "지출": -1, "환불지급": -1}

def read_csv(name):
    """utf-8-sig 로 BOM 대응, 전체 행을 dict 리스트로 읽어 반환. 읽기 전용."""
    path = os.path.join(DATA_DIR, name)
    with open(path, encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    return rows, len(rows)

def main():
    result = {"근거문서": {
        "CLUB-01": "빛담 동아리 운영 규칙 (제1조 확정=구매 기본 인원, 제3조 대기자 미리 합산 금지, 제4조 원본 보존)",
        "ACCOUNT-01": "빛담 동아리 회계 집계 기준 (제1조 기초잔액, 제2조 부호, 제3조 잔액·E04 순지출, 제5조 구매계획 산식)",
        "MEMO-04": "빛담 운영회의 메모 (승인 정원 160, 180 변경 미승인)",
    }, "확인_필요": []}

    # ---------- 1) 참가신청 집계 ----------
    signups, n_signup = read_csv("참가신청.csv")
    status_counter = Counter()
    inhwa = Counter()   # 확정자의 인화체험 선택
    food = Counter()    # 확정자의 식음료 선택
    KNOWN_STATUS = {"확정", "대기", "취소"}  # CLUB-01 제1조
    for r in signups:
        st = (r.get("신청상태") or "").strip()
        status_counter[st] += 1
        if st not in KNOWN_STATUS:
            result["확인_필요"].append(f"참가신청 {r.get('신청_ID')}: 예상밖 신청상태 '{st}'")
        if st == "확정":  # CLUB-01 제1조: 구매 기본 인원 = 확정 인원
            inhwa[(r.get("인화체험") or "").strip()] += 1
            food[(r.get("식음료") or "").strip()] += 1

    confirmed = status_counter.get("확정", 0)
    result["참가"] = {
        "총_신청행": n_signup,
        "상태별_인원": dict(status_counter),
        "확정_인원": confirmed,
        "확정자_인화체험_선택": dict(inhwa),
        "확정자_식음료_선택": dict(food),
        "근거": "CLUB-01 제1조 (확정=구매 기본 인원), 제3조 (대기자 미리 합산 안 함)",
    }

    # ---------- 2) 회계 집계 ----------
    ledger, n_ledger = read_csv("회계내역.csv")
    balance = defaultdict(int)   # 재원별 현재 잔액 (전 행사 포함)
    e04_net = defaultdict(int)   # E04 순지출 (지출+환불지급-환불입금, 수입 제외)
    event_ids = set()
    types_seen = Counter()
    for r in ledger:
        fund = (r.get("재원") or "").strip()
        typ = (r.get("유형") or "").strip()
        eid = (r.get("행사_ID") or "").strip()
        event_ids.add(eid)
        types_seen[typ] += 1
        try:
            amt = int((r.get("금액") or "0").strip())
        except ValueError:
            result["확인_필요"].append(f"회계 {r.get('거래_ID')}: 금액 파싱 실패 '{r.get('금액')}'")
            continue
        if typ not in SIGN:
            result["확인_필요"].append(f"회계 {r.get('거래_ID')}: 예상밖 유형 '{typ}'")
            continue
        # ACCOUNT-01 제3조: 잔액 = 기초 + 수입 + 환불입금 - 지출 - 환불지급
        balance[fund] += SIGN[typ] * amt
        # ACCOUNT-01 제3조: E04 순지출 = 지출 + 환불지급 - 환불입금 (수입 제외)
        if eid == "E04":
            if typ == "지출":
                e04_net[fund] += amt
            elif typ == "환불지급":
                e04_net[fund] += amt
            elif typ == "환불입금":
                e04_net[fund] -= amt
            # 수입은 순지출에서 제외

    # 기초 잔액 더하기 (ACCOUNT-01 제1조)
    current_balance = {}
    for fund, opening in OPENING.items():
        current_balance[fund] = opening + balance.get(fund, 0)
    # 기초에 없던 재원이 등장하면 확인
    for fund in balance:
        if fund not in OPENING:
            current_balance[fund] = balance[fund]
            result["확인_필요"].append(f"회계: 기초잔액 기준에 없는 재원 '{fund}' 등장 (기초 0 가정)")

    result["회계"] = {
        "총_거래행": n_ledger,
        "포함_행사_ID": sorted(event_ids),
        "유형별_건수": dict(types_seen),
        "기초잔액": OPENING,
        "현재_잔액": current_balance,
        "E04_순지출": dict(e04_net),
        "근거": "ACCOUNT-01 제1조(기초잔액)·제2조(부호)·제3조(현재잔액=기초+수입+환불입금-지출-환불지급; E04 순지출=지출+환불지급-환불입금, 수입 제외)",
    }

    # ---------- 3) 구매계획 (140/160/180명 시나리오) ----------
    plan, n_plan = read_csv("구매계획.csv")
    scenarios = [140, 160, 180]
    plan_result = {}
    for cap in scenarios:
        per_fund = defaultdict(int)
        for r in plan:
            basis = (r.get("수량기준") or "").strip()
            try:
                coef = int((r.get("계수") or "0").strip())
                unit = int((r.get("단가") or "0").strip())
            except ValueError:
                result["확인_필요"].append(f"구매계획 {r.get('항목_ID')}: 계수/단가 파싱 실패")
                continue
            fund = (r.get("예정재원") or "").strip()
            # ACCOUNT-01 제5조: 참가자 => 인원*계수, 고정 => 계수 자체가 수량
            if basis == "참가자":
                qty = cap * coef
            elif basis == "고정":
                qty = coef
            else:
                result["확인_필요"].append(f"구매계획 {r.get('항목_ID')}: 예상밖 수량기준 '{basis}'")
                continue
            per_fund[fund] += qty * unit  # 예정 비용 = 수량 * 단가
        plan_result[str(cap)] = {
            "예정비용": dict(per_fund),
            "현금대비(현재잔액-예정비용)": {
                f: current_balance.get(f, 0) - per_fund.get(f, 0) for f in per_fund
            },
        }
    result["구매계획_시나리오"] = {
        "총_품목행": n_plan,
        "산식": "ACCOUNT-01 제5조: 참가자=확정/시나리오인원*계수, 고정=계수, 예정비용=수량*단가. 회계 미합산(제4조).",
        "정원_승인_주의": "MEMO-04: 승인 정원 160명. 180명은 변경 미승인이라 별도 시나리오. 140명은 하한 참고.",
        "시나리오별": plan_result,
    }

    if not result["확인_필요"]:
        result["확인_필요"] = ["없음 (모든 값이 알려진 기준에 부합)"]

    out_path = os.path.join(OUT_DIR, "W04_집계.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"참가신청 읽은 행: {n_signup}")
    print(f"회계내역 읽은 행: {n_ledger}")
    print(f"구매계획 읽은 행: {n_plan}")
    print(f"상태별 인원: {dict(status_counter)}")
    print(f"확정 인원: {confirmed}")
    print(f"확정자 인화체험 선택: {dict(inhwa)}")
    print(f"확정자 식음료 선택: {dict(food)}")
    print(f"현재 잔액: {current_balance}")
    print(f"E04 순지출: {dict(e04_net)}")
    print(f"포함 행사: {sorted(event_ids)} / 유형별: {dict(types_seen)}")
    for cap in scenarios:
        print(f"[{cap}명] {plan_result[str(cap)]}")
    print(f"확인 필요: {result['확인_필요']}")
    print(f"JSON 저장: {out_path}")

if __name__ == "__main__":
    main()
