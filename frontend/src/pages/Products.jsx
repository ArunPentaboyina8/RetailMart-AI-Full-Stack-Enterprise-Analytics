import { useState, useEffect } from 'react';
import Header from '../components/Header';
import ChartCard from '../components/ChartCard';
import DataTable from '../components/DataTable';
import { getTopProducts, getCategories, getABCAnalysis } from '../api';
import { fmt, fmtNum } from '../utils';

export default function Products() {
  const [products, setProducts] = useState(null);
  const [categories, setCategories] = useState(null);
  const [abc, setAbc] = useState(null);

  useEffect(() => {
    getTopProducts(15).then(r => setProducts(r.data)).catch(() => { });
    getCategories().then(r => setCategories(r.data)).catch(() => { });
    getABCAnalysis().then(r => {
      const d = r.data;
      // ABC data may come as { summary: [...], topAProducts: [...] } or as array
      setAbc(Array.isArray(d) ? d : d?.summary || []);
    }).catch(() => { });
  }, []);

  const topChart = products ? {
    labels: products.slice(0, 10).map(p => (p.prod_name || p.productName || '').substring(0, 20)),
    datasets: [{ label: 'Revenue', data: products.slice(0, 10).map(p => p.gross_revenue || p.net_revenue || p.revenue) }],
  } : null;

  const abcChart = abc ? {
    labels: abc.map(a => `Class ${a.abc_classification || a.class || a.classification}`),
    datasets: [{ data: abc.map(a => a.product_count || a.productCount) }],
  } : null;

  const catChart = categories ? {
    labels: categories.map(c => c.category),
    datasets: [{ label: 'Revenue', data: categories.map(c => c.net_revenue || c.gross_revenue || c.revenue) }],
  } : null;

  return (
    <>
      <Header title="📦 Product Analytics" />
      <div className="page-content">
        <div className="page-header">
          <h2>Product Analytics</h2>
          <p>Product performance, ABC analysis, and category breakdown</p>
        </div>
        <div className="charts-grid">
          <ChartCard title="🏆 Top Products by Revenue" type="bar" data={topChart} fullWidth />
          <ChartCard title="📊 ABC Analysis" type="doughnut" data={abcChart} />
          <ChartCard title="📈 Category Performance" type="bar" data={catChart} />
        </div>
        <DataTable
          title="📋 Product Details"
          columns={[
            { header: '#', key: '_idx', render: (_, __, i) => i + 1 },
            { header: 'Product', key: 'prod_name', render: (v, row) => v || row.productName },
            { header: 'Category', key: 'category' },
            { header: 'Brand', key: 'brand' },
            { header: 'Revenue', key: 'gross_revenue', render: (v, row) => fmt(v || row.revenue) },
            { header: 'Units', key: 'total_units_sold', render: (v, row) => fmtNum(v || row.unitsSold) },
          ]}
          rows={products}
        />
      </div>
    </>
  );
}
