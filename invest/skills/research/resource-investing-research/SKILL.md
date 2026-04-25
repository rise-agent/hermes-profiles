---
description: Systematic copper, uranium, solar, and agriculture stock watchlist with Rick Rule-inspired 5P scoring, rate-limit-safe price updates via Polygon.io, Kitco/Alpha Vantage commodity tracking, dynamic periodicity scheduler, target buy logic, and automated daily cron.
tags: [investing, commodities, copper, uranium, solar, agriculture, apis, scoring, cron, scheduler]
name: resource-investing-research
---

# Resource Investing Research Skill

## Objective
Systematically track, score, and time entries for resource equities (copper, uranium, solar, agriculture) using a disciplined, margin-of-safety framework inspired by Rick Rule.

## Architecture
- **Skill location:** `~/.hermes/profiles/invest/skills/research/resource-investing-research/`
- **Data files:** CSVs in skill directory: `copper.csv`, `uranium.csv`, `solar.csv`, `agriculture.csv`, plus `portfolio.json`
- **Update scripts:**
  - `scripts/scheduler.py` — orchestrator; runs only sources whose `next_update <= now`
  - `scripts/watchlist_updater.py` — Polygon.io price fetcher (callable module; reads agriculture.csv too)
  - `scripts/kitco_scraper.py` — Kitco __NEXT_DATA__ JSON + Alpha Vantage commodity prices
- **Scheduler registry:** `data_sources.json` — each source tracks `last_updated`, `next_update`, `periodicity`, `enabled`, `last_status`
- **History CSVs:** `prices_history/equity_prices.csv`, `prices_history/commodity_spot.csv` — append-only time series
- **Cron output:** `~/.hermes/profiles/invest/cron/output/resource_investing_report_YYYYMMDD.md`

## Data Sources & Periodicity

| Source | Method | Periodicity | Purpose | Status |
|---|---|---|---|---|
| **Equity Prices** | Polygon.io `/v2/aggs/{ticker}/prev` | Weekdays 07:00 UTC | Prior-day close for all watchlist tickers | Enabled |
| **Commodity Spot** | Kitco (precious metals) + Alpha Vantage (copper) | Mon/Thu 07:15 UTC | Gold, silver, copper spot prices | Enabled |
| **Composite Scores** | Manual CSV review flag | Monthly 1st 08:00 UTC | Trigger re-rating of 5P scores | Enabled (flags only) |
| **Uranium Spot** | Derived (CCJ premium logic) | Weekly Mon 07:30 UTC | Long-term U assumption divergence | Enabled |
| **News Sentiment** | Alpha Vantage NEWS_SENTIMENT | Weekly Mon 08:30 UTC | Catalyst/headline tracking | **Disabled** (25 calls/day limit) |
| **Macro Indicators** | Manual | Quarterly (toggle around events) | Fed, DXY, 10Y, inventory | Disabled by default |

The scheduler runs **daily at 07:00 UTC** (`0 7 * * *`) and only processes sources whose `next_update` has passed. This is more efficient than a weekly bulk run because each source refreshes on its own natural cadence.

## Data Source Details

### 1. Equity Prices (Polygon.io)
```
GET https://api.polygon.io/v2/aggs/ticker/{SYMBOL}/prev?apikey={POLYGON_API_KEY}
```
**Rate limit:** ~5 req/min on free tier → Sleep 15s between calls.

Watchlist tickers are defined in `data_sources.json` under `equity_prices.tickers`:
- **Copper:** FCX, SCCO, COPX, ERO, HBM, WRN
- **Uranium:** CCJ, UUUU, DNN, NXE, URA, URNM, URNJ
- **Solar:** FSLR, ENPH, SEDG, RUN, SHLS, ICLN, TAN
- **Agriculture:** CF, NTR, AGCO, DE, MOS (Top 5 picks), plus 17 additional candidates for screening

### 2. Commodity Spot Prices
- **Gold/Silver:** Parsed from Kitco's `__NEXT_DATA__` JSON on `/price/precious-metals` (server-hydrated TanStack Query). Bid/ask averaged to mid.
- **Copper:** Alpha Vantage `COPPER` function (monthly, USD/metric ton). Divide by 2204.62 for $/lb conversion if needed.

**Avoid:** direct Kitco `/charts/copper.html` (404s), Mining.com (CDN blocks), MarketWatch (Cloudflare).

### 3. Alpha Vantage (OVERVIEW use only; free tier extremely constrained)
Free tier: 25 calls/day, 1 call/sec. Do not use for bulk price updates.  
Safe uses:
- `OVERVIEW` — company fundamentals (single tickers only, spaced 1.2+s)
- `COPPER` — global copper price (monthly, in USD/mt)

**Pitfall:** Once the quota is burned (~20 tickers), the rest of the session receives `{"Note":"Thank you for using Alpha Vantage..."}` errors.  
**Workaround:** If you need fundamentals for >20 names, split into multiple days or combine with domain-knowledge scoring when data is incomplete.

### 4. FMP (unavailable for new accounts; legacy endpoints disabled post-Apr 2025)  
All new signups are blocked from legacy API endpoints. **Do not plan or rely on FMP.** Fallbacks: Alpha Vantage OVERVIEW (25 calls/day) or Yahoo Finance via `curl` + `q` query parameter.

### 5. Yahoo Finance / yfinance (not pre-installed; often simplest for prices)
Not available in all execution environments (pip may be missing). When available, it is the simplest way to get current prices, forward PE, and balance-sheet hints without rate limits. If it's not installed, an installer attempt will fail; fall back to `curl` against Yahoo chart endpoint.

