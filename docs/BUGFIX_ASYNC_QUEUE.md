# 异步任务队列 - 问题修复指南

## 问题现象

1. **任务提交后无法在列表中显示**
   - 任务队列面板显示"暂无任务"
   - 后台日志显示任务已处理完成
   - API 请求返回 404 错误

2. **重复的 API GET 请求失败**
   ```
   INFO: 127.0.0.1:xxx - "GET /api/tasks/async?status=completed HTTP/1.1" 404 Not Found
   ```

## 根本原因

### 问题 1: FastAPI 路由顺序问题

**原因**: FastAPI 按照定义顺序匹配路由。如果 `/api/tasks/async/{task_id}` 定义在 `/api/tasks/async` 之前，所有请求都会被当作带 `task_id` 参数的路由处理。

**示例**:
```python
# ❌ 错误顺序
@app.get("/api/tasks/async/{task_id}")  # 先定义
async def get_async_task_status(task_id: str): ...

@app.get("/api/tasks/async")  # 后定义，永远不会匹配
async def list_async_tasks(status: Optional[str] = None): ...
```

当请求 `GET /api/tasks/async?status=completed` 时：
- FastAPI 匹配到第一个路由 `/api/tasks/async/{task_id}`
- 将空字符串或查询参数当作 `task_id`
- 在任务字典中找不到对应任务
- 返回 404 "任务不存在"

**修复**: 调换路由定义顺序
```python
# ✅ 正确顺序
@app.get("/api/tasks/async")  # 先定义，精确匹配
async def list_async_tasks(status: Optional[str] = None): ...

@app.get("/api/tasks/async/{task_id}")  # 后定义，路径参数匹配
async def get_async_task_status(task_id: str): ...
```

### 问题 2: 枚举类型序列化

**原因**: 任务对象的 `type` 和 `status` 字段是枚举类型（`TaskType.TEXT`, `TaskStatus.COMPLETED`），直接序列化为 JSON 会产生枚举对象而不是字符串。

**修复**: 在返回响应时转换为字符串值
```python
# ✅ 正确做法
return {
    "type": task.type.value if hasattr(task.type, 'value') else task.type,
    "status": task.status.value if hasattr(task.status, 'value') else task.status,
    ...
}
```

### 问题 3: 状态过滤参数类型不匹配

**原因**: API 接收的 `status` 参数是字符串，但 `get_all_tasks` 尝试与枚举对象比较。

**修复**:
1. API 端：传递字符串而不是转换为枚举
2. Queue 端：使用 `task.status.value == status` 比较枚举的字符串值

## 已修复的文件

### 1. src/api/app.py

**修改内容**:
- ✅ 调换路由顺序（1055-1134行）
- ✅ 枚举转字符串（1088-1089, 1124-1125行）
- ✅ 状态验证逻辑优化（1070-1079行）

**关键代码**:
```python
# 路由顺序
@app.get("/api/tasks/async")  # 先定义
async def list_async_tasks(status: Optional[str] = None): ...

@app.get("/api/tasks/async/{task_id}")  # 后定义
async def get_async_task_status(task_id: str): ...

# 状态过滤
status_filter = None
if status:
    # 验证状态值
    valid_statuses = {s.value for s in AsyncTaskStatus}
    if status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Invalid status...")
    # 直接传递字符串
    status_filter = status

# 枚举序列化
"type": task.type.value if hasattr(task.type, 'value') else task.type,
"status": task.status.value if hasattr(task.status, 'value') else task.status,
```

### 2. src/utils/async_task_queue.py

**修改内容**:
- ✅ `get_all_tasks` 方法支持字符串过滤（146-165行）

**关键代码**:
```python
def get_all_tasks(self, status: Optional[str] = None) -> List[Task]:
    """
    Args:
        status: 字符串值 "queued", "processing", "completed", "failed"
    """
    tasks = list(self._tasks.values())

    if status:
        # 比较枚举的字符串值
        tasks = [t for t in tasks if t.status.value == status]

    tasks.sort(key=lambda t: t.created_at, reverse=True)
    return tasks
```

## 如何应用修复

### ⚠️ 重要：必须重启后端服务

由于 FastAPI 的 `--reload` 模式只监控文件保存，修改已经保存但服务还在使用旧代码。

**步骤**:

1. **停止当前后端服务**
   ```bash
   # 在运行后端的终端按 Ctrl+C
   ```

2. **重新启动后端**
   ```bash
   cd d:\LLM_learning\interview_agent
   python -m uvicorn src.api.app:app --reload --port 8000
   ```

3. **验证修复是否生效**
   ```bash
   # 查询所有任务
   curl "http://localhost:8000/api/tasks/async"

   # 应该返回类似:
   # {"tasks": [...], "total": N}

   # 查询已完成任务
   curl "http://localhost:8000/api/tasks/async?status=completed"

   # 查询队列信息
   curl "http://localhost:8000/api/tasks/queue/info"
   ```

