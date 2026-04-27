export default function KPICard({ icon, label, value, change }) {
  const isPositive = change && !String(change).startsWith('-');
  return (
    <div className="kpi-card">
      <div className="kpi-icon">{icon}</div>
      <div className="kpi-label">{label}</div>
      <div className="kpi-value">{value ?? '--'}</div>
      {change !== undefined && change !== null && (
        <div className={`kpi-change ${isPositive ? 'positive' : 'negative'}`}>
          {isPositive ? '↑' : '↓'} {String(change).replace('-', '')}
        </div>
      )}
    </div>
  );
}
