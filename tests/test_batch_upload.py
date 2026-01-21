"""
批量上传功能测试脚本
测试批量处理API和任务队列管理器
"""

import requests
import time
from pathlib import Path

# API base URL
BASE_URL = "http://localhost:8000/api"


def test_batch_upload():
    """测试批量上传功能"""
    print("=" * 50)
    print("批量上传功能测试")
    print("=" * 50)

    # 1. 准备测试文件（使用示例图片路径）
    # 注意：这里需要替换成实际存在的图片文件路径
    test_files = [
        "test_image_1.png",
        "test_image_2.png",
        "test_image_3.png",
    ]

    print(f"\n准备上传 {len(test_files)} 个文件...")
    print("注意：请确保测试图片文件存在！")

    # 2. 检查文件是否存在
    existing_files = []
    for file_path in test_files:
        if Path(file_path).exists():
            existing_files.append(file_path)
            print(f"✓ 找到文件: {file_path}")
        else:
            print(f"✗ 文件不存在: {file_path}")

    if not existing_files:
        print("\n❌ 没有找到测试文件，跳过测试")
        print("提示：请在项目根目录下放置测试图片文件")
        return

    # 3. 创建批量处理任务
    print(f"\n创建批量处理任务...")
    files = []
    for file_path in existing_files:
        files.append(
            ('files', (Path(file_path).name, open(file_path, 'rb'), 'image/png'))
        )

    data = {
        'generate_answers': 'false',
        'export_format': 'both'
    }

    try:
        response = requests.post(
            f"{BASE_URL}/process/batch",
            files=files,
            data=data,
            timeout=30
        )

        # 关闭文件句柄
        for _, (_, file_obj, _) in files:
            file_obj.close()

        if response.status_code == 200:
            result = response.json()
            task_id = result['task_id']
            print(f"✓ 批量任务创建成功")
            print(f"  任务ID: {task_id}")
            print(f"  文件总数: {result['total_files']}")
            print(f"  状态: {result['status']}")

            # 4. 轮询任务状态
            print(f"\n监控任务进度...")
            poll_count = 0
            max_polls = 60  # 最多轮询60次（2分钟）

            while poll_count < max_polls:
                time.sleep(2)  # 每2秒轮询一次
                poll_count += 1

                status_response = requests.get(f"{BASE_URL}/batch/{task_id}")
                if status_response.status_code == 200:
                    status = status_response.json()

                    print(f"\r进度: {status['completed_count'] + status['failed_count']}/{status['total_files']} "
                          f"| 完成: {status['completed_count']} | 失败: {status['failed_count']} "
                          f"| 状态: {status['status']}", end='')

                    # 检查是否完成
                    if status['status'] in ['completed', 'failed', 'cancelled']:
                        print("\n")
                        print(f"\n任务 {status['status'].upper()}!")

                        # 显示子任务详情
                        print("\n子任务详情:")
                        for idx, sub_task in enumerate(status['sub_tasks'], 1):
                            status_icon = {
                                'completed': '✓',
                                'failed': '✗',
                                'processing': '⊙',
                                'pending': '○'
                            }.get(sub_task['status'], '?')

                            print(f"  {status_icon} [{idx}] {sub_task['file_name']}: {sub_task['status']}")
                            if sub_task['error']:
                                print(f"      错误: {sub_task['error']}")
                            if sub_task['experience_id']:
                                print(f"      面经ID: {sub_task['experience_id']}")
                            if sub_task['processing_time'] > 0:
                                print(f"      耗时: {sub_task['processing_time']:.2f}s")

                        # 测试成功
                        if status['status'] == 'completed':
                            print(f"\n✓ 批量处理测试通过！")
                            print(f"  成功处理: {status['completed_count']} 个文件")
                            if status['failed_count'] > 0:
                                print(f"  失败: {status['failed_count']} 个文件")
                        break
                else:
                    print(f"\n❌ 获取任务状态失败: {status_response.status_code}")
                    break

            if poll_count >= max_polls:
                print(f"\n⚠ 轮询超时，任务可能仍在处理中")

        else:
            print(f"❌ 创建批量任务失败: {response.status_code}")
            print(f"响应: {response.text}")

    except requests.exceptions.ConnectionError:
        print(f"\n❌ 无法连接到后端服务")
        print(f"请确保后端服务运行在 {BASE_URL}")
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()


def test_list_batch_tasks():
    """测试获取批量任务列表"""
    print("\n" + "=" * 50)
    print("测试获取批量任务列表")
    print("=" * 50)

    try:
        response = requests.get(f"{BASE_URL}/batch")
        if response.status_code == 200:
            result = response.json()
            tasks = result['tasks']
            print(f"\n找到 {len(tasks)} 个批量任务:")

            for task in tasks:
                print(f"\n任务ID: {task['id']}")
                print(f"  状态: {task['status']}")
                print(f"  文件总数: {task['total_files']}")
                print(f"  已完成: {task['completed_count']}")
                print(f"  失败: {task['failed_count']}")
                print(f"  创建时间: {task['created_at']}")

            print(f"\n✓ 获取任务列表成功")
        else:
            print(f"❌ 获取任务列表失败: {response.status_code}")

    except Exception as e:
        print(f"❌ 测试失败: {e}")


def test_health_check():
    """测试健康检查"""
    print("\n" + "=" * 50)
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
            print(f"❌ 健康检查失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 无法连接到后端服务: {e}")
        return False


if __name__ == "__main__":
    print("批量上传功能测试脚本")
    print("=" * 50)

    # 1. 健康检查
    if not test_health_check():
        print("\n请先启动后端服务:")
        print("  python -m src.api.app")
        exit(1)

    # 2. 测试批量上传
    test_batch_upload()

    # 3. 测试获取任务列表
    test_list_batch_tasks()

    print("\n" + "=" * 50)
    print("测试完成")
    print("=" * 50)
