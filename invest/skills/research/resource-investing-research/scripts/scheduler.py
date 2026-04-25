#!/usr/bin/env python3
"""
Data source scheduler — runs only sources whose next_update <= now.
Updates data_sources.json with last_updated, next_update, status.
Produces a structured summary report.
"""
import json
import os
import sys
import traceback
from datetime import datetime, timezone, timedelta
from pathlib import Path

# Resolve skill directory from __file__ so it works from cron or direct run
BASE_DIR = Path(__file__).resolve().parent.parent  # scripts/ → skill root
SCRIPTS_DIR = BASE_DIR / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

from watchlist_updater import update_equity_prices
from kitco_scraper import run_commodity_fetch

DATA_SOURCES = BASE_DIR / "data_sources.json"
REPORT_DIR = BASE_DIR / ".." / ".." / ".." / ".." / "cron" / "output"
REPORT_DIR = REPORT_DIR.resolve()


def load_sources() -> dict:
    with open(DATA_SOURCES) as f:
        return json.load(f)


def save_sources(data: dict):
    with open(DATA_SOURCES, "w") as f:
        json.dump(data, f, indent=2)


def compute_next_update(periodicity: dict, from_time: datetime) -> datetime:
    """Compute the next update time after from_time based on periodicity config."""
    ptype = periodicity.get("type")
    time_utc = periodicity.get("time_utc", "07:00")
    hour, minute = map(int, time_utc.split(":"))

    if ptype == "weekdays":
        delta = 1
        nxt = from_time + timedelta(days=1)
        while nxt.weekday() >= 5:  # skip weekend
            nxt += timedelta(days=1)
        nxt = nxt.replace(hour=hour, minute=minute, second=0, microsecond=0)
        return nxt

    elif ptype == "days_of_week":
        days = sorted(periodicity.get("days", [1, 4]))
        nxt = from_time + timedelta(days=1)
        for _ in range(14):  # safety bound
            if nxt.weekday() + 1 in days:
                cand = nxt.replace(hour=hour, minute=minute, second=0, microsecond=0)
                if cand > from_time:
                    return cand
            nxt += timedelta(days=1)
        return from_time + timedelta(days=7)

    elif ptype == "weekly":
        dow = periodicity.get("day_of_week", 1)  # 1=Mon
        nxt = from_time + timedelta(days=1)
        for _ in range(14):
            if nxt.weekday() + 1 == dow:
                cand = nxt.replace(hour=hour, minute=minute, second=0, microsecond=0)
                if cand > from_time:
                    return cand
            nxt += timedelta(days=1)
        return from_time + timedelta(days=7)

    elif ptype == "monthly":
        dom = periodicity.get("day_of_month", 1)
        if from_time.day < dom or (from_time.day == dom and (from_time.hour, from_time.minute) < (hour, minute)):
            nxt = from_time.replace(day=dom, hour=hour, minute=minute, second=0, microsecond=0)
        else:
            # next month
            if from_time.month == 12:
                nxt = from_time.replace(year=from_time.year + 1, month=1, day=dom, hour=hour, minute=minute, second=0, microsecond=0)
            else:
                nxt = from_time.replace(month=from_time.month + 1, day=dom, hour=hour, minute=minute, second=0, microsecond=0)
        return nxt

    elif ptype == "quarterly":
        months = sorted(periodicity.get("months", [1, 4, 7, 10]))
        dom = periodicity.get("day_of_month", 1)
        for m in months:
            if from_time.month < m or (from_time.month == m and (from_time.day, from_time.hour, from_time.minute) < (dom, hour, minute)):
                return from_time.replace(month=m, day=dom, hour=hour, minute=minute, second=0, microsecond=0)
        # roll to next year first quarter
        return from_time.replace(year=from_time.year + 1, month=months[0], day=dom, hour=hour, minute=minute, second=0, microsecond=0)

    # fallback: daily
    nxt = from_time + timedelta(days=1)
    return nxt.replace(hour=hour, minute=minute, second=0, microsecond=0)


def should_run(source: dict) -> bool:
    if not source.get("enabled", False):
        return False
    next_update_str = source.get("next_update")
    if not next_update_str:
        return True
    try:
        next_update = datetime.fromisoformat(next_update_str.replace("Z", "+00:00"))
    except Exception:
        return True
    return datetime.now(timezone.utc) >= next_update


