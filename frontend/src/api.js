import axios from 'axios';

const API = axios.create({
  baseURL: 'http://localhost:8000',
  timeout: 5000,
});

// Base path for static data (matches Vite's base config)
const DATA_BASE = import.meta.env.BASE_URL + 'data';

/**
 * Helper: try the live API first; on failure, load from static JSON.
 * The static files live in public/data/ and are served as-is by Vite/GH Pages.
 */
async function withFallback(apiCall, staticPath, transform) {
  try {
    const res = await apiCall();
    return res.data;                         // live backend response
  } catch {
    const res = await axios.get(`${DATA_BASE}/${staticPath}`);
    const raw = res.data;
    // Wrap in the same { status, data } envelope the backend returns
    return transform ? transform(raw) : { status: 'ok', data: raw };
  }
}

// ── Executive ──
export const getExecutiveSummary = () =>
  withFallback(
    () => API.get('/api/executive-summary'),
    'sales/executive_summary.json',
    (d) => ({ status: 'ok', data: d })       // single object, not array
  );

// ── Sales ──
export const getMonthlySales = (limit = 12) =>
  withFallback(
    () => API.get(`/api/sales/monthly-trend?limit=${limit}`),
    'sales/monthly_trend.json',
    (d) => ({ status: 'ok', data: d.slice(0, limit) })
  );

export const getDailySales = (limit = 30) =>
  withFallback(
    () => API.get(`/api/sales/daily-trend?limit=${limit}`),
    'sales/recent_trend.json',
    (d) => ({ status: 'ok', data: d.slice(0, limit) })
  );

export const getPaymentModes = () =>
  withFallback(
    () => API.get('/api/sales/payment-modes'),
    'sales/payment_modes.json'
  );

export const getDayOfWeek = () =>
  withFallback(
    () => API.get('/api/sales/day-of-week'),
    'sales/dayofweek.json'
  );

export const getQuarterlySales = () =>
  withFallback(
    () => API.get('/api/sales/quarterly'),
    'sales/quarterly_sales.json'
  );

// ── Customers ──
export const getTopCustomers = (limit = 10) =>
  withFallback(
    () => API.get(`/api/customers/top?limit=${limit}`),
    'customers/top_customers.json',
    (d) => ({ status: 'ok', data: d.slice(0, limit) })
  );

export const getCLVTiers = () =>
  withFallback(
    () => API.get('/api/customers/clv-tiers'),
    'customers/clv_tiers.json'
  );

export const getRFMSegments = () =>
  withFallback(
    () => API.get('/api/customers/rfm-segments'),
    'customers/rfm_segments.json'
  );

export const getChurnRisk = () =>
  withFallback(
    () => API.get('/api/customers/churn-risk'),
    'customers/churn_risk.json',
    (d) => ({ status: 'ok', data: Array.isArray(d) ? d.slice(0, 100) : d })
  );

// ── Products ──
export const getTopProducts = (limit = 10) =>
  withFallback(
    () => API.get(`/api/products/top?limit=${limit}`),
    'products/top_products.json',
    (d) => ({ status: 'ok', data: d.slice(0, limit) })
  );

export const getCategories = () =>
  withFallback(
    () => API.get('/api/products/categories'),
    'products/categories.json'
  );

export const getABCAnalysis = () =>
  withFallback(
    () => API.get('/api/products/abc-analysis'),
    'products/abc_analysis.json'
  );

// ── Stores ──
export const getStorePerformance = (limit = 10) =>
  withFallback(
    () => API.get(`/api/stores/performance?limit=${limit}`),
    'stores/top_stores.json',
    (d) => ({ status: 'ok', data: d.slice(0, limit) })
  );

export const getRegionalData = () =>
  withFallback(
    () => API.get('/api/stores/regional'),
    'stores/regional.json'
  );

// ── Operations ──
export const getOpsSummary = () =>
  withFallback(
    () => API.get('/api/operations/summary'),
    'operations/summary.json'
  );

export const getDelivery = () =>
  withFallback(
    () => API.get('/api/operations/delivery'),
    'operations/delivery.json'
  );

export const getCouriers = () =>
  withFallback(
    () => API.get('/api/operations/couriers'),
    'operations/couriers.json'
  );

// ── Marketing ──
export const getCampaigns = () =>
  withFallback(
    () => API.get('/api/marketing/campaigns'),
    'marketing/campaigns.json',
    (d) => ({ status: 'ok', data: Array.isArray(d) ? d.slice(0, 50) : d })
  );

export const getChannels = () =>
  withFallback(
    () => API.get('/api/marketing/channels'),
    'marketing/channels.json'
  );

// ── Alerts ──
export const getAlerts = () =>
  API.get('/api/alerts').then(r => r.data).catch(() => ({ status: 'ok', data: [] }));

// ── Health ──
export const getHealth = () =>
  API.get('/health').then(r => r.data).catch(() => ({
    status: 'ok', database: 'demo_mode', knowledge_base: 'demo_mode'
  }));

// ── AI Chat ──
export const sendChat = (question) =>
  API.post('/api/chat', { question, show_sql: true }).then(r => r.data).catch(() => ({
    status: 'ok',
    data: {
      answer: '🔌 AI Chat requires a running backend. This is a static demo deployed on GitHub Pages — the charts and data you see are from pre-loaded analytics data.',
      sql: null
    }
  }));

export default API;
