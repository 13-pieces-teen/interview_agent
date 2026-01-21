export interface Question {
  id: string
  question: string
  answer?: string
  has_original_answer: boolean
  tags: string[]
}

export interface InterviewExperience {
  id: string
  created_at: string
  source_type: string
  company_name?: string
  company_scale?: string
  position?: string
  interview_stage?: string
  interview_experience?: string
  questions: Question[]
  tags: string[]
  raw_content: string
  notes?: string
  processing_time?: number
}

export interface ProcessResponse {
  success: boolean
  processing_time: number
  experience?: InterviewExperience
  experience_id?: string
  output_files: string[]
  error?: string
  validation_score?: number
  validation_message?: string
}

export interface ValidationResponse {
  is_valid: boolean
  confidence_score: number
  message: string
}

export interface FileInfo {
  filename: string
  size: number
  created_at: string
  modified_at: string
}

export interface ExperienceListItem {
  id: string
  created_at: string
  source_type: string
  company_name?: string
  company_scale?: string
  position?: string
  interview_stage?: string
  interview_experience?: string
  tags: string[]
  questions_count: number
  has_answers: boolean
  notes?: string
  processing_time?: number
  is_generating_answers?: boolean  // 是否正在生成答案
}

export interface QuestionGroup {
  question: string
  count: number
  tags: string[]
  occurrences: Array<{
    experience_id: string
    company_name?: string
    position?: string
    interview_stage?: string
    answer?: string
    has_original_answer: boolean
    created_at: string
  }>
}

export interface QuestionGroupsResponse {
  total: number
  groups: QuestionGroup[]
}

export interface AnswerGenerationTaskResponse {
  task_id: string
  status: string
  message: string
  total_questions: number
}

export interface AnswerGenerationTaskStatus {
  status: string  // pending, processing, completed, failed
  experience_id: string
  progress: number
  total_questions: number
  created_at: string
  completed_at?: string
  error?: string
}
