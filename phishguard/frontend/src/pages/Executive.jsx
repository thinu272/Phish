import React from 'react'
import Page from '../components/Page'
import Card, { Grid, Section } from '../components/Card'
import { KpiRow } from '../components/KpiCard'
import { BarChart, DonutChart, Gauge } from '../components/Charts'
import Funnel from '../components/Funnel'
import DataTable, { SevBadge, StatusBadge, Overdue } from '../components/DataTable'
import { SEVC, OK, WARN, BAD } from '../theme'

export default function Executive() {
  return (
    <Page endpoint="executive">{(d) => (
      <>
        <Section>Key performance indicators</Section>
        <KpiRow kpis={d.kpis} />
        <Section>Security performance</Section>
        <Grid>
          <Card span={8} title="Phishing Emails by Month — Security Outcome" note="Blocked vs delivered with warning vs missed (delivered to inbox)">
            <BarChart h="t" stacked labels={d.monthly.labels} datasets={[
              { label: 'Blocked / Quarantined', data: d.monthly.blocked, color: OK },
              { label: 'Delivered with warning', data: d.monthly.warning, color: WARN },
              { label: 'Missed — delivered to inbox', data: d.monthly.missed, color: BAD },
            ]} />
          </Card>
          <Card span={4} title="Detection Rate" note="Share of phishing emails caught by security filters">
            <Gauge rate={d.gauge.rate} detected={d.gauge.detected} missed={d.gauge.missed} missRate={d.gauge.miss_rate} />
          </Card>
        </Grid>
        <Grid>
          <Card span={4} title="Emails by Severity">
            <DonutChart labels={d.severity.labels} values={d.severity.values} colors={d.severity.labels.map((l) => SEVC[l])} />
          </Card>
          <Card span={4} title="Attack Funnel" note="Where phishing emails end up"><Funnel steps={d.funnel} /></Card>
          <Card span={4} title="Most Targeted Departments">
            <BarChart h="s" horizontal labels={d.departments.labels} datasets={[{ label: 'Phishing emails', data: d.departments.values }]} />
          </Card>
        </Grid>
        <Grid>
          <Card span={12} title="Active Critical &amp; High Incidents" note="Needs analyst attention · sorted by severity then age">
            <DataTable rows={d.incidents} columns={[
              { label: 'Incident', key: 'incident_id' },
              { label: 'Severity', render: (r) => <SevBadge s={r.severity} /> },
              { label: 'Attack type', key: 'attack_type' },
              { label: 'Department', key: 'department' },
              { label: 'Team', key: 'team' },
              { label: 'Status', render: (r) => <><StatusBadge>{r.status}</StatusBadge>{r.overdue && <> <Overdue /></>}</> },
              { label: 'Age', render: (r) => `${r.age_days}d` },
            ]} />
          </Card>
        </Grid>
      </>
    )}</Page>
  )
}
