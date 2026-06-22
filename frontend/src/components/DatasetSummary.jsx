import { Database } from 'lucide-react'
import { PieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer } from 'recharts'

const PIE_COLORS = { home_win: '#22c55e', draw: '#f59e0b', away_win: '#3b82f6' }
const PIE_LABEL  = { home_win: 'Home Win', draw: 'Draw', away_win: 'Away Win' }

export default function DatasetSummary({ dataset, summary }) {
  const d = dataset?.data || {}
  const outcome = d.outcome_distribution || {}
  const pieData = Object.entries(outcome).map(([k, v]) => ({
    name: PIE_LABEL[k] || k, value: v, key: k
  }))

  return (
    <div className="card">
      <h2 className="section-title"><Database className="w-5 h-5 text-blue-400" />Dataset Health</h2>

      <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 mb-5">
        {[
          { label: 'Total Loaded',    val: d.total_rows_loaded?.toLocaleString() },
          { label: 'After Cleaning',  val: d.final_usable_rows?.toLocaleString() },
          { label: 'Rows Removed',    val: d.rows_removed?.toLocaleString() },
          { label: 'From',            val: d.date_range?.from },
          { label: 'To',              val: d.date_range?.to },
          { label: 'Unique Teams',    val: d.unique_teams?.toLocaleString() },
        ].map(({ label, val }) => (
          <div key={label} className="card-sm">
            <p className="label mb-1">{label}</p>
            <p className="text-sm font-semibold text-slate-200">{val ?? '—'}</p>
          </div>
        ))}
      </div>

      {pieData.length > 0 && (
        <div>
          <p className="label mb-3">Outcome Distribution</p>
          <ResponsiveContainer width="100%" height={180}>
            <PieChart>
              <Pie data={pieData} cx="50%" cy="50%" innerRadius={45} outerRadius={75}
                   paddingAngle={3} dataKey="value">
                {pieData.map((e, i) => <Cell key={i} fill={PIE_COLORS[e.key] || '#64748b'} />)}
              </Pie>
              <Tooltip formatter={(v) => v.toLocaleString()} contentStyle={{ background:'#0d1529',border:'1px solid #334155',borderRadius:'8px' }} />
              <Legend formatter={(val) => <span style={{color:'#94a3b8',fontSize:12}}>{val}</span>} />
            </PieChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  )
}
