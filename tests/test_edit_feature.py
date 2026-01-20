"""
Test the edit/update functionality for interview experiences.

This test verifies:
1. Creating a new experience
2. Updating various fields
3. Updating questions
4. Adding/removing tags
"""

import requests
import json
from datetime import datetime

# API Base URL
API_BASE = "http://localhost:8000/api"


def test_update_experience():
    """Test updating an interview experience."""

    print("=" * 60)
    print("Testing Interview Experience Update Functionality")
    print("=" * 60)

    # Step 1: Create a test experience
    print("\n1. Creating a test experience...")

    test_content = """
    面试公司：测试科技有限公司
    职位：Python 后端工程师
    面试阶段：一面

    面试问题：
    1. 请介绍一下 Python 的 GIL
    答：GIL（全局解释器锁）是 Python 中的一个互斥锁...

    2. 什么是装饰器？
    答：装饰器是一个可以修改函数或类行为的函数...
    """

    create_response = requests.post(
        f"{API_BASE}/process/text",
        json={
            "content": test_content,
            "generate_answers": False,
            "export_format": "json"
        }
    )

    if create_response.status_code != 200:
        print(f"❌ Failed to create experience: {create_response.text}")
        return

    result = create_response.json()
    if not result["success"]:
        print(f"❌ Processing failed: {result.get('error')}")
        return

    experience_id = result["experience_id"]
    print(f"✅ Created experience with ID: {experience_id}")

    # Step 2: Test updating company info
    print("\n2. Testing company info update...")

    update_data = {
        "company_name": "更新后的科技公司",
        "company_scale": "大厂",
        "position": "高级Python工程师",
        "interview_stage": "二面"
    }

    update_response = requests.put(
        f"{API_BASE}/experiences/{experience_id}",
        json=update_data
    )

    if update_response.status_code != 200:
        print(f"❌ Failed to update: {update_response.text}")
        return

    updated = update_response.json()
    if updated["success"]:
        exp = updated["experience"]
        print(f"✅ Company name updated: {exp['company_name']}")
        print(f"✅ Company scale updated: {exp['company_scale']}")
        print(f"✅ Position updated: {exp['position']}")
        print(f"✅ Interview stage updated: {exp['interview_stage']}")
    else:
        print("❌ Update failed")
        return

    # Step 3: Test updating interview experience
    print("\n3. Testing interview experience update...")

    update_data = {
        "interview_experience": "面试体验很好，面试官很专业，问题有深度。整体氛围轻松愉快。"
    }

    update_response = requests.put(
        f"{API_BASE}/experiences/{experience_id}",
        json=update_data
    )

    if update_response.status_code == 200 and update_response.json()["success"]:
        print(f"✅ Interview experience updated")
    else:
        print("❌ Failed to update interview experience")
        return

    # Step 4: Test updating tags
    print("\n4. Testing tags update...")

    update_data = {
        "tags": ["Python", "后端", "GIL", "装饰器", "高并发", "数据库优化"]
    }

    update_response = requests.put(
        f"{API_BASE}/experiences/{experience_id}",
        json=update_data
    )

    if update_response.status_code == 200:
        result = update_response.json()
        if result["success"]:
            tags = result["experience"]["tags"]
            print(f"✅ Tags updated: {', '.join(tags)}")
        else:
            print("❌ Failed to update tags")
            return
    else:
        print(f"❌ Request failed: {update_response.text}")
        return

    # Step 5: Test updating questions
    print("\n5. Testing questions update...")

    # Get current experience to get question IDs
    get_response = requests.get(f"{API_BASE}/experiences/{experience_id}")
    current_exp = get_response.json()["experience"]
    questions = current_exp["questions"]

    # Update first question's answer
    if len(questions) > 0:
        questions[0]["answer"] = "更新后的答案：GIL（全局解释器锁）确保同一时刻只有一个线程在执行Python字节码。这简化了CPython的实现，但在多核系统上限制了并行性能。"

    # Add a new question
    questions.append({
        "id": f"q-{int(datetime.now().timestamp())}",
        "question": "描述一下 Python 的内存管理机制",
        "answer": "Python使用引用计数和垃圾回收机制。引用计数追踪对象的引用次数，当计数为0时释放内存。垃圾回收器用于处理循环引用。",
        "has_original_answer": False,
        "tags": ["Python", "内存管理"]
    })

    update_data = {
        "questions": questions
    }

    update_response = requests.put(
        f"{API_BASE}/experiences/{experience_id}",
        json=update_data
    )

    if update_response.status_code == 200:
        result = update_response.json()
        if result["success"]:
            updated_questions = result["experience"]["questions"]
            print(f"✅ Questions updated. Total questions: {len(updated_questions)}")
            print(f"   - Updated answer for question 1")
            print(f"   - Added new question about memory management")
        else:
            print("❌ Failed to update questions")
            return
    else:
        print(f"❌ Request failed: {update_response.text}")
        return

    # Step 6: Verify final state
    print("\n6. Verifying final state...")

    get_response = requests.get(f"{API_BASE}/experiences/{experience_id}")
    if get_response.status_code == 200:
        final_exp = get_response.json()["experience"]
        print("\n" + "=" * 60)
        print("FINAL EXPERIENCE STATE")
        print("=" * 60)
        print(f"Company: {final_exp['company_name']} ({final_exp['company_scale']})")
        print(f"Position: {final_exp['position']}")
        print(f"Stage: {final_exp['interview_stage']}")
        print(f"Tags: {', '.join(final_exp['tags'])}")
        print(f"Questions: {len(final_exp['questions'])}")
        print(f"Interview Experience: {final_exp.get('interview_experience', 'N/A')[:50]}...")
        print("=" * 60)
        print("\n✅ All tests passed successfully!")
    else:
        print("❌ Failed to retrieve final state")
        return

    # Step 7: Cleanup (optional)
    print("\n7. Cleaning up test data...")
    delete_response = requests.delete(f"{API_BASE}/experiences/{experience_id}")
    if delete_response.status_code == 200:
        print(f"✅ Test experience deleted")
    else:
        print(f"⚠️  Failed to delete test experience (ID: {experience_id})")

    print("\n" + "=" * 60)
    print("Test completed!")
    print("=" * 60)


if __name__ == "__main__":
    try:
        test_update_experience()
    except requests.exceptions.ConnectionError:
        print("❌ Error: Cannot connect to API server at http://localhost:8000")
        print("   Please make sure the backend server is running:")
        print("   cd src/api && python app.py")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
