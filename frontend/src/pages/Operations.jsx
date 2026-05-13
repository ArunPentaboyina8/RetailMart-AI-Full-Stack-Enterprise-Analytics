import { useState, useEffect } from 'react';
import Header from '../components/Header';
import KPICard from '../components/KPICard';
import ChartCard from '../components/ChartCard';
import { getOpsSummary, getDelivery, getCouriers } from '../api';
import { fmt, fmtPct, fmtNum } from '../utils';

export default function Operations() {
  const [ops, setOps] = useState(null);
  const [couriers, setCouriers] = useState(null);

  useEffect(() => {
    getOpsSummary().then(r => {
      // ops summary may be a single object (not wrapped in data) or { data: {...} }
      const d = r.data;
      setOps(d);
    }).catch(() => {});
    getCouriers().then(r => setCouriers(r.data)).catch(() => {});
  }, []);

  const courierChart = couriers ? {
    labels: couriers.map(c => c.courier_name || c.courier),
    datasets: [{ label: 'On-Time %', data: couriers.map(c => c.on_time_pct || c.onTimePct || c.on_time) }],
  } : null;

  const courierShipments = couriers ? {
    labels: couriers.map(c => c.courier_name || c.courier),
    datasets: [
      { label: 'Shipments', data: couriers.map(c => c.shipments || c.delivered || c.delivered_orders) },
    ],
  } : null;

  return (
    <>
      <Header title="🚚 Operations Analytics" />
      <div className="page-content">
        <div className="page-header">
          <h2>Operations Analytics</h2>
          <p>Delivery SLA, courier performance, and return analysis</p>
        </div>
        <div className="kpi-grid">
          <KPICard icon="✅" label="Delivery SLA" value={ops ? fmtPct(ops.delivery_sla_pct || ops.onTimePct || ops.on_time_pct) : null} />
          <KPICard icon="⏱️" label="Avg Delivery Days" value={ops?.avg_delivery_days || ops?.avgDeliveryDays ? `${Number(ops.avg_delivery_days || ops.avgDeliveryDays).toFixed(1)} days` : null} />
          <KPICard icon="↩️" label="Total Returns" value={ops ? fmtNum(ops.total_returns || ops.returnCount) : null} />
          <KPICard icon="💸" label="Total Refunds" value={ops ? fmt(ops.total_refunds || ops.totalRefunds) : null} />
        </div>
        <div className="charts-grid">
          <ChartCard title="🚚 Courier On-Time Performance" type="bar" data={courierChart} fullWidth />
          <ChartCard title="📦 Courier Shipment Volume" type="bar" data={courierShipments} />
        </div>
      </div>
    </>
  );
}
