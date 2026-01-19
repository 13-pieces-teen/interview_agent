import axios from 'axios'
import type { ProcessResponse, FileInfo } from '../types'

const API_BASE = import.meta.env.VITE_API_BASE || '/api'

export const api = axios.create({
  baseURL: API_BASE,
  timeout: 120000, // Increased timeout for multiple images
  headers: {
    'Content-Type': 'application/json',
  },
})

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
