import {
  Chart, CategoryScale, LinearScale, BarElement, LineElement, PointElement, ArcElement, Tooltip, Legend, Filler,
} from 'chart.js'

Chart.register(CategoryScale, LinearScale, BarElement, LineElement, PointElement, ArcElement, Tooltip, Legend, Filler)

Chart.defaults.color = '#8fa3bf'
Chart.defaults.font.family = 'Inter, "Segoe UI", system-ui, sans-serif'
Chart.defaults.font.size = 11.5
Chart.defaults.borderColor = 'rgba(143,163,191,.1)'
Chart.defaults.maintainAspectRatio = false
Chart.defaults.responsive = true
Object.assign(Chart.defaults.plugins.tooltip, {
  backgroundColor: '#0a1120', borderColor: 'rgba(34,211,238,.45)', borderWidth: 1, titleColor: '#e6f1ff',
  bodyColor: '#cfe0f5', padding: 10, cornerRadius: 8, boxPadding: 4,
})
Object.assign(Chart.defaults.plugins.legend.labels, { usePointStyle: true, boxWidth: 8, boxHeight: 8 })
Chart.defaults.plugins.legend.position = 'bottom'
