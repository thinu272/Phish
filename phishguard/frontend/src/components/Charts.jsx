import React, { useMemo } from 'react'
import { Bar, Line, Doughnut } from 'react-chartjs-2'
import { PAL, nf } from '../theme'

/** `h` is the plot height: 's' (210px) | '' (250px) | 't' (320px). */
const Box = ({ h = '', children }) => <div className={`cv ${h}`}>{children}</div>

const grid = { color: 'rgba(143,163,191,.08)', drawTicks: false }
const noGrid = { display: false }

const valueText = (v, unit) => (unit === '%' || unit === ' h' || unit === ' min' ? Number(v).toFixed(1) : nf(v)) + unit

/**
 * datasets: [{ label, data, color }]  (color may be an array for per-bar colours)
 * horizontal: ranked bars, stacked: stacked columns, unit: '%', ' h' ...
 */
export function BarChart({ labels, datasets, horizontal = false, stacked = false, unit = '', max, h }) {
  const data = useMemo(() => ({
    labels,
    datasets: datasets.map((d, i) => ({
      label: d.label, data: d.data, backgroundColor: d.color || PAL[i % PAL.length],
      borderRadius: stacked ? 2 : 4, borderSkipped: false, maxBarThickness: horizontal ? 20 : 34,
      stack: stacked ? 'a' : undefined, categoryPercentage: 0.8, barPercentage: 0.82,
      borderColor: '#0d1424', borderWidth: stacked ? 1 : 0,
    })),
  }), [labels, datasets, horizontal, stacked])

  const options = useMemo(() => {
    const rotate = !horizontal && labels.length <= 14 && (labels.length > 6 || labels.some((l) => String(l).length > 7))
    const valueTicks = unit ? { callback: (v) => v + unit } : {}
    const catTicks = horizontal
      ? { callback(v) { const l = String(this.getLabelForValue(v)); return l.length > 24 ? l.slice(0, 23) + '…' : l } }
      : rotate ? { maxRotation: 40, minRotation: 40, autoSkip: false }
        : labels.length <= 14 ? { maxRotation: 0, autoSkip: false } : { maxRotation: 0, autoSkip: true }
    const cat = { stacked, grid: horizontal ? noGrid : noGrid, ticks: catTicks, border: { display: false } }
    const val = { stacked, beginAtZero: true, grid, border: { display: false }, ticks: valueTicks, max }
    return {
      indexAxis: horizontal ? 'y' : 'x',
      plugins: {
        legend: { display: datasets.length > 1 },
        tooltip: {
          mode: stacked ? 'index' : 'nearest', intersect: false,
          callbacks: { label: (c) => ` ${c.dataset.label}: ${valueText(horizontal ? c.parsed.x : c.parsed.y, unit)}` },
        },
      },
      scales: horizontal ? { x: { ...val, grid }, y: cat } : { x: cat, y: val },
    }
  }, [labels, datasets, horizontal, stacked, unit, max])

  return <Box h={h}><Bar data={data} options={options} /></Box>
}

/** datasets: [{ label, data, color, fill, width, points }] */
export function LineChart({ labels, datasets, unit = '', maxTicks = 12, h }) {
  const data = useMemo(() => ({
    labels,
    datasets: datasets.map((d, i) => {
      const c = d.color || PAL[i % PAL.length]
      return {
        label: d.label, data: d.data, borderColor: c, backgroundColor: d.fill || 'transparent', fill: !!d.fill,
        borderWidth: d.width || 2, pointRadius: d.points ?? 0, pointHoverRadius: 5, pointBackgroundColor: c,
        pointBorderColor: '#0d1424', pointBorderWidth: 2, tension: 0.3,
      }
    }),
  }), [labels, datasets])
  const options = useMemo(() => ({
    interaction: { mode: 'index', intersect: false },
    plugins: {
      legend: { display: datasets.length > 1 },
      tooltip: { callbacks: { label: (c) => ` ${c.dataset.label}: ${valueText(c.parsed.y, unit)}` } },
    },
    scales: {
      x: { grid: noGrid, ticks: { maxRotation: 0, autoSkip: true, maxTicksLimit: maxTicks }, border: { display: false } },
      y: { beginAtZero: true, grid, border: { display: false }, ticks: unit ? { callback: (v) => v + unit } : {} },
    },
  }), [datasets.length, unit, maxTicks])
  return <Box h={h}><Line data={data} options={options} /></Box>
}

export function DonutChart({ labels, values, colors = PAL, legend = 'right', h = 's' }) {
  const data = useMemo(() => ({
    labels, datasets: [{ data: values, backgroundColor: colors, borderColor: '#0d1424', borderWidth: 3, hoverOffset: 6 }],
  }), [labels, values, colors])
  const options = useMemo(() => ({
    cutout: '64%',
    plugins: {
      legend: { position: legend, labels: { padding: 12 } },
      tooltip: {
        callbacks: {
          label: (c) => {
            const t = c.dataset.data.reduce((a, b) => a + b, 0)
            return ` ${c.label}: ${nf(c.parsed)} (${t ? ((c.parsed / t) * 100).toFixed(1) : 0}%)`
          },
        },
      },
    },
  }), [legend])
  return <Box h={h}><Doughnut data={data} options={options} /></Box>
}

/** Half-circle detection-rate gauge. */
export function Gauge({ rate, detected, missed, missRate }) {
  const data = { labels: ['Detected', 'Missed'], datasets: [{ data: [detected, missed], backgroundColor: ['#22d3ee', 'rgba(255,77,109,.55)'], borderColor: '#0d1424', borderWidth: 3 }] }
  const options = { rotation: -90, circumference: 180, cutout: '76%', plugins: { legend: { display: false } } }
  return (
    <>
      <div className="gwrap">
        <Doughnut data={data} options={options} />
        <div className="gtxt"><b>{rate.toFixed(1)}%</b><span>detected</span></div>
      </div>
      <div className="gstats">
        <div><b>{nf(detected)}</b>Detected</div>
        <div><b style={{ color: '#ff8fa3' }}>{nf(missed)}</b>Missed</div>
        <div><b>{missRate.toFixed(1)}%</b>Miss rate</div>
      </div>
    </>
  )
}
