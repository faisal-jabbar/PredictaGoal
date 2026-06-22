import { Activity, AlertTriangle, CheckCircle } from 'lucide-react'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell, ReferenceLine } from 'recharts'

const LEVEL_CONFIG = {
  none:   { cls: 'badge-green', icon: CheckCircle, color: '#22c55e' },
  low:    { cls: 'badge-blue',  icon: CheckCircle, color: '#3b82f6' },
  medium: { cls: 'badge-amber', icon: AlertTriangle, color: '#f59e0b' },
  high:   { cls: 'badge-red',   icon: AlertTriangle, color: '#ef4444' },
}

export default function DriftReportPanel({ data }) {
  if (!data?.data) return null
  const d = data.data
  const cfg = LEVEL_CONFIG[d.overall_drift_level] || LEVEL_CONFIG.low
  const Icon = cfg.icon

  const chartData = (d.feature_details || []).slice(0, 14).map(f => ({
    name: f.feature.replace(/_/g, ' ').slice(0, 14),
    psi: f.psi,
    level: f.drift_level,
  }))

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-4">
        <h2 className="section-title mb-0"><Activity className="w-5 h-5 text-amber-400" />Drift Monitoring</h2>
        <span className={cfg.cls}><Icon className="w-3 h-3" />{d.overall_drift_level?.toUpperCase()} DRIFT</span>
      </div>

      <div className="grid grid-cols-3 gap-3 mb-5">
        {[
          { label: 'Features Checked', val: d.features_checked },
          { label: 'Drifted',          val: d.drifted_count },
          { label: 'Max PSI',          val: d.max_psi?.toFixed(3) },
        ].map(({ label, val }) => (
          <div key={label} className="card-sm text-center">
            <p className="label mb-1">{label}</p>
            <p className="font-semibold text-slate-200">{val ?? '—'}</p>
          </div>
        ))}
      </div>

      {chartData.length > 0 && (
        <ResponsiveContainer width="100%" height={180}>
          <BarChart data={chartData} layout="vertical" margin={{ left: 8, right: 24, top: 4, bottom: 4 }}>
            <XAxis type="number" tick={{ fill: '#64748b', fontSize: 10 }} />
            <YAxis type="category" dataKey="name" width={110} tick={{ fill: '#94a3b8', fontSize: 10 }} />
            <Tooltip contentStyle={{ background:'#0d1529',border:'1px solid #334155',borderRadius:'8px',fontSize:12 }} />
            <ReferenceLine x={0.10} stroke="#22c55e" strokeDasharray="3 3" />
            <ReferenceLine x={0.20} stroke="#f59e0b" strokeDasharray="3 3" />
            <ReferenceLine x={0.25} stroke="#ef4444" strokeDasharray="3 3" />
            <Bar dataKey="psi" radius={[0,3,3,0]}>
              {chartData.map((e, i) => (
                <Cell key={i} fill={e.level === 'high' ? '#ef4444' : e.level === 'medium' ? '#f59e0b' : e.level === 'low' ? '#3b82f6' : '#22c55e'} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      )}

      {d.drifted_features?.length > 0 && (
        <p className="text-xs text-amber-400 mt-3 flex items-center gap-1">
          <AlertTriangle className="w-3 h-3" /> Drifted: {d.drifted_features.join(', ')}
        </p>
      )}
      <p className="mt-3 text-xs text-slate-600 border-t border-slate-700/50 pt-3">{d.notes}</p>
    </div>
  )
}
