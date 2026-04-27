export default function AlertModal({ alerts, onClose }) {
  if (!alerts) return null;

  const items = alerts.alerts || [];

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-box" onClick={e => e.stopPropagation()}>
        <div className="modal-header">
          <h2>🔔 Active Alerts ({alerts.total_count})</h2>
          <button className="modal-close" onClick={onClose}>&times;</button>
        </div>
        <div className="modal-body">
          {items.length === 0 ? (
            <p style={{ color: 'var(--text-muted)', textAlign: 'center', padding: '20px' }}>No active alerts</p>
          ) : (
            items.map((alert, i) => (
              <div key={i} className={`alert-item ${(alert.severity || alert.priority || '').toLowerCase()}`}>
                <h4>{alert.alert_type || alert.type || 'Alert'}</h4>
                <p>{alert.message || alert.description || JSON.stringify(alert)}</p>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}
