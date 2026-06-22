import { Trophy, Calendar, MapPin } from 'lucide-react'
import ProbabilityBars from './ProbabilityBars.jsx'

const TIER_BADGE = {
  HIGH:       'badge-green',
  MEDIUM:     'badge-blue',
  LOW:        'badge-amber',
  UNRELIABLE: 'badge-red',
}
const PRED_BADGE = {
  home_win: 'badge-green',
  draw:     'badge-amber',
  away_win: 'badge-blue',
}
const PRED_LABEL = { home_win: 'Home Win', draw: 'Draw', away_win: 'Away Win' }

export default function PredictionCard({ prediction }) {
  if (!prediction) return null
  const { home_team, away_team, match_date, tournament, prediction: pred,
          probabilities, confidence, pcs, confidence_tier, confidence_note } = prediction
  return (
    <div className="card">
      <h2 className="section-title"><Trophy className="w-5 h-5 text-amber-400" />Featured Prediction</h2>

      <div className="flex items-center justify-between mb-6">
        <div className="text-center flex-1">
          <p className="text-2xl font-bold text-white">{home_team}</p>
          <p className="text-xs text-slate-500 mt-1">Home</p>
        </div>
        <div className="text-center px-4">
          <p className="text-slate-500 font-bold text-lg">vs</p>
        </div>
        <div className="text-center flex-1">
          <p className="text-2xl font-bold text-white">{away_team}</p>
          <p className="text-xs text-slate-500 mt-1">Away</p>
        </div>
      </div>

      <div className="flex flex-wrap gap-2 mb-5">
        <span className={PRED_BADGE[pred] || 'badge-slate'}>
          {PRED_LABEL[pred] || pred}
        </span>
        {confidence_tier && (
          <span className={TIER_BADGE[confidence_tier] || 'badge-slate'}>
            {confidence_tier} Confidence
          </span>
        )}
        <span className="badge-slate">{(confidence * 100).toFixed(1)}% leading</span>
      </div>

      <ProbabilityBars probabilities={probabilities} />

      {confidence_note && (
        <p className="mt-4 text-xs text-slate-500 border-t border-slate-700/50 pt-3 leading-relaxed">
          {confidence_note}
        </p>
      )}

      <div className="flex gap-4 mt-4 text-xs text-slate-600">
        {match_date && <span className="flex items-center gap-1"><Calendar className="w-3 h-3" />{match_date}</span>}
        {tournament && <span className="flex items-center gap-1"><MapPin className="w-3 h-3" />{tournament}</span>}
      </div>
    </div>
  )
}
