"""Test script for content validator."""

from src.validators.content_validator import validate_content


def test_validation():
    """Test content validation with various inputs."""

    test_cases = [
        # 有效的面经内容
        {
            "content": """字节跳动 大模型算法工程师 一面
1. 介绍一下Transformer的注意力机制
2. 讲讲LoRA微调的原理
3. 算法题：LeetCode 146 LRU缓存""",
            "expected": True,
        },
        {
            "content": """腾讯二面面经
面试官问了：
1. Redis的持久化方式有哪些？
2. MySQL的索引优化
3. 手撕代码：实现一个线程安全的单例模式""",
            "expected": True,
        },
        # 无效的内容
        {
            "content": "你好",
            "expected": False,
        },
        {
            "content": "测试一下",
            "expected": False,
        },
        {
            "content": "123456",
            "expected": False,
        },
        # 边界情况
        {
            "content": """请问如何准备算法面试？""",
            "expected": False,
        },
        {
            "content": """公司：阿里巴巴
职位：Java开发工程师
一面面试题目：
1. HashMap的底层实现
2. JVM垃圾回收机制
3. Spring AOP的原理
4. 设计一个秒杀系统
面试体验：⭐⭐⭐⭐⭐""",
            "expected": True,
        },
    ]

    print("=" * 80)
    print("内容验证测试")
    print("=" * 80)

    for i, test_case in enumerate(test_cases, 1):
        content = test_case["content"]
        expected = test_case["expected"]

        is_valid, score, message = validate_content(content)

        status = "[PASS]" if is_valid == expected else "[FAIL]"
        print(f"\n测试用例 {i}: {status}")
        print(f"内容预览: {content[:50]}...")
        print(f"验证结果: {'通过' if is_valid else '未通过'}")
        print(f"置信度分数: {score}/100")
        print(f"提示信息: {message}")

        if is_valid != expected:
            print(f"[WARNING] 预期 {'通过' if expected else '未通过'}，实际 {'通过' if is_valid else '未通过'}")

    print("\n" + "=" * 80)


if __name__ == "__main__":
    test_validation()
