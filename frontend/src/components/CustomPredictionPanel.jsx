import { useState } from 'react'
import { Target, AlertCircle } from 'lucide-react'
import * as api from '../api/client.js'
import ProbabilityBars from './ProbabilityBars.jsx'
import LoadingState from './LoadingState.jsx'

const TOURNAMENTS = [
  'Friendly', 'FIFA World Cup', 'UEFA Euro', 'Copa America',
  'AFC Asian Cup', 'Africa Cup of Nations', 'Qualification',
]

const TIER_BADGE = { HIGH: 'badge-green', MEDIUM: 'badge-blue', LOW: 'badge-amber', UNRELIABLE: 'badge-red' }
const PRED_BADGE = { home_win: 'badge-green', draw: 'badge-amber', away_win: 'badge-blue' }
const PRED_LABEL = { home_win: 'Home Win', draw: 'Draw', away_win: 'Away Win' }

function validate(form) {
  const e = {}
  if (!form.home_team.trim()) e.home_team = 'Required'
  if (!form.away_team.trim()) e.away_team = 'Required'
  if (form.home_team.trim() && form.away_team.trim() &&
      form.home_team.trim().toLowerCase() === form.away_team.trim().toLowerCase())
    e.away_team = 'Must differ from home team'
  if (!form.match_date) e.match_date = 'Required'
  else if (!/^\d{4}-\d{2}-\d{2}$/.test(form.match_date)) e.match_date = 'Use YYYY-MM-DD'
  return e
}

function Field({ label, error, children }) {
  return (
    <div>
      <label className="label mb-1.5 block">{label}</label>
      {children}
      {error && <p className="text-xs text-danger-400 mt-1">{error}</p>}
    </div>
  )
}

export default function CustomPredictionPanel() {
  const [form, setForm] = useState({
    home_team: '', away_team: '', match_date: '', tournament: 'Friendly', neutral_venue: false,
  })
  const [errors, setErrors]   = useState({})
  const [loading, setLoading] = useState(false)
  const [result, setResult]   = useState(null)
  const [apiError, setApiErr] = useState(null)

  const set = (k, v) => { setForm(f => ({ ...f, [k]: v })); setErrors(e => ({ ...e, [k]: null })) }

  const inputCls = key =>
    `w-full bg-navy-900 border ${errors[key] ? 'border-danger-500' : 'border-slate-700'} rounded-lg px-3 py-2.5 text-sm text-slate-100 placeholder-slate-600 focus:outline-none focus:border-pitch-500 transition-colors`

  const submit = async () => {
    const errs = validate(form)
    setErrors(errs)
    if (Object.keys(errs).length) return
    setLoading(true); setResult(null); setApiErr(null)
    try {
      setResult(await api.postCustomPrediction(form))
    } catch (e) {
      setApiErr(e.response?.data?.detail || 'Prediction failed. Is the backend running with processed data?')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="card">
      <h2 className="section-title">
        <Target className="w-5 h-5 text-pitch-400" />
        Custom Match Prediction
      </h2>

      <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4 mb-4">
        <Field label="Home Team" error={errors.home_team}>
          <input type="text" value={form.home_team} onChange={e => set('home_team', e.target.value)}
            placeholder="e.g. Brazil" className={inputCls('home_team')} />
        </Field>

        <Field label="Away Team" error={errors.away_team}>
          <input type="text" value={form.away_team} onChange={e => set('away_team', e.target.value)}
            placeholder="e.g. Argentina" className={inputCls('away_team')} />
        </Field>

        <Field label="Match Date" error={errors.match_date}>
          <input type="date" value={form.match_date} onChange={e => set('match_date', e.target.value)}
            className={inputCls('match_date')} />
        </Field>

        <Field label="Tournament">
          <select value={form.tournament} onChange={e => set('tournament', e.target.value)}
            className="w-full bg-navy-900 border border-slate-700 rounded-lg px-3 py-2.5 text-sm text-slate-100 focus:outline-none focus:border-pitch-500 transition-colors">
            {TOURNAMENTS.map(t => <option key={t} value={t}>{t}</option>)}
          </select>
        </Field>

        <div className="flex items-center gap-3 pt-5">
          <input type="checkbox" id="neutral" checked={form.neutral_venue}
            onChange={e => set('neutral_venue', e.target.checked)}
            className="w-4 h-4 rounded accent-pitch-500" />
          <label htmlFor="neutral" className="text-sm text-slate-300 cursor-pointer select-none">
            Neutral Venue
          </label>
        </div>

        <div className="flex items-end">
          <button onClick={submit} disabled={loading}
            className="w-full py-2.5 bg-pitch-500 hover:bg-pitch-400 disabled:bg-slate-700 disabled:text-slate-500 text-navy-900 font-semibold text-sm rounded-lg transition-colors">
            {loading ? 'Predicting…' : 'Predict Match'}
          </button>
        </div>
      </div>

      {loading && <LoadingState label="Running prediction…" />}

      {apiError && (
        <div className="flex items-start gap-2 p-3 bg-danger-500/10 border border-danger-500/30 rounded-lg text-sm text-danger-300 mb-2">
          <AlertCircle className="w-4 h-4 mt-0.5 shrink-0" />{apiError}
        </div>
      )}

      {result && (
        <div className="border-t border-slate-700/50 pt-5 space-y-4">
          <div className="flex flex-wrap items-center justify-between gap-2">
            <p className="text-sm font-semibold text-slate-200">
              {result.home_team} vs {result.away_team}
            </p>
            <div className="flex flex-wrap gap-2">
              <span className={PRED_BADGE[result.prediction] || 'badge-slate'}>
                {PRED_LABEL[result.prediction] || result.prediction}
              </span>
              {result.confidence_tier && (
                <span className={TIER_BADGE[result.confidence_tier] || 'badge-slate'}>
                  {result.confidence_tier} Confidence
                </span>
              )}
              {result.pcs != null && (
                <span className="badge-slate">PCS {(result.pcs * 100).toFixed(1)}%</span>
              )}
            </div>
          </div>

          <ProbabilityBars probabilities={result.probabilities} />

          {result.explanation && (
            <p className="text-xs text-slate-400 leading-relaxed bg-navy-900/60 p-3 rounded-lg border border-slate-700/30">
              {result.explanation}
            </p>
          )}

          {result.audit_event_id && (
            <p className="text-xs text-slate-600 font-mono">Audit ID: {result.audit_event_id}</p>
          )}
        </div>
      )}
    </div>
  )
}
