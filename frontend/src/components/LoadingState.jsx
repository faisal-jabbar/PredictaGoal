export default function LoadingState({ label = 'Loading...' }) {
  return (
    <div className="flex flex-col items-center justify-center py-12 gap-3 text-slate-500">
      <div className="w-8 h-8 border-2 border-slate-600 border-t-pitch-500 rounded-full animate-spin" />
      <span className="text-sm">{label}</span>
    </div>
  )
}
