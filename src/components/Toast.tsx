import { ToastProps } from '../types'

export default function Toast({ message, type, onClose }: ToastProps) {
  return (
    <div className="fixed bottom-4 right-4 z-50">
      <div className={`rounded-lg px-4 py-3 shadow-lg max-w-sm ${
        type === 'error' 
          ? 'bg-red-50 border border-red-200 text-red-800' 
          : 'bg-emerald-50 border border-emerald-200 text-emerald-800'
      }`}>
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <p className="text-sm font-medium">{message}</p>
          </div>
          <button
            onClick={onClose}
            className="ml-4 flex-shrink-0 text-slate-400 hover:text-slate-600 focus:outline-none focus:text-slate-600"
            aria-label="Close notification"
          >
            <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      </div>
    </div>
  )
}
