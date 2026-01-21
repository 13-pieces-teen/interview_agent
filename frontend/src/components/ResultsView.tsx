import { useState } from 'react'
import { InterviewExperience } from '../types'
import { Building2, Briefcase, MapPin, Tag, Edit } from 'lucide-react'
import { EditExperienceModal } from './EditExperienceModal'
import { updateExperience } from '../services/api'

interface ResultsViewProps {
  experience: InterviewExperience
  processingTime: number
  onUpdate?: (updatedExperience: InterviewExperience) => void
}

export const ResultsView = ({ experience, processingTime, onUpdate }: ResultsViewProps) => {
  const [showEditModal, setShowEditModal] = useState(false)
  const [currentExperience, setCurrentExperience] = useState(experience)

  const handleSave = async (updates: any) => {
    try {
      const result = await updateExperience(currentExperience.id, updates)
      if (result.success) {
        setCurrentExperience(result.experience)
        if (onUpdate) {
          onUpdate(result.experience)
        }
      }
    } catch (error) {
      console.error('Failed to update experience:', error)
      throw error
    }
  }

  return (
    <>
      <div className="w-full max-w-3xl mx-auto space-y-6">
        {/* Header Info */}
        <div className="bg-white dark:bg-gray-900 rounded-xl p-8 border border-gray-200 dark:border-gray-800 transition-colors">
          <div className="flex items-start justify-between mb-6">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white">面经详情</h2>
            <button
              onClick={() => setShowEditModal(true)}
              className="px-3 py-1.5 text-sm font-medium text-gray-700 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white border border-gray-200 dark:border-gray-800 rounded-lg hover:border-gray-300 dark:hover:border-gray-700 transition-colors flex items-center gap-1.5"
            >
              <Edit className="w-3.5 h-3.5" />
              编辑
            </button>
          </div>

        <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
          {currentExperience.company_name && (
            <div className="flex items-start gap-2.5">
              <Building2 className="w-4 h-4 text-gray-400 mt-0.5 flex-shrink-0" />
              <div className="flex-1 min-w-0">
                <p className="text-xs text-gray-500 dark:text-gray-500 mb-0.5">公司</p>
                <p className="text-sm text-gray-900 dark:text-white truncate">{currentExperience.company_name}</p>
              </div>
            </div>
          )}

          {currentExperience.position && (
            <div className="flex items-start gap-2.5">
              <Briefcase className="w-4 h-4 text-gray-400 mt-0.5 flex-shrink-0" />
              <div className="flex-1 min-w-0">
                <p className="text-xs text-gray-500 dark:text-gray-500 mb-0.5">职位</p>
                <p className="text-sm text-gray-900 dark:text-white truncate">{currentExperience.position}</p>
              </div>
            </div>
          )}

          {currentExperience.company_scale && (
            <div className="flex items-start gap-2.5">
              <MapPin className="w-4 h-4 text-gray-400 mt-0.5 flex-shrink-0" />
              <div className="flex-1 min-w-0">
                <p className="text-xs text-gray-500 dark:text-gray-500 mb-0.5">公司规模</p>
                <p className="text-sm text-gray-900 dark:text-white truncate">{currentExperience.company_scale}</p>
              </div>
            </div>
          )}

          {currentExperience.interview_stage && (
            <div className="flex items-start gap-2.5">
              <Tag className="w-4 h-4 text-gray-400 mt-0.5 flex-shrink-0" />
              <div className="flex-1 min-w-0">
                <p className="text-xs text-gray-500 dark:text-gray-500 mb-0.5">面试阶段</p>
                <p className="text-sm text-gray-900 dark:text-white truncate">{currentExperience.interview_stage}</p>
              </div>
            </div>
          )}
        </div>

        {currentExperience.tags.length > 0 && (
          <div className="mt-6 pt-6 border-t border-gray-100 dark:border-gray-800">
            <p className="text-xs text-gray-500 dark:text-gray-500 mb-3">技术标签</p>
            <div className="flex flex-wrap gap-2">
              {currentExperience.tags.map((tag, idx) => (
                <span
                  key={idx}
                  className="px-2.5 py-1 bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 rounded-md text-xs"
                >
                  {tag}
                </span>
              ))}
            </div>
          </div>
        )}

        {currentExperience.interview_experience && (
          <div className="mt-6 pt-6 border-t border-gray-100 dark:border-gray-800">
            <p className="text-xs text-gray-500 dark:text-gray-500 mb-3">整体评价</p>
            <p className="text-sm text-gray-700 dark:text-gray-300 leading-relaxed whitespace-pre-wrap">{currentExperience.interview_experience}</p>
          </div>
        )}

        {currentExperience.notes && currentExperience.notes.trim() && (
          <div className="mt-6 pt-6 border-t border-gray-100 dark:border-gray-800">
            <p className="text-xs text-amber-600 dark:text-amber-400 font-medium mb-3">备注</p>
            <div className="text-sm text-gray-700 dark:text-gray-300 leading-relaxed whitespace-pre-wrap bg-amber-50 dark:bg-amber-500/10 rounded-lg p-4 border-l-2 border-amber-500">
              {currentExperience.notes}
            </div>
          </div>
        )}
      </div>

      {/* Questions */}
      <div className="bg-white dark:bg-gray-900 rounded-xl p-8 border border-gray-200 dark:border-gray-800 transition-colors">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-white mb-6">
          面试问题 ({currentExperience.questions.length})
        </h3>

        <div className="space-y-4">
          {currentExperience.questions.map((q, idx) => (
            <div
              key={idx}
              className="bg-gray-50 dark:bg-gray-800/50 rounded-lg p-5 border border-gray-100 dark:border-gray-800 transition-colors"
            >
              <div className="flex items-start gap-3 mb-3">
                <span className="flex-shrink-0 w-6 h-6 bg-primary-600 text-white rounded-lg flex items-center justify-center font-semibold text-xs">
                  {idx + 1}
                </span>
                <div className="flex-1">
                  <p className="text-sm text-gray-900 dark:text-white font-medium leading-relaxed">{q.question}</p>
                </div>
              </div>

              {q.answer && (
                <div className="ml-9 mb-3">
                  <p className="text-xs text-gray-500 dark:text-gray-500 mb-2">回答</p>
                  <p className="text-sm text-gray-700 dark:text-gray-300 leading-relaxed whitespace-pre-wrap">{q.answer}</p>
                  {q.is_ai_generated && (
                    <span className="inline-block mt-3 px-2 py-0.5 bg-yellow-100 dark:bg-yellow-900/30 text-yellow-700 dark:text-yellow-400 rounded text-xs">
                      AI 生成
                    </span>
                  )}
                </div>
              )}

              {q.tags.length > 0 && (
                <div className="ml-9">
                  <div className="flex flex-wrap gap-1.5">
                    {q.tags.map((tag, tagIdx) => (
                      <span
                        key={tagIdx}
                        className="px-2 py-0.5 bg-gray-200 dark:bg-gray-700 text-gray-600 dark:text-gray-400 rounded text-xs"
                      >
                        {tag}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>

    {/* Edit Modal */}
    {showEditModal && (
      <EditExperienceModal
        experience={currentExperience}
        onClose={() => setShowEditModal(false)}
        onSave={handleSave}
      />
    )}
  </>
  )
}
