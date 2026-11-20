import React from 'react'
import { nf } from '../theme'

const COLORS = ['#4a8cf0', '#0fa5c0', '#3ddc97', '#f2c14e', '#8b7cf6', '#e06a30', '#ff4d6d']

export default function Funnel({ steps }) {
  const mx = Math.max(steps[0]?.value || 1, 1)
  return (
    <div className="fun">
      {steps.map((s, i) => (
        <div className="r" key={s.label}>
          <span>{s.label}</span>
          <div className="tr"><div className="fi" style={{ width: `${Math.max((s.value / mx) * 100, 0.8)}%`, background: COLORS[i % COLORS.length] }} /></div>
          <b>{nf(s.value)}</b>
        </div>
      ))}
    </div>
  )
}
