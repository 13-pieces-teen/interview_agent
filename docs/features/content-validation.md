# 内容验证功能文档

## 功能概述

在调用AI大模型之前，使用**基于规则的轻量级验证器**快速判断用户输入是否为面经相关内容。这样可以：

1. **节省成本**：避免对无效输入调用昂贵的AI模型
2. **提升速度**：快速返回验证结果，无需等待AI响应
3. **改善体验**：提前给出明确的提示信息

## 验证逻辑

### 1. 基础验证（权重 20%）
- **长度检查**：最少10个字符
- **字符类型**：必须包含中文或英文字母
- **格式检查**：不能全是数字和符号

### 2. 关键词匹配（权重 50%）
检查是否包含面经相关关键词，包括：

**公司相关**：
- 公司、大厂、中厂、小厂、初创
- 字节、腾讯、阿里、百度、美团等

**面试相关**：
- 面试、一面、二面、三面、终面、HR面、技术面
- 面经、笔试、offer、挂了、通过

**职位相关**：
- 后端、前端、算法、开发、工程师、实习
- Java、Python、C++、Go等

**问题相关**：
- 问题、题目、算法题、手撕、项目、场景、设计
- 问：、答：、Q:、A:

**技术关键词**：
- 数据结构、算法、LeetCode、Redis、MySQL
- Transformer、大模型、RAG、Agent等

### 3. 结构检测（权重 30%）
检查内容是否包含典型的面经结构：

- 问答格式：`问：`、`答：`、`Q:`、`A:`
- 编号列表：`1.`、`2.`、`（1）`
- 多行结构：包含换行符

### 4. 负面检测（权重 -30%）
检测明显不是面经的内容：

- 测试性质文本：test、hello、你好
- 疑问句：怎么、如何、能否、请问
- 过短且包含负面关键词的内容

## 评分机制

**置信度分数范围**：0-100

- **70-100分**：内容很可能是面经，可以处理
- **50-69分**：内容可能是面经，建议确认
- **30-49分**：内容勉强通过验证，建议检查
- **0-29分**：内容不是面经，拒绝处理

**阈值**：30分（低于30分将被拒绝）

## API端点

### 1. 内容验证端点

**请求**：
```http
POST /api/validate
Content-Type: application/json

{
  "content": "用户输入的文本内容"
}
```

**响应**：
```json
{
  "is_valid": true,
  "confidence_score": 80,
  "message": "内容看起来是面经相关，可以处理"
}
```

### 2. 处理端点（自动验证）

**请求**：
```http
POST /api/process/text
Content-Type: application/json

{
  "content": "面经内容",
  "generate_answers": false,
  "export_format": "both"
}
```

**响应**（验证失败时）：
```json
{
  "success": false,
  "processing_time": 0.001,
  "error": "输入内容似乎不是面经相关。建议包含面试相关信息...",
  "validation_score": 20,
  "validation_message": "输入内容似乎不是面经相关。建议包含面试相关信息..."
}
```

**响应**（验证成功时）：
```json
{
  "success": true,
  "processing_time": 2.5,
  "experience": { ... },
  "experience_id": "uuid-here",
  "output_files": ["output.json", "output.md"],
  "validation_score": 80,
  "validation_message": "内容看起来是面经相关，可以处理"
}
```

## 使用示例

### Python示例

```python
from src.validators.content_validator import validate_content

# 验证内容
content = "字节跳动一面面经：介绍一下Transformer"
is_valid, score, message = validate_content(content)

print(f"验证结果: {'通过' if is_valid else '未通过'}")
print(f"置信度分数: {score}/100")
print(f"提示信息: {message}")
```

### 前端集成示例

```typescript
// 1. 先验证内容（可选，可以提供即时反馈）
const validateContent = async (content: string) => {
  const response = await api.post('/validate', { content })
  return response.data
}

// 2. 处理内容（自动验证）
const processContent = async (content: string) => {
  const response = await api.post('/process/text', {
    content,
    generate_answers: false,
    export_format: 'both'
  })

  if (!response.data.success) {
    // 显示验证错误信息
    alert(response.data.validation_message)
  }

  return response.data
}
```

## 测试用例

运行测试：
```bash
python test_validator.py
```

测试包含：
- ✓ 有效面经内容（包含公司、职位、面试题目）
- ✓ 无效内容（过短、无关内容）
- ✓ 边界情况（问答格式、疑问句等）

## 优势

1. **零成本**：完全基于规则，不调用AI模型
2. **极快响应**：通常在1ms内完成验证
3. **可调节**：可以调整关键词、权重、阈值
4. **可扩展**：易于添加新的验证规则
5. **透明度高**：返回置信度分数和详细提示

## 局限性

1. **规则局限**：基于预定义规则，可能有漏判或误判
2. **语言限制**：主要针对中文面经优化
3. **上下文理解**：无法像AI模型那样深度理解语义

## 未来改进方向

1. **机器学习增强**：使用小型分类模型提升准确性
2. **自适应阈值**：根据历史数据动态调整阈值
3. **多语言支持**：添加英文面经的关键词库
4. **用户反馈学习**：收集误判案例优化规则

## 配置选项

可以在 `src/validators/content_validator.py` 中调整：

```python
# 修改验证阈值（默认30）
threshold = 30

# 修改权重分配
total_score = int(
    basic_score * 0.2 +      # 基础验证权重
    keyword_score * 0.5 +    # 关键词匹配权重
    structure_score * 0.3 -  # 结构检测权重
    negative_score * 0.3     # 负面检测权重
)

# 添加自定义关键词
INTERVIEW_KEYWORDS.add("你的关键词")
```

## 总结

内容验证功能提供了一个**快速、低成本的预检层**，在调用昂贵的AI模型之前过滤掉明显无效的输入，既节省了成本，又提升了用户体验。
