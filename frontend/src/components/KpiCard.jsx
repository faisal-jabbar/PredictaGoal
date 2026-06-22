export default function KpiCard({ title, value, subtitle, icon: Icon, accent = 'green' }) {
  const accentCls = {
    green: 'text-pitch-400',
    amber: 'text-amber-400',
    blue:  'text-blue-400',
    slate: 'text-slate-400',
  }[accent] || 'text-pitch-400'

  return (
    <div className="card flex flex-col gap-3 hover:border-slate-600 transition-colors">
      <div className="flex items-start justify-between">
        <span className="label">{title}</span>
        {Icon && <Icon className={`w-5 h-5 ${accentCls}`} />}
      </div>
      <p className={`value-lg ${accentCls}`}>{value ?? '—'}</p>
      {subtitle && <p className="text-xs text-slate-500">{subtitle}</p>}
    </div>
  )
}
