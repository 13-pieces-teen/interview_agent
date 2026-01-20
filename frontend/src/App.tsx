import { useState } from 'react'
import { Brain, Sparkles, History, Sun, Moon } from 'lucide-react'
import { UploadZone } from './components/UploadZone'
import { ResultsView } from './components/ResultsView'
import { ExportPanel } from './components/ExportPanel'
import { ErrorMessage } from './components/ErrorMessage'
import { ExperienceGallery } from './components/ExperienceGallery'
import { processText, processImages } from './services/api'
import { useTheme } from './contexts/ThemeContext'
import type { ProcessResponse } from './types'

function App() {
  const [isProcessing, setIsProcessing] = useState(false)
  const [result, setResult] = useState<ProcessResponse | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [generateAnswers, setGenerateAnswers] = useState(false)
  const [showGallery, setShowGallery] = useState(false)
  const { theme, toggleTheme } = useTheme()

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

  // Show gallery if requested
  if (showGallery) {
    return <ExperienceGallery onClose={() => setShowGallery(false)} />
  }

  return (
    <div className="min-h-screen bg-white dark:bg-gray-950 transition-colors">
      {/* Header */}
      <header className="border-b border-gray-100 dark:border-gray-800 transition-colors">
        <div className="max-w-5xl mx-auto px-6 py-8">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="w-10 h-10 bg-primary-600 rounded-xl flex items-center justify-center">
                <Brain className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-semibold text-gray-900 dark:text-white">Interview Agent</h1>
              </div>
            </div>

            {/* Action Buttons */}
            <div className="flex items-center gap-2">
              {/* Theme Toggle */}
              <button
                onClick={toggleTheme}
                className="p-2 text-gray-500 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white transition-colors"
                title={theme === 'dark' ? '切换到浅色模式' : '切换到深色模式'}
              >
                {theme === 'dark' ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
              </button>

              {/* History Button */}
              <button
                onClick={() => setShowGallery(true)}
                className="flex items-center gap-2 px-4 py-2 text-gray-700 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white transition-colors"
              >
                <History className="w-4 h-4" />
                <span className="text-sm font-medium">历史记录</span>
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-5xl mx-auto px-6 py-12">
        {/* Options */}
        <div className="w-full max-w-3xl mx-auto mb-8">
          <label className="flex items-start gap-3 cursor-pointer group">
            <input
              type="checkbox"
              checked={generateAnswers}
              onChange={(e) => setGenerateAnswers(e.target.checked)}
              disabled={isProcessing}
              className="mt-0.5 w-4 h-4 text-primary-600 bg-gray-100 dark:bg-gray-800 border-gray-300 dark:border-gray-700 rounded focus:ring-primary-500 focus:ring-2"
            />
            <div className="flex-1">
              <div className="flex items-center gap-2">
                <Sparkles className="w-4 h-4 text-primary-500" />
                <span className="text-sm font-medium text-gray-900 dark:text-white">
                  AI 自动生成答案
                </span>
              </div>
              <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                为没有回答的面试问题智能生成建议答案
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
          <div className="mt-8">
            <ErrorMessage message={error} onDismiss={() => setError(null)} />
          </div>
        )}

        {/* Results */}
        {result && result.success && result.experience && (
          <div className="space-y-8">
            <ResultsView
              experience={result.experience}
              processingTime={result.processing_time}
            />

            <ExportPanel outputFiles={result.output_files} />

            <div className="w-full max-w-3xl mx-auto flex justify-center pt-4">
              <button
                onClick={handleReset}
                className="px-6 py-2.5 text-sm font-medium text-gray-700 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white border border-gray-200 dark:border-gray-700 rounded-lg hover:border-gray-300 dark:hover:border-gray-600 transition-colors"
              >
                处理新的面经
              </button>
            </div>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="mt-20 py-8 border-t border-gray-100 dark:border-gray-800">
        <div className="max-w-5xl mx-auto px-6 text-center text-gray-400 dark:text-gray-600 text-xs">
          <p>Powered by DeepSeek-V3.2 and GLM-4.6V</p>
        </div>
      </footer>
    </div>
  )
}

export default App
