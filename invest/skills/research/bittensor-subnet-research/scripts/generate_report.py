#!/usr/bin/env python3
"""
Generate a human-readable Markdown report from a valuation snapshot.

Usage:
    python3 generate_report.py --snapshot data/valuation_snapshot_YYYYMMDD.json
    python3 generate_report.py                  # auto-finds latest snapshot

Output:
    reports/subnet_report_YYYYMMDD.md
"""

import argparse
import json
import logging
from datetime import datetime, timezone
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger("generate_report")

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
DATA_DIR = PROJECT_ROOT / "data"
REPORTS_DIR = PROJECT_ROOT / "reports"


def find_latest_snapshot(data_dir: Path) -> Path | None:
    candidates = sorted(data_dir.glob("valuation_snapshot_*.json"), reverse=True)
    return candidates[0] if candidates else None


def verdict_emoji(verdict: str) -> str:
    return {
        "Attractive": "🟢",
        "Fair": "🟡",
        "Expensive": "🟠",
        "Bubble": "🔴",
        "Speculative": "🟡",
        "Dying": "🔴",
    }.get(verdict, "⚪")


def build_report(snapshot: dict) -> str:
    meta = snapshot.get("meta", {})
    summary = snapshot.get("summary", {})
    valuations = snapshot.get("valuations", [])
    tao_price = float(meta.get("tao_price_usd", 250.0) or 250.0)
    report_date = meta.get("valuation_date", datetime.now(timezone.utc).isoformat())
    total_subnets = int(meta.get("total_subnets_on_chain", len(valuations)) or len(valuations))

    # Sort: Attractive first, then by price within verdict
    verdict_order = {"Attractive": 0, "Fair": 1, "Expensive": 2, "Bubble": 3, "Speculative": 4, "Dying": 5}
    valuations.sort(key=lambda v: (verdict_order.get(v["verdict"], 99), v.get("price_usd", 0)))

    lines = [
        "# Bittensor Subnet Valuation Report",
        "",
        f"**Date:** {report_date}  ",
        f"**TAO Price:** ${tao_price:,.2f}  ",
        f"**Subnets Evaluated:** {len(valuations)} / {total_subnets} live  ",
        "",
        "---",
        "",
        "## Executive Summary",
        "",
        f"This report applies the **Yuma OpEx-replacement framework** to Bittensor subnet tokens. "
        f"Fundamental value = Daily OpEx Replacement / Daily Miner Emissions. "
        f"Subnets are scored by maturity stage (Speculative → Early → Maturing → Root).",
        "",
        "### Verdict Distribution",
        "",
        "| Verdict | Count |",
        "|---------|-------|",
    ]
    for k, v in summary.get("verdict_distribution", {}).items():
        lines.append(f"| {k} | {v} |")

    suggested = summary.get("suggested_basket", [])
    if suggested:
        lines += [
            "",
            "### Suggested Basket (Top Picks)",
            "",
            "| Subnet | Symbol | Price (USD) | Fundamental Mid | Verdict |",
            "|--------|--------|------------|-----------------|---------|",
        ]
        for b in suggested:
            symbol = b.get("symbol") or b.get("name") or f"SN{b['netuid']}"
            mid = b.get("fundamental_mid_usd", 0)
            mid_str = f"${mid:.2f}" if mid else "N/A"
            lines.append(
                f"| SN{b['netuid']} {b.get('name','')} | {symbol} | "
                f"${b.get('price_usd',0):.2f} | {mid_str} | {verdict_emoji(b['verdict'])} {b['verdict']} |"
            )

    lines += [
        "",
        "---",
        "",
        "## Full Valuation Table",
        "",
        "| NetUID | Name | Stage | Price (TAO) | Price (USD) | UID Fill | Fundamental (mid) | Verdict |",
        "|--------|------|-------|------------|-------------|----------|-------------------|---------|",
    ]

    for v in valuations:
        netuid = v.get("netuid", "")
        name = v.get("name", "") or "—"
        stage = v.get("stage", "")
        price_tao = v.get("price_tao", 0)
        price_usd = v.get("price_usd", 0)
        fill = v.get("uid_fill_pct", 0)
        fund = v.get("fundamental_mid_usd", 0)
        verdict = v.get("verdict", "")
        fund_str = f"${fund:.2f}" if fund > 0 else "N/A"
        lines.append(
            f"| {netuid} | {name} | {stage} | {price_tao:.6f} | ${price_usd:.2f} | "
            f"{fill:.0f}% | {fund_str} | {verdict_emoji(verdict)} {verdict} |"
        )

    # Detailed write-ups for interesting subnets
    lines += [
        "",
        "---",
        "",
        "## Notable Subnet Profiles",
        "",
    ]

    interesting = [v for v in valuations if v.get("verdict") in ("Attractive", "Bubble", "Expensive") or int(v.get("netuid", 0)) in (0, 2, 4, 64, 96)]
    for v in interesting:
        netuid = v.get("netuid", "")
        name = v.get("name", "")
        symbol = v.get("symbol", "")
        stage = v.get("stage", "")
        use_case = v.get("use_case", "")
        price_usd = v.get("price_usd", 0)
        price_tao = v.get("price_tao", 0)
        fund_low = v.get("fundamental_low_usd", 0)
        fund_high = v.get("fundamental_high_usd", 0)
        verdict = v.get("verdict", "")
        notes = v.get("notes", "")
        risks = v.get("risk_flags", [])

        lines += [
            f"### SN{netuid}: {name} ({symbol})",
            "",
            f"- **Stage:** {stage}",
            f"- **Use case:** {use_case}",
            f"- **Price:** {price_tao:.6f} TAO (${price_usd:.2f})",
        ]
        if fund_low > 0:
            lines.append(f"- **Fundamental range:** ${fund_low:.2f} — ${fund_high:.2f}")
        lines += [
            f"- **Verdict:** {verdict_emoji(verdict)} {verdict}",
            "",
        ]
        if notes:
            lines.append(f"*{notes}*")
            lines.append("")
        if risks:
            lines.append("**Risk flags:**")
            for r in risks:
                lines.append(f"- {r}")
            lines.append("")

    lines += [
        "---",
        "",
        "## Methodology Notes",
        "",
        "1. **Yuma Framework:** Subnet tokens replace internal operational expenses. "
        "Fundamental value = (Annual OpEx / 365) / Daily Miner Emissions.",
        "2. **Comparable OpEx:** For subnets without public revenue, we estimate "
        "what the equivalent centralized service would cost (OpenAI API, AWS compute, etc.)",
        "3. **Emissions safety margin:** 10% buffer added to daily emissions assumption.",
        "4. **Miner sell pressure:** Assumes miners must cover hardware/power costs, "
        "so external buyers must step in to sustain price.",
        "5. **Speculative subnets:** Price < 0.003 TAO + low fill = likely worthless. "
        "Price > 0.05 TAO with no use case = bubble risk.",
        "",
        "---",
        "",
        "*Disclaimer: Subnet tokens are highly speculative, illiquid, and pre-revenue. "
        "Most will fail. This framework provides valuation discipline, not a guarantee of returns. "
        "Position size accordingly (suggested max 2-5% of portfolio).",
    ]

    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate Markdown report from valuation snapshot.")
    parser.add_argument(
        "--snapshot",
        type=str,
        default=None,
        help="Path to valuation_snapshot JSON",
    )
    args = parser.parse_args()

    snap_path = Path(args.snapshot) if args.snapshot else find_latest_snapshot(DATA_DIR)
    if not snap_path or not snap_path.exists():
        logger.error("No valuation snapshot found. Run subnet_valuation.py first.")
        raise SystemExit(1)

    snapshot = json.loads(snap_path.read_text(encoding="utf-8"))
    report_md = build_report(snapshot)

    today_str = datetime.now(timezone.utc).strftime("%Y%m%d")
    out_path = REPORTS_DIR / f"subnet_report_{today_str}.md"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(report_md, encoding="utf-8")
    logger.info("Report generated: %s", out_path)
    print(f"Report saved: {out_path}")


if __name__ == "__main__":
    main()
