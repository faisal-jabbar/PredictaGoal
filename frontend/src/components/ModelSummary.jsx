import { Brain } from 'lucide-react'
import { RadarChart, PolarGrid, PolarAngleAxis, Radar, ResponsiveContainer } from 'recharts'

export default function ModelSummary({ model }) {
  const d = model?.data || {}
  const clf = d.classification_report || {}
  const radarData = ['home_win','draw','away_win'].map(cls => ({
    class: cls === 'home_win' ? 'Home Win' : cls === 'draw' ? 'Draw' : 'Away Win',
    precision: Math.round((clf[cls]?.precision || 0) * 100),
    recall:    Math.round((clf[cls]?.recall    || 0) * 100),
    f1:        Math.round((clf[cls]?.['f1-score'] || 0) * 100),
  }))

  return (
    <div className="card">
      <h2 className="section-title"><Brain className="w-5 h-5 text-pitch-400" />Model Performance</h2>

      <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 mb-5">
        {[
          { label: 'Model Type',   val: d.model_type },
          { label: 'Train Size',   val: d.train_size?.toLocaleString() },
          { label: 'Test Size',    val: d.test_size?.toLocaleString() },
          { label: 'Split',        val: '80/20 time-based' },
          { label: 'Random Seed',  val: '42' },
          { label: 'Test Accuracy',val: d.accuracy ? `${(d.accuracy*100).toFixed(1)}%` : '—' },
        ].map(({ label, val }) => (
          <div key={label} className="card-sm">
            <p className="label mb-1">{label}</p>
            <p className="text-sm font-semibold text-slate-200">{val ?? '—'}</p>
          </div>
        ))}
      </div>

      {radarData.length > 0 && (
        <ResponsiveContainer width="100%" height={200}>
          <RadarChart data={radarData} margin={{ top: 8, right: 24, bottom: 8, left: 24 }}>
            <PolarGrid stroke="#1e2a45" />
            <PolarAngleAxis dataKey="class" tick={{ fill: '#94a3b8', fontSize: 12 }} />
            <Radar name="Precision" dataKey="precision" stroke="#22c55e" fill="#22c55e" fillOpacity={0.15} />
            <Radar name="Recall"    dataKey="recall"    stroke="#3b82f6" fill="#3b82f6" fillOpacity={0.10} />
            <Radar name="F1"        dataKey="f1"        stroke="#f59e0b" fill="#f59e0b" fillOpacity={0.10} />
          </RadarChart>
        </ResponsiveContainer>
      )}

      <p className="text-xs text-slate-600 mt-2">
        Radar shows per-class precision (green), recall (blue), and F1 (amber) as percentages.
        Draws are hardest to predict in football analytics.
      </p>
    </div>
  )
}
