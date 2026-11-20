import React from 'react'
import Page from '../components/Page'
import Card, { Grid, Section } from '../components/Card'
import { BarChart } from '../components/Charts'
import DataTable, { userCell } from '../components/DataTable'

const one = (c, label, color) => ({ labels: c.labels, datasets: [{ label, data: c.values, color }] })
const base = { label: 'User', render: userCell }
const dept = { label: 'Department', key: 'department' }

export default function Users() {
  return (
    <Page endpoint="users">{(d) => (
      <>
        <Section>Departments</Section>
        <Grid>
          <Card span={4} title="Phishing Incidents by Department"><BarChart horizontal {...one(d.incidents_by_dept, 'Incidents')} /></Card>
          <Card span={4} title="Most Targeted Departments"><BarChart horizontal {...one(d.targeted_by_dept, 'Emails')} /></Card>
          <Card span={4} title="High-Risk Departments" note="Risk index = (clicks + 3×credential submissions) per 100 staff">
            <BarChart horizontal {...one(d.risk_by_dept, 'Risk index', '#e06a30')} />
          </Card>
        </Grid>
        <Grid>
          <Card span={6} title="Phishing Click Rate by Department" note="Clicks ÷ emails delivered to inbox"><BarChart unit="%" {...one(d.click_rate_by_dept, 'Click rate', '#e06a30')} /></Card>
          <Card span={6} title="Phishing Reporting Rate by Department" note="Reports ÷ emails delivered to inbox"><BarChart unit="%" {...one(d.report_rate_by_dept, 'Reporting rate', '#1fae7a')} /></Card>
        </Grid>
        <Section>Users</Section>
        <Grid>
          <Card span={6} title="Top 10 Most Targeted Users">
            <DataTable rows={d.top_targeted} columns={[base, dept, { label: 'Level', key: 'level' }, { label: 'Emails', num: true, key: 'emails' }, { label: 'Clicks', num: true, key: 'clicks' }]} />
          </Card>
          <Card span={6} title="High-Risk Users" note="Risk score = clicks×3 + credential submissions×5">
            <DataTable rows={d.high_risk} columns={[base, dept, { label: 'Clicks', num: true, key: 'clicks' }, { label: 'Creds', num: true, key: 'creds' }, { label: 'Risk', num: true, key: 'risk' }]} />
          </Card>
        </Grid>
        <Grid>
          <Card span={6} title="Users Who Clicked Phishing Links" note="Top 10 by clicks">
            <DataTable rows={d.clickers} columns={[base, dept, { label: 'Clicks', num: true, key: 'clicks' }, { label: 'Of emails', num: true, key: 'emails' }]} />
          </Card>
          <Card span={6} title="Users Who Submitted Credentials" note="Top 10 · reset required">
            <DataTable rows={d.credential_submitters} columns={[base, dept, { label: 'Credentials submitted', num: true, key: 'creds' }, { label: 'Level', key: 'level' }]} />
          </Card>
        </Grid>
        <Grid>
          <Card span={6} title="Users Who Reported Phishing Emails" note="Top 10 reporters — security champions">
            <DataTable rows={d.reporters} columns={[base, dept, { label: 'Reports', num: true, key: 'reports' }, { label: 'Of emails', num: true, key: 'emails' }]} />
          </Card>
          <Card span={6} title="Repeat Phishing Targets" note="Users who clicked 2+ times">
            <DataTable rows={d.repeat_targets} columns={[base, dept, { label: 'Clicks', num: true, key: 'clicks' }, { label: 'Campaigns hit', num: true, key: 'campaigns' }]} />
          </Card>
        </Grid>
      </>
    )}</Page>
  )
}
