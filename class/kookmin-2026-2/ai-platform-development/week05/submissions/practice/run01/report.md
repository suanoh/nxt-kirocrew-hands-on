# 창고 A·B·C 재고 집계 리포트

입력 파일: `warehouse-a.md`, `warehouse-b.md`, `warehouse-c.md`

저재고 기준: 원본 창고 행(warehouse row) 수량 < 5 (low_stock_basis = `warehouse_row`)

## 창고별 합계

| 창고 | 합계 |
| --- | ---: |
| A | 22 |
| B | 16 |
| C | 16 |
| **총합계** | **54** |

## 품목별 총수량

| 품목 | 총수량 |
| --- | ---: |
| mug | 17 |
| bottle | 12 |
| sensor | 11 |
| hub | 13 |
| cable | 1 |

## 저재고 목록 (수량 < 5)

| 창고 | 품목 | 수량 |
| --- | --- | ---: |
| A | bottle | 3 |
| B | hub | 2 |
| C | sensor | 4 |
| C | cable | 1 |
