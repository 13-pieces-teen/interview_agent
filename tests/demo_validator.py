"""Interactive demo for content validator."""

from src.validators.content_validator import validate_content


def print_separator():
    """Print separator line."""
    print("\n" + "=" * 80 + "\n")


def validate_and_display(content: str):
    """Validate content and display results."""
    print(f"输入内容:\n{content}\n")

    is_valid, score, message = validate_content(content)

    print(f"验证结果: {'✅ 通过' if is_valid else '❌ 未通过'}")
    print(f"置信度分数: {score}/100")
    print(f"提示信息: {message}")

    # 显示评分级别
    if score >= 70:
        level = "优秀"
    elif score >= 50:
        level = "良好"
    elif score >= 30:
        level = "及格"
    else:
        level = "不及格"

    print(f"评分级别: {level}")


def main():
    """Main interactive demo."""
    print_separator()
    print("📝 面经内容验证器 - 交互式演示")
    print_separator()

    # 示例1：典型的面经内容
    print("示例 1: 典型面经内容")
    print_separator()
    validate_and_display("""字节跳动 大模型算法工程师 一面

面试时间：2024年3月
面试形式：视频面试

技术问题：
1. 介绍一下Transformer的注意力机制原理
2. LoRA微调的核心思想是什么？
3. 如何评估大模型的性能？
4. RAG系统中如何选择合适的Embedding模型？

算法题：
LeetCode 146 - LRU缓存机制

面试体验：⭐⭐⭐⭐""")

    # 示例2：简短的面经片段
    print_separator()
    print("示例 2: 简短面经片段")
    print_separator()
    validate_and_display("""腾讯二面
问了Redis持久化和MySQL索引优化""")

    # 示例3：非面经内容
    print_separator()
    print("示例 3: 非面经内容")
    print_separator()
    validate_and_display("请问如何准备算法面试？")

    # 示例4：无效输入
    print_separator()
    print("示例 4: 无效输入")
    print_separator()
    validate_and_display("测试一下")

    # 交互模式
    print_separator()
    print("🎮 交互模式")
    print("输入您的面经内容进行验证（输入 'quit' 退出）")
    print_separator()

    while True:
        try:
            user_input = input("\n请输入面经内容: ").strip()

            if user_input.lower() in ['quit', 'exit', 'q']:
                print("\n再见！")
                break

            if not user_input:
                print("输入为空，请重新输入")
                continue

            print_separator()
            validate_and_display(user_input)
            print_separator()

        except KeyboardInterrupt:
            print("\n\n程序已终止")
            break
        except Exception as e:
            print(f"\n错误: {e}")


if __name__ == "__main__":
    main()
