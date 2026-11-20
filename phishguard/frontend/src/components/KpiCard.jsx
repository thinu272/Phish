import React from 'react'
import { fmt } from '../theme'

function Spark({ values, color }) {
  if (!values || values.length < 2) return null
  const w = 60, h = 28
  const mx = Math.max(...values, 1e-9), mn = Math.min(...values, 0)
  const pts = values.map((v, i) => [(i / (values.length - 1)) * w, h - 3 - ((v - mn) / (mx - mn || 1)) * (h - 8)])
  const last = pts[pts.length - 1]
  return (
    <svg width={w} height={h} viewBox={`0 0 ${w} ${h}`} aria-hidden="true">
      <polyline points={pts.map((p) => p.map((x) => x.toFixed(1)).join(',')).join(' ')} fill="none" stroke={color}
        strokeWidth="1.8" strokeLinejoin="round" strokeLinecap="round" />
      <circle cx={last[0]} cy={last[1]} r="2.6" fill={color} />
    </svg>
  )
}

export function KpiCard({ kpi }) {
  const d = kpi.delta
  return (
    <div className="kpi" style={{ '--ac': kpi.color }}>
      <div className="l">{kpi.label}</div>
      <Spark values={kpi.spark} color={kpi.color} />
      <div className="v">{fmt[kpi.fmt](kpi.value)}</div>
      <div className="n">
        {d && <span className={`d ${d.tone}`}>{d.value > 0 ? '▲' : d.value < 0 ? '▼' : '■'} {Math.abs(d.value).toFixed(1)}{d.unit === 'pp' ? ' pp' : '%'}</span>}
        {kpi.note}
      </div>
    </div>
  )
}

export const KpiRow = ({ kpis }) => <div className="kpis">{kpis.map((k) => <KpiCard key={k.label} kpi={k} />)}</div>
