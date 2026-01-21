"""
诊断FastAPI路由问题
"""
import sys
sys.path.insert(0, 'd:\\LLM_learning\\interview_agent')

from src.api.app import app

print("=" * 60)
print("FastAPI 路由诊断")
print("=" * 60)

print("\n所有注册的路由:")
print("-" * 60)

routes = []
for route in app.routes:
    if hasattr(route, 'path') and hasattr(route, 'methods'):
        routes.append({
            'path': route.path,
            'methods': route.methods,
            'name': route.name if hasattr(route, 'name') else 'N/A'
        })

# 过滤包含 'async' 的路由
async_routes = [r for r in routes if 'async' in r['path'].lower()]

print(f"\n找到 {len(async_routes)} 个包含 'async' 的路由:\n")
for idx, route in enumerate(async_routes, 1):
    print(f"{idx}. 路径: {route['path']}")
    print(f"   方法: {route['methods']}")
    print(f"   函数: {route['name']}")
    print()

# 检查路由顺序
print("=" * 60)
print("路由定义顺序检查")
print("=" * 60)

target_routes = [
    '/api/tasks/async',
    '/api/tasks/async/{task_id}'
]

print("\n期望顺序:")
for idx, path in enumerate(target_routes, 1):
    print(f"{idx}. {path}")

print("\n实际顺序:")
actual_order = []
for idx, route in enumerate(app.routes):
    if hasattr(route, 'path') and route.path in target_routes:
        actual_order.append(route.path)
        print(f"{len(actual_order)}. {route.path} (索引: {idx})")

if actual_order == target_routes:
    print("\n✓ 路由顺序正确")
else:
    print("\n✗ 路由顺序错误!")
    print(f"  期望: {target_routes}")
    print(f"  实际: {actual_order}")

# 测试路由匹配
print("\n" + "=" * 60)
print("路由匹配测试")
print("=" * 60)

test_paths = [
    "/api/tasks/async",
    "/api/tasks/async?status=completed",
    "/api/tasks/async/12345"
]

print("\n测试路径匹配:")
for test_path in test_paths:
    print(f"\n  测试: {test_path}")
    matched = False
    for route in app.routes:
        if hasattr(route, 'path') and hasattr(route, 'path_regex'):
            # 移除查询参数
            path_only = test_path.split('?')[0]
            if route.path_regex.match(path_only):
                print(f"    → 匹配到: {route.path} ({route.name})")
                matched = True
                break
    if not matched:
        print(f"    → 未匹配到任何路由")

print("\n" + "=" * 60)
