import { useState, useEffect } from 'react';
import { HiOutlineBell } from 'react-icons/hi';
import { getAlerts, getHealth } from '../api';
import AlertModal from './AlertModal';

export default function Header({ title }) {
  const [alerts, setAlerts] = useState(null);
  const [showAlerts, setShowAlerts] = useState(false);
  const [health, setHealth] = useState(null);

  useEffect(() => {
    getAlerts().then(setAlerts).catch(() => {});
    getHealth().then(setHealth).catch(() => {});
  }, []);

  const alertCount = alerts?.total_count || 0;

  return (
    <>
      <header className="top-header">
        <h1 className="header-title">{title}</h1>
        <div className="header-actions">
          <div className="header-status">
            <span className="status-dot" style={{
              background: health?.status === 'healthy' ? 'var(--accent-green)'
                : health?.database === 'demo_mode' ? 'var(--accent-blue, #60a5fa)' : 'var(--accent-orange)'
            }} />
            <span>{health?.status === 'healthy' ? 'All systems online'
              : health?.database === 'demo_mode' ? 'Demo Mode' : 'Connecting...'}</span>
          </div>
          <button className="header-badge" onClick={() => setShowAlerts(true)} id="alert-button">
            <HiOutlineBell />
            {alertCount > 0 && <span className="badge-count">{alertCount}</span>}
          </button>
        </div>
      </header>
      {showAlerts && <AlertModal alerts={alerts} onClose={() => setShowAlerts(false)} />}
    </>
  );
}
