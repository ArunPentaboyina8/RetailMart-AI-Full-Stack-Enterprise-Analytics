import axios from 'axios';

const API = axios.create({
  baseURL: 'http://localhost:8000',
  timeout: 30000,
});

// ── Executive ──
export const getExecutiveSummary = () => API.get('/api/executive-summary').then(r => r.data);

// ── Sales ──
export const getMonthlySales = (limit = 12) => API.get(`/api/sales/monthly-trend?limit=${limit}`).then(r => r.data);
export const getDailySales = (limit = 30) => API.get(`/api/sales/daily-trend?limit=${limit}`).then(r => r.data);
export const getPaymentModes = () => API.get('/api/sales/payment-modes').then(r => r.data);
export const getDayOfWeek = () => API.get('/api/sales/day-of-week').then(r => r.data);
export const getQuarterlySales = () => API.get('/api/sales/quarterly').then(r => r.data);

// ── Customers ──
export const getTopCustomers = (limit = 10) => API.get(`/api/customers/top?limit=${limit}`).then(r => r.data);
export const getCLVTiers = () => API.get('/api/customers/clv-tiers').then(r => r.data);
export const getRFMSegments = () => API.get('/api/customers/rfm-segments').then(r => r.data);
export const getChurnRisk = () => API.get('/api/customers/churn-risk').then(r => r.data);

// ── Products ──
export const getTopProducts = (limit = 10) => API.get(`/api/products/top?limit=${limit}`).then(r => r.data);
export const getCategories = () => API.get('/api/products/categories').then(r => r.data);
export const getABCAnalysis = () => API.get('/api/products/abc-analysis').then(r => r.data);

// ── Stores ──
export const getStorePerformance = (limit = 10) => API.get(`/api/stores/performance?limit=${limit}`).then(r => r.data);
export const getRegionalData = () => API.get('/api/stores/regional').then(r => r.data);

// ── Operations ──
export const getOpsSummary = () => API.get('/api/operations/summary').then(r => r.data);
export const getDelivery = () => API.get('/api/operations/delivery').then(r => r.data);
export const getCouriers = () => API.get('/api/operations/couriers').then(r => r.data);

// ── Marketing ──
export const getCampaigns = () => API.get('/api/marketing/campaigns').then(r => r.data);
export const getChannels = () => API.get('/api/marketing/channels').then(r => r.data);

// ── Alerts ──
export const getAlerts = () => API.get('/api/alerts').then(r => r.data);

// ── Health ──
export const getHealth = () => API.get('/health').then(r => r.data);

// ── AI Chat ──
export const sendChat = (question) =>
  API.post('/api/chat', { question, show_sql: true }).then(r => r.data);

export default API;
