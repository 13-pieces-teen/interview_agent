import { useState } from 'react'
import { useOutletContext } from 'react-router-dom'
import { UploadZone } from '../components/UploadZone'
import { ResultsView } from '../components/ResultsView'
import { ExportPanel } from '../components/ExportPanel'
import { ErrorMessage } from '../components/ErrorMessage'
import { BatchProgress } from '../components/BatchProgress'
import { TaskQueue } from '../components/TaskQueue'
import ApiKeyConfig from '../components/ApiKeyConfig'
import { processText, processImages, processBatch, processTextAsync, processImagesAsync } from '../services/api'
import { List } from 'lucide-react'
import type { ProcessResponse } from '../types'

export function HomePage() {
  const { showTaskQueue, isDark } = useOutletContext<{ showTaskQueue: boolean; isDark: boolean }>()
  const [isProcessing, setIsProcessing] = useState(false)
  const [result, setResult] = useState<ProcessResponse | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [batchTaskId, setBatchTaskId] = useState<string | null>(null)
  const [asyncMode, setAsyncMode] = useState(true)

  const handleTextSubmit = async (text: string) => {
    if (asyncMode) {
      try {
        const response = await processTextAsync(text, false, 'both')
        setError(null)
        setResult(null)
        alert(`任务已提交到队列！任务ID: ${response.task_id.substring(0, 8)}...`)
      } catch (err) {
        setError(err instanceof Error ? err.message : '提交任务失败')
      }
    } else {
      setIsProcessing(true)
      setError(null)
      setResult(null)

      try {
        const response = await processText(text, false, 'both')
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
  }

  const handleImagesSubmit = async (files: File[]) => {
    if (asyncMode) {
      try {
        const response = await processImagesAsync(files, false, 'both')
        setError(null)
        setResult(null)
        alert(`任务已提交到队列！将处理 ${response.file_count} 个文件`)
      } catch (err) {
        setError(err instanceof Error ? err.message : '提交任务失败')
      }
    } else {
      setIsProcessing(true)
      setError(null)
      setResult(null)

      try {
        const response = await processImages(files, false, 'both')
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
  }

  const handleBatchSubmit = async (files: File[]) => {
    setIsProcessing(true)
    setError(null)
    setResult(null)
    setBatchTaskId(null)

    try {
      const response = await processBatch(files, false, 'both')
      setBatchTaskId(response.task_id)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to start batch processing')
      setIsProcessing(false)
    }
  }

  const handleBatchComplete = (result: { taskId: string; completedCount: number; failedCount: number }) => {
    setIsProcessing(false)
    setError(null)

    if (result.failedCount > 0) {
      setError(`批量处理完成：${result.completedCount} 个成功，${result.failedCount} 个失败`)
    }

    setTimeout(() => {
      setBatchTaskId(null)
    }, 2000)
  }

  const handleBatchError = (error: string) => {
    setIsProcessing(false)
    setError(error)
    setBatchTaskId(null)
  }

  const handleReset = () => {
    setResult(null)
    setError(null)
  }

  return (
    <div className="max-w-7xl mx-auto px-6 py-12">
      <div className="flex gap-8 items-start">
        {/* Left Sidebar - API Config */}
        <aside className="w-80 flex-shrink-0 sticky top-6">
          <ApiKeyConfig isDark={isDark} />
        </aside>

        {/* Main Content */}
        <main className="flex-1 min-w-0">
          {/* Options */}
          <div className="w-full max-w-3xl mx-auto mb-8 space-y-4">
            {/* Async Mode Toggle */}
            <label className="flex items-start gap-3 cursor-pointer group">
              <input
                type="checkbox"
                checked={asyncMode}
                onChange={(e) => setAsyncMode(e.target.checked)}
                disabled={isProcessing}
                className="mt-0.5 w-4 h-4 text-primary-600 bg-gray-100 dark:bg-gray-800 border-gray-300 dark:border-gray-700 rounded focus:ring-primary-500 focus:ring-2"
              />
              <div className="flex-1">
                <div className="flex items-center gap-2">
                  <List className="w-4 h-4 text-primary-500" />
                  <span className="text-sm font-medium text-gray-900 dark:text-white">
                    异步处理模式（推荐）
                  </span>
                </div>
                <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                  提交后任务在后台处理，您可以继续提交新任务。关闭此选项将等待当前任务完成。
                </p>
              </div>
            </label>
          </div>

          {/* Task Queue Panel */}
          {showTaskQueue && (
            <div className="w-full max-w-3xl mx-auto mb-8">
              <TaskQueue
                onTaskComplete={(taskId, result) => {
                  console.log('Task completed:', taskId, result)
                }}
                autoRefresh={true}
                refreshInterval={3000}
              />
            </div>
          )}

          {/* Upload Zone */}
          {!result && !batchTaskId && (
            <UploadZone
              onTextSubmit={handleTextSubmit}
              onImagesSubmit={handleImagesSubmit}
              onBatchSubmit={handleBatchSubmit}
              isProcessing={isProcessing}
            />
          )}

          {/* Batch Progress */}
          {batchTaskId && (
            <div className="mt-8">
              <BatchProgress
                taskId={batchTaskId}
                onComplete={handleBatchComplete}
                onError={handleBatchError}
              />
            </div>
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
      </div>
    </div>
  )
}
