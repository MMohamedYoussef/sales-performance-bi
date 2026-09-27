import csv
import json
from pathlib import Path

import duckdb
import pytest

from src.sales import export_dataset, generate_orders, summarize_orders


def test_summary_excludes_refunded_revenue_and_cost():
    # A refunded line must leave both revenue and cost out of profit.
    rows = [
        {"order_id": "A", "quantity": 2, "unit_price_usd": 100, "unit_cost_usd": 60, "returned": 0},
        {"order_id": "B", "quantity": 1, "unit_price_usd": 80, "unit_cost_usd": 50, "returned": 1},
        {"order_id": "C", "quantity": 3, "unit_price_usd": 40, "unit_cost_usd": 20, "returned": 0},
    ]

    assert summarize_orders(rows) == {
        "orders": 3,
        "gross_revenue_usd": 400,
        "refunds_usd": 80,
        "net_revenue_usd": 320,
        "cogs_usd": 180,
        "profit_usd": 140,
        "return_rate": 1 / 3,
    }


def test_generation_is_reproducible_with_unique_order_ids():
    first = generate_orders(count=50, seed=17)
    second = generate_orders(count=50, seed=17)

    assert first == second
    assert len(first) == 50
    assert len({row["order_id"] for row in first}) == 50
    assert all(row["unit_price_usd"] >= row["unit_cost_usd"] for row in first)


def test_export_writes_csv_and_matching_kpis(tmp_path):
    export_dataset(tmp_path, count=12, seed=17)

    with (tmp_path / "orders.csv").open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    metrics = json.loads((tmp_path / "kpis.json").read_text(encoding="utf-8"))

    assert len(rows) == 12
    assert metrics["orders"] == 12
    assert metrics["gross_revenue_usd"] == sum(
        int(row["quantity"]) * int(row["unit_price_usd"]) for row in rows
    )
    assert metrics["net_revenue_usd"] == metrics["gross_revenue_usd"] - metrics["refunds_usd"]


def test_sql_reference_matches_hand_checked_fixture():
    db = duckdb.connect(":memory:")
    db.execute(
        "CREATE TABLE orders(order_id VARCHAR, quantity INTEGER, unit_price_usd INTEGER, "
        "unit_cost_usd INTEGER, returned INTEGER)"
    )
    db.executemany(
        "INSERT INTO orders VALUES (?, ?, ?, ?, ?)",
        [("A", 2, 100, 60, 0), ("B", 1, 80, 50, 1), ("C", 3, 40, 20, 0)],
    )

    sql = (Path(__file__).parents[1] / "sql" / "reference_kpis.sql").read_text(encoding="utf-8")
    row = db.execute(sql).fetchone()

    assert row[:6] == (3, 400, 80, 320, 180, 140)
    assert row[6] == pytest.approx(1 / 3)
