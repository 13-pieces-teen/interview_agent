import { InterviewExperience } from '../types'
import { Building2, Briefcase, MapPin, Tag, Clock } from 'lucide-react'

interface ResultsViewProps {
  experience: InterviewExperience
  processingTime: number
}

export const ResultsView = ({ experience, processingTime }: ResultsViewProps) => {
  return (
    <div className="w-full max-w-4xl mx-auto space-y-6">
      {/* Header Info */}
      <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-2xl font-bold text-white">Interview Experience</h2>
          <span className="text-sm text-gray-400 flex items-center gap-2">
            <Clock className="w-4 h-4" />
            Processed in {processingTime.toFixed(2)}s
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {experience.company_name && (
            <div className="flex items-start gap-3">
              <Building2 className="w-5 h-5 text-primary-400 mt-0.5" />
              <div>
                <p className="text-sm text-gray-400">Company</p>
                <p className="text-white font-medium">{experience.company_name}</p>
              </div>
            </div>
          )}

          {experience.position && (
            <div className="flex items-start gap-3">
              <Briefcase className="w-5 h-5 text-primary-400 mt-0.5" />
              <div>
                <p className="text-sm text-gray-400">Position</p>
                <p className="text-white font-medium">{experience.position}</p>
              </div>
            </div>
          )}

          {experience.company_scale && (
            <div className="flex items-start gap-3">
              <MapPin className="w-5 h-5 text-primary-400 mt-0.5" />
              <div>
                <p className="text-sm text-gray-400">Company Scale</p>
                <p className="text-white font-medium">{experience.company_scale}</p>
              </div>
            </div>
          )}

          {experience.interview_stage && (
            <div className="flex items-start gap-3">
              <Tag className="w-5 h-5 text-primary-400 mt-0.5" />
              <div>
                <p className="text-sm text-gray-400">Interview Stage</p>
                <p className="text-white font-medium">{experience.interview_stage}</p>
              </div>
            </div>
          )}
        </div>

        {experience.tags.length > 0 && (
          <div className="mt-4 pt-4 border-t border-gray-700">
            <p className="text-sm text-gray-400 mb-2">Tags</p>
            <div className="flex flex-wrap gap-2">
              {experience.tags.map((tag, idx) => (
                <span
                  key={idx}
                  className="px-3 py-1 bg-primary-600/20 text-primary-300 rounded-full text-sm"
                >
                  {tag}
                </span>
              ))}
            </div>
          </div>
        )}

        {experience.interview_experience && (
          <div className="mt-4 pt-4 border-t border-gray-700">
            <p className="text-sm text-gray-400 mb-2">Overall Experience</p>
            <p className="text-white whitespace-pre-wrap">{experience.interview_experience}</p>
          </div>
        )}
      </div>

      {/* Questions */}
      <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
        <h3 className="text-xl font-bold text-white mb-4">
          Questions ({experience.questions.length})
        </h3>

        <div className="space-y-4">
          {experience.questions.map((q, idx) => (
            <div
              key={idx}
              className="bg-gray-900 rounded-lg p-4 border border-gray-700"
            >
              <div className="flex items-start gap-3 mb-3">
                <span className="flex-shrink-0 w-8 h-8 bg-primary-600 text-white rounded-full flex items-center justify-center font-bold text-sm">
                  {idx + 1}
                </span>
                <div className="flex-1">
                  <p className="text-white font-medium">{q.question}</p>
                </div>
              </div>

              {q.answer && (
                <div className="ml-11 mb-3">
                  <p className="text-sm text-gray-400 mb-1">Answer</p>
                  <p className="text-gray-300 whitespace-pre-wrap">{q.answer}</p>
                  {!q.has_original_answer && (
                    <span className="inline-block mt-2 px-2 py-1 bg-yellow-600/20 text-yellow-300 rounded text-xs">
                      AI Generated
                    </span>
                  )}
                </div>
              )}

              {q.tags.length > 0 && (
                <div className="ml-11">
                  <div className="flex flex-wrap gap-2">
                    {q.tags.map((tag, tagIdx) => (
                      <span
                        key={tagIdx}
                        className="px-2 py-1 bg-gray-700 text-gray-300 rounded text-xs"
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
  )
}