## 验证清单

重启后端服务后，检查以下功能：

- [ ] 提交新任务成功
  ```bash
  curl -X POST http://localhost:8000/api/process/text/async \
    -H "Content-Type: application/json" \
    -d '{"content":"测试面经：公司腾讯，岗位前端","generate_answers":false,"export_format":"both"}'
  ```

- [ ] 查询所有任务列表
  ```bash
  curl "http://localhost:8000/api/tasks/async"
  ```

- [ ] 按状态过滤任务
  ```bash
  curl "http://localhost:8000/api/tasks/async?status=completed"
  curl "http://localhost:8000/api/tasks/async?status=processing"
  ```

- [ ] 查询特定任务
  ```bash
  curl "http://localhost:8000/api/tasks/async/{task_id}"
  ```

- [ ] 前端任务队列面板显示任务列表
  - 打开浏览器访问 http://localhost:5173
  - 点击"任务队列"按钮
  - 应该能看到所有已提交的任务

## 预期结果

### API 响应示例

**GET /api/tasks/async**
```json
{
  "tasks": [
    {
      "id": "5b71d2a5-4df6-4ef8-a6e8-d5743194cbc5",
      "type": "text",
      "status": "completed",
      "created_at": "2026-01-20T23:32:01.131354",
      "started_at": "2026-01-20T23:32:01.134786",
      "completed_at": "2026-01-20T23:32:42.315123",
      "processing_time": 41.18,
      "error": null,
      "metadata": {
        "validation_score": 55,
        "validation_message": "内容可能是面经相关，建议确认"
      }
    }
  ],
  "total": 1
}
```

**GET /api/tasks/async?status=completed**
```json
{
  "tasks": [
    // 只包含已完成的任务
  ],
  "total": N
}
```

### 前端显示

任务队列面板应该显示：

```
┌─────────────────────────────────────┐
│  📋 任务队列                  🔄     │
├─────────────────────────────────────┤
│  全部(2) 排队中(0) 处理中(0) 已完成(2) 失败(0) │
├─────────────────────────────────────┤
│  ✓ [文本] 5分钟前                    │
│     耗时: 41.18s  状态: 已完成        │
├─────────────────────────────────────┤
│  ✓ [文本] 10分钟前                   │
│     耗时: 38.52s  状态: 已完成        │
└─────────────────────────────────────┘
```

## 排查步骤（如果问题依然存在）

1. **确认后端服务已重启**
   ```bash
   # 检查启动日志，应该看到：
   # ✓ 异步任务队列系统已启动
   ```

2. **清除浏览器缓存**
   - 按 Ctrl+Shift+R 强制刷新
   - 或打开开发者工具，右键刷新按钮选择"清空缓存并硬性重新加载"

3. **检查前端控制台**
   - 按 F12 打开开发者工具
   - 查看 Console 是否有错误
   - 查看 Network 标签，确认 API 请求状态

4. **测试 API 端点**
   ```bash
   # 测试基础连接
   curl http://localhost:8000/health

   # 测试队列信息
   curl http://localhost:8000/api/tasks/queue/info

   # 测试任务列表
   curl http://localhost:8000/api/tasks/async
   ```

5. **查看后端日志**
   - 检查是否有错误信息
   - 确认任务处理完成的日志：`✓ 任务完成: xxx (耗时: xx.xxs)`

## 技术总结

### FastAPI 路由匹配规则

1. **顺序优先**: 按照路由定义的顺序匹配
2. **精确匹配优先**: 没有路径参数的路由应该定义在前面
3. **路径参数匹配**: 带 `{param}` 的路由应该定义在后面

**最佳实践**:
```python
# ✅ 正确顺序
@app.get("/users/me")          # 精确匹配
@app.get("/users/{user_id}")   # 路径参数匹配

# ❌ 错误顺序
@app.get("/users/{user_id}")   # 会匹配所有 /users/* 请求
@app.get("/users/me")          # 永远不会被匹配
```

### Pydantic 枚举序列化

使用枚举时需要注意序列化：

```python
from enum import Enum

class Status(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"

# 枚举对象
status = Status.ACTIVE

# 序列化为字符串
status_str = status.value  # "active"

# FastAPI 响应
return {"status": status.value}  # ✅ 正确
return {"status": status}         # ❌ 可能导致序列化问题
```

## 相关文档

- [FastAPI 路由文档](https://fastapi.tiangolo.com/tutorial/path-params/#order-matters)
- [Python Enum 文档](https://docs.python.org/3/library/enum.html)
- [异步队列使用指南](./ASYNC_QUEUE_GUIDE.md)
- [快速开始](./ASYNC_QUEUE_QUICKSTART.md)

## 版本信息

- 修复时间: 2026-01-20
- 受影响版本: v1.0.0
- 修复版本: v1.0.1
