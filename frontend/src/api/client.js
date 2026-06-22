import axios from 'axios'

const BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

const api     = axios.create({ baseURL: BASE, timeout: 10000 })
const slowApi = axios.create({ baseURL: BASE, timeout: 30000 })

// ── Phase 01 / 02 ────────────────────────────────────────────
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

// ── Phase 03 ─────────────────────────────────────────────────
export const fetchSystemStatus    = () => slowApi.get('/api/v1/system/status').then(r => r.data)
export const fetchProviders       = () => api.get('/api/v1/providers/status').then(r => r.data)
export const fetchRetraining      = () => api.get('/api/v1/retraining/status').then(r => r.data)
export const fetchModelVersion    = () => api.get('/api/v1/model/version').then(r => r.data)
export const fetchAuditRecent     = () => api.get('/api/v1/audit/recent').then(r => r.data)
export const fetchAlertsRecent    = () => api.get('/api/v1/alerts/recent').then(r => r.data)
export const postCustomPrediction = body => slowApi.post('/api/v1/predictions/custom', body).then(r => r.data)
export const postAgentQuery       = (query, session_id) =>
  slowApi.post('/api/v1/agent/query', { query, session_id }).then(r => r.data)
