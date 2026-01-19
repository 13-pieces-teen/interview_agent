export interface Question {
  question: string
  answer?: string
  has_original_answer: boolean
  tags: string[]
}

export interface InterviewExperience {
  source_type: string
  company_name?: string
  company_scale?: string
  position?: string
  interview_stage?: string
  interview_experience?: string
  questions: Question[]
  tags: string[]
  raw_content: string
}

export interface ProcessResponse {
  success: boolean
  processing_time: number
  experience?: InterviewExperience
  output_files: string[]
  error?: string
}

export interface FileInfo {
  filename: string
  size: number
  created_at: string
  modified_at: string
}
