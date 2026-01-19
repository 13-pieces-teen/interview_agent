import { useState } from 'react'
import { Brain, Sparkles } from 'lucide-react'
import { UploadZone } from './components/UploadZone'
import { ResultsView } from './components/ResultsView'
import { ExportPanel } from './components/ExportPanel'
import { ErrorMessage } from './components/ErrorMessage'
import { processText, processImages } from './services/api'
import type { ProcessResponse } from './types'

function App() {
  const [isProcessing, setIsProcessing] = useState(false)
  const [result, setResult] = useState<ProcessResponse | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [generateAnswers, setGenerateAnswers] = useState(false)

  const handleTextSubmit = async (text: string) => {
    setIsProcessing(true)
    setError(null)
    setResult(null)

    try {
      const response = await processText(text, generateAnswers, 'both')
      setResult(response)

      if (!response.success) {
        setError(response.error || 'Unknown error occurred')
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to process interview experience')
    } finally {
      setIsProcessing(false)
    }
  }

  const handleImagesSubmit = async (files: File[]) => {
    setIsProcessing(true)
    setError(null)
    setResult(null)

    try {
      const response = await processImages(files, generateAnswers, 'both')
      setResult(response)

      if (!response.success) {
        setError(response.error || 'Unknown error occurred')
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to process interview experience')
    } finally {
      setIsProcessing(false)
    }
  }

  const handleReset = () => {
    setResult(null)
    setError(null)
  }

  return (
    <div className="min-h-screen bg-gray-900">
      {/* Header */}
      <header className="bg-gray-800 border-b border-gray-700">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 bg-primary-600 rounded-lg flex items-center justify-center">
              <Brain className="w-7 h-7 text-white" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-white">Interview Agent</h1>
              <p className="text-gray-400 text-sm">
                AI-powered interview experience processor
              </p>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 py-8">
        {/* Options */}
        <div className="w-full max-w-4xl mx-auto mb-6">
          <label className="flex items-center gap-3 p-4 bg-gray-800 rounded-lg border border-gray-700 cursor-pointer hover:border-primary-500 transition-all">
            <input
              type="checkbox"
              checked={generateAnswers}
              onChange={(e) => setGenerateAnswers(e.target.checked)}
              disabled={isProcessing}
              className="w-5 h-5 text-primary-600 bg-gray-700 border-gray-600 rounded focus:ring-primary-500 focus:ring-2"
            />
            <div className="flex-1">
              <div className="flex items-center gap-2">
                <Sparkles className="w-4 h-4 text-primary-400" />
                <span className="text-white font-medium">
                  Generate AI answers for questions without responses
                </span>
              </div>
              <p className="text-sm text-gray-400 mt-1">
                Use AI to suggest answers for interview questions that don't have responses
              </p>
            </div>
          </label>
        </div>

        {/* Upload Zone */}
        {!result && (
          <UploadZone
            onTextSubmit={handleTextSubmit}
            onImagesSubmit={handleImagesSubmit}
            isProcessing={isProcessing}
          />
        )}

        {/* Error */}
        {error && (
          <div className="mt-6">
            <ErrorMessage message={error} onDismiss={() => setError(null)} />
          </div>
        )}

        {/* Results */}
        {result && result.success && result.experience && (
          <div className="space-y-6">
            <ResultsView
              experience={result.experience}
              processingTime={result.processing_time}
            />

            <ExportPanel outputFiles={result.output_files} />

            <div className="w-full max-w-4xl mx-auto flex justify-center">
              <button
                onClick={handleReset}
                className="px-6 py-3 bg-gray-700 text-white rounded-lg font-medium hover:bg-gray-600 transition-all"
              >
                Process Another Interview
              </button>
            </div>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="mt-12 py-6 border-t border-gray-800">
        <div className="max-w-7xl mx-auto px-4 text-center text-gray-500 text-sm">
          <p>Powered by DeepSeek-V3.2 and GLM-4.6V</p>
        </div>
      </footer>
    </div>
  )
}

export default App
