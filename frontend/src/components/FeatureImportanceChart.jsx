import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts'
import { BarChart2 } from 'lucide-react'

const COLOURS = ['#22c55e','#4ade80','#86efac','#3b82f6','#60a5fa','#93c5fd','#f59e0b','#fbbf24']

const CustomTooltip = ({ active, payload }) => {
  if (!active || !payload?.length) return null
  return (
    <div className="bg-navy-800 border border-slate-700 rounded-lg px-3 py-2 text-xs shadow-xl">
      <p className="text-slate-300">{payload[0].payload.display_name}</p>
      <p className="text-pitch-400 font-semibold">Importance: {(payload[0].value * 100).toFixed(2)}%</p>
    </div>
  )
}

export default function FeatureImportanceChart({ features = [] }) {
  const data = features.slice(0, 8).map(f => ({
    name: (f.display_name || f.feature).replace(/\s+\(.+\)/, '').slice(0, 18),
    display_name: f.display_name || f.feature,
    importance: f.importance,
  }))

  return (
    <div className="card">
      <h2 className="section-title"><BarChart2 className="w-5 h-5 text-pitch-400" />Top Influencing Features</h2>
      {data.length === 0 ? (
        <p className="text-slate-500 text-sm">No feature data available.</p>
      ) : (
        <ResponsiveContainer width="100%" height={260}>
          <BarChart data={data} layout="vertical" margin={{ left: 8, right: 24, top: 4, bottom: 4 }}>
            <XAxis type="number" tick={{ fill: '#64748b', fontSize: 11 }}
                   tickFormatter={v => `${(v*100).toFixed(1)}%`} />
            <YAxis type="category" dataKey="name" width={140}
                   tick={{ fill: '#94a3b8', fontSize: 11 }} />
            <Tooltip content={<CustomTooltip />} cursor={{ fill: 'rgba(255,255,255,0.03)' }} />
            <Bar dataKey="importance" radius={[0, 4, 4, 0]}>
              {data.map((_, i) => <Cell key={i} fill={COLOURS[i % COLOURS.length]} />)}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      )}
    </div>
  )
}
