import { useState } from 'react'
import { Bot, Send, ChevronRight } from 'lucide-react'
import * as api from '../api/client.js'
import LoadingState from './LoadingState.jsx'

const INTENT_BADGE = {
  latest_prediction:      'badge-green',
  explain_prediction:     'badge-blue',
  model_accuracy:         'badge-blue',
  drift_status:           'badge-amber',
  bias_fairness:          'badge-amber',
  retraining_status:      'badge-amber',
  provider_status:        'badge-slate',
  audit_trail:            'badge-slate',
  system_health:          'badge-blue',
  dataset_summary:        'badge-blue',
  confidence_explanation: 'badge-blue',
  context_availability:   'badge-slate',
  how_to_run:             'badge-slate',
  model_limitations:      'badge-amber',
}

const EXAMPLES = [
  'What did the model predict?',
  'How accurate is the model?',
  'Is there data drift?',
  'What is the retraining status?',
  'Explain model limitations',
]

export default function AgentQueryPanel() {
  const [query, setQuery]   = useState('')
  const [loading, setLoad]  = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError]   = useState(null)

  const submit = async () => {
    const q = query.trim()
    if (!q) return
    setLoad(true); setResult(null); setError(null)
    try {
      setResult(await api.postAgentQuery(q))
    } catch {
      setError('Agent query failed. Is the backend running?')
    } finally {
      setLoad(false)
    }
  }

  const onKey = e => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); submit() } }

  return (
    <div className="card">
      <h2 className="section-title">
        <Bot className="w-5 h-5 text-blue-400" />
        Conversational Agent
      </h2>

      <div className="flex gap-2 mb-3">
        <input
          type="text"
          value={query}
          onChange={e => setQuery(e.target.value)}
          onKeyDown={onKey}
          placeholder="Ask a question about the model, predictions, drift, or system status…"
          className="flex-1 bg-navy-900 border border-slate-700 rounded-lg px-4 py-2.5 text-sm text-slate-100 placeholder-slate-600 focus:outline-none focus:border-blue-500 transition-colors"
        />
        <button
          onClick={submit}
          disabled={loading || !query.trim()}
          className="flex items-center gap-2 px-4 py-2.5 bg-blue-600 hover:bg-blue-500 disabled:bg-slate-700 disabled:text-slate-500 text-white text-sm font-medium rounded-lg transition-colors"
        >
          <Send className="w-4 h-4" />
          Ask
        </button>
      </div>

      <div className="flex flex-wrap gap-1.5 mb-4">
        <span className="text-xs text-slate-600 self-center">Try:</span>
        {EXAMPLES.map(q => (
          <button key={q} onClick={() => setQuery(q)}
            className="text-xs text-slate-500 hover:text-slate-300 bg-navy-900/60 hover:bg-navy-700 border border-slate-700/50 px-2 py-1 rounded-md transition-colors">
            {q}
          </button>
        ))}
      </div>

      {loading && <LoadingState label="Agent thinking…" />}

      {error && (
        <div className="p-3 bg-danger-500/10 border border-danger-500/30 rounded-lg text-sm text-danger-300">
          {error}
        </div>
      )}

      {result && (
        <div className="space-y-3">
          <div className="flex flex-wrap gap-2 items-center">
            <span className={INTENT_BADGE[result.intent] || 'badge-slate'}>
              {result.intent?.replace(/_/g, ' ')}
            </span>
            {result.confidence != null && (
              <span className="text-xs text-slate-500">
                Confidence: {(result.confidence * 100).toFixed(0)}%
              </span>
            )}
            {result.status === 'not_available' && (
              <span className="badge-slate">Not available</span>
            )}
          </div>

          <div className={`p-4 rounded-xl border text-sm leading-relaxed whitespace-pre-wrap ${
            result.status === 'not_available'
              ? 'bg-slate-800/40 border-slate-700/40 text-slate-500'
              : 'bg-navy-900/60 border-slate-700/40 text-slate-200'
          }`}>
            {result.answer}
          </div>

          {result.sources?.length > 0 && (
            <div className="flex flex-wrap gap-2 items-center">
              <span className="text-xs text-slate-600">Sources:</span>
              {result.sources.map((s, i) => (
                <span key={i} className="flex items-center gap-1 text-xs text-slate-500">
                  <ChevronRight className="w-3 h-3" />{s}
                </span>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  )
}
