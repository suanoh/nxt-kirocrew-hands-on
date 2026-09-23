# -*- coding: utf-8 -*-
"""
data-to-html 스킬 규칙에 따라 W04 운영 보고서 HTML 조립.
입력: submissions/W04_집계.json (이미 규칙대로 집계됨)
출력: submissions/운영보고서_초기.html (UTF-8 직접 저장 -- 한글 모지케 방지)
근거: CLUB-01 / ACCOUNT-01 / MEMO-04 (+ data-to-html 스킬: 정원=승인서 기준 160, 미입금 500,000 제외)
원본 CSV/JSON 미수정.
"""
import json
import os

SUB = r"C:\Users\LOTTE\Downloads\nxt-kirocrew-hands-on\class\kookmin-2026-2\ai-platform-development\week04\submissions"
JSON_PATH = os.path.join(SUB, "W04_집계.json")
OUT = os.path.join(SUB, "운영보고서_초기.html")

with open(JSON_PATH, encoding="utf-8") as f:
    d = json.load(f)

part = d["참가"]
acc = d["회계"]
plan = d["구매계획_시나리오"]["시나리오별"]
bal = acc["현재_잔액"]

def won(n):
    return f"{n:,}원"

def signed(n):
    s = f"{n:+,}원"
    return s

# 시나리오 표 행
scen_rows = ""
for cap in ["140", "160", "180"]:
    s = plan[cap]
    sj = s["예정비용"]["학교지원금"]
    hj = s["예정비용"]["동아리회비"]
    scash = s["현금대비(현재잔액-예정비용)"]["학교지원금"]
    hcash = s["현금대비(현재잔액-예정비용)"]["동아리회비"]
    note = ""
    if cap == "160":
        note = "승인 정원(승인서 기준)"
    elif cap == "180":
        note = "변경 미승인 · 별도 시나리오"
    elif cap == "140":
        note = "확정 인원 하한 참고"
    scls = "neg" if scash < 0 else "pos"
    hcls = "neg" if hcash < 0 else "pos"
    scen_rows += f"""      <tr>
        <td><strong>{cap}명</strong><br><span class="tag">{note}</span></td>
        <td>{won(sj)}</td><td class="{scls}">{signed(scash)}</td>
        <td>{won(hj)}</td><td class="{hcls}">{signed(hcash)}</td>
      </tr>
"""

