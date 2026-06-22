import axios from 'axios'

const BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

const api = axios.create({ baseURL: BASE, timeout: 10000 })

export const fetchHealth       = () => api.get('/health').then(r => r.data)
export const fetchSummary      = () => api.get('/api/v1/summary').then(r => r.data)
export const fetchPrediction   = () => api.get('/api/v1/predictions/sample').then(r => r.data)
export const fetchDataset      = () => api.get('/api/v1/reports/dataset').then(r => r.data)
export const fetchModel        = () => api.get('/api/v1/reports/model').then(r => r.data)
export const fetchConfidence   = () => api.get('/api/v1/reports/confidence').then(r => r.data)
export const fetchExplanation  = () => api.get('/api/v1/reports/explanation').then(r => r.data)
export const fetchDrift        = () => api.get('/api/v1/reports/drift').then(r => r.data)
export const fetchBias         = () => api.get('/api/v1/reports/bias').then(r => r.data)
export const fetchContextual   = () => api.get('/api/v1/reports/contextual').then(r => r.data)
