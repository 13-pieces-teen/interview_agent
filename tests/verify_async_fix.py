"""
快速测试异步任务队列修复
运行此脚本前请确保已重启后端服务
"""

import requests
import time
import sys

BASE_URL = "http://localhost:8000"


def test_health():
    """测试后端健康状态"""
    print("=" * 50)
    print("1. 测试后端健康状态")
    print("=" * 50)

    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✓ 后端服务正常运行")
            return True
        else:
            print(f"✗ 后端返回错误: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ 无法连接到后端: {e}")
        print("\n请先启动后端服务:")
        print("  python -m uvicorn src.api.app:app --reload --port 8000")
        return False


def test_queue_info():
    """测试队列信息API"""
    print("\n" + "=" * 50)
    print("2. 测试队列信息API")
    print("=" * 50)

    try:
        response = requests.get(f"{BASE_URL}/api/tasks/queue/info", timeout=5)
        if response.status_code == 200:
            info = response.json()
            print("✓ 队列信息API正常")
            print(f"  总任务数: {info['total_tasks']}")
            print(f"  排队中: {info['queued']}")
            print(f"  处理中: {info['processing']}")
            print(f"  已完成: {info['completed']}")
            print(f"  失败: {info['failed']}")
            print(f"  队列运行: {'是' if info['is_running'] else '否'}")
            return True
        else:
            print(f"✗ API返回错误: {response.status_code}")
            print(f"  响应: {response.text}")
            return False
    except Exception as e:
        print(f"✗ 请求失败: {e}")
        return False


def test_list_all_tasks():
    """测试获取所有任务列表"""
    print("\n" + "=" * 50)
    print("3. 测试获取所有任务列表（核心修复）")
    print("=" * 50)

    try:
        response = requests.get(f"{BASE_URL}/api/tasks/async", timeout=5)

        if response.status_code == 200:
            data = response.json()
            print("✓ 任务列表API正常")
            print(f"  找到 {data['total']} 个任务")

            if data['total'] > 0:
                print(f"\n  最近的任务:")
                for task in data['tasks'][:3]:
                    print(f"    - ID: {task['id'][:8]}...")
                    print(f"      类型: {task['type']}")
                    print(f"      状态: {task['status']}")
                    print(f"      创建时间: {task['created_at']}")
            return True
        elif response.status_code == 404:
            print("✗ 返回 404 错误 - 路由匹配失败")
            print("  这意味着后端服务可能未重启或使用旧代码")
            print("\n  解决方案:")
            print("  1. 停止当前后端服务 (Ctrl+C)")
            print("  2. 重新启动: python -m uvicorn src.api.app:app --reload --port 8000")
            return False
        else:
            print(f"✗ API返回错误: {response.status_code}")
            print(f"  响应: {response.text}")
            return False
    except Exception as e:
        print(f"✗ 请求失败: {e}")
        return False


def test_list_filtered_tasks():
    """测试按状态过滤任务"""
    print("\n" + "=" * 50)
    print("4. 测试按状态过滤任务")
    print("=" * 50)

    statuses = ["queued", "processing", "completed", "failed"]
    results = {}

    for status in statuses:
        try:
            response = requests.get(
                f"{BASE_URL}/api/tasks/async?status={status}",
                timeout=5
            )

            if response.status_code == 200:
                data = response.json()
                count = data['total']
                results[status] = count
                print(f"  {status:12} : {count} 个任务 ✓")
            elif response.status_code == 404:
                print(f"  {status:12} : 404 错误 ✗ (需要重启后端)")
                return False
            else:
                print(f"  {status:12} : 错误 {response.status_code} ✗")
                return False
        except Exception as e:
            print(f"  {status:12} : 请求失败 ✗ ({e})")
            return False

    print("\n✓ 所有状态过滤测试通过")
    return True


def test_submit_task():
    """测试提交新任务"""
    print("\n" + "=" * 50)
    print("5. 测试提交新任务")
    print("=" * 50)

    try:
        payload = {
            "content": "测试面经：腾讯前端面试，问了Vue和React。公司：腾讯，岗位：前端工程师",
            "generate_answers": False,
            "export_format": "both"
        }

        response = requests.post(
            f"{BASE_URL}/api/process/text/async",
            json=payload,
            timeout=10
        )

        if response.status_code == 200:
            data = response.json()
            task_id = data['task_id']
            print("✓ 任务提交成功")
            print(f"  任务ID: {task_id}")
            print(f"  状态: {data['status']}")
            print(f"  消息: {data['message']}")

            # 等待任务处理
            print("\n  等待任务处理...")
            for i in range(10):
                time.sleep(2)
                status_response = requests.get(
                    f"{BASE_URL}/api/tasks/async/{task_id}",
                    timeout=5
                )

                if status_response.status_code == 200:
                    task = status_response.json()
                    print(f"  [{i+1}] 状态: {task['status']}", end="")

                    if task['status'] == 'completed':
                        print(f" ✓ (耗时: {task['processing_time']:.2f}s)")
                        return True
                    elif task['status'] == 'failed':
                        print(f" ✗ (错误: {task['error']})")
                        return False
                    else:
                        print()

            print("\n  ⚠ 任务处理超时（20秒）")
            return True
        else:
            print(f"✗ 提交失败: {response.status_code}")
            print(f"  响应: {response.text}")
            return False
    except Exception as e:
        print(f"✗ 提交失败: {e}")
        return False


def main():
    print("\n异步任务队列修复验证脚本")
    print("=" * 50)

    results = []

    # 1. 健康检查
    if not test_health():
        print("\n❌ 后端服务未运行，测试终止")
        sys.exit(1)

    # 2. 队列信息
    results.append(("队列信息API", test_queue_info()))

    # 3. 核心修复：任务列表
    results.append(("获取任务列表", test_list_all_tasks()))

    # 4. 状态过滤
    results.append(("状态过滤", test_list_filtered_tasks()))

    # 5. 提交任务（可选）
    print("\n是否要提交测试任务？(y/n): ", end="", flush=True)
    if input().lower() == 'y':
        results.append(("提交任务", test_submit_task()))

    # 汇总结果
    print("\n" + "=" * 50)
    print("测试结果汇总")
    print("=" * 50)

    for name, result in results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"  {name:20} : {status}")

    all_passed = all(result for _, result in results)

    if all_passed:
        print("\n✓ 所有测试通过！异步任务队列已修复")
        print("\n前端任务队列面板现在应该可以正常显示任务了")
        print("请刷新浏览器页面: http://localhost:5173")
    else:
        print("\n✗ 部分测试失败")
        print("\n可能的原因:")
        print("  1. 后端服务未重启（最常见）")
        print("  2. 端口冲突")
        print("  3. 代码未正确保存")
        print("\n解决方案:")
        print("  1. 停止后端服务 (Ctrl+C)")
        print("  2. 重新启动: python -m uvicorn src.api.app:app --reload --port 8000")
        print("  3. 重新运行此测试脚本")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n测试被中断")
        sys.exit(0)
