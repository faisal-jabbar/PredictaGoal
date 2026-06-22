import { Scale } from 'lucide-react'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Legend } from 'recharts'

export default function BiasReportPanel({ data }) {
  if (!data?.data) return null
  const d = data.data
  const acc = d.accuracy_by_class || {}
  const pred = d.prediction_distribution || {}
  const actual = d.actual_distribution || {}

  const classData = Object.entries(acc).map(([cls, a]) => ({
    class: cls === 'home_win' ? 'Home Win' : cls === 'draw' ? 'Draw' : 'Away Win',
    Accuracy: Math.round((a || 0) * 100),
  }))

  const distData = Object.keys(pred).map(cls => ({
    class: cls === 'home_win' ? 'Home Win' : cls === 'draw' ? 'Draw' : 'Away Win',
    Predicted: Math.round((pred[cls] || 0) * 100),
    Actual:    Math.round((actual[cls] || 0) * 100),
  }))

  return (
    <div className="card">
      <h2 className="section-title"><Scale className="w-5 h-5 text-blue-400" />Bias & Fairness Review</h2>

      <div className="grid grid-cols-2 gap-3 mb-5">
        <div className="card-sm">
          <p className="label mb-1">Overall Accuracy</p>
          <p className="value-md text-pitch-400">{d.overall_accuracy ? `${(d.overall_accuracy*100).toFixed(1)}%` : '—'}</p>
        </div>
        <div className="card-sm">
          <p className="label mb-1">Test Set Size</p>
          <p className="value-md text-slate-200">{d.test_set_size?.toLocaleString() ?? '—'}</p>
        </div>
      </div>

      <p className="label mb-3">Accuracy by Outcome Class</p>
      <ResponsiveContainer width="100%" height={140}>
        <BarChart data={classData} margin={{ left: 0, right: 8, top: 4, bottom: 4 }}>
          <XAxis dataKey="class" tick={{ fill: '#94a3b8', fontSize: 11 }} />
          <YAxis domain={[0,100]} tick={{ fill: '#64748b', fontSize: 10 }} unit="%" />
          <Tooltip contentStyle={{ background:'#0d1529',border:'1px solid #334155',borderRadius:'8px',fontSize:12 }} formatter={v=>`${v}%`} />
          <Bar dataKey="Accuracy" fill="#22c55e" radius={[4,4,0,0]} />
        </BarChart>
      </ResponsiveContainer>

      <p className="label mt-4 mb-3">Predicted vs Actual Distribution</p>
      <ResponsiveContainer width="100%" height={140}>
        <BarChart data={distData} margin={{ left: 0, right: 8, top: 4, bottom: 4 }}>
          <XAxis dataKey="class" tick={{ fill: '#94a3b8', fontSize: 11 }} />
          <YAxis domain={[0,60]} tick={{ fill: '#64748b', fontSize: 10 }} unit="%" />
          <Tooltip contentStyle={{ background:'#0d1529',border:'1px solid #334155',borderRadius:'8px',fontSize:12 }} formatter={v=>`${v}%`} />
          <Legend formatter={v=><span style={{color:'#94a3b8',fontSize:11}}>{v}</span>} />
          <Bar dataKey="Predicted" fill="#3b82f6" radius={[3,3,0,0]} />
          <Bar dataKey="Actual"    fill="#22c55e" radius={[3,3,0,0]} />
        </BarChart>
      </ResponsiveContainer>

      {d.known_issue && (
        <div className="mt-4 p-3 bg-amber-500/10 border border-amber-500/20 rounded-lg">
          <p className="text-xs text-amber-300 leading-relaxed">{d.known_issue}</p>
        </div>
      )}
      {d.fairness_notes && (
        <p className="mt-3 text-xs text-slate-600 border-t border-slate-700/50 pt-3">{d.fairness_notes}</p>
      )}
    </div>
  )
}
