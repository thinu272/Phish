import React from 'react'

export default function Heatmap({ rows, cols, values }) {
  const mx = Math.max(1, ...values.flat())
  return (
    <>
      <div className="heat">
        <div className="h" />
        {cols.map((c) => <div className="h" key={c}>{c % 3 === 0 ? c : ''}</div>)}
        {rows.map((r, d) => (
          <React.Fragment key={r}>
            <div className="rl">{r}</div>
            {values[d].map((v, i) => (
              <div key={i} title={`${r} ${String(i).padStart(2, '0')}:00 — ${v} emails`}
                style={{ background: `rgba(34,211,238,${(0.05 + 0.95 * Math.pow(v / mx, 0.65)).toFixed(3)})` }} />
            ))}
          </React.Fragment>
        ))}
      </div>
      <div className="hleg">low <i /> high</div>
    </>
  )
}
