import { useState, useEffect } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { Search, Filter, RotateCcw, Building2, Tag, Calendar, List, Grid, Download } from 'lucide-react'
import type { ExperienceListItem, QuestionGroup } from '../types'
import { ExperienceCard } from '../components/ExperienceCard'
import { QuestionGroupView } from '../components/QuestionGroupView'
import ExportModal from '../components/ExportModal'
import {
  listExperiences,
  getAllTags,
  getAllCompanies,
  deleteExperience,
  getStats,
  getGroupedQuestions,
  generateAnswers,
  getAnswerGenerationTaskStatus,
  listAnswerGenerationTasks,
} from '../services/api'

type ViewMode = 'experiences' | 'questions'

export function GalleryPage() {
  const navigate = useNavigate()
  const [searchParams, setSearchParams] = useSearchParams()

  const [viewMode, setViewMode] = useState<ViewMode>('experiences')
  const [experiences, setExperiences] = useState<ExperienceListItem[]>([])
  const [questionGroups, setQuestionGroups] = useState<QuestionGroup[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // Filters
  const [companyFilter, setCompanyFilter] = useState('')
  const [selectedTags, setSelectedTags] = useState<string[]>([])
  const [timeFilter, setTimeFilter] = useState<'all' | 'today' | '3d' | '7d' | '30d' | '90d' | 'custom'>('all')
  const [customStartDate, setCustomStartDate] = useState('')
  const [customEndDate, setCustomEndDate] = useState('')
  const [stageFilter, setStageFilter] = useState('')
  const [questionSearch, setQuestionSearch] = useState('')

  // Available options
  const [allTags, setAllTags] = useState<string[]>([])
  const [allCompanies, setAllCompanies] = useState<string[]>([])

  // Stats
  const [stats, setStats] = useState<{
    total_experiences: number
    total_questions: number
    unique_companies: number
  } | null>(null)

  const [showFilters, setShowFilters] = useState(false)
  const [showExportModal, setShowExportModal] = useState(false)

  // Answer generation tracking
  const [generatingAnswersFor, setGeneratingAnswersFor] = useState<Map<string, string>>(new Map())

  useEffect(() => {
    loadData()
    loadFilterOptions()
    loadStats()
  }, [])

  useEffect(() => {
    loadData()
  }, [companyFilter, selectedTags, timeFilter, stageFilter, viewMode, questionSearch, customStartDate, customEndDate])

  // Poll for answer generation status
  useEffect(() => {
    if (generatingAnswersFor.size === 0) return

    const interval = setInterval(async () => {
      const updates = new Map(generatingAnswersFor)
      let hasChanges = false

      for (const [experienceId, taskId] of generatingAnswersFor.entries()) {
        try {
          const status = await getAnswerGenerationTaskStatus(taskId)

          if (status.status === 'completed' || status.status === 'failed') {
            updates.delete(experienceId)
            hasChanges = true

            if (status.status === 'completed') {
              loadData()
            }
          }
        } catch (err) {
          console.error('Failed to check task status:', err)
          updates.delete(experienceId)
          hasChanges = true
        }
      }

      if (hasChanges) {
        setGeneratingAnswersFor(updates)
      }
    }, 3000)

    return () => clearInterval(interval)
  }, [generatingAnswersFor])

  // Restore answer generation state on mount
  useEffect(() => {
    const restoreGeneratingState = async () => {
      try {
        const { tasks } = await listAnswerGenerationTasks()

        // Filter for active tasks (pending or processing)
        const activeTasks = tasks.filter(
          task => task.status === 'pending' || task.status === 'processing'
        )

        if (activeTasks.length > 0) {
          const restoredMap = new Map<string, string>()

          activeTasks.forEach(task => {
            restoredMap.set(task.experience_id, task.task_id)
          })

          setGeneratingAnswersFor(restoredMap)

          // Also update experiences list to show generating state
          setExperiences(prev =>
            prev.map(exp => ({
              ...exp,
              is_generating_answers: restoredMap.has(exp.id)
            }))
          )
        }
      } catch (err) {
        console.error('Failed to restore answer generation state:', err)
        // Don't show error to user - this is background restoration
      }
    }

    restoreGeneratingState()
  }, []) // Empty dependency array - run only on mount

  // Helper to convert time range preset to ISO date strings
  const convertTimeRangeToDateStrings = (
    timeRange: 'all' | 'today' | '3d' | '7d' | '30d' | '90d' | 'custom'
  ): { startDate?: string; endDate?: string } => {
    if (timeRange === 'all') {
      return { startDate: undefined, endDate: undefined }
    }

    if (timeRange === 'custom') {
      // Use custom date range
      const start = customStartDate ? new Date(customStartDate + 'T00:00:00') : undefined
      const end = customEndDate ? new Date(customEndDate + 'T23:59:59') : undefined

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

  const loadData = async () => {
    try {
      setLoading(true)
      setError(null)

      if (viewMode === 'experiences') {
        const { startDate } = convertTimeRangeToDateStrings(timeFilter)

        const { experiences: data } = await listExperiences({
          companyName: companyFilter || undefined,
          tags: selectedTags.length > 0 ? selectedTags : undefined,
          startDate,
          interviewStage: stageFilter || undefined,
          limit: 100,
        })

        setExperiences(data)
      } else {
        const { groups } = await getGroupedQuestions({
          search: questionSearch || undefined,
          tags: selectedTags.length > 0 ? selectedTags : undefined,
          companyName: companyFilter || undefined,
          limit: 100,
        })

        setQuestionGroups(groups)
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load data')
    } finally {
      setLoading(false)
    }
  }

  const loadFilterOptions = async () => {
    try {
      const [tagsData, companiesData] = await Promise.all([getAllTags(), getAllCompanies()])
      setAllTags(tagsData.tags)
      setAllCompanies(companiesData.companies)
    } catch (err) {
      console.error('Failed to load filter options:', err)
    }
  }

  const loadStats = async () => {
    try {
      const statsData = await getStats()
      setStats(statsData)
    } catch (err) {
      console.error('Failed to load stats:', err)
    }
  }

  const handleCardClick = (id: string) => {
    navigate(`/experience/${id}`)
  }

  const handleDelete = async (id: string) => {
    try {
      await deleteExperience(id)
      setExperiences(experiences.filter((exp) => exp.id !== id))
      loadStats()
    } catch (err) {
      alert('Failed to delete experience')
    }
  }

  const handleResetFilters = () => {
    setCompanyFilter('')
    setSelectedTags([])
    setTimeFilter('all')
    setCustomStartDate('')
    setCustomEndDate('')
    setStageFilter('')
    setQuestionSearch('')
  }

  const toggleTag = (tag: string) => {
    setSelectedTags((prev) =>
      prev.includes(tag) ? prev.filter((t) => t !== tag) : [...prev, tag]
    )
  }

  const handleGenerateAnswers = async (experienceId: string, event: React.MouseEvent) => {
    event.stopPropagation()

    try {
      const response = await generateAnswers(experienceId)

      if (response.task_id) {
        setGeneratingAnswersFor(prev => new Map(prev).set(experienceId, response.task_id))

        setExperiences(prev =>
          prev.map(exp =>
            exp.id === experienceId
              ? { ...exp, is_generating_answers: true }
              : exp
          )
        )
      }
    } catch (err) {
      alert(`生成答案失败: ${err instanceof Error ? err.message : '未知错误'}`)
    }
  }

  return (
    <div className="min-h-screen bg-white dark:bg-gray-950 transition-colors">
      {/* Header */}
      <div className="sticky top-0 bg-white/80 dark:bg-gray-950/80 backdrop-blur-sm border-b border-gray-100 dark:border-gray-800 z-10 transition-colors">
        <div className="max-w-7xl mx-auto px-6 py-6">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h2 className="text-lg font-semibold text-gray-900 dark:text-white">历史记录</h2>
              {stats && (
                <p className="text-xs text-gray-500 dark:text-gray-500 mt-1">
                  {stats.total_experiences} 条面经 · {stats.total_questions} 个问题 ·{' '}
                  {stats.unique_companies} 家公司
                </p>
              )}
            </div>
            <button
              onClick={() => setShowExportModal(true)}
              className="flex items-center gap-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors text-sm font-medium"
            >
              <Download className="w-4 h-4" />
              一键导出
            </button>
          </div>

          {/* View Mode Toggle */}
          <div className="flex gap-2 mb-4">
            <button
              onClick={() => setViewMode('experiences')}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                viewMode === 'experiences'
                  ? 'bg-primary-600 text-white'
                  : 'bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 text-gray-700 dark:text-gray-300 hover:border-gray-300 dark:hover:border-gray-700'
              }`}
            >
              <Grid className="w-4 h-4" />
              按面经排列
            </button>
            <button
              onClick={() => setViewMode('questions')}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                viewMode === 'questions'
                  ? 'bg-primary-600 text-white'
                  : 'bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 text-gray-700 dark:text-gray-300 hover:border-gray-300 dark:hover:border-gray-700'
              }`}
            >
              <List className="w-4 h-4" />
              按题目排列
            </button>
          </div>

          {/* Search and Filter Toggle */}
          <div className="flex gap-2">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
              <input
                type="text"
                placeholder={viewMode === 'experiences' ? '搜索公司...' : '搜索题目...'}
                value={viewMode === 'experiences' ? companyFilter : questionSearch}
                onChange={(e) =>
                  viewMode === 'experiences'
                    ? setCompanyFilter(e.target.value)
                    : setQuestionSearch(e.target.value)
                }
                className="w-full pl-9 pr-4 py-2 text-sm bg-white dark:bg-gray-900 text-gray-900 dark:text-white rounded-lg border border-gray-200 dark:border-gray-800 focus:border-gray-300 dark:focus:border-gray-700 focus:outline-none transition-colors"
              />
            </div>
            <button
              onClick={() => setShowFilters(!showFilters)}
              className={`px-4 py-2 text-sm rounded-lg border transition-colors flex items-center gap-2 ${
                showFilters
                  ? 'bg-primary-600 border-primary-600 text-white'
                  : 'bg-white dark:bg-gray-900 border-gray-200 dark:border-gray-800 text-gray-700 dark:text-gray-300 hover:border-gray-300 dark:hover:border-gray-700'
              }`}
            >
              <Filter className="w-4 h-4" />
              筛选
            </button>
            <button
              onClick={handleResetFilters}
              className="px-4 py-2 text-sm bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 text-gray-700 dark:text-gray-300 rounded-lg hover:border-gray-300 dark:hover:border-gray-700 transition-colors flex items-center gap-2"
            >
              <RotateCcw className="w-3.5 h-3.5" />
              重置
            </button>
          </div>
        </div>

        {/* Filter Panel */}
        {showFilters && (
          <div className="border-t border-gray-100 dark:border-gray-800 bg-gray-50 dark:bg-gray-900/50 transition-colors">
            <div className="max-w-7xl mx-auto px-6 py-5 space-y-5">
              {/* Time Filter */}
              {viewMode === 'experiences' && (
                <div>
                  <label className="flex items-center gap-2 text-xs font-medium text-gray-600 dark:text-gray-400 mb-3">
                    <Calendar className="w-3.5 h-3.5" />
                    时间范围
                  </label>
                  <div className="space-y-3">
                    {/* Preset buttons */}
                    <div className="flex flex-wrap gap-2">
                      {[
                        { value: 'all', label: '全部' },
                        { value: 'today', label: '今天' },
                        { value: '3d', label: '3天' },
                        { value: '7d', label: '7天' },
                        { value: '30d', label: '30天' },
                        { value: '90d', label: '90天' },
                        { value: 'custom', label: '自定义' },
                      ].map((option) => (
                        <button
                          key={option.value}
                          onClick={() => {
                            setTimeFilter(option.value as any)
                            // Clear custom dates when switching to preset
                            if (option.value !== 'custom') {
                              setCustomStartDate('')
                              setCustomEndDate('')
                            }
                          }}
                          className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${
                            timeFilter === option.value
                              ? 'bg-primary-600 text-white'
                              : 'bg-white dark:bg-gray-900 text-gray-600 dark:text-gray-400 border border-gray-200 dark:border-gray-800 hover:text-gray-900 dark:hover:text-white hover:border-gray-300 dark:hover:border-gray-700'
                          }`}
                        >
                          {option.label}
                        </button>
                      ))}
                    </div>

                    {/* Custom date range picker */}
                    {timeFilter === 'custom' && (
                      <div className="flex items-center gap-3 p-3 bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-800">
                        <div className="flex-1">
                          <label className="block text-xs text-gray-500 dark:text-gray-400 mb-1">
                            开始日期
                          </label>
                          <input
                            type="date"
                            value={customStartDate}
                            onChange={(e) => setCustomStartDate(e.target.value)}
                            className="w-full px-2 py-1 text-xs bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded text-gray-900 dark:text-white focus:outline-none focus:border-primary-500"
                          />
                        </div>
                        <span className="text-gray-400 dark:text-gray-600 mt-5">-</span>
                        <div className="flex-1">
                          <label className="block text-xs text-gray-500 dark:text-gray-400 mb-1">
                            结束日期
                          </label>
                          <input
                            type="date"
                            value={customEndDate}
                            onChange={(e) => setCustomEndDate(e.target.value)}
                            className="w-full px-2 py-1 text-xs bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded text-gray-900 dark:text-white focus:outline-none focus:border-primary-500"
                          />
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* Stage Filter */}
              {viewMode === 'experiences' && (
                <div>
                  <label className="flex items-center gap-2 text-xs font-medium text-gray-600 dark:text-gray-400 mb-3">
                    <Building2 className="w-3.5 h-3.5" />
                    面试阶段
                  </label>
                  <div className="flex flex-wrap gap-2">
                    {['', '一面', '二面', '三面', '终面', 'HR面'].map((stage) => (
                      <button
                        key={stage}
                        onClick={() => setStageFilter(stage)}
                        className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${
                          stageFilter === stage
                            ? 'bg-primary-600 text-white'
                            : 'bg-white dark:bg-gray-900 text-gray-600 dark:text-gray-400 border border-gray-200 dark:border-gray-800 hover:text-gray-900 dark:hover:text-white hover:border-gray-300 dark:hover:border-gray-700'
                        }`}
                      >
                        {stage || '全部'}
                      </button>
                    ))}
                  </div>
                </div>
              )}

              {/* Tags Filter */}
              <div>
                <label className="flex items-center gap-2 text-xs font-medium text-gray-600 dark:text-gray-400 mb-3">
                  <Tag className="w-3.5 h-3.5" />
                  技术标签 {selectedTags.length > 0 && `(${selectedTags.length})`}
                </label>
                <div className="flex flex-wrap gap-2 max-h-32 overflow-y-auto">
                  {allTags.slice(0, 30).map((tag) => (
                    <button
                      key={tag}
                      onClick={() => toggleTag(tag)}
                      className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${
                        selectedTags.includes(tag)
                          ? 'bg-primary-600 text-white'
                          : 'bg-white dark:bg-gray-900 text-gray-600 dark:text-gray-400 border border-gray-200 dark:border-gray-800 hover:text-gray-900 dark:hover:text-white hover:border-gray-300 dark:hover:border-gray-700'
                      }`}
                    >
                      {tag}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Content */}
      <div className="max-w-7xl mx-auto px-4 py-8">
        {loading && (
          <div className="text-center py-12">
            <div className="inline-block w-8 h-8 border-4 border-primary-500 border-t-transparent rounded-full animate-spin"></div>
            <p className="text-gray-600 dark:text-gray-400 mt-4">加载中...</p>
          </div>
        )}

        {error && (
          <div className="text-center py-12">
            <p className="text-red-600 dark:text-red-400">{error}</p>
          </div>
        )}

        {!loading && !error && viewMode === 'experiences' && experiences.length === 0 && (
          <div className="text-center py-12">
            <p className="text-gray-600 dark:text-gray-400">没有找到面经记录</p>
            <p className="text-gray-500 text-sm mt-2">尝试调整筛选条件或处理新的面经</p>
          </div>
        )}

        {!loading && !error && viewMode === 'experiences' && experiences.length > 0 && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {experiences.map((experience) => (
              <ExperienceCard
                key={experience.id}
                experience={{
                  ...experience,
                  is_generating_answers: generatingAnswersFor.has(experience.id)
                }}
                onClick={() => handleCardClick(experience.id)}
                onDelete={handleDelete}
                onGenerateAnswers={handleGenerateAnswers}
                isGeneratingAnswers={generatingAnswersFor.has(experience.id)}
              />
            ))}
          </div>
        )}

        {!loading && !error && viewMode === 'questions' && (
          <QuestionGroupView groups={questionGroups} onExperienceClick={handleCardClick} />
        )}
      </div>

      {/* Export Modal */}
      <ExportModal
        isOpen={showExportModal}
        onClose={() => setShowExportModal(false)}
        currentFilters={{
          companyName: companyFilter || undefined,
          tags: selectedTags.length > 0 ? selectedTags : undefined,
          timeRange: timeFilter,
          customStartDate: customStartDate || undefined,
          customEndDate: customEndDate || undefined,
          stage: stageFilter || undefined,
        }}
      />
    </div>
  )
}
