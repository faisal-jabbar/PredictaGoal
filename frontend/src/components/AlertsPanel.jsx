import { Bell, AlertTriangle, Info, CheckCircle } from 'lucide-react'
import LoadingState from './LoadingState.jsx'
import ErrorState from './ErrorState.jsx'

function fmtDate(ts) {
  if (!ts) return '—'
  try { return new Date(ts).toLocaleString('en-GB', { dateStyle: 'short', timeStyle: 'short' }) }
  catch { return ts }
}

const SEV_ICON = {
  warning: <AlertTriangle className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />,
  high:    <AlertTriangle className="w-4 h-4 text-danger-400 shrink-0 mt-0.5" />,
  info:    <Info          className="w-4 h-4 text-blue-400  shrink-0 mt-0.5" />,
}
const SEV_BADGE = {
  warning: 'badge-amber',
  high:    'badge-red',
  info:    'badge-blue',
}

export default function AlertsPanel({ data, loading, error }) {
  const alerts = data?.alerts || []

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-4">
        <h2 className="section-title mb-0">
          <Bell className="w-5 h-5 text-amber-400" />
          Recent Alerts
        </h2>
        {!loading && !error && (
          alerts.length > 0
            ? <span className="badge-amber">{alerts.length} active</span>
            : <span className="badge-green">All clear</span>
        )}
      </div>

      {loading && <LoadingState label="Loading alerts…" />}
      {error   && <ErrorState  message="Alerts unavailable." />}

      {!loading && !error && alerts.length === 0 && (
        <div className="flex flex-col items-center gap-2 py-6 text-slate-600">
          <CheckCircle className="w-6 h-6 text-pitch-400" />
          <p className="text-sm">No active alerts.</p>
        </div>
      )}

      {alerts.length > 0 && (
        <div className="space-y-2 overflow-y-auto max-h-64">
          {alerts.map((alert, i) => {
            const sev = (alert.severity || 'info').toLowerCase()
            const emailSent = alert.email_result?.sent
            return (
              <div key={alert.alert_id || i}
                className="flex items-start gap-3 p-3 bg-navy-900/60 rounded-lg border border-slate-700/20">
                {SEV_ICON[sev] || SEV_ICON.info}
                <div className="flex-1 min-w-0">
                  <div className="flex flex-wrap gap-1.5 items-center mb-1">
                    <span className="text-xs font-medium text-slate-200">
                      {alert.alert_type?.replace(/_/g, ' ')}
                    </span>
                    <span className={SEV_BADGE[sev] || 'badge-slate'}>{sev}</span>
                    {emailSent != null && (
                      <span className={emailSent ? 'badge-green' : 'badge-slate'}>
                        Email {emailSent ? 'sent' : 'disabled'}
                      </span>
                    )}
                  </div>
                  <p className="text-xs text-slate-400 leading-relaxed">{alert.message}</p>
                  <p className="text-xs text-slate-600 mt-1">{fmtDate(alert.timestamp || alert._written_at)}</p>
                </div>
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}
