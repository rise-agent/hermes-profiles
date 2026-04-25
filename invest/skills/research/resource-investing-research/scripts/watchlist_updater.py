#!/usr/bin/env python3
"""
Resource Investing Watchlist Updater — scheduler-callable module.
Fetches prior-day closes from Polygon.io and updates CSVs + history.
"""
import csv
import json
import os
import traceback
from datetime import datetime, timezone
from pathlib import Path

import requests

API_KEY=os.environ.get("POLYGON_API_KEY", "")
# Resolve skill directory from __file__ so it works from cron or direct run
BASE_DIR = Path(__file__).resolve().parent.parent  # scripts/ → skill root
REPORT_DIR = BASE_DIR / ".." / ".." / ".." / ".." / "cron" / "output"
REPORT_DIR = REPORT_DIR.resolve()
SLEEP_SEC = 15
HISTORY_DIR = BASE_DIR / "prices_history"


def ensure_dirs():
    BASE_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    HISTORY_DIR.mkdir(parents=True, exist_ok=True)


def ensure_csv(filepath: Path, header: list, rows: list):
    if not filepath.exists():
        with open(filepath, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(header)
            writer.writerows(rows)


def ensure_watchlists():
    """Create starter CSVs if missing."""
    c = ["ticker", "name", "sector", "jurisdiction", "market_cap_b",
         "score_people", "score_property", "score_politics", "score_phinance", "score_paper",
         "composite_score", "rating", "last_close", "change_pct",
         "target_entry", "target_scale_in", "target_full",
         "position_size_pct", "notes"]
    copper = [
        ["FCX","Freeport-McMoRan","Copper/Gold","USA/Indonesia","97","4","4","3","4","2","3.4","Satellite","","","58.00","62.00","66.00","5","+111% run; insider selling $35M; P/E 46; wait for 10% correction"],
        ["SCCO","Southern Copper","Copper","Peru/Mexico","143","3","5","2","4","2","3.2","Satellite","","","165.00","172.00","182.00","4","Lowest cost curve; Peru political risk; CEO transition"],
        ["COPX","Global X Copper Miners ETF","ETF","Global","3","3","3","3","3","3","3.0","Satellite","","","74.00","76.00","80.00","3","Diversified juniors/majors; use as sector proxy"],
        ["ERO","Ero Copper","Copper","Brazil","2","4","3","3","3","3","3.2","Satellite","","","","","","3","High-grade Brazil underground; good mgmt; smaller scale"],
        ["HBM","Hudbay Minerals","Copper/Zinc","Canada/Peru","3","3","3","3","3","3","3.0","Satellite","","","","","","3","Re-rating story; Constancia + Snow Lake; watch balance sheet"],
        ["WRN","Western Copper & Gold","Copper/Gold Dev","Canada","0.4","3","4","4","2","2","3.0","Speculative","","","","","","2","Casino project; developer stage; permitting risk; optionality"],
    ]
    u = [
        ["CCJ","Cameco","Uranium","Canada/USA/Kazakhstan","26","5","4","3","4","3","3.8","Core","","","32.00","35.00","38.00","8","Largest producer; Inkai JV; conservative mgmt; quality anchor"],
        ["UUUU","Energy Fuels","Uranium/REE","USA","1.2","4","3","4","3","3","3.4","Satellite","","","","","","3","US producer; White Mesa mill; REE pivot; political premium"],
        ["DNN","Denison Mines","Uranium Dev","Canada","1.5","4","4","4","3","3","3.6","Satellite","","","","","","3","Wheel River; ISR development; permitting progress"],
        ["NXE","NexGen Energy","Uranium Dev","Canada","4","4","5","4","3","2","3.6","Satellite","","","","","","4","Arrow deposit; best undeveloped asset globally; financing risk"],
        ["URA","Global X Uranium ETF","ETF","Global","3","3","3","3","3","3","3.0","Satellite","","","","","","3","Diversified uranium exposure; use for sector beta"],
        ["URNM","Sprott Uranium Miners ETF","ETF","Global","2","3","3","3","3","3","3.0","Satellite","","","","","","2","Concentrated producer dev exposure; Sprott liquidity"],
        ["URNJ","Sprott Junior Uranium Miners ETF","ETF","Global","0.5","3","3","3","3","3","3.0","Speculative","","","","","","2","High-beta juniors; volatile; only for speculation"],
    ]
    s = [
        ["FSLR","First Solar","Solar Modules","USA/Malaysia","18","4","5","4","4","3","4.0","Core","","","","","7","US manufacturing; IRA beneficiary; thin-film leader; quality"],
        ["ENPH","Enphase Energy","Microinverters","USA","8","4","4","3","3","4","3.6","Satellite","","","","","4","Microinverter leader; demand pause; inventory correction ongoing"],
        ["SEDG","SolarEdge","Power Optimizers","Israel/USA","2","3","3","3","2","4","3.0","Speculative","","","","","2","Losses widening; market share pressure; turnaround bet only"],
        ["RUN","Sunrun","Residential Solar","USA","2","3","3","3","2","3","2.8","Speculative","","","","","2","NEM 3.0 headwinds; financing model under pressure; avoid for now"],
        ["SHLS","Shoals Technologies","BOS/Electrification","USA","2","4","4","3","3","3","3.4","Satellite","","","","","3","EBOS leader; data center + solar convergence; solid mgmt"],
        ["ICLN","iShares Global Clean Energy ETF","ETF","Global","3","3","3","3","3","3","3.0","Satellite","","","","","3","Diversified clean energy; use for broad exposure"],
        ["TAN","Invesco Solar ETF","ETF","Global","0.8","3","3","3","3","3","3.0","Satellite","","","","","2","Concentrated solar; higher beta than ICLN"],
    ]
    a = [
        ["CF","CF Industries Holdings Inc","Materials","USA","18.8","4","5","5","5","4.5","4.7","Core","125.59","0.0","96.00","108.00","120.00","8","Best-in-class nitrogen cost curve. Fortress balance sheet. Non-substitutable input.","","120.00"],
        ["NTR","Nutrien Ltd","Materials","Canada","34.7","3.5","4.5","4","4","4","4.0","Core","72.19","0.0","48.00","54.00","60.00","6","World's largest potash + retail. Defensive. 3% dividend. Canadian jurisdiction.","","60.00"],
        ["AGCO","AGCO Corporation","Industrials","USA/EU","8.7","4","3.5","4","4","4.5","4.0","Core","119.54","0.0","88.00","99.00","110.00","5","Deep-value equipment alternative to DE. Fendt brand. Global footprint.","","110.00"],
        ["DE","Deere & Company","Industrials","USA","156.7","4","5","3.5","4","2.5","3.8","Satellite","591.95","0.0","320.00","360.00","400.00","3","Unmatched precision-ag moat. Quality franchise but 33x PE = expensive. Watchlist until $320-400 entry.","","400.00"],
        ["MOS","The Mosaic Company","Materials","USA","7.9","3","4","3.5","3.5","4.5","3.7","Satellite","24.28","0.0","16.00","18.00","20.00","4","Value phosphate/potash. Florida env risk. 3.6% yield. Smaller position only.","","20.00"],
    ]
    for fname, rows in [("copper.csv", copper), ("uranium.csv", u), ("solar.csv", s), ("agriculture.csv", a)]:
        ensure_csv(BASE_DIR / fname, c, rows)


def fetch_price(ticker: str, retries: int = 2) -> dict:
    url = f"https://api.polygon.io/v2/aggs/ticker/{ticker}/prev"
    for attempt in range(retries + 1):
        try:
            r = requests.get(url, params={"apikey": API_KEY}, timeout=20)
            data = r.json()
        except Exception as e:
            return {"error": f"request: {e}"}
        status = data.get("status", "")
        if status not in ("OK", "DELAYED"):
            err = data.get("error", "")
            if "maximum requests per minute" in err.lower() and attempt < retries:
                import time
                time.sleep(30 * (attempt + 1))
                continue
            return {"error": f"API {status}: {err}"}
        results = data.get("results", [])
        if not results:
            return {"error": "no results"}
        p = results[0]
        return {
            "close": float(p["c"]),
            "open": float(p.get("o", p["c"])),
            "change_pct": round(((float(p["c"]) - float(p.get("o", p["c"]))) / float(p.get("o", p["c"]))) * 100, 2) if float(p.get("o", p["c"])) else 0.0,
            "volume": float(p.get("v", 0)),
        }
    return {"error": "retries exhausted"}


def record_equity_history(date_iso: str, ticker: str, close: float, change_pct: float):
    hist = HISTORY_DIR / "equity_prices.csv"
    if not hist.exists():
        with open(hist, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["date", "ticker", "close", "change_pct"])
    with open(hist, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([date_iso, ticker, round(close, 4), change_pct])


def update_equity_prices(now: datetime, tickers: list = None) -> dict:
    """Returns {status, updated, errors, source_next_update}."""
    import time
    ensure_dirs()
    ensure_watchlists()

    if not API_KEY:
        return {"status": "error", "errors": ["POLYGON_API_KEY not set"], "updated": 0}

    date_iso = now.strftime("%Y-%m-%d")
    files = ["copper.csv", "uranium.csv", "solar.csv", "agriculture.csv"]
    total_updated = 0
    errors = []

    for fname in files:
        fpath = BASE_DIR / fname
        rows = []
        with open(fpath, newline="") as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames or []
            rows = list(reader)

        for row in rows:
            ticker = row["ticker"].strip()
            if tickers and ticker not in tickers:
                continue
            pdata = fetch_price(ticker)
            if "error" in pdata:
                errors.append(f"{ticker}: {pdata['error']}")
                time.sleep(SLEEP_SEC)
                continue
            prev = row.get("last_close", "").strip()
            close = pdata["close"]
            chg = pdata["change_pct"]
            row["last_close"] = str(close)
            row["change_pct"] = str(chg)

            # Recompute composite
            try:
                scores = [float(row.get(f"score_{p}", 3)) for p in ["people", "property", "politics", "phinance", "paper"]]
                comp = round(sum(scores) / 5, 1)
                row["composite_score"] = str(comp)
                row["rating"] = "Core" if comp >= 4.0 else ( "Satellite" if comp >= 3.0 else "Speculative")
            except Exception:
                pass

            vs_target = ""
            target = row.get("target_entry", "").strip()
            if target:
                try:
                    t = float(target)
                    vs_target = "AT/BUY" if close <= t else ( "NEAR" if close <= t * 1.05 else "ABOVE")
                except Exception:
                    pass
            row["vs_target"] = vs_target
            record_equity_history(date_iso, ticker, close, chg)
            total_updated += 1
            time.sleep(SLEEP_SEC)

        # Write back
        with open(fpath, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames + ([ "vs_target"] if "vs_target" not in fieldnames else []))
            writer.writeheader()
            writer.writerows(rows)

    return {
        "status": "ok" if not errors else "partial",
        "updated": total_updated,
        "errors": errors,
        "next_update": _next_weekday_7am(now),
    }


def _next_weekday_7am(now: datetime) -> str:
    """Return next Monday-Friday 7am UTC after now."""
    weekday = now.weekday()  # 0=Mon
    if weekday >= 4:  # Fri or weekend
        delta = 7 - weekday
    else:
        delta = 1
    nxt = now + __import__("datetime").timedelta(days=delta)
    nxt = nxt.replace(hour=7, minute=0, second=0, microsecond=0)
    return nxt.strftime("%Y-%m-%dT%H:%M:%SZ")
