import { AlertCircle } from 'lucide-react'
export default function ErrorState({ message = 'Unable to load data.', hint }) {
  return (
    <div className="flex flex-col items-center justify-center py-10 gap-2 text-slate-500">
      <AlertCircle className="w-8 h-8 text-danger-400" />
      <p className="text-sm text-slate-400">{message}</p>
      {hint && <p className="text-xs text-slate-600">{hint}</p>}
    </div>
  )
}
