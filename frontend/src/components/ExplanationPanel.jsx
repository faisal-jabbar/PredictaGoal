import { Lightbulb, Cpu } from 'lucide-react'

const METHOD_BADGE = {
  shap:                  { cls: 'badge-green', label: 'SHAP Explainer' },
  rf_feature_importance: { cls: 'badge-blue',  label: 'Feature Importance' },
  rule_based:            { cls: 'badge-slate', label: 'Rule-Based' },
}

export default function ExplanationPanel({ data }) {
  if (!data?.data) return null
  const d = data.data
  const mb = METHOD_BADGE[d.method] || { cls: 'badge-slate', label: d.method }

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-4">
        <h2 className="section-title mb-0"><Lightbulb className="w-5 h-5 text-amber-400" />Why This Prediction?</h2>
        <span className={mb.cls}><Cpu className="w-3 h-3" />{mb.label}</span>
      </div>

      <p className="text-sm text-slate-300 leading-relaxed mb-5 border-l-2 border-pitch-500 pl-4">
        {d.explanation_text || 'Explanation not available.'}
      </p>

      {d.top_features?.length > 0 && (
        <div>
          <p className="label mb-3">Top Contributing Features</p>
          <div className="space-y-2">
            {d.top_features.slice(0, 6).map((f, i) => (
              <div key={i} className="flex items-center gap-3">
                <span className="text-xs text-slate-500 w-4">{i + 1}</span>
                <div className="flex-1">
                  <div className="flex justify-between mb-0.5">
                    <span className="text-xs text-slate-300">{f.display_name || f.feature}</span>
                    <span className="text-xs font-mono text-pitch-400">{(f.importance * 100).toFixed(2)}%</span>
                  </div>
                  <div className="h-1.5 bg-navy-900 rounded-full overflow-hidden">
                    <div className="h-full bg-pitch-500 rounded-full"
                         style={{ width: `${Math.min(f.importance * 300, 100)}%` }} />
                  </div>
                </div>
                <span className="text-xs text-slate-600 w-16 text-right font-mono">
                  {typeof f.feature_value === 'number' ? f.feature_value.toFixed(2) : '—'}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      <p className="mt-4 text-xs text-slate-600 border-t border-slate-700/50 pt-3">
        This is an analytical estimate based on historical statistics. Not financial or betting advice.
      </p>
    </div>
  )
}
