# 异步任务队列系统 - 实现总结

## 功能概述

实现了**异步任务队列系统**，允许用户多次提交面经处理任务，任务在后台队列中自动处理，用户无需等待即可继续提交新任务。

## 实现的功能

### ✅ 核心功能

1. **异步任务提交**
   - 文本异步处理
   - 图片异步处理
   - 立即返回任务ID
   - 不阻塞用户操作

2. **后台任务队列**
   - 自动启动工作线程
   - 队列顺序处理
   - 线程安全设计
   - 统一任务管理

3. **实时状态追踪**
   - 任务状态查询
   - 任务列表获取
   - 队列统计信息
   - 自动状态更新

4. **灵活模式切换**
   - 异步模式（默认）
   - 同步模式（可选）
   - 前端一键切换
   - 无缝体验过渡

5. **任务队列UI**
   - 实时状态显示
   - 自动刷新机制
   - 任务分类过滤
   - 统计信息展示

## 文件清单

### 新增文件

#### 后端
- [src/utils/async_task_queue.py](../src/utils/async_task_queue.py) - 异步任务队列核心
  - `AsyncTaskQueue` 类：单例模式队列管理器
  - `Task` 数据类：任务数据结构
  - `TaskType` 枚举：任务类型（text, image, batch）
  - `TaskStatus` 枚举：任务状态（queued, processing, completed, failed）

#### 前端
- [frontend/src/components/TaskQueue.tsx](../frontend/src/components/TaskQueue.tsx) - 任务队列UI组件
  - 实时任务列表显示
  - 自动轮询刷新（3秒）
  - 状态过滤标签
  - 统计信息面板

#### 文档
- [docs/ASYNC_QUEUE_GUIDE.md](./ASYNC_QUEUE_GUIDE.md) - 完整使用指南
- [docs/ASYNC_QUEUE_QUICKSTART.md](./ASYNC_QUEUE_QUICKSTART.md) - 快速开始指南
- [docs/ASYNC_QUEUE_README.md](./ASYNC_QUEUE_README.md) - 本文件

#### 测试
- [tests/test_async_queue.py](../tests/test_async_queue.py) - 功能测试脚本

### 修改文件

#### 后端
- [src/api/app.py](../src/api/app.py)
  - 导入任务队列模块
  - 设置任务处理函数
  - 启动工作线程
  - 新增 `POST /api/process/text/async` - 异步处理文本
  - 新增 `POST /api/process/images/async` - 异步处理图片
  - 新增 `GET /api/tasks/async/{task_id}` - 查询任务状态
  - 新增 `GET /api/tasks/async` - 获取任务列表
  - 新增 `GET /api/tasks/queue/info` - 获取队列信息

#### 前端
- [frontend/src/services/api.ts](../frontend/src/services/api.ts)
  - 新增 `processTextAsync()` - 异步处理文本
  - 新增 `processImagesAsync()` - 异步处理图片
  - 新增 `getAsyncTaskStatus()` - 获取任务状态
  - 新增 `listAsyncTasks()` - 获取任务列表
  - 新增 `getQueueInfo()` - 获取队列信息

- [frontend/src/App.tsx](../frontend/src/App.tsx)
  - 新增 `asyncMode` 状态（默认开启）
  - 新增 `showTaskQueue` 状态
  - 修改 `handleTextSubmit` 支持异步/同步模式
  - 修改 `handleImagesSubmit` 支持异步/同步模式
  - 新增异步模式切换开关UI
  - 新增任务队列按钮
  - 集成 TaskQueue 组件

## 技术架构

### 数据结构

#### Task (任务)

```python
@dataclass
class Task:
    id: str                          # 任务ID（UUID）
    type: TaskType                   # 任务类型（text/image/batch）
    status: TaskStatus               # 任务状态
    input_data: Any                  # 输入数据
    generate_answers: bool           # 是否生成答案
    export_format: str               # 导出格式

    # 时间戳
    created_at: str                  # 创建时间
    started_at: Optional[str]        # 开始时间
    completed_at: Optional[str]      # 完成时间

    # 结果
    result: Optional[Dict]           # 处理结果
    error: Optional[str]             # 错误信息
    processing_time: float           # 处理耗时

    # 元数据
    metadata: Dict[str, Any]         # 额外信息
```

#### TaskType (任务类型)

