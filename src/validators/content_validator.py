"""Content validator for checking if input is interview-related."""

import re
from typing import Tuple


class ContentValidator:
    """Validator for checking if content is interview experience related."""

    # 面经相关关键词
    INTERVIEW_KEYWORDS = {
        # 公司相关
        "公司", "大厂", "中厂", "小厂", "初创", "企业", "字节", "腾讯", "阿里", "百度",
        "美团", "拼多多", "京东", "华为", "小米",

        # 面试相关
        "面试", "一面", "二面", "三面", "终面", "HR面", "技术面", "电话面", "视频面",
        "面经", "笔试", "offer", "挂了", "通过", "过了",

        # 职位相关
        "后端", "前端", "算法", "开发", "工程师", "实习", "校招", "社招", "岗位",
        "职位", "Java", "Python", "C++", "Go", "前端", "全栈",

        # 问题相关
        "问题", "题目", "算法题", "手撕", "项目", "场景", "设计", "八股",
        "问：", "答：", "Q:", "A:", "问了", "答了", "回答",

        # 技术关键词
        "数据结构", "算法", "LeetCode", "力扣", "Redis", "MySQL", "数据库",
        "分布式", "微服务", "并发", "多线程", "网络", "操作系统",
        "Transformer", "大模型", "机器学习", "深度学习", "RAG", "Agent",
    }

    # 问答结构模式
    QA_PATTERNS = [
        r'问[：:]\s*',
        r'答[：:]\s*',
        r'Q[：:]\s*',
        r'A[：:]\s*',
        r'\d+[\.\、]\s*.{3,}',  # 编号列表
        r'[（(]\d+[）)]\s*.{3,}',  # (1) 这种格式
    ]

    # 负面关键词（明显不是面经的内容）
    NEGATIVE_KEYWORDS = {
        "测试", "test", "hello", "你好", "帮我", "请问",
        "怎么", "如何", "能否", "可以吗",
    }

    def __init__(self):
        """Initialize the validator."""
        pass

    def validate(self, content: str) -> Tuple[bool, int, str]:
        """Validate if content is likely interview experience related.

        Args:
            content: Input content to validate

        Returns:
            Tuple of (is_valid, confidence_score, message)
            - is_valid: True if content passes validation
            - confidence_score: 0-100 score indicating confidence
            - message: Validation message or suggestion
        """
        if not content or not isinstance(content, str):
            return False, 0, "输入内容为空"

        content = content.strip()

        # 1. 基础验证
        basic_valid, basic_score, basic_msg = self._validate_basic(content)
        if not basic_valid:
            return False, basic_score, basic_msg

        # 2. 关键词匹配
        keyword_score = self._calculate_keyword_score(content)

        # 3. 结构检测
        structure_score = self._calculate_structure_score(content)

        # 4. 负面检测
        negative_score = self._calculate_negative_score(content)

        # 综合评分
        total_score = int(
            basic_score * 0.2 +
            keyword_score * 0.5 +
            structure_score * 0.3 -
            negative_score * 0.3
        )
        total_score = max(0, min(100, total_score))

        # 判断是否通过
        threshold = 30  # 阈值设为30分
        is_valid = total_score >= threshold

        if is_valid:
            if total_score >= 70:
                message = "内容看起来是面经相关，可以处理"
            elif total_score >= 50:
                message = "内容可能是面经相关，建议确认"
            else:
                message = "内容勉强通过验证，建议检查"
        else:
            message = self._generate_suggestion(content, keyword_score, structure_score)

        return is_valid, total_score, message

    def _validate_basic(self, content: str) -> Tuple[bool, int, str]:
        """Basic validation checks.

        Args:
            content: Input content

        Returns:
            Tuple of (is_valid, score, message)
        """
        # 长度检查
        if len(content) < 10:
            return False, 0, "输入内容过短（少于10个字符），请提供完整的面经内容"

        # 检查是否全是数字或符号
        if re.match(r'^[\d\s\.\,\!\?\-_=+@#$%^&*()]+$', content):
            return False, 0, "输入内容无效（仅包含数字和符号）"

        # 检查是否有中文或英文字母
        has_text = bool(re.search(r'[\u4e00-\u9fa5a-zA-Z]', content))
        if not has_text:
            return False, 0, "输入内容无效（没有检测到文字）"

        # 基础分数根据长度给分
        if len(content) >= 200:
            score = 100
        elif len(content) >= 100:
            score = 80
        elif len(content) >= 50:
            score = 60
        else:
            score = 40

        return True, score, "基础验证通过"

    def _calculate_keyword_score(self, content: str) -> int:
        """Calculate score based on keyword matching.

        Args:
            content: Input content

        Returns:
            Score from 0-100
        """
        matched_keywords = 0
        content_lower = content.lower()

        for keyword in self.INTERVIEW_KEYWORDS:
            if keyword.lower() in content_lower:
                matched_keywords += 1

        # 根据匹配的关键词数量计算分数
        # 匹配3个以上关键词就给高分
        if matched_keywords >= 5:
            return 100
        elif matched_keywords >= 3:
            return 80
        elif matched_keywords >= 2:
            return 60
        elif matched_keywords >= 1:
            return 40
        else:
            return 0

    def _calculate_structure_score(self, content: str) -> int:
        """Calculate score based on structure patterns.

        Args:
            content: Input content

        Returns:
            Score from 0-100
        """
        matched_patterns = 0

        for pattern in self.QA_PATTERNS:
            if re.search(pattern, content):
                matched_patterns += 1

        # 有问答结构或列表结构得高分
        if matched_patterns >= 3:
            return 100
        elif matched_patterns >= 2:
            return 80
        elif matched_patterns >= 1:
            return 60
        else:
            # 检查是否有换行符（可能是结构化的文本）
            if '\n' in content and content.count('\n') >= 3:
                return 40
            return 20

    def _calculate_negative_score(self, content: str) -> int:
        """Calculate negative score based on negative keywords.

        Args:
            content: Input content

        Returns:
            Penalty score from 0-100
        """
        content_lower = content.lower()
        matched_negative = 0

        for keyword in self.NEGATIVE_KEYWORDS:
            if keyword.lower() in content_lower:
                matched_negative += 1

        # 如果内容很短且包含负面关键词，惩罚更重
        if len(content) < 50 and matched_negative > 0:
            return matched_negative * 30

        return matched_negative * 10

    def _generate_suggestion(
        self, content: str, keyword_score: int, structure_score: int
    ) -> str:
        """Generate helpful suggestion message.

        Args:
            content: Input content
            keyword_score: Keyword matching score
            structure_score: Structure matching score

        Returns:
            Suggestion message
        """
        suggestions = ["输入内容似乎不是面经相关。"]

        if keyword_score < 40:
            suggestions.append(
                "建议包含面试相关信息，如：公司名称、面试轮次、技术问题等。"
            )

        if structure_score < 40:
            suggestions.append(
                "建议使用清晰的结构，如：1. 问题描述 2. 解答思路 等。"
            )

        if len(content) < 50:
            suggestions.append(
                "内容较短，建议提供更详细的面试经历或问题描述。"
            )

        return " ".join(suggestions)


# 全局实例
validator = ContentValidator()


def validate_content(content: str) -> Tuple[bool, int, str]:
    """Validate content using global validator instance.

    Args:
        content: Input content to validate

    Returns:
        Tuple of (is_valid, confidence_score, message)
    """
    return validator.validate(content)
