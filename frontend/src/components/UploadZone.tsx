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
    <div className="w-full max-w-3xl mx-auto">
      <div className="flex gap-2 mb-6">
        <button
          onClick={() => setInputMode('text')}
          className={clsx(
            'flex-1 py-3 px-4 rounded-lg text-sm font-medium transition-colors',
            inputMode === 'text'
              ? 'bg-primary-600 text-white'
              : 'bg-white dark:bg-gray-900 text-gray-600 dark:text-gray-400 border border-gray-200 dark:border-gray-800 hover:text-gray-900 dark:hover:text-white hover:border-gray-300 dark:hover:border-gray-700'
          )}
          disabled={isProcessing}
        >
          <FileText className="inline-block mr-2 w-4 h-4" />
          文本输入
        </button>
        <button
          onClick={() => setInputMode('image')}
          className={clsx(
            'flex-1 py-3 px-4 rounded-lg text-sm font-medium transition-colors',
            inputMode === 'image'
              ? 'bg-primary-600 text-white'
              : 'bg-white dark:bg-gray-900 text-gray-600 dark:text-gray-400 border border-gray-200 dark:border-gray-800 hover:text-gray-900 dark:hover:text-white hover:border-gray-300 dark:hover:border-gray-700'
          )}
          disabled={isProcessing}
        >
          <ImageIcon className="inline-block mr-2 w-4 h-4" />
          图片上传 {selectedImages.length > 0 && `(${selectedImages.length})`}
        </button>
      </div>

      {inputMode === 'text' ? (
        <div className="space-y-4">
          <textarea
            value={textContent}
            onChange={(e) => setTextContent(e.target.value)}
            placeholder="粘贴你的面经内容..."
            className="w-full h-72 p-6 bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-xl text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-600 focus:outline-none focus:ring-1 focus:ring-gray-300 dark:focus:ring-gray-700 resize-none transition-colors text-sm"
            disabled={isProcessing}
          />
          <button
            onClick={handleTextSubmit}
            disabled={!textContent.trim() || isProcessing}
            className="w-full py-3 px-6 bg-primary-600 text-white rounded-lg text-sm font-medium hover:bg-primary-700 disabled:bg-gray-200 dark:disabled:bg-gray-800 disabled:text-gray-400 dark:disabled:text-gray-600 disabled:cursor-not-allowed transition-colors flex items-center justify-center gap-2"
          >
            {isProcessing ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                处理中...
              </>
            ) : (
              <>
                <Upload className="w-4 h-4" />
                开始处理
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
              'border-2 border-dashed rounded-xl p-12 text-center cursor-pointer transition-all',
              isDragActive
                ? 'border-primary-400 bg-primary-50/50 dark:bg-primary-950/20'
                : 'border-gray-200 dark:border-gray-800 hover:border-gray-300 dark:hover:border-gray-700 bg-white dark:bg-gray-900',
              isProcessing && 'opacity-50 cursor-not-allowed',
              selectedImages.length > 0 && 'p-8'
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
                <Upload className="w-12 h-12 mx-auto mb-4 text-gray-300 dark:text-gray-700" />
                {isDragActive ? (
                  <p className="text-sm text-primary-600">释放文件...</p>
                ) : (
                  <>
                    <p className="text-sm text-gray-900 dark:text-white mb-1">
                      拖拽图片到这里，或点击选择文件
                    </p>
                    <p className="text-xs text-gray-500 dark:text-gray-500 mb-4">
                      支持 PNG、JPG、JPEG、GIF、WebP、BMP
                    </p>
                    <div className="flex items-center justify-center gap-2 text-xs text-gray-400 dark:text-gray-600">
                      <Clipboard className="w-3.5 h-3.5" />
                      <span>或按 Ctrl+V 从剪贴板粘贴</span>
                    </div>
                  </>
                )}
              </>
            ) : (
              <div className="flex items-center justify-center gap-4 text-xs text-gray-600 dark:text-gray-400">
                <button
                  onClick={(e) => {
                    e.stopPropagation()
                    handleSelectFiles()
                  }}
                  className="px-3 py-1.5 bg-gray-100 dark:bg-gray-800 hover:bg-gray-200 dark:hover:bg-gray-700 rounded-lg transition-colors text-gray-700 dark:text-gray-300"
                >
                  添加更多图片
                </button>
                <span>或拖拽文件到这里</span>
              </div>
            )}
          </div>

          {/* Image Previews */}
          {selectedImages.length > 0 && (
            <div className="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-xl p-5 transition-colors">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-sm font-medium text-gray-900 dark:text-white">
                  已选择 {selectedImages.length} 张图片
                </h3>
                <button
                  onClick={clearAllImages}
                  disabled={isProcessing}
                  className="text-xs text-red-600 dark:text-red-400 hover:text-red-700 dark:hover:text-red-300 transition-colors disabled:opacity-50"
                >
                  清空
                </button>
              </div>

              <div className="grid grid-cols-3 md:grid-cols-4 gap-3">
                {selectedImages.map((file, index) => (
                  <div
                    key={`${file.name}-${index}`}
                    className="relative group aspect-square bg-gray-50 dark:bg-gray-800 rounded-lg overflow-hidden border border-gray-100 dark:border-gray-800"
                  >
                    <img
                      src={imagePreviews[index]}
                      alt={file.name}
                      className="w-full h-full object-cover"
                    />
                    <div className="absolute inset-0 bg-black/60 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
                      <button
                        onClick={() => removeImage(index)}
                        disabled={isProcessing}
                        className="p-1.5 bg-red-600 hover:bg-red-700 rounded-lg transition-colors disabled:opacity-50"
                      >
                        <X className="w-3.5 h-3.5 text-white" />
                      </button>
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
            className="w-full py-3 px-6 bg-primary-600 text-white rounded-lg text-sm font-medium hover:bg-primary-700 disabled:bg-gray-200 dark:disabled:bg-gray-800 disabled:text-gray-400 dark:disabled:text-gray-600 disabled:cursor-not-allowed transition-colors flex items-center justify-center gap-2"
          >
            {isProcessing ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                处理 {selectedImages.length} 张图片中...
              </>
            ) : (
              <>
                <Upload className="w-4 h-4" />
                处理 {selectedImages.length} 张图片
              </>
            )}
          </button>
        </div>
      )}
    </div>
  )
}
