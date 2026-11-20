import React from 'react'
import Page from '../components/Page'
import Card, { Grid, Section } from '../components/Card'
import { BarChart, LineChart } from '../components/Charts'
import Heatmap from '../components/Heatmap'

export default function Trends() {
  return (
    <Page endpoint="trends">{(d) => (
      <>
        <Section>Volume over time</Section>
        <Grid>
          <Card span={6} title="Phishing Emails by Month">
            <BarChart labels={d.monthly.labels} datasets={[{ label: 'Phishing emails', data: d.monthly.values }]} />
          </Card>
          <Card span={6} title="Phishing Emails by Week">
            <LineChart maxTicks={10} labels={d.weekly.labels} datasets={[{ label: 'Phishing emails', data: d.weekly.values, fill: 'rgba(15,165,192,.14)' }]} />
          </Card>
        </Grid>
        <Grid>
          <Card span={12} title="Phishing Attack Trend — daily volume with 7-day average">
            <LineChart h="t" maxTicks={14} labels={d.daily.labels} datasets={[
              { label: 'Daily emails', data: d.daily.values, color: 'rgba(15,165,192,.55)', width: 1.2 },
              { label: '7-day average', data: d.daily.average, color: '#e0509a', width: 2.4 },
            ]} />
          </Card>
        </Grid>
        <Section>Incidents &amp; timing</Section>
        <Grid>
          <Card span={6} title="Phishing Incidents Over Time" note="Weekly incidents opened">
            <LineChart maxTicks={10} labels={d.incidents_weekly.labels} datasets={[{ label: 'Incidents opened', data: d.incidents_weekly.values, color: '#8b7cf6', fill: 'rgba(139,124,246,.14)' }]} />
          </Card>
          <Card span={6} title="Phishing Emails by Day of the Week">
            <BarChart labels={d.dow.labels} datasets={[{ label: 'Phishing emails', data: d.dow.values }]} />
          </Card>
        </Grid>
        <Grid>
          <Card span={6} title="Phishing Emails by Hour of the Day">
            <BarChart labels={d.hour.labels} datasets={[{ label: 'Phishing emails', data: d.hour.values }]} />
          </Card>
          <Card span={6} title="When Attacks Land — Day × Hour" note="Darker = more emails"><Heatmap {...d.heatmap} /></Card>
        </Grid>
      </>
    )}</Page>
  )
}
