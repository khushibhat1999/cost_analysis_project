"""Generate three interactive HTML dashboards from sales_cost_master.csv.

Run:
    python dashboards/build_dashboards.py

Outputs, in dashboards/html/:
    01_executive_pnl.html
    02_cost_deep_dive.html
    03_customer_intelligence.html
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

REPO_ROOT = Path(__file__).resolve().parent.parent
CSV_PATH = REPO_ROOT / "sales_cost_master.csv"
OUT_DIR = REPO_ROOT / "dashboards" / "html"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Palette
BLUE = "#3498DB"
GREEN = "#27AE60"
RED = "#C0392B"
PURPLE = "#8E44AD"
ORANGE = "#E67E22"
GREY = "#7F8C8D"
INDIGO = "#2C3E50"

TEMPLATE = "plotly_white"


def load() -> pd.DataFrame:
    df = pd.read_csv(CSV_PATH, parse_dates=["InvoiceDate"])
    df["Month"] = df["InvoiceDate"].dt.to_period("M").dt.to_timestamp()
    return df


# ---------------------------------------------------------------------------
# Dashboard 1 — Executive P&L Overview
# ---------------------------------------------------------------------------
def build_executive_pnl(df: pd.DataFrame, out: Path) -> None:
    total_rev = df["Revenue"].sum()
    total_cost = df["EstimatedCost"].sum()
    total_profit = df["Profit"].sum()
    margin = total_profit / total_rev

    fig = make_subplots(
        rows=4,
        cols=4,
        specs=[
            [{"type": "indicator"}, {"type": "indicator"}, {"type": "indicator"}, {"type": "indicator"}],
            [{"type": "xy", "colspan": 4}, None, None, None],
            [{"type": "xy", "colspan": 2}, None, {"type": "choropleth", "colspan": 2}, None],
            [{"type": "xy", "colspan": 4}, None, None, None],
        ],
        row_heights=[0.14, 0.28, 0.32, 0.26],
        vertical_spacing=0.09,
        horizontal_spacing=0.08,
        subplot_titles=(
            "", "", "", "",
            "Monthly revenue, cost & profit",
            "Top 12 genres by profit (color = margin %)", "Revenue by country",
            "Top 10 countries by profit",
        ),
    )

    # Row 1 — KPI indicators
    fig.add_trace(go.Indicator(mode="number", value=total_rev, number={"prefix": "$", "valueformat": ",.0f"}, title={"text": "Total Revenue"}), row=1, col=1)
    fig.add_trace(go.Indicator(mode="number", value=total_cost, number={"prefix": "$", "valueformat": ",.0f"}, title={"text": "Estimated Cost"}), row=1, col=2)
    fig.add_trace(go.Indicator(mode="number", value=total_profit, number={"prefix": "$", "valueformat": ",.0f"}, title={"text": "Profit"}), row=1, col=3)
    fig.add_trace(go.Indicator(mode="number", value=margin * 100, number={"suffix": "%", "valueformat": ".1f"}, title={"text": "Overall Margin"}), row=1, col=4)

    # Row 2 — monthly trend
    monthly = df.groupby("Month", as_index=False).agg(
        Revenue=("Revenue", "sum"),
        Cost=("EstimatedCost", "sum"),
        Profit=("Profit", "sum"),
        Invoices=("InvoiceId", "nunique"),
    )
    for name, color, col in [("Revenue", BLUE, "Revenue"), ("Cost", RED, "Cost"), ("Profit", GREEN, "Profit")]:
        fig.add_trace(
            go.Scatter(
                x=monthly["Month"], y=monthly[col], mode="lines+markers", name=name,
                line=dict(color=color, width=2), marker=dict(size=5),
                hovertemplate=f"<b>%{{x|%b %Y}}</b><br>{name}: $%{{y:,.2f}}<extra></extra>",
            ),
            row=2, col=1,
        )

    # Row 3 col 1 — top genres by profit (colored by margin)
    genre = (
        df.groupby("GenreName", as_index=False)
        .agg(Revenue=("Revenue", "sum"), Profit=("Profit", "sum"), Lines=("InvoiceLineId", "count"))
    )
    genre["Margin"] = genre["Profit"] / genre["Revenue"]
    genre = genre.sort_values("Profit", ascending=False).head(12).sort_values("Profit")
    fig.add_trace(
        go.Bar(
            x=genre["Profit"], y=genre["GenreName"], orientation="h",
            marker=dict(
                color=genre["Margin"] * 100, colorscale="RdYlGn", cmin=-100, cmax=100,
                colorbar=dict(title="Margin %", x=0.47, len=0.28, y=0.42, thickness=10),
            ),
            hovertemplate="<b>%{y}</b><br>Profit: $%{x:,.2f}<br>Margin: %{marker.color:.1f}%<extra></extra>",
            name="Genre profit", showlegend=False,
        ),
        row=3, col=1,
    )

    # Row 3 col 3 — choropleth revenue by country
    country = df.groupby("Country", as_index=False).agg(
        Revenue=("Revenue", "sum"), Profit=("Profit", "sum"),
        Invoices=("InvoiceId", "nunique"), Customers=("CustomerId", "nunique"),
    )
    country["Margin"] = country["Profit"] / country["Revenue"]
    fig.add_trace(
        go.Choropleth(
            locations=country["Country"], locationmode="country names",
            z=country["Revenue"], colorscale="Blues",
            colorbar=dict(title="Revenue $", x=1.02, len=0.28, y=0.42, thickness=10),
            hovertemplate="<b>%{location}</b><br>Revenue: $%{z:,.2f}<extra></extra>",
        ),
        row=3, col=3,
    )

    # Row 4 — top 10 countries by profit
    top_country = country.sort_values("Profit", ascending=False).head(10).sort_values("Profit")
    fig.add_trace(
        go.Bar(
            x=top_country["Profit"], y=top_country["Country"], orientation="h",
            marker=dict(color=GREEN),
            text=[f"${v:,.0f}" for v in top_country["Profit"]], textposition="outside",
            hovertemplate="<b>%{y}</b><br>Profit: $%{x:,.2f}<extra></extra>",
            name="Country profit", showlegend=False,
        ),
        row=4, col=1,
    )

    fig.update_geos(row=3, col=3, showcoastlines=True, showland=True, landcolor="#f7f9fb", projection_type="natural earth")
    fig.update_layout(
        template=TEMPLATE,
        height=1300,
        title=dict(
            text="<b>Chinook Music Store — Executive P&L Overview</b><br><span style='font-size:13px;color:#7F8C8D'>Full-history KPIs, monthly trend, catalog and geography breakdowns</span>",
            x=0.02, y=0.985, xanchor="left",
        ),
        showlegend=True,
        legend=dict(orientation="h", y=0.78, x=0.5, xanchor="center", yanchor="bottom"),
        margin=dict(l=60, r=60, t=110, b=40),
        paper_bgcolor="white", plot_bgcolor="white",
    )
    fig.update_xaxes(title="Month", row=2, col=1)
    fig.update_yaxes(title="USD", row=2, col=1)
    fig.update_xaxes(title="Profit ($)", row=3, col=1)
    fig.update_xaxes(title="Profit ($)", row=4, col=1)

    fig.write_html(out, include_plotlyjs="cdn", full_html=True)


# ---------------------------------------------------------------------------
# Dashboard 2 — Cost & Content Deep Dive
# ---------------------------------------------------------------------------
def build_cost_deep_dive(df: pd.DataFrame, out: Path) -> None:
    media = (
        df.assign(
            SoldMB=lambda d: d["Megabytes"] * d["Quantity"],
            SoldMin=lambda d: d["Minutes"] * d["Quantity"],
        )
        .groupby("MediaTypeName", as_index=False)
        .agg(
            Lines=("InvoiceLineId", "count"),
            Revenue=("Revenue", "sum"), Cost=("EstimatedCost", "sum"), Profit=("Profit", "sum"),
            SoldMB=("SoldMB", "sum"), SoldMin=("SoldMin", "sum"),
        )
    )
    media["Margin"] = media["Profit"] / media["Revenue"]
    media["ProfitPerMB"] = media["Profit"] / media["SoldMB"]
    media["ProfitPerMin"] = media["Profit"] / media["SoldMin"]

    best_genre = df.groupby("GenreName").apply(lambda g: g["Profit"].sum() / g["Revenue"].sum()).idxmax()
    worst_media = media.sort_values("Margin").iloc[0]["MediaTypeName"]
    n_unprofitable = int((media["Profit"] < 0).sum())
    avg_ppmb = df["Profit"].sum() / (df["Megabytes"] * df["Quantity"]).sum()

    fig = make_subplots(
        rows=4, cols=4,
        specs=[
            [{"type": "indicator"}, {"type": "indicator"}, {"type": "indicator"}, {"type": "indicator"}],
            [{"type": "xy", "colspan": 2}, None, {"type": "xy", "colspan": 2}, None],
            [{"type": "xy", "colspan": 4}, None, None, None],
            [{"type": "xy", "colspan": 4}, None, None, None],
        ],
        row_heights=[0.14, 0.26, 0.30, 0.30],
        vertical_spacing=0.09, horizontal_spacing=0.10,
        subplot_titles=(
            "", "", "", "",
            "Profit per MB by media type", "Margin by track duration bucket",
            "Line-item scatter — file size vs profit (per unit)",
            "Country × media type — total profit heatmap",
        ),
    )

    fig.add_trace(go.Indicator(mode="number", value=avg_ppmb, number={"prefix": "$", "valueformat": ".4f"}, title={"text": "Avg profit per MB"}), row=1, col=1)
    fig.add_trace(go.Indicator(mode="number", value=n_unprofitable, title={"text": "Unprofitable media types"}), row=1, col=2)
    fig.add_trace(go.Indicator(mode="number", value=media["Margin"].min() * 100, number={"suffix": "%", "valueformat": ".1f"}, title={"text": f"Worst margin<br><span style='font-size:11px'>{worst_media[:32]}</span>"}), row=1, col=3)
    fig.add_trace(go.Indicator(mode="number", value=df[df["GenreName"] == best_genre]["Profit"].sum() / df[df["GenreName"] == best_genre]["Revenue"].sum() * 100, number={"suffix": "%", "valueformat": ".1f"}, title={"text": f"Best-margin genre<br><span style='font-size:11px'>{best_genre}</span>"}), row=1, col=4)

    # Row 2 col 1 — profit per MB by media type
    m_sorted = media.sort_values("ProfitPerMB")
    colors = [RED if v < 0 else GREEN for v in m_sorted["ProfitPerMB"]]
    fig.add_trace(
        go.Bar(
            x=m_sorted["ProfitPerMB"], y=m_sorted["MediaTypeName"], orientation="h",
            marker=dict(color=colors),
            text=[f"${v:.4f}" for v in m_sorted["ProfitPerMB"]], textposition="outside",
            hovertemplate="<b>%{y}</b><br>Profit/MB: $%{x:.4f}<br>Total profit: $%{customdata:,.2f}<extra></extra>",
            customdata=m_sorted["Profit"],
            name="Profit / MB", showlegend=False,
        ),
        row=2, col=1,
    )

    # Row 2 col 3 — margin by duration bucket
    bins = [0, 2, 4, 6, 8, 10, np.inf]
    labels = ["<2 min", "2–4", "4–6", "6–8", "8–10", "10+"]
    df["DurationBucket"] = pd.cut(df["Minutes"], bins=bins, labels=labels, right=False)
    bucket = df.groupby("DurationBucket", observed=True).agg(
        Revenue=("Revenue", "sum"), Profit=("Profit", "sum"), Lines=("InvoiceLineId", "count"),
    )
    bucket["Margin"] = bucket["Profit"] / bucket["Revenue"] * 100
    bcolors = [RED if v < 0 else GREEN for v in bucket["Margin"]]
    fig.add_trace(
        go.Bar(
            x=bucket.index.astype(str), y=bucket["Margin"], marker=dict(color=bcolors),
            text=[f"{v:.1f}%" for v in bucket["Margin"]], textposition="outside",
            hovertemplate="<b>%{x}</b><br>Margin: %{y:.1f}%<br>Lines: %{customdata}<extra></extra>",
            customdata=bucket["Lines"],
            name="Duration margin", showlegend=False,
        ),
        row=2, col=3,
    )

    # Row 3 — scatter MB vs profit (per line)
    sample = df.copy()
    sample["ProfitPerUnit"] = sample["Profit"] / sample["Quantity"]
    for mt, color in zip(
        sample["MediaTypeName"].value_counts().index,
        [BLUE, GREEN, PURPLE, ORANGE, RED],
    ):
        s = sample[sample["MediaTypeName"] == mt]
        fig.add_trace(
            go.Scatter(
                x=s["Megabytes"], y=s["ProfitPerUnit"], mode="markers",
                name=mt, marker=dict(color=color, size=6, opacity=0.6),
                hovertemplate=(
                    "<b>%{customdata[0]}</b><br>Media: " + mt + "<br>"
                    "Size: %{x:.1f} MB<br>Profit / unit: $%{y:.3f}<extra></extra>"
                ),
                customdata=np.stack([s["TrackName"]], axis=-1),
            ),
            row=3, col=1,
        )

    # Row 4 — heatmap country × media type
    pivot = df.pivot_table(index="Country", columns="MediaTypeName", values="Profit", aggfunc="sum", fill_value=0)
    pivot = pivot.loc[pivot.sum(axis=1).sort_values(ascending=False).index]
    fig.add_trace(
        go.Heatmap(
            z=pivot.values, x=pivot.columns, y=pivot.index,
            colorscale="RdYlGn", zmid=0,
            colorbar=dict(title="Profit $", thickness=10, len=0.25, y=0.13, yanchor="bottom", x=1.02),
            hovertemplate="Country: %{y}<br>Media: %{x}<br>Profit: $%{z:,.2f}<extra></extra>",
        ),
        row=4, col=1,
    )

    fig.update_layout(
        template=TEMPLATE, height=1500,
        title=dict(
            text="<b>Cost & Content Deep Dive</b><br><span style='font-size:13px;color:#7F8C8D'>Why file size and media type make or break profitability</span>",
            x=0.02, y=0.985, xanchor="left",
        ),
        showlegend=True, legend=dict(orientation="h", y=0.485, x=0.5, xanchor="center"),
        margin=dict(l=60, r=60, t=110, b=40),
        paper_bgcolor="white", plot_bgcolor="white",
    )
    fig.update_xaxes(title="Profit per MB ($)", row=2, col=1)
    fig.update_xaxes(title="Duration bucket", row=2, col=3)
    fig.update_yaxes(title="Margin (%)", row=2, col=3)
    fig.update_xaxes(title="File size (MB, log scale)", type="log", row=3, col=1)
    fig.update_yaxes(title="Profit per unit ($)", row=3, col=1)
    fig.update_xaxes(title="Media type", row=4, col=1)
    fig.update_yaxes(title="Country", row=4, col=1)

    fig.write_html(out, include_plotlyjs="cdn", full_html=True)


# ---------------------------------------------------------------------------
# Dashboard 3 — Customer Intelligence
# ---------------------------------------------------------------------------
def build_customer_intel(df: pd.DataFrame, out: Path) -> None:
    ref_date = df["InvoiceDate"].max()

    cust = df.groupby(["CustomerId", "Country"], as_index=False).agg(
        Revenue=("Revenue", "sum"), Profit=("Profit", "sum"),
        Invoices=("InvoiceId", "nunique"),
        LastPurchase=("InvoiceDate", "max"), FirstPurchase=("InvoiceDate", "min"),
    )
    cust["DaysSinceLast"] = (ref_date - cust["LastPurchase"]).dt.days
    cust["Margin"] = cust["Profit"] / cust["Revenue"]

    total_customers = len(cust)
    avg_ltv = cust["Profit"].mean()
    top_country = df.groupby("Country")["Profit"].sum().idxmax()
    top_country_profit = df.groupby("Country")["Profit"].sum().max()
    pct_dormant = (cust["DaysSinceLast"] > 365).mean() * 100

    fig = make_subplots(
        rows=4, cols=4,
        specs=[
            [{"type": "indicator"}, {"type": "indicator"}, {"type": "indicator"}, {"type": "indicator"}],
            [{"type": "xy", "colspan": 2}, None, {"type": "xy", "colspan": 2}, None],
            [{"type": "xy", "colspan": 4}, None, None, None],
            [{"type": "xy", "colspan": 4}, None, None, None],
        ],
        row_heights=[0.14, 0.28, 0.30, 0.28],
        vertical_spacing=0.09, horizontal_spacing=0.10,
        subplot_titles=(
            "", "", "", "",
            "Distribution of customer recency",
            "Recency cohort — # customers & total profit",
            "Top 10 customers by lifetime profit",
            "Country bubble — Revenue vs Profit per Invoice (size = customer count)",
        ),
    )

    fig.add_trace(go.Indicator(mode="number", value=total_customers, title={"text": "Total Customers"}), row=1, col=1)
    fig.add_trace(go.Indicator(mode="number", value=avg_ltv, number={"prefix": "$", "valueformat": ".2f"}, title={"text": "Avg Lifetime Profit"}), row=1, col=2)
    fig.add_trace(go.Indicator(mode="number", value=top_country_profit, number={"prefix": "$", "valueformat": ",.0f"}, title={"text": f"Top country profit<br><span style='font-size:11px'>{top_country}</span>"}), row=1, col=3)
    fig.add_trace(go.Indicator(mode="number", value=pct_dormant, number={"suffix": "%", "valueformat": ".1f"}, title={"text": "Dormant (365+ days)"}), row=1, col=4)

    # Row 2 col 1 — recency histogram
    fig.add_trace(
        go.Histogram(
            x=cust["DaysSinceLast"], nbinsx=25, marker=dict(color=BLUE, line=dict(width=1, color="white")),
            hovertemplate="Days: %{x}<br># customers: %{y}<extra></extra>",
        ),
        row=2, col=1,
    )
    # Vertical "365-day dormancy" reference line. Drawn as a Scatter trace instead
    # of add_vline() because add_vline scans all subplots and errors on Indicators.
    y_max = int(cust["DaysSinceLast"].value_counts().max()) + 5
    fig.add_trace(
        go.Scatter(
            x=[365, 365], y=[0, y_max],
            mode="lines", line=dict(color=RED, dash="dash", width=1.5),
            hoverinfo="skip", showlegend=False, name="365 d",
        ),
        row=2, col=1,
    )
    fig.add_annotation(
        x=365, y=y_max, text="365 d", showarrow=False,
        xanchor="left", yanchor="top", xshift=4,
        font=dict(color=RED, size=10),
        row=2, col=1,
    )

    # Row 2 col 3 — recency cohort bar with profit line
    buckets = [-1, 30, 90, 180, 365, np.inf]
    labels = ["0–30", "31–90", "91–180", "181–365", "365+"]
    cust["RecencyBucket"] = pd.cut(cust["DaysSinceLast"], bins=buckets, labels=labels)
    cohort = cust.groupby("RecencyBucket", observed=True).agg(
        Customers=("CustomerId", "count"), Profit=("Profit", "sum"),
    )
    fig.add_trace(
        go.Bar(
            x=cohort.index.astype(str), y=cohort["Customers"],
            marker=dict(color=PURPLE), name="# customers",
            text=cohort["Customers"], textposition="outside",
            hovertemplate="Cohort: %{x} days<br>Customers: %{y}<br>Lifetime profit: $%{customdata:,.2f}<extra></extra>",
            customdata=cohort["Profit"],
        ),
        row=2, col=3,
    )

    # Row 3 — top 10 customers by profit
    cust_name = df.groupby("CustomerId").agg(
        Revenue=("Revenue", "sum"), Profit=("Profit", "sum"),
        Invoices=("InvoiceId", "nunique"), Country=("Country", "first"),
    ).reset_index()
    # attach a display name if available (from Country + short ID since names weren't in csv)
    cust_name["Label"] = cust_name.apply(
        lambda r: f"Customer #{int(r['CustomerId']):02d}  ·  {r['Country']}", axis=1
    )
    top10 = cust_name.sort_values("Profit", ascending=False).head(10).sort_values("Profit")
    fig.add_trace(
        go.Bar(
            x=top10["Profit"], y=top10["Label"], orientation="h",
            marker=dict(color=GREEN),
            text=[f"${v:.2f}" for v in top10["Profit"]], textposition="outside",
            hovertemplate="<b>%{y}</b><br>Profit: $%{x:.2f}<br>Revenue: $%{customdata[0]:.2f}<br>Invoices: %{customdata[1]}<extra></extra>",
            customdata=np.stack([top10["Revenue"], top10["Invoices"]], axis=-1),
        ),
        row=3, col=1,
    )

    # Row 4 — country bubble
    country = df.groupby("Country", as_index=False).agg(
        Revenue=("Revenue", "sum"), Profit=("Profit", "sum"),
        Invoices=("InvoiceId", "nunique"), Customers=("CustomerId", "nunique"),
    )
    country["RevPerInvoice"] = country["Revenue"] / country["Invoices"]
    country["ProfitPerInvoice"] = country["Profit"] / country["Invoices"]
    country["Margin"] = country["Profit"] / country["Revenue"] * 100

    # Only label the larger-customer countries so the chart doesn't become a wall of overlapping text.
    label_threshold = country["Customers"].quantile(0.65)
    display_labels = country["Country"].where(country["Customers"] >= label_threshold, "")

    fig.add_trace(
        go.Scatter(
            x=country["RevPerInvoice"], y=country["ProfitPerInvoice"], mode="markers+text",
            marker=dict(
                size=country["Customers"] * 5 + 8,
                color=country["Margin"], colorscale="RdYlGn", cmin=-100, cmax=100,
                colorbar=dict(title="Margin %", thickness=10, len=0.26, y=0.12, yanchor="bottom", x=1.02),
                line=dict(width=1, color="white"),
            ),
            text=display_labels, textposition="top center", textfont=dict(size=9),
            hovertemplate=(
                "<b>%{customdata[1]}</b><br>Rev/invoice: $%{x:.2f}<br>Profit/invoice: $%{y:.2f}<br>"
                "Customers: %{customdata[0]}<br>Margin: %{marker.color:.1f}%<extra></extra>"
            ),
            customdata=np.stack([country["Customers"], country["Country"]], axis=-1),
            name="Country",
        ),
        row=4, col=1,
    )

    fig.update_layout(
        template=TEMPLATE, height=1500,
        title=dict(
            text="<b>Customer Intelligence</b><br><span style='font-size:13px;color:#7F8C8D'>Lifetime value, recency cohorts, top customers & geography</span>",
            x=0.02, y=0.985, xanchor="left",
        ),
        showlegend=False,
        margin=dict(l=60, r=60, t=110, b=40),
        paper_bgcolor="white", plot_bgcolor="white",
    )
    fig.update_xaxes(title="Days since last purchase", row=2, col=1)
    fig.update_yaxes(title="# customers", row=2, col=1)
    fig.update_xaxes(title="Recency cohort", row=2, col=3)
    fig.update_yaxes(title="# customers", row=2, col=3)
    fig.update_xaxes(title="Lifetime profit ($)", row=3, col=1)
    fig.update_xaxes(title="Revenue per invoice ($)", row=4, col=1)
    fig.update_yaxes(title="Profit per invoice ($)", row=4, col=1)

    fig.write_html(out, include_plotlyjs="cdn", full_html=True)


def main() -> None:
    df = load()
    print(f"Loaded {len(df):,} rows from {CSV_PATH.name}")
    for name, fn in [
        ("01_executive_pnl.html", build_executive_pnl),
        ("02_cost_deep_dive.html", build_cost_deep_dive),
        ("03_customer_intelligence.html", build_customer_intel),
    ]:
        out = OUT_DIR / name
        fn(df, out)
        size_kb = out.stat().st_size / 1024
        print(f"  wrote {out.relative_to(REPO_ROOT)}  ({size_kb:,.0f} KB)")


if __name__ == "__main__":
    main()
