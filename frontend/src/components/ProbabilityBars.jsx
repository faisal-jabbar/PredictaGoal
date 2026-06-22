const COLORS = {
  home_win: { bar: 'bg-pitch-500', text: 'text-pitch-400' },
  draw:     { bar: 'bg-amber-500', text: 'text-amber-400' },
  away_win: { bar: 'bg-blue-500',  text: 'text-blue-400' },
}
const LABELS = { home_win: 'Home Win', draw: 'Draw', away_win: 'Away Win' }

export default function ProbabilityBars({ probabilities = {} }) {
  return (
    <div className="space-y-3">
      {Object.entries(probabilities).map(([key, pct]) => {
        const { bar, text } = COLORS[key] || { bar: 'bg-slate-500', text: 'text-slate-400' }
        return (
          <div key={key}>
            <div className="flex justify-between mb-1">
              <span className="text-sm text-slate-300">{LABELS[key] || key}</span>
              <span className={`text-sm font-semibold ${text}`}>{(pct * 100).toFixed(1)}%</span>
            </div>
            <div className="h-2.5 bg-navy-900 rounded-full overflow-hidden">
              <div className={`h-full ${bar} rounded-full transition-all duration-700`}
                   style={{ width: `${(pct * 100).toFixed(1)}%` }} />
            </div>
          </div>
        )
      })}
    </div>
  )
}
