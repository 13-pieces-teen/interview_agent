import axios from 'axios'
import type {
  ProcessResponse,
  FileInfo,
  InterviewExperience,
  ExperienceListItem,
  ValidationResponse,
  QuestionGroupsResponse,
  AnswerGenerationTaskResponse,
  AnswerGenerationTaskStatus
} from '../types'

const API_BASE = import.meta.env.VITE_API_BASE || '/api'

export const api = axios.create({
  baseURL: API_BASE,
  timeout: 120000, // Increased timeout for multiple images
  headers: {
    'Content-Type': 'application/json',
  },
})

// Add response interceptor for better error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.code === 'ECONNABORTED' || error.code === 'ERR_NETWORK') {
      console.error('Network error:', error)
      return Promise.reject(new Error('Connection error. Please check if the backend server is running.'))
    }

    if (error.response) {
      // Server responded with error status
      const message = error.response.data?.detail || error.response.data?.error || error.response.statusText
      console.error('API error:', error.response.status, message)
      return Promise.reject(new Error(`Server error: ${message}`))
    }

    if (error.request) {
      // Request was made but no response received
      console.error('No response from server:', error.request)
      return Promise.reject(new Error('No response from server. Please check if the backend is running on http://localhost:8000'))
    }

    // Something else happened
    console.error('Request error:', error.message)
    return Promise.reject(error)
  }
)

export const processText = async (
  content: string,
  generateAnswers: boolean = false,
  exportFormat: string = 'both'
): Promise<ProcessResponse> => {
  const response = await api.post<ProcessResponse>('/process/text', {
    content,
    generate_answers: generateAnswers,
    export_format: exportFormat,
  })
  return response.data
}

export const processImage = async (
  file: File,
  generateAnswers: boolean = false,
  exportFormat: string = 'both'
): Promise<ProcessResponse> => {
  const formData = new FormData()
  formData.append('file', file)
  formData.append('generate_answers', String(generateAnswers))
  formData.append('export_format', exportFormat)

  const response = await api.post<ProcessResponse>('/process/image', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  })
  return response.data
}

export const processImages = async (
  files: File[],
  generateAnswers: boolean = false,
  exportFormat: string = 'both'
): Promise<ProcessResponse> => {
  const formData = new FormData()

  // Add all files
  files.forEach((file) => {
    formData.append('files', file)
  })

  formData.append('generate_answers', String(generateAnswers))
  formData.append('export_format', exportFormat)

  const response = await api.post<ProcessResponse>('/process/images', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
    timeout: 180000, // 3 minutes for multiple images
  })
  return response.data
}

export const listFiles = async (): Promise<FileInfo[]> => {
  const response = await api.get<{ files: FileInfo[] }>('/files')
  return response.data.files
}

export const downloadFile = (filename: string): string => {
  return `${API_BASE}/download/${filename}`
}

export const validateContent = async (content: string): Promise<ValidationResponse> => {
  const response = await api.post<ValidationResponse>('/validate', {
    content,
  })
  return response.data
}

// Database API functions
export const listExperiences = async (params?: {
  companyName?: string
  companyScale?: string
  tags?: string[]
  startDate?: string
  endDate?: string
  interviewStage?: string
  limit?: number
  offset?: number
}): Promise<{ experiences: ExperienceListItem[]; count: number }> => {
  const queryParams = new URLSearchParams()

  if (params?.companyName) queryParams.append('company_name', params.companyName)
  if (params?.companyScale) queryParams.append('company_scale', params.companyScale)
  if (params?.tags?.length) queryParams.append('tags', params.tags.join(','))
  if (params?.startDate) queryParams.append('start_date', params.startDate)
  if (params?.endDate) queryParams.append('end_date', params.endDate)
  if (params?.interviewStage) queryParams.append('interview_stage', params.interviewStage)
  if (params?.limit) queryParams.append('limit', String(params.limit))
  if (params?.offset) queryParams.append('offset', String(params.offset))

  const response = await api.get(`/experiences?${queryParams.toString()}`)
  return response.data
}

export const getExperience = async (
  experienceId: string
): Promise<{ experience: InterviewExperience }> => {
  const response = await api.get(`/experiences/${experienceId}`)
  return response.data
}

export const deleteExperience = async (
  experienceId: string
): Promise<{ success: boolean; message: string }> => {
  const response = await api.delete(`/experiences/${experienceId}`)
  return response.data
}

export const getAllTags = async (): Promise<{ tags: string[] }> => {
  const response = await api.get('/tags')
  return response.data
}

export const getAllCompanies = async (): Promise<{ companies: string[] }> => {
  const response = await api.get('/companies')
  return response.data
}

export const getStats = async (): Promise<{
  total_experiences: number
  total_questions: number
  unique_companies: number
}> => {
  const response = await api.get('/stats')
  return response.data
}

