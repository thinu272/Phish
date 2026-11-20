import React from 'react'
import Page from '../components/Page'
import Card, { Grid, Section } from '../components/Card'
import { KpiRow } from '../components/KpiCard'
import { BarChart, LineChart } from '../components/Charts'
import DataTable from '../components/DataTable'
import { OK } from '../theme'

const pct = (v) => v.toFixed(1) + '%'

export default function Awareness() {
  return (
    <Page endpoint="awareness">{(d) => (
      <>
        <Section>Awareness KPIs</Section>
        <KpiRow kpis={d.kpis} />
        <Grid>
          <Card span={6} title="Phishing Simulation — Click vs Report Rate by Month">
            <LineChart unit="%" labels={d.simulation.labels} datasets={[
              { label: 'Click rate', data: d.simulation.click, color: '#e06a30', points: 4 },
              { label: 'Report rate', data: d.simulation.report, color: '#1fae7a', points: 4 },
            ]} />
          </Card>
          <Card span={6} title="Security Awareness Training Completion by Course">
            <BarChart horizontal unit="%" max={100} labels={d.courses.labels} datasets={[{ label: 'Completed', data: d.courses.values, color: OK }]} />
          </Card>
        </Grid>
        <Grid>
          <Card span={6} title="Click Rate vs Reporting Rate by Department" note="Live phishing, % of delivered emails">
            <BarChart h="t" horizontal unit="%" labels={d.click_vs_report.labels} datasets={[
              { label: 'Click rate', data: d.click_vs_report.click, color: '#e06a30' },
              { label: 'Reporting rate', data: d.click_vs_report.report, color: '#1fae7a' },
            ]} />
          </Card>
          <Card span={6} title="Training Completion by Department" note="All assigned courses">
            <BarChart h="t" horizontal unit="%" max={100} labels={d.training_by_dept.labels} datasets={[{ label: 'Completion', data: d.training_by_dept.values, color: OK }]} />
          </Card>
        </Grid>
        <Grid>
          <Card span={6} title="False Positive Detection Rate by Month" note="Legitimate emails wrongly flagged ÷ all flagged">
            <LineChart unit="%" labels={d.false_positive.labels} datasets={[{ label: 'False positive rate', data: d.false_positive.values, color: '#e0509a', points: 4, fill: 'rgba(224,80,154,.1)' }]} />
          </Card>
          <Card span={6} title="Simulation Click Rate by Template">
            <BarChart horizontal unit="%" labels={d.templates.labels} datasets={[{ label: 'Click rate', data: d.templates.values, color: '#e06a30' }]} />
          </Card>
        </Grid>
        <Grid>
          <Card span={12} title="Department Security Awareness Scorecard">
            <DataTable rows={d.scorecard} columns={[
              { label: 'Department', key: 'department' }, { label: 'Staff', num: true, key: 'staff' },
              { label: 'Click rate', num: true, render: (r) => pct(r.click_rate) }, { label: 'Reporting rate', num: true, render: (r) => pct(r.report_rate) },
              { label: 'Simulation pass', num: true, render: (r) => pct(r.sim_pass) }, { label: 'Training done', num: true, render: (r) => pct(r.training) },
              { label: 'Credentials given', num: true, key: 'creds' },
            ]} />
          </Card>
        </Grid>
      </>
    )}</Page>
  )
}
