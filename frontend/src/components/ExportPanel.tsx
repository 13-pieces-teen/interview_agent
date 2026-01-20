import { Download } from 'lucide-react'
import { downloadFile } from '../services/api'

interface ExportPanelProps {
  outputFiles: string[]
}

export const ExportPanel = ({ outputFiles }: ExportPanelProps) => {
  if (outputFiles.length === 0) return null

  return (
    <div className="w-full max-w-3xl mx-auto">
      <div className="bg-white dark:bg-gray-900 rounded-xl p-6 border border-gray-200 dark:border-gray-800 transition-colors">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-white mb-4">导出文件</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {outputFiles.map((filename) => {
            const isJson = filename.endsWith('.json')
            const isMarkdown = filename.endsWith('.md')

            return (
              <a
                key={filename}
                href={downloadFile(filename)}
                download
                className="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-800/50 rounded-lg border border-gray-100 dark:border-gray-800 hover:border-gray-300 dark:hover:border-gray-700 transition-colors group"
              >
                <div className="flex items-center gap-3">
                  <div className={`w-9 h-9 rounded-lg flex items-center justify-center text-xs font-semibold ${
                    isJson ? 'bg-green-100 dark:bg-green-900/20 text-green-600 dark:text-green-400' :
                    isMarkdown ? 'bg-blue-100 dark:bg-blue-900/20 text-blue-600 dark:text-blue-400' :
                    'bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400'
                  }`}>
                    {isJson ? 'JSON' : isMarkdown ? 'MD' : 'FILE'}
                  </div>
                  <div>
                    <p className="text-sm text-gray-900 dark:text-white font-medium group-hover:text-primary-600 dark:group-hover:text-primary-400 transition-colors">
                      {filename}
                    </p>
                    <p className="text-xs text-gray-500 dark:text-gray-500">
                      {isJson ? 'JSON 格式' : isMarkdown ? 'Markdown 格式' : '文件'}
                    </p>
                  </div>
                </div>
                <Download className="w-4 h-4 text-gray-400 group-hover:text-primary-600 dark:group-hover:text-primary-400 transition-colors" />
              </a>
            )
          })}
        </div>
      </div>
    </div>
  )
}
