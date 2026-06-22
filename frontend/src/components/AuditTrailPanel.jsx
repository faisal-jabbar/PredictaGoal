import { Shield, Hash } from 'lucide-react'
import LoadingState from './LoadingState.jsx'
import ErrorState from './ErrorState.jsx'

function fmtDate(ts) {
  if (!ts) return '—'
  try { return new Date(ts).toLocaleString('en-GB', { dateStyle: 'short', timeStyle: 'short' }) }
  catch { return ts }
}

const PHASE_CLS = {
  'Phase 01': 'badge-slate',
  'Phase 02': 'badge-blue',
  'Phase 03': 'badge-green',
}

export default function AuditTrailPanel({ data, loading, error }) {
  const events    = data?.events    || []
  const integrity = data?.integrity

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-4">
        <h2 className="section-title mb-0">
          <Shield className="w-5 h-5 text-pitch-400" />
          Audit Trail
        </h2>
        {integrity != null && (
          <span className={integrity.valid ? 'badge-green' : 'badge-red'}>
            <Hash className="w-3 h-3" />
            {integrity.valid ? 'Chain Valid' : 'Chain Broken'}
            {integrity.events_checked != null && ` · ${integrity.events_checked}`}
          </span>
        )}
      </div>

      {loading && <LoadingState label="Loading audit events…" />}
      {error   && <ErrorState  message="Audit trail unavailable." />}

      {!loading && !error && events.length === 0 && (
        <p className="text-sm text-slate-500 py-4 text-center">No audit events recorded yet.</p>
      )}

      {events.length > 0 && (
        <div className="overflow-y-auto max-h-64 space-y-1.5 pr-1">
          {[...events].reverse().map((ev, i) => (
            <div key={ev.event_id || i}
              className="flex items-start gap-3 p-2.5 bg-navy-900/60 rounded-lg border border-slate-700/20">
              <div className="flex-1 min-w-0">
                <div className="flex flex-wrap gap-1.5 items-center mb-1">
                  <span className="text-xs font-medium text-slate-200">
                    {ev.event_type?.replace(/_/g, ' ')}
                  </span>
                  {ev.phase && (
                    <span className={PHASE_CLS[ev.phase] || 'badge-slate'}>{ev.phase}</span>
                  )}
                </div>
                <div className="flex flex-wrap gap-3 text-xs text-slate-600">
                  <span>{ev.actor || 'system'}</span>
                  <span>{fmtDate(ev.timestamp)}</span>
                  {ev.hash && (
                    <span className="font-mono">{ev.hash.slice(0, 12)}…</span>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
