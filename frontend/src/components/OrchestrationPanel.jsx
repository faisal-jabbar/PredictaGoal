import { Cpu, ExternalLink, Clock } from 'lucide-react'

const DAGS = [
  {
    name:     'predictagoal_daily_pipeline',
    schedule: '0 6 * * *',
    desc:     'Daily at 06:00 UTC — preprocess → features → predict → confidence → explanation → drift → bias',
    tasks:    9,
  },
  {
    name:     'predictagoal_retraining_pipeline',
    schedule: '0 2 * * 0',
    desc:     'Weekly Sunday 02:00 — evaluates drift; retrains + promotes model if PSI ≥ 0.25',
    tasks:    4,
  },
  {
    name:     'predictagoal_monitoring_pipeline',
    schedule: '*/30 * * * *',
    desc:     'Every 30 min — backend health, report freshness, model artifact check',
    tasks:    3,
  },
]

const LINKS = [
  { label: 'FastAPI Docs',  url: 'http://localhost:8000/docs', color: 'text-pitch-400'  },
  { label: 'MLflow UI',     url: 'http://localhost:5000',      color: 'text-blue-400'   },
  { label: 'Airflow UI',    url: 'http://localhost:8081',      color: 'text-amber-400'  },
  { label: 'Prometheus',    url: 'http://localhost:9090',      color: 'text-slate-300'  },
  { label: 'Grafana',       url: 'http://localhost:3000',      color: 'text-pitch-400'  },
]

export default function OrchestrationPanel() {
  return (
    <div className="card">
      <h2 className="section-title">
        <Cpu className="w-5 h-5 text-blue-400" />
        Orchestration &amp; Monitoring
      </h2>

      <div className="grid md:grid-cols-2 gap-6">

        {/* Airflow DAGs */}
        <div>
          <p className="label mb-3">Airflow DAGs</p>
          <div className="space-y-2">
            {DAGS.map(dag => (
              <div key={dag.name} className="p-3 bg-navy-900/60 rounded-lg border border-slate-700/20">
                <div className="flex items-start justify-between gap-2 mb-1.5">
                  <span className="text-xs font-medium text-slate-200 font-mono break-all">{dag.name}</span>
                  <div className="flex gap-1.5 shrink-0">
                    <span className="badge-slate font-mono text-xs"><Clock className="w-2.5 h-2.5" />{dag.schedule}</span>
                    <span className="badge-blue">{dag.tasks}T</span>
                  </div>
                </div>
                <p className="text-xs text-slate-500 leading-relaxed">{dag.desc}</p>
              </div>
            ))}
          </div>
          <p className="text-xs text-slate-600 mt-2">
            Requires <code className="font-mono bg-navy-900 px-1 rounded">apache-airflow</code> or Docker Compose.
            DAG files at <code className="font-mono bg-navy-900 px-1 rounded">airflow/dags/</code>.
          </p>
        </div>

        {/* Monitoring links */}
        <div>
          <p className="label mb-3">Service Links</p>
          <div className="space-y-2">
            {LINKS.map(link => (
              <a key={link.url} href={link.url} target="_blank" rel="noopener noreferrer"
                className="flex items-center justify-between p-3 bg-navy-900/60 rounded-lg border border-slate-700/20 hover:border-slate-600 transition-colors group">
                <span className={`text-sm font-medium ${link.color}`}>{link.label}</span>
                <div className="flex items-center gap-2">
                  <span className="text-xs text-slate-600 font-mono">{link.url.replace('http://', '')}</span>
                  <ExternalLink className="w-3.5 h-3.5 text-slate-600 group-hover:text-slate-400 transition-colors" />
                </div>
              </a>
            ))}
          </div>
          <p className="text-xs text-slate-600 mt-2">
            Links open in a new tab. Services must be running locally or via{' '}
            <code className="font-mono bg-navy-900 px-1 rounded">docker compose up</code>.
          </p>
        </div>

      </div>
    </div>
  )
}
