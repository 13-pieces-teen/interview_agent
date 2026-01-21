import { useState } from 'react'
import { ChevronDown, ChevronRight, Building2, Briefcase, Calendar } from 'lucide-react'
import type { QuestionGroup } from '../types'

interface QuestionGroupViewProps {
  groups: QuestionGroup[]
  onExperienceClick?: (experienceId: string) => void
}

export function QuestionGroupView({ groups, onExperienceClick }: QuestionGroupViewProps) {
  const [expandedGroups, setExpandedGroups] = useState<Set<number>>(new Set())

  const toggleGroup = (index: number) => {
    const newExpanded = new Set(expandedGroups)
    if (newExpanded.has(index)) {
      newExpanded.delete(index)
    } else {
      newExpanded.add(index)
    }
    setExpandedGroups(newExpanded)
  }

  const formatDate = (dateStr: string) => {
    try {
      const date = new Date(dateStr)
      return date.toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' })
    } catch {
      return dateStr
    }
  }

  if (groups.length === 0) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-600 dark:text-gray-400">没有找到题目</p>
        <p className="text-gray-500 text-sm mt-2">尝试调整搜索或筛选条件</p>
      </div>
    )
  }

  return (
    <div className="space-y-3">
      {groups.map((group, index) => {
        const isExpanded = expandedGroups.has(index)

        return (
          <div
            key={index}
            className="bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-800 overflow-hidden transition-colors"
          >
            {/* Question Header */}
            <button
              onClick={() => toggleGroup(index)}
              className="w-full px-5 py-4 flex items-start gap-3 hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors text-left"
            >
              <span className="mt-0.5 text-gray-400 dark:text-gray-600">
                {isExpanded ? (
                  <ChevronDown className="w-4 h-4" />
                ) : (
                  <ChevronRight className="w-4 h-4" />
                )}
              </span>

              <div className="flex-1 min-w-0">
                <div className="flex items-start justify-between gap-3 mb-2">
                  <p className="text-sm font-medium text-gray-900 dark:text-white leading-relaxed">
                    {group.question}
                  </p>
                  <span className="flex-shrink-0 px-2 py-0.5 bg-primary-100 dark:bg-primary-900/30 text-primary-700 dark:text-primary-400 rounded text-xs font-medium">
                    {group.count} 次
                  </span>
                </div>

                {group.tags.length > 0 && (
                  <div className="flex flex-wrap gap-1.5">
                    {group.tags.slice(0, 5).map((tag, tagIdx) => (
                      <span
                        key={tagIdx}
                        className="px-2 py-0.5 bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400 rounded text-xs"
                      >
                        {tag}
                      </span>
                    ))}
                    {group.tags.length > 5 && (
                      <span className="px-2 py-0.5 text-gray-500 dark:text-gray-500 text-xs">
                        +{group.tags.length - 5}
                      </span>
                    )}
                  </div>
                )}
              </div>
            </button>

            {/* Occurrences List */}
            {isExpanded && (
              <div className="border-t border-gray-100 dark:border-gray-800 bg-gray-50 dark:bg-gray-900/50">
                <div className="px-5 py-4 space-y-3">
                  {group.occurrences.map((occurrence, occIdx) => (
                    <div
                      key={occIdx}
                      className="bg-white dark:bg-gray-900 rounded-lg p-4 border border-gray-200 dark:border-gray-800 hover:border-gray-300 dark:hover:border-gray-700 transition-all cursor-pointer"
                      onClick={() => onExperienceClick?.(occurrence.experience_id)}
                    >
                      {/* Company and Position Info */}
                      <div className="flex items-center gap-4 mb-3 text-xs">
                        {occurrence.company_name && (
                          <div className="flex items-center gap-1.5">
                            <Building2 className="w-3.5 h-3.5 text-gray-400" />
                            <span className="text-gray-700 dark:text-gray-300 font-medium">
                              {occurrence.company_name}
                            </span>
                          </div>
                        )}

                        {occurrence.position && (
                          <div className="flex items-center gap-1.5">
                            <Briefcase className="w-3.5 h-3.5 text-gray-400" />
                            <span className="text-gray-600 dark:text-gray-400">
                              {occurrence.position}
                            </span>
                          </div>
                        )}

                        {occurrence.interview_stage && (
                          <span className="px-2 py-0.5 bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400 rounded">
                            {occurrence.interview_stage}
                          </span>
                        )}

                        <div className="flex items-center gap-1.5 ml-auto">
                          <Calendar className="w-3.5 h-3.5 text-gray-400" />
                          <span className="text-gray-500 dark:text-gray-500">
                            {formatDate(occurrence.created_at)}
                          </span>
                        </div>
                      </div>

                      {/* Answer */}
                      {occurrence.answer && (
                        <div>
                          <div className="flex items-center gap-2 mb-2">
                            <p className="text-xs text-gray-500 dark:text-gray-500">回答</p>
                            {occurrence.is_ai_generated && (
                              <span className="px-1.5 py-0.5 bg-yellow-100 dark:bg-yellow-900/30 text-yellow-700 dark:text-yellow-400 rounded text-xs">
                                AI 生成
                              </span>
                            )}
                          </div>
                          <p className="text-sm text-gray-700 dark:text-gray-300 leading-relaxed whitespace-pre-wrap line-clamp-3">
                            {occurrence.answer}
                          </p>
                        </div>
                      )}

                      {!occurrence.answer && (
                        <p className="text-xs text-gray-400 dark:text-gray-600 italic">
                          暂无回答
                        </p>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )
      })}
    </div>
  )
}
