# Calculated fields — paste into Tableau

Create each of these in Tableau via **Analysis → Create Calculated Field…**. The name on the left becomes the field name in the sheet.

Everything the dashboards need is here. Many fields are tiny but naming them explicitly keeps the view shelves readable.

---

## Core measures

### `Revenue (sum)`
```
SUM([Revenue])
```

### `Cost (sum)`
```
SUM([EstimatedCost])
```

### `Profit (sum)`
```
SUM([Profit])
```

### `Margin %`
```
SUM([Profit]) / SUM([Revenue])
```
Format: Percentage, 1 decimal.

### `Profit per MB`
```
SUM([Profit]) / SUM([Megabytes] * [Quantity])
```
Format: Number (custom), `$0.0000`.

### `Profit per Minute`
```
SUM([Profit]) / SUM([Minutes] * [Quantity])
```
Format: `$0.0000`.

### `Profit per Unit`  *(line-level, for scatter)*
```
[Profit] / [Quantity]
```
Format: `$0.000`.

---

## Date fields

### `Invoice Month`
```
DATETRUNC('month', [InvoiceDate])
```
Set the default date part to **Month** (right-click → Default properties).

### `Invoice Year`
```
YEAR([InvoiceDate])
```

### `Days Since Last Purchase`
```
DATEDIFF('day', { FIXED [CustomerId] : MAX([InvoiceDate]) }, { MAX([InvoiceDate]) })
```
Negative values mean "customer's last purchase is before the dataset max" — exactly what we want.

### `Recency Bucket`
```
IF [Days Since Last Purchase] <= 30 THEN "0–30 d"
ELSEIF [Days Since Last Purchase] <= 90 THEN "31–90 d"
ELSEIF [Days Since Last Purchase] <= 180 THEN "91–180 d"
ELSEIF [Days Since Last Purchase] <= 365 THEN "181–365 d"
ELSE "365+ d"
END
```
After creating, right-click → *Default properties → Sort* → Manual, drag into the order above.

### `Duration Bucket`
```
IF [Minutes] < 2 THEN "<2 min"
ELSEIF [Minutes] < 4 THEN "2–4 min"
ELSEIF [Minutes] < 6 THEN "4–6 min"
ELSEIF [Minutes] < 8 THEN "6–8 min"
ELSEIF [Minutes] < 10 THEN "8–10 min"
ELSE "10+ min"
END
```

---

## Customer-level LOD measures (for ranking / top-N)

### `Customer Lifetime Revenue`
```
{ FIXED [CustomerId] : SUM([Revenue]) }
```

### `Customer Lifetime Profit`
```
{ FIXED [CustomerId] : SUM([Profit]) }
```

### `Customer Rank by Profit`
```
RANK_UNIQUE([Customer Lifetime Profit], 'desc')
```
Used in a Top-10 table; wrap with a filter like `[Customer Rank by Profit] <= 10`.

### `Customer Display Name`
```
"Customer #" + RIGHT("0" + STR([CustomerId]), 2) + "  ·  " + [Country]
```
Produces labels like `Customer #47  ·  Italy` (matches the HTML mock-ups).

---

## Dimension flags

### `Is Video`
```
IF CONTAINS(LOWER([MediaTypeName]), "video") THEN 1 ELSE 0 END
```

### `Content Type`
```
IF [Is Video] = 1 THEN "Video" ELSE "Audio" END
```
Useful for a top-level filter on dashboards 1 and 2.

### `Margin Band`
```
IF [Margin %] >= 0.7 THEN "🟢 Healthy ≥70%"
ELSEIF [Margin %] >= 0 THEN "🟡 Thin 0–70%"
ELSE "🔴 Loss-making"
END
```
Three-color banding you can drop onto any mark.

---

## Country metrics (for the exec dashboard)

### `Country Revenue`
```
{ FIXED [Country] : SUM([Revenue]) }
```

### `Country Profit`
```
{ FIXED [Country] : SUM([Profit]) }
```

### `Country Customers`
```
{ FIXED [Country] : COUNTD([CustomerId]) }
```

### `Country Invoices`
```
{ FIXED [Country] : COUNTD([InvoiceId]) }
```

### `Revenue per Invoice`
```
SUM([Revenue]) / COUNTD([InvoiceId])
```

### `Profit per Invoice`
```
SUM([Profit]) / COUNTD([InvoiceId])
```

---

## Parameters (one-time setup, enable the "what-if" demos)

Create these via **right-click in Data pane → Create Parameter…**.

### Parameter: `p_Cost_Per_MB`
- Data type: Float
- Current value: `0.01`
- Range: 0.001 – 0.1 (step 0.001)
- Display format: `$0.0000`

### Parameter: `p_Cost_Per_Minute`
- Data type: Float
- Current value: `0.005`
- Range: 0.001 – 0.05 (step 0.001)
- Display format: `$0.0000`

### Parameter: `p_Monthly_Overhead`
- Data type: Float
- Current value: `5.00`
- Range: 0 – 500 (step 1)
- Display format: `$0.00`

### Calc: `What-if EstimatedCost`
```
[Megabytes] * [Quantity] * [p_Cost_Per_MB]
+ [Minutes] * [Quantity] * [p_Cost_Per_Minute]
+ { FIXED DATETRUNC('month', [InvoiceDate]) : SUM([Revenue]) } * 0 + [p_Monthly_Overhead]
  * [Revenue] / { FIXED DATETRUNC('month', [InvoiceDate]) : SUM([Revenue]) }
```

### Calc: `What-if Profit`
```
[Revenue] - [What-if EstimatedCost]
```

### Calc: `What-if Margin`
```
SUM([What-if Profit]) / SUM([Revenue])
```

**Add the three parameter controls to the Executive dashboard** → the whole workbook becomes an interactive cost-model sandbox. This is the single highest-impact touch for a resume demo.

---

## Formatting cheat sheet

| Use | Format string |
|---|---|
| Big KPI dollars | `$,##0` |
| Dollar values on bar labels | `$#,##0.00` |
| Per-MB / per-minute rates | `$#,##0.0000` |
| Margin | `0.0%` |
| Row-level dollar amounts | `$#,##0.000;($#,##0.000)` (parentheses for negatives) |
| Dates on axes | `mmm yyyy` |
