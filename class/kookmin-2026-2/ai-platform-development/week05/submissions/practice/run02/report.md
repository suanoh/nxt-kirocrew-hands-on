# 창고 재고 집계 보고서

창고 A·B·C의 재고를 코드로 읽어 집계하고, 품목별 전체 합산 수량과 저재고 품목을 산출한 보고서다.

- **저재고 판정 기준 (low_stock_basis)**: `item_total` (창고 전체 합산 수량 기준)
- **임계값 (threshold)**: `5` (합산 수량이 5 미만이면 저재고)

## 창고별 총계 (Per-warehouse totals)

| 창고 | 총 수량 |
|------|---------|
| warehouse-a | 20 |
| warehouse-b | 16 |
| warehouse-c | 15 |

## 품목별 총계 (Per-item totals)

| 품목 | 총 수량 |
|------|---------|
| bolt | 4 |
| bracket | 13 |
| clip | 2 |
| gasket | 3 |
| nut | 3 |
| screw | 3 |
| washer | 23 |

## 저재고 목록 (Low-stock list)

합산 수량이 5 미만인 품목:

- bolt (4)
- clip (2)
- gasket (3)
- nut (3)
- screw (3)

## 기준 및 임계값 (Basis and threshold)

- `low_stock_basis`: `item_total`
- `threshold`: `5`
