"""All dashboard calculations (pandas). One function per dashboard page."""
from __future__ import annotations

import calendar
from datetime import timedelta
from typing import Optional

import numpy as np
import pandas as pd

from .filters import Filters
from .store import Store

SEV_ORDER = ["Critical", "High", "Medium", "Low"]
SEV_RANK = {"Low": 0, "Medium": 1, "High": 2, "Critical": 3}
DOW = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
STATUSES = ["Open", "In Progress", "Escalated", "Resolved"]

OK, WARN, BAD, CY = "#3ddc97", "#f2c14e", "#ff4d6d", "#22d3ee"


# ----------------------------------------------------------------- helpers ----
def rate(a, b) -> float:
    return float(a) / float(b) * 100 if b else 0.0


def top_counts(series: pd.Series, n: int = 10) -> dict:
    vc = series.dropna().value_counts().head(n)
    return {"labels": [str(x) for x in vc.index], "values": [int(v) for v in vc.values]}


def top_dict(d: dict, n: int = 11) -> dict:
    items = sorted(((k, v) for k, v in d.items() if v > 0), key=lambda x: -x[1])[:n]
    return {"labels": [k for k, _ in items], "values": [round(float(v), 1) for _, v in items]}


def month_list(f: Filters) -> list[int]:
    return list(range(f.start.month, f.end.month + 1))


def month_labels(months) -> list[str]:
    return [calendar.month_abbr[m] for m in months]


def week_starts(f: Filters) -> pd.DatetimeIndex:
    first = f.start - timedelta(days=f.start.weekday())
    return pd.date_range(first, f.end, freq="7D")


def wlabel(d: pd.Timestamp) -> str:
    return f"{d:%b} {d.day}"


# --------------------------------------------------------------- selection ----
def sel_emails(s: Store, f: Filters, start=None, end=None) -> pd.DataFrame:
    E = s.E
    m = (E.received_date >= (start or f.start)) & (E.received_date <= (end or f.end))
    if f.department: m &= E.department.eq(f.department)
    if f.attack_type: m &= E.attack_type.eq(f.attack_type)
    if f.severity: m &= E.severity.eq(f.severity)
    if f.country: m &= E.sender_country.eq(f.country)
    if f.domain: m &= E.sender_domain.eq(f.domain)
    if f.status: m &= E.inc_status.eq(f.status)          # emails whose incident has this status
    return E[m]


def sel_inc(s: Store, f: Filters, start=None, end=None) -> pd.DataFrame:
    I = s.I
    m = (I.created_date >= (start or f.start)) & (I.created_date <= (end or f.end))
    if f.department: m &= I.department.eq(f.department)
    if f.attack_type: m &= I.attack_type.eq(f.attack_type)
    if f.severity: m &= I.severity.eq(f.severity)        # incident's own (possibly escalated) severity
    if f.country: m &= I.sender_country.eq(f.country)
    if f.domain: m &= I.sender_domain.eq(f.domain)
    if f.status: m &= I.status.eq(f.status)
    return I[m]


def sel_sims(s: Store, f: Filters) -> pd.DataFrame:
    S = s.S
    m = (S.send_date >= f.start) & (S.send_date <= f.end)
    if f.department: m &= S.department.eq(f.department)
    return S[m]


def sel_training(s: Store, f: Filters) -> pd.DataFrame:
    return s.T[s.T.department.eq(f.department)] if f.department else s.T


def sel_filter_daily(s: Store, f: Filters) -> pd.DataFrame:
    return s.F[(s.F.date >= f.start) & (s.F.date <= f.end)]


