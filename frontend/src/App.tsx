import { BrowserRouter, Routes, Route, Outlet, Link, useLocation } from 'react-router-dom'
import { Brain, History, Sun, Moon, List } from 'lucide-react'
import { HomePage } from './pages/HomePage'
import { GalleryPage } from './pages/GalleryPage'
import { ExperienceDetailPage } from './pages/ExperienceDetailPage'
import { useTheme } from './contexts/ThemeContext'
import { useState } from 'react'

function Layout() {
  const { theme, toggleTheme } = useTheme()
  const [showTaskQueue, setShowTaskQueue] = useState(false)
  const location = useLocation()

  return (
    <div className="min-h-screen bg-white dark:bg-gray-950 transition-colors">
      {/* Header */}
      <header className="border-b border-gray-100 dark:border-gray-800 transition-colors">
        <div className="max-w-7xl mx-auto px-6 py-8">
          <div className="flex items-center justify-between">
            <Link to="/" className="flex items-center gap-4 hover:opacity-80 transition-opacity">
              <div className="w-10 h-10 bg-primary-600 rounded-xl flex items-center justify-center">
                <Brain className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-semibold text-gray-900 dark:text-white">Interview Agent</h1>
              </div>
            </Link>

            {/* Action Buttons */}
            <div className="flex items-center gap-6">
              {/* Task Queue Toggle - Only show on home page */}
              {location.pathname === '/' && (
                <button
                  onClick={() => setShowTaskQueue(!showTaskQueue)}
                  className="flex items-center gap-2 px-4 py-2 text-gray-700 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white transition-colors"
                  title="任务队列"
                >
                  <List className="w-4 h-4" />
                  <span className="text-sm font-medium">任务队列</span>
                </button>
              )}

              {/* Theme Toggle */}
              <button
                onClick={toggleTheme}
                className="p-2 text-gray-500 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white transition-colors"
                title={theme === 'dark' ? '切换到浅色模式' : '切换到深色模式'}
              >
                {theme === 'dark' ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
              </button>

              {/* History Button */}
              <Link
                to="/gallery"
                className="flex items-center gap-2 px-4 py-2 text-gray-700 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white transition-colors"
              >
                <History className="w-4 h-4" />
                <span className="text-sm font-medium">历史记录</span>
              </Link>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <Outlet context={{ showTaskQueue }} />

      {/* Footer */}
      <footer className="mt-20 py-8 border-t border-gray-100 dark:border-gray-800">
        <div className="max-w-5xl mx-auto px-6 text-center text-gray-400 dark:text-gray-600 text-xs">
          <p>Powered by DeepSeek-V3.2 and GLM-4.6V</p>
        </div>
      </footer>
    </div>
  )
}

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<HomePage />} />
          <Route path="gallery" element={<GalleryPage />} />
          <Route path="experience/:id" element={<ExperienceDetailPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}

export default App
