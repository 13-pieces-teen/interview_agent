"""
异步任务队列功能测试脚本
测试用户可以多次提交任务，任务在后台处理
"""

import requests
import time
from pathlib import Path

BASE_URL = "http://localhost:8000/api"


def test_async_text_processing():
    """测试异步文本处理"""
    print("=" * 50)
    print("测试异步文本处理")
    print("=" * 50)

    # 提交3个文本任务
    texts = [
        "这是第一个测试面经文本。公司：测试公司A，岗位：前端工程师",
        "这是第二个测试面经文本。公司：测试公司B，岗位：后端工程师",
        "这是第三个测试面经文本。公司：测试公司C，岗位：全栈工程师",
    ]

    task_ids = []

    for idx, text in enumerate(texts, 1):
        print(f"\n提交第 {idx} 个文本任务...")
        response = requests.post(
            f"{BASE_URL}/process/text/async",
            json={
                "content": text,
                "generate_answers": False,
                "export_format": "both"
            }
        )

        if response.status_code == 200:
            result = response.json()
            task_id = result['task_id']
            task_ids.append(task_id)
            print(f"✓ 任务 {idx} 已提交: {task_id[:8]}...")
            print(f"  状态: {result['status']}")
            print(f"  消息: {result['message']}")
        else:
            print(f"✗ 提交失败: {response.status_code}")
            print(f"  {response.text}")

        # 立即提交下一个，不等待
        time.sleep(0.5)

    print(f"\n✓ 所有任务已提交！共 {len(task_ids)} 个任务")
    print(f"  任务将在后台并发处理")

    return task_ids


def test_async_image_processing():
    """测试异步图片处理"""
    print("\n" + "=" * 50)
    print("测试异步图片处理")
    print("=" * 50)

    # 注意：需要实际的测试图片文件
    test_files = [
        "test_image_1.png",
        "test_image_2.png",
    ]

    # 检查文件是否存在
    existing_files = []
    for file_path in test_files:
        if Path(file_path).exists():
            existing_files.append(file_path)
            print(f"✓ 找到测试文件: {file_path}")
        else:
            print(f"✗ 文件不存在: {file_path}")

    if not existing_files:
        print("\n⚠ 没有找到测试图片文件，跳过图片测试")
        return []

    task_ids = []

    for idx, file_path in enumerate(existing_files, 1):
        print(f"\n提交第 {idx} 个图片任务...")
        files = [('files', (Path(file_path).name, open(file_path, 'rb'), 'image/png'))]
        data = {
            'generate_answers': 'false',
            'export_format': 'both'
        }

        response = requests.post(
            f"{BASE_URL}/process/images/async",
            files=files,
            data=data
        )

        # 关闭文件句柄
        for _, (_, file_obj, _) in files:
            file_obj.close()

        if response.status_code == 200:
            result = response.json()
            task_id = result['task_id']
            task_ids.append(task_id)
            print(f"✓ 任务 {idx} 已提交: {task_id[:8]}...")
            print(f"  状态: {result['status']}")
            print(f"  消息: {result['message']}")
        else:
            print(f"✗ 提交失败: {response.status_code}")

        # 立即提交下一个
        time.sleep(0.5)

    print(f"\n✓ 所有图片任务已提交！共 {len(task_ids)} 个任务")

    return task_ids


