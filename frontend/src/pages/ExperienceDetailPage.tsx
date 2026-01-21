import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { Loader2 } from 'lucide-react'
import { getExperience, getAnswerGenerationTaskStatus } from '../services/api'
import { ResultsView } from '../components/ResultsView'

export function ExperienceDetailPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [experience, setExperience] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [isGenerating, setIsGenerating] = useState(false)

  useEffect(() => {
    if (id) {
      loadExperience(id)
    }
  }, [id])

  const loadExperience = async (experienceId: string) => {
    try {
      setLoading(true)
      setError(null)
      const { experience: data } = await getExperience(experienceId)
      setExperience(data)

      // Check if answers are being generated
      if (data.is_generating_answers) {
        setIsGenerating(true)
        pollForAnswerGeneration(experienceId)
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load experience')
    } finally {
      setLoading(false)
    }
  }

  const pollForAnswerGeneration = async (experienceId: string) => {
    // This is a simplified polling - in production you'd want to track the actual task_id
    const interval = setInterval(async () => {
      try {
        const { experience: data } = await getExperience(experienceId)

        if (!data.is_generating_answers) {
          setIsGenerating(false)
          setExperience(data)
          clearInterval(interval)
        }
      } catch (err) {
        console.error('Failed to poll for updates:', err)
        clearInterval(interval)
        setIsGenerating(false)
      }
    }, 3000)

    // Clean up on unmount
    return () => clearInterval(interval)
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-white dark:bg-gray-950 flex items-center justify-center">
        <div className="text-center">
          <div className="inline-block w-8 h-8 border-4 border-primary-500 border-t-transparent rounded-full animate-spin"></div>
          <p className="text-gray-600 dark:text-gray-400 mt-4">加载中...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen bg-white dark:bg-gray-950 flex items-center justify-center">
        <div className="text-center">
          <p className="text-red-600 dark:text-red-400 mb-4">{error}</p>
          <button
            onClick={() => navigate('/gallery')}
            className="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white border border-gray-200 dark:border-gray-700 rounded-lg hover:border-gray-300 dark:hover:border-gray-600 transition-colors"
          >
            返回列表
          </button>
        </div>
      </div>
    )
  }

  if (!experience) {
    return (
      <div className="min-h-screen bg-white dark:bg-gray-950 flex items-center justify-center">
        <div className="text-center">
          <p className="text-gray-600 dark:text-gray-400 mb-4">未找到面经记录</p>
          <button
            onClick={() => navigate('/gallery')}
            className="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white border border-gray-200 dark:border-gray-700 rounded-lg hover:border-gray-300 dark:hover:border-gray-600 transition-colors"
          >
            返回列表
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-white dark:bg-gray-950 transition-colors">
      <div className="max-w-5xl mx-auto px-6 py-8">
        <div className="mb-8">
          <button
            onClick={() => navigate('/gallery')}
            className="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white border border-gray-200 dark:border-gray-800 rounded-lg hover:border-gray-300 dark:hover:border-gray-700 transition-colors"
          >
            ← 返回列表
          </button>
        </div>

        {/* Show generation indicator if this experience is generating answers */}
        {isGenerating && (
          <div className="mb-6 p-4 bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800 rounded-lg">
            <div className="flex items-center gap-3">
              <Loader2 className="w-5 h-5 text-amber-700 dark:text-amber-400 animate-spin" />
              <div>
                <p className="text-sm font-medium text-amber-900 dark:text-amber-100">AI正在生成答案...</p>
                <p className="text-xs text-amber-700 dark:text-amber-300 mt-1">答案生成完成后将自动刷新显示</p>
              </div>
            </div>
          </div>
        )}

        <ResultsView
          experience={experience}
          processingTime={experience.processing_time || 0}
        />
      </div>
    </div>
  )
}