# ----------------------------------------------------------------- metrics ----
def metrics(E: pd.DataFrame, I: pd.DataFrame) -> dict:
    n = len(E)
    det, blk = int(E.is_detected.sum()), int(E.is_blocked.sum())
    deliv, miss = int(E.is_delivered.sum()), int(E.is_missed.sum())
    clk, rep, cred = int(E.clicked.sum()), int(E.reported_by_user.sum()), int(E.submitted_credentials.sum())
    done = I[I.status == "Resolved"]
    return dict(
        total=n, det=det, blk=blk, deliv=deliv, miss=miss, clk=clk, rep=rep, cred=cred,
        det_rate=rate(det, n), clk_rate=rate(clk, deliv), rep_rate=rate(rep, deliv),
        inc=len(I), res=len(done), act=len(I) - len(done), od=int(I.is_overdue.sum()),
        avg_resp=float(I.response_time_minutes.mean()) if len(I) else 0.0,
        avg_res=float(done.resolution_time_hours.mean()) if len(done) else 0.0,
        breach=rate(I.sla_breached.sum(), len(I)),
    )


def prev_metrics(s: Store, f: Filters) -> Optional[dict]:
    """Same-length period immediately before the selected one (None if it starts before the data)."""
    length = (f.end - f.start).days + 1
    ps, pe = f.start - timedelta(days=length), f.start - timedelta(days=1)
    if ps < s.min_date or f.start <= s.min_date:
        return None
    return metrics(sel_emails(s, f, ps, pe), sel_inc(s, f, ps, pe))


# name -> definition. `metric` is a key of metrics(); up = which direction is good.
KPI = {
    "rep": dict(metric="rep", label="Phishing Emails Reported", fmt="int", up="good", color="#4a8cf0",
                note=lambda m: f"by employees · {m['rep_rate']:.1f}% of delivered"),
    "det": dict(metric="det", label="Phishing Emails Detected", fmt="int", up="good", color="#0fa5c0",
                note=lambda m: f"of {m['total']:,} total phishing emails"),
    "blk": dict(metric="blk", label="Phishing Emails Blocked", fmt="int", up="good", color=OK,
                note=lambda m: f"{rate(m['blk'], m['total']):.1f}% blocked or quarantined"),
    "clk": dict(metric="clk", label="Phishing Emails Clicked", fmt="int", up="bad", color=BAD,
                note=lambda m: f"{m['clk_rate']:.1f}% click rate · {m['cred']:,} gave credentials"),
    "res": dict(metric="res", label="Incidents Resolved", fmt="int", up="good", color=OK,
                note=lambda m: f"of {m['inc']:,} incidents"),
    "det_rate": dict(metric="det_rate", label="Detection Rate", fmt="pct", up="good", pp=True, color="#0fa5c0",
                     note=lambda m: f"{m['miss']:,} missed by filters"),
    "avg_resp": dict(metric="avg_resp", label="Avg Incident Response Time", fmt="minutes", up="bad", color="#8b7cf6",
                     note=lambda m: "time to first analyst response"),
    "act": dict(metric="act", label="Active Phishing Incidents", fmt="int", up=None, color=WARN,
                note=lambda m: f"{m['od']:,} overdue past SLA"),
    # incident page
    "open": dict(metric="act", label="Open Phishing Incidents", fmt="int", up=None, color=WARN,
                 note=lambda m: "Open · In Progress · Escalated"),
    "od": dict(metric="od", label="Overdue Incidents", fmt="int", up=None, color=BAD,
               note=lambda m: "Past SLA and still unresolved"),
    "avg_res": dict(metric="avg_res", label="Avg Time to Resolve", fmt="hours", up="bad", color="#8b7cf6",
                    note=lambda m: "resolved incidents"),
    "breach": dict(metric="breach", label="SLA Breach Rate", fmt="pct", up="bad", pp=True, color="#e06a30",
                   note=lambda m: "incidents beyond SLA target"),
}


