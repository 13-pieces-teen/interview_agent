# 面经历史记录功能

## 功能概述

新增了面经结果保存和可视化功能，用户处理的所有面经将自动保存到本地数据库，并可通过卡片画廊的形式浏览、筛选和管理。

## 主要特性

### 1. 自动保存
- ✅ 每次处理完面经后自动保存到SQLite数据库
- ✅ 无需手动操作，处理完成即保存
- ✅ 保存完整的面经数据（公司、问题、答案、标签等）

### 2. 卡片可视化
- ✅ 以美观的卡片形式展示面经
- ✅ 每张卡片显示：
  - 公司名称和规模
  - 职位和面试阶段
  - 创建日期
  - 问题数量
  - 技术标签（最多显示5个）
  - 面试体验描述
  - 是否包含答案

### 3. 强大的筛选功能
支持多维度筛选：
- **按公司筛选**：搜索框输入公司名称（支持模糊匹配）
- **按标签筛选**：选择一个或多个技术标签（如RAG、强化学习、Agent等）
- **按时间筛选**：全部/最近7天/最近30天/最近90天
- **按面试阶段筛选**：一面/二面/三面/终面/HR面

### 4. 详细视图
- ✅ 点击卡片查看完整面经内容
- ✅ 显示所有问题和答案
- ✅ 支持返回列表

### 5. 删除管理
- ✅ 每张卡片右上角有删除按钮（悬停显示）
- ✅ 删除前需要确认
- ✅ 删除后实时更新列表和统计数据

### 6. 统计数据
在页面顶部显示：
- 总面经数量
- 总问题数量
- 涉及的公司数量

## 技术实现

### 后端

#### 1. 数据库模块 ([src/utils/database.py](src/utils/database.py))
使用SQLite存储面经数据，主要功能：
- `save_experience()` - 保存面经
- `get_experience()` - 获取单条面经详情
- `list_experiences()` - 列出面经（支持筛选）
- `delete_experience()` - 删除面经
- `get_all_tags()` - 获取所有标签
- `get_all_companies()` - 获取所有公司
- `get_stats()` - 获取统计数据

数据库表结构：
```sql
CREATE TABLE experiences (
    id TEXT PRIMARY KEY,
    created_at TEXT NOT NULL,
    source_type TEXT NOT NULL,
    company_name TEXT,
    company_scale TEXT,
    position TEXT,
    interview_stage TEXT,
    interview_experience TEXT,
    questions_json TEXT NOT NULL,
    tags_json TEXT NOT NULL,
    raw_content TEXT NOT NULL,
    questions_count INTEGER DEFAULT 0,
    has_answers BOOLEAN DEFAULT FALSE
)
```

#### 2. API端点 ([src/api/app.py](src/api/app.py:355-505))
新增以下REST API端点：

- `GET /api/experiences` - 列出面经（支持筛选参数）
- `GET /api/experiences/{id}` - 获取单条面经详情
- `DELETE /api/experiences/{id}` - 删除面经
- `GET /api/tags` - 获取所有标签
- `GET /api/companies` - 获取所有公司
- `GET /api/stats` - 获取统计数据

#### 3. 自动保存集成
在以下处理端点中添加了自动保存：
- `/api/process/text` - 文本处理后自动保存
- `/api/process/image` - 单图片处理后自动保存
- `/api/process/images` - 多图片处理后自动保存

### 前端

#### 1. 组件结构

**ExperienceCard.tsx** ([frontend/src/components/ExperienceCard.tsx](frontend/src/components/ExperienceCard.tsx))
- 单个面经卡片组件
- 显示摘要信息
- 支持点击查看详情
- 悬停显示删除按钮

**ExperienceGallery.tsx** ([frontend/src/components/ExperienceGallery.tsx](frontend/src/components/ExperienceGallery.tsx))
- 面经画廊主组件
- 管理筛选状态
- 加载和显示面经列表
- 处理筛选、搜索、删除等操作

