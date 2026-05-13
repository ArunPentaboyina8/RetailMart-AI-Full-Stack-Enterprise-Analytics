import { useState, useEffect } from 'react';
import Header from '../components/Header';
import ChartCard from '../components/ChartCard';
import DataTable from '../components/DataTable';
import { getStorePerformance, getRegionalData } from '../api';
import { fmt, fmtPct } from '../utils';

export default function Stores() {
  const [stores, setStores] = useState(null);
  const [regional, setRegional] = useState(null);

  useEffect(() => {
    getStorePerformance(15).then(r => setStores(r.data)).catch(() => {});
    getRegionalData().then(r => setRegional(r.data)).catch(() => {});
  }, []);

  const regionalChart = regional ? {
    labels: regional.map(r => r.region),
    datasets: [{ label: 'Revenue', data: regional.map(r => r.total_revenue || r.revenue) }],
  } : null;

  const storeChart = stores ? {
    labels: stores.slice(0, 10).map(s => s.store_name || s.storeName || `Store ${s.store_id || s.storeId}`),
    datasets: [{ label: 'Revenue', data: stores.slice(0, 10).map(s => s.total_revenue || s.revenue) }],
  } : null;

  return (
    <>
      <Header title="🏪 Store Analytics" />
      <div className="page-content">
        <div className="page-header">
          <h2>Store Analytics</h2>
          <p>Regional performance and store-level scorecards</p>
        </div>
        <div className="charts-grid">
          <ChartCard title="🌍 Regional Performance" type="bar" data={regionalChart} fullWidth />
          <ChartCard title="🏪 Store Rankings" type="bar" data={storeChart} />
        </div>
        <DataTable
          title="📊 Store Scorecard"
          columns={[
            { header: '#', key: '_idx', render: (_, __, i) => i + 1 },
            { header: 'Store', key: 'store_name', render: (v, row) => v || row.storeName },
            { header: 'City', key: 'city' },
            { header: 'Region', key: 'region' },
            { header: 'Revenue', key: 'total_revenue', render: (v, row) => fmt(v || row.revenue) },
            { header: 'Profit', key: 'total_profit', render: (v, row) => fmt(v || row.profit) },
            { header: 'Margin', key: 'avg_profit_margin', render: (v, row) => {
              const m = v || row.profitMargin;
              return m ? fmtPct(m) : '--';
            }},
          ]}
          rows={stores}
        />
      </div>
    </>
  );
}
