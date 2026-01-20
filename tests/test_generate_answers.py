"""Test script to verify generate_answers functionality."""

import requests
import json

# Test data
test_data = {
    "content": "面试了字节跳动的算法岗位，二面问了：1. 什么是Transformer？2. 解释注意力机制的原理",
    "generate_answers": True,
    "export_format": "json"
}

# Test without answers
test_data_no_answers = {
    "content": "面试了字节跳动的算法岗位，二面问了：1. 什么是Transformer？2. 解释注意力机制的原理",
    "generate_answers": False,
    "export_format": "json"
}

print("Testing with generate_answers=True...")
print("-" * 60)

try:
    response = requests.post(
        "http://localhost:8000/api/process/text",
        json=test_data,
        timeout=120
    )

    if response.status_code == 200:
        result = response.json()
        print(f"Success: {result['success']}")
        print(f"Processing time: {result['processing_time']:.2f}s")

        if result.get('experience'):
            exp = result['experience']
            print(f"\nCompany: {exp.get('company_name')}")
            print(f"Position: {exp.get('position')}")
            print(f"Stage: {exp.get('interview_stage')}")
            print(f"\nQuestions ({len(exp.get('questions', []))}):")

            for i, q in enumerate(exp.get('questions', []), 1):
                print(f"\n{i}. {q['question']}")
                if q.get('answer'):
                    print(f"   Answer: {q['answer'][:200]}..." if len(q['answer']) > 200 else f"   Answer: {q['answer']}")
                    print(f"   Has original answer: {q.get('has_original_answer', False)}")
                else:
                    print("   Answer: None")
    else:
        print(f"Error: {response.status_code}")
        print(response.text)

except Exception as e:
    print(f"Error: {e}")

print("\n" + "=" * 60)
print("\nTesting with generate_answers=False...")
print("-" * 60)

try:
    response = requests.post(
        "http://localhost:8000/api/process/text",
        json=test_data_no_answers,
        timeout=120
    )

    if response.status_code == 200:
        result = response.json()
        print(f"Success: {result['success']}")

        if result.get('experience'):
            exp = result['experience']
            print(f"\nQuestions ({len(exp.get('questions', []))}):")

            for i, q in enumerate(exp.get('questions', []), 1):
                print(f"\n{i}. {q['question']}")
                if q.get('answer'):
                    print(f"   Answer: {q['answer'][:100]}...")
                else:
                    print("   Answer: None (expected)")
    else:
        print(f"Error: {response.status_code}")
        print(response.text)

except Exception as e:
    print(f"Error: {e}")
