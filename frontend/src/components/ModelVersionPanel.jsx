import { Package, CheckCircle } from 'lucide-react'
import LoadingState from './LoadingState.jsx'
import ErrorState from './ErrorState.jsx'

function Metric({ label, value, accent = 'green' }) {
  const cls = { green: 'text-pitch-400', amber: 'text-amber-400', blue: 'text-blue-400' }[accent]
  return (
    <div className="bg-navy-900/60 rounded-lg p-3 border border-slate-700/30">
      <p className="label mb-1">{label}</p>
      <p className={`text-2xl font-bold ${cls}`}>{value ?? '—'}</p>
    </div>
  )
}

function Row({ label, value, mono }) {
  return (
    <div className="flex justify-between items-start py-1.5 border-b border-slate-700/20 last:border-0">
      <span className="text-xs text-slate-500 shrink-0">{label}</span>
      <span className={`text-xs text-slate-300 text-right ml-4 ${mono ? 'font-mono' : ''}`}>{value || '—'}</span>
    </div>
  )
}

export default function ModelVersionPanel({ data, loading, error }) {
  return (
    <div className="card">
      <h2 className="section-title">
        <Package className="w-5 h-5 text-blue-400" />
        MLflow Model Version
      </h2>

      {loading && <LoadingState label="Loading model version…" />}
      {error   && <ErrorState  message="Model version unavailable." hint="Run scripts/15_run_mlflow_check.py" />}

      {data && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <span className="text-xl font-bold text-white font-mono">{data.model_version || '—'}</span>
            <div className="flex gap-2">
              {data.status && (
                <span className={data.status === 'active' ? 'badge-green' : 'badge-slate'}>
                  {data.status}
                </span>
              )}
              {data.promoted && (
                <span className="badge-green"><CheckCircle className="w-3 h-3" />Promoted</span>
              )}
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <Metric label="Test Accuracy"
              value={data.accuracy != null ? `${(data.accuracy * 100).toFixed(2)}%` : '—'}
              accent="green" />
            <Metric label="Draw F1"
              value={data.draw_f1 != null ? `${(data.draw_f1 * 100).toFixed(1)}%` : '—'}
              accent="amber" />
          </div>

          <div>
            <Row label="Model type"  value={data.model_type} />
            <Row label="MLflow run"  value={data.mlflow_run_id ? data.mlflow_run_id.slice(0, 16) + '…' : '—'} mono />
            <Row label="Git commit"  value={data.git_commit} mono />
            <Row label="Artifact"    value={data.artifact_path?.replace(/\\/g, '/').split('/').pop()} />
            <Row label="Created"
              value={data.created_at ? new Date(data.created_at).toLocaleDateString('en-GB') : '—'} />
          </div>
        </div>
      )}
    </div>
  )
}
