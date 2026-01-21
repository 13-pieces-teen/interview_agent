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

  const handleExport = async () => {
    try {
      setIsExporting(true)
      setError(null)

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
        })

        onClose()
      } else {
        // Markdown export
        const { content, filename } = await exportMarkdown({
          exportType,
          experienceIds: selectedExperienceIds,
          companyName: currentFilters?.companyName,
          tags: currentFilters?.tags,
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

            <div className="flex space-x-3">
              <button
                onClick={() => setExportFormat('markdown')}
                className={`flex-1 p-3 rounded-lg border-2 transition-all ${
                  exportFormat === 'markdown'
                    ? 'border-blue-500 bg-blue-50'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
                disabled={isExporting}
              >
                <div className="flex items-center justify-center space-x-2">
                  <FileText
                    size={20}
                    className={exportFormat === 'markdown' ? 'text-blue-500' : 'text-gray-400'}
                  />
                  <span className={`font-medium ${exportFormat === 'markdown' ? 'text-blue-700' : 'text-gray-700'}`}>
                    Markdown
                  </span>
                </div>
              </button>

              <button
                onClick={() => {
                  setExportFormat('excel')
                  setExportType('by_question')
                }}
                className={`flex-1 p-3 rounded-lg border-2 transition-all ${
                  exportFormat === 'excel'
                    ? 'border-green-500 bg-green-50'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
                disabled={isExporting}
              >
                <div className="flex items-center justify-center space-x-2">
                  <FileSpreadsheet
                    size={20}
                    className={exportFormat === 'excel' ? 'text-green-500' : 'text-gray-400'}
                  />
                  <span className={`font-medium ${exportFormat === 'excel' ? 'text-green-700' : 'text-gray-700'}`}>
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
          <div className="bg-gray-50 rounded-lg p-4">
            <div className="text-sm text-gray-700">
              <div className="font-medium mb-2">导出范围:</div>
              <ul className="space-y-1 text-gray-600">
                {selectedExperienceIds && selectedExperienceIds.length > 0 ? (
                  <li>• 已选择 {selectedExperienceIds.length} 条面经</li>
                ) : (
                  <>
                    {currentFilters?.companyName && (
                      <li>• 公司: {currentFilters.companyName}</li>
                    )}
                    {currentFilters?.tags && currentFilters.tags.length > 0 && (
                      <li>• 标签: {currentFilters.tags.join(', ')}</li>
                    )}
                    {!currentFilters?.companyName &&
                      (!currentFilters?.tags || currentFilters.tags.length === 0) && (
                        <li>• 所有面经</li>
                      )}
                  </>
                )}
              </ul>
            </div>
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
