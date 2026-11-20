import React, { useEffect, useState } from 'react'

export const PAGES = [
  { id: 'exec', label: 'Executive Overview', icon: '◈', sub: 'Overall phishing KPIs and security performance' },
  { id: 'trends', label: 'Phishing Trends', icon: '≋', sub: 'Monthly, weekly and daily phishing patterns' },
  { id: 'threat', label: 'Threat Analysis', icon: '⌖', sub: 'Attack types, malicious domains, URLs and severity' },
  { id: 'users', label: 'User & Department', icon: '☷', sub: 'Employee interactions and department risk' },
  { id: 'inc', label: 'Incident Management', icon: '⚑', sub: 'Open incidents, resolution status and response time' },
  { id: 'aware', label: 'Security Awareness', icon: '✦', sub: 'Employee reporting, click rates and training performance' },
]

export default function Sidebar({ page, onNavigate }) {
  const [clock, setClock] = useState('')
  useEffect(() => {
    const tick = () => setClock(new Date().toISOString().slice(0, 19).replace('T', ' ') + ' UTC')
    tick(); const t = setInterval(tick, 1000); return () => clearInterval(t)
  }, [])
  return (
    <aside className="side" aria-label="Dashboard navigation">
      <div className="brand">
        <div className="logo">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#22d3ee" strokeWidth="1.8" strokeLinejoin="round">
            <path d="M12 2.5 4 5.5v6c0 5 3.4 8.6 8 10 4.6-1.4 8-5 8-10v-6z" /><path d="m8.5 12 2.6 2.6 4.6-5" strokeLinecap="round" />
          </svg>
        </div>
        <div><b>PHISHGUARD</b><small>SOC // EMAIL THREATS</small></div>
      </div>
      {PAGES.map((p, i) => (
        <button key={p.id} className={`nav ${page === p.id ? 'on' : ''}`} onClick={() => onNavigate(p.id)}>
          <i>{p.icon}</i>{p.label}<kbd>{i + 1}</kbd>
        </button>
      ))}
      <div className="sidefoot"><div className="live"><span className="dot" />LIVE FEED</div>{clock}<br />Sample data · design preview</div>
    </aside>
  )
}
