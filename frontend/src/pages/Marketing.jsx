import { useState, useEffect } from 'react';
import Header from '../components/Header';
import ChartCard from '../components/ChartCard';
import DataTable from '../components/DataTable';
import { getCampaigns, getChannels } from '../api';
import { fmt, fmtPct, fmtNum } from '../utils';

export default function Marketing() {
  const [campaigns, setCampaigns] = useState(null);
  const [channels, setChannels] = useState(null);

  useEffect(() => {
    getCampaigns().then(r => setCampaigns(r.data)).catch(() => {});
    getChannels().then(r => setChannels(r.data)).catch(() => {});
  }, []);

  const channelChart = channels ? {
    labels: channels.map(c => c.channel),
    datasets: [{ data: channels.map(c => c.total_spend || c.spend) }],
  } : null;

  const convChart = channels ? {
    labels: channels.map(c => c.channel),
    datasets: [{ label: 'Conversion Rate %', data: channels.map(c => c.conversion_rate_pct || c.conversionRate || c.conversions) }],
  } : null;

  return (
    <>
      <Header title="📢 Marketing Analytics" />
      <div className="page-content">
        <div className="page-header">
          <h2>Marketing Analytics</h2>
          <p>Campaign performance, channel analysis, and ROI tracking</p>
        </div>
        <div className="charts-grid">
          <ChartCard title="📢 Channel Spend Distribution" type="doughnut" data={channelChart} />
          <ChartCard title="📊 Channel Conversion Rate" type="bar" data={convChart} />
        </div>
        <DataTable
          title="📋 Campaign Details"
          columns={[
            { header: 'Campaign', key: 'campaign_name' },
            { header: 'Duration', key: 'duration_days', render: v => `${v} days` },
            { header: 'Budget', key: 'budget', render: v => fmt(v) },
            { header: 'Spend', key: 'actual_spend', render: v => fmt(v) },
            { header: 'Clicks', key: 'total_clicks', render: v => fmtNum(v) },
            { header: 'Conv %', key: 'conversion_rate_pct', render: v => fmtPct(v) },
          ]}
          rows={campaigns}
        />
      </div>
    </>
  );
}
