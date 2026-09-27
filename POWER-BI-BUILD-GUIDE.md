# Power BI report design

Import `data/orders.csv` as table **Orders**. Set `order_date` to Date, quantity/price/cost/returned to Whole Number, and text fields to Text. `returned` is 0 or 1, where 1 means a full refund. Keep `order_id` as text and do not summarize it.

Create these measures:

```DAX
Orders = COUNTROWS(Orders)
Gross Revenue = SUMX(Orders, Orders[quantity] * Orders[unit_price_usd])
Refunds = SUMX(FILTER(Orders, Orders[returned] = 1), Orders[quantity] * Orders[unit_price_usd])
Net Revenue = [Gross Revenue] - [Refunds]
COGS = SUMX(FILTER(Orders, Orders[returned] = 0), Orders[quantity] * Orders[unit_cost_usd])
Profit = [Net Revenue] - [COGS]
Return Rate = DIVIDE(CALCULATE([Orders], Orders[returned] = 1), [Orders])
```

Format revenue, refunds, COGS and profit as USD currency; Return Rate as percentage. Build an **Executive** page with cards for Net Revenue, Profit, Orders and Return Rate; a trend of Net Revenue by order month; and bars of Net Revenue by category and region. Add date, region and channel slicers. Build a **Product** page with a table of product, category, Orders, Net Revenue, Profit and Return Rate, sorted by Profit. The preview PNG in `assets/` is generated from CSV and shows the recommended color/layout direction; it is not a Power BI report.

Before saving a `.pbix` or `.pbip`, compare unfiltered cards with `data/kpis.json` and `sql/reference_kpis.sql`. Measures should divide totals after filters; do not average row-level return percentages.
