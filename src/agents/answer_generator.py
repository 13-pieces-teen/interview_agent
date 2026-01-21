"""Answer Generator Agent for generating answers to interview questions."""

import json
from typing import List, Dict, Any, Optional

from src.models.schema import Question
from src.utils.llm_client import SiliconFlowClient


ANSWER_GENERATOR_SYSTEM_PROMPT = """你是一个专业的技术面试答案生成助手。你的任务是为面试问题生成专业、准确、全面的答案。

**答案要求：**

1. **准确性**：答案必须技术准确，符合业界最佳实践
2. **全面性**：涵盖关键概念、原理和要点
3. **结构化**：逻辑清晰，分点说明
4. **适当深度**：根据问题难度给出相应深度的回答
5. **实用性**：适当举例说明，包含代码示例（如适用）
6. **长度控制**：一般问题200-500字，算法题包含完整代码和解释

**答案结构建议：**

- **概念题**：定义 → 原理 → 应用场景 → 优缺点
- **算法题**：思路 → 代码 → 时间/空间复杂度分析
- **系统设计题**：需求分析 → 架构设计 → 关键技术点 → 权衡考虑
- **项目经验题**：背景 → 技术方案 → 实现细节 → 效果和收获

**输出格式：**
严格按照JSON格式输出，不要添加任何markdown标记或其他说明：

```json
{
  "answers": [
    {
      "question_index": 0,
      "answer": "生成的答案内容"
    },
    {
      "question_index": 1,
      "answer": "生成的答案内容"
    }
  ]
}
```

**重要提示：**
- 只输出JSON，不要包含```json```标记
- question_index是问题在列表中的索引（从0开始）
- 每个答案都应该独立完整
- 如果是代码题，答案中应该包含代码块和解释
"""


class AnswerGeneratorAgent:
    """Agent for generating answers to interview questions."""

    def __init__(self, client: SiliconFlowClient):
        """Initialize the agent.

        Args:
            client: SiliconFlow API client
        """
        self.client = client

    def generate_answers(self, questions: List[Question]) -> List[Optional[str]]:
        """Generate answers for questions that don't have answers.

        Args:
            questions: List of Question objects

        Returns:
            List of generated answers (parallel to questions list, None for questions that already have answers)
        """
        # Find questions without answers
        questions_to_generate = []
        indices_to_generate = []

        for i, q in enumerate(questions):
            if not q.answer:
                questions_to_generate.append(q)
                indices_to_generate.append(i)

        if not questions_to_generate:
            # All questions already have answers
            return [q.answer for q in questions]

        # Generate prompt
        user_prompt = self._build_prompt(questions_to_generate, indices_to_generate)

        # Call LLM
        response = self.client.process_text(
            prompt=user_prompt,
            system_prompt=ANSWER_GENERATOR_SYSTEM_PROMPT
        )

        # Parse response
        generated_answers = self._parse_response(response)

        # Build result list
        result = []
        try:
            generated_map = {item["question_index"]: item["answer"] for item in generated_answers}
        except KeyError as e:
            # If we still get a KeyError here, it means validation didn't work
            raise ValueError(f"LLM返回的答案格式不正确，缺少必需字段: {str(e)}")

        for i, q in enumerate(questions):
            if i in generated_map:
                result.append(generated_map[i])
            else:
                result.append(q.answer)

        return result

    def _build_prompt(self, questions: List[Question], indices: List[int]) -> str:
        """Build prompt for answer generation.

        Args:
            questions: Questions to generate answers for
            indices: Original indices of questions

        Returns:
            Formatted prompt
        """
        prompt_parts = ["请为以下面试问题生成专业的答案：\n"]

        for original_idx, q in zip(indices, questions):
            tags_str = ", ".join(q.tags) if q.tags else "无标签"
            prompt_parts.append(
                f"\n{original_idx}. {q.question}\n"
                f"   标签: {tags_str}\n"
            )

        return "".join(prompt_parts)

    def _parse_response(self, response: str) -> List[Dict[str, Any]]:
        """Parse LLM response.

        Args:
            response: LLM response string

        Returns:
            List of answer objects

        Raises:
            ValueError: If response cannot be parsed
        """
        # Remove markdown code blocks
        response = response.strip()
        if response.startswith("```json"):
            response = response[7:]
        if response.startswith("```"):
            response = response[3:]
        if response.endswith("```"):
            response = response[:-3]
        response = response.strip()

        try:
            data = json.loads(response)
            answers = data.get("answers", [])

            # Validate that each answer has required fields
            validated_answers = []
            for item in answers:
                if not isinstance(item, dict):
                    continue
                if "question_index" not in item or "answer" not in item:
                    # Skip malformed items
                    continue
                validated_answers.append(item)

            return validated_answers
        except json.JSONDecodeError as e:
            raise ValueError(f"LLM返回的答案不是有效JSON格式: {str(e)}")