export const updateExperience = async (
  experienceId: string,
  updates: {
    company_name?: string
    company_scale?: string
    position?: string
    interview_stage?: string
    interview_experience?: string
    tags?: string[]
    questions?: any[]
  }
): Promise<{ success: boolean; experience: InterviewExperience }> => {
  const response = await api.put(`/experiences/${experienceId}`, updates)
  return response.data
}

export const getGroupedQuestions = async (params?: {
  search?: string
  tags?: string[]
  companyName?: string
  limit?: number
  offset?: number
}): Promise<QuestionGroupsResponse> => {
  const queryParams = new URLSearchParams()

  if (params?.search) queryParams.append('search', params.search)
  if (params?.tags?.length) queryParams.append('tags', params.tags.join(','))
  if (params?.companyName) queryParams.append('company_name', params.companyName)
  if (params?.limit) queryParams.append('limit', String(params.limit))
  if (params?.offset) queryParams.append('offset', String(params.offset))

  const response = await api.get(`/questions/grouped?${queryParams.toString()}`)
  return response.data
}

// Batch processing API functions
export const processBatch = async (
  files: File[],
  generateAnswers: boolean = false,
  exportFormat: string = 'both'
): Promise<{ task_id: string; total_files: number; status: string; message: string }> => {
  const formData = new FormData()

  // Add all files
  files.forEach((file) => {
    formData.append('files', file)
  })

  formData.append('generate_answers', String(generateAnswers))
  formData.append('export_format', exportFormat)

  const response = await api.post('/process/batch', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
    timeout: 30000, // 30 seconds to create batch task
  })
  return response.data
}

export const getBatchStatus = async (taskId: string): Promise<{
  id: string
  total_files: number
  created_at: string
  status: string
  current_index: number
  completed_count: number
  failed_count: number
  started_at: string | null
  completed_at: string | null
  generate_answers: boolean
  export_format: string
  sub_tasks: Array<{
    id: string
    file_name: string
    status: string
    error: string | null
    experience_id: string | null
    started_at: string | null
    completed_at: string | null
    processing_time: number
  }>
}> => {
  const response = await api.get(`/batch/${taskId}`)
  return response.data
}

export const listBatchTasks = async (status?: string): Promise<{
  tasks: any[]
  total: number
}> => {
  const queryParams = status ? `?status=${status}` : ''
  const response = await api.get(`/batch${queryParams}`)
  return response.data
}

export const cancelBatchTask = async (taskId: string): Promise<{
  success: boolean
  message: string
}> => {
  const response = await api.delete(`/batch/${taskId}`)
  return response.data
}

// Async task queue API functions
export const processTextAsync = async (
  content: string,
  generateAnswers: boolean = false,
  exportFormat: string = 'both'
): Promise<{ task_id: string; status: string; message: string }> => {
  const response = await api.post('/process/text/async', {
    content,
    generate_answers: generateAnswers,
    export_format: exportFormat,
  })
  return response.data
}

export const processImagesAsync = async (
  files: File[],
  generateAnswers: boolean = false,
  exportFormat: string = 'both'
): Promise<{ task_id: string; status: string; file_count: number; message: string }> => {
  const formData = new FormData()

  files.forEach((file) => {
    formData.append('files', file)
  })

  formData.append('generate_answers', String(generateAnswers))
  formData.append('export_format', exportFormat)

  const response = await api.post('/process/images/async', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
    timeout: 30000,
  })
  return response.data
}

export const getAsyncTaskStatus = async (taskId: string): Promise<{
  id: string
  type: string
  status: string
  created_at: string
  started_at: string | null
  completed_at: string | null
  processing_time: number
  result: any
  error: string | null
  metadata: any
}> => {
  const response = await api.get(`/tasks/async/${taskId}`)
  return response.data
}

export const listAsyncTasks = async (status?: string): Promise<{
  tasks: any[]
  total: number
}> => {
  const queryParams = status ? `?status=${status}` : ''
  const response = await api.get(`/tasks/async${queryParams}`)
  return response.data
}

export const getQueueInfo = async (): Promise<{
  total_tasks: number
  queued: number
  processing: number
  completed: number
  failed: number
  queue_size: number
  is_running: boolean
}> => {
  const response = await api.get('/tasks/queue/info')
  return response.data
}

// Answer generation API functions
export const generateAnswers = async (
  experienceId: string
): Promise<AnswerGenerationTaskResponse> => {
  const response = await api.post(`/experiences/${experienceId}/generate-answers`)
  return response.data
}

export const getAnswerGenerationTaskStatus = async (
  taskId: string
): Promise<AnswerGenerationTaskStatus> => {
  const response = await api.get(`/tasks/answer-generation/${taskId}`)
  return response.data
}
