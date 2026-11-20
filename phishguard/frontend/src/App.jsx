import React, { useEffect, useState } from 'react'
import { FilterProvider, useFilters } from './FilterContext'
import { useApi } from './api'
import Sidebar, { PAGES } from './components/Sidebar'
import FilterBar from './components/FilterBar'
import Executive from './pages/Executive'
import Trends from './pages/Trends'
import Threats from './pages/Threats'
import Users from './pages/Users'
import Incidents from './pages/Incidents'
import Awareness from './pages/Awareness'

const VIEWS = { exec: Executive, trends: Trends, threat: Threats, users: Users, inc: Incidents, aware: Awareness }
const LEVEL_COLOR = { ELEVATED: '#ff4d6d', GUARDED: '#f2c14e', STABLE: '#3ddc97' }

function Shell() {
  const initial = PAGES.some((p) => p.id === location.hash.slice(1)) ? location.hash.slice(1) : 'exec'
  const [page, setPage] = useState(initial)
  const { filters } = useFilters()
  const { data: summary } = useApi('summary', filters)

  const go = (id) => { setPage(id); history.replaceState(null, '', '#' + id); window.scrollTo({ top: 0 }) }
  useEffect(() => {
    const onKey = (e) => {
      if (/INPUT|SELECT|TEXTAREA/.test(e.target.tagName) || e.ctrlKey || e.metaKey) return
      const i = '123456'.indexOf(e.key)
      if (i >= 0) go(PAGES[i].id)
    }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [])

  const meta = PAGES.find((p) => p.id === page)
  const View = VIEWS[page]
  const lc = summary ? LEVEL_COLOR[summary.threat_level] : '#8fa3bf'
  return (
    <div className="app">
      <Sidebar page={page} onNavigate={go} />
      <main>
        <div className="top">
          <div className="titlerow">
            <h1>{meta.label === 'User & Department' ? 'User & Department Analysis' : meta.label}</h1>
            <span className="sub">{'// ' + meta.sub}</span>
            {summary && <div className="threat" style={{ color: lc, borderColor: lc + '88', background: lc + '18' }}>● THREAT LEVEL: {summary.threat_level}</div>}
          </div>
          <FilterBar summary={summary} />
        </div>
        <section className="page on"><View /></section>
        <div className="foot">Synthetic dataset · all figures respond to the slicers above</div>
      </main>
    </div>
  )
}

export default function App() {
  return <FilterProvider><Shell /></FilterProvider>
}
