# 面经卡片编辑功能

## 功能概述

为面经卡片系统新增了完整的编辑功能，允许用户在查看面经详情时进行内容编辑，包括公司信息、面试体验、问题答案等。

## 功能特性

### 1. 可编辑字段

#### 公司信息
- **公司名称**: 文本输入框
- **公司规模**: 下拉选择（大厂、中厂、小厂、初创）
- **职位**: 文本输入框
- **面试阶段**: 下拉选择（一面、二面、三面、终面、HR面）

#### 面试体验
- **面试体验描述**: 多行文本框，支持详细描述面试流程、氛围等

#### 技术标签
- **添加标签**: 输入框 + 添加按钮，支持回车键快速添加
- **删除标签**: 点击标签上的 × 图标

#### 面试问题
- **添加新问题**: 点击"添加问题"按钮
- **编辑问题内容**: 多行文本框
- **编辑答案**: 多行文本框，支持用户自行填入答案
- **删除问题**: 点击垃圾桶图标（需确认）

### 2. 用户界面

#### 编辑按钮
- 位置：面经详情页右上角
- 图标：编辑图标 + "编辑"文字
- 样式：主题色按钮，悬停效果

#### 编辑弹窗
- **模态框设计**: 居中显示，带遮罩层
- **响应式布局**: 最大宽度 4xl，自适应高度
- **滚动支持**: 内容区域可滚动，适应大量数据
- **分区明确**: 公司信息、面试体验、技术标签、面试问题分区展示

#### 交互反馈
- **保存状态**: 保存时显示加载动画和"保存中..."提示
- **删除确认**: 删除问题前弹出确认对话框
- **按钮禁用**: 保存过程中禁用所有操作按钮

### 3. 数据持久化

#### 后端 API
- **端点**: `PUT /api/experiences/{experience_id}`
- **请求体**: 包含所有可编辑字段的 JSON 对象
- **响应**: 返回更新后的完整面经数据

#### 前端更新
- 保存成功后立即更新本地状态
- 通过回调函数通知父组件数据已更新
- 自动关闭编辑弹窗

## 技术实现

### 文件结构

```
frontend/src/
├── components/
│   ├── EditExperienceModal.tsx    # 编辑模态框组件
│   ├── ResultsView.tsx             # 面经详情视图（已更新）
│   └── ...
└── services/
    └── api.ts                      # API 调用（已添加 updateExperience）

src/
└── api/
    └── app.py                      # FastAPI 后端（已添加更新端点）
```

### 核心组件

#### EditExperienceModal
- **Props**:
  - `experience`: 当前面经数据
  - `onClose`: 关闭回调
  - `onSave`: 保存回调（异步函数）
- **状态管理**:
  - `formData`: 表单数据（深拷贝 experience）
  - `newTag`: 新标签输入
  - `saving`: 保存状态

#### ResultsView 更新
- **新增状态**:
  - `showEditModal`: 控制编辑弹窗显示
  - `currentExperience`: 当前面经数据（支持实时更新）
- **新增 Props**:
  - `onUpdate?`: 可选的更新回调

### API 接口

#### 更新面经
```typescript
updateExperience(experienceId: string, updates: {
  company_name?: string
  company_scale?: string
  position?: string
  interview_stage?: string
  interview_experience?: string
  tags?: string[]
  questions?: Question[]
}): Promise<{ success: boolean; experience: InterviewExperience }>
```

#### 后端实现
```python
class UpdateExperienceRequest(BaseModel):
    company_name: Optional[str] = None
    company_scale: Optional[str] = None
    position: Optional[str] = None
    interview_stage: Optional[str] = None
    interview_experience: Optional[str] = None
    tags: Optional[List[str]] = None
    questions: Optional[List[dict]] = None

@app.put("/api/experiences/{experience_id}")
async def update_experience(experience_id: str, request: UpdateExperienceRequest)
```

## 使用方法

### 用户操作流程

1. **进入编辑模式**
   - 在面经详情页点击右上角的"编辑"按钮
   - 编辑弹窗打开，显示当前数据

2. **编辑内容**
   - 修改公司信息字段
   - 编辑或添加技术标签
   - 修改面试体验描述
   - 编辑现有问题的内容和答案
   - 添加新的问题和答案
   - 删除不需要的问题

3. **保存修改**
   - 点击"保存修改"按钮
   - 等待保存完成（显示加载状态）
   - 自动返回详情页，查看更新后的内容

4. **取消编辑**
   - 点击"取消"按钮或关闭图标
   - 放弃所有未保存的修改

### 特殊功能

#### 快速添加标签
- 在标签输入框中输入标签名称
- 按 `Enter` 键快速添加
- 或点击右侧的 `+` 按钮添加

#### 问题管理
- **添加问题**: 点击"添加问题"按钮，新问题会追加到列表末尾
- **编辑问题**: 直接在文本框中修改问题内容和答案
- **删除问题**: 点击问题卡片右上角的垃圾桶图标，确认后删除

## 样式特性

### 深色模式支持
- 所有组件完全支持深色模式
- 使用 Tailwind CSS 的 `dark:` 前缀实现
- 自动适应系统主题设置

### 响应式设计
- 移动端友好的布局
- 表单字段在小屏幕上堆叠显示
- 弹窗自适应屏幕尺寸（最大高度 90vh）

### 交互动画
- 按钮悬停效果
- 保存时的加载动画
- 平滑的过渡效果

## 数据验证

### 前端验证
- 标签去重：相同标签不会重复添加
- 空标签过滤：自动过滤空白标签
- 必填字段提示：问题内容不能为空

### 后端验证
- 面经 ID 存在性检查
- 数据类型验证（Pydantic）
- 数据库完整性保证

## 错误处理

### 前端错误
- 保存失败时显示提示框
- 网络错误自动重试提示
- 控制台输出详细错误信息

### 后端错误
- 404: 面经不存在
- 500: 服务器内部错误
- 返回详细错误信息给前端

## 未来改进方向

1. **字段级验证**
   - 添加实时表单验证
   - 必填字段提示
   - 格式验证（如邮箱、URL）

2. **撤销/重做**
   - 支持操作历史记录
   - Ctrl+Z 撤销编辑

3. **自动保存**
   - 定时自动保存草稿
   - 防止数据丢失

4. **批量编辑**
   - 支持同时编辑多条面经
   - 批量修改标签

5. **权限控制**
   - 用户身份验证
   - 编辑权限管理

6. **版本历史**
   - 记录修改历史
   - 支持查看和恢复旧版本

## 相关文件

- [EditExperienceModal.tsx](../frontend/src/components/EditExperienceModal.tsx)
- [ResultsView.tsx](../frontend/src/components/ResultsView.tsx)
- [api.ts](../frontend/src/services/api.ts)
- [app.py](../src/api/app.py)