def build_kpis(s: Store, f: Filters, names: list[str]) -> list[dict]:
    E, I = sel_emails(s, f), sel_inc(s, f)
    cur, prev = metrics(E, I), prev_metrics(s, f)
    months = month_list(f)
    series = [metrics(E[E.month == m], I[I.created_month == m]) for m in months]
    out = []
    for name in names:
        d = KPI[name]
        key = d["metric"]
        delta = None
        if prev is not None and d.get("up"):
            v, p = cur[key], prev[key]
            ch = (v - p) if d.get("pp") else ((v - p) / p * 100 if p else 0.0)
            tone = "flat" if abs(ch) < 0.05 else ("good" if (ch > 0) == (d["up"] == "good") else "bad")
            delta = {"value": round(ch, 1), "unit": "pp" if d.get("pp") else "%", "tone": tone}
        out.append(dict(key=name, label=d["label"], fmt=d["fmt"], value=cur[key], color=d["color"],
                        note=d["note"](cur), delta=delta, spark=[x[key] for x in series]))
    return out


# ------------------------------------------------------------------ pages -----
def summary(s: Store, f: Filters) -> dict:
    E, I = sel_emails(s, f), sel_inc(s, f)
    active = I[I.status != "Resolved"]
    crit = int((active.severity == "Critical").sum())
    level = "ELEVATED" if crit >= 2 else ("GUARDED" if len(active) >= 10 else "STABLE")
    return dict(emails=len(E), incidents=len(I), active=len(active), critical_open=crit, threat_level=level)


def meta(s: Store) -> dict:
    E = s.E
    order = E.sender_domain.value_counts()
    return dict(
        min_date=f"{s.min_date:%Y-%m-%d}", max_date=f"{s.max_date:%Y-%m-%d}",
        departments=list(s.dept.department_name),
        attack_types=list(E.attack_type.value_counts().index),
        severities=SEV_ORDER, statuses=STATUSES,
        countries=list(E.sender_country.value_counts().index),
        domains=list(order.index[:80]),
    )


def _incident_rows(s: Store, df: pd.DataFrame) -> list[dict]:
    return [dict(incident_id=r.incident_id, created=f"{r.created_date:%Y-%m-%d}", severity=r.severity,
                 attack_type=r.attack_type, department=r.department, team=r.assigned_team, status=r.status,
                 investigation=r.investigation_status, overdue=bool(r.is_overdue),
                 age_days=int((s.now - r.created_date).days)) for r in df.itertuples()]


def executive(s: Store, f: Filters) -> dict:
    E, I = sel_emails(s, f), sel_inc(s, f)
    m = metrics(E, I)
    months = month_list(f)
    blocked = [int(E[E.month == x].is_blocked.sum()) for x in months]
    warn = [int(((E.month == x) & (E.is_detected == 1) & (E.is_delivered == 1)).sum()) for x in months]
    missed = [int(E[E.month == x].is_missed.sum()) for x in months]
    sev = E.severity.value_counts().reindex(SEV_ORDER, fill_value=0)
    funnel = [("Total phishing emails", m["total"]), ("Detected", m["det"]), ("Blocked / quarantined", m["blk"]),
              ("Delivered to mailbox", m["deliv"]), ("Reported by employees", m["rep"]),
              ("Clicked a link", m["clk"]), ("Submitted credentials", m["cred"])]
    crit = I[(I.status != "Resolved") & I.severity.isin(["Critical", "High"])].copy()
    crit["rank"] = crit.severity.map(SEV_RANK)
    crit = crit.sort_values(["rank", "created_date"], ascending=[False, True]).head(8)
    return dict(
        kpis=build_kpis(s, f, ["rep", "det", "blk", "clk", "res", "det_rate", "avg_resp", "act"]),
        monthly=dict(labels=month_labels(months), blocked=blocked, warning=warn, missed=missed),
        gauge=dict(rate=m["det_rate"], detected=m["det"], missed=m["miss"], miss_rate=rate(m["miss"], m["total"])),
        severity=dict(labels=SEV_ORDER, values=[int(v) for v in sev.values]),
        funnel=[dict(label=a, value=int(b)) for a, b in funnel],
        departments=top_counts(E.department, 6),
        incidents=_incident_rows(s, crit),
    )


