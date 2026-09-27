WITH line_values AS (
    SELECT
        quantity * unit_price_usd AS gross,
        CASE WHEN returned = 1 THEN quantity * unit_price_usd ELSE 0 END AS refund,
        CASE WHEN returned = 0 THEN quantity * unit_cost_usd ELSE 0 END AS cogs,
        returned
    FROM orders
)
SELECT
    COUNT(*) AS orders,
    COALESCE(SUM(gross), 0) AS gross_revenue_usd,
    COALESCE(SUM(refund), 0) AS refunds_usd,
    COALESCE(SUM(gross - refund), 0) AS net_revenue_usd,
    COALESCE(SUM(cogs), 0) AS cogs_usd,
    COALESCE(SUM(gross - refund - cogs), 0) AS profit_usd,
    COALESCE(AVG(CAST(returned AS DOUBLE)), 0) AS return_rate
FROM line_values;
