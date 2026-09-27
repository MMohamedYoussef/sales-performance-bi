"""Deterministic retail orders and portfolio KPI definitions."""

from datetime import date, timedelta
from random import Random
import argparse
import csv
import json
from pathlib import Path


PRODUCTS = (
    ("Desk Lamp", "Home", 45, 19),
    ("Coffee Grinder", "Home", 89, 42),
    ("Wireless Mouse", "Electronics", 35, 12),
    ("Headphones", "Electronics", 120, 54),
    ("Running Shoes", "Sports", 95, 43),
    ("Yoga Mat", "Sports", 39, 15),
    ("Backpack", "Travel", 75, 31),
    ("Travel Bottle", "Travel", 25, 8),
)


def summarize_orders(rows):
    """Return order-level KPIs, treating a full return as a full refund."""
    rows = list(rows)
    gross = sum(int(r["quantity"]) * int(r["unit_price_usd"]) for r in rows)
    refunds = sum(int(r["quantity"]) * int(r["unit_price_usd"]) for r in rows if int(r["returned"]))
    cogs = sum(int(r["quantity"]) * int(r["unit_cost_usd"]) for r in rows if not int(r["returned"]))
    net = gross - refunds
    return {
        "orders": len(rows),
        "gross_revenue_usd": gross,
        "refunds_usd": refunds,
        "net_revenue_usd": net,
        "cogs_usd": cogs,
        "profit_usd": net - cogs,
        "return_rate": sum(int(r["returned"]) for r in rows) / len(rows) if rows else 0.0,
    }


def generate_orders(count=2000, seed=42):
    """Generate synthetic order lines; one order has exactly one product line."""
    rng = Random(seed)
    start = date(2024, 1, 1)
    rows = []
    for index in range(count):
        product, category, price, cost = rng.choice(PRODUCTS)
        rows.append(
            {
                "order_id": f"ORD-{index + 1:05d}",
                "order_date": (start + timedelta(days=rng.randrange(731))).isoformat(),
                "product": product,
                "category": category,
                "region": rng.choice(("North", "South", "East", "West")),
                "channel": rng.choice(("Online", "Retail", "Partner")),
                "quantity": rng.randint(1, 4),
                "unit_price_usd": price,
                "unit_cost_usd": cost,
                "returned": int(rng.random() < 0.08),
            }
        )
    return rows


def export_dataset(destination, count=2000, seed=42):
    """Write reproducible source data and a JSON KPI benchmark."""
    destination = Path(destination)
    destination.mkdir(parents=True, exist_ok=True)
    rows = generate_orders(count=count, seed=seed)
    fields = (
        "order_id", "order_date", "product", "category", "region", "channel",
        "quantity", "unit_price_usd", "unit_cost_usd", "returned",
    )
    with (destination / "orders.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    (destination / "kpis.json").write_text(
        json.dumps(summarize_orders(rows), indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Build a deterministic sales dashboard dataset")
    parser.add_argument("--output", default="data")
    parser.add_argument("--count", type=int, default=2000)
    parser.add_argument("--seed", type=int, default=42)
    arguments = parser.parse_args()
    export_dataset(arguments.output, count=arguments.count, seed=arguments.seed)
