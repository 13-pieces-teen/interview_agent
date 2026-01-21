# 异步任务队列 - 快速开始

## 5分钟快速上手

### 1. 启动服务

```bash
# 启动后端
python -m uvicorn src.api.app:app --reload --port 8000

# 启动前端（新终端）
cd frontend
npm run dev
```

### 2. 使用异步模式

1. 打开浏览器访问 http://localhost:5173
2. 勾选 **"异步处理模式（推荐）"**
3. 输入面经文本或上传图片
4. 点击提交 → 任务立即提交到队列
5. 继续提交下一个任务，无需等待！

### 3. 查看任务进度

点击顶部 **"任务队列"** 按钮，实时查看所有任务状态

## 核心概念

### 异步模式 vs 同步模式

| | 异步模式 | 同步模式 |
|--|---------|---------|
| 提交后 | 立即返回 ✓ | 等待完成 ⏳ |
| 继续操作 | 可以 ✓ | 不可以 ✗ |
| 适用场景 | 日常使用 | 需要立即看结果 |

### 使用建议

**推荐使用异步模式：**
- ✅ 提交多个面经
- ✅ 不着急看结果
- ✅ 想要流畅体验

**使用同步模式：**
- 只有一个任务
- 需要立即查看结果
- 处理紧急面经

## 快速测试

### 使用Web界面

1. 勾选"异步处理模式"
2. 连续提交3个文本任务：
   ```
   任务1: "腾讯前端面试，问了Vue和React..."
   任务2: "字节跳动后端面试，问了MySQL..."
   任务3: "阿里云架构面试，问了分布式..."
   ```
3. 打开"任务队列"查看
4. 到"历史记录"查看生成的面经

### 使用API测试

```python
import requests

# 连续提交3个任务
texts = ["面经1...", "面经2...", "面经3..."]

for text in texts:
    response = requests.post(
        'http://localhost:8000/api/process/text/async',
        json={'content': text, 'generate_answers': False, 'export_format': 'both'}
    )
    print(f"已提交: {response.json()['task_id'][:8]}...")
    # 立即提交下一个，无需等待！

print("✓ 所有任务已提交！")
```

### 运行测试脚本

```bash
python tests/test_async_queue.py
```

## 常见操作

### 查看队列状态

**Web界面**: 点击"任务队列"按钮

**API**:
```bash
curl http://localhost:8000/api/tasks/queue/info
```

### 查询特定任务

**API**:
```bash
curl http://localhost:8000/api/tasks/async/{task_id}
```

### 获取所有任务

**API**:
```bash
# 所有任务
curl http://localhost:8000/api/tasks/async

# 只看已完成的
curl http://localhost:8000/api/tasks/async?status=completed

# 只看处理中的
curl http://localhost:8000/api/tasks/async?status=processing
```

## 核心文件

| 文件 | 说明 |
|-----|------|
| [src/utils/async_task_queue.py](../src/utils/async_task_queue.py) | 任务队列核心 |
| [src/api/app.py](../src/api/app.py) | 异步API端点 |
| [frontend/src/components/TaskQueue.tsx](../frontend/src/components/TaskQueue.tsx) | 队列UI组件 |
| [frontend/src/App.tsx](../frontend/src/App.tsx) | 异步模式集成 |

## 下一步

- 查看完整文档: [docs/ASYNC_QUEUE_GUIDE.md](./ASYNC_QUEUE_GUIDE.md)
- 运行测试: `python tests/test_async_queue.py`
- 查看 API 文档: http://localhost:8000/docs

## 常见问题

**Q: 为什么推荐使用异步模式？**

A: 异步模式让你可以连续提交多个任务，不用等待，体验更流畅。

**Q: 如何知道任务完成了？**

A: 打开"任务队列"查看，或者到"历史记录"查看新面经。

**Q: 任务会按顺序处理吗？**

A: 是的，任务按提交顺序排队处理。

**Q: 如果想等待结果怎么办？**

A: 取消勾选"异步处理模式"，切换到同步模式。
