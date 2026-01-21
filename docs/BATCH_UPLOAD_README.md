# 批量上传功能实现总结

## 功能概述

实现了面经批量上传功能，支持按照上传顺序逐个处理多个文件，并提供实时进度追踪。

## 实现的功能

### ✅ 核心功能

1. **批量任务管理**
   - 创建批量处理任务
   - 按上传顺序依次处理文件
   - 实时任务状态追踪
   - 自动保存处理结果

2. **进度可视化**
   - 总体进度条显示
   - 文件级别的状态展示
   - 实时统计（总数/完成/失败）
   - 处理耗时显示

3. **错误处理**
   - 单文件失败不影响其他文件
   - 详细错误信息展示
   - 自动清理临时文件

4. **用户界面**
   - 批量模式切换开关
   - 直观的进度展示
   - 完成后自动跳转

## 文件清单

### 新增文件

#### 后端
- [src/utils/batch_processor.py](../src/utils/batch_processor.py) - 批量任务处理器（核心）
- [tests/test_batch_upload.py](../tests/test_batch_upload.py) - 功能测试脚本

#### 前端
- [frontend/src/components/BatchProgress.tsx](../frontend/src/components/BatchProgress.tsx) - 进度显示组件

#### 文档
- [docs/BATCH_UPLOAD_GUIDE.md](./BATCH_UPLOAD_GUIDE.md) - 完整使用指南
- [docs/BATCH_UPLOAD_QUICKSTART.md](./BATCH_UPLOAD_QUICKSTART.md) - 快速开始指南
- [docs/BATCH_UPLOAD_README.md](./BATCH_UPLOAD_README.md) - 本文件

### 修改文件

#### 后端
- [src/api/app.py](../src/api/app.py)
  - 新增 `POST /api/process/batch` - 创建批量任务
  - 新增 `GET /api/batch/{task_id}` - 查询任务状态
  - 新增 `GET /api/batch` - 获取任务列表
  - 新增 `DELETE /api/batch/{task_id}` - 取消任务

#### 前端
- [frontend/src/components/UploadZone.tsx](../frontend/src/components/UploadZone.tsx)
  - 新增批量模式切换开关
  - 新增批量提交处理逻辑
  - 优化UI展示

- [frontend/src/services/api.ts](../frontend/src/services/api.ts)
  - 新增 `processBatch()` - 创建批量任务
  - 新增 `getBatchStatus()` - 查询任务状态
  - 新增 `listBatchTasks()` - 获取任务列表
  - 新增 `cancelBatchTask()` - 取消任务

- [frontend/src/App.tsx](../frontend/src/App.tsx)
  - 集成批量处理流程
  - 新增进度显示逻辑
  - 新增完成/错误处理

## 技术架构

### 后端架构

```
┌─────────────────────────────────────────────┐
│           API Layer (FastAPI)               │
│  POST /api/process/batch                    │
│  GET  /api/batch/{task_id}                  │
│  GET  /api/batch                            │
│  DELETE /api/batch/{task_id}                │
└────────────────┬────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────┐
│        BatchProcessor (单例)                │
│  - create_batch_task()                      │
│  - start_batch_processing()                 │
│  - get_task_status()                        │
│  - cancel_task()                            │
└────────────────┬────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────┐
│      Background Thread (按顺序处理)          │
│  For each file:                             │
│    1. OCR 提取文本                           │
│    2. 核心处理器分析                         │
│    3. 保存到数据库                           │
│    4. 更新任务状态                           │
└─────────────────────────────────────────────┘
```

### 前端架构

```
┌─────────────────────────────────────────────┐
│              App.tsx                        │
│  - 管理批量任务状态                          │
│  - 协调组件交互                              │
└────────────────┬────────────────────────────┘
                 │
         ┌───────┴───────┐
         ▼               ▼
┌─────────────┐   ┌──────────────┐
│ UploadZone  │   │BatchProgress │
│ - 批量模式   │   │ - 进度显示   │
│ - 文件选择   │   │ - 状态轮询   │
└─────────────┘   └──────────────┘
         │               │
         └───────┬───────┘
                 ▼
┌─────────────────────────────────────────────┐
│           api.ts (API Services)             │
│  - processBatch()                           │
│  - getBatchStatus()                         │
│  - listBatchTasks()                         │
└─────────────────────────────────────────────┘
```

## 数据结构

### BatchTask (批量任务)

```python
@dataclass
class BatchTask:
    id: str                          # 任务ID
    total_files: int                 # 文件总数
    created_at: str                  # 创建时间
    status: TaskStatus               # 任务状态
    current_index: int               # 当前处理索引
    completed_count: int             # 完成数量
    failed_count: int                # 失败数量
    sub_tasks: List[SubTask]         # 子任务列表
    started_at: Optional[str]        # 开始时间
    completed_at: Optional[str]      # 完成时间
    generate_answers: bool           # 是否生成答案
    export_format: str               # 导出格式
```