def trends(s: Store, f: Filters) -> dict:
    E, I = sel_emails(s, f), sel_inc(s, f)
    months = month_list(f)
    weeks = week_starts(f)
    wk = E.groupby("week_start_date").size().reindex(weeks, fill_value=0)
    wi = I.groupby("created_week").size().reindex(weeks, fill_value=0)
    days = pd.date_range(f.start, f.end)
    daily = E.groupby("received_date").size().reindex(days, fill_value=0)
    ma = daily.rolling(7, min_periods=1).mean().round(1)
    dow = E.groupby("dow").size().reindex(range(7), fill_value=0)
    hour = E.groupby("hour_of_day").size().reindex(range(24), fill_value=0)
    heat = pd.crosstab(E.dow, E.hour_of_day).reindex(index=range(7), columns=range(24), fill_value=0)
    return dict(
        monthly=dict(labels=month_labels(months), values=[int((E.month == m).sum()) for m in months]),
        weekly=dict(labels=[wlabel(d) for d in weeks], values=[int(v) for v in wk.values]),
        daily=dict(labels=[f"{d:%m-%d}" for d in days], values=[int(v) for v in daily.values], average=[float(v) for v in ma.values]),
        incidents_weekly=dict(labels=[wlabel(d) for d in weeks], values=[int(v) for v in wi.values]),
        dow=dict(labels=DOW, values=[int(v) for v in dow.values]),
        hour=dict(labels=[f"{h:02d}" for h in range(24)], values=[int(v) for v in hour.values]),
        heatmap=dict(rows=DOW, cols=list(range(24)), values=heat.values.tolist()),
    )


def threats(s: Store, f: Filters) -> dict:
    E = sel_emails(s, f)
    sev = E.severity.value_counts().reindex(SEV_ORDER, fill_value=0)
    urls = (E[E.malicious_url.notna()].groupby("malicious_url")
            .agg(emails=("email_id", "size"), clicks=("clicked", "sum")).sort_values("emails", ascending=False).head(10))
    camp = (E[E.campaign_id != "CMP-000"].groupby("campaign_id")
            .agg(emails=("email_id", "size"), detected=("is_detected", "mean"), clicks=("clicked", "sum"))
            .sort_values("emails", ascending=False).head(10).reset_index()
            .merge(s.camps[["campaign_id", "campaign_name", "primary_attack_type"]], on="campaign_id", how="left"))
    return dict(
        attack_type=top_counts(E.attack_type, 12),
        severity=dict(labels=SEV_ORDER, values=[int(v) for v in sev.values]),
        category=top_counts(E.threat_category, 8),
        domains=top_counts(E.sender_domain, 10),
        subjects=top_counts(E.subject, 10),
        attachments=top_counts(E.attachment_type, 9),
        countries=top_counts(E.sender_country, 8),
        providers=top_counts(E.email_provider, 7),
        urls=[dict(url=u, emails=int(r.emails), clicks=int(r.clicks)) for u, r in urls.iterrows()],
        campaigns=[dict(name=r.campaign_name, type=r.primary_attack_type, emails=int(r.emails),
                        detect_pct=round(float(r.detected) * 100, 1), clicks=int(r.clicks)) for r in camp.itertuples()],
    )


def _dept_stats(s: Store, E: pd.DataFrame, I: pd.DataFrame) -> pd.DataFrame:
    depts = list(s.dept.department_name)
    g = E.groupby("department").agg(emails=("email_id", "size"), delivered=("is_delivered", "sum"), clicks=("clicked", "sum"),
                                    reports=("reported_by_user", "sum"), creds=("submitted_credentials", "sum")).reindex(depts, fill_value=0)
    g["incidents"] = I.groupby("department").size().reindex(depts, fill_value=0)
    g["headcount"] = s.dept.set_index("department_name").headcount.reindex(depts)
    g["click_rate"] = [rate(a, b) for a, b in zip(g.clicks, g.delivered)]
    g["report_rate"] = [rate(a, b) for a, b in zip(g.reports, g.delivered)]
    g["risk"] = (g.clicks + 3 * g.creds) / g.headcount * 100
    return g


