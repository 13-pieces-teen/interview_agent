# 批量上传功能使用指南

## 功能概述

批量上传功能允许用户一次性上传多个面经图片，系统将按照上传顺序依次处理每个文件，并实时展示处理进度。

## 核心特性

### 1. 按顺序处理
- ✓ 按照用户上传的顺序依次处理每个文件
- ✓ 当前文件处理完成后才开始下一个
- ✓ 保证处理的可预测性和稳定性

### 2. 实时进度追踪
- ✓ 显示总体进度条
- ✓ 实时更新当前处理的文件
- ✓ 展示每个文件的处理状态（等待中、处理中、完成、失败）
- ✓ 显示每个文件的处理耗时

### 3. 独立的任务管理
- ✓ 每个批量任务有唯一的任务ID
- ✓ 可以查询任务状态和历史记录
- ✓ 自动保存每个成功处理的面经

### 4. 错误处理
- ✓ 单个文件失败不影响其他文件处理
- ✓ 详细的错误信息展示
- ✓ 完成后显示成功和失败统计

## 使用方法

### 前端界面使用

#### 步骤 1：选择图片上传模式
1. 在主界面点击"图片上传"标签
2. 上传或拖拽多张面经截图

#### 步骤 2：启用批量模式
1. 当选择了2张或以上的图片时，会出现"批量模式"复选框
2. 勾选"批量模式"切换到按顺序处理模式
3. 界面会显示提示："批量模式：将按照上传顺序依次处理每张图片，可实时查看进度"

#### 步骤 3：开始处理
1. 点击"批量处理 N 张图片（按顺序）"按钮
2. 系统会立即创建批量任务并开始处理

#### 步骤 4：查看进度
处理过程中会显示：
- 总体进度条
- 文件总数、已完成数、失败数统计
- 每个文件的详细状态列表
  - 文件名
  - 处理状态（等待中、处理中、完成、失败）
  - 处理耗时
  - 错误信息（如果失败）

#### 步骤 5：查看结果
- 处理完成后会自动跳转到历史记录页面
- 可以查看所有成功处理的面经

### 与普通模式的区别

| 功能 | 普通模式 | 批量模式 |
|------|---------|---------|
| 处理方式 | 合并所有图片内容后一次性处理 | 按顺序逐个处理 |
| 进度展示 | 简单的加载提示 | 详细的进度条和文件状态 |
| 失败处理 | 整个任务失败 | 单个文件失败不影响其他 |
| 结果保存 | 一个合并的面经 | 多个独立的面经 |
| 适用场景 | 同一场面试的多个截图 | 多个不同的面经 |

## API 使用

### 1. 创建批量处理任务

**端点:** `POST /api/process/batch`

**请求参数:**
- `files`: 文件列表（multipart/form-data）
- `generate_answers`: 是否生成答案（可选，默认 false）
- `export_format`: 导出格式（可选，默认 "both"）

**响应:**
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "total_files": 3,
  "status": "processing",
  "message": "Batch processing started for 3 files"
}
```

**示例代码 (Python):**
```python
import requests

files = [
    ('files', ('image1.png', open('image1.png', 'rb'), 'image/png')),
    ('files', ('image2.png', open('image2.png', 'rb'), 'image/png')),
]

data = {
    'generate_answers': 'false',
    'export_format': 'both'
}

response = requests.post(
    'http://localhost:8000/api/process/batch',
    files=files,
    data=data
)

result = response.json()
task_id = result['task_id']
print(f"任务ID: {task_id}")
```

### 2. 查询任务状态

**端点:** `GET /api/batch/{task_id}`

**响应:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "total_files": 3,
  "created_at": "2025-01-20T10:30:00",
  "status": "processing",
  "current_index": 1,
  "completed_count": 1,
  "failed_count": 0,
  "started_at": "2025-01-20T10:30:01",
  "completed_at": null,
  "generate_answers": false,
  "export_format": "both",
  "sub_tasks": [
    {
      "id": "sub-task-1",
      "file_name": "image1.png",
      "status": "completed",
      "error": null,
      "experience_id": "exp-123",
      "started_at": "2025-01-20T10:30:01",
      "completed_at": "2025-01-20T10:30:05",
      "processing_time": 4.2
    },
    {
      "id": "sub-task-2",
      "file_name": "image2.png",
      "status": "processing",
      "error": null,
      "experience_id": null,
      "started_at": "2025-01-20T10:30:05",
      "completed_at": null,
      "processing_time": 0
    }
  ]
}
```

**示例代码 (Python):**
```python
import requests
import time

task_id = "550e8400-e29b-41d4-a716-446655440000"

while True:
    response = requests.get(f'http://localhost:8000/api/batch/{task_id}')
    status = response.json()

    print(f"进度: {status['completed_count']}/{status['total_files']}")

    if status['status'] in ['completed', 'failed', 'cancelled']:
        print(f"任务{status['status']}")
        break

    time.sleep(2)
```

### 3. 获取任务列表

**端点:** `GET /api/batch?status={status}`