### SubTask (子任务)

```python
@dataclass
class SubTask:
    id: str                          # 子任务ID
    file_path: str                   # 文件路径
    file_name: str                   # 文件名
    status: TaskStatus               # 任务状态
    error: Optional[str]             # 错误信息
    result: Optional[Dict]           # 处理结果
    experience_id: Optional[str]     # 面经ID
    started_at: Optional[str]        # 开始时间
    completed_at: Optional[str]      # 完成时间
    processing_time: float           # 处理耗时
```

### TaskStatus (任务状态)

```python
class TaskStatus(str, Enum):
    PENDING = "pending"              # 等待中
    PROCESSING = "processing"        # 处理中
    COMPLETED = "completed"          # 已完成
    FAILED = "failed"                # 失败
    CANCELLED = "cancelled"          # 已取消
```

## 处理流程

### 完整流程图

```
用户操作
    ↓
选择多个文件
    ↓
勾选批量模式
    ↓
点击"批量处理"
    ↓
前端: processBatch(files)
    ↓
后端: 保存临时文件
    ↓
后端: create_batch_task()
    ↓
后端: start_batch_processing()
    ↓
后台线程启动
    ↓
┌─────────────────────┐
│ For each file:      │
│  1. 更新状态为处理中 │
│  2. OCR 提取文本    │
│  3. 核心处理器分析  │
│  4. 保存到数据库    │
│  5. 更新子任务状态  │
│  6. 清理临时文件    │
└─────────────────────┘
    ↓
前端: 轮询状态（2秒）
    ↓
前端: 更新进度UI
    ↓
所有文件处理完成
    ↓
显示完成统计
    ↓
自动跳转历史记录
```

## API 端点详情

### 1. POST /api/process/batch
创建批量处理任务

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
  "total_files": 3,
  "status": "processing",
  "message": "Batch processing started for 3 files"
}
```

### 2. GET /api/batch/{task_id}
查询任务状态

**响应:**
```json
{
  "id": "uuid",
  "total_files": 3,
  "status": "processing",
  "current_index": 1,
  "completed_count": 1,
  "failed_count": 0,
  "sub_tasks": [...]
}
```

### 3. GET /api/batch
获取任务列表

**查询参数:**
- `status`: 可选，过滤状态

**响应:**
```json
{
  "tasks": [...],
  "total": 10
}
```

### 4. DELETE /api/batch/{task_id}
取消任务（仅 pending 状态）

**响应:**
```json
{
  "success": true,
  "message": "Task cancelled successfully"
}
```

## 使用示例

### 前端使用

```typescript
// 创建批量任务
const response = await processBatch(files, false, 'both')
const taskId = response.task_id

// 轮询状态
const interval = setInterval(async () => {
  const status = await getBatchStatus(taskId)

  if (status.status !== 'processing') {
    clearInterval(interval)
    // 处理完成
  }
}, 2000)
```

### 后端使用

```python
from src.utils.batch_processor import batch_processor

# 创建任务
task_id = batch_processor.create_batch_task(
    file_paths=[...],
    file_names=[...],
    generate_answers=False,
    export_format="both"
)

# 启动处理
batch_processor.start_batch_processing(task_id, process_func)

# 查询状态
status = batch_processor.get_task_status(task_id)
```

## 性能特点

### 优势
- ✅ 按顺序处理，稳定可靠
- ✅ 实时进度反馈
- ✅ 单文件失败不影响其他
- ✅ 自动资源清理
- ✅ 内存占用低（顺序处理）

### 限制
- ⚠️ 不支持并发处理
- ⚠️ 任务状态存储在内存中
- ⚠️ 处理时间与文件数量成正比

### 推荐配置
- 单次上传：≤ 20 个文件
- 文件大小：≤ 10MB/个
- 轮询间隔：2 秒
- 任务保留：24 小时

## 测试

### 运行测试

```bash
# 启动后端
python -m uvicorn src.api.app:app --reload --port 8000

# 运行测试脚本
python tests/test_batch_upload.py
```

### 测试覆盖

- ✅ 批量任务创建
- ✅ 任务状态查询
- ✅ 任务列表获取
- ✅ 顺序处理验证
- ✅ 错误处理验证
- ✅ 进度更新验证

## 未来优化方向

### 短期 (1-2周)
1. 添加任务暂停/恢复功能
2. 支持任务优先级设置
3. 优化轮询机制（WebSocket）

### 中期 (1-2月)
1. 任务状态持久化到数据库
2. 支持并行处理模式
3. 添加任务历史查询

### 长期 (3月+)
1. 分布式任务处理
2. 任务调度优化
3. 完整的任务管理系统

## 相关文档

- [完整使用指南](./BATCH_UPLOAD_GUIDE.md)
- [快速开始](./BATCH_UPLOAD_QUICKSTART.md)
- [API 文档](http://localhost:8000/docs)

## 贡献者

- 实现时间: 2025-01-20
- 版本: v1.0.0
