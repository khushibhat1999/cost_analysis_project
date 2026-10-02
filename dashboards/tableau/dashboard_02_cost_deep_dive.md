# Dashboard 2 — Cost & Content Deep Dive

**Business question:** "Which parts of the catalog destroy margin, and why?"

**Audience:** Finance, content ops, catalog strategy.

**One-sentence insight to prove:** *"Four of our five media types earn 76–83 % margin, but Protected MPEG-4 video files (111 line-items, 445 MB each on average) run at **−144 % margin** — removing or re-pricing them turns a $-318 drag into breakeven."*

---

## Layout

```
┌───────────────────────────────────────────────────────────────────────┐
│  Title — "Cost & Content Deep Dive"                       | filters > │
├────────────┬───────────────┬──────────────────┬───────────────────────┤
│ Profit/MB  │ Unprofitable  │ Worst margin     │ Best-margin genre     │
│  (KPI)     │ media types   │ (media type)     │                       │
├────────────┴───────────────┴──────────────────┴───────────────────────┤
│  Profit per MB by Media Type  │  Margin by Track Duration Bucket     │
├───────────────────────────────┴──────────────────────────────────────┤
│  Line-item scatter — File size (log) vs Profit per unit               │
│  (one point per invoice line, colored by Media Type)                  │
├───────────────────────────────────────────────────────────────────────┤
│  Country × Media Type — total profit heatmap                          │
└───────────────────────────────────────────────────────────────────────┘
Filters (top right): Country, Date Range, Content Type (Audio/Video).
```

Target canvas size: **1200 × 1500**.

---

## Sheet-by-sheet build

### KPI tiles (4 small sheets)

| Sheet | Measure | Format | Subtitle |
|---|---|---|---|
| K1 Profit/MB | `Profit per MB` | `$0.0000` | "Avg profit per MB (all content)" |
| K2 Unprofitable | `COUNTD(IF {FIXED [MediaTypeName]: SUM([Profit])} < 0 THEN [MediaTypeName] END)` — see note | integer | "Unprofitable media types" |
| K3 Worst margin | `MIN({FIXED [MediaTypeName]: SUM([Profit])/SUM([Revenue])})` | `0.0%` | "Worst margin (media type)" |
| K4 Best margin | `MAX({FIXED [GenreName]: SUM([Profit])/SUM([Revenue])})` | `0.0%` | "Best-margin genre" |

> Note for K2 — easiest to build via a second LOD. Create `Media Loss Flag = IF {FIXED [MediaTypeName]: SUM([Profit])} < 0 THEN 1 ELSE 0 END`, then show `COUNTD(IF [Media Loss Flag]=1 THEN [MediaTypeName] END)` on text.

For K3 and K4, add a text annotation below the big number showing *which* media type / genre it is (use `MIN({FIXED [MediaTypeName]: ...})` logic in a second mark, or just drop the dimension on Text with an aggregation of MIN).

### Sheet 5 — "Profit per MB by Media Type"
- **Columns**: `Profit per MB`
- **Rows**: `MediaTypeName`
- Sort rows by Profit per MB descending.
- **Marks → Bar**. Color = *IF profit per MB < 0 THEN red ELSE green* via a calculated `Color: Profit/MB` field, or simply color by the measure with a two-color diverging palette centered on 0.
- Label: `Profit per MB`, format `$0.0000`.
- Tooltip: `<MediaTypeName>: $<Profit per MB>/MB   •   Total profit $<Profit (sum)>`.

### Sheet 6 — "Margin by Duration Bucket"
- **Columns**: `Duration Bucket`
- **Rows**: `Margin %`
- **Marks → Bar**, color via `Margin Band` calc (green/yellow/red).
- Label: `Margin %` on bar end.
- Second row for context: add `AGG(COUNTD([InvoiceLineId]))` to the Rows shelf as *dual axis*, make it a line (grey), synchronize axes OFF (secondary axis = line sales count). Keeps the chart compact and shows the volume behind each bucket.

### Sheet 7 — "File Size vs Profit per Unit"
- **Columns**: `Megabytes` (continuous)
- **Rows**: `Profit per Unit` (continuous)
- **Detail**: `InvoiceLineId` (so each line is its own mark, not aggregated away).
- **Color**: `MediaTypeName` (categorical).
- Set the X axis to **logarithmic**.
- Marks → Circle, size ~6, opacity 60 %.
- Add a horizontal **Reference Line** at y = 0 (lightest grey).
- Tooltip: `<TrackName>  (<MediaTypeName>)  —  <Megabytes> MB  →  $<Profit per Unit> profit per unit`.

### Sheet 8 — "Country × Media Type Heatmap"
- **Columns**: `MediaTypeName`
- **Rows**: `Country`
- Sort rows by `Country Profit` descending (so big markets are on top).
- **Marks → Square (or default heatmap)**. Color = `Profit (sum)` with diverging red-yellow-green centered at 0.
- Add `Profit (sum)` to Label for the top ~5 countries only (filter using a rank calc if needed, or just leave labels off for density).
- Tooltip: `<Country> × <MediaTypeName>: $<Profit (sum)> profit on <COUNTD([InvoiceLineId])> lines`.

---

## Assembling the dashboard

1. Horizontal container top → KPI tiles K1–K4.
2. Horizontal container middle-top → Sheet 5 (left, 50%) + Sheet 6 (right, 50%).
3. Sheet 7 (scatter) → full-width, min 350 px tall.
4. Sheet 8 (heatmap) → full-width, min 400 px tall.
5. Filters floating top-right: Country, Date Range, Content Type.

### Interactivity

- **Media type drill-down**: click a bar in Sheet 5 → Filter action → updates scatter (Sheet 7) + heatmap (Sheet 8) to that media type only.
- **Country drill-down**: click a country row in the heatmap → filter action → updates Sheet 5 + Sheet 7 for that country only. Reviewers can see *"OK, in Czech Republic specifically, what does the media mix look like?"*
- **Highlight on scatter**: hovering a country in Sheet 8 → Highlight action on the scatter → the matching country's lines pop and others fade. Useful for storytelling: pick Ireland or Chile and watch the "big MB, negative profit" cluster light up.

### Polish

- Set the color-coding to be consistent with Dashboard 1: red = loss / cost; green = profit; blue = revenue.
- In the Line-item scatter title, drop a sentence: *"Each dot = one track sold. Dots below the grey zero line are unprofitable units."*
- Add a footnote: *"Note: The 'Protected MPEG-4 video file' type stores music videos at ~445 MB each — ~60× the size of a typical MP3. The cost model's per-MB rate therefore makes them loss leaders."*

---

## What good looks like

Mock-up: `../html/02_cost_deep_dive.html`.

Working signals:
- Sheet 5 has 4 green bars (audio types, $0.08–$0.26 profit/MB) and 1 very noticeable red bar (video, ≈ −$0.06).
- The duration bucket chart cliff-dives from +84 % at <2 min to −123 % at 10+ min.
- The scatter has a clear, dense audio cluster around $0.60–0.90 profit/unit and a thin "loss tail" of large-MB video dots extending to −$8 at ~1000 MB.
- Heatmap has one bright-red column (Protected MPEG-4) that lights up for exactly the countries flagged in Dashboard 3 (Ireland, Chile, Czech Republic).
