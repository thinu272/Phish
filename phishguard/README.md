# PhishGuard SOC Dashboard — React + Python (FastAPI)

A cyber-security phishing dashboard with **6 pages, 8 KPI cards, ~45 charts/tables and 7 slicers**.

* **Backend** – Python, FastAPI + pandas. Reads CSV tables, applies the slicers and returns ready-to-plot JSON.
* **Frontend** – React 18 + Vite + Chart.js (react-chartjs-2). Pure presentation: every number comes from the API.
* **Data** – a synthetic dataset (12,000 phishing emails, 1,196 incidents, 620 users, simulations, training…) that is generated automatically the first time the backend starts. You can swap in your own data (see section 8).

```
phishguard/
├── README.md
├── backend/
│   ├── requirements.txt
│   ├── generate_data.py        # synthetic dataset generator  ->  backend/data/*.csv
│   ├── data/                   # 9 CSV tables (auto-created if missing)
│   └── app/
│       ├── main.py             # FastAPI app, routes, serves the built React app
│       ├── store.py            # loads CSVs once, adds helper columns
│       ├── filters.py          # slicer query-params  ->  Filters object
│       └── analytics.py        # ALL dashboard maths (one function per page)
└── frontend/
    ├── package.json  vite.config.js  index.html
    └── src/
        ├── main.jsx  App.jsx           # layout, navigation, keyboard shortcuts 1-6
        ├── api.js                      # useApi() hook (fetch + slicers)
        ├── FilterContext.jsx           # global slicer state
        ├── chartSetup.js  theme.js     # Chart.js defaults, palette, number formats
        ├── styles.css                  # cyber-security dark theme
        ├── components/                 # Card, Charts (Bar/Line/Donut/Gauge), KpiCard,
        │                               # DataTable, Funnel, Heatmap, FilterBar, Sidebar, Page
        └── pages/                      # Executive, Trends, Threats, Users, Incidents, Awareness
```

---

## 1. Prerequisites

| Tool | Version | Check |
|---|---|---|
| Python | 3.10 or newer | `python --version` |
| Node.js | 18 or newer (includes npm) | `node --version` |

## 2. Quick start — development mode (two terminals)

**Terminal 1 – backend (API on port 8000)**

