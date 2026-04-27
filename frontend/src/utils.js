export function fmt(n) {
  if (n == null) return '--';
  const num = Number(n);
  if (isNaN(num)) return String(n);
  if (Math.abs(num) >= 1e7) return '₹' + (num / 1e7).toFixed(2) + ' Cr';
  if (Math.abs(num) >= 1e5) return '₹' + (num / 1e5).toFixed(2) + ' L';
  if (Math.abs(num) >= 1e3) return '₹' + (num / 1e3).toFixed(1) + 'K';
  return '₹' + num.toLocaleString('en-IN', { maximumFractionDigits: 0 });
}

export function fmtNum(n) {
  if (n == null) return '--';
  return Number(n).toLocaleString('en-IN');
}

export function fmtPct(n) {
  if (n == null) return '--';
  return Number(n).toFixed(1) + '%';
}
