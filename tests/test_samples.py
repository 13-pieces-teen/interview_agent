"""Example test cases for the Interview Agent."""

# Sample interview experience text - Case 1: Questions only (no answers)
SAMPLE_CASE_1 = """
1. 介绍一下lora
2. 除了lora你还知道哪些大模型微调方法？
3. 你能不能介绍一下transformer？
4. 什么是attention机制？
5. PPO和GRPO有什么区别？
"""

# Sample interview experience text - Case 2: With simple answers
SAMPLE_CASE_2 = """
阿里巴巴 AI Agent应用开发 二面

1. 介绍一下你的实习项目
答: 我在实习期间主要负责开发基于大模型的RAG系统，使用向量数据库进行文档检索...

2. RAG系统的核心组件有哪些？
答: 主要包括文档加载、文本分割、Embedding生成、向量存储、检索和生成

3. Agent架构设计
答: 包括Profile模块、Memory模块、Planning模块和Action模块

4. 手撕算法：最长公共子序列
"""

# Sample interview experience text - Case 3: Complex structured content
SAMPLE_CASE_3 = """
新鲜面经——字节跳动 大模型算法工程师 三面

面试体验：⭐⭐⭐⭐⭐（面试官很专业）

流程：
自我介绍
项目深挖
技术细节
算法题
反问环节

技术问题：
1. 介绍一下LoRA的原理
答: LoRA通过在预训练模型的权重矩阵旁边添加低秩矩阵来实现高效微调...

2. 为什么LoRA可以减少参数量？
答: 因为低秩分解，r << d，所以参数量从d*d降到d*r*2

3. 你在项目中用过哪些Prompt Engineering技巧？

4. 介绍一下你做的Agent系统

手撕算法：
岛屿数量（LeetCode 200）

反问：
团队规模、技术栈等
"""

# Sample interview experience text - Case 4: Simple list with company info
SAMPLE_CASE_4 = """
腾讯 WXG 大模型方向 一面

1. 自我介绍
2. transformer原理
3. 多头注意力机制
4. FFN的作用
5. 残差连接和层归一化
6. BERT和GPT的区别
7. 预训练和微调的区别
8. 介绍你的项目
9. RAG系统的优化方法
10. 算法题：合并两个有序链表
"""


if __name__ == "__main__":
    print("Sample test cases loaded.")
    print("\nCase 1 - Questions only:")
    print(SAMPLE_CASE_1)
    print("\nCase 2 - With simple answers:")
    print(SAMPLE_CASE_2)
    print("\nCase 3 - Complex structured:")
    print(SAMPLE_CASE_3)
    print("\nCase 4 - Simple list:")
    print(SAMPLE_CASE_4)
