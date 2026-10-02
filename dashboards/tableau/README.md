# Chinook Cost Analysis — Tableau Dashboard Pack

Three resume-ready Tableau dashboards built on `sales_cost_master.csv`.

## Contents

```
tableau/
├── README.md                              ← this file
├── calculated_fields.md                   ← paste-ready Tableau formulas
├── dashboard_01_executive_pnl.md          ← full build spec, dashboard 1
├── dashboard_02_cost_deep_dive.md         ← full build spec, dashboard 2
├── dashboard_03_customer_intelligence.md  ← full build spec, dashboard 3
└── data/
    └── sales_cost_master.csv              ← the single data source
```

For a preview of what the finished dashboards look like, open the three HTML mock-ups in `../html/` in any browser.

## Setup (one time, ~5 min)

1. **Download Tableau Public** (free): https://public.tableau.com/en-us/s/download
2. **Open Tableau Public** → *Connect → Text File* → point at `tableau/data/sales_cost_master.csv`.
3. In the **Data Source** tab, Tableau auto-detects types. Verify the following columns:
   - `InvoiceDate` → Date (not String)
   - `Revenue`, `EstimatedCost`, `Profit`, `Margin`, `UnitPrice`, `Megabytes`, `Minutes`, `Milliseconds`, `Bytes` → Numeric (Measure)
   - `GenreName`, `ArtistName`, `AlbumTitle`, `MediaTypeName`, `Country`, `City` → String (Dimension)
   - `CustomerId`, `InvoiceId`, `InvoiceLineId`, `TrackId` → leave as Dimension (not auto-converted to Measure)
4. Create the calculated fields in [`calculated_fields.md`](./calculated_fields.md) (copy / paste; takes ~10 min).
5. Build the three dashboards by following each spec file (each ~30–60 min).
6. **Save as `.twbx`** so the data is embedded, then publish to Tableau Public for a shareable link to put on your resume.

## The three dashboards

| # | Name | Audience | Business question |
|---|---|---|---|
| 1 | **Executive P&L Overview** | Exec / general audience | "How healthy is the business and where is the money?" |
| 2 | **Cost & Content Deep Dive** | Finance / content ops | "Which parts of the catalog destroy margin and why?" |
| 3 | **Customer Intelligence** | Growth / CRM | "Who are our best customers and who's about to churn?" |

The three are designed to tell a connected story: dashboard 1 raises the question "why is overall margin only 55%?", dashboard 2 answers it (video files), and dashboard 3 operationalizes it (which customers / countries are affected, who to win back).

## Portfolio tips

- Publish all three workbooks to **Tableau Public** under one profile. Link that profile from your resume.
- In each dashboard, add a text box at the bottom crediting the data source: *"Data: Chinook sample DB (Lerocha, GitHub). Cost model: author's own assumptions."*
- Add a cover worksheet to each workbook with the business question, the key insight (one sentence), and a thumbnail of the dashboard.
- Record a 60-second Loom walkthrough per dashboard — explain the business question, the finding, and one specific action a stakeholder would take. This is what separates a portfolio from a gallery.

## Cost model assumptions (bake into dashboard footers)

The CSV was generated with these parameters — repeat them on the dashboards so reviewers understand the model:

| Parameter | Value | Meaning |
|---|---|---|
| `COST_PER_MB` | $0.01 / MB | CDN / egress / storage |
| `COST_PER_MINUTE` | $0.005 / min | Licensing / royalty |
| `MONTHLY_OVERHEAD` | $5 / month | Fixed platform cost, allocated to each line in proportion to that line's share of its month's revenue |
