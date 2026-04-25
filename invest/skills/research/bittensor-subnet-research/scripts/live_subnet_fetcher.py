#!/usr/bin/env python3
"""
Fetch live Bittensor subnet data from the Finney chain.

Produces a CSV with one row per subnet, including:
  - netuid, name, symbol, price_tao, price_usd
  - uid_fill_pct, burn_cost_tao, alpha_in, alpha_out
  - emission_tao, tempo, total_subnets, tao_price_usd

Usage:
    python3 live_subnet_fetcher.py
    python3 live_subnet_fetcher.py --output /path/to/custom.csv

Requires: bittensor>=9.6.0 (tested with 10.2.1)
"""

import argparse
import csv
import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path

from bittensor import Subtensor

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger("subnet_fetcher")

# ---------------------------------------------------------------------------
# Configurable paths (relative to this script -> project root)
# ---------------------------------------------------------------------------
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
DATA_DIR = PROJECT_ROOT / "data"
REPORTS_DIR = PROJECT_ROOT / "reports"

# ---------------------------------------------------------------------------
# TAO/USD price helpers
# ---------------------------------------------------------------------------

def _get_tao_price_usd() -> float:
    """
    Fetch TAO->USD from CoinGecko simple API as primary source.
    Falls back to subtensor.get_tao_price() if requests unavailable.
    """
    try:
        import requests  # noqa: F401
        url = (
            "https://api.coingecko.com/api/v3/simple/price"
            "?ids=bittensor&vs_currencies=usd"
        )
        r = requests.get(url, timeout=15)
        r.raise_for_status()
        data = r.json()
        price = data["bittensor"]["usd"]
        logger.info("TAO price from CoinGecko: %.2f USD", price)
        return float(price)
    except Exception as exc:
        logger.warning("CoinGecko failed: %s", exc)

    try:
        subtensor = Subtensor(network="finney")
        if hasattr(subtensor, "get_tao_price"):
            price = subtensor.get_tao_price()
            if price and price > 0:
                logger.info("TAO price from subtensor: %.2f USD", price)
                return float(price)
    except Exception as exc:
        logger.warning("subtensor price failed: %s", exc)

    logger.warning("Falling back to 250.0 USD")
    return 250.0


def fetch_subnet_rows(subtensor: Subtensor, tao_price: float) -> list[dict]:
    """
    Iterates over every netuid on Finney and gathers on-chain fields.
    Returns a list of row dicts.
    """
    total_subnets = subtensor.get_total_subnets()
    logger.info("Total subnets reported: %d", total_subnets)

    rows = []
    valid_subnet_ids = []

    for netuid in range(total_subnets + 5):
        try:
            # DynamicInfo: price, symbol, name, alpha_in, alpha_out
            dynamic = subtensor.subnet(netuid)
            # SubnetInfo: max_n, subnetwork_n, burn, tempo, emission_value
            info = subtensor.get_subnet_info(netuid)
        except Exception:
            # No such subnet on-chain
            continue

        if dynamic is None or info is None:
            continue

        valid_subnet_ids.append(netuid)

        # ----- Extract fields from DynamicInfo -----
        try:
            name = getattr(dynamic, "subnet_name", "") or ""
            symbol = getattr(dynamic, "symbol", "") or ""
            price_tao = float(getattr(dynamic, "price", 0) or 0)
            alpha_in = float(getattr(dynamic, "alpha_in", 0) or 0)
            alpha_out = float(getattr(dynamic, "alpha_out", 0) or 0)
        except Exception as exc:
            logger.debug("DynamicInfo failed for netuid %d: %s", netuid, exc)
            name, symbol, price_tao, alpha_in, alpha_out = "", "", 0.0, 0.0, 0.0

        # ----- Extract fields from SubnetInfo -----
        try:
            max_n = int(getattr(info, "max_n", 256) or 256)
            subnetwork_n = int(getattr(info, "subnetwork_n", 0) or 0)
            burn = float(getattr(info, "burn", 0) or 0)
            tempo = int(getattr(info, "tempo", 0) or 0)
            emission = float(getattr(info, "emission_value", 0) or 0)
        except Exception as exc:
            logger.debug("SubnetInfo failed for netuid %d: %s", netuid, exc)
            max_n, subnetwork_n, burn, tempo, emission = 256, 0, 0.0, 0, 0.0

        uid_fill_pct = round((subnetwork_n / max_n) * 100, 2) if max_n else 0.0

        rows.append(
            {
                "netuid": netuid,
                "name": name,
                "symbol": symbol,
                "price_tao": round(price_tao, 9),
                "price_usd": round(price_tao * tao_price, 4),
                "tao_price_usd": round(tao_price, 2),
                "uid_fill_pct": uid_fill_pct,
                "subnetwork_n": subnetwork_n,
                "max_n": max_n,
                "burn_tao": round(burn, 6),
                "alpha_in": round(alpha_in, 6),
                "alpha_out": round(alpha_out, 6),
                "emission_tao": round(emission, 8),
                "tempo": tempo,
                "total_subnets": int(total_subnets),
                "fetched_at": datetime.now(timezone.utc).isoformat(),
            }
        )

    logger.info(
        "Fetched %d live subnets out of %d scanned",
        len(valid_subnet_ids),
        total_subnets + 5,
    )
    return rows


def save_csv(rows: list[dict], out_path: Path) -> Path:
    """Write rows to CSV; create parent dirs if needed."""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        logger.warning("No rows to write.")
        return out_path

    fieldnames = list(rows[0].keys())
    with out_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    logger.info("Wrote %s", out_path)
    return out_path


def append_history(rows: list[dict], history_path: Path) -> None:
    """Append rows to a running history CSV."""
    history_path.parent.mkdir(parents=True, exist_ok=True)
    file_exists = history_path.exists() and history_path.stat().st_size > 0
    fieldnames = list(rows[0].keys())
    with history_path.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerows(rows)
    logger.info("Appended %d rows to history: %s", len(rows), history_path)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Fetch live Bittensor subnet prices and metadata."
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Override output CSV path",
    )
    parser.add_argument(
        "--tao-price",
        type=float,
        default=None,
        help="Override TAO price (USD)",
    )
    parser.add_argument(
        "--no-history",
        action="store_true",
        help="Skip appending to the running history file",
    )
    args = parser.parse_args()

    # Get TAO/USD price
    tao_price = args.tao_price if args.tao_price else _get_tao_price_usd()

    today_str = datetime.now(timezone.utc).strftime("%Y%m%d")
    out_path = (
        Path(args.output)
        if args.output
        else DATA_DIR / f"subnet_prices_{today_str}.csv"
    )

    logger.info("Connecting to Finney...")
    subtensor = Subtensor(network="finney")

    rows = fetch_subnet_rows(subtensor, tao_price)
    if not rows:
        logger.error("No subnet data retrieved. Exiting.")
        sys.exit(1)

    save_csv(rows, out_path)

    if not args.no_history:
        history_path = DATA_DIR / "subnet_valuation_history.csv"
        append_history(rows, history_path)

    # Dump a tiny summary JSON for downstream scripts
    summary = {
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "total_subnets": rows[0]["total_subnets"],
        "tao_price_usd": rows[0]["tao_price_usd"],
        "subnets_fetched": len(rows),
        "latest_csv": str(out_path),
    }
    summary_path = DATA_DIR / f"fetch_summary_{today_str}.json"
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    logger.info("Summary JSON: %s", summary_path)


if __name__ == "__main__":
    main()
