import React from 'react'
import Page from '../components/Page'
import Card, { Grid, Section } from '../components/Card'
import { BarChart, DonutChart } from '../components/Charts'
import DataTable from '../components/DataTable'
import { SEVC, PAL, nf } from '../theme'

const hbar = (c, label = 'Emails') => ({ labels: c.labels, datasets: [{ label, data: c.values }] })

export default function Threats() {
  return (
    <Page endpoint="threats">{(d) => (
      <>
        <Section>Attack categories</Section>
        <Grid>
          <Card span={6} title="Phishing Emails by Attack Type"><BarChart h="t" horizontal {...hbar(d.attack_type)} /></Card>
          <Card span={3} title="By Severity">
            <DonutChart h="t" legend="bottom" labels={d.severity.labels} values={d.severity.values} colors={d.severity.labels.map((l) => SEVC[l])} />
          </Card>
          <Card span={3} title="By Threat Category"><DonutChart h="t" legend="bottom" labels={d.category.labels} values={d.category.values} colors={PAL} /></Card>
        </Grid>
        <Section>Infrastructure</Section>
        <Grid>
          <Card span={6} title="Top 10 Malicious Sender Domains"><BarChart h="t" horizontal {...hbar(d.domains)} /></Card>
          <Card span={6} title="Top 10 Frequently Reported Subjects" note="Most common phishing email subjects"><BarChart h="t" horizontal {...hbar(d.subjects)} /></Card>
        </Grid>
        <Grid>
          <Card span={4} title="By Attachment Type"><BarChart h="s" {...hbar(d.attachments)} /></Card>
          <Card span={4} title="Phishing Attacks by Country" note="Sender origin"><BarChart h="s" horizontal {...hbar(d.countries)} /></Card>
          <Card span={4} title="By Email Provider"><BarChart h="s" horizontal {...hbar(d.providers)} /></Card>
        </Grid>
        <Grid>
          <Card span={6} title="Phishing Emails by Malicious URL" note="Top 10 URLs (defanged) · clicks show user exposure">
            <DataTable rows={d.urls.map((r, i) => ({ ...r, n: i + 1 }))} columns={[
              { label: '#', key: 'n' }, { label: 'Malicious URL (defanged)', key: 'url' },
              { label: 'Emails', num: true, render: (r) => nf(r.emails) }, { label: 'Clicks', num: true, key: 'clicks' },
            ]} />
          </Card>
          <Card span={6} title="Phishing Campaign Analysis" note="Top campaigns by volume">
            <DataTable rows={d.campaigns} columns={[
              { label: 'Campaign', key: 'name' }, { label: 'Type', render: (r) => <span style={{ color: 'var(--mut)' }}>{r.type}</span> },
              { label: 'Emails', num: true, render: (r) => nf(r.emails) }, { label: 'Detect %', num: true, render: (r) => r.detect_pct.toFixed(1) + '%' },
              { label: 'Clicks', num: true, key: 'clicks' },
            ]} />
          </Card>
        </Grid>
      </>
    )}</Page>
  )
}
