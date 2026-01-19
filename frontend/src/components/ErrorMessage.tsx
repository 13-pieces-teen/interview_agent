import { AlertCircle } from 'lucide-react'

interface ErrorMessageProps {
  message: string
  onDismiss?: () => void
}

export const ErrorMessage = ({ message, onDismiss }: ErrorMessageProps) => {
  return (
    <div className="w-full max-w-4xl mx-auto">
      <div className="bg-red-900/20 border border-red-700 rounded-lg p-4 flex items-start gap-3">
        <AlertCircle className="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" />
        <div className="flex-1">
          <h4 className="text-red-400 font-medium mb-1">Error Processing Interview</h4>
          <p className="text-red-300 text-sm">{message}</p>
        </div>
        {onDismiss && (
          <button
            onClick={onDismiss}
            className="text-red-400 hover:text-red-300 transition-colors"
          >
            ✕
          </button>
        )}
      </div>
    </div>
  )
}
