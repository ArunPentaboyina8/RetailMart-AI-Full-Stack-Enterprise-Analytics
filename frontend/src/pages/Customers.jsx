import { useState, useEffect } from 'react';
import Header from '../components/Header';
import ChartCard from '../components/ChartCard';
import DataTable from '../components/DataTable';
import { getRFMSegments, getCLVTiers, getChurnRisk } from '../api';
import { fmt, fmtNum } from '../utils';

export default function Customers() {
  const [rfm, setRfm] = useState(null);
  const [clv, setClv] = useState(null);
  const [churn, setChurn] = useState(null);

  useEffect(() => {
    getRFMSegments().then(r => setRfm(r.data)).catch(() => {});
    getCLVTiers().then(r => setClv(r.data)).catch(() => {});
    getChurnRisk().then(r => setChurn(r.data)).catch(() => {});
  }, []);

  const rfmChart = rfm ? {
    labels: rfm.map(r => r.rfm_segment || r.segment),
    datasets: [{ label: 'Customers', data: rfm.map(r => r.customer_count || r.customerCount) }],
  } : null;

  const clvChart = clv ? {
    labels: clv.map(c => c.clv_tier || c.tier),
    datasets: [{ data: clv.map(c => c.customer_count || c.customerCount) }],
  } : null;

  return (
    <>
      <Header title="👥 Customer Analytics" />
      <div className="page-content">
        <div className="page-header">
          <h2>Customer Analytics</h2>
          <p>RFM segments, CLV tiers, and churn risk analysis</p>
        </div>
        <div className="charts-grid">
          <ChartCard title="🎯 RFM Segments" type="bar" data={rfmChart} />
          <ChartCard title="💎 CLV Tier Distribution" type="doughnut" data={clvChart} />
        </div>
        <DataTable
          title="🚨 High-Priority Churn Risk Customers"
          columns={[
            { header: 'Customer', key: 'full_name', render: (v, row) => v || row.fullName },
            { header: 'Tier', key: 'clv_tier', render: (v, row) => <span className="badge badge-orange">{v || row.clvTier}</span> },
            { header: 'Total Spent', key: 'total_spent', render: (v, row) => fmt(v || row.totalSpent) },
            { header: 'Inactive Days', key: 'days_inactive', render: (v, row) => fmtNum(v || row.daysInactive || row.avgDaysInactive) },
            { header: 'Risk Level', key: 'churn_risk_level', render: (v, row) => {
              const risk = v || row.churnRiskLevel || row.riskLevel;
              return <span className={`badge ${risk === 'High' ? 'badge-red' : risk === 'Medium' ? 'badge-orange' : 'badge-blue'}`}>{risk}</span>;
            }},
          ]}
          rows={churn}
        />
      </div>
    </>
  );
}
