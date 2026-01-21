import { useEffect, useState } from 'react'
import { getBatchStatus } from '../services/api'
import { CheckCircle, XCircle, Clock, Loader2, FileText, AlertCircle } from 'lucide-react'

interface BatchProgressProps {
  taskId: string
  onComplete?: (result: BatchResult) => void
  onError?: (error: string) => void
}

interface BatchResult {
  taskId: string
  completedCount: number
  failedCount: number
  successfulExperiences: string[]
}

interface SubTask {
  id: string
  file_name: string
  status: string
  error: string | null
  experience_id: string | null
  started_at: string | null
  completed_at: string | null
  processing_time: number
}

interface BatchStatus {
  id: string
  total_files: number
  status: string
  current_index: number
  completed_count: number
  failed_count: number
  sub_tasks: SubTask[]
}

export function BatchProgress({ taskId, onComplete, onError }: BatchProgressProps) {
  const [batchStatus, setBatchStatus] = useState<BatchStatus | null>(null)
  const [isPolling, setIsPolling] = useState(true)

  useEffect(() => {
    let pollInterval: NodeJS.Timeout

    const pollStatus = async () => {
      try {
        const status = await getBatchStatus(taskId)
        setBatchStatus(status)

        // Stop polling if completed, failed, or cancelled
        if (['completed', 'failed', 'cancelled'].includes(status.status)) {
          setIsPolling(false)

          if (status.status === 'completed' && onComplete) {
            const successfulExperiences = status.sub_tasks
              .filter(st => st.experience_id)
              .map(st => st.experience_id!)

            onComplete({
              taskId: status.id,
              completedCount: status.completed_count,
              failedCount: status.failed_count,
              successfulExperiences,
            })
          } else if (status.status === 'failed' && onError) {
            onError('Batch processing failed')
          }
        }
      } catch (error) {
        console.error('Error polling batch status:', error)
        if (onError) {
          onError(error instanceof Error ? error.message : 'Unknown error')
        }
        setIsPolling(false)
      }
    }

    // Initial poll
    pollStatus()

    // Set up polling interval (every 2 seconds)
    if (isPolling) {
      pollInterval = setInterval(pollStatus, 2000)
    }

    return () => {
      if (pollInterval) {
        clearInterval(pollInterval)
      }
    }
  }, [taskId, isPolling, onComplete, onError])

  if (!batchStatus) {
    return (
      <div className="flex items-center justify-center py-8">
        <Loader2 className="w-6 h-6 animate-spin text-blue-500" />
        <span className="ml-2 text-gray-600">Loading batch status...</span>
      </div>
    )
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="w-5 h-5 text-green-500" />
      case 'failed':
        return <XCircle className="w-5 h-5 text-red-500" />
      case 'processing':
        return <Loader2 className="w-5 h-5 animate-spin text-blue-500" />
      case 'pending':
        return <Clock className="w-5 h-5 text-gray-400" />
      default:
        return <FileText className="w-5 h-5 text-gray-400" />
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'text-green-600'
      case 'failed':
        return 'text-red-600'
      case 'processing':
        return 'text-blue-600'
      case 'pending':
        return 'text-gray-500'
      default:
        return 'text-gray-600'
    }
  }

  const progressPercent = batchStatus.total_files > 0
    ? Math.round(((batchStatus.completed_count + batchStatus.failed_count) / batchStatus.total_files) * 100)
    : 0

  return (
    <div className="bg-white rounded-lg shadow-md p-6 space-y-6">
      {/* Overall Progress */}
      <div>
        <div className="flex items-center justify-between mb-2">
          <h3 className="text-lg font-semibold text-gray-800">批量处理进度</h3>
          <span className={`text-sm font-medium ${getStatusColor(batchStatus.status)}`}>
            {batchStatus.status.toUpperCase()}
          </span>
        </div>

        {/* Progress Bar */}
        <div className="w-full bg-gray-200 rounded-full h-3 mb-4">
          <div
            className="bg-blue-500 h-3 rounded-full transition-all duration-300"
            style={{ width: `${progressPercent}%` }}
          />
        </div>

        {/* Stats */}
        <div className="grid grid-cols-3 gap-4 text-center">
          <div className="bg-gray-50 rounded-lg p-3">
            <div className="text-2xl font-bold text-gray-800">{batchStatus.total_files}</div>
            <div className="text-sm text-gray-600">总文件数</div>
          </div>
          <div className="bg-green-50 rounded-lg p-3">
            <div className="text-2xl font-bold text-green-600">{batchStatus.completed_count}</div>
            <div className="text-sm text-gray-600">已完成</div>
          </div>
          <div className="bg-red-50 rounded-lg p-3">
            <div className="text-2xl font-bold text-red-600">{batchStatus.failed_count}</div>
            <div className="text-sm text-gray-600">失败</div>
          </div>
        </div>
      </div>

      {/* Sub-tasks List */}
      <div>
        <h4 className="text-md font-semibold text-gray-700 mb-3">文件处理详情</h4>
        <div className="space-y-2 max-h-96 overflow-y-auto">
          {batchStatus.sub_tasks.map((subTask, index) => (
            <div
              key={subTask.id}
              className={`flex items-start justify-between p-3 rounded-lg border ${
                subTask.status === 'processing'
                  ? 'border-blue-300 bg-blue-50'
                  : subTask.status === 'completed'
                  ? 'border-green-200 bg-green-50'
                  : subTask.status === 'failed'
                  ? 'border-red-200 bg-red-50'
                  : 'border-gray-200 bg-gray-50'
              }`}
            >
              <div className="flex items-start space-x-3 flex-1 min-w-0">
                <div className="flex-shrink-0 mt-0.5">{getStatusIcon(subTask.status)}</div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center space-x-2">
                    <span className="text-sm font-medium text-gray-700">#{index + 1}</span>
                    <span className="text-sm text-gray-800 truncate" title={subTask.file_name}>
                      {subTask.file_name}
                    </span>
                  </div>
                  {subTask.error && (
                    <div className="flex items-start space-x-1 mt-1">
                      <AlertCircle className="w-4 h-4 text-red-500 flex-shrink-0 mt-0.5" />
                      <span className="text-xs text-red-600">{subTask.error}</span>
                    </div>
                  )}
                  {subTask.processing_time > 0 && (
                    <span className="text-xs text-gray-500 mt-1 block">
                      处理耗时: {subTask.processing_time.toFixed(2)}s
                    </span>
                  )}
                </div>
              </div>
              <span className={`text-xs font-medium ml-2 flex-shrink-0 ${getStatusColor(subTask.status)}`}>
                {subTask.status === 'completed'
                  ? '完成'
                  : subTask.status === 'processing'
                  ? '处理中'
                  : subTask.status === 'failed'
                  ? '失败'
                  : '等待中'}
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* Current Processing Info */}
      {batchStatus.status === 'processing' && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="flex items-center space-x-2">
            <Loader2 className="w-5 h-5 animate-spin text-blue-500" />
            <span className="text-sm text-blue-800">
              正在处理第 {batchStatus.current_index + 1} 个文件，共 {batchStatus.total_files} 个...
            </span>
          </div>
        </div>
      )}
    </div>
  )
}
