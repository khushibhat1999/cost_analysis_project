# Dashboard 3 — Customer Intelligence

**Business question:** "Who are our best customers and who's about to churn?"

**Audience:** Growth, CRM, lifecycle marketing.

**One-sentence insight to prove:** *"13 of our 59 customers (22 %) haven't bought in over a year — they represent $286 of lifetime profit at risk. A targeted win-back campaign should focus on these dormant customers in high-margin countries first."*

---

## Layout

```
┌───────────────────────────────────────────────────────────────────────┐
│  Title — "Customer Intelligence"                          | filters > │
├───────────────┬──────────────────┬─────────────────┬──────────────────┤
│ Customers (#) │ Avg Lifetime     │ Top Country     │ % Dormant        │
│  (KPI)        │ Profit           │ (profit)        │ (365+ d)         │
├───────────────┴──────────────────┴─────────────────┴──────────────────┤
│  Recency Histogram            │  Recency Cohort — # Customers by     │
│  (days since last purchase)   │  bucket + total profit per bucket    │
├───────────────────────────────┴──────────────────────────────────────┤
│  Top 10 Customers by Lifetime Profit — horizontal bar                 │
├───────────────────────────────────────────────────────────────────────┤
│  Country bubble — Revenue/invoice vs Profit/invoice                   │
│  size = # customers, color = margin                                   │
└───────────────────────────────────────────────────────────────────────┘
Filters (top right): Country, Recency Bucket, Content Type.
```

Target canvas size: **1200 × 1500**.

---

## Sheet-by-sheet build

### KPI tiles (4 sheets)

| Sheet | Measure | Format | Subtitle |
|---|---|---|---|
| K1 Total Customers | `COUNTD([CustomerId])` | integer | "Total Customers" |
| K2 Avg LTV Profit | `SUM([Profit]) / COUNTD([CustomerId])` | `$0.00` | "Avg Lifetime Profit" |
| K3 Top Country Profit | `MAX({FIXED [Country]: SUM([Profit])})` | `$,##0` | "Top country profit" — add a text annotation showing the country name using `MIN(IF {FIXED [Country]: SUM([Profit])} = {MAX({FIXED [Country]: SUM([Profit])})} THEN [Country] END)` |
| K4 Dormant % | `SUM(IF [Days Since Last Purchase] > 365 THEN 1 ELSE 0 END) / COUNTD([CustomerId])` | `0.0%` | "Dormant (365+ days)" |

### Sheet 5 — "Recency Histogram"
- **Columns**: `Days Since Last Purchase` → right-click → *Create → Bins…* → size 30.
- **Rows**: `COUNTD([CustomerId])`.
- **Marks → Bar**, color #3498DB.
- Add a **Reference Line** at x = 365 (dashed red, label "365 d dormancy").
- Tooltip: `<days since last purchase>: <COUNTD> customers`.

### Sheet 6 — "Recency Cohort"
- **Columns**: `Recency Bucket`
- **Rows**: `COUNTD([CustomerId])`
- Sort the bucket dimension manually (already set via default sort in `calculated_fields.md`).
- **Marks → Bar**, color #8E44AD, label = `COUNTD([CustomerId])` on top of bar.
- Second measure on dual axis: `Profit (sum)` as a line, grey. Synchronize OFF. Shows that the big dormant bar is costing you real money.
- Tooltip: `<Recency Bucket>: <COUNTD> customers, $<Profit (sum)> lifetime profit`.

### Sheet 7 — "Top 10 Customers by Profit"
- **Columns**: `Profit (sum)`
- **Rows**: `Customer Display Name`
- **Filter**: `Customer Rank by Profit` <= 10.
- Sort descending.
- **Marks → Bar**, color #27AE60, label on bar end = `Profit (sum)`, format `$0.00`.
- Tooltip: `<Customer Display Name>:  $<Profit (sum)> profit on $<Revenue (sum)> revenue · <COUNTD([InvoiceId])> invoices · last seen <MAX([InvoiceDate])>`.

