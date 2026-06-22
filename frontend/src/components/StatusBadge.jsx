export default function StatusBadge({ status, label }) {
  const cls = status === 'ok' || status === 'connected' ? 'badge-green'
            : status === 'warning' ? 'badge-amber'
            : 'badge-red'
  const dot = status === 'ok' || status === 'connected' ? 'bg-pitch-400' : 'bg-amber-400'
  return (
    <span className={cls}>
      <span className={`w-1.5 h-1.5 rounded-full ${dot} animate-pulse`} />
      {label}
    </span>
  )
}
