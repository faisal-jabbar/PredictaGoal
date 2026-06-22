import { useState, useEffect } from 'react'
import { Activity, Database, Brain, Target, Calendar, Layers, Wifi, WifiOff } from 'lucide-react'

import * as api from './api/client.js'
import KpiCard            from './components/KpiCard.jsx'
import PredictionCard     from './components/PredictionCard.jsx'
import ConfidenceGauge    from './components/ConfidenceGauge.jsx'
import ExplanationPanel   from './components/ExplanationPanel.jsx'
import FeatureImportanceChart from './components/FeatureImportanceChart.jsx'
import DatasetSummary     from './components/DatasetSummary.jsx'
import ModelSummary       from './components/ModelSummary.jsx'
import DriftReportPanel   from './components/DriftReportPanel.jsx'
import BiasReportPanel    from './components/BiasReportPanel.jsx'
import ContextualPanel    from './components/ContextualPanel.jsx'
import LoadingState       from './components/LoadingState.jsx'
import ErrorState         from './components/ErrorState.jsx'

function useAsync(fn, deps = []) {
  const [state, setState] = useState({ data: null, loading: true, error: null })
  useEffect(() => {
    setState(s => ({ ...s, loading: true, error: null }))
    fn().then(data => setState({ data, loading: false, error: null }))
       .catch(err  => setState({ data: null, loading: false, error: err.message }))
  }, deps)
  return state
}

