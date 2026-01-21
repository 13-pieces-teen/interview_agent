import { useState } from 'react'
import { Brain, History, Sun, Moon, List } from 'lucide-react'
import { UploadZone } from './components/UploadZone'
import { ResultsView } from './components/ResultsView'
import { ExportPanel } from './components/ExportPanel'
import { ErrorMessage } from './components/ErrorMessage'
import { ExperienceGallery } from './components/ExperienceGallery'
import { BatchProgress } from './components/BatchProgress'
import { TaskQueue } from './components/TaskQueue'
import { processText, processImages, processBatch, processTextAsync, processImagesAsync } from './services/api'
import { useTheme } from './contexts/ThemeContext'
import type { ProcessResponse } from './types'

function App() {
  const [isProcessing, setIsProcessing] = useState(false)
  const [result, setResult] = useState<ProcessResponse | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [showGallery, setShowGallery] = useState(false)
  const [batchTaskId, setBatchTaskId] = useState<string | null>(null) // 批量任务ID
  const [asyncMode, setAsyncMode] = useState(true) // 异步模式开关（默认开启）
  const [showTaskQueue, setShowTaskQueue] = useState(false) // 任务队列显示开关
  const { theme, toggleTheme } = useTheme()

  const handleTextSubmit = async (text: string) => {
    if (asyncMode) {
      // 异步模式：立即返回，不阻塞
      try {
        const response = await processTextAsync(text, false, 'both')
        // 显示提示信息
        setError(null)
        setResult(null)
        // 可以显示一个toast提示
        alert(`任务已提交到队列！任务ID: ${response.task_id.substring(0, 8)}...`)
      } catch (err) {
        setError(err instanceof Error ? err.message : '提交任务失败')
      }
    } else {
      // 同步模式：等待完成
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
      // 异步模式：立即返回，不阻塞
      try {
        const response = await processImagesAsync(files, false, 'both')
        setError(null)
        setResult(null)
        alert(`任务已提交到队列！将处理 ${response.file_count} 个文件`)
      } catch (err) {
        setError(err instanceof Error ? err.message : '提交任务失败')
      }
    } else {
      // 同步模式：等待完成
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

    // 显示完成信息
    if (result.failedCount > 0) {
      setError(`批量处理完成：${result.completedCount} 个成功，${result.failedCount} 个失败`)
    }

    // 可以选择刷新列表或跳转到历史记录
    setTimeout(() => {
      setBatchTaskId(null)
      setShowGallery(true)
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
              {/* Task Queue Toggle */}
              <button
                onClick={() => setShowTaskQueue(!showTaskQueue)}
                className="flex items-center gap-2 px-4 py-2 text-gray-700 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white transition-colors"
                title="任务队列"
              >
                <List className="w-4 h-4" />
                <span className="text-sm font-medium">任务队列</span>
              </button>

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
                // 可以选择跳转到历史记录或显示通知
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
