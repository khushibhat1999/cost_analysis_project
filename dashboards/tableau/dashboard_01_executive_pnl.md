# Dashboard 1 — Executive P&L Overview

**Business question:** "How healthy is the business, and where is the money?"

**Audience:** executives, general stakeholders.

**One-sentence insight to prove:** *"We make $1,287 on $2,329 of revenue (55 % margin), but video content is dragging a healthy ~75 % audio margin down — fix that and we unlock ~$500 of latent profit."*

---

## Layout

```
┌───────────────────────────────────────────────────────────────────────┐
│  Title bar — "Chinook Music Store — Executive P&L"       | filters > │
├────────────┬────────────┬────────────┬────────────┬───────────────────┤
│  Revenue   │   Cost     │  Profit    │  Margin %  │  (KPI tiles)      │
├────────────┴────────────┴────────────┴────────────┴───────────────────┤
│  Monthly Revenue, Cost, Profit — multi-line time series               │
├───────────────────────────────────┬───────────────────────────────────┤
│  Top 12 Genres by Profit          │  Revenue by Country (choropleth)  │
│  (color = margin band)            │                                   │
├───────────────────────────────────┴───────────────────────────────────┤
│  Top 10 Countries by Profit — horizontal bar                          │
└───────────────────────────────────────────────────────────────────────┘
Filters (top right): Content Type (Audio/Video), Date Range, Media Type.
```

Target canvas size: **1200 × 1300**.

---

## Sheet-by-sheet build

### Sheet 1 — "KPI – Revenue"
- **Columns**: *(empty)*
- **Rows**: *(empty)*
- **Marks → Text**: `Revenue (sum)`
- **Format**: `$,##0`, large font (36pt), bold.
- Add a title inside the sheet: "Total Revenue" (12pt grey).

Repeat identically for **Sheet 2 – Cost** (`Cost (sum)`), **Sheet 3 – Profit** (`Profit (sum)`), **Sheet 4 – Margin** (`Margin %`, format `0.0%`).

### Sheet 5 — "Monthly P&L"
- **Columns**: `Invoice Month` (continuous)
- **Rows**: `Measure Values`
- **Measure Values filter**: `Revenue (sum)`, `Cost (sum)`, `Profit (sum)`.
- **Marks → Line**. Color = *Measure Names*. Set colors: Revenue #3498DB, Cost #C0392B, Profit #27AE60.
- Dual markers on: *Analytics pane → Reference Band* at y=0 (lightest grey).
- Title: "Monthly revenue, cost & profit".

### Sheet 6 — "Genre Profit (top 12)"
- **Columns**: `Profit (sum)`
- **Rows**: `GenreName`
- **Filter**: `GenreName` → *Top 12 by* `Profit (sum)`.
- Sort rows by Profit descending.
- **Marks → Bar**. Color = `Margin %` with a diverging red-yellow-green palette, center at 0.
- Edit colors → "Advanced" → Start = -1, Center = 0, End = 1.
- Tooltip: `<GenreName> made <Profit (sum)> on <Revenue (sum)> (margin <Margin %>)`.

### Sheet 7 — "World Revenue"
- **Columns / Rows**: double-click `Country` → Tableau converts to Longitude / Latitude.
- **Marks → Filled Map (Map menu → Map Layers → turn on country borders only)**.
- Color = `Revenue (sum)` with Blue sequential palette.
- Tooltip includes `Country Revenue`, `Country Profit`, `Country Customers`, `Country Invoices`.

### Sheet 8 — "Top 10 Countries by Profit"
- **Columns**: `Profit (sum)`
- **Rows**: `Country`
- **Filter**: Country → *Top 10 by* `Profit (sum)`.
- Sort descending.
- **Marks → Bar**, color #27AE60.
- Label: `Profit (sum)` on bar end, format `$,##0`.

---

## Assembling the dashboard

1. New dashboard → Size: *Automatic* with min width 1200.
2. Drop a **Horizontal container** at top: drag Sheets 1–4 in; fit width.
3. **Monthly P&L** (sheet 5): fit width, height ~300 px.
4. **Horizontal container** middle row: Genre Profit (left, 50%) + World Revenue (right, 50%).
5. **Top 10 Countries** (sheet 8): fit width, height ~250 px.
6. **Title text box** at top: "Chinook Music Store — Executive P&L Overview" (18pt bold).
7. **Legend / filter rail** on top right as floating container: Content Type filter + Date Range filter.

### Interactivity (actions)

- **Country drill-down**: Dashboard → Actions → Add Action → *Filter* → source: World Revenue sheet, target: Monthly P&L + Genre Profit + Top 10 Countries. Run on *Select*. Clear selection = "Show all values". Now clicking any country re-scopes the whole dashboard to that country.
- **Genre focus**: another Filter action from Genre Profit → World Revenue + Monthly P&L.
- **Highlight (not filter) the top country bar** when hovering a country on the map: Highlight action instead of Filter.

### Polish

- Hide all axis titles that duplicate the sheet title.
- Set every sheet's background to white, grid to light grey.
- Add a small footer text box: *"Data: Chinook sample DB. Cost model: $0.01/MB + $0.005/min + $5/month overhead allocated by revenue share."*
- Add parameter controls for the three cost parameters along the right rail (shows this is model-driven, not static reporting).

---

## What good looks like

The visual target is the Plotly mock-up at `../html/01_executive_pnl.html`. Open it alongside Tableau while you build so your layout, color palette, and KPI prominence match.

Signal that this dashboard is working:
- The time-series shows 5–6 **sharp cost spikes** — those are the video-sale months. A reviewer should immediately ask "what's with those spikes?", which is the perfect segue to Dashboard 2.
- The Genre bar is overwhelmingly green except for 3–4 red loss-makers (video genres) at the bottom.
- USA / Canada / Brazil dominate country profit; the choropleth shows the tri-regional concentration.
