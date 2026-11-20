"""Loads the CSV tables once at start-up and prepares helper columns."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
TABLES = [
    "dim_date", "dim_department", "dim_user", "dim_campaign", "fact_phishing_emails",
    "fact_incidents", "fact_simulations", "fact_training", "fact_filter_daily",
]


def ensure_data() -> None:
    """Generate the synthetic dataset if the CSV files are missing."""
    if all((DATA / f"{t}.csv").exists() for t in TABLES):
        return
    print("[phishguard] CSV data not found - generating it now ...")
    subprocess.run([sys.executable, str(ROOT / "generate_data.py")], check=True, cwd=ROOT)


class Store:
    def __init__(self) -> None:
        ensure_data()
        rd = lambda name, **kw: pd.read_csv(DATA / f"{name}.csv", **kw)  # noqa: E731

        self.dept = rd("dim_department")
        self.users = rd("dim_user")
        self.camps = rd("dim_campaign")
        E = rd("fact_phishing_emails", parse_dates=["received_datetime", "received_date", "week_start_date"])
        I = rd("fact_incidents", parse_dates=["created_datetime", "created_date", "resolved_datetime", "resolved_date"])
        S = rd("fact_simulations", parse_dates=["send_date"])
        T = rd("fact_training")
        F = rd("fact_filter_daily", parse_dates=["date"])

        # --- derived columns --------------------------------------------------
        E["month"] = E.received_date.dt.month
        E["dow"] = E.day_of_week_num - 1                      # 0 = Monday
        inc_status = I.set_index("incident_id").status
        E["inc_status"] = E.incident_id.map(inc_status)       # NaN when no incident exists

        em = E.set_index("email_id")
        I["sender_country"] = I.email_id.map(em.sender_country)
        I["sender_domain"] = I.email_id.map(em.sender_domain)
        I["created_month"] = I.created_date.dt.month
        I["resolved_month"] = I.resolved_date.dt.month
        I["created_week"] = I.created_date - pd.to_timedelta(I.created_date.dt.weekday, unit="D")
        S["month"] = S.send_date.dt.month

        self.E, self.I, self.S, self.T, self.F = E, I, S, T, F
        self.min_date = E.received_date.min()
        self.max_date = E.received_date.max()               # "today" for the dashboard
        self.now = self.max_date


_store: Store | None = None


def get_store() -> Store:
    global _store
    if _store is None:
        _store = Store()
    return _store
