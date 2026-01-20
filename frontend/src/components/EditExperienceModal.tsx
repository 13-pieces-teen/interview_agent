import { useState, useEffect } from 'react'
import { X, Plus, Trash2, Save, Building2, Briefcase, Calendar, FileText, Tag } from 'lucide-react'
import type { InterviewExperience, Question } from '../types'

interface EditExperienceModalProps {
  experience: InterviewExperience
  onClose: () => void
  onSave: (updates: any) => Promise<void>
}

export function EditExperienceModal({ experience, onClose, onSave }: EditExperienceModalProps) {
  const [saving, setSaving] = useState(false)
  const [formData, setFormData] = useState({
    company_name: experience.company_name || '',
    company_scale: experience.company_scale || '',
    position: experience.position || '',
    interview_stage: experience.interview_stage || '',
    interview_experience: experience.interview_experience || '',
    tags: experience.tags || [],
    questions: experience.questions.map((q) => ({ ...q })),
  })

  const [newTag, setNewTag] = useState('')

  const handleFieldChange = (field: string, value: any) => {
    setFormData((prev) => ({
      ...prev,
      [field]: value,
    }))
  }

  const handleQuestionChange = (index: number, field: keyof Question, value: string) => {
    const updatedQuestions = [...formData.questions]
    updatedQuestions[index] = {
      ...updatedQuestions[index],
      [field]: value,
    }
    setFormData((prev) => ({
      ...prev,
      questions: updatedQuestions,
    }))
  }

  const handleAddQuestion = () => {
    setFormData((prev) => ({
      ...prev,
      questions: [
        ...prev.questions,
        {
          id: `q-${Date.now()}`,
          question: '',
          answer: '',
          has_original_answer: false,
          tags: [],
        },
      ],
    }))
  }

  const handleRemoveQuestion = (index: number) => {
    if (confirm('确定要删除这个问题吗？')) {
      setFormData((prev) => ({
        ...prev,
        questions: prev.questions.filter((_, i) => i !== index),
      }))
    }
  }

  const handleAddTag = () => {
    if (newTag.trim() && !formData.tags.includes(newTag.trim())) {
      setFormData((prev) => ({
        ...prev,
        tags: [...prev.tags, newTag.trim()],
      }))
      setNewTag('')
    }
  }

  const handleRemoveTag = (tag: string) => {
    setFormData((prev) => ({
      ...prev,
      tags: prev.tags.filter((t) => t !== tag),
    }))
  }

  const handleSave = async () => {
    try {
      setSaving(true)
      await onSave(formData)
      onClose()
    } catch (error) {
      console.error('Failed to save:', error)
      alert('保存失败，请重试')
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-hidden flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-gray-200 dark:border-gray-700">
          <h2 className="text-xl font-bold text-gray-900 dark:text-white">编辑面经</h2>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
          >
            <X className="w-5 h-5 text-gray-600 dark:text-gray-400" />
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto px-6 py-4">
          <div className="space-y-6">
            {/* Company Info Section */}
            <div className="space-y-4">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white flex items-center gap-2">
                <Building2 className="w-5 h-5 text-primary-500" />
                公司信息
              </h3>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    公司名称
                  </label>
                  <input
                    type="text"
                    value={formData.company_name}
                    onChange={(e) => handleFieldChange('company_name', e.target.value)}
                    className="w-full px-3 py-2 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg focus:border-primary-500 focus:outline-none text-gray-900 dark:text-white"
                    placeholder="例如：字节跳动"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    公司规模
                  </label>
                  <select
                    value={formData.company_scale}
                    onChange={(e) => handleFieldChange('company_scale', e.target.value)}
                    className="w-full px-3 py-2 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg focus:border-primary-500 focus:outline-none text-gray-900 dark:text-white"
                  >
                    <option value="">请选择</option>
                    <option value="大厂">大厂</option>
                    <option value="中厂">中厂</option>
                    <option value="小厂">小厂</option>
                    <option value="初创">初创</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    职位
                  </label>
                  <input
                    type="text"
                    value={formData.position}
                    onChange={(e) => handleFieldChange('position', e.target.value)}
                    className="w-full px-3 py-2 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg focus:border-primary-500 focus:outline-none text-gray-900 dark:text-white"
                    placeholder="例如：前端工程师"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    面试阶段
                  </label>
                  <select
                    value={formData.interview_stage}
                    onChange={(e) => handleFieldChange('interview_stage', e.target.value)}
                    className="w-full px-3 py-2 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg focus:border-primary-500 focus:outline-none text-gray-900 dark:text-white"
                  >
                    <option value="">请选择</option>
                    <option value="一面">一面</option>
                    <option value="二面">二面</option>
                    <option value="三面">三面</option>
                    <option value="终面">终面</option>
                    <option value="HR面">HR面</option>
                  </select>
                </div>
              </div>
            </div>

            {/* Interview Experience */}
            <div className="space-y-2">
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 flex items-center gap-2">
                <FileText className="w-4 h-4 text-primary-500" />
                面试体验
              </label>
              <textarea
                value={formData.interview_experience}
                onChange={(e) => handleFieldChange('interview_experience', e.target.value)}
                rows={3}
                className="w-full px-3 py-2 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg focus:border-primary-500 focus:outline-none text-gray-900 dark:text-white resize-none"
                placeholder="描述面试体验、流程、氛围等..."
              />
            </div>

            {/* Tags Section */}
            <div className="space-y-2">
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 flex items-center gap-2">
                <Tag className="w-4 h-4 text-primary-500" />
                技术标签
              </label>
              <div className="flex gap-2">
                <input
                  type="text"
                  value={newTag}
                  onChange={(e) => setNewTag(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && handleAddTag()}
                  className="flex-1 px-3 py-2 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg focus:border-primary-500 focus:outline-none text-gray-900 dark:text-white"
                  placeholder="输入标签后按回车添加"
                />
                <button
                  onClick={handleAddTag}
                  className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
                >
                  <Plus className="w-4 h-4" />
                </button>
              </div>
              <div className="flex flex-wrap gap-2 mt-2">
                {formData.tags.map((tag, index) => (
                  <span
                    key={index}
                    className="px-3 py-1 bg-primary-50 dark:bg-primary-500/10 text-primary-600 dark:text-primary-300 rounded-full text-sm flex items-center gap-2"
                  >
                    {tag}
                    <button
                      onClick={() => handleRemoveTag(tag)}
                      className="hover:text-primary-800 dark:hover:text-primary-100"
                    >
                      <X className="w-3 h-3" />
                    </button>
                  </span>
                ))}
              </div>
            </div>

            {/* Questions Section */}
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white flex items-center gap-2">
                  <FileText className="w-5 h-5 text-primary-500" />
                  面试问题 ({formData.questions.length})
                </h3>
                <button
                  onClick={handleAddQuestion}
                  className="px-3 py-1.5 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors text-sm flex items-center gap-1"
                >
                  <Plus className="w-4 h-4" />
                  添加问题
                </button>
              </div>

              <div className="space-y-4">
                {formData.questions.map((q, index) => (
                  <div
                    key={q.id}
                    className="p-4 bg-gray-50 dark:bg-gray-750 rounded-lg border border-gray-200 dark:border-gray-700 space-y-3"
                  >
                    <div className="flex items-start justify-between">
                      <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                        问题 {index + 1}
                      </span>
                      <button
                        onClick={() => handleRemoveQuestion(index)}
                        className="p-1 hover:bg-red-500/10 rounded text-red-500 hover:text-red-600 transition-colors"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>

                    <div>
                      <label className="block text-xs font-medium text-gray-600 dark:text-gray-400 mb-1">
                        问题内容
                      </label>
                      <textarea
                        value={q.question}
                        onChange={(e) => handleQuestionChange(index, 'question', e.target.value)}
                        rows={2}
                        className="w-full px-3 py-2 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg focus:border-primary-500 focus:outline-none text-gray-900 dark:text-white text-sm resize-none"
                        placeholder="输入问题..."
                      />
                    </div>

                    <div>
                      <label className="block text-xs font-medium text-gray-600 dark:text-gray-400 mb-1">
                        答案
                      </label>
                      <textarea
                        value={q.answer || ''}
                        onChange={(e) => handleQuestionChange(index, 'answer', e.target.value)}
                        rows={4}
                        className="w-full px-3 py-2 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg focus:border-primary-500 focus:outline-none text-gray-900 dark:text-white text-sm resize-none"
                        placeholder="输入答案..."
                      />
                    </div>
                  </div>
                ))}

                {formData.questions.length === 0 && (
                  <div className="text-center py-8 text-gray-500 dark:text-gray-400">
                    暂无问题，点击"添加问题"开始添加
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="flex items-center justify-end gap-3 px-6 py-4 border-t border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-750">
          <button
            onClick={onClose}
            className="px-4 py-2 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700 rounded-lg transition-colors"
            disabled={saving}
          >
            取消
          </button>
          <button
            onClick={handleSave}
            disabled={saving}
            className="px-6 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {saving ? (
              <>
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                保存中...
              </>
            ) : (
              <>
                <Save className="w-4 h-4" />
                保存修改
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  )
}
