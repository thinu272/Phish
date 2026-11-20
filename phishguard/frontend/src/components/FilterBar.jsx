import React, { useEffect, useState } from 'react'
import { useFilters } from '../FilterContext'

const addDays = (iso, n) => new Date(Date.parse(iso) + n * 864e5).toISOString().slice(0, 10)

const Select = ({ id, label, value, onChange, all, options }) => (
  <div className="fg">
    <label htmlFor={id}>{label}</label>
    <select id={id} value={value} onChange={(e) => onChange(e.target.value)}>
      <option value="">{all}</option>
      {options.map((o) => <option key={o} value={o}>{o}</option>)}
    </select>
  </div>
)

export default function FilterBar({ summary }) {
  const { filters: f, set, reset } = useFilters()
  const [meta, setMeta] = useState(null)
  useEffect(() => { fetch('/api/meta').then((r) => r.json()).then(setMeta).catch(() => {}) }, [])
  if (!meta) return <div className="filters" />

  const preset = (label, days) => (
    <button key={label} className={`pill ${f.preset === label ? 'on' : ''}`}
      onClick={() => set(days ? { from: addDays(meta.max_date, -(days - 1)), to: meta.max_date, preset: label } : { from: '', to: '', preset: label })}>
      {label}
    </button>
  )
  return (
    <>
      <div className="filters">
        <div className="fg"><label>Date range</label>
          <div className="pills">{preset('7D', 7)}{preset('30D', 30)}{preset('90D', 90)}{preset('YTD', 0)}</div></div>
        <div className="fg"><label htmlFor="fFrom">From</label>
          <input id="fFrom" type="date" min={meta.min_date} max={meta.max_date} value={f.from || meta.min_date}
            onChange={(e) => set({ from: e.target.value, preset: '' })} /></div>
        <div className="fg"><label htmlFor="fTo">To</label>
          <input id="fTo" type="date" min={meta.min_date} max={meta.max_date} value={f.to || meta.max_date}
            onChange={(e) => set({ to: e.target.value, preset: '' })} /></div>
        <Select id="fDept" label="Department" value={f.department} onChange={(v) => set({ department: v })} all="All departments" options={meta.departments} />
        <Select id="fAtk" label="Attack type" value={f.attack_type} onChange={(v) => set({ attack_type: v })} all="All attack types" options={meta.attack_types} />
        <Select id="fSev" label="Severity" value={f.severity} onChange={(v) => set({ severity: v })} all="All severities" options={meta.severities} />
        <Select id="fStatus" label="Incident status" value={f.status} onChange={(v) => set({ status: v })} all="All statuses" options={meta.statuses} />
        <Select id="fCtry" label="Country" value={f.country} onChange={(v) => set({ country: v })} all="All countries" options={meta.countries} />
        <Select id="fDom" label="Email domain" value={f.domain} onChange={(v) => set({ domain: v })} all="All domains (top 80)" options={meta.domains} />
        <button className="reset" onClick={reset}>↺ Reset</button>
      </div>
      <div className="scope">
        <b>{f.from || meta.min_date}</b> → <b>{f.to || meta.max_date}</b>
        {['department', 'attack_type', 'severity', 'status', 'country', 'domain'].filter((k) => f[k]).map((k) => <span key={k}> · <b>{f[k]}</b></span>)}
        {summary && <> — {summary.emails.toLocaleString()} emails · {summary.incidents.toLocaleString()} incidents</>}
      </div>
    </>
  )
}
