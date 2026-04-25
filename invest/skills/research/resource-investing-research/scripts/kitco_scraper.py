#!/usr/bin/env python3
"""
Kitco / Alpha Vantage commodity price fetcher.
Uses Kitco __NEXT_DATA__ JSON for gold/silver.
Uses Alpha Vantage COPPER function for copper.
Appends to prices_history/commodity_spot.csv
"""
import csv
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path

import requests

HISTORY_DIR = Path(__file__).resolve().parent.parent / "prices_history"
ALPHA_KEY = os.environ.get("ALPHA_VANTAGE_API_KEY", "")


def fetch_kitco_json() -> dict:
    """Fetch Kitco HTML and parse __NEXT_DATA__ for metal prices."""
    url = "https://www.kitco.com/price/precious-metals"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "text/html",
    }
    r = requests.get(url, headers=headers, timeout=30)
    r.raise_for_status()

    m = re.search(r'id="__NEXT_DATA__"\s*type="application/json"[^>]*>({.*?})</script>', r.text, re.DOTALL)
    if not m:
        raise RuntimeError("Kitco __NEXT_DATA__ not found")

    data = json.loads(m.group(1))
    queries = data["props"]["pageProps"]["dehydratedState"]["queries"]
    for q in queries:
        key = q.get("queryKey", [])
        if isinstance(key, list) and len(key) >= 2 and key[1] == "allMetalsQuote":
            return q["state"]["data"]
    raise RuntimeError("allMetalsQuote not found in Kitco data")


def extract_kitco_prices(data: dict) -> dict:
    """Extract gold/silver from Kitco allMetalsQuote dict."""
    prices = {}
    metal_mapping = {
        "gold": ("XAU", "Gold", "USD/oz"),
        "silver": ("XAG", "Silver", "USD/oz"),
    }
    for metal_key, (sym, name, unit) in metal_mapping.items():
        if metal_key not in data:
            continue
        info = data[metal_key]
        results = info.get("results", [])
        if not results:
            continue
        latest = results[0]
        bid = latest.get("bid")
        ask = latest.get("ask")
        mid = latest.get("mid")
        if mid:
            prices[sym] = {"price": float(mid), "name": name, "unit": unit, "source": "kitco"}
        elif bid and ask:
            prices[sym] = {"price": (float(bid) + float(ask)) / 2, "name": name, "unit": unit, "source": "kitco"}
    return prices


def fetch_alpha_vantage_copper() -> dict:
    """Fetch latest copper from Alpha Vantage."""
    if not ALPHA_KEY:
        return {}
    url = "https://www.alphavantage.co/query?function=COPPER&interval=monthly&apikey=" + ALPHA_KEY
    try:
        r = requests.get(url, timeout=30)
        data = r.json()
        name = data.get("name", "")
        unit = data.get("unit", "")
        latest = data.get("data", [{}])[0]
        value = float(latest.get("value", 0))
        return {
            "XCU": {
                "price": value,
                "name": "Copper",
                "unit": "USD/mt",
                "source": "alphavantage",
                "note": "monthly",
            }
        }
    except Exception as e:
        print(f"  Alpha Vantage copper error: {e}")
        return {}


def record_spot_history(date_iso: str, symbol: str, name: str, unit: str, price: float, source: str):
    hist = HISTORY_DIR / "commodity_spot.csv"
    if not hist.exists():
        with open(hist, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["date", "symbol", "name", "unit", "price", "source"])
    with open(hist, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([date_iso, symbol, name, unit, round(price, 4), source])


def run_commodity_fetch(now: datetime) -> dict:
    """Returns {status, prices, errors}."""
    HISTORY_DIR.mkdir(parents=True, exist_ok=True)
    date_iso = now.strftime("%Y-%m-%d")
    results = {"status": "ok", "prices": {}, "errors": []}

    # Kitco for gold/silver
    try:
        kitco_data = fetch_kitco_json()
        kitco_prices = extract_kitco_prices(kitco_data)
        results["prices"].update(kitco_prices)
    except Exception as e:
        results["errors"].append(f"kitco: {e}")

    # Alpha Vantage for copper
    av_prices = fetch_alpha_vantage_copper()
    if av_prices:
        results["prices"].update(av_prices)
    else:
        results["errors"].append("alphavantage copper: no data or API key missing")

    # Record history
    for sym, info in results["prices"].items():
        record_spot_history(
            date_iso, sym, info["name"], info["unit"],
            info["price"], info.get("source", "unknown")
        )

    if not results["prices"]:
        results["status"] = "error"
    elif results["errors"]:
        results["status"] = "partial"

    return results
