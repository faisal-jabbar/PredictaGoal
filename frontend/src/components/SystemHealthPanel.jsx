import { Activity, CheckCircle, XCircle, AlertTriangle } from 'lucide-react'
import LoadingState from './LoadingState.jsx'
import ErrorState from './ErrorState.jsx'

const OVERALL = {
  healthy:  { badge: 'badge-green', icon: CheckCircle,   color: 'text-pitch-400' },
  warning:  { badge: 'badge-amber', icon: AlertTriangle, color: 'text-amber-400' },
  degraded: { badge: 'badge-red',   icon: XCircle,       color: 'text-danger-400' },
}

function Check({ label, ok, note }) {
  return (
    <div className="flex items-center justify-between py-2.5 border-b border-slate-700/30 last:border-0">
      <div className="flex items-center gap-2">
        {ok
          ? <CheckCircle className="w-4 h-4 text-pitch-400 shrink-0" />
          : <XCircle     className="w-4 h-4 text-danger-400 shrink-0" />}
        <span className="text-sm text-slate-300">{label}</span>
      </div>
      {note && <span className="text-xs text-slate-500">{note}</span>}
    </div>
  )
}

export default function SystemHealthPanel({ data, loading, error }) {
  const o = OVERALL[data?.overall] || OVERALL.warning

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-4">
        <h2 className="section-title mb-0">
          <Activity className="w-5 h-5 text-pitch-400" />
          System Health
        </h2>
        {data && <span className={o.badge}>{data.overall}</span>}
      </div>

      {loading && <LoadingState label="Checking system health…" />}
      {error   && <ErrorState  message="System status unavailable." />}

      {data && (
        <div>
          <Check label="API Backend"    ok={data.api_ok}
            note={data.details?.api?.version ? `v${data.details.api.version}` : undefined} />
          <Check label="Firestore"      ok={data.firestore_ok} />
          <Check label="Model Artifact" ok={data.model_ok} note={data.model_ok ? 'Ready' : 'Missing'} />
          <Check label="Reports Fresh"  ok={data.stale_reports === 0}
            note={data.stale_reports > 0 ? `${data.stale_reports} stale` : 'All current'} />
        </div>
      )}
    </div>
  )
}
