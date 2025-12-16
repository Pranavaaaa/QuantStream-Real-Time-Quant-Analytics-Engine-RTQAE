import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

const api = axios.create({
    baseURL: API_BASE_URL,
    timeout: 10000,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Ingestion API
export const ingestionAPI = {
    start: (symbols) => api.post('/ingestion/start', { symbols }),
    stop: () => api.post('/ingestion/stop'),
    getStatus: () => api.get('/ingestion/status'),
    getLatestPrices: () => api.get('/ingestion/latest_prices'),
    getBuffer: (symbol, limit = 50) => api.get('/ingestion/buffer', { params: { symbol, limit } }),
};

// Analytics API
export const analyticsAPI = {
    getSummary: () => api.get('/analytics/summary'),
    getStats: (symbol) => api.get(`/analytics/stats/${symbol}`),
    getAllStats: () => api.get('/analytics/stats'),
    getZScore: (symbol) => api.get(`/analytics/zscore/${symbol}`),
    getAllZScores: () => api.get('/analytics/zscores'),
    getCorrelation: (symbol1, symbol2, type = 'pearson') =>
        api.get('/analytics/correlation', { params: { symbol1, symbol2, corr_type: type } }),
    getCorrelationMatrix: () => api.get('/analytics/correlation/matrix'),
    getSpread: (symbol1, symbol2, hedgeRatio = 1.0) =>
        api.get('/analytics/spread', { params: { symbol1, symbol2, hedge_ratio: hedgeRatio } }),
    getRegression: (symbolX, symbolY) =>
        api.get('/analytics/regression', { params: { symbol_x: symbolX, symbol_y: symbolY } }),
    getADFTest: (symbol) => api.get(`/analytics/adf/${symbol}`),
    getAlerts: (limit = 50) => api.get('/analytics/alerts', { params: { limit } }),
};

// Export API
export const exportAPI = {
    getOHLCV: (symbol, timeframe = '1m', limit = 100) =>
        api.get('/export/ohlcv', { params: { symbol, timeframe, limit } }),
    getAlerts: (format = 'csv', limit = 1000) =>
        api.get('/export/alerts', { params: { format, limit }, responseType: format === 'csv' ? 'blob' : 'json' }),
};

// Health check
export const healthAPI = {
    check: () => api.get('/health'),
};

export default api;