```bash
cd phishguard/backend
python -m venv .venv

# activate the virtual environment
source .venv/bin/activate          # macOS / Linux
.venv\Scripts\activate             # Windows (PowerShell / cmd)

pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

First start prints `CSV data not found - generating it now ...` (takes ~10 s) and creates `backend/data/*.csv`.
Check it: open <http://localhost:8000/api/health> → `{"status":"ok","emails":12000,...}`.
Interactive API docs: <http://localhost:8000/docs>.

**Terminal 2 – frontend (React dev server on port 5173)**

```bash
cd phishguard/frontend
npm install
npm run dev
```

Open <http://localhost:5173>. Vite proxies every `/api/...` request to the backend (see `vite.config.js`), and edits to the React code hot-reload instantly.

## 3. Production mode (one server, one port)

```bash
cd phishguard/frontend
npm install
npm run build                      # creates frontend/dist

cd ../backend
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

If `frontend/dist` exists, FastAPI serves the React app **and** the API from <http://localhost:8000>.
Remove `--reload` in production; put it behind nginx / a cloud service if you need HTTPS.

## 4. Using the dashboard

* **Pages** – click the sidebar buttons or press keys **1–6**: Executive Overview, Phishing Trends, Threat Analysis, User & Department, Incident Management, Security Awareness.
* **Slicers** (top bar, apply to every page): date range (7D / 30D / 90D / YTD or From–To), department, attack type, severity, incident status, country, email domain. **Reset** clears them. The line under the slicers shows the active scope and the number of matching emails / incidents.
* **KPI cards** – value, change vs. the previous period of the same length (green = good, red = bad) and a monthly sparkline.
* **Threat level badge** – ELEVATED (≥2 open critical incidents), GUARDED (≥10 active incidents), otherwise STABLE.
* Hover any chart for a tooltip; hover heat-map cells for exact counts.

How the slicers behave (identical to the original HTML mock-up):

| Slicer | Emails | Incidents | Simulations | Training | Filter stats (false positives) |
|---|---|---|---|---|---|
| Date range | received date | created date | send date | – | date |
| Department | ✔ | ✔ | ✔ | ✔ | – |
| Attack type / Country / Domain | ✔ | ✔ (via the email) | – | – | – |
| Severity | email severity | incident severity | – | – | – |
| Incident status | emails whose incident has this status | ✔ | – | – | – |

## 5. API reference

All endpoints are `GET`, return JSON, and accept the same optional slicer parameters:

`from=YYYY-MM-DD  to=YYYY-MM-DD  department=  attack_type=  severity=  status=  country=  domain=`

| Endpoint | Powers | Main fields in the response |
|---|---|---|
| `/api/meta` | slicer drop-downs | `min_date, max_date, departments, attack_types, severities, statuses, countries, domains` |
| `/api/summary` | header badge / scope line | `emails, incidents, active, critical_open, threat_level` |
| `/api/executive` | page 1 | `kpis, monthly, gauge, severity, funnel, departments, incidents` |
| `/api/trends` | page 2 | `monthly, weekly, daily(+average), incidents_weekly, dow, hour, heatmap` |
| `/api/threats` | page 3 | `attack_type, severity, category, domains, subjects, attachments, countries, providers, urls, campaigns` |
| `/api/users` | page 4 | `*_by_dept, top_targeted, high_risk, clickers, credential_submitters, reporters, repeat_targets` |
| `/api/incidents` | page 5 | `kpis, status, investigation, team, opened_vs_resolved, resolution_trend, severity, open_incidents` |
| `/api/awareness` | page 6 | `kpis, simulation, courses, training_by_dept, click_vs_report, false_positive, templates, scorecard` |

Example: `curl "http://localhost:8000/api/executive?from=2026-08-01&department=Finance&severity=High"`

## 6. Where each requirement lives

| Dashboard item | Backend (`analytics.py`) | Frontend |
|---|---|---|
| 8 KPI cards | `KPI` dict, `build_kpis()`, `metrics()` | `components/KpiCard.jsx`, `pages/Executive.jsx` |
| Trends (month / week / day / hour / weekday) | `trends()` | `pages/Trends.jsx`, `components/Heatmap.jsx` |
| Attack categories, domains, URLs, campaigns | `threats()` | `pages/Threats.jsx` |
| Users & departments, high-risk, repeat targets | `users()`, `_dept_stats()` | `pages/Users.jsx` |
| Incident management, SLA | `incidents()` | `pages/Incidents.jsx` |
| Security awareness, simulations, training, false positives | `awareness()` | `pages/Awareness.jsx` |
| Slicers | `filters.py`, `sel_*()` functions | `components/FilterBar.jsx`, `FilterContext.jsx` |

KPI formulas (all in `metrics()`): detection rate = detected ÷ total; click rate = clicked ÷ delivered; reporting rate = reported ÷ delivered; active incidents = status ≠ Resolved; average response time = mean `response_time_minutes`; average time to resolve = mean `resolution_time_hours` of resolved incidents; SLA breach rate = share of incidents with `sla_breached = 1`; department risk index = (clicks + 3 × credential submissions) ÷ headcount × 100.

## 7. Customising

* **Regenerate data** – `cd backend && python generate_data.py [seed] [n_emails]` (e.g. `python generate_data.py 7 30000`), then restart the backend. Delete `backend/data/` to force regeneration on next start.
* **Colours / theme** – `frontend/src/theme.js` (chart palette, severity colours) and the `:root` variables at the top of `frontend/src/styles.css`.
* **Add a chart** – 1) compute it in the matching function in `analytics.py` and return it as `{labels:[...], values:[...]}`; 2) add `<Card><BarChart .../></Card>` to the page in `frontend/src/pages/`.
* **Add a KPI** – add an entry to `KPI` in `analytics.py`, put its name in the page's `build_kpis(...)` list. The card, change badge and sparkline are automatic.
* **Add a page** – new function in `analytics.py`, register it in the route list in `main.py`, create `pages/NewPage.jsx` (copy an existing page, change the `endpoint`), and add it to `VIEWS` in `App.jsx` and `PAGES` in `components/Sidebar.jsx`.
* **Change "today"** – the dashboard treats the latest email date as today (`Store.now` in `store.py`).

## 8. Using your own (real) data

Replace the CSVs in `backend/data/` with exports from your mail-security / SIEM / ticketing tools using the same file and column names, or edit `store.py` to read from a database (`pd.read_sql`). The columns the code uses:

* `fact_phishing_emails.csv` – `email_id, received_datetime, received_date, week_start_date, day_of_week_num (1=Mon), hour_of_day, campaign_id, sender_domain, sender_domain_type, email_provider, sender_country, subject, attack_type, threat_category, severity (Low|Medium|High|Critical), attachment_type, malicious_url, target_user_id, department, is_detected, is_blocked, is_delivered, is_missed, clicked, submitted_credentials, reported_by_user (all 0/1), incident_id`
* `fact_incidents.csv` – `incident_id, email_id, created_datetime, created_date, resolved_datetime, resolved_date, severity, attack_type, department, assigned_team, status (Open|In Progress|Escalated|Resolved), investigation_status, response_time_minutes, resolution_time_hours, is_overdue, sla_breached`
* `dim_user.csv` – `user_id, full_name, department, seniority` · `dim_department.csv` – `department_name, headcount` · `dim_campaign.csv` – `campaign_id, campaign_name, primary_attack_type`
* `fact_simulations.csv` – `send_date, user_id, department, template_type, clicked, reported, passed`
* `fact_training.csv` – `course_id, course_name, user_id, department, status (Completed|In Progress|Not Started|Overdue)`
* `fact_filter_daily.csv` – `date, false_positives, total_flagged`

Dates must be ISO (`2026-11-18` or `2026-11-18 14:30:00`). The pandas code handles tens of thousands of rows instantly; for millions of rows, pre-aggregate in your database or cache results.

## 9. Troubleshooting

| Symptom | Fix |
|---|---|
| Page shows "Could not load /api/… Is the backend running?" | Start the backend (step 2, terminal 1). In dev mode it must listen on **port 8000**. |
| `ModuleNotFoundError: fastapi` | Activate the virtual environment, then `pip install -r requirements.txt`. |
| Run `uvicorn` and get `Could not import module "app.main"` | You must run it **from the `backend` folder**. |
| Port already in use | Use another port: `uvicorn app.main:app --port 8001` and change the proxy target in `vite.config.js`. |
| Blank white page after `npm run build` | Open the site from the backend URL (`:8000`), not by double-clicking `dist/index.html`. |
| Want different numbers | `python generate_data.py <new-seed>` then restart the backend. |
