"""Slicer parameters shared by every endpoint (query-string -> Filters)."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Optional

import pandas as pd
from fastapi import Query

from .store import get_store


@dataclass
class Filters:
    start: pd.Timestamp
    end: pd.Timestamp
    department: Optional[str] = None
    attack_type: Optional[str] = None
    severity: Optional[str] = None
    status: Optional[str] = None
    country: Optional[str] = None
    domain: Optional[str] = None


def get_filters(
    date_from: Optional[date] = Query(None, alias="from"),
    date_to: Optional[date] = Query(None, alias="to"),
    department: Optional[str] = None,
    attack_type: Optional[str] = None,
    severity: Optional[str] = None,
    status: Optional[str] = None,
    country: Optional[str] = None,
    domain: Optional[str] = None,
) -> Filters:
    s = get_store()
    start = pd.Timestamp(date_from) if date_from else s.min_date
    end = pd.Timestamp(date_to) if date_to else s.max_date
    start, end = max(min(start, end), s.min_date), min(max(start, end), s.max_date)
    return Filters(start, end, department or None, attack_type or None, severity or None,
                   status or None, country or None, domain or None)