export default function App() {
  const health      = useAsync(api.fetchHealth)
  const summary     = useAsync(api.fetchSummary)
  const prediction  = useAsync(api.fetchPrediction)
  const dataset     = useAsync(api.fetchDataset)
  const model       = useAsync(api.fetchModel)
  const confidence  = useAsync(api.fetchConfidence)
  const explanation = useAsync(api.fetchExplanation)
  const drift       = useAsync(api.fetchDrift)
  const bias        = useAsync(api.fetchBias)
  const contextual  = useAsync(api.fetchContextual)

  const apiOnline = !health.error
  const fbStatus  = health.data?.firebase || 'unknown'
  const now       = new Date().toLocaleString('en-GB', { dateStyle: 'medium', timeStyle: 'short' })

  const s = summary.data || {}
  const p = prediction.data || {}

  return (
    <div className="min-h-screen">
      {/* ── NAV ── */}
      <header className="sticky top-0 z-50 border-b border-slate-700/40 bg-navy-900/90 backdrop-blur-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 py-4 flex items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <span className="text-2xl">⚽</span>
            <div>
              <h1 className="text-lg font-bold text-white leading-tight">PredictaGoal</h1>
              <p className="text-xs text-slate-500 leading-tight">AI Football Match Prediction Agent</p>
            </div>
          </div>
          <div className="hidden sm:flex items-center gap-2 flex-wrap justify-end">
            <span className="badge-blue text-xs">Phase 02 Intelligence Dashboard</span>
            {apiOnline
              ? <span className="badge-green"><Wifi className="w-3 h-3" />API Online</span>
              : <span className="badge-red"><WifiOff className="w-3 h-3" />API Offline</span>
            }
            {fbStatus.includes('connected')
              ? <span className="badge-green">Firestore Connected</span>
              : <span className="badge-amber">Local Fallback</span>
            }
            <span className="text-xs text-slate-600">{now}</span>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 py-8 space-y-8">

        {!apiOnline && (
          <div className="bg-danger-500/10 border border-danger-500/30 rounded-xl p-4 text-sm text-danger-300">
            <strong>Backend offline.</strong> Start with: <code className="font-mono text-xs bg-navy-900 px-2 py-0.5 rounded">uvicorn src.api.main:app --reload</code>
          </div>
        )}

        {/* ── KPI CARDS ── */}
        <section>
          <p className="label mb-4">System Overview</p>
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
            <KpiCard title="Total Matches"    value={s.dataset_rows?.toLocaleString()} subtitle="Raw dataset rows"      icon={Database} accent="blue"  />
            <KpiCard title="After Cleaning"   value={s.cleaned_rows?.toLocaleString()} subtitle="Usable for training"   icon={Database} accent="green" />
            <KpiCard title="Model Accuracy"   value={s.model_accuracy ? `${(s.model_accuracy*100).toFixed(1)}%` : '—'} subtitle="Time-based test split" icon={Brain}  accent="green" />
            <KpiCard title="Features"         value={s.features_count ?? 14}           subtitle="Engineered signals"    icon={Layers}  accent="blue"  />
            <KpiCard title="Data From"        value={s.date_range_from}                subtitle="Dataset start"         icon={Calendar} accent="slate" />
            <KpiCard title="Prediction"       value={p.prediction?.replace('_',' ')?.replace(/\b\w/g,c=>c.toUpperCase())} subtitle={`${p.home_team} vs ${p.away_team}`} icon={Target} accent="amber" />
          </div>
        </section>

        {/* ── PREDICTION + CONFIDENCE ── */}
        <section className="grid lg:grid-cols-2 gap-6">
          <div>
            {prediction.loading ? <LoadingState label="Loading prediction..." /> :
             prediction.error   ? <ErrorState message="Prediction unavailable." hint="Is the backend running?" /> :
             <PredictionCard prediction={prediction.data} />}
          </div>
          <div>
            {confidence.loading ? <LoadingState label="Loading confidence..." /> :
             confidence.error   ? <ErrorState message="Confidence report unavailable." hint="Run scripts/10_calculate_confidence.py" /> :
             <ConfidenceGauge data={confidence.data} />}
          </div>
        </section>

        {/* ── EXPLANATION + FEATURE IMPORTANCE ── */}
        <section className="grid lg:grid-cols-2 gap-6">
          <div>
            {explanation.loading ? <LoadingState label="Loading explanation..." /> :
             explanation.error   ? <ErrorState message="Explanation unavailable." hint="Run scripts/09_generate_explanations.py" /> :
             <ExplanationPanel data={explanation.data} />}
          </div>
          <div>
            {explanation.loading ? <LoadingState /> :
             explanation.error   ? <ErrorState message="Feature data unavailable." /> :
             <FeatureImportanceChart features={explanation.data?.data?.top_features || []} />}
          </div>
        </section>

        {/* ── DATASET + MODEL ── */}
        <section className="grid lg:grid-cols-2 gap-6">
          <div>
            {dataset.loading ? <LoadingState label="Loading dataset report..." /> :
             dataset.error   ? <ErrorState message="Dataset report unavailable." hint="Run scripts/05_preprocess_data.py" /> :
             <DatasetSummary dataset={dataset.data} summary={summary.data} />}
          </div>
          <div>
            {model.loading  ? <LoadingState label="Loading model report..." /> :
             model.error    ? <ErrorState message="Model report unavailable." hint="Run scripts/07_train_model.py" /> :
             <ModelSummary model={model.data} />}
          </div>
        </section>

        {/* ── DRIFT + BIAS ── */}
        <section className="grid lg:grid-cols-2 gap-6">
          <div>
            {drift.loading  ? <LoadingState label="Loading drift report..." /> :
             drift.error    ? <ErrorState message="Drift report unavailable." hint="Run scripts/11_generate_drift_report.py" /> :
             <DriftReportPanel data={drift.data} />}
          </div>
          <div>
            {bias.loading   ? <LoadingState label="Loading bias report..." /> :
             bias.error     ? <ErrorState message="Bias report unavailable." hint="Run scripts/12_generate_bias_report.py" /> :
             <BiasReportPanel data={bias.data} />}
          </div>
        </section>

        {/* ── CONTEXTUAL ── */}
        <section>
          {contextual.loading ? <LoadingState label="Loading contextual data..." /> :
           contextual.error   ? <ErrorState message="Contextual report unavailable." hint="Run scripts/09_generate_explanations.py (generates contextual report too)" /> :
           <ContextualPanel data={contextual.data} />}
        </section>

        {/* ── FOOTER ── */}
        <footer className="border-t border-slate-700/40 pt-6 text-center">
          <p className="text-xs text-slate-600">
            PredictaGoal — Phase 02 Intelligence Dashboard · Built with React + FastAPI + Firebase ·
            For analytical purposes only · Not financial or betting advice
          </p>
        </footer>
      </main>
    </div>
  )
}
