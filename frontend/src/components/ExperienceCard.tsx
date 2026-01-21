import { Building2, Calendar, Tag, FileText, Loader2, Sparkles, Trash2 } from 'lucide-react'
import type { ExperienceListItem } from '../types'

interface ExperienceCardProps {
  experience: ExperienceListItem
  onClick: () => void
  onDelete: (id: string) => void
  onGenerateAnswers?: (id: string, event: React.MouseEvent) => void
  isGeneratingAnswers?: boolean
}

export function ExperienceCard({ experience, onClick, onDelete, onGenerateAnswers, isGeneratingAnswers }: ExperienceCardProps) {
  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr)
    return date.toLocaleDateString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
    })
  }

  const handleDelete = (e: React.MouseEvent) => {
    e.stopPropagation()
    if (confirm('确定要删除这条面经吗？')) {
      onDelete(experience.id)
    }
  }

  return (
    <div
      className={`bg-white dark:bg-gray-800 rounded-lg border transition-all cursor-pointer p-6 group relative h-[300px] flex flex-col ${
        experience.is_generating_answers
          ? 'border-amber-500 dark:border-amber-500 shadow-lg shadow-amber-500/20 animate-pulse'
          : 'border-gray-200 dark:border-gray-700 hover:border-primary-500 dark:hover:border-primary-500'
      }`}
      onClick={onClick}
    >
      {/* 删除按钮 - 在右上角 */}
      {!experience.is_generating_answers && (
        <button
          onClick={handleDelete}
          className="absolute top-4 right-4 p-2 bg-white dark:bg-gray-900 hover:bg-red-50 dark:hover:bg-red-900/20 border border-gray-200 dark:border-gray-700 hover:border-red-300 dark:hover:border-red-700 text-gray-400 hover:text-red-600 dark:hover:text-red-400 rounded-lg transition-all opacity-0 group-hover:opacity-100 z-10 shadow-sm"
          title="删除面经"
        >
          <Trash2 className="w-4 h-4" />
        </button>
      )}

      {/* AI答案生成中指示器 */}
      {experience.is_generating_answers && (
        <div className="absolute top-4 right-4 flex items-center gap-2 px-3 py-1.5 bg-amber-100 dark:bg-amber-900/40 text-amber-700 dark:text-amber-400 rounded-lg text-xs font-medium shadow-sm z-10">
          <Loader2 className="w-3.5 h-3.5 animate-spin" />
          <span>AI正在生成答案...</span>
        </div>
      )}

      {/* Header - Fixed Section */}
      <div className="flex-shrink-0 mb-4">
        {experience.company_name && (
          <div className="flex items-center gap-2 mb-2">
            <Building2 className="w-5 h-5 text-primary-400" />
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
              {experience.company_name}
            </h3>
            {experience.company_scale && (
              <span className="px-2 py-1 text-xs bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded">
                {experience.company_scale}
              </span>
            )}
          </div>
        )}
        {experience.position && (
          <p className="text-gray-600 dark:text-gray-400 text-sm">{experience.position}</p>
        )}
      </div>

      {/* Content Section - Scrollable */}
      <div className="flex-1 overflow-y-auto space-y-3 mb-3 min-h-0">
        {/* Metadata */}
        <div className="flex items-center gap-4 text-sm text-gray-600 dark:text-gray-400">
        <div className="flex items-center gap-1">
          <Calendar className="w-4 h-4" />
          <span>{formatDate(experience.created_at)}</span>
        </div>
        {experience.interview_stage && (
          <div className="flex items-center gap-1">
            <span className="px-2 py-0.5 bg-blue-100 dark:bg-blue-500/10 text-blue-600 dark:text-blue-400 rounded text-xs">
              {experience.interview_stage}
            </span>
          </div>
        )}
        <div className="flex items-center gap-1">
          <FileText className="w-4 h-4" />
          <span>{experience.questions_count} 个问题</span>
        </div>
      </div>

        {/* Tags */}
        {experience.tags.length > 0 && (
          <div className="flex items-start gap-2">
            <Tag className="w-4 h-4 text-gray-400 mt-1 flex-shrink-0" />
            <div className="flex flex-wrap gap-2">
              {experience.tags.slice(0, 5).map((tag, index) => (
                <span
                  key={index}
                  className="px-2 py-1 text-xs bg-primary-50 dark:bg-primary-500/10 text-primary-600 dark:text-primary-300 rounded"
                >
                  {tag}
                </span>
              ))}
              {experience.tags.length > 5 && (
                <span className="px-2 py-1 text-xs text-gray-500 dark:text-gray-400">
                  +{experience.tags.length - 5} 更多
                </span>
              )}
            </div>
          </div>
        )}

        {/* Interview Experience */}
        {experience.interview_experience && (
          <div className="text-sm text-gray-700 dark:text-gray-300 bg-gray-50 dark:bg-gray-750 rounded p-3 border-l-2 border-primary-500">
            {experience.interview_experience}
          </div>
        )}

        {/* Notes */}
        {experience.notes && experience.notes.trim() && (
          <div className="text-sm text-gray-600 dark:text-gray-400 bg-amber-50 dark:bg-amber-500/10 rounded p-3 border-l-2 border-amber-500">
            <div className="flex items-start gap-2">
              <span className="text-amber-600 dark:text-amber-400 font-medium text-xs">备注:</span>
              <span className="flex-1">{experience.notes}</span>
            </div>
          </div>
        )}
      </div>

      {/* Footer - Fixed Section */}
      <div className="flex-shrink-0 pt-4 border-t border-gray-200 dark:border-gray-700 flex items-center justify-between text-xs text-gray-500">
        <span>来源: {experience.source_type === 'text' ? '文本' : '图片'}</span>
        <div className="flex items-center gap-2">
          {experience.has_answers && (
            <span className="text-green-600 dark:text-green-400">✓ 包含答案</span>
          )}
          {!experience.has_answers && !isGeneratingAnswers && onGenerateAnswers && (
            <button
              onClick={(e) => {
                e.stopPropagation()
                onGenerateAnswers(experience.id, e)
              }}
              className="flex items-center gap-1.5 px-3 py-1.5 bg-primary-600 hover:bg-primary-700 text-white rounded-lg text-xs font-medium shadow-sm transition-colors"
              title="为此面经生成AI答案"
            >
              <Sparkles className="w-3.5 h-3.5" />
              生成答案
            </button>
          )}
        </div>
      </div>
    </div>
  )
}