**查询参数:**
- `status`: 可选，过滤状态（pending, processing, completed, failed, cancelled）

**响应:**
```json
{
  "tasks": [
    {
      "id": "task-1",
      "status": "completed",
      "total_files": 3,
      "completed_count": 3,
      "failed_count": 0,
      "created_at": "2025-01-20T10:30:00"
    }
  ],
  "total": 1
}
```

### 4. 取消任务

**端点:** `DELETE /api/batch/{task_id}`

**响应:**
```json
{
  "success": true,
  "message": "Task cancelled successfully"
}
```

**注意:** 只能取消状态为 `pending` 的任务。

## 系统架构

### 后端组件

#### 1. BatchProcessor (批量处理器)
- 位置: `src/utils/batch_processor.py`
- 功能: 管理批量任务队列，按顺序处理文件
- 特点: 单例模式，线程安全

#### 2. API 端点
- 位置: `src/api/app.py`
- 端点:
  - `POST /api/process/batch` - 创建批量任务
  - `GET /api/batch/{task_id}` - 查询任务状态
  - `GET /api/batch` - 获取任务列表
  - `DELETE /api/batch/{task_id}` - 取消任务

### 前端组件

#### 1. BatchProgress 组件
- 位置: `frontend/src/components/BatchProgress.tsx`
- 功能: 显示批量处理进度
- 特点:
  - 自动轮询任务状态（每2秒）
  - 实时更新UI
  - 处理完成/错误回调

#### 2. UploadZone 组件更新
- 位置: `frontend/src/components/UploadZone.tsx`
- 新增: 批量模式切换开关
- 功能: 根据模式调用不同的处理函数

#### 3. API 服务
- 位置: `frontend/src/services/api.ts`
- 新增函数:
  - `processBatch()` - 创建批量任务
  - `getBatchStatus()` - 获取任务状态
  - `listBatchTasks()` - 获取任务列表
  - `cancelBatchTask()` - 取消任务

## 数据流程

```
用户上传多个文件
    ↓
前端: 勾选批量模式
    ↓
前端: 调用 processBatch(files)
    ↓
后端: 保存所有文件到临时目录
    ↓
后端: 创建 BatchTask 和多个 SubTask
    ↓
后端: 启动后台线程，按顺序处理
    ↓
后端: 逐个处理文件
  ├─ OCR 提取文本
  ├─ 核心处理器分析
  ├─ 保存到数据库
  └─ 更新子任务状态
    ↓
前端: 轮询任务状态（每2秒）
    ↓
前端: 更新进度UI
    ↓
处理完成: 显示结果统计
    ↓
自动跳转到历史记录页面
```

## 配置选项

### 批量处理器配置

在 `src/utils/batch_processor.py` 中可以调整：

```python
# 任务清理
batch_processor.cleanup_old_tasks(max_age_hours=24)  # 清理24小时前的任务
```

### 轮询间隔配置

在 `frontend/src/components/BatchProgress.tsx` 中可以调整：

```typescript
// 轮询间隔（毫秒）
pollInterval = setInterval(pollStatus, 2000)  // 默认2秒
```

### 超时配置

在 `frontend/src/services/api.ts` 中可以调整：

```typescript
const response = await api.post('/process/batch', formData, {
  timeout: 30000,  // 创建任务的超时时间：30秒
})
```

## 注意事项

1. **文件大小限制**
   - 建议每个图片不超过 10MB
   - 批量上传建议不超过 20 个文件

2. **处理时间**
   - 每个文件平均处理时间：5-10秒
   - 包含 OCR、分析、保存等步骤

3. **并发限制**
   - 当前实现为顺序处理，不支持并发
   - 如需并发可修改 `batch_processor.py`

4. **内存管理**
   - 任务信息存储在内存中
   - 建议定期调用 `cleanup_old_tasks()` 清理

5. **错误恢复**
   - 单个文件失败不影响其他文件
   - 所有临时文件会自动清理

## 故障排查

### 问题 1: 任务一直处于 pending 状态

**原因:** 后台线程未启动

**解决方案:**
1. 检查后端日志是否有错误
2. 确认 `start_batch_processing()` 被调用
3. 检查线程是否正常创建

### 问题 2: 前端无法获取任务状态

**原因:** 跨域或网络问题

**解决方案:**
1. 检查 CORS 配置
2. 确认后端服务运行正常
3. 查看浏览器控制台错误

### 问题 3: 文件处理失败

**原因:** OCR 服务异常或文件格式问题

**解决方案:**
1. 检查图片格式是否支持
2. 查看子任务的 error 字段
3. 确认 OCR API 配置正确

## 测试

运行测试脚本：

```bash
python tests/test_batch_upload.py
```

确保：
1. 后端服务运行在 `http://localhost:8000`
2. 测试图片文件存在
3. OCR API 配置正确

## 未来改进

- [ ] 支持并行处理多个文件
- [ ] 添加任务优先级
- [ ] 支持暂停/恢复任务
- [ ] 持久化任务状态到数据库
- [ ] 添加任务进度 WebSocket 推送
- [ ] 支持批量导出结果
