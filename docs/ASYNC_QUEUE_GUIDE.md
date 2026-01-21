# 异步任务队列系统使用指南

## 功能概述

异步任务队列系统允许用户**多次提交面经处理任务，任务在后台队列中异步处理**，用户无需等待当前任务完成即可继续提交新任务。

### 核心特性

1. **非阻塞提交** - 提交任务后立即返回，不需要等待处理完成
2. **后台处理** - 所有任务在后台线程中排队处理
3. **实时追踪** - 可以查询任务状态和队列信息
4. **灵活模式** - 支持同步和异步两种模式切换
5. **统一管理** - 文本和图片任务使用同一个队列系统

## 与批量上传的区别

| 功能 | 批量上传 | 异步任务队列 |
|------|---------|-------------|
| **使用场景** | 一次性上传多个文件 | 多次独立提交任务 |
| **提交方式** | 一次提交所有文件 | 每次提交一个任务 |
| **处理方式** | 按顺序处理同一批次 | 队列统一管理所有任务 |
| **任务类型** | 仅图片批量处理 | 文本、图片均支持 |
| **界面体验** | 等待批量任务完成 | 随时提交，无需等待 |
| **适用场景** | 处理一组相关的面经截图 | 日常使用，随时提交任务 |

## 使用方法

### 前端界面使用

#### 1. 启用异步模式

在主界面勾选 **"异步处理模式（推荐）"** 复选框：

```
☑ 异步处理模式（推荐）
提交后任务在后台处理，您可以继续提交新任务
```

#### 2. 提交任务

- **文本输入**：输入面经文本，点击"处理"
- **图片上传**：选择图片，点击"提交"

提交后会立即显示提示：`任务已提交到队列！任务ID: xxxxxxxx...`

#### 3. 查看任务队列

点击顶部的 **"任务队列"** 按钮，打开任务队列面板：

```
┌─────────────────────────────────────┐
│  📋 任务队列                  🔄     │
├─────────────────────────────────────┤
│  全部(5) 排队中(1) 处理中(1) 已完成(3) 失败(0) │
├─────────────────────────────────────┤
│  ⊙ [文本] 30秒前                     │
│     状态: 处理中                      │
├─────────────────────────────────────┤
│  ○ [图片] 45秒前                     │
│     2个文件  状态: 排队中             │
├─────────────────────────────────────┤
│  ✓ [文本] 1分钟前                    │
│     耗时: 5.2s  状态: 已完成          │
└─────────────────────────────────────┘
```

#### 4. 继续提交新任务

无需等待当前任务完成，可以立即提交新的任务！

#### 5. 查看处理结果

任务完成后：
- 会在任务队列中标记为"已完成"
- 可以到"历史记录"中查看生成的面经

### 同步模式（可选）

如果需要等待任务完成，取消勾选"异步处理模式"：
- 提交后会显示处理进度
- 完成后直接显示结果
- 处理期间无法提交新任务

## API 使用

### 1. 异步处理文本

**端点:** `POST /api/process/text/async`

**请求:**
```json
{
  "content": "面经文本内容...",
  "generate_answers": false,
  "export_format": "both"
}
```

**响应:**
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "queued",
  "message": "任务已提交到队列，将在后台处理"
}
```

**示例代码 (Python):**
```python
import requests

response = requests.post(
    'http://localhost:8000/api/process/text/async',
    json={
        'content': '面经文本...',
        'generate_answers': False,
        'export_format': 'both'
    }
)

result = response.json()
task_id = result['task_id']
print(f"任务已提交: {task_id}")

# 立即提交下一个任务，无需等待
```

### 2. 异步处理图片

**端点:** `POST /api/process/images/async`

**请求:**
```
Content-Type: multipart/form-data

files: File[]
generate_answers: boolean
export_format: string
```

**响应:**
```json
{
  "task_id": "uuid",
  "status": "queued",
  "file_count": 3,
  "message": "任务已提交到队列，将处理 3 个文件"
}
```

**示例代码 (Python):**
```python
files = [
    ('files', ('img1.png', open('img1.png', 'rb'), 'image/png')),
    ('files', ('img2.png', open('img2.png', 'rb'), 'image/png')),
]

response = requests.post(
    'http://localhost:8000/api/process/images/async',
    files=files,
    data={'generate_answers': 'false', 'export_format': 'both'}
)

task_id = response.json()['task_id']
print(f"任务已提交: {task_id}")

# 立即提交下一个任务
```

### 3. 查询任务状态

**端点:** `GET /api/tasks/async/{task_id}`

**响应:**
```json
{
  "id": "task-id",
  "type": "text",  // 或 "image"
  "status": "processing",  // queued, processing, completed, failed
  "created_at": "2025-01-20T10:30:00",
  "started_at": "2025-01-20T10:30:05",
  "completed_at": null,
  "processing_time": 0,
  "result": null,
  "error": null,
  "metadata": {}
}
```

**轮询示例:**
```python
import time

while True:
    response = requests.get(f'http://localhost:8000/api/tasks/async/{task_id}')
    status = response.json()

    if status['status'] in ['completed', 'failed']:
        print(f"任务{status['status']}")
        if status['status'] == 'completed':
            print(f"面经ID: {status['result']['experience_id']}")
        break

    time.sleep(2)
