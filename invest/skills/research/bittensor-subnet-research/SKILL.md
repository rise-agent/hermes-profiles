---
skill_id: bittensor-subnet-research
description: >
  Systematic Bittensor subnet token valuation using the Yuma framework.
  Fetches live data for all 129 subnets, applies OpEx-replacement fundamental
  analysis, scores by maturity/stage, and generates markdown reports.
  Designed for value-investors allocating 2-5% to a Bittensor basket.
category: research
tags: [bittensor, crypto, subnets, valuation, yuma-framework, ai-infrastructure]
created: "2026-04-25"
author: "Invest analysis pipeline"
sources:
  - "Yuma Subnet Tokens Report (Jan 2026)"
  - "bittensor Python SDK (subtensor)"
  - "Finney chain live data"
---

# Bittensor Subnet Token Valuation

## Overview

Bittensor subnet tokens are **operational-expense replacements**, not equities.
A company needing $2M/year of model-training dev work can pay miners in subnet
 tokens instead of salaries. The Yuma framework values tokens by:

```
Fundamental Token Value = Daily OpEx Replacement / Daily Miner Emissions
```

Since most subnets lack public OpEx data, we use a **staged approach** based on maturity.

## Staged Valuation Framework

| Stage      | Criteria                              | Method                              |
|----------- | ------------------------------------- | ----------------------------------- |
| Speculative| No product, no buyers, generic desc   | Probability-weighted boundary       |
| Early      | Clear use case, active miners, no rev | Comparable OpEx proxy               |
| Maturing   | Known users, visible demand, buybacks | Direct Yuma OpEx replacement        |
| Root (SN0) | TAO itself                            | Staking yield + network growth      |

## Quick Start

1. **Ensure `bittensor` is installed:**
   ```bash
   pip install bittensor==9.6.0
   ```

2. **Fetch live prices:**
   ```bash
   python3 scripts/live_subnet_fetcher.py
   ```
   Output: `data/subnet_prices_YYYYMMDD.csv`

3. **Run valuation:**
   ```bash
   python3 scripts/subnet_valuation.py
   ```
   Output: `data/valuation_snapshot_YYYYMMDD.json`

4. **Generate report:**
   ```bash
   python3 scripts/generate_report.py
   ```
   Output: `reports/subnet_report_YYYYMMDD.md`

## Observables We Track

| Metric          | What It Tells Us                          |
| --------------- | ----------------------------------------- |
| Token price (TAO)| Market-implied value vs TAO               |
| UID fill rate   | Miner demand / competition                |
| Burn cost       | Barrier to entry                          |
| Emission share  | TAO flowing to subnet (network priority)  |
| Alpha in/out    | Supply dynamics, staking                  |
| Tempo           | Epoch frequency (activity proxy)          |
| Mechanism count | Incentive complexity                      |

## Rick Rule 5P for Subnets

- **People**   → Subnet team track record, GitHub activity, validator concentration
- **Property** → Use case defensibility, technical moat
- **Politics** → Regulatory risk (finance subnets = SEC), Bittensor governance
- **Phinance** → Inflation, burn, miner sell pressure, validator take
- **Paper**    → Price vs Yuma OpEx-replacement fundamental

## Suggested Basket (2-5% of portfolio max)

| Subnet | Ticker | Rationale                       | Stage         |
| ------ | ------ | ------------------------------- | ------------- |
| SN2    | β      | Inference = clearest use case   | Early         |
| SN64   | ش      | Premium inference, near revenue | Maturing      |
| SN4    | δ      | Compute marketplace, large TAM  | Early→Maturing|
| SN1    | α      | Algo optimization, active       | Early         |

Avoid: SN96 (Verathos at ~741 TAO — bubble/unjustified), all $0.003 junk subnets.

## Risk Flags (Auto-flagged in Reports)

- **🔴 Bubble**: Price >2× upper fundamental bound
- **🔴 Dying**: UID fill <50% or price <0.003 TAO with no activity
- **🟡 Expensive**: Price > upper fundamental bound but <2×
- **🟢 Attractive**: Price within or below fundamental range

## Dependencies

```text
bittensor>=9.6.0
pyyaml
requests
pandas  (optional, for history)
```

## Data Flow

```
Finney chain (live) ──► live_subnet_fetcher.py ──► subnet_prices.csv
                                                               │
                                                               ▼
valuation_metadata.json ────────────► subnet_valuation.py ──► valuation_snapshot.json
                                                                     │
                                                                     ▼
                                                        generate_report.py
                                                                     │
                                                                     ▼
                                                              subnet_report.md
```

## Output Files

- `data/subnet_prices_YYYYMMDD.csv` — Raw live prices per subnet
- `data/valuation_snapshot_YYYYMMDD.json` — Fundamental scores + verdicts
- `reports/subnet_report_YYYYMMDD.md` — Human-readable markdown report
- `data/subnet_valuation_history.csv` — Running history (append mode)