### Sheet 8 — "Country Bubble"
- **Columns**: `Revenue per Invoice`
- **Rows**: `Profit per Invoice`
- **Detail**: `Country`
- **Size**: `Country Customers` (fixed LOD).
- **Color**: `Margin %`, diverging red-yellow-green centered at 0.
- **Label**: `Country` — but **only** for countries with ≥ 2 customers (use `IF {FIXED [Country]: COUNTD([CustomerId])} >= 2 THEN [Country] ELSE "" END` as the label field to keep the chart from becoming a wall of text).
- Marks → Circle, opacity 70 %, white border 1 px.
- Add a quadrant reference: *Analytics → Reference Line* on each axis at the median value. Call out quadrants with text boxes: top-right = *"profitable & high-ticket"*, top-left = *"profitable but small basket"*, etc.

---

## Assembling the dashboard

1. Horizontal container top: K1 – K4.
2. Horizontal container middle: Sheet 5 (50%) + Sheet 6 (50%).
3. Sheet 7 full-width, height ~280 px.
4. Sheet 8 full-width, min 400 px.
5. Filters top-right.

### Interactivity

- **Click a recency bucket (Sheet 6) → filter action** → updates Top 10 Customers (Sheet 7) + Country Bubble (Sheet 8). Reviewer can slice: "show me the top customers who are dormant" by clicking the 365+ bar.
- **Click a country bubble (Sheet 8) → filter action** → updates Top 10 Customers + Recency histogram for just that country. Instant country-level customer file.
- **Hover a customer bar (Sheet 7) → highlight action** on the Country Bubble → that customer's country bubble pops.

### Polish

- Add a "Win-back candidates" callout somewhere: a small text box or additional sheet listing the 13 customers in the 365+ bucket, sorted by lifetime profit. These are the specific people to re-engage.
- Add a dynamic subtitle below the title that updates with the applied filters: `"Showing " + STR(COUNTD([CustomerId])) + " customers across " + STR(COUNTD([Country])) + " countries"`.
- Match the color palette to Dashboards 1 and 2 (blue = volume, green = profit, red = loss, purple = cohorts).

---

## What good looks like

Mock-up: `../html/03_customer_intelligence.html`.

Working signals:
- The recency histogram has a visible right tail past the 365-day line (the dormant cohort).
- The cohort bar chart shows the dormant bucket is actually substantial (13 of 59 = ~22 %).
- Top 10 customer bars are nearly identical heights ($28.80 – $29.53) — a subtle but interesting insight for a reviewer: **every top customer buys the same volume**, so the margin spread is entirely driven by *what they buy*, not *how much*. Credit Dashboard 2 for the "what".
- Country bubble: Canada, UK, Brazil cluster top-left (small basket, healthy margin); USA sits top-middle (biggest bubble by far); Czech Republic, Ireland, Chile sit bottom-right (bigger baskets but anemic margin — the video effect again).

---

## Portfolio-tier addition (optional, high ROI)

Add a 5th sheet — **"RFM Score Table"**:

- Create three calculated fields:
  - `R Score`: `IIF([Days Since Last Purchase] <= 90, 3, IIF([Days Since Last Purchase] <= 365, 2, 1))`
  - `F Score`: ntile of `COUNTD([InvoiceId])` per customer (use `WINDOW_PERCENTILE_RANK`).
  - `M Score`: ntile of `Customer Lifetime Profit`.
  - `RFM = STR([R Score]) + STR([F Score]) + STR([M Score])`.
- Build a tiny crosstab: rows = Customer Display Name, columns = R / F / M / RFM.
- Show the top 15 highest RFM scores — these are the champions.
- A classic marketing framework, applied with the cost-aware profit score instead of raw revenue — that framing is what makes it resume-worthy.
