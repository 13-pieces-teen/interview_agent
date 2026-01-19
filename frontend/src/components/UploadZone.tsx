import { useState, useCallback, useEffect, useRef } from 'react'
import { useDropzone } from 'react-dropzone'
import { Upload, FileText, Image as ImageIcon, Loader2, X, Clipboard } from 'lucide-react'
import clsx from 'clsx'

interface UploadZoneProps {
  onTextSubmit: (text: string) => void
  onImagesSubmit: (files: File[]) => void
  isProcessing: boolean
}

export const UploadZone = ({ onTextSubmit, onImagesSubmit, isProcessing }: UploadZoneProps) => {
  const [inputMode, setInputMode] = useState<'text' | 'image'>('text')
  const [textContent, setTextContent] = useState('')
  const [selectedImages, setSelectedImages] = useState<File[]>([])
  const [imagePreviews, setImagePreviews] = useState<string[]>([])
  const fileInputRef = useRef<HTMLInputElement>(null)

  // Handle paste event for images
  useEffect(() => {
    const handlePaste = (e: ClipboardEvent) => {
      if (inputMode !== 'image' || isProcessing) return

      const items = e.clipboardData?.items
      if (!items) return

      const imageFiles: File[] = []

      for (let i = 0; i < items.length; i++) {
        const item = items[i]
        if (item.type.startsWith('image/')) {
          const file = item.getAsFile()
          if (file) {
            imageFiles.push(file)
          }
        }
      }

      if (imageFiles.length > 0) {
        e.preventDefault()
        addImages(imageFiles)
      }
    }

    document.addEventListener('paste', handlePaste)
    return () => document.removeEventListener('paste', handlePaste)
  }, [inputMode, isProcessing])

  // Create image previews
  useEffect(() => {
    const previews: string[] = []
    selectedImages.forEach((file) => {
      const url = URL.createObjectURL(file)
      previews.push(url)
    })
    setImagePreviews(previews)

    // Cleanup URLs on unmount
    return () => {
      previews.forEach((url) => URL.revokeObjectURL(url))
    }
  }, [selectedImages])

  const addImages = useCallback(
    (files: File[]) => {
      if (isProcessing) return
      setSelectedImages((prev) => [...prev, ...files])
    },
    [isProcessing]
  )

  const removeImage = useCallback((index: number) => {
    setSelectedImages((prev) => prev.filter((_, i) => i !== index))
  }, [])

  const clearAllImages = useCallback(() => {
    setSelectedImages([])
  }, [])

  const onDrop = useCallback(
    (acceptedFiles: File[]) => {
      if (!isProcessing) {
        addImages(acceptedFiles)
      }
    },
    [addImages, isProcessing]
  )

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/*': ['.png', '.jpg', '.jpeg', '.gif', '.webp', '.bmp'],
    },
    multiple: true,
    disabled: isProcessing,
    noClick: selectedImages.length > 0, // 如果已有图片，点击不打开文件选择
  })

  const handleTextSubmit = () => {
    if (textContent.trim() && !isProcessing) {
      onTextSubmit(textContent)
    }
  }

  const handleImagesSubmit = () => {
    if (selectedImages.length > 0 && !isProcessing) {
      onImagesSubmit(selectedImages)
    }
  }

  const handleSelectFiles = () => {
    fileInputRef.current?.click()
  }

  return (
    <div className="w-full max-w-4xl mx-auto">
      <div className="flex gap-4 mb-6">
        <button
          onClick={() => setInputMode('text')}
          className={clsx(
            'flex-1 py-3 px-6 rounded-lg font-medium transition-all',
            inputMode === 'text'
              ? 'bg-primary-600 text-white shadow-lg'
              : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
          )}
          disabled={isProcessing}
        >
          <FileText className="inline-block mr-2 w-5 h-5" />
          Text Input
        </button>
        <button
          onClick={() => setInputMode('image')}
          className={clsx(
            'flex-1 py-3 px-6 rounded-lg font-medium transition-all',
            inputMode === 'image'
              ? 'bg-primary-600 text-white shadow-lg'
              : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
          )}
          disabled={isProcessing}
        >
          <ImageIcon className="inline-block mr-2 w-5 h-5" />
          Image Upload ({selectedImages.length})
        </button>
      </div>

      {inputMode === 'text' ? (
        <div className="space-y-4">
          <textarea
            value={textContent}
            onChange={(e) => setTextContent(e.target.value)}
            placeholder="Paste your interview experience here..."
            className="w-full h-64 p-4 bg-gray-800 border border-gray-700 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-primary-500 resize-none"
            disabled={isProcessing}
          />
          <button
            onClick={handleTextSubmit}
            disabled={!textContent.trim() || isProcessing}
            className="w-full py-3 px-6 bg-primary-600 text-white rounded-lg font-medium hover:bg-primary-700 disabled:bg-gray-700 disabled:cursor-not-allowed transition-all flex items-center justify-center gap-2"
          >
            {isProcessing ? (
              <>
                <Loader2 className="w-5 h-5 animate-spin" />
                Processing...
              </>
            ) : (
              <>
                <Upload className="w-5 h-5" />
                Process Interview Experience
              </>
            )}
          </button>
        </div>
      ) : (
        <div className="space-y-4">
          {/* Drop Zone */}
          <div
            {...getRootProps()}
            className={clsx(
              'border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-all',
              isDragActive
                ? 'border-primary-500 bg-primary-500/10'
                : 'border-gray-700 hover:border-gray-600 bg-gray-800/50',
              isProcessing && 'opacity-50 cursor-not-allowed',
              selectedImages.length > 0 && 'p-6'
            )}
          >
            <input {...getInputProps()} />
            <input
              ref={fileInputRef}
              type="file"
              multiple
              accept="image/*"
              onChange={(e) => {
                const files = Array.from(e.target.files || [])
                if (files.length > 0) {
                  addImages(files)
                }
              }}
              className="hidden"
            />

            {selectedImages.length === 0 ? (
              <>
                <Upload className="w-16 h-16 mx-auto mb-4 text-gray-400" />
                {isDragActive ? (
                  <p className="text-lg text-primary-400">Drop images here...</p>
                ) : (
                  <>
                    <p className="text-lg text-gray-300 mb-2">
                      Drag & drop images here, or click to select
                    </p>
                    <p className="text-sm text-gray-500 mb-3">
                      Supports PNG, JPG, JPEG, GIF, WebP, BMP
                    </p>
                    <div className="flex items-center justify-center gap-2 text-sm text-primary-400">
                      <Clipboard className="w-4 h-4" />
                      <span>Or press Ctrl+V to paste from clipboard</span>
                    </div>
                  </>
                )}
              </>
            ) : (
              <div className="flex items-center justify-center gap-4 text-sm text-gray-400">
                <button
                  onClick={(e) => {
                    e.stopPropagation()
                    handleSelectFiles()
                  }}
                  className="px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg transition-all"
                >
                  Add More Images
                </button>
                <span>or drag & drop more files</span>
                <div className="flex items-center gap-2 text-primary-400">
                  <Clipboard className="w-4 h-4" />
                  <span>Ctrl+V to paste</span>
                </div>
              </div>
            )}
          </div>

          {/* Image Previews */}
          {selectedImages.length > 0 && (
            <div className="bg-gray-800 border border-gray-700 rounded-lg p-4">
              <div className="flex items-center justify-between mb-3">
                <h3 className="text-white font-medium">
                  Selected Images ({selectedImages.length})
                </h3>
                <button
                  onClick={clearAllImages}
                  disabled={isProcessing}
                  className="text-sm text-red-400 hover:text-red-300 transition-colors disabled:opacity-50"
                >
                  Clear All
                </button>
              </div>

              <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
                {selectedImages.map((file, index) => (
                  <div
                    key={`${file.name}-${index}`}
                    className="relative group aspect-square bg-gray-900 rounded-lg overflow-hidden border border-gray-700"
                  >
                    <img
                      src={imagePreviews[index]}
                      alt={file.name}
                      className="w-full h-full object-cover"
                    />
                    <div className="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
                      <button
                        onClick={() => removeImage(index)}
                        disabled={isProcessing}
                        className="p-2 bg-red-600 hover:bg-red-700 rounded-full transition-colors disabled:opacity-50"
                      >
                        <X className="w-4 h-4 text-white" />
                      </button>
                    </div>
                    <div className="absolute bottom-0 left-0 right-0 bg-black/70 p-2">
                      <p className="text-xs text-gray-300 truncate">{file.name}</p>
                      <p className="text-xs text-gray-500">
                        {(file.size / 1024).toFixed(1)} KB
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Submit Button */}
          <button
            onClick={handleImagesSubmit}
            disabled={selectedImages.length === 0 || isProcessing}
            className="w-full py-3 px-6 bg-primary-600 text-white rounded-lg font-medium hover:bg-primary-700 disabled:bg-gray-700 disabled:cursor-not-allowed transition-all flex items-center justify-center gap-2"
          >
            {isProcessing ? (
              <>
                <Loader2 className="w-5 h-5 animate-spin" />
                Processing {selectedImages.length} image(s)...
              </>
            ) : (
              <>
                <Upload className="w-5 h-5" />
                Process {selectedImages.length} Image(s)
              </>
            )}
          </button>
        </div>
      )}
    </div>
  )
}
