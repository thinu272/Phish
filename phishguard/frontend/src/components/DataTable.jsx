import React from 'react'

export const SevBadge = ({ s }) => <span className={`b ${s}`}>{s}</span>
export const StatusBadge = ({ children }) => <span className="b st">{children}</span>
export const Overdue = () => <span className="b od">OVERDUE</span>

/**
 * columns: [{ key, label, num?, render?(row) }]   rows: array of objects
 */
export default function DataTable({ columns, rows }) {
  if (!rows || !rows.length) return <div className="empty">No records match the current filters</div>
  return (
    <div className="tw">
      <table>
        <thead><tr>{columns.map((c) => <th key={c.label} className={c.num ? 'num' : ''}>{c.label}</th>)}</tr></thead>
        <tbody>
          {rows.map((r, i) => (
            <tr key={i}>{columns.map((c) => <td key={c.label} className={c.num ? 'num' : ''}>{c.render ? c.render(r) : r[c.key]}</td>)}</tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

export const userCell = (r) => (
  <>{r.name} <span style={{ color: 'var(--dim)', fontFamily: 'var(--mono)', fontSize: 11 }}>{r.user_id}</span></>
)
