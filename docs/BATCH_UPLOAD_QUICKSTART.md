# 批量上传功能 - 快速开始

## 5 分钟快速上手

### 1. 启动后端服务

```bash
# 在项目根目录
python -m uvicorn src.api.app:app --reload --port 8000
```

### 2. 启动前端服务

```bash
cd frontend
npm install  # 首次运行
npm run dev
```

### 3. 使用批量上传

1. 打开浏览器访问 http://localhost:5173
2. 点击"图片上传"标签
3. 上传或拖拽多张面经截图（2张以上）
4. 勾选"批量模式"复选框
5. 点击"批量处理 N 张图片（按顺序）"
6. 观察实时处理进度
7. 完成后自动跳转到历史记录

## 功能演示

### 批量模式界面

```
┌─────────────────────────────────────────┐
│  ☑ 批量模式                              │
│  批量模式：将按照上传顺序依次处理每张    │
│  图片，可实时查看进度                    │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│  已选择 3 张图片           ☑ 批量模式 清空│
├─────────────────────────────────────────┤
│  [图1] [图2] [图3]                       │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│    批量处理 3 张图片（按顺序） ▶          │
└─────────────────────────────────────────┘
```

### 进度显示

```
┌─────────────────────────────────────────┐
│  批量处理进度              PROCESSING     │
├─────────────────────────────────────────┤
│  ████████████░░░░░░░░░░░░░░░░  60%      │
├─────────────────────────────────────────┤
│  总文件数    已完成      失败             │
│     3         2         0               │
└─────────────────────────────────────────┘

文件处理详情:
  ✓ [1] image1.png: 完成 (3.2s)
  ⊙ [2] image2.png: 处理中
  ○ [3] image3.png: 等待中

正在处理第 2 个文件，共 3 个...
```

## API 快速测试

### Python 示例

```python
import requests

# 创建批量任务
files = [
    ('files', ('img1.png', open('img1.png', 'rb'), 'image/png')),
    ('files', ('img2.png', open('img2.png', 'rb'), 'image/png')),
]

response = requests.post(
    'http://localhost:8000/api/process/batch',
    files=files,
    data={'generate_answers': 'false', 'export_format': 'both'}
)

task_id = response.json()['task_id']
print(f"任务创建成功: {task_id}")

# 查询状态
import time
while True:
    status = requests.get(f'http://localhost:8000/api/batch/{task_id}').json()
    print(f"进度: {status['completed_count']}/{status['total_files']}")

    if status['status'] != 'processing':
        break
    time.sleep(2)

print("处理完成!")
```

### cURL 示例

```bash
# 创建批量任务
curl -X POST "http://localhost:8000/api/process/batch" \
  -F "files=@image1.png" \
  -F "files=@image2.png" \
  -F "generate_answers=false" \
  -F "export_format=both"

# 查询状态（替换 {task_id}）
curl "http://localhost:8000/api/batch/{task_id}"

# 获取所有任务
curl "http://localhost:8000/api/batch"
```

## 核心文件说明

| 文件路径 | 说明 |
|---------|------|
| `src/utils/batch_processor.py` | 批量任务处理器（核心逻辑） |
| `src/api/app.py` | API 端点（新增批量接口） |
| `frontend/src/components/BatchProgress.tsx` | 进度显示组件 |
| `frontend/src/components/UploadZone.tsx` | 上传组件（新增批量模式） |
| `frontend/src/services/api.ts` | API 调用函数 |

## 常见问题

**Q: 批量模式和普通模式有什么区别？**

A:
- **普通模式**: 合并所有图片内容，生成一个面经
- **批量模式**: 按顺序独立处理，生成多个面经，可查看进度

**Q: 一次最多可以上传多少文件？**

A: 建议不超过 20 个文件，每个文件不超过 10MB

**Q: 处理失败会怎样？**

A: 单个文件失败不影响其他文件，会显示具体的错误信息

**Q: 可以取消正在处理的任务吗？**

A: 目前只能取消状态为 pending 的任务，正在处理的任务无法取消

## 下一步

- 查看完整文档: [docs/BATCH_UPLOAD_GUIDE.md](./BATCH_UPLOAD_GUIDE.md)
- 运行测试: `python tests/test_batch_upload.py`
- 查看 API 文档: http://localhost:8000/docs
