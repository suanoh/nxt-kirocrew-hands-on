#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
신청 현황 점검 — 참가신청 CSV를 행사안내 규칙대로 집계한다.

규칙 (행사안내 기준):
  1. 참가 여부 == "참가"인 사람만 인원/주문에 포함. "불참"은 전부 제외.
  2. 간식(참가자만): 샌드위치/주먹밥 = 1인 1개, "받지 않음" = 0개,
     참가자의 빈칸 = 미응답(확인 필요, 수량 미포함), 불참자의 빈칸 = 무시.
  3. 생수 = 참가 인원수.
  4. 정원(기본 12) 초과 시 표시.

사용법:
  python tally_signups.py <참가신청.csv> [--정원 12]
"""

import argparse
import csv
import json
import sys
from datetime import datetime

# 열 이름 (CSV 헤더와 일치해야 함)
COL_ID = "신청번호"
COL_NAME = "이름"
COL_ATTEND = "참가 여부"
COL_SNACK = "간식 선택"

ATTEND_YES = "참가"
ATTEND_NO = "불참"
SNACK_MENUS = ("샌드위치", "주먹밥")
SNACK_NONE = "받지 않음"


def tally(rows, capacity):
    참가, 불참 = 0, 0
    간식 = {"샌드위치": 0, "주먹밥": 0, "받지_않음": 0}
    미응답 = []

    for row in rows:
        attend = (row.get(COL_ATTEND) or "").strip()
        snack = (row.get(COL_SNACK) or "").strip()

        if attend == ATTEND_NO:
            불참 += 1
            continue          # 불참자는 간식 빈칸도 확인하지 않음
        if attend != ATTEND_YES:
            # 참가/불참 외 값은 자료에 없는 상태 → 집계하지 않고 표시
            미응답.append({
                "신청번호": (row.get(COL_ID) or "").strip(),
                "이름": (row.get(COL_NAME) or "").strip(),
                "사유": f"참가 여부 값이 예상 밖('{attend}')",
            })
            continue

        참가 += 1
        if snack in SNACK_MENUS:
            간식[snack] += 1
        elif snack == SNACK_NONE:
            간식["받지_않음"] += 1
        elif snack == "":
            # 참가자 미응답 — 임의로 메뉴를 정하지 않는다
            미응답.append({
                "신청번호": (row.get(COL_ID) or "").strip(),
                "이름": (row.get(COL_NAME) or "").strip(),
                "사유": "간식 미선택",
            })
        else:
            # 예상 밖 메뉴 값도 임의 판단하지 않고 표시
            미응답.append({
                "신청번호": (row.get(COL_ID) or "").strip(),
                "이름": (row.get(COL_NAME) or "").strip(),
                "사유": f"간식 값이 예상 밖('{snack}')",
            })

    return {
        "집계일시": datetime.now().isoformat(timespec="seconds"),
        "전체_신청수": len(rows),
        "참가_인원": 참가,
        "불참_인원": 불참,
        "정원": capacity,
        "정원초과": 참가 > capacity,
        "간식": 간식,
        "생수": 참가,
        "미응답_확인필요": 미응답,
    }


def load_rows(path):
    # BOM 대응: utf-8-sig 로 열어 헤더 첫 열이 깨지지 않게 한다
    with open(path, encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        expected = {COL_ID, COL_NAME, COL_ATTEND, COL_SNACK}
        missing = expected - set(reader.fieldnames or [])
        if missing:
            sys.exit(f"[오류] CSV에 필요한 열이 없습니다: {', '.join(sorted(missing))}")
        return list(reader)


def main():
    p = argparse.ArgumentParser(description="참가신청 집계")
    p.add_argument("csv_path", help="참가신청.csv 경로")
    p.add_argument("--정원", type=int, default=12, dest="capacity")
    args = p.parse_args()

    rows = load_rows(args.csv_path)
    result = tally(rows, args.capacity)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