```

### 4. 获取任务列表

**端点:** `GET /api/tasks/async?status={status}`

**查询参数:**
- `status` (可选): `queued`, `processing`, `completed`, `failed`

**响应:**
```json
{
  "tasks": [
    {
      "id": "task-1",
      "type": "text",
      "status": "completed",
      "created_at": "2025-01-20T10:30:00",
      "processing_time": 5.2,
      "metadata": {}
    }
  ],
  "total": 10
}
```

### 5. 获取队列统计

**端点:** `GET /api/tasks/queue/info`

**响应:**
```json
{
  "total_tasks": 15,
  "queued": 3,
  "processing": 1,
  "completed": 10,
  "failed": 1,
  "queue_size": 3,
  "is_running": true
}
```

## 系统架构

### 后端架构

```
┌──────────────────────────────────────┐
│         FastAPI Application          │
│  POST /api/process/text/async        │
│  POST /api/process/images/async      │
│  GET  /api/tasks/async/{task_id}     │
│  GET  /api/tasks/async               │
│  GET  /api/tasks/queue/info          │
└─────────────┬────────────────────────┘
              │
              ▼
┌──────────────────────────────────────┐
│      AsyncTaskQueue (单例)            │
│  - submit_task()                     │
│  - get_task()                        │
│  - get_all_tasks()                   │
│  - get_queue_info()                  │
└─────────────┬────────────────────────┘
              │
              ▼
┌──────────────────────────────────────┐
│       Background Worker Thread        │
│  - 从队列取任务                        │
│  - 调用处理函数                        │
│  - 更新任务状态                        │
│  - 保存到数据库                        │
└──────────────────────────────────────┘
```

### 前端架构

```
┌──────────────────────────────────────┐
│              App.tsx                 │
│  - asyncMode 状态                     │
│  - 异步/同步提交选择                   │
└─────────────┬────────────────────────┘
              │
      ┌───────┴────────┐
      ▼                ▼
┌─────────────┐  ┌─────────────┐
│ UploadZone  │  │ TaskQueue   │
│ - 提交任务   │  │ - 显示队列   │
│            │  │ - 轮询状态   │
└─────────────┘  └─────────────┘
      │                │
      └───────┬────────┘
              ▼
┌──────────────────────────────────────┐
│      api.ts (API Services)           │
│  - processTextAsync()                │
│  - processImagesAsync()              │
│  - getAsyncTaskStatus()              │
│  - listAsyncTasks()                  │
└──────────────────────────────────────┘
```

## 任务状态流转

```
提交任务
  ↓
QUEUED (排队中)
  ↓
PROCESSING (处理中)
  ↓
COMPLETED / FAILED (完成 / 失败)
```

## 典型使用流程

### 场景：连续提交多个面经

```
用户操作时间线:

10:00:00  提交第1个文本任务 ✓
10:00:01  提交第2个文本任务 ✓  (无需等待)
10:00:02  提交第3个图片任务 ✓  (无需等待)
10:00:03  打开任务队列查看进度
10:00:10  第1个任务完成 ✓
10:00:15  第2个任务完成 ✓
10:00:20  第3个任务完成 ✓
10:00:21  查看历史记录，所有面经已保存
```

### 场景：日常使用

1. 早上上班，提交昨天面试的文本内容
2. 中午休息，上传面试截图
3. 下午提交新的面经文本
4. 晚上查看任务队列，确认所有任务完成
5. 到历史记录查看整理好的面经

## 性能特点

### 优势

- ✅ 非阻塞提交，用户体验流畅
- ✅ 后台自动处理，无需等待
- ✅ 支持多任务并发提交
- ✅ 实时状态追踪
- ✅ 统一的队列管理

### 注意事项

1. **队列顺序**: 任务按提交顺序排队处理
2. **内存限制**: 任务信息存储在内存中，重启后清空
3. **处理时间**: 每个任务平均耗时 5-10 秒
4. **建议配置**:
   - 单次提交任务数：不限
   - 队列大小：建议 < 100
   - 任务保留时间：24 小时

## 测试

运行测试脚本：

```bash
# 确保后端运行
python -m uvicorn src.api.app:app --reload --port 8000

# 运行测试
python tests/test_async_queue.py
```

测试覆盖：
- ✅ 连续提交多个文本任务
- ✅ 连续提交多个图片任务
- ✅ 任务状态查询
- ✅ 任务列表获取
- ✅ 队列信息统计
- ✅ 后台自动处理

## 常见问题

**Q: 异步模式和同步模式有什么区别？**

A:
- **异步模式**: 提交后立即返回，任务在后台处理，可以继续提交新任务
- **同步模式**: 提交后等待处理完成，完成后显示结果

**Q: 如何知道任务处理完成？**

A:
- 方法1: 打开"任务队列"面板，会自动刷新显示状态
- 方法2: 到"历史记录"查看新生成的面经
- 方法3: 使用API轮询任务状态

**Q: 任务失败会怎样？**

A: 任务失败后会在队列中显示错误信息，不影响其他任务

**Q: 可以取消正在处理的任务吗？**

A: 当前版本不支持取消，任务会自动完成或失败

**Q: 服务器重启后任务会丢失吗？**

A: 是的，当前任务存储在内存中，重启后会清空

## 未来优化

- [ ] 任务持久化（数据库存储）
- [ ] 支持任务取消
- [ ] 支持任务优先级
- [ ] WebSocket 实时推送
- [ ] 分布式任务队列
- [ ] 任务重试机制

## 相关文件

### 后端
- [src/utils/async_task_queue.py](../src/utils/async_task_queue.py) - 异步任务队列核心
- [src/api/app.py](../src/api/app.py) - API端点（新增异步接口）

### 前端
- [frontend/src/components/TaskQueue.tsx](../frontend/src/components/TaskQueue.tsx) - 任务队列组件
- [frontend/src/services/api.ts](../frontend/src/services/api.ts) - API服务（新增异步函数）
- [frontend/src/App.tsx](../frontend/src/App.tsx) - 主应用（集成异步模式）

### 测试
- [tests/test_async_queue.py](../tests/test_async_queue.py) - 功能测试脚本

## 贡献

- 实现时间: 2025-01-20
- 版本: v1.0.0
