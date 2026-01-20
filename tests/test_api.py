"""Test script for the web API."""

import requests
import json

API_BASE = "http://localhost:8000"

# Test 1: Health check
print("Testing health check...")
response = requests.get(f"{API_BASE}/health")
print(f"Status: {response.status_code}")
print(f"Response: {response.json()}\n")

# Test 2: Process text
print("Testing text processing...")
test_data = {
    "content": """公司：字节跳动
职位：Python工程师
阶段：一面

问题1：介绍一下Python的GIL
答：全局解释器锁，保护多线程访问Python对象。

问题2：Redis和MySQL的区别
答：Redis是内存数据库，速度快；MySQL是关系型数据库，持久化存储。
""",
    "generate_answers": False,
    "export_format": "both"
}

try:
    response = requests.post(f"{API_BASE}/api/process/text", json=test_data, timeout=60)
    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        result = response.json()
        print(f"Success: {result['success']}")
        print(f"Processing time: {result['processing_time']:.2f}s")
        print(f"Output files: {result['output_files']}")

        if result['experience']:
            exp = result['experience']
            print(f"\nCompany: {exp.get('company_name')}")
            print(f"Position: {exp.get('position')}")
            print(f"Questions: {len(exp.get('questions', []))}")
            print(f"Tags: {', '.join(exp.get('tags', []))}")
    else:
        print(f"Error: {response.text}")

except Exception as e:
    print(f"Request failed: {e}")
