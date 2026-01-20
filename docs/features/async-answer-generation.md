# 异步答案生成功能实现文档

## 架构设计

### 1. 工作流程

```
用户提交面经
     ↓
快速提取结构（5-10秒）
     ↓
返回结果给用户（用户可以立即继续输入下一个）
     ↓
如果用户勾选"生成答案"
     ↓
后台异步生成答案（15-30秒）
     ↓
完成后更新数据库
     ↓
前端轮询或WebSocket通知用户
```

### 2. 已实现组件

#### Answer Generator Agent
文件: [src/agents/answer_generator.py](src/agents/answer_generator.py)

- 专门负责答案生成的Agent
- 输入：问题列表
- 输出：生成的答案列表
- 使用独立的System Prompt优化答案质量

### 3. 需要实现的组件

#### 3.1 后端API端点

需要在 `src/api/app.py` 添加：

```python
import asyncio
from threading import Thread
from typing import Dict
import uuid

# 全局变量：答案生成任务状态
answer_generation_tasks: Dict[str, dict] = {}

@app.post("/api/experiences/{experience_id}/generate-answers")
async def generate_answers_async(experience_id: str):
    """
    异步生成面经答案

    工作流程:
    1. 立即返回任务ID
    2. 在后台线程中生成答案
    3. 完成后更新数据库
    """
    # 获取面经
    experience = db.get_experience(experience_id)
    if not experience:
        raise HTTPException(status_code=404, detail="Experience not found")

    # 创建任务
    task_id = str(uuid.uuid4())
    answer_generation_tasks[task_id] = {
        "status": "pending",
        "experience_id": experience_id,
        "progress": 0,
        "total_questions": len(experience.questions)
    }

    # 启动后台任务
    thread = Thread(
        target=_generate_answers_background,
        args=(task_id, experience_id, experience)
    )
    thread.daemon = True
    thread.start()

    return {
        "task_id": task_id,
        "status": "started",
        "message": "答案生成任务已启动"
    }


def _generate_answers_background(task_id: str, experience_id: str, experience):
    """后台生成答案"""
    try:
        answer_generation_tasks[task_id]["status"] = "processing"

        # 使用AnswerGeneratorAgent生成答案
        from src.agents.answer_generator import AnswerGeneratorAgent
        generator = AnswerGeneratorAgent(agent.client)

        generated_answers = generator.generate_answers(experience.questions)

        # 更新问题的答案
        for i, answer in enumerate(generated_answers):
            if answer and not experience.questions[i].has_original_answer:
                experience.questions[i].answer = answer

        # 保存回数据库
        db.save_experience(experience)

        answer_generation_tasks[task_id]["status"] = "completed"
        answer_generation_tasks[task_id]["progress"] = len(experience.questions)

    except Exception as e:
        answer_generation_tasks[task_id]["status"] = "failed"
        answer_generation_tasks[task_id]["error"] = str(e)


@app.get("/api/tasks/{task_id}")
async def get_task_status(task_id: str):
    """获取任务状态"""
    if task_id not in answer_generation_tasks:
        raise HTTPException(status_code=404, detail="Task not found")

    return answer_generation_tasks[task_id]
```

#### 3.2 修改现有处理端点

将 `/api/process/text`, `/api/process/image`, `/api/process/images` 中：

```python
# 移除 generate_answers 参数
# 修改为：
result = agent.process(
    input_data=request.content,
    export_format=request.export_format,
)

# 保存后，如果用户勾选了生成答案，返回任务提示
response_data = {
    "success": True,
    "processing_time": processing_time,
    "experience": result.experience.model_dump() if result.experience else None,
    "experience_id": experience_id,
    "output_files": result.output_files,
}

# 前端可以根据用户选择调用异步答案生成API
return ProcessResponse(**response_data)
```

#### 3.3 前端修改

**文件**: [frontend/src/App.tsx](frontend/src/App.tsx)

```typescript
const handleTextSubmit = async (text: string) => {
  setIsProcessing(true)
  setError(null)
  setResult(null)

  try {
    // 第一步：快速提取面经结构
    const response = await processText(text, 'both')
    setResult(response)

    if (!response.success) {
      setError(response.error || 'Unknown error occurred')
      return
    }

    // 第二步：如果用户勾选了生成答案，异步生成
    if (generateAnswers && response.experience_id) {
      // 在后台生成，不阻塞用户
      generateAnswersAsync(response.experience_id)
        .then(() => {
          // 可选：显示通知
          console.log('答案生成完成')
        })
        .catch(err => console.error('答案生成失败:', err))
    }
  } catch (err) {
    setError(err instanceof Error ? err.message : 'Failed to process')
  } finally {
    setIsProcessing(false)
  }
}
```

**文件**: [frontend/src/services/api.ts](frontend/src/services/api.ts)

```typescript
export const generateAnswersAsync = async (experienceId: string): Promise<{task_id: string}> => {
  const response = await api.post(`/experiences/${experienceId}/generate-answers`)
  return response.data
}

export const getTaskStatus = async (taskId: string) => {
  const response = await api.get(`/tasks/${taskId}`)
  return response.data
}
```

### 4. 实现优先级

#### 阶段1：基础功能（当前任务）
- ✅ 创建 AnswerGeneratorAgent
- ⏳ 添加后端异步答案生成API
- ⏳ 修改现有API端点移除 generate_answers 参数
- ⏳ 前端调用异步API

#### 阶段2：用户体验优化
- 添加答案生成进度显示
- 添加"重新生成答案"按钮
- WebSocket实时通知（替代轮询）

#### 阶段3：高级功能
- 支持单个问题重新生成答案
- 答案质量评分
- 用户编辑和保存答案

### 5. 技术要点

#### 后台任务管理
- 使用 `threading.Thread` 简单实现
- 生产环境建议使用 Celery + Redis

#### 前端状态管理
- 不阻塞用户继续输入
- 可选显示生成进度（轮询task状态）

#### 数据库
- 当前schema已支持，无需修改
- `has_original_answer` 字段区分原始答案和生成答案

## 下一步

继续实现后端API端点。
