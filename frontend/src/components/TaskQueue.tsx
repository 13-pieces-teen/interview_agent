import { useEffect, useState } from 'react'
import { CheckCircle, XCircle, Clock, Loader2, FileText, List, RefreshCw } from 'lucide-react'
import { getAsyncTaskStatus, listAsyncTasks } from '../services/api'

interface TaskQueueProps {
  onTaskComplete?: (taskId: string, result: any) => void
  autoRefresh?: boolean
  refreshInterval?: number
}

interface AsyncTask {
  id: string
  type: string
  status: string
  created_at: string
  started_at: string | null
  completed_at: string | null
  processing_time: number
  error: string | null
  metadata: {
    file_names?: string[]
    file_count?: number
    validation_score?: number
  }
}

export function TaskQueue({
  onTaskComplete,
  autoRefresh = true,
  refreshInterval = 3000
}: TaskQueueProps) {
  const [tasks, setTasks] = useState<AsyncTask[]>([])
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState<string>('all')

  useEffect(() => {
    loadTasks()

    if (autoRefresh) {
      const interval = setInterval(loadTasks, refreshInterval)
      return () => clearInterval(interval)
    }
  }, [filter, autoRefresh, refreshInterval])

  const loadTasks = async () => {
    try {
      const statusFilter = filter === 'all' ? undefined : filter
      const response = await listAsyncTasks(statusFilter)
      setTasks(response.tasks)
      setLoading(false)

      // 检查是否有任务刚完成
      if (onTaskComplete) {
        response.tasks.forEach((task: AsyncTask) => {
          if (task.status === 'completed') {
            onTaskComplete(task.id, task)
          }
        })
      }
    } catch (error) {
      console.error('Failed to load tasks:', error)
      setLoading(false)
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="w-4 h-4 text-green-500" />
      case 'failed':
        return <XCircle className="w-4 h-4 text-red-500" />
      case 'processing':
        return <Loader2 className="w-4 h-4 animate-spin text-blue-500" />
      case 'queued':
        return <Clock className="w-4 h-4 text-gray-400" />
      default:
        return <FileText className="w-4 h-4 text-gray-400" />
    }
  }

  const getStatusText = (status: string) => {
    const statusMap: { [key: string]: string } = {
      queued: '排队中',
      processing: '处理中',
      completed: '已完成',
      failed: '失败'
    }
    return statusMap[status] || status
  }

  const getTaskTypeText = (type: string) => {
    const typeMap: { [key: string]: string } = {
      text: '文本',
      image: '图片',
      batch: '批量'
    }
    return typeMap[type] || type
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'bg-green-50 border-green-200'
      case 'failed':
        return 'bg-red-50 border-red-200'
      case 'processing':
        return 'bg-blue-50 border-blue-200'
      case 'queued':
        return 'bg-gray-50 border-gray-200'
      default:
        return 'bg-gray-50 border-gray-200'
    }
  }

  const getTimeAgo = (timestamp: string) => {
    const now = new Date()
    const then = new Date(timestamp)
    const diffMs = now.getTime() - then.getTime()
    const diffSecs = Math.floor(diffMs / 1000)

    if (diffSecs < 60) return `${diffSecs}秒前`
    if (diffSecs < 3600) return `${Math.floor(diffSecs / 60)}分钟前`
    if (diffSecs < 86400) return `${Math.floor(diffSecs / 3600)}小时前`
    return `${Math.floor(diffSecs / 86400)}天前`
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center py-8">
        <Loader2 className="w-6 h-6 animate-spin text-blue-500" />
        <span className="ml-2 text-gray-600">加载任务队列...</span>
      </div>
    )
  }

  const filteredTasks = tasks

  const statsCount = {
    all: tasks.length,
    queued: tasks.filter(t => t.status === 'queued').length,
    processing: tasks.filter(t => t.status === 'processing').length,
    completed: tasks.filter(t => t.status === 'completed').length,
    failed: tasks.filter(t => t.status === 'failed').length,
  }

  return (
    <div className="bg-white rounded-lg shadow-md p-6 space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <List className="w-5 h-5 text-gray-700" />
          <h3 className="text-lg font-semibold text-gray-800">任务队列</h3>
        </div>
        <button
          onClick={loadTasks}
          className="p-2 text-gray-500 hover:text-gray-700 transition-colors"
          title="刷新"
        >
          <RefreshCw className="w-4 h-4" />
        </button>
      </div>

      {/* Filter Tabs */}
      <div className="flex gap-2 border-b border-gray-200">
        {[
          { key: 'all', label: '全部', count: statsCount.all },
          { key: 'queued', label: '排队中', count: statsCount.queued },
          { key: 'processing', label: '处理中', count: statsCount.processing },
          { key: 'completed', label: '已完成', count: statsCount.completed },
          { key: 'failed', label: '失败', count: statsCount.failed },
        ].map((tab) => (
          <button
            key={tab.key}
            onClick={() => setFilter(tab.key)}
            className={`px-3 py-2 text-sm font-medium transition-colors ${
              filter === tab.key
                ? 'text-blue-600 border-b-2 border-blue-600'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            {tab.label}
            {tab.count > 0 && (
              <span className="ml-1.5 px-1.5 py-0.5 text-xs rounded-full bg-gray-100">
                {tab.count}
              </span>
            )}
          </button>
        ))}
      </div>

      {/* Task List */}
      <div className="space-y-2 max-h-96 overflow-y-auto">
        {filteredTasks.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            <List className="w-12 h-12 mx-auto mb-2 text-gray-300" />
            <p>暂无任务</p>
          </div>
        ) : (
          filteredTasks.map((task) => (
            <div
              key={task.id}
              className={`flex items-start justify-between p-3 rounded-lg border ${getStatusColor(
                task.status
              )}`}
            >
              <div className="flex items-start gap-3 flex-1 min-w-0">
                <div className="flex-shrink-0 mt-0.5">{getStatusIcon(task.status)}</div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-medium text-gray-500">
                      {getTaskTypeText(task.type)}
                    </span>
                    <span className="text-xs text-gray-400">
                      {getTimeAgo(task.created_at)}
                    </span>
                  </div>

                  {task.metadata?.file_names && (
                    <div className="text-sm text-gray-700 mt-1">
                      {task.metadata.file_count} 个文件
                    </div>
                  )}

                  {task.error && (
                    <div className="text-xs text-red-600 mt-1 line-clamp-2">
                      错误: {task.error}
                    </div>
                  )}

                  {task.status === 'completed' && task.processing_time > 0 && (
                    <div className="text-xs text-gray-500 mt-1">
                      耗时: {task.processing_time.toFixed(2)}s
                    </div>
                  )}
                </div>
              </div>

              <span
                className={`text-xs font-medium ml-2 flex-shrink-0 ${
                  task.status === 'completed'
                    ? 'text-green-600'
                    : task.status === 'failed'
                    ? 'text-red-600'
                    : task.status === 'processing'
                    ? 'text-blue-600'
                    : 'text-gray-500'
                }`}
              >
                {getStatusText(task.status)}
              </span>
            </div>
          ))
        )}
      </div>

      {/* Stats */}
      {tasks.length > 0 && (
        <div className="border-t border-gray-200 pt-3">
          <div className="grid grid-cols-4 gap-2 text-center text-xs">
            <div>
              <div className="font-semibold text-gray-700">{statsCount.queued}</div>
              <div className="text-gray-500">排队中</div>
            </div>
            <div>
              <div className="font-semibold text-blue-600">{statsCount.processing}</div>
              <div className="text-gray-500">处理中</div>
            </div>
            <div>
              <div className="font-semibold text-green-600">{statsCount.completed}</div>
              <div className="text-gray-500">已完成</div>
            </div>
            <div>
              <div className="font-semibold text-red-600">{statsCount.failed}</div>
              <div className="text-gray-500">失败</div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
