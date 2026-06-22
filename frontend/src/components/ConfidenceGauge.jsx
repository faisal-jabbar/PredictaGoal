import { ShieldCheck, ShieldAlert, AlertTriangle, XCircle } from 'lucide-react'

const TIER_CONFIG = {
  HIGH:       { color: 'text-pitch-400', bg: 'bg-pitch-500', bar: 'bg-pitch-500', icon: ShieldCheck, label: 'High Confidence' },
  MEDIUM:     { color: 'text-blue-400',  bg: 'bg-blue-500',  bar: 'bg-blue-500',  icon: ShieldCheck, label: 'Medium Confidence' },
  LOW:        { color: 'text-amber-400', bg: 'bg-amber-500', bar: 'bg-amber-500', icon: AlertTriangle, label: 'Low Confidence' },
  UNRELIABLE: { color: 'text-danger-400',bg: 'bg-danger-500',bar: 'bg-danger-500',icon: XCircle, label: 'Unreliable' },
}

export default function ConfidenceGauge({ data }) {
  if (!data?.data) return null
  const d = data.data
  const cfg = TIER_CONFIG[d.confidence_tier] || TIER_CONFIG.LOW
  const Icon = cfg.icon
  const pct = Math.round((d.pcs || 0) * 100)

  return (
    <div className="card">
      <h2 className="section-title"><ShieldCheck className="w-5 h-5 text-blue-400" />Prediction Confidence</h2>

      <div className="flex items-center gap-5 mb-5">
        <div className="relative w-24 h-24 flex-shrink-0">
          <svg viewBox="0 0 36 36" className="w-24 h-24 -rotate-90">
            <circle cx="18" cy="18" r="15.9" fill="none" stroke="#1e2a45" strokeWidth="3.8" />
            <circle cx="18" cy="18" r="15.9" fill="none" strokeWidth="3.8"
              stroke={d.confidence_tier === 'HIGH' ? '#22c55e' : d.confidence_tier === 'MEDIUM' ? '#3b82f6' : d.confidence_tier === 'LOW' ? '#f59e0b' : '#ef4444'}
              strokeDasharray={`${pct} 100`} strokeLinecap="round" />
          </svg>
          <div className="absolute inset-0 flex flex-col items-center justify-center">
            <span className={`text-xl font-bold ${cfg.color}`}>{pct}%</span>
          </div>
        </div>

        <div>
          <div className="flex items-center gap-2 mb-2">
            <Icon className={`w-5 h-5 ${cfg.color}`} />
            <span className={`font-semibold ${cfg.color}`}>{cfg.label}</span>
          </div>
          <p className="text-xs text-slate-400 leading-relaxed max-w-xs">{d.confidence_note}</p>
        </div>
      </div>

      <div className="grid grid-cols-3 gap-3 mt-2">
        {[
          { label: 'Margin Score', val: d.margin_score?.toFixed(3) },
          { label: 'Top-2 Gap',    val: d.top2_margin?.toFixed(3) },
          { label: 'Entropy',      val: d.entropy?.toFixed(3) },
        ].map(({ label, val }) => (
          <div key={label} className="card-sm text-center">
            <p className="label mb-1">{label}</p>
            <p className="font-mono text-sm text-slate-200">{val ?? '—'}</p>
          </div>
        ))}
      </div>
    </div>
  )
}
