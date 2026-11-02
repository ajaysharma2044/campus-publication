"""Revenue model and report import (SPEC §23). Every quantity has its own denominator and name;
nothing is mixed. Scenarios are labelled as scenarios, never forecasts."""
from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path

import psycopg


@dataclass(frozen=True)
class Metrics:
    pageviews: int
    sessions: int | None
    ad_impressions: int | None
    viewable_impressions: int | None
    earnings_minor: int | None          # net publisher earnings as reported by the network
    currency: str = "USD"

    def page_rpm_minor(self) -> float | None:
        if self.earnings_minor is None or not self.pageviews:
            return None
        return self.earnings_minor / (self.pageviews / 1000)

    def impression_rpm_minor(self) -> float | None:
        if self.earnings_minor is None or not self.ad_impressions:
            return None
        return self.earnings_minor / (self.ad_impressions / 1000)

    def viewability(self) -> float | None:
        if not self.ad_impressions or self.viewable_impressions is None:
            return None
        return self.viewable_impressions / self.ad_impressions

    def session_revenue_minor(self) -> float | None:
        if self.earnings_minor is None or not self.sessions:
            return None
        return self.earnings_minor / self.sessions


def page_revenue_scenario_minor(pageviews: int, assumed_page_rpm_minor: int) -> int:
    """Scenario only (SPEC §23 example): pageviews / 1,000 × assumed publisher page RPM. The RPM is
    net publisher earnings per 1,000 pageviews; do not deduct the network share again."""
    return round(pageviews / 1000 * assumed_page_rpm_minor)


@dataclass
class Contribution:
    gross_publisher_earnings_minor: int
    sponsorship_minor: int
    actual_costs_minor: int
    estimated_costs_minor: int
    missing_cost_items: list[str]

    @property
    def contribution_minor(self) -> int:
        return self.gross_publisher_earnings_minor + self.sponsorship_minor - self.actual_costs_minor - self.estimated_costs_minor


def contribution(conn: psycopg.Connection, month: str, *, hosting_minor: int | None, licensing_minor: int | None, other_minor: int | None = 0) -> Contribution:
    with conn.cursor() as cur:
        cur.execute("SELECT COALESCE(SUM(earnings_minor),0) AS e FROM revenue_reports WHERE provider='adsense' AND granularity='site' AND to_char(report_date,'YYYY-MM')=%s", (month,))
        earnings = int(cur.fetchone()["e"])
        cur.execute("SELECT COALESCE(SUM(earnings_minor),0) AS e FROM revenue_reports WHERE provider='direct_sponsorship' AND to_char(report_date,'YYYY-MM')=%s", (month,))
        spons = int(cur.fetchone()["e"])
        cur.execute("SELECT COALESCE(SUM(amount_minor),0) AS c FROM usage_ledger WHERE month=%s AND kind='actual' AND priced", (month,))
        api_actual = int(cur.fetchone()["c"])
        cur.execute("SELECT count(*) AS n FROM usage_ledger WHERE month=%s AND NOT priced", (month,))
        unpriced = cur.fetchone()["n"]
    missing = []
    if hosting_minor is None:
        missing.append("hosting")
    if licensing_minor is None:
        missing.append("data licensing")
    if unpriced:
        missing.append(f"{unpriced} unpriced API usage entries")
    return Contribution(earnings, spons, api_actual + (hosting_minor or 0) + (other_minor or 0), licensing_minor or 0, missing)


def import_adsense_report(conn: psycopg.Connection, path: Path, *, currency: str) -> int:
    """Import a network CSV (site-level or page-level) as reported, flagged estimated (reports lag
    and revise). Columns: date, granularity, page_path (optional), pageviews, ad_impressions,
    viewable_impressions, clicks, earnings (decimal)."""
    n = 0
    with path.open(newline="", encoding="utf-8") as fh, conn.cursor() as cur:
        for r in csv.DictReader(fh):
            page_id = None
            if r.get("page_path"):
                cur.execute("SELECT id FROM pages WHERE path=%s", (r["page_path"],))
                row = cur.fetchone()
                page_id = row["id"] if row else None
                if page_id is None:
                    continue  # unknown page path: skip rather than invent
            earnings = r.get("earnings")
            cur.execute(
                """INSERT INTO revenue_reports (provider, report_date, granularity, page_id, pageviews, ad_impressions, viewable_impressions, clicks, earnings_minor, currency, is_estimated, raw)
                   VALUES ('adsense',%s,%s,%s,%s,%s,%s,%s,%s,%s,TRUE,%s::jsonb)
                   ON CONFLICT (provider, report_date, granularity, page_id) DO UPDATE SET pageviews=EXCLUDED.pageviews, ad_impressions=EXCLUDED.ad_impressions,
                   viewable_impressions=EXCLUDED.viewable_impressions, clicks=EXCLUDED.clicks, earnings_minor=EXCLUDED.earnings_minor, imported_at=now(), raw=EXCLUDED.raw""",
                (date.fromisoformat(r["date"]), r.get("granularity") or ("page" if page_id else "site"), page_id,
                 int(r["pageviews"]) if r.get("pageviews") else None, int(r["ad_impressions"]) if r.get("ad_impressions") else None,
                 int(r["viewable_impressions"]) if r.get("viewable_impressions") else None, int(r["clicks"]) if r.get("clicks") else None,
                 round(float(earnings) * 100) if earnings not in (None, "") else None, currency, __import__("json").dumps(r)),
            )
            n += 1
    conn.commit()
    return n
