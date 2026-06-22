import { Globe, CheckCircle, XCircle, AlertCircle } from 'lucide-react'
import LoadingState from './LoadingState.jsx'
import ErrorState from './ErrorState.jsx'

const META = {
  kaggle:   { label: 'Kaggle Dataset',        detail: 'martj42/international-football-results' },
  weather:  { label: 'Weather (Open-Meteo)',   detail: 'Free — no API key required' },
  fixtures: { label: 'Fixtures API',           detail: 'Requires FOOTBALL_API_KEY in .env' },
  injury:   { label: 'Injury Feed',            detail: 'Requires INJURY_API_KEY in .env' },
}

function ProviderRow({ name, info }) {
  const { label, detail } = META[name] || { label: name, detail: '' }
  const status = info?.status || 'unknown'
  const isOk       = status === 'ok' || status === 'healthy'
  const isDisabled = status === 'disabled'

  return (
    <div className="flex items-center justify-between py-3 border-b border-slate-700/30 last:border-0">
      <div className="flex items-center gap-3">
        {isOk
          ? <CheckCircle className="w-4 h-4 text-pitch-400 shrink-0" />
          : isDisabled
          ? <XCircle     className="w-4 h-4 text-slate-600 shrink-0" />
          : <AlertCircle className="w-4 h-4 text-amber-400 shrink-0" />}
        <div>
          <p className="text-sm font-medium text-slate-200">{label}</p>
          <p className="text-xs text-slate-600">{detail}</p>
        </div>
      </div>
      <div className="text-right shrink-0 ml-3">
        {isOk       && <span className="badge-green">Connected</span>}
        {isDisabled && (
          <div>
            <span className="badge-slate">Requires API key</span>
            {info?.reason && <p className="text-xs text-slate-600 mt-1 max-w-[180px] text-right">{info.reason}</p>}
          </div>
        )}
        {!isOk && !isDisabled && <span className="badge-amber">{status}</span>}
      </div>
    </div>
  )
}

export default function ProviderStatusPanel({ data, loading, error }) {
  const providers = data?.providers || {}

  return (
    <div className="card">
      <h2 className="section-title">
        <Globe className="w-5 h-5 text-blue-400" />
        External Data Providers
      </h2>

      {loading && <LoadingState label="Checking providers…" />}
      {error   && <ErrorState  message="Provider status unavailable." />}

      {!loading && !error && (
        <>
          {['kaggle', 'weather', 'fixtures', 'injury'].map(name => (
            <ProviderRow key={name} name={name} info={providers[name]} />
          ))}
          <p className="text-xs text-slate-600 pt-3 border-t border-slate-700/20 mt-1">
            Disabled providers return no-op responses. The system continues operating without them.
          </p>
        </>
      )}
    </div>
  )
}