def users(s: Store, f: Filters) -> dict:
    E, I = sel_emails(s, f), sel_inc(s, f)
    g = _dept_stats(s, E, I)
    ua = (E.groupby("target_user_id").agg(n=("email_id", "size"), clk=("clicked", "sum"), rep=("reported_by_user", "sum"),
                                         cred=("submitted_credentials", "sum"), camps=("campaign_id", "nunique"))
          .join(s.users.set_index("user_id")[["full_name", "department", "seniority"]]))
    ua["risk"] = ua.clk * 3 + ua.cred * 5
    ua = ua.reset_index().rename(columns={"target_user_id": "user_id"})

    def rows(df, n=10):
        return [dict(user_id=r.user_id, name=r.full_name, department=r.department, level=r.seniority, emails=int(r.n),
                     clicks=int(r.clk), reports=int(r.rep), creds=int(r.cred), campaigns=int(r.camps), risk=int(r.risk))
                for r in df.head(n).itertuples()]

    return dict(
        incidents_by_dept=top_dict(g.incidents.to_dict()),
        targeted_by_dept=top_dict(g.emails.to_dict()),
        risk_by_dept=top_dict(g.risk.to_dict()),
        click_rate_by_dept=top_dict(g.click_rate.to_dict()),
        report_rate_by_dept=top_dict(g.report_rate.to_dict()),
        top_targeted=rows(ua.sort_values("n", ascending=False)),
        high_risk=rows(ua[ua.risk > 0].sort_values(["risk", "n"], ascending=False)),
        clickers=rows(ua[ua.clk > 0].sort_values(["clk", "n"], ascending=False)),
        credential_submitters=rows(ua[ua.cred > 0].sort_values(["cred", "clk"], ascending=False)),
        reporters=rows(ua[ua.rep > 0].sort_values("rep", ascending=False)),
        repeat_targets=rows(ua[ua.clk >= 2].sort_values(["clk", "camps"], ascending=False)),
    )


def incidents(s: Store, f: Filters) -> dict:
    I = sel_inc(s, f)
    months = month_list(f)
    labels = month_labels(months)
    by = lambda col: I[col].value_counts()  # noqa: E731
    resolved = I[I.status == "Resolved"]
    opened = [int((I.created_month == m).sum()) for m in months]
    closed = [int((I.resolved_month == m).sum()) for m in months]
    avg_hours = [round(float(resolved[resolved.resolved_month == m].resolution_time_hours.mean()), 1)
                 if (resolved.resolved_month == m).any() else 0.0 for m in months]
    sev_stats = I.groupby("severity").agg(n=("incident_id", "size"), resp=("response_time_minutes", "mean"),
                                          breach=("sla_breached", "mean")).reindex(SEV_ORDER)
    sev_stats = sev_stats.fillna(0)
    status = I.status.value_counts().reindex(STATUSES, fill_value=0)
    openlist = I[I.status != "Resolved"].sort_values("created_date").head(30)
    return dict(
        kpis=build_kpis(s, f, ["open", "res", "od", "avg_res", "avg_resp", "breach"]),
        status=dict(labels=STATUSES, values=[int(v) for v in status.values]),
        investigation={"labels": list(by("investigation_status").index), "values": [int(v) for v in by("investigation_status").values]},
        team={"labels": list(by("assigned_team").index), "values": [int(v) for v in by("assigned_team").values]},
        opened_vs_resolved=dict(labels=labels, opened=opened, resolved=closed),
        resolution_trend=dict(labels=labels, values=avg_hours),
        severity=dict(labels=SEV_ORDER, count=[int(v) for v in sev_stats.n],
                      response=[round(float(v), 1) for v in sev_stats.resp], breach=[round(float(v) * 100, 1) for v in sev_stats.breach]),
        open_incidents=_incident_rows(s, openlist),
    )


