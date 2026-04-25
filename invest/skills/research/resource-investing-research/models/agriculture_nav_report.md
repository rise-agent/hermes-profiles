# Agricultural Equities — NAV-Calibrated Targets & Analysis

**Generated:** 2026-04-24  
**Framework:** Rick Rule 5P scoring | Buy rule: < 80% conservative NAV | Hold: 5-year horizon  
**Commodity deck:** Food inflation thesis; fertilizer prices already elevated

---

## Key Insight: No Name Is Currently at Entry

All five agricultural picks are trading **above** their conservative NAV-based entry zones. This is consistent with a market already pricing in some food-inflation premium and the fertilizer run-up you noted.

**How to read this table:**
- **Conservative Entry** = 80% of NAV; your "all-weather" buy zone
- **Scale-In** = 90% of NAV; start building if you want exposure before full value
- **Target Full** = 100% of NAV; price at which the name is fairly valued on normalized assumptions
- **Status:** `ABOVE` = wait; `NEAR` = within 5% of entry; `AT/BUY` = at or below entry

---

## Agriculture — Top 5

| Ticker | Name | Score | Rating | Close | Conservative NAV | Conservative Entry | Scale-In | Target Full | Status | Notes |
|--------|------|-------|--------|-------|-----------------|--------------------|----------|-------------|--------|-------|
| **CF** | CF Industries | 4.7 | Core | $125.59 | $120.00 | **$96.00** | $108.00 | $120.00 | ABOVE | Best nitrogen cost curve. Fortress BS. Non-substitutable. |
| **NTR** | Nutrien | 4.0 | Core | $72.19 | $60.00 | **$48.00** | $54.00 | $60.00 | ABOVE | Largest potash + retail. 3% div. Defensive holding. |
| **AGCO** | AGCO Corp | 4.0 | Core | $119.54 | $110.00 | **$88.00** | $99.00 | $110.00 | ABOVE | Deep-value alternative to DE. Fendt brand. |
| **DE** | Deere | 3.8 | Satellite | $591.95 | $400.00 | **$320.00** | $360.00 | $400.00 | ABOVE | Unmatched moat but 33x PE. Wait for recession scare entry. |
| **MOS** | Mosaic | 3.7 | Satellite | $24.28 | $20.00 | **$16.00** | $18.00 | $20.00 | ABOVE | Phosphate/potash value. 3.6% yield. Florida env risk. |

---

## How NAV Was Derived

| Ticker | Approach | Key Assumptions |
|--------|----------|----------------|
| **CF** | Normalized EPS × modest multiple | Nitrogen margins normalize to ~$10/share; 12x = $120. Not peak-cycle $15+ EPS. |
| **NTR** | Sum-of-parts + dividend yield | Potash retail $40 + mining $20; haircut for retail competition. |
| **AGCO** | Mid-cycle PE × normalized EPS | Equipment demand soft post-2023 peak; $10 EPS × 11x = $110. |
| **DE** | Quality-discounted DCF | $25 normalized EPS × 16x (below historical 18-20x due to cycle). Premium for moat but not 33x. |
| **MOS** | Asset/NAV + yield support | Potash/phosphate reserve value + cash flow at $1.50 normalized EPS × 13x = $20. |

**Conservative by design.** These are 5-year hold levels, not momentum trades. If fertilizer stays elevated or food inflation accelerates, the "NAV" itself rises, so the entry zones move up with it.

---

## Action Plan

| Priority | Action |
|----------|--------|
| 🟢 1 | **CF** — Closest to fair value ($126 vs $120 NAV). If it dips into the $105-110 range on any sector washout, start scaling. |
| 🟢 2 | **NTR** — At $72 vs $60 NAV. Need a 17% pullback to hit entry. Patient. 3% dividend pays you to wait. |
| 🟢 3 | **AGCO** — At $120 vs $110 NAV. Small margin above value. A 10% market correction could bring it to $108 scale-in. |
| 🔴 4 | **DE** — Far too expensive at $592 vs $400 NAV. Do not chase. Set alerts at $360 and $320. |
| 🔴 5 | **MOS** — At $24 vs $20 NAV. Needs 17% pullback for full entry, 33% for conservative entry. Yield helps, but patience required. |

---

## Integration with Daily Scheduler

The agriculture tickers are now in `data_sources.json` under `equity_prices.tickers`, and `watchlist_updater.py` processes `agriculture.csv` alongside copper, uranium, and solar.

**Daily at 07:00 UTC**, the cron job:
1. Fetches prior-day closes for CF, NTR, AGCO, DE, MOS
2. Updates `last_close` and `change_pct` in `agriculture.csv`
3. Recomputes `vs_target` (AT/BUY / NEAR / ABOVE)
4. Appends to `prices_history/equity_prices.csv`
5. Generates the daily report

---

## Files

| File | Path |
|------|------|
| Agriculture CSV | `~/.hermes/profiles/invest/skills/research/resource-investing-research/agriculture.csv` |
| Agriculture Report | `~/.hermes/profiles/invest/skills/research/resource-investing-research/agriculture_report.md` |
| This NAV Report | `~/.hermes/profiles/invest/skills/research/resource-investing-research/models/agriculture_nav_report.md` |
| Daily Cron Output | `~/.hermes/profiles/invest/cron/output/resource_investing_report_YYYYMMDD.md` |

---

*Disclaimer: Conservative long-term entry planning only. Models use simplifying assumptions. Not investment advice.*
