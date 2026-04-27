import { useState, useEffect } from 'react';
import Header from '../components/Header';
import KPICard from '../components/KPICard';
import ChartCard from '../components/ChartCard';
import DataTable from '../components/DataTable';
import { getExecutiveSummary, getMonthlySales, getTopProducts, getTopCustomers, getCategories } from '../api';
import { fmt, fmtNum } from '../utils';

export default function Executive() {
  const [summary, setSummary] = useState(null);
  const [monthly, setMonthly] = useState(null);
  const [products, setProducts] = useState(null);
  const [customers, setCustomers] = useState(null);
  const [categories, setCategories] = useState(null);

  useEffect(() => {
    getExecutiveSummary().then(r => setSummary(r.data)).catch(() => {});
    getMonthlySales(12).then(r => setMonthly(r.data)).catch(() => {});
    getTopProducts(10).then(r => setProducts(r.data)).catch(() => {});
    getTopCustomers(10).then(r => setCustomers(r.data)).catch(() => {});
    getCategories().then(r => setCategories(r.data)).catch(() => {});
  }, []);

  const revenueChart = monthly ? {
    labels: monthly.map(m => `${m.month_name || m.month}/${m.year}`),
    datasets: [{
      label: 'Revenue',
      data: monthly.map(m => m.net_revenue || m.gross_revenue || m.total_revenue || m.revenue),
    }],
  } : null;

  const categoryChart = categories ? {
    labels: categories.map(c => c.category || c.product_category),
    datasets: [{
      data: categories.map(c => c.net_revenue || c.gross_revenue || c.total_revenue || c.revenue),
    }],
  } : null;

  return (
    <>
      <Header title="📊 Executive Dashboard" />
      <div className="page-content">
        <div className="page-header">
          <h2>Executive Overview</h2>
          <p>Key performance metrics across all business units</p>
        </div>

        <div className="kpi-grid">
          <KPICard icon="💰" label="Total Revenue" value={summary ? fmt(summary.total_revenue) : null}
            change={summary?.revenue_growth_pct ? `${summary.revenue_growth_pct}%` : null} />
          <KPICard icon="📦" label="Total Orders" value={summary ? fmtNum(summary.total_orders) : null}
            change={summary?.orders_growth_pct ? `${summary.orders_growth_pct}%` : null} />
          <KPICard icon="👥" label="Total Customers" value={summary ? fmtNum(summary.total_customers) : null} />
          <KPICard icon="🛒" label="Avg Order Value" value={summary ? fmt(summary.overall_aov || summary.avg_order_value) : null} />
        </div>

        <div className="charts-grid">
          <ChartCard title="📈 Revenue Trend (Last 12 Months)" type="line" data={revenueChart} fullWidth />
          <ChartCard title="🥧 Revenue by Category" type="doughnut" data={categoryChart} />
        </div>

        <div className="charts-grid">
          <DataTable
            title="🏆 Top 10 Products"
            columns={[
              { header: '#', key: '_idx', render: (_, __, i) => i + 1 },
              { header: 'Product', key: 'prod_name', render: (v, row) => v || row.productName || row.product_name || '--' },
              { header: 'Category', key: 'category', render: (v, row) => v || row.product_category || '--' },
              { header: 'Revenue', key: 'gross_revenue', render: (v, row) => fmt(v || row.net_revenue || row.revenue || row.total_revenue) },
            ]}
            rows={products}
          />
          <DataTable
            title="⭐ Top 10 Customers"
            columns={[
              { header: '#', key: '_idx', render: (_, __, i) => i + 1 },
              { header: 'Customer', key: 'full_name', render: (v, row) => v || row.fullName || row.customer_name || '--' },
              { header: 'City', key: 'city' },
              { header: 'Total Spent', key: 'total_revenue', render: (v, row) => fmt(v || row.totalRevenue || row.total_spent) },
            ]}
            rows={customers}
          />
        </div>
      </div>
    </>
  );
}