def awareness(s: Store, f: Filters) -> dict:
    E, I = sel_emails(s, f), sel_inc(s, f)
    S, T, F = sel_sims(s, f), sel_training(s, f), sel_filter_daily(s, f)
    m = metrics(E, I)
    months = month_list(f)
    courses = s.T[["course_id", "course_name"]].drop_duplicates().values.tolist()
    done = lambda cid: rate((T[T.course_id == cid].status == "Completed").sum(), (T.course_id == cid).sum())  # noqa: E731
    old = T[T.course_id.isin([c[0] for c in courses[:2]])]
    fp, flagged = int(F.false_positives.sum()), int(F.total_flagged.sum())
    kp = lambda label, value, note, color: dict(label=label, fmt="pct", value=value, note=note, color=color, delta=None, spark=[])  # noqa: E731
    kpis = [
        kp("Training Completion", rate((old.status == "Completed").sum(), len(old)), "Annual + refresher courses", OK),
        kp("Q4 Course Progress", done(courses[2][0]), "Social Engineering & BEC · in progress", WARN),
        kp("Simulation Success Rate", float(S.passed.mean() * 100) if len(S) else 0.0, "users who did not click", CY),
        kp("Simulation Reporting Rate", float(S.reported.mean() * 100) if len(S) else 0.0, "users who reported the test email", "#4a8cf0"),
        kp("Employee Reporting Rate", m["rep_rate"], "live phishing reported ÷ delivered", "#8b7cf6"),
        kp("False Positive Rate", rate(fp, flagged), f"{fp:,} legit emails flagged", "#e06a30"),
    ]
    sim_m = [S[S.month == x] for x in months]
    pct = lambda col: [round(float(d[col].mean() * 100), 1) if len(d) else 0.0 for d in sim_m]  # noqa: E731
    F2 = F.assign(month=F.date.dt.month)
    fp_month = [round(rate(F2[F2.month == x].false_positives.sum(), F2[F2.month == x].total_flagged.sum()), 2) for x in months]
    dept_tr = T.groupby("department").apply(lambda d: rate((d.status == "Completed").sum(), len(d)), include_groups=False)
    g = _dept_stats(s, E, I)
    order = g.sort_values("report_rate", ascending=False)
    tpl = S.groupby("template_type").clicked.mean().mul(100).round(1)
    tpl = tpl[tpl > 0].sort_values(ascending=False)
    sim_dept = S.groupby("department").passed.mean().mul(100)
    score = []
    for d, r in g.iterrows():
        score.append(dict(department=d, staff=int(r.headcount), click_rate=round(r.click_rate, 1), report_rate=round(r.report_rate, 1),
                          sim_pass=round(float(sim_dept.get(d, 0)), 1), training=round(float(dept_tr.get(d, 0)), 1), creds=int(r.creds)))
    score.sort(key=lambda x: -x["click_rate"])
    return dict(
        kpis=kpis,
        simulation=dict(labels=month_labels(months), click=pct("clicked"), report=pct("reported")),
        courses=dict(labels=[c[1] for c in courses], values=[round(done(c[0]), 1) for c in courses]),
        training_by_dept=top_dict(dept_tr.to_dict()),
        click_vs_report=dict(labels=list(order.index), click=[round(v, 1) for v in order.click_rate], report=[round(v, 1) for v in order.report_rate]),
        false_positive=dict(labels=month_labels(months), values=fp_month),
        templates=dict(labels=list(tpl.index), values=[float(v) for v in tpl.values]),
        scorecard=score,
    )
