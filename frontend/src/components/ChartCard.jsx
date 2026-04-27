import { useRef, useEffect } from 'react';
import { Chart, registerables } from 'chart.js';

Chart.register(...registerables);

// Dark theme defaults
Chart.defaults.color = '#9ca3b8';
Chart.defaults.borderColor = 'rgba(42,47,69,0.5)';
Chart.defaults.font.family = "'Inter', sans-serif";

const PALETTE = [
  '#6366f1', '#a855f7', '#22d3ee', '#34d399', '#fb923c',
  '#f87171', '#f472b6', '#818cf8', '#fbbf24', '#2dd4bf',
];

export default function ChartCard({ title, type, data, options = {}, fullWidth = false }) {
  const canvasRef = useRef(null);
  const chartRef = useRef(null);

  useEffect(() => {
    if (!canvasRef.current || !data) return;

    if (chartRef.current) chartRef.current.destroy();

    const datasets = (data.datasets || []).map((ds, i) => ({
      ...ds,
      backgroundColor: ds.backgroundColor || (
        type === 'doughnut' || type === 'pie'
          ? PALETTE
          : PALETTE[i % PALETTE.length] + '99'
      ),
      borderColor: ds.borderColor || PALETTE[i % PALETTE.length],
      borderWidth: ds.borderWidth ?? (type === 'line' ? 2 : 1),
      tension: ds.tension ?? 0.4,
      fill: ds.fill ?? (type === 'line'),
      pointRadius: ds === 'line' ? 0 : ds.pointRadius,
    }));

    chartRef.current = new Chart(canvasRef.current, {
      type,
      data: { ...data, datasets },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            display: type === 'doughnut' || type === 'pie' || datasets.length > 1,
            position: 'bottom',
            labels: { padding: 16, usePointStyle: true, pointStyleWidth: 8 },
          },
          tooltip: {
            backgroundColor: '#1e2235',
            borderColor: '#2a2f45',
            borderWidth: 1,
            titleFont: { weight: 600 },
            padding: 10,
            cornerRadius: 8,
          },
        },
        scales: (type === 'doughnut' || type === 'pie') ? {} : {
          x: { grid: { display: false } },
          y: { grid: { color: 'rgba(42,47,69,0.3)' }, beginAtZero: true },
        },
        ...options,
      },
    });

    return () => { if (chartRef.current) chartRef.current.destroy(); };
  }, [data, type, options]);

  return (
    <div className={`chart-card ${fullWidth ? 'full-width' : ''}`}>
      <h3>{title}</h3>
      <div className="chart-wrapper">
        {data ? <canvas ref={canvasRef} /> : (
          <div className="spinner-container"><div className="spinner" /></div>
        )}
      </div>
    </div>
  );
}
