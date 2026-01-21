# 异步任务队列 BUG 修复

## 问题描述

**问题 1**: 提交任务后无法在列表中刷新看到
**问题 2**: 重复的 API GET 请求失败（404错误）

```
INFO: 127.0.0.1:xxx - "GET /api/tasks/async?status=completed HTTP/1.1" 404 Not Found
```

**现象**:
- ✅ 任务提交成功
- ✅ 后台处理完成
- ❌ 前端任务队列面板显示"暂无任务"
- ❌ API 请求返回 404

## 根本原因

### FastAPI 路由顺序问题

FastAPI 按照定义顺序匹配路由。带路径参数的路由 `/api/tasks/async/{task_id}` 定义在列表路由 `/api/tasks/async` 之前，导致所有请求都被当作查询特定任务处理。

```python
# ❌ 错误（旧代码）
@app.get("/api/tasks/async/{task_id}")  # 先定义
async def get_async_task_status(task_id: str): ...

@app.get("/api/tasks/async")  # 后定义，永远匹配不到
async def list_async_tasks(status: Optional[str] = None): ...

# 请求 GET /api/tasks/async?status=completed
# 会被匹配到第一个路由，task_id="" 或 task_id=None
# 查找不到任务，返回 404
```

```python
# ✅ 正确（新代码）
@app.get("/api/tasks/async")  # 先定义，精确匹配
async def list_async_tasks(status: Optional[str] = None): ...

@app.get("/api/tasks/async/{task_id}")  # 后定义
async def get_async_task_status(task_id: str): ...
```

## 修复内容

### 修改的文件

1. **src/api/app.py**
   - 调换路由定义顺序 (1055-1134行)
   - 修复枚举序列化问题
   - 优化状态过滤逻辑

2. **src/utils/async_task_queue.py**
   - 修改 `get_all_tasks` 方法支持字符串状态过滤 (146-165行)

### 关键修复

```python
# app.py

# 1️⃣ 路由顺序修复
@app.get("/api/tasks/async")  # 必须在前
async def list_async_tasks(status: Optional[str] = None): ...

@app.get("/api/tasks/async/{task_id}")  # 必须在后
async def get_async_task_status(task_id: str): ...

# 2️⃣ 枚举序列化修复
return {
    "type": task.type.value if hasattr(task.type, 'value') else task.type,
    "status": task.status.value if hasattr(task.status, 'value') else task.status,
    ...
}

# 3️⃣ 状态过滤修复
status_filter = None
if status:
    valid_statuses = {s.value for s in AsyncTaskStatus}
    if status not in valid_statuses:
        raise HTTPException(status_code=400, detail=...)
    status_filter = status  # 传递字符串

# async_task_queue.py

# 4️⃣ 字符串比较修复
def get_all_tasks(self, status: Optional[str] = None) -> List[Task]:
    tasks = list(self._tasks.values())
    if status:
        tasks = [t for t in tasks if t.status.value == status]  # 比较枚举值
    return tasks
```

## 如何应用修复

### ⚠️ 重要：必须重启后端服务

```bash
# 1. 停止当前后端服务
# 在后端终端按 Ctrl+C

# 2. 重新启动
python -m uvicorn src.api.app:app --reload --port 8000

# 3. 验证修复
python tests/verify_async_fix.py
```

### 验证步骤

1. **命令行测试**:
```bash
# 查询所有任务（应该返回任务列表而不是404）
curl "http://localhost:8000/api/tasks/async"

# 按状态过滤（应该返回过滤后的任务）
curl "http://localhost:8000/api/tasks/async?status=completed"

# 队列信息（应该返回统计数据）
curl "http://localhost:8000/api/tasks/queue/info"
```

2. **前端测试**:
   - 打开浏览器访问 http://localhost:5173
   - 提交一个测试任务
   - 点击"任务队列"按钮
   - ✅ 应该能看到任务列表
   - ✅ 可以按状态过滤
   - ✅ 实时刷新显示进度

3. **自动化测试**:
```bash
python tests/verify_async_fix.py
```

## 预期结果

### API 响应

**GET /api/tasks/async**
```json
{
  "tasks": [
    {
      "id": "xxx",
      "type": "text",
      "status": "completed",
      "created_at": "2026-01-20T...",
      "processing_time": 41.18,
      ...
    }
  ],
  "total": 1
}
```

### 前端显示

```
┌─────────────────────────────────────┐
│  📋 任务队列                  🔄     │
├─────────────────────────────────────┤
│  全部(2) 排队中(0) 处理中(0) 已完成(2) │
├─────────────────────────────────────┤
│  ✓ [文本] 5分钟前                    │
│     耗时: 41.18s  状态: 已完成        │
└─────────────────────────────────────┘
```

## 技术要点

### FastAPI 路由匹配规则

1. **顺序敏感**: 按定义顺序匹配路由
2. **精确优先**: 无参数路由应在前
3. **参数匹配**: 带 `{param}` 的路由应在后

### 最佳实践

```python
# ✅ 推荐顺序
@app.get("/items/special")      # 1. 精确路径
@app.get("/items/{item_id}")    # 2. 路径参数

# ❌ 错误顺序
@app.get("/items/{item_id}")    # 会匹配所有 /items/*
@app.get("/items/special")      # 永远不会被匹配
```

## 相关文档

- [详细修复指南](./BUGFIX_ASYNC_QUEUE.md)
- [异步队列使用指南](./ASYNC_QUEUE_GUIDE.md)
- [快速开始](./ASYNC_QUEUE_QUICKSTART.md)

## 版本信息

- 问题发现: 2026-01-20
- 修复完成: 2026-01-20
- 影响版本: v1.0.0
- 修复版本: v1.0.1

## 常见问题

**Q: 重启后仍然返回404？**

A: 检查以下几点：
1. 确认服务器完全停止后再启动
2. 检查代码是否正确保存
3. 清除浏览器缓存（Ctrl+Shift+R）
4. 查看后端启动日志是否有错误

**Q: 如何确认使用的是新代码？**

A: 运行验证脚本：
```bash
python tests/verify_async_fix.py
```

**Q: 前端仍然显示"暂无任务"？**

A:
1. 检查浏览器开发者工具 Network 标签
2. 确认 API 请求返回 200 而不是 404
3. 检查返回的 JSON 数据是否正确
4. 强制刷新页面（Ctrl+Shift+R）