#### 2. API服务 ([frontend/src/services/api.ts](frontend/src/services/api.ts:78-136))
新增API调用函数：
- `listExperiences()` - 获取面经列表
- `getExperience()` - 获取详情
- `deleteExperience()` - 删除面经
- `getAllTags()` - 获取标签
- `getAllCompanies()` - 获取公司
- `getStats()` - 获取统计

#### 3. 类型定义 ([frontend/src/types/index.ts](frontend/src/types/index.ts))
新增类型：
```typescript
interface ExperienceListItem {
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
}
```

#### 4. 主应用集成 ([frontend/src/App.tsx](frontend/src/App.tsx))
- 添加"历史记录"按钮到页头
- 点击按钮打开面经画廊
- 使用全屏模态框显示

## 使用指南

### 1. 查看历史记录
1. 在主页右上角点击"历史记录"按钮
2. 进入面经画廊页面

### 2. 筛选面经
1. **搜索公司**：在搜索框输入公司名称
2. **应用筛选**：点击"筛选"按钮展开筛选面板
3. **选择条件**：
   - 时间范围：点击时间按钮（7天/30天/90天）
   - 面试阶段：选择面试轮次
   - 技术标签：点击标签进行多选
4. **重置筛选**：点击"重置"按钮清除所有筛选条件

### 3. 查看详情
1. 点击任意面经卡片
2. 查看完整的问题和答案
3. 点击"返回列表"返回画廊

### 4. 删除面经
1. 鼠标悬停在卡片上
2. 点击右上角的删除图标
3. 确认删除

## 数据存储

### 数据库位置
```
data/interviews.db
```

### 备份建议
定期备份`data/interviews.db`文件以防数据丢失。

## 性能优化

### 数据库索引
为提高查询性能，创建了以下索引：
- `idx_created_at` - 按创建时间排序
- `idx_company_name` - 公司名称查询
- `idx_company_scale` - 公司规模筛选

### 分页支持
API支持分页参数：
- `limit` - 每页数量（默认50）
- `offset` - 偏移量（默认0）

前端暂时设置为一次加载100条，后续可扩展为无限滚动加载。

## 未来改进

### 潜在功能
1. **导出功能**：批量导出选中的面经为PDF/Markdown
2. **标签管理**：编辑和合并标签
3. **搜索增强**：全文搜索问题内容
4. **统计分析**：
   - 按公司统计问题类型
   - 高频问题排行
   - 技术栈分布图
5. **收藏功能**：标记重要的面经
6. **笔记功能**：为面经添加个人笔记
7. **分享功能**：生成分享链接

### 性能优化
1. **懒加载**：实现无限滚动
2. **虚拟列表**：大量数据时使用虚拟滚动
3. **缓存策略**：缓存筛选结果

## 版本历史

### v0.3.0 (2026-01-19)
- ✅ 新增SQLite数据库支持
- ✅ 实现自动保存功能
- ✅ 创建面经卡片画廊
- ✅ 支持多维度筛选（公司、标签、时间、阶段）
- ✅ 添加统计数据显示
- ✅ 实现详情查看和删除功能

## 技术栈

### 后端
- **FastAPI** - REST API框架
- **SQLite** - 轻量级数据库
- **Pydantic** - 数据验证和序列化

### 前端
- **React 18** - UI框架
- **TypeScript** - 类型安全
- **Tailwind CSS** - 样式
- **Lucide React** - 图标库
- **Axios** - HTTP客户端

## 故障排除

### 数据库文件找不到
**问题**：启动时报错数据库不存在
**解决**：数据库会自动创建，确保`data/`目录有写权限

### 面经没有自动保存
**问题**：处理完面经后在历史记录中看不到
**解决**：
1. 检查浏览器控制台是否有错误
2. 确认后端服务正常运行
3. 检查数据库文件权限

### 筛选不生效
**问题**：设置筛选条件后没有结果
**解决**：
1. 检查筛选条件是否过于严格
2. 点击"重置"按钮清除所有筛选
3. 尝试单独使用一个筛选条件

## API文档

详细的API文档可通过访问以下地址查看：
```
http://localhost:8000/docs
```

这是FastAPI自动生成的交互式API文档（Swagger UI）。
