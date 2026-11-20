// Chart palette (validated for colour-blind separation on the dark surface).
export const PAL = ['#0fa5c0', '#8b7cf6', '#1fae7a', '#bb860a', '#e0509a', '#4a8cf0', '#e06a30']
export const SEVC = { Low: '#3ddc97', Medium: '#f2c14e', High: '#ff8a3d', Critical: '#ff4d6d' }
export const OK = '#3ddc97'
export const WARN = '#f2c14e'
export const BAD = '#ff4d6d'
export const CY = '#22d3ee'
export const STATUS_COLORS = [WARN, '#4a8cf0', BAD, OK] // Open, In Progress, Escalated, Resolved

export const nf = (n) => Math.round(n).toLocaleString('en-US')
export const fmt = {
  int: nf,
  pct: (n) => n.toFixed(1) + '%',
  hours: (n) => n.toFixed(1) + ' h',
  minutes: (m) => (m >= 90 ? `${Math.floor(m / 60)}h ${String(Math.round(m % 60)).padStart(2, '0')}m` : `${Math.round(m)} min`),
}
