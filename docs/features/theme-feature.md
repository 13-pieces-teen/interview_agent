# 主题切换功能

## 功能概述

新增了深色/浅色主题切换功能，用户可以根据个人喜好选择界面主题。

## 主要特性

### 1. 一键切换
- ✅ 页面右上角的太阳/月亮图标按钮
- ✅ 点击即可切换主题
- ✅ 切换时有平滑的过渡动画

### 2. 主题持久化
- ✅ 主题选择自动保存到localStorage
- ✅ 下次打开网页时自动恢复上次的主题选择
- ✅ 无需重新设置

### 3. 系统主题检测
- ✅ 首次访问时自动检测系统主题偏好
- ✅ 如果系统设置为深色模式，网页默认使用深色主题
- ✅ 如果系统设置为浅色模式，网页默认使用浅色主题

### 4. 全局主题支持
- ✅ 所有页面和组件都支持主题切换
- ✅ 包括主页、上传区、结果展示、历史记录等所有界面
- ✅ 统一的视觉体验

## 技术实现

### 1. 主题上下文 ([frontend/src/contexts/ThemeContext.tsx](frontend/src/contexts/ThemeContext.tsx))

使用React Context API管理主题状态：

```typescript
export function ThemeProvider({ children }: { children: ReactNode }) {
  const [theme, setTheme] = useState<Theme>(() => {
    // 优先从localStorage读取
    const saved = localStorage.getItem('theme')
    if (saved === 'light' || saved === 'dark') {
      return saved
    }
    // 检测系统偏好
    if (window.matchMedia('(prefers-color-scheme: dark)').matches) {
      return 'dark'
    }
    return 'light'
  })

  useEffect(() => {
    // 更新document class
    if (theme === 'dark') {
      document.documentElement.classList.add('dark')
    } else {
      document.documentElement.classList.remove('dark')
    }
    // 保存到localStorage
    localStorage.setItem('theme', theme)
  }, [theme])

  const toggleTheme = () => {
    setTheme((prev) => (prev === 'dark' ? 'light' : 'dark'))
  }

  return (
    <ThemeContext.Provider value={{ theme, toggleTheme }}>
      {children}
    </ThemeContext.Provider>
  )
}
```

### 2. Tailwind配置 ([frontend/tailwind.config.js](frontend/tailwind.config.js))

启用class模式的深色模式支持：

```javascript
export default {
  darkMode: 'class', // 使用class策略
  // ... 其他配置
}
```

### 3. 主题切换按钮

在App组件的header中添加：

```tsx
<button
  onClick={toggleTheme}
  className="p-2 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-600 transition-all"
  title={theme === 'dark' ? '切换到浅色模式' : '切换到深色模式'}
>
  {theme === 'dark' ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
</button>
```

### 4. Tailwind深色模式样式

使用`dark:`前缀定义深色模式下的样式：

```tsx
// 背景色
className="bg-white dark:bg-gray-800"

// 文字颜色
className="text-gray-900 dark:text-white"

// 边框颜色
className="border-gray-200 dark:border-gray-700"

// 过渡动画
className="transition-colors"
```

## 颜色方案

