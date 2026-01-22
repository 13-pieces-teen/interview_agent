import React, { useState } from 'react'
import { X, Download, FileText, List, FileSpreadsheet } from 'lucide-react'
import { exportMarkdown, exportExcel } from '../services/api'

interface ExportModalProps {
  isOpen: boolean
  onClose: () => void
  selectedExperienceIds?: string[]
  currentFilters?: {
    companyName?: string
    tags?: string[]
    timeRange?: 'all' | 'today' | '3d' | '7d' | '30d' | '90d' | 'custom'
    customStartDate?: string
    customEndDate?: string
    stage?: string
  }
}

const ExportModal: React.FC<ExportModalProps> = ({
  isOpen,
  onClose,
  selectedExperienceIds,
  currentFilters,
}) => {
  const [exportType, setExportType] = useState<'by_interview' | 'by_question'>('by_interview')
  const [exportFormat, setExportFormat] = useState<'markdown' | 'excel'>('markdown')
  const [isExporting, setIsExporting] = useState(false)
  const [error, setError] = useState<string | null>(null)

  if (!isOpen) return null

  // Helper to convert time range preset to ISO date strings
  const convertTimeRangeToDateStrings = (
    timeRange?: 'all' | 'today' | '3d' | '7d' | '30d' | '90d' | 'custom'
  ): { startDate?: string; endDate?: string } => {
    if (!timeRange || timeRange === 'all') {
      return { startDate: undefined, endDate: undefined }
    }

    if (timeRange === 'custom') {
      // Use custom date range from props
      const start = currentFilters?.customStartDate ? new Date(currentFilters.customStartDate + 'T00:00:00') : undefined
      const end = currentFilters?.customEndDate ? new Date(currentFilters.customEndDate + 'T23:59:59') : undefined

      return {
        startDate: start?.toISOString(),
        endDate: end?.toISOString(),
      }
    }

    const now = new Date()
    const start = new Date()

    // Set start time to beginning of the day
    start.setHours(0, 0, 0, 0)

    if (timeRange === 'today') {
      // Today: from 00:00:00 to 23:59:59
      const endOfDay = new Date()
      endOfDay.setHours(23, 59, 59, 999)
      return {
        startDate: start.toISOString(),
        endDate: endOfDay.toISOString(),
      }
    }

    // For other presets, subtract days
    const days = timeRange === '3d' ? 3 : timeRange === '7d' ? 7 : timeRange === '30d' ? 30 : 90
    start.setDate(now.getDate() - days)

    return {
      startDate: start.toISOString(),
      endDate: now.toISOString(),
    }
  }

  // Build concise filter summary for display
  const buildFilterSummary = (): string => {
    const filters: string[] = []

    // Time range
    if (currentFilters?.timeRange && currentFilters.timeRange !== 'all') {
      const timeLabels = {
        'today': '今天',
        '3d': '最近3天',
        '7d': '最近7天',
        '30d': '最近30天',
        '90d': '最近90天',
        'custom': '自定义时间'
      }
      filters.push(timeLabels[currentFilters.timeRange])
    }

    // Interview stage
    if (currentFilters?.stage) {
      filters.push(currentFilters.stage)
    }

    // Tags - show first 2 + count if more
    if (currentFilters?.tags && currentFilters.tags.length > 0) {
      const tagDisplay = currentFilters.tags.length <= 2
        ? currentFilters.tags.join(', ')
        : `${currentFilters.tags.slice(0, 2).join(', ')} +${currentFilters.tags.length - 2}`
      filters.push(tagDisplay)
    }

    // Company name
    if (currentFilters?.companyName) {
      filters.push(currentFilters.companyName)
    }

    return filters.length > 0 ? filters.join(', ') : ''
  }

  const filterSummary = buildFilterSummary()

  const handleExport = async () => {
    try {
      setIsExporting(true)
      setError(null)

      // Convert time range to date strings
      const { startDate, endDate } = convertTimeRangeToDateStrings(currentFilters?.timeRange)

      if (exportFormat === 'excel') {
        // Excel export - only supports by_question
        if (exportType !== 'by_question') {
          setError('Excel导出仅支持按题目排列')
          setIsExporting(false)
          return
        }

        await exportExcel({
          exportType,
          companyName: currentFilters?.companyName,
          tags: currentFilters?.tags,
          startDate,
          endDate,
          interviewStage: currentFilters?.stage,
        })

        onClose()
      } else {
        // Markdown export
        const { content, filename } = await exportMarkdown({
          exportType,
          experienceIds: selectedExperienceIds,
          companyName: currentFilters?.companyName,
          tags: currentFilters?.tags,
          startDate,
          endDate,
          interviewStage: currentFilters?.stage,
        })

        // Create a download link
        const blob = new Blob([content], { type: 'text/markdown;charset=utf-8' })
        const url = URL.createObjectURL(blob)
        const link = document.createElement('a')
        link.href = url
        link.download = filename
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
        URL.revokeObjectURL(url)

        onClose()
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : '导出失败')
    } finally {
      setIsExporting(false)
    }
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-md w-full mx-4">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b">
          <h2 className="text-xl font-semibold text-gray-900">一键导出</h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 transition-colors"
            disabled={isExporting}
          >
            <X size={24} />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 space-y-4">
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
              {error}
            </div>
          )}

          {/* Export format selection */}
          <div className="space-y-3">
            <label className="block text-sm font-medium text-gray-700">
              选择导出格式
            </label>

            <div className="grid grid-cols-2 gap-3">
              <button
                onClick={() => setExportFormat('markdown')}
                className={`p-3 rounded-lg border-2 transition-all ${
                  exportFormat === 'markdown'
                    ? 'border-blue-500 bg-blue-50'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
                disabled={isExporting}
              >
                <div className="flex flex-col items-center space-y-1">
                  <FileText
                    size={20}
                    className={exportFormat === 'markdown' ? 'text-blue-500' : 'text-gray-400'}
                  />
                  <span className={`font-medium text-sm ${exportFormat === 'markdown' ? 'text-blue-700' : 'text-gray-700'}`}>
                    Markdown
                  </span>
                </div>
              </button>

              <button
                onClick={() => {
                  setExportFormat('excel')
                  setExportType('by_question')
                }}
                className={`p-3 rounded-lg border-2 transition-all ${
                  exportFormat === 'excel'
                    ? 'border-green-500 bg-green-50'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
                disabled={isExporting}
              >
                <div className="flex flex-col items-center space-y-1">
                  <FileSpreadsheet
                    size={20}
                    className={exportFormat === 'excel' ? 'text-green-500' : 'text-gray-400'}
                  />
                  <span className={`font-medium text-sm ${exportFormat === 'excel' ? 'text-green-700' : 'text-gray-700'}`}>
                    Excel
                  </span>
                </div>
              </button>
            </div>
          </div>

          <div className="space-y-3">
              <label className="block text-sm font-medium text-gray-700">
                选择导出方式
              </label>

              {/* Export by interview */}
              <button
                onClick={() => setExportType('by_interview')}
                className={`w-full p-4 rounded-lg border-2 transition-all ${
                  exportType === 'by_interview'
                    ? 'border-blue-500 bg-blue-50'
                    : 'border-gray-200 hover:border-gray-300'
                } ${exportFormat === 'excel' ? 'opacity-50 cursor-not-allowed' : ''}`}
                disabled={isExporting || exportFormat === 'excel'}
              >
                <div className="flex items-start space-x-3">
                  <FileText
                    size={24}
                    className={exportType === 'by_interview' ? 'text-blue-500' : 'text-gray-400'}
                  />
                  <div className="flex-1 text-left">
                    <div className="font-medium text-gray-900">按面经排列</div>
                    <div className="text-sm text-gray-500 mt-1">
                      每个面经包含标题、标签和问题列表
                      {exportFormat === 'excel' && ' (仅支持Markdown)'}
                    </div>
                  </div>
                </div>
              </button>

              {/* Export by question */}
              <button
                onClick={() => setExportType('by_question')}
                className={`w-full p-4 rounded-lg border-2 transition-all ${
                  exportType === 'by_question'
                    ? 'border-blue-500 bg-blue-50'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
                disabled={isExporting}
              >
                <div className="flex items-start space-x-3">
                  <List
                    size={24}
                    className={exportType === 'by_question' ? 'text-blue-500' : 'text-gray-400'}
                  />
                  <div className="flex-1 text-left">
                    <div className="font-medium text-gray-900">按题目排列</div>
                    <div className="text-sm text-gray-500 mt-1">
                      相同题目分组，显示所有出现的面经
                    </div>
                  </div>
                </div>
              </button>
            </div>

          {/* Export scope info */}
          {/* Export scope information */}
          <div className="bg-blue-50 rounded-lg p-4">
            <p className="text-sm text-gray-700">
              <strong className="text-gray-900">导出范围: </strong>
              {selectedExperienceIds && selectedExperienceIds.length > 0 ? (
                <>
                  已选择 {selectedExperienceIds.length} 条
                  {filterSummary && (
                    <span className="ml-2 text-blue-700">
                      | 筛选: {filterSummary}
                    </span>
                  )}
                </>
              ) : (
                <>
                  所有面经
                  {filterSummary && (
                    <span className="ml-2 text-blue-700">
                      | 筛选: {filterSummary}
                    </span>
                  )}
                </>
              )}
            </p>
          </div>

          {/* Format preview */}
          <div className="bg-blue-50 rounded-lg p-4">
            <div className="text-sm text-blue-900">
              <div className="font-medium mb-2">格式示例:</div>
                {exportType === 'by_interview' ? (
                  <pre className="text-xs text-blue-800 whitespace-pre-wrap font-mono">
                    {`## 公司名 - 职位 - 面试阶段
Tag: xxx, xxxx, xxxx

**问题列表**:

### 1. 如何维护多异步任务下上下文窗口不被污染
**答案**: ...

### 2. rag流程
**答案**: ...`}
                  </pre>
                ) : (
                  <pre className="text-xs text-blue-800 whitespace-pre-wrap font-mono">
                    {`## 1. 如何维护多异步任务下上下文窗口不被污染
**出现次数**: 3

**出现在以下面经**:
- 公司A - Python开发 - 一面
  - 答案: ...
- 公司B - 后端工程师 - 二面
  - 答案: ...`}
                  </pre>
                )}
              </div>
            </div>
        </div>

        {/* Footer */}
        <div className="flex items-center justify-end space-x-3 p-6 border-t bg-gray-50 rounded-b-lg">
          <button
            onClick={onClose}
            className="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
            disabled={isExporting}
          >
            取消
          </button>
          <button
            onClick={handleExport}
            disabled={isExporting}
            className="flex items-center space-x-2 px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Download size={18} />
            <span>{isExporting ? '导出中...' : '导出'}</span>
          </button>
        </div>
      </div>
    </div>
  )
}

export default ExportModal