```python
class TaskType(str, Enum):
    TEXT = "text"      # 文本处理
    IMAGE = "image"    # 图片处理
    BATCH = "batch"    # 批量处理
```

#### TaskStatus (任务状态)

```python
class TaskStatus(str, Enum):
    QUEUED = "queued"           # 排队中
    PROCESSING = "processing"   # 处理中
    COMPLETED = "completed"     # 已完成
    FAILED = "failed"           # 失败
```

### 后端架构

```
┌─────────────────────────────────────────────┐
│           FastAPI Application               │
│  - POST /api/process/text/async             │
│  - POST /api/process/images/async           │
│  - GET  /api/tasks/async/{task_id}          │
│  - GET  /api/tasks/async                    │
│  - GET  /api/tasks/queue/info               │
└────────────────┬────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────┐
│      AsyncTaskQueue (单例模式)               │
│  - submit_task()      提交任务              │
│  - get_task()         获取任务              │
│  - get_all_tasks()    获取任务列表          │
│  - get_queue_info()   获取队列信息          │
└────────────────┬────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────┐
│      Background Worker Thread (单线程)      │
│  - 从队列取任务（queue.Queue）               │
│  - 调用 process_func 处理任务               │
│  - 更新任务状态                              │
│  - 保存结果到数据库                          │
│  - 清理临时文件                              │
└─────────────────────────────────────────────┘
```

### 前端架构

```
┌─────────────────────────────────────────────┐
│              App.tsx                        │
│  - asyncMode: boolean (异步模式开关)         │
│  - showTaskQueue: boolean (队列显示)        │
│  - handleTextSubmit (支持异步/同步)         │
│  - handleImagesSubmit (支持异步/同步)       │
└────────────────┬────────────────────────────┘
                 │
         ┌───────┴────────┐
         ▼                ▼
┌─────────────┐    ┌──────────────┐
│ UploadZone  │    │  TaskQueue   │
│ - 提交任务   │    │  - 任务列表   │
│            │    │  - 状态过滤   │
└─────────────┘    │  - 轮询刷新   │
         │         └──────────────┘
         └───────┬────────┘
                 ▼
┌─────────────────────────────────────────────┐
│         api.ts (API Services)               │
│  - processTextAsync()                       │
│  - processImagesAsync()                     │
│  - getAsyncTaskStatus()                     │
│  - listAsyncTasks()                         │
│  - getQueueInfo()                           │
└─────────────────────────────────────────────┘
```

## 处理流程

### 完整流程图

```
用户提交任务（文本/图片）
    ↓
前端: 检查 asyncMode
    ↓
【异步模式】              【同步模式】
    ↓                       ↓
调用 async API           调用同步 API
    ↓                       ↓
后端: 创建 Task          后端: 直接处理
    ↓                       ↓
后端: 加入队列            后端: 返回结果
    ↓                       ↓
后端: 立即返回 task_id   前端: 显示结果
    ↓
前端: 提示已提交
    ↓
用户: 可继续提交新任务
    ↓
后台线程: 从队列取任务
    ↓
后台线程: 调用处理函数
    ↓
后台线程: 更新任务状态
    ↓
后台线程: 保存到数据库
    ↓
前端轮询: 查询任务状态
    ↓
任务完成: 在队列中显示
    ↓
用户: 到历史记录查看
```

### 任务状态流转

```
submit_task()
    ↓
QUEUED (排队中)
    ↓
_worker_loop() 获取任务
    ↓
PROCESSING (处理中)
    ↓
_process_task() 调用处理函数
    ↓
COMPLETED / FAILED
```

## API 端点详情

### 1. POST /api/process/text/async
异步处理文本

**请求:**
```json
{
  "content": "面经文本内容",
  "generate_answers": false,
  "export_format": "both"
}
```

**响应:**
```json
{
  "task_id": "uuid",
  "status": "queued",
  "message": "任务已提交到队列，将在后台处理"
}
```

### 2. POST /api/process/images/async
异步处理图片

**请求:** multipart/form-data
- files: File[]
- generate_answers: boolean
- export_format: string

**响应:**
```json
{
  "task_id": "uuid",
  "status": "queued",
  "file_count": 3,
  "message": "任务已提交到队列，将处理 3 个文件"
}
```

### 3. GET /api/tasks/async/{task_id}
查询任务状态