## Rick Rule "5P" Scoring Framework (1-5 each, equal 20% weight)

| P | Weight | Description |
|---|--------|-------------|
| **People** (Management) | 20% | Track record, insider alignment, capital discipline, skin in game |
| **Property** (Asset Quality) | 20% | Grade, size, mine life, expansion optionality, cost-curve position |
| **Politics** (Jurisdiction) | 20% | Rule of law, tax/regulatory stability, local community relations, permitting risk |
| **Phinance** (Balance Sheet) | 20% | Net debt/EBITDA, FCF yield, liquidity, ability to fund through downturns |
| **Paper** (Valuation/NAV) | 20% | P/NAV, EV/EBITDA, discount to conservative NPV, margin of safety |

Composite Score thresholds:
- **4.0+**: Core position (up to 10% portfolio)
- **3.0–3.9**: Satellite / speculative (up to 4% portfolio)
- **<3.0**: Avoid / monitor only

## Target Buy Logic
- Model long-term commodity prices: **Cu $4.50/lb**, **U $65/lb**, **solar tariff-adjusted LCOE**
- Agriculture: use **normalized mid-cycle earnings** (not peak-cycle) and quality-discounted PE multiples
- Base-case NAV using conservative discount rates (10-12%)
- Buy only when price < **80% of fair value NAV**
- Pre-define target entry, scale-in, and full position prices per name
- No new buys within 48h of earnings for non-core positions

## Agriculture NAV Methodology
When DCF data is unavailable for ag names, derive conservative NAV as follows:

| Approach | When to Use | Example |
|----------|------------|---------|
| **Normalized EPS × modest PE** | Cyclical producers with visible earnings history | CF: ~$10 normalized EPS × 12x = $120 (not peak $15+) |
| **Sum-of-parts + yield support** | Diversified with retail/mining split | NTR: retail $40 + mining $20, haircut for competition = $60 |
| **Mid-cycle PE × normalized EPS** | Equipment OEMs post-supercycle | AGCO: $10 mid-cycle EPS × 11x = $110 |
| **Quality-discounted DCF/PE** | Premium franchise, rich valuation | DE: $25 normalized EPS × 16x = $400 (below historical 18-20x) |
| **Reserve/NAV + yield floor** | Asset-heavy, commodity price-linked | MOS: reserve value + $1.50 norm EPS × 13x = $20 |

Key rule: always use **normalized earnings** (mid-cycle, not peak or trough) and apply a **discount to historical multiples** to build margin of safety. Conservative Entry = 80% of NAV; Scale-In = 90%.

## Running the Scheduler

### Daily Auto-Run (Cron)
Cron job `0 7 * * *` runs `scripts/scheduler.py`, which checks `data_sources.json` and only processes due sources.

### Manual Run (Force a Specific Source)
To force-run a specific source (e.g., refresh commodity spots early):
```bash
# Reset next_update to null for that source
python3 -c "
import json
with open('data_sources.json') as f: d = json.load(f)
d['sources']['commodity_spot']['next_update'] = None
with open('data_sources.json', 'w') as f: json.dump(d, f, indent=2)
"
# Then run scheduler
python3 scripts/scheduler.py
```

### Direct Module Calls (for one-off analysis)
```python
from scripts.watchlist_updater import update_equity_prices
from scripts.kitco_scraper import run_commodity_fetch
from datetime import datetime, timezone

now = datetime.now(timezone.utc)
update_equity_prices(now)
run_commodity_fetch(now)
```

## Research Workflow

1. **Check scheduler report** (delivered daily at 07:00 UTC via cron). Review source statuses and any errors.
2. **Check spot-equity divergence** from latest history CSVs. If equity down but spot flat/up → investigate catalysts.
3. **Review weekly trend plots** (generate from `prices_history/equity_prices.csv` or `commodity_spot.csv`).
4. **Score refresh** triggered monthly by scheduler. Review 5P scores; adjust if new permits, M&A, or guidance changes thesis.
5. **Record**: Date, spot, equity closes, spread commentary, any notable catalyst.

## Common Pitfalls
- Do not hit Polygon rapidly — you will get `max requests per minute` error. Space calls 15s.
- Alpha Vantage COPPER only updates monthly; do not expect daily copper moves.
- Kitco base-metals page TanStack Query hydration may change — the scraper falls back to the precious-metals page JSON.
- Finviz, MarketWatch, Mining.com generally blocked from headless browser — skip them.
- Scripts run from cron must use `Path(__file__)` resolution (not `__file__` relative paths).
- `pip install yfinance` may fail if pip is missing from the active venv. Test import first; if unavailable, use `curl` against Yahoo Finance chart endpoint as fallback.
- `browser_console` cannot execute JavaScript functions — it is only for DOM snapshots / reading values. Must use `curl` to verify HTML content is served correctly.
- `env` for API keys inside execute_code: `os.environ['KEY']` may be empty. Use `subprocess.run(['bash','-c','echo "$KEY"'], capture_output=True)` to read keys from shell env.

## Commodity-Equity Divergence Check
When spot is flat/up but miners are down:
- Profit-taking after parabolic runs (common in copper juniors)
- Insider selling reports
- Pre-earnings jitters
- Cost/revision fears (AISC, Grasberg incidents, permitting delays)

When spot is down but miners flat/up:
- Market pricing in supply cuts or cost-curve support
- ETF/index rebalancing
- M&A speculation