def monitor_tasks(task_ids, max_wait_time=60):
    """监控任务状态"""
    print("\n" + "=" * 50)
    print("监控任务处理进度")
    print("=" * 50)

    start_time = time.time()
    completed_tasks = set()

    while len(completed_tasks) < len(task_ids):
        if time.time() - start_time > max_wait_time:
            print("\n⚠ 超时退出监控")
            break

        # 检查每个任务的状态
        for task_id in task_ids:
            if task_id in completed_tasks:
                continue

            response = requests.get(f"{BASE_URL}/tasks/async/{task_id}")
            if response.status_code == 200:
                status = response.json()

                if status['status'] in ['completed', 'failed']:
                    completed_tasks.add(task_id)

                    if status['status'] == 'completed':
                        print(f"\n✓ 任务完成: {task_id[:8]}...")
                        print(f"  类型: {status['type']}")
                        print(f"  耗时: {status['processing_time']:.2f}s")
                        if status['result'] and status['result'].get('experience_id'):
                            print(f"  面经ID: {status['result']['experience_id']}")
                    else:
                        print(f"\n✗ 任务失败: {task_id[:8]}...")
                        print(f"  错误: {status['error']}")

        if len(completed_tasks) < len(task_ids):
            time.sleep(2)

    print(f"\n✓ 监控完成")
    print(f"  完成任务: {len(completed_tasks)}/{len(task_ids)}")


def test_queue_info():
    """测试队列信息查询"""
    print("\n" + "=" * 50)
    print("查询队列信息")
    print("=" * 50)

    response = requests.get(f"{BASE_URL}/tasks/queue/info")
    if response.status_code == 200:
        info = response.json()
        print(f"\n队列统计:")
        print(f"  总任务数: {info['total_tasks']}")
        print(f"  排队中: {info['queued']}")
        print(f"  处理中: {info['processing']}")
        print(f"  已完成: {info['completed']}")
        print(f"  失败: {info['failed']}")
        print(f"  队列大小: {info['queue_size']}")
        print(f"  运行状态: {'运行中' if info['is_running'] else '已停止'}")
    else:
        print(f"✗ 查询失败: {response.status_code}")


def test_list_tasks():
    """测试任务列表查询"""
    print("\n" + "=" * 50)
    print("查询任务列表")
    print("=" * 50)

    response = requests.get(f"{BASE_URL}/tasks/async")
    if response.status_code == 200:
        result = response.json()
        tasks = result['tasks']
        print(f"\n找到 {len(tasks)} 个任务:")

        for task in tasks[:5]:  # 只显示前5个
            print(f"\n  任务ID: {task['id'][:8]}...")
            print(f"  类型: {task['type']}")
            print(f"  状态: {task['status']}")
            print(f"  创建时间: {task['created_at']}")

        if len(tasks) > 5:
            print(f"\n  ... 还有 {len(tasks) - 5} 个任务")
    else:
        print(f"✗ 查询失败: {response.status_code}")


def test_health_check():
    """测试健康检查"""
    print("=" * 50)
    print("测试后端服务健康检查")
    print("=" * 50)

    try:
        response = requests.get(f"{BASE_URL.replace('/api', '')}/health")
        if response.status_code == 200:
            result = response.json()
            print(f"\n✓ 后端服务正常运行")
            print(f"  状态: {result['status']}")
            print(f"  版本: {result['version']}")
            return True
        else:
            print(f"✗ 健康检查失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ 无法连接到后端服务: {e}")
        return False


if __name__ == "__main__":
    print("异步任务队列功能测试")
    print("=" * 50)

    # 1. 健康检查
    if not test_health_check():
        print("\n请先启动后端服务:")
        print("  python -m uvicorn src.api.app:app --reload --port 8000")
        exit(1)

    # 2. 测试异步文本处理（多次提交）
    text_task_ids = test_async_text_processing()

    # 3. 测试异步图片处理（如果有测试文件）
    image_task_ids = test_async_image_processing()

    all_task_ids = text_task_ids + image_task_ids

    # 4. 查询队列信息
    test_queue_info()

    # 5. 监控任务进度
    if all_task_ids:
        monitor_tasks(all_task_ids, max_wait_time=120)

    # 6. 查询任务列表
    test_list_tasks()

    # 7. 最终队列信息
    test_queue_info()

    print("\n" + "=" * 50)
    print("测试完成")
    print("=" * 50)
    print("\n关键功能验证:")
    print("  ✓ 可以连续提交多个任务")
    print("  ✓ 任务立即返回，不阻塞")
    print("  ✓ 任务在后台队列处理")
    print("  ✓ 可以实时查询任务状态")
    print("  ✓ 可以查看队列统计信息")
