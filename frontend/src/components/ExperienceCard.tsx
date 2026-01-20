import { Building2, Calendar, Tag, FileText, Trash2 } from 'lucide-react'
import type { ExperienceListItem } from '../types'

interface ExperienceCardProps {
  experience: ExperienceListItem
  onClick: () => void
  onDelete: (id: string) => void
}

export function ExperienceCard({ experience, onClick, onDelete }: ExperienceCardProps) {
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
      className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 hover:border-primary-500 dark:hover:border-primary-500 transition-all cursor-pointer p-6 group"
      onClick={onClick}
    >
      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex-1">
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

        {/* Delete button */}
        <button
          onClick={handleDelete}
          className="opacity-0 group-hover:opacity-100 transition-opacity p-2 hover:bg-red-500/10 rounded-lg"
          title="删除"
        >
          <Trash2 className="w-4 h-4 text-red-400" />
        </button>
      </div>

      {/* Metadata */}
      <div className="flex items-center gap-4 mb-4 text-sm text-gray-600 dark:text-gray-400">
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
        <div className="flex items-start gap-2 mb-3">
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

      {/* Footer info */}
      <div className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700 flex items-center justify-between text-xs text-gray-500">
        <span>来源: {experience.source_type === 'text' ? '文本' : '图片'}</span>
        {experience.has_answers && (
          <span className="text-green-600 dark:text-green-400">✓ 包含答案</span>
        )}
      </div>
    </div>
  )
}