html = f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>빛담 E04 운영 보고서 (초기)</title>
<style>
  * {{ box-sizing: border-box; }}
  body {{ font-family: 'Segoe UI', system-ui, sans-serif; margin: 0; padding: 28px;
         background: #f2f6f7; color: #1a2b32; line-height: 1.55; }}
  .wrap {{ max-width: 900px; margin: 0 auto; }}
  header {{ background: linear-gradient(135deg, #217a70, #2a9d8f); color: #fff;
           padding: 22px 26px; border-radius: 14px; }}
  header h1 {{ margin: 0 0 6px; font-size: 22px; }}
  header p {{ margin: 0; opacity: .92; font-size: 13px; }}
  .concl {{ background: #fff; border: 2px solid #2a9d8f; border-radius: 12px;
           padding: 16px 20px; margin: 18px 0; }}
  .concl h2 {{ margin: 0 0 8px; font-size: 15px; color: #217a70; }}
  .concl ol {{ margin: 0; padding-left: 20px; }}
  .concl li {{ margin: 4px 0; }}
  section {{ background: #fff; border-radius: 12px; padding: 18px 22px; margin: 16px 0;
            box-shadow: 0 1px 4px rgba(0,0,0,.06); }}
  section h2 {{ font-size: 16px; margin: 0 0 12px; border-left: 5px solid #2a9d8f;
               padding-left: 10px; }}
  table {{ border-collapse: collapse; width: 100%; font-size: 13.5px; margin: 6px 0; }}
  th, td {{ border: 1px solid #d5dde0; padding: 7px 10px; text-align: right; }}
  th:first-child, td:first-child {{ text-align: left; }}
  thead th {{ background: #e6f4f1; color: #1a2b32; }}
  .neg {{ color: #d9822b; font-weight: 700; }}
  .pos {{ color: #2a9d8f; font-weight: 700; }}
  .tag {{ font-size: 11px; color: #6b7b82; }}
  .cards {{ display: flex; gap: 12px; flex-wrap: wrap; }}
  .card {{ flex: 1 1 200px; background: #f7fbfa; border: 1px solid #cfe4e0;
          border-radius: 10px; padding: 12px 14px; }}
  .card .k {{ font-size: 12px; color: #6b7b82; }}
  .card .v {{ font-size: 20px; font-weight: 700; color: #217a70; }}
  ul.opt {{ margin: 6px 0; padding-left: 20px; }}
  ul.opt li {{ margin: 6px 0; }}
  .src {{ font-size: 12px; color: #55666d; background: #f0f4f5; border-radius: 8px;
         padding: 8px 12px; margin-top: 8px; }}
  .src code {{ background: #dfeae8; padding: 1px 5px; border-radius: 4px; }}
  footer {{ font-size: 11px; color: #84969c; text-align: center; margin: 20px 0 6px; }}
</style>
</head>
<body>
<div class="wrap">
  <header>
    <h1>빛담 동아리 E04 운영 보고서 <span style="font-size:14px;opacity:.85">(초기안)</span></h1>
    <p>지식 근거(CLUB-01 · ACCOUNT-01 · MEMO-04)와 submissions 집계 JSON 기반 · 기준일 2026-09-22</p>
    <p style="font-size:11px;margin-top:6px;opacity:.8">AI플랫폼개발 수업용 가상 자료. 실제 규정·회계와 무관.</p>
  </header>

  <div class="concl">
    <h2>한눈에 보는 결론 3줄</h2>
    <ol>
      <li>확정 <strong>{part['확정_인원']}명</strong> (대기 {part['상태별_인원']['대기']} · 취소 {part['상태별_인원']['취소']}), 승인 정원은 <strong>160명</strong>(승인서 기준, 홍보 180·회의 요청 무효).</li>
      <li>현재 잔액 학교지원금 <strong>{won(bal['학교지원금'])}</strong> · 동아리회비 <strong>{won(bal['동아리회비'])}</strong>. E04 순지출 학교 {won(acc['E04_순지출']['학교지원금'])} · 회비 {won(acc['E04_순지출']['동아리회비'])}.</li>
      <li>구매계획상 <strong>학교지원금은 140·160·180명 모두 현금 부족</strong>(−6,000/−34,000/−62,000), 동아리회비는 세 경우 모두 충분.</li>
    </ol>
  </div>

  <section>
    <h2>1. 참가 현황</h2>
    <div class="cards">
      <div class="card"><div class="k">확정</div><div class="v">{part['상태별_인원']['확정']}명</div></div>
      <div class="card"><div class="k">대기</div><div class="v">{part['상태별_인원']['대기']}명</div></div>
      <div class="card"><div class="k">취소</div><div class="v">{part['상태별_인원']['취소']}명</div></div>
    </div>
    <table>
      <thead><tr><th>확정자 선택</th><th>신청</th><th>미신청/받지않음</th></tr></thead>
      <tbody>
        <tr><td>인화체험</td><td>{part['확정자_인화체험_선택']['신청']}명</td><td>{part['확정자_인화체험_선택']['미신청']}명</td></tr>
        <tr><td>식음료</td><td>{part['확정자_식음료_선택']['신청']}명</td><td>{part['확정자_식음료_선택']['받지않음']}명</td></tr>
      </tbody>
    </table>
    <div class="src">근거: <code>CLUB-01 제1조</code> 확정=물품 기본 인원 · <code>제3조</code> 대기 40명은 확정에 미리 합산하지 않음(별도 시나리오). 총 신청 200행(확정 140+대기 40+취소 20).</div>
  </section>

  <section>
    <h2>2. 재원별 잔액 · E04 순지출</h2>
    <table>
      <thead><tr><th>재원</th><th>기초잔액</th><th>현재 잔액</th><th>E04 순지출</th></tr></thead>
      <tbody>
        <tr><td>학교지원금</td><td>{won(acc['기초잔액']['학교지원금'])}</td><td>{won(bal['학교지원금'])}</td><td>{won(acc['E04_순지출']['학교지원금'])}</td></tr>
        <tr><td>동아리회비</td><td>{won(acc['기초잔액']['동아리회비'])}</td><td>{won(bal['동아리회비'])}</td><td>{won(acc['E04_순지출']['동아리회비'])}</td></tr>
      </tbody>
    </table>
    <div class="src">근거: <code>ACCOUNT-01 제1조</code> 기초잔액(학교 0/회비 800,000) · <code>제2조</code> 부호(수입·환불입금 +, 지출·환불지급 −) · <code>제3조</code> 현재잔액=기초+수입+환불입금−지출−환불지급, E04 순지출=지출+환불지급−환불입금(수입 제외). 거래 120건(E01~E04), 유형: 수입 5·지출 110·환불입금 5. 미입금 승인분 500,000원은 가용 현금에서 제외.</div>
  </section>

  <section>
    <h2>3. 구매계획 시나리오 비교 (140 · 160 · 180명)</h2>
    <table>
      <thead><tr><th>정원</th><th>학교지원금 예정</th><th>학교 현금대비</th><th>회비 예정</th><th>회비 현금대비</th></tr></thead>
      <tbody>
{scen_rows}      </tbody>
    </table>
    <div class="src">근거: <code>ACCOUNT-01 제5조</code> 참가자=인원×계수, 고정=계수, 예정비용=단가×수량 · <code>제4조</code> 구매계획은 회계에 미합산. 현금대비=현재잔액−예정비용. 정원 기준: <code>MEMO-04</code> 승인 160·180 미승인 / 스킬 규칙 정원=승인서.</div>
  </section>

  <section>
    <h2>4. 가능한 운영안</h2>
    <ul class="opt">
      <li><strong>안 A — 승인 정원 160명 유지, 학교지원금 예정 구매 축소.</strong> 학교지원금은 160명 기준 34,000원 부족 → 인화 체험 소모품(P01~P03) 등 참가자 계수 항목을 확정 인원(140) 기준으로 조정하거나 우선순위 낮은 고정 항목을 회비로 이관.</li>
      <li><strong>안 B — 부족분을 회비로 보전.</strong> 동아리회비 잔액은 세 시나리오 모두 충분(+1.6M대). 단 <code>CLUB-01 제2조</code> 회비 기념품은 1인 3,000원·결재·영수증 요건, <code>제2조</code> 학교지원금의 기념품 제외 규정은 불변 → 재원 목적 대조 후 이관.</li>
      <li><strong>안 C — 140명(확정)으로 우선 확정 후 대기 전환은 별도 계산.</strong> <code>CLUB-01 제3조</code>대로 승인 정원·물품·재원을 함께 확인한 뒤 신청 순서 전환. 180명은 정원 변경 승인 확보 전까지 보류.</li>
    </ul>
  </section>

  <section>
    <h2>5. 추가 확인 사항 (확인 필요)</h2>
    <ul class="opt">
      <li><strong>180명 정원 변경 승인 여부</strong> — <code>MEMO-04</code>: 변경 요청 예정이나 승인 기록 없음. 승인 전 180명 시나리오는 계획용으로만.</li>
      <li><strong>학교지원금 사용 적격</strong> — <code>ACCOUNT-01 제4조</code>: 결제 사실만으로 적격 아님. 인화비 중 용도 미기재 건(<code>MEMO-04</code>)은 영수증·사용 목적 재확인.</li>
      <li><strong>미입금 승인분 500,000원</strong> — 가용 현금에서 제외(스킬 규칙). 실제 입금 시점 확인 필요.</li>
      <li><strong>외부인 참가 조건</strong> — <code>MEMO-04</code>: 이번 회의에서 미결정.</li>
    </ul>
    <p style="font-size:12.5px;color:#55666d;margin:4px 0 0">집계 단계 예상 밖 값·파싱 실패: <strong>없음</strong>(모든 신청상태·회계 유형·수량기준이 근거 문서 정의와 일치).</p>
  </section>

  <section>
    <h2>판단 근거 문서</h2>
    <table>
      <thead><tr><th>문서 ID</th><th>적용 조항</th></tr></thead>
      <tbody>
        <tr><td>CLUB-01 (운영 규칙)</td><td>제1조 확정=구매 기본 인원 · 제2조 회비 기념품 요건 · 제3조 대기 전환 · 제4조 원본 보존</td></tr>
        <tr><td>ACCOUNT-01 (회계 집계 기준)</td><td>제1조 기초잔액 · 제2조 부호 · 제3조 현재잔액·E04 순지출 · 제4조 적격/구매계획 미합산 · 제5조 수량 산식</td></tr>
        <tr><td>MEMO-04 (운영회의 메모)</td><td>승인 정원 160 · 180 변경 미승인 · 인화비 용도 확인 · 외부인 미결정</td></tr>
      </tbody>
    </table>
  </section>

  <footer>빛담 동아리 E04 운영 보고서(초기) · data-to-html 스킬 규칙 적용 · 원본 CSV/JSON 미수정</footer>
</div>
</body>
</html>
"""

with open(OUT, "w", encoding="utf-8") as f:
    f.write(html)
print(f"저장: {OUT} ({len(html)} chars)")
