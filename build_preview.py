"""Render a reproducible sales dashboard preview from the checked-in CSV."""

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd


frame = pd.read_csv("data/orders.csv", parse_dates=["order_date"])
kpis = json.loads(Path("data/kpis.json").read_text(encoding="utf-8"))
frame["net_revenue"] = frame["quantity"] * frame["unit_price_usd"] * (1 - frame["returned"])
by_category = frame.groupby("category")["net_revenue"].sum().sort_values()
by_region = frame.groupby("region")["net_revenue"].sum().sort_values()
fig = plt.figure(figsize=(13, 7), facecolor="#101827")
fig.text(.06, .92, "SALES | PERFORMANCE", fontsize=14, weight="bold", color="#67e8f9")
fig.text(.06, .84, "Revenue & margin overview", fontsize=28, weight="bold", color="white")
cards = (
    (.06, f"${kpis['net_revenue_usd']:,.0f}", "Net revenue", "white"),
    (.35, f"${kpis['profit_usd']:,.0f}", "Profit", "#67e8f9"),
    (.59, f"{kpis['orders']:,}", "Orders", "white"),
    (.79, f"{kpis['return_rate']:.1%}", "Return rate", "#fda4af"),
)
for x, value, label, color in cards:
    fig.text(x, .71, value, fontsize=26, weight="bold", color=color)
    fig.text(x, .66, label, fontsize=10, color="#9fb2c8")
for pos, title, values, color in (
    ([.16, .16, .33, .38], "Net revenue by category", by_category, "#67e8f9"),
    ([.61, .16, .33, .38], "Net revenue by region", by_region, "#a78bfa"),
):
    ax = fig.add_axes(pos, facecolor="#1a2940")
    bars = ax.barh(values.index, values.values, color=color, height=.58)
    ax.bar_label(bars, labels=[f"${v:,.0f}" for v in values.values], color="white", padding=5, fontsize=9)
    ax.set_xlim(0, max(values.values) * 1.28)
    ax.set_title(title, loc="left", pad=14, color="white", weight="bold", fontsize=13)
    ax.tick_params(axis="y", colors="#d6e3f0", length=0)
    ax.tick_params(axis="x", bottom=False, labelbottom=False)
    for spine in ax.spines.values():
        spine.set_visible(False)
fig.text(.06, .07, "Synthetic orders • full refunds • fixed seed", fontsize=9, color="#8398ae")
out = Path("assets/sales-preview.png")
out.parent.mkdir(exist_ok=True)
fig.savefig(out, dpi=150, facecolor=fig.get_facecolor())
plt.close(fig)
print(out)
