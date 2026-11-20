import React from 'react'
import Page from '../components/Page'
import Card, { Grid, Section } from '../components/Card'
import { KpiRow } from '../components/KpiCard'
import { BarChart, LineChart, DonutChart } from '../components/Charts'
import DataTable, { SevBadge, StatusBadge, Overdue } from '../components/DataTable'
import { SEVC, STATUS_COLORS, OK, PAL } from '../theme'

export default function Incidents() {
  return (
    <Page endpoint="incidents">{(d) => {
      const sevColors = d.severity.labels.map((l) => SEVC[l])
      return (
        <>
          <Section>Incident KPIs</Section>
          <KpiRow kpis={d.kpis} />
          <Grid>
            <Card span={4} title="Incidents by Status"><DonutChart labels={d.status.labels} values={d.status.values} colors={STATUS_COLORS} /></Card>
            <Card span={4} title="Incidents by Investigation Status"><BarChart h="s" horizontal labels={d.investigation.labels} datasets={[{ label: 'Incidents', data: d.investigation.values }]} /></Card>
            <Card span={4} title="Incidents by Assigned Security Team"><BarChart h="s" horizontal labels={d.team.labels} datasets={[{ label: 'Incidents', data: d.team.values, color: '#8b7cf6' }]} /></Card>
          </Grid>
          <Grid>
            <Card span={6} title="Incidents Opened vs Resolved by Month">
              <BarChart labels={d.opened_vs_resolved.labels} datasets={[
                { label: 'Opened', data: d.opened_vs_resolved.opened, color: PAL[0] },
                { label: 'Resolved', data: d.opened_vs_resolved.resolved, color: OK },
              ]} />
            </Card>
            <Card span={6} title="Incident Resolution Trend — avg hours to resolve">
              <LineChart unit=" h" labels={d.resolution_trend.labels} datasets={[{ label: 'Avg hours to resolve', data: d.resolution_trend.values, color: '#8b7cf6', points: 4, fill: 'rgba(139,124,246,.12)' }]} />
            </Card>
          </Grid>
          <Grid>
            <Card span={4} title="Incidents by Severity"><BarChart h="s" horizontal labels={d.severity.labels} datasets={[{ label: 'Incidents', data: d.severity.count, color: sevColors }]} /></Card>
            <Card span={4} title="Avg Response Time by Severity" note="Minutes to first analyst response">
              <BarChart h="s" horizontal unit=" min" labels={d.severity.labels} datasets={[{ label: 'Avg response', data: d.severity.response, color: sevColors }]} />
            </Card>
            <Card span={4} title="SLA Breach Rate by Severity">
              <BarChart h="s" horizontal unit="%" max={100} labels={d.severity.labels} datasets={[{ label: 'SLA breach', data: d.severity.breach, color: sevColors }]} />
            </Card>
          </Grid>
          <Grid>
            <Card span={12} title="Open Phishing Incidents" note="Open, In Progress and Escalated · oldest first">
              <DataTable rows={d.open_incidents} columns={[
                { label: 'Incident', key: 'incident_id' },
                { label: 'Severity', render: (r) => <SevBadge s={r.severity} /> },
                { label: 'Attack type', key: 'attack_type' },
                { label: 'Department', key: 'department' },
                { label: 'Analyst team', key: 'team' },
                { label: 'Investigation', render: (r) => <StatusBadge>{r.investigation}</StatusBadge> },
                { label: 'Age', render: (r) => `${r.age_days}d` },
                { label: 'SLA', render: (r) => (r.overdue ? <Overdue /> : <span style={{ color: 'var(--grn)' }}>On track</span>) },
              ]} />
            </Card>
          </Grid>
        </>
      )
    }}</Page>
  )
}