def run_source(source_id: str, source: dict, now: datetime) -> dict:
    """Run a single source updater and return result metadata."""
    method = source.get("method", "unknown")
    periodicity = source.get("periodicity", {})

    try:
        if method == "polygon_prev":
            tickers = source.get("tickers", [])
            result = update_equity_prices(now, tickers=tickers if tickers else None)
        elif method == "kitco_scrape":
            result = run_commodity_fetch(now)
        elif method == "derived":
            # Placeholder: record CCJ premium to long-term U assumption
            result = {"status": "ok", "note": "Derived uranium metrics recorded manually"}
        elif method == "manual_csv":
            result = {"status": "ok", "note": "Manual review flagged; no auto-update"}
        elif method == "manual":
            result = {"status": "ok", "note": "Manual source; toggle enabled to process"}
        else:
            result = {"status": "error", "errors": [f"unknown method: {method}"]}
    except Exception as e:
        result = {"status": "error", "errors": [str(e), traceback.format_exc()]}

    # Update source metadata
    source["last_updated"] = now.strftime("%Y-%m-%dT%H:%M:%SZ")
    source["last_status"] = result.get("status", "unknown")
    source["last_error"] = "; ".join(result.get("errors", [])) if result.get("errors") else None
    source["next_update"] = compute_next_update(periodicity, now).strftime("%Y-%m-%dT%H:%M:%SZ")

    result["source_id"] = source_id
    result["next_scheduled"] = source["next_update"]
    return result


def build_report(results: list) -> str:
    now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines = [
        f"# Resource Investing Data Report\n",
        f"**Generated:** {now_str}  \n",
        f"**Framework:** Rick Rule 5P scoring | Buy rule: < 80% NAV | Hold: 5-year horizon  \n\n",
        "## Source Updates\n",
        "| Source | Method | Status | Updated | Next Update | Detail |",
        "|--------|--------|--------|---------|-------------|--------|",
    ]
    for r in results:
        sid = r.get("source_id", "?")
        status = r.get("status", "?")
        updated = r.get("updated", "-")
        nxt = r.get("next_scheduled", "?")
        detail = ""
        if "prices" in r:
            price_parts = []
            for k, v in r["prices"].items():
                if isinstance(v, dict):
                    price_parts.append(f"{k}=${v['price']:,.2f}")
                else:
                    price_parts.append(f"{k}=${v:,.2f}")
            detail = ", ".join(price_parts)
        elif "updated" in r:
            detail = f"{r['updated']} tickers updated"
        elif "note" in r:
            detail = r["note"]
        lines.append(f"| {sid} | {r.get('_method', '-')} | {status} | {updated} | {nxt} | {detail} |")

    lines.append("\n## Errors\n")
    errors = [r for r in results if r.get("errors")]
    if errors:
        for r in errors:
            for e in r.get("errors", []):
                lines.append(f"- **{r['source_id']}**: {e}")
    else:
        lines.append("_No errors._")

    lines.append("\n## Pending (not yet due)\n")
    # This gets filled by main if needed
    lines.append("_All enabled due sources were processed._\n")

    return "\n".join(lines)


def main():
    now = datetime.now(timezone.utc)
    data = load_sources()
    sources = data.get("sources", {})
    results = []
    pending = []

    for sid, source in sources.items():
        if should_run(source):
            # Tag method for reporting
            source_copy = dict(source)
            result = run_source(sid, source, now)
            result["_method"] = source_copy.get("method", "-")
            results.append(result)
        else:
            next_up = source.get("next_update", "?")
            pending.append(f"- **{sid}**: next {next_up}")

    save_sources(data)

    # Inject pending into report
    report = build_report(results)
    if pending:
        report = report.replace("_All enabled due sources were processed._", "\n".join(pending))

    date_stamp = now.strftime("%Y%m%d")
    report_path = REPORT_DIR / f"resource_investing_report_{date_stamp}.md"
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    with open(report_path, "w") as f:
        f.write(report)

    print(report)
    print(f"\nReport saved: {report_path}")
    print(f"Sources processed: {len(results)}, pending: {len(pending)}")


if __name__ == "__main__":
    main()
