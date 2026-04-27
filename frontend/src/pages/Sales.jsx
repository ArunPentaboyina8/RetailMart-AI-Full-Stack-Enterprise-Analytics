import { useState, useEffect } from 'react';
import Header from '../components/Header';
import ChartCard from '../components/ChartCard';
import { getDailySales, getDayOfWeek, getPaymentModes, getQuarterlySales } from '../api';

export default function Sales() {
  const [daily, setDaily] = useState(null);
  const [dow, setDow] = useState(null);
  const [payment, setPayment] = useState(null);
  const [quarterly, setQuarterly] = useState(null);

  useEffect(() => {
    getDailySales(30).then(r => setDaily(r.data)).catch(() => { });
    getDayOfWeek().then(r => setDow(r.data)).catch(() => { });
    getPaymentModes().then(r => setPayment(r.data)).catch(() => { });
    getQuarterlySales().then(r => setQuarterly(r.data)).catch(() => { });
  }, []);

  const dailyChart = daily ? {
    labels: daily.map(d => d.order_date || d.date),
    datasets: [{ label: 'Daily Revenue', data: daily.map(d => d.daily_revenue || d.total_revenue) }],
  } : null;

  const dowChart = dow ? {
    labels: dow.map(d => d.day_name),
    datasets: [{ label: 'Total Revenue', data: dow.map(d => d.total_revenue) }],
  } : null;

  const paymentChart = payment ? {
    labels: payment.map(p => p.payment_mode || p.mode),
    datasets: [{ data: payment.map(p => p.total_revenue || p.order_count) }],
  } : null;

  const qChart = quarterly ? {
    labels: quarterly.map(q => q.quarter_label),
    datasets: [{ label: 'Quarterly Revenue', data: quarterly.map(q => q.total_revenue) }],
  } : null;

  return (
    <>
      <Header title="💰 Sales Analytics" />
      <div className="page-content">
        <div className="page-header">
          <h2>Sales Analytics</h2>
          <p>Revenue trends, payment analysis, and seasonal patterns</p>
        </div>
        <div className="charts-grid">
          <ChartCard title="📅 Daily Sales (Last 30 Days)" type="line" data={dailyChart} fullWidth />
          <ChartCard title="📆 Sales by Day of Week" type="bar" data={dowChart} />
          <ChartCard title="💳 Payment Methods" type="doughnut" data={paymentChart} />
          <ChartCard title="📊 Quarterly Performance" type="bar" data={qChart} />
        </div>
      </div>
    </>
  );
}
