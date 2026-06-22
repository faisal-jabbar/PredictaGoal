import { Globe, CheckCircle, Clock } from 'lucide-react'

const DISPLAY = {
  tournament: 'Tournament', tournament_type: 'Type', venue_type: 'Venue Type',
  neutral_venue: 'Neutral Venue', rivalry_match: 'Rivalry Match',
  host_country: 'Host Country', host_city: 'Host City',
}

export default function ContextualPanel({ data }) {
  if (!data?.data) return null
  const d = data.data
  const avail = d.available_context || {}
  const unavail = d.unavailable_context || {}

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-4">
        <h2 className="section-title mb-0"><Globe className="w-5 h-5 text-pitch-400" />Context Availability</h2>
        <span className="badge-slate">{d.context_coverage_pct ?? '—'}% coverage</span>
      </div>

      <p className="label mb-3 text-pitch-400 flex items-center gap-1.5">
        <CheckCircle className="w-3 h-3" /> Available from Dataset
      </p>
      <div className="grid grid-cols-2 gap-2 mb-5">
        {Object.entries(avail).map(([key, val]) => {
          const label = DISPLAY[key] || key.replace(/_/g, ' ')
          const display = typeof val === 'boolean' ? (val ? 'Yes' : 'No')
                        : typeof val === 'object' ? JSON.stringify(val).slice(0,40)
                        : String(val)
          return (
            <div key={key} className="card-sm flex items-start gap-2">
              <CheckCircle className="w-3.5 h-3.5 text-pitch-500 mt-0.5 flex-shrink-0" />
              <div>
                <p className="text-xs text-slate-500">{label}</p>
                <p className="text-xs font-medium text-slate-200 capitalize">{display}</p>
              </div>
            </div>
          )
        })}
      </div>

      <p className="label mb-3 text-amber-400 flex items-center gap-1.5">
        <Clock className="w-3 h-3" /> Planned Future Integrations
      </p>
      <div className="space-y-2">
        {Object.entries(unavail).map(([key, info]) => (
          <div key={key} className="flex items-start gap-2 p-2 rounded-lg bg-navy-900/50 border border-slate-700/30">
            <Clock className="w-3.5 h-3.5 text-amber-500 mt-0.5 flex-shrink-0" />
            <div>
              <p className="text-xs font-medium text-slate-300 capitalize">{key.replace(/_/g, ' ')}</p>
              <p className="text-xs text-slate-600">{info?.note || info?.status || 'Pending'}</p>
            </div>
          </div>
        ))}
      </div>

      {d.notes && (
        <p className="mt-4 text-xs text-slate-600 border-t border-slate-700/50 pt-3">{d.notes}</p>
      )}
    </div>
  )
}
