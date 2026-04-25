#!/usr/bin/env python3
"""
Apply Yuma OpEx-replacement valuation to a live subnet price CSV.

Produces a JSON valuation snapshot with per-subnet:
  - fundamental_low_usd, fundamental_high_usd
  - verdict (Attractive / Fair / Expensive / Bubble / Speculative / Dying)
  - stage, use_case_summary
  - risk_flags

Usage:
    python3 subnet_valuation.py --prices data/subnet_prices_20260115.csv
    python3 subnet_valuation.py                      # auto-finds latest CSV
"""

import argparse
import csv
import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger("subnet_valuation")

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
DATA_DIR = PROJECT_ROOT / "data"
META_PATH = DATA_DIR / "valuation_metadata.json"

# ---------------------------------------------------------------------------
# Emission constants (from Yuma paper / Bittensor whitepaper)
# ---------------------------------------------------------------------------
DAILY_EMISSIONS_PER_SUBNET = 2952.0  # tokens/day at current epoch


def load_metadata(meta_path: Path) -> dict:
    if not meta_path.exists():
        logger.error("Metadata file not found: %s", meta_path)
        sys.exit(1)
    return json.loads(meta_path.read_text(encoding="utf-8"))


def find_latest_prices_csv(data_dir: Path) -> Path | None:
    """Find the most recent subnet_prices_YYYYMMDD.csv."""
    candidates = sorted(data_dir.glob("subnet_prices_*.csv"), reverse=True)
    return candidates[0] if candidates else None


def load_prices(csv_path: Path) -> list[dict]:
    with csv_path.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = [r for r in reader]
    logger.info("Loaded %d rows from %s", len(rows), csv_path)
    return rows


def compute_fundamentals(row: dict, meta: dict) -> dict:
    """
    Apply Yuma formula: Fundamental = Daily OpEx Replacement / Daily Miner Emissions
    Where Daily OpEx = annual_opEx / 365
    """
    netuid = row.get("netuid", "")
    netuid_str = str(int(float(netuid))) if netuid else ""
    price_usd = float(row.get("price_usd", 0) or 0)
    price_tao = float(row.get("price_tao", 0) or 0)
    uid_fill_pct = float(row.get("uid_fill_pct", 0) or 0)
    tao_price = float(row.get("tao_price_usd", 250.0) or 250.0)

    subnet_meta = meta.get("subnets", {}).get(netuid_str, {})
    stage = subnet_meta.get("stage", "Speculative")
    opex_range = subnet_meta.get("comparable_opex_annual_usd")
    notes = subnet_meta.get("fundamental_notes", "")

    # ----------------------------------------
    # Speculative / unknown subnets
    # ----------------------------------------
    if stage in ("Speculative", "Root") or opex_range is None:
        # For speculative subnets, we set a wide band based on
        # heuristic: if price < 0.003 TAO and no fill, probably worthless.
        if price_tao < 0.003 and uid_fill_pct < 50:
            verdict = "Dying"
            risk = ["🔴 Dying subnet — low fill, no visible use case"]
        elif price_tao > 0.05 and stage == "Speculative":
            verdict = "Bubble"
            risk = ["🔴 Bubble risk — speculative with no identifiable OpEx replacement"]
        else:
            verdict = "Speculative"
            risk = ["🟡 Speculative — no OpEx data, purely option value"]

        return {
            "netuid": netuid,
            "name": row.get("name", ""),
            "symbol": row.get("symbol", ""),
            "price_tao": price_tao,
            "price_usd": price_usd,
            "tao_price_usd": tao_price,
            "stage": stage,
            "use_case": subnet_meta.get("use_case", ""),
            "fundamental_low_usd": 0.0,
            "fundamental_high_usd": 0.0,
            "fundamental_mid_usd": 0.0,
            "uid_fill_pct": uid_fill_pct,
            "verdict": verdict,
            "risk_flags": risk,
            "notes": notes,
        }

    # ----------------------------------------
    # Early / Maturing: apply Yuma formula
    # ----------------------------------------
    low_annual, high_annual = opex_range
    daily_low = low_annual / 365.0
    daily_high = high_annual / 365.0

    # Adjust for miner sell pressure assumption
    # If miners sell 80% daily, effective emissions = 20% retained
    # But for valuation we care about the BUY side: what must buyers pay
    # to keep emissions flowing. So we use gross emissions.
    # Optional: adjust for safety margin.
    safety = meta.get("global_assumptions", {}).get("emission_safety_margin", 0.10)
    effective_emissions = DAILY_EMISSIONS_PER_SUBNET * (1 + safety)

    fund_low = daily_low / effective_emissions
    fund_high = daily_high / effective_emissions
    fund_mid = (fund_low + fund_high) / 2.0

    # Verdict logic
    if price_usd <= fund_low * 1.1:
        verdict = "Attractive"
        risk = ["🟢 Price at or below fundamental low"]
    elif price_usd <= fund_high:
        verdict = "Fair"
        risk = ["🟡 Price within fundamental range"]
    elif price_usd <= fund_high * 2:
        verdict = "Expensive"
        risk = ["🟠 Price above fundamental range but <2×"]
    else:
        verdict = "Bubble"
        risk = ["🔴 Price >2× upper fundamental bound"]

    # Additional risk flags
    if uid_fill_pct < 50:
        risk.append("🟡 Low UID fill — declining miner interest")
    if price_tao > 0.5:
        risk.append("🟡 Very high TAO price — assumes massive OpEx replacement")

    return {
        "netuid": netuid,
        "name": row.get("name", ""),
        "symbol": row.get("symbol", ""),
        "price_tao": price_tao,
        "price_usd": price_usd,
        "tao_price_usd": tao_price,
        "stage": stage,
        "use_case": subnet_meta.get("use_case", ""),
        "fundamental_low_usd": round(fund_low, 4),
        "fundamental_high_usd": round(fund_high, 4),
        "fundamental_mid_usd": round(fund_mid, 4),
        "uid_fill_pct": uid_fill_pct,
        "verdict": verdict,
        "risk_flags": risk,
        "notes": notes,
    }


