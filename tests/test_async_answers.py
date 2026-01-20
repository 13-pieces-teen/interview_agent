"""Test async answer generation API."""

import requests
import time
import sys

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Step 1: Process a text interview (without answers in the original text)
print("Step 1: Processing interview experience...")
print("-" * 60)

test_data = {
    "content": "我面试了阿里巴巴的AI算法工程师岗位，二面。面试官问了：1. 什么是Transformer？2. 解释注意力机制的原理。3. 如何优化大模型推理速度？",
    "export_format": "json"
}

response = requests.post(
    "http://localhost:8000/api/process/text",
    json=test_data,
    timeout=120  # Increased timeout
)

if response.status_code != 200:
    print(f"Error: {response.status_code}")
    print(response.text)
    exit(1)

result = response.json()
print(f"✓ Processing successful!")
print(f"  Experience ID: {result['experience_id']}")
print(f"  Processing time: {result['processing_time']:.2f}s")
print(f"  Questions extracted: {len(result['experience']['questions'])}")

# Check that answers are None
for i, q in enumerate(result['experience']['questions'], 1):
    print(f"  {i}. {q['question']}")
    print(f"     Answer: {q.get('answer', 'None')}")

experience_id = result['experience_id']

# Step 2: Start async answer generation
print("\n" + "=" * 60)
print("Step 2: Starting async answer generation...")
print("-" * 60)

response = requests.post(
    f"http://localhost:8000/api/experiences/{experience_id}/generate-answers",
    timeout=5
)

if response.status_code != 200:
    print(f"Error: {response.status_code}")
    print(response.text)
    exit(1)

gen_result = response.json()
print(f"✓ Answer generation started!")
print(f"  Task ID: {gen_result['task_id']}")
print(f"  Status: {gen_result['status']}")
print(f"  Total questions: {gen_result['total_questions']}")

task_id = gen_result['task_id']

# Step 3: Poll task status
print("\n" + "=" * 60)
print("Step 3: Polling task status...")
print("-" * 60)

max_wait = 120  # 2 minutes max
start_time = time.time()

while time.time() - start_time < max_wait:
    response = requests.get(
        f"http://localhost:8000/api/tasks/{task_id}",
        timeout=5
    )

    if response.status_code != 200:
        print(f"Error: {response.status_code}")
        print(response.text)
        break

    status = response.json()
    elapsed = time.time() - start_time

    if status['status'] == 'completed':
        print(f"\n✓ Answer generation completed!")
        print(f"  Total time: {elapsed:.2f}s")
        print(f"  Questions with generated answers: {status['progress']}/{status['total_questions']}")
        break
    elif status['status'] == 'failed':
        print(f"\n✗ Answer generation failed!")
        print(f"  Error: {status.get('error', 'Unknown error')}")
        break
    else:
        print(f"  [{elapsed:.1f}s] Status: {status['status']} ({status['progress']}/{status['total_questions']})")
        time.sleep(3)
else:
    print("\n⚠ Timeout waiting for task completion")

# Step 4: Verify answers were generated
print("\n" + "=" * 60)
print("Step 4: Verifying generated answers...")
print("-" * 60)

response = requests.get(
    f"http://localhost:8000/api/experiences/{experience_id}",
    timeout=5
)

if response.status_code != 200:
    print(f"Error: {response.status_code}")
    print(response.text)
    exit(1)

experience = response.json()['experience']
print(f"✓ Retrieved experience with {len(experience['questions'])} questions\n")

for i, q in enumerate(experience['questions'], 1):
    print(f"{i}. {q['question']}")
    if q.get('answer'):
        answer_preview = q['answer'][:150] + "..." if len(q['answer']) > 150 else q['answer']
        print(f"   Answer: {answer_preview}")
        print(f"   Has original answer: {q.get('has_original_answer', False)}")
    else:
        print(f"   Answer: None")
    print()

print("=" * 60)
print("Test completed!")
