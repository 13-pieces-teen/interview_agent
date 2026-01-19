import { Download } from 'lucide-react'
import { downloadFile } from '../services/api'

interface ExportPanelProps {
  outputFiles: string[]
}

export const ExportPanel = ({ outputFiles }: ExportPanelProps) => {
  if (outputFiles.length === 0) return null

  return (
    <div className="w-full max-w-4xl mx-auto">
      <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
        <h3 className="text-lg font-bold text-white mb-4">Export Files</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {outputFiles.map((filename) => {
            const isJson = filename.endsWith('.json')
            const isMarkdown = filename.endsWith('.md')

            return (
              <a
                key={filename}
                href={downloadFile(filename)}
                download
                className="flex items-center justify-between p-4 bg-gray-900 rounded-lg border border-gray-700 hover:border-primary-500 transition-all group"
              >
                <div className="flex items-center gap-3">
                  <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${
                    isJson ? 'bg-green-600/20 text-green-400' :
                    isMarkdown ? 'bg-blue-600/20 text-blue-400' :
                    'bg-gray-600/20 text-gray-400'
                  }`}>
                    {isJson ? 'JSON' : isMarkdown ? 'MD' : 'FILE'}
                  </div>
                  <div>
                    <p className="text-white font-medium text-sm group-hover:text-primary-400 transition-colors">
                      {filename}
                    </p>
                    <p className="text-xs text-gray-500">
                      {isJson ? 'JSON Format' : isMarkdown ? 'Markdown Format' : 'File'}
                    </p>
                  </div>
                </div>
                <Download className="w-5 h-5 text-gray-400 group-hover:text-primary-400 transition-colors" />
              </a>
            )
          })}
        </div>
      </div>
    </div>
  )
}