def generate_summary(valuations: list[dict]) -> dict:
    """Produce a basket-level summary."""
    attractive = [v for v in valuations if v["verdict"] == "Attractive"]
    fair = [v for v in valuations if v["verdict"] == "Fair"]
    expensive = [v for v in valuations if v["verdict"] == "Expensive"]
    bubble = [v for v in valuations if v["verdict"] == "Bubble"]
    speculative = [v for v in valuations if v["verdict"] == "Speculative"]
    dying = [v for v in valuations if v["verdict"] == "Dying"]

    # Suggest basket (top 5 by attractiveness within fundamental)
    ranked = sorted(
        [v for v in valuations if v["verdict"] in ("Attractive", "Fair")],
        key=lambda x: x["price_usd"] / max(x["fundamental_mid_usd"], 0.001)
        if x["fundamental_mid_usd"] > 0
        else 999,
    )[:5]

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "subnets_evaluated": len(valuations),
        "verdict_distribution": {
            "Attractive": len(attractive),
            "Fair": len(fair),
            "Expensive": len(expensive),
            "Bubble": len(bubble),
            "Speculative": len(speculative),
            "Dying": len(dying),
        },
        "suggested_basket": [
            {
                "netuid": v["netuid"],
                "name": v["name"],
                "symbol": v["symbol"],
                "price_usd": v["price_usd"],
                "verdict": v["verdict"],
                "fundamental_mid_usd": v["fundamental_mid_usd"],
            }
            for v in ranked
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Yuma valuation engine for Bittensor subnets.")
    parser.add_argument(
        "--prices",
        type=str,
        default=None,
        help="Path to subnet_prices CSV (auto-detected if omitted)",
    )
    args = parser.parse_args()

    prices_path = Path(args.prices) if args.prices else find_latest_prices_csv(DATA_DIR)
    if not prices_path or not prices_path.exists():
        logger.error("No price CSV found. Run live_subnet_fetcher.py first.")
        sys.exit(1)

    meta = load_metadata(META_PATH)
    rows = load_prices(prices_path)
    if not rows:
        logger.error("Empty price CSV.")
        sys.exit(1)

    valuations = [compute_fundamentals(r, meta) for r in rows]
    summary = generate_summary(valuations)

    snapshot = {
        "meta": {
            "tao_price_usd": rows[0].get("tao_price_usd", 250.0),
            "total_subnets_on_chain": rows[0].get("total_subnets", 0),
            "price_csv": str(prices_path),
            "valuation_date": datetime.now(timezone.utc).isoformat(),
        },
        "summary": summary,
        "valuations": valuations,
    }

    today_str = datetime.now(timezone.utc).strftime("%Y%m%d")
    out_path = DATA_DIR / f"valuation_snapshot_{today_str}.json"
    out_path.write_text(json.dumps(snapshot, indent=2), encoding="utf-8")
    logger.info("Wrote valuation snapshot: %s", out_path)

    # Also write a mini CSV for quick inspection
    csv_path = DATA_DIR / f"valuation_summary_{today_str}.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        fieldnames = [
            "netuid",
            "name",
            "symbol",
            "stage",
            "price_tao",
            "price_usd",
            "fundamental_mid_usd",
            "uid_fill_pct",
            "verdict",
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for v in valuations:
            writer.writerow({k: v.get(k, "") for k in fieldnames})
    logger.info("Wrote valuation CSV: %s", csv_path)

    # Print summary
    print("\n" + "=" * 60)
    print("  Bittensor Subnet Valuation Summary")
    print("=" * 60)
    print(f"  Subnets evaluated: {summary['subnets_evaluated']}")
    for k, v in summary["verdict_distribution"].items():
        print(f"    {k}: {v}")
    print(f"\n  Suggested basket ({len(summary['suggested_basket'])} subnets):")
    for b in summary["suggested_basket"]:
        symbol = b.get("symbol") or b.get("name") or f"SN{b['netuid']}"
        print(
            f"    {symbol:12s} @ ${b['price_usd']:.4f}  — {b['verdict']}"
        )
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