**响应:**
```json
{
  "id": "task-id",
  "type": "text",
  "status": "completed",
  "created_at": "2025-01-20T10:00:00",
  "started_at": "2025-01-20T10:00:05",
  "completed_at": "2025-01-20T10:00:10",
  "processing_time": 5.2,
  "result": {
    "success": true,
    "experience_id": "exp-123",
    "experience": {...}
  },
  "error": null,
  "metadata": {}
}
```

### 4. GET /api/tasks/async
获取任务列表

**查询参数:**
- status (可选): queued, processing, completed, failed

**响应:**
```json
{
  "tasks": [...],
  "total": 10
}
```

### 5. GET /api/tasks/queue/info
获取队列统计

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

## 使用示例

### 前端使用

```typescript
// 异步提交文本
const response = await processTextAsync(text, false, 'both')
console.log(`任务已提交: ${response.task_id}`)
// 立即继续下一个操作

// 异步提交图片
const response = await processImagesAsync(files, false, 'both')
console.log(`已提交 ${response.file_count} 个文件`)
// 无需等待

// 查询任务状态
const status = await getAsyncTaskStatus(taskId)
console.log(`状态: ${status.status}`)
```

### 后端使用

```python
from src.utils.async_task_queue import task_queue, TaskType

# 提交任务
task_id = task_queue.submit_task(
    task_type=TaskType.TEXT,
    input_data="面经文本...",
    generate_answers=False,
    export_format="both"
)

# 查询任务
task = task_queue.get_task(task_id)
print(f"状态: {task.status}")

# 获取队列信息
info = task_queue.get_queue_info()
print(f"队列大小: {info['queue_size']}")
```

## 性能特点

### 优势
- ✅ 非阻塞提交，用户体验流畅
- ✅ 后台自动处理，无需等待
- ✅ 支持多任务连续提交
- ✅ 实时状态追踪
- ✅ 统一队列管理
- ✅ 线程安全设计
- ✅ 自动资源清理

### 限制
- ⚠️ 单线程处理（顺序执行）
- ⚠️ 任务存储在内存中（重启清空）
- ⚠️ 处理时间与队列长度成正比
- ⚠️ 当前不支持任务取消

### 推荐配置
- 队列大小：< 100 个任务
- 轮询间隔：3 秒
- 任务保留：24 小时
- 平均处理时间：5-10 秒/任务

## 测试

### 运行测试

```bash
# 启动后端
python -m uvicorn src.api.app:app --reload --port 8000

# 运行测试脚本
python tests/test_async_queue.py
```

### 测试覆盖

- ✅ 连续提交多个文本任务
- ✅ 连续提交多个图片任务
- ✅ 任务立即返回不阻塞
- ✅ 后台自动处理
- ✅ 任务状态查询
- ✅ 任务列表获取
- ✅ 队列信息统计
- ✅ 错误处理验证

## 与批量上传的对比

| 功能 | 批量上传 | 异步任务队列 |
|------|---------|-------------|
| 使用场景 | 一次性上传多个相关文件 | 多次独立提交任务 |
| 提交方式 | 一次提交所有文件 | 每次提交一个任务 |
| 处理方式 | 按顺序处理同一批次 | 统一队列管理 |
| 任务类型 | 仅图片 | 文本+图片 |
| 用户体验 | 等待批次完成 | 随时提交 |
| 进度显示 | 批次进度条 | 任务队列面板 |
| 适用场景 | 同一场面试的多个截图 | 日常使用 |

**两者可以共存！**
- 批量上传：处理一组相关文件
- 异步队列：日常连续提交任务

## 未来优化方向

### 短期 (1-2周)
1. 任务持久化（SQLite存储）
2. 支持任务取消
3. WebSocket 实时推送
4. 任务重试机制

### 中期 (1-2月)
1. 多线程并发处理
2. 任务优先级
3. 任务分组管理
4. 定时任务支持

### 长期 (3月+)
1. 分布式任务队列（Celery/RQ）
2. 任务调度优化
3. 完整的任务管理系统
4. 性能监控和报警

## 相关文档

- [完整使用指南](./ASYNC_QUEUE_GUIDE.md)
- [快速开始](./ASYNC_QUEUE_QUICKSTART.md)
- [批量上传对比](./BATCH_UPLOAD_GUIDE.md)
- [API 文档](http://localhost:8000/docs)

## 贡献者

- 实现时间: 2025-01-20
- 版本: v1.0.0