### 深色主题
- 背景：`bg-gray-900` (#111827)
- 卡片：`bg-gray-800` (#1F2937)
- 边框：`border-gray-700` (#374151)
- 文字：`text-white` (#FFFFFF)
- 次要文字：`text-gray-400` (#9CA3AF)

### 浅色主题
- 背景：`bg-gray-50` (#F9FAFB)
- 卡片：`bg-white` (#FFFFFF)
- 边框：`border-gray-200` (#E5E7EB)
- 文字：`text-gray-900` (#111827)
- 次要文字：`text-gray-600` (#4B5563)

### 主题色（两种模式通用）
- Primary: `bg-primary-600` (#0284C7)
- Primary Hover: `bg-primary-700` (#0369A1)

## 使用指南

### 切换主题
1. 在任何页面右上角找到太阳/月亮图标
2. 点击图标即可切换主题
3. 主题会立即应用到所有界面

### 查看当前主题
- **月亮图标** = 当前是浅色主题，点击切换到深色
- **太阳图标** = 当前是深色主题，点击切换到浅色

## 更新的组件

所有主要组件已更新以支持主题：

### 1. App.tsx
- 添加主题切换按钮
- 更新所有样式类以支持深色模式
- 集成useTheme hook

### 2. UploadZone.tsx
- 模式切换按钮（文本/图片）
- 文本输入框
- 图片拖放区域
- 图片预览卡片
- 提交按钮

### 3. ExperienceGallery.tsx
- 页面背景和头部
- 搜索框和筛选按钮
- 筛选面板
- 加载和错误状态

### 4. ExperienceCard.tsx
- 卡片背景和边框
- 公司信息
- 标签样式
- 元数据显示

### 5. ResultsView.tsx
- 结果展示卡片（已更新）
- 问题和答案显示（已更新）
- 标签和元数据（已更新）

### 6. ExportPanel.tsx
- 下载按钮（已更新）
- 文件列表（已更新）

## 浏览器兼容性

### CSS特性
- ✅ CSS Variables (CSS自定义属性)
- ✅ `prefers-color-scheme` 媒体查询
- ✅ Tailwind的`dark:`前缀

### 支持的浏览器
- ✅ Chrome/Edge 76+
- ✅ Firefox 67+
- ✅ Safari 12.1+
- ✅ Opera 62+

### localStorage
所有现代浏览器都支持localStorage，用于保存主题偏好。

## 开发指南

### 添加新组件时的主题支持

在创建新组件时，遵循以下模式：

```tsx
// 1. 背景色
<div className="bg-white dark:bg-gray-800">

// 2. 文字颜色
<p className="text-gray-900 dark:text-white">

// 3. 边框
<div className="border border-gray-200 dark:border-gray-700">

// 4. 悬停效果
<button className="hover:bg-gray-100 dark:hover:bg-gray-700">

// 5. 添加过渡动画
<div className="transition-colors">
```

### 使用主题上下文

在需要读取或切换主题的组件中：

```tsx
import { useTheme } from './contexts/ThemeContext'

function MyComponent() {
  const { theme, toggleTheme } = useTheme()

  return (
    <button onClick={toggleTheme}>
      当前主题: {theme}
    </button>
  )
}
```

## 未来改进

### 潜在功能
1. **更多主题选项**：
   - 增加自定义颜色主题
   - 预设主题（蓝色、绿色、紫色等）

2. **自动切换**：
   - 根据时间自动切换（白天/夜晚）
   - 跟随系统主题实时切换

3. **高对比度模式**：
   - 为视觉障碍用户提供高对比度选项

4. **主题预览**：
   - 在切换前预览主题效果

## 版本历史

### v0.3.1 (2026-01-20)
- ✅ 新增深色/浅色主题切换功能
- ✅ 添加主题持久化到localStorage
- ✅ 支持系统主题检测
- ✅ 更新所有主要组件支持主题
- ✅ 添加平滑过渡动画

## 故障排除

### 主题不生效
**问题**：切换主题后界面没有变化
**解决**：
1. 检查浏览器控制台是否有错误
2. 确认`<html>`标签上是否有`dark`类
3. 清除浏览器缓存并刷新

### 主题不保存
**问题**：刷新页面后主题重置
**解决**：
1. 检查浏览器是否启用了localStorage
2. 确认浏览器不在隐私模式
3. 检查是否有浏览器插件阻止localStorage

### 部分组件没有主题
**问题**：某些界面元素没有响应主题切换
**解决**：
1. 检查组件是否使用了`dark:`前缀
2. 确认组件是否在ThemeProvider内部
3. 添加`transition-colors`类实现平滑过渡

## 技术栈

- **React Context API** - 全局状态管理
- **Tailwind CSS** - 样式框架（class策略的深色模式）
- **localStorage** - 主题偏好持久化
- **Lucide React** - 图标（Sun/Moon）

## 相关文档

- [Tailwind CSS Dark Mode](https://tailwindcss.com/docs/dark-mode)
- [React Context](https://react.dev/reference/react/useContext)
- [prefers-color-scheme](https://developer.mozilla.org/en-US/docs/Web/CSS/@media/prefers-color-scheme)
