import { RefreshCw, AlertCircle, CheckCircle } from 'lucide-react'
import LoadingState from './LoadingState.jsx'
import ErrorState from './ErrorState.jsx'

function fmtDate(ts) {
  if (!ts) return '—'
  try { return new Date(ts).toLocaleString('en-GB', { dateStyle: 'medium', timeStyle: 'short' }) }
  catch { return ts }
}

function Row({ label, value, accent }) {
  return (
    <div className="flex justify-between items-start py-1.5 border-b border-slate-700/20 last:border-0">
      <span className="text-xs text-slate-500 shrink-0">{label}</span>
      <span className={`text-xs font-medium text-right ml-4 ${accent || 'text-slate-300'}`}>{value || '—'}</span>
    </div>
  )
}

export default function RetrainingPanel({ data, loading, error }) {
  return (
    <div className="card">
      <h2 className="section-title">
        <RefreshCw className="w-5 h-5 text-amber-400" />
        Retraining Decision
      </h2>

      {loading && <LoadingState label="Checking retraining status…" />}
      {error   && <ErrorState  message="Retraining status unavailable." />}

      {data && (() => {
        const needed  = data.should_retrain ?? data.retrain_needed
        const reasons = Array.isArray(data.reasons) ? data.reasons.join(' · ') : (data.reason || '—')
        const maxPsi  = data.max_psi
        const drifted = Array.isArray(data.drifted_features) ? data.drifted_features.join(', ') : null
        const ts      = data.evaluated_at || data.timestamp

        return (
          <div className="space-y-3">
            <div className="flex flex-wrap gap-2">
              {needed
                ? <span className="badge-amber"><AlertCircle className="w-3 h-3" />Retraining Required</span>
                : <span className="badge-green"><CheckCircle className="w-3 h-3" />No Retraining Needed</span>}
              {data.status && (
                <span className="badge-slate font-mono text-xs">{data.status}</span>
              )}
            </div>

            <div>
              <Row label="Reason"         value={reasons} />
              {maxPsi != null && (
                <Row label="Max PSI"      value={maxPsi.toFixed(4)}
                     accent={maxPsi >= 0.25 ? 'text-amber-400' : 'text-slate-300'} />
              )}
              <Row label="Threshold"      value="PSI ≥ 0.25 or HIGH drift" />
              {drifted && <Row label="Drifted features" value={drifted} />}
              <Row label="Evaluated at"   value={fmtDate(ts)} />
            </div>
          </div>
        )
      })()}
    </div>
  )
}
