#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文档链接更新脚本
自动更新文档中的相互引用链接
"""

import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple

# Fix Windows console encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


# 文件移动映射 (旧路径 -> 新路径)
FILE_MOVES = {
    "GETTING_STARTED.md": "docs/guides/getting-started.md",
    "SETUP_GUIDE.md": "docs/guides/setup-guide.md",
    "QUICK_REFERENCE.md": "docs/guides/quick-reference.md",
    "DEMO_WALKTHROUGH.md": "docs/guides/demo-walkthrough.md",
    "TROUBLESHOOTING.md": "docs/guides/troubleshooting.md",
    "MULTI_IMAGE_GUIDE.md": "docs/features/multi-image-guide.md",
    "CONTENT_VALIDATION.md": "docs/features/content-validation.md",
    "THEME_FEATURE.md": "docs/features/theme-feature.md",
    "HISTORY_FEATURE.md": "docs/features/history-feature.md",
    "HISTORY_QUICKSTART.md": "docs/features/history-quickstart.md",
    "ASYNC_ANSWER_GENERATION.md": "docs/features/async-answer-generation.md",
    "ARCHITECTURE.md": "docs/development/architecture.md",
    "WEB_INTERFACE_SUMMARY.md": "docs/development/web-interface-summary.md",
    "CONTENT_VALIDATION_SUMMARY.md": "docs/development/content-validation-summary.md",
    "IMAGE_OCR_FIX.md": "docs/development/image-ocr-fix.md",
    "BUGFIXES.md": "docs/development/bugfixes.md",
    "CHANGELOG.md": "docs/changelog/CHANGELOG.md",
}


def find_markdown_links(content: str) -> List[Tuple[str, str, str]]:
    """
    查找 Markdown 文件中的所有链接
    返回: [(完整匹配, 链接文本, 链接URL), ...]
    """
    # 匹配 [text](url) 格式的链接
    pattern = r'\[([^\]]+)\]\(([^)]+)\)'
    matches = re.finditer(pattern, content)

    links = []
    for match in matches:
        full_match = match.group(0)
        link_text = match.group(1)
        link_url = match.group(2)
        links.append((full_match, link_text, link_url))

    return links


def calculate_relative_path(from_path: Path, to_path: Path) -> str:
    """
    计算从 from_path 到 to_path 的相对路径
    """
    try:
        return str(Path(to_path).relative_to(from_path.parent))
    except ValueError:
        # 如果无法计算相对路径，使用 os.path.relpath
        import os
        return os.path.relpath(to_path, from_path.parent).replace("\\", "/")


def update_links_in_file(
    file_path: Path,
    file_moves: Dict[str, str],
    dry_run: bool = False
) -> Tuple[int, List[str]]:
    """
    更新单个文件中的链接
    返回: (更新数量, 更新详情列表)
    """
    if not file_path.exists():
        return 0, [f"File not found: {file_path}"]

    # 读取文件内容
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    original_content = content
    updates = []

    # 查找所有链接
    links = find_markdown_links(content)

    for full_match, link_text, link_url in links:
        # 跳过外部链接和锚点链接
        if link_url.startswith(("http://", "https://", "#")):
            continue

        # 提取文件名（去除路径和锚点）
        url_parts = link_url.split("#")
        file_part = url_parts[0]
        anchor = "#" + url_parts[1] if len(url_parts) > 1 else ""

        # 检查是否需要更新
        if file_part in file_moves:
            # 计算新的相对路径
            new_absolute_path = file_moves[file_part]
            new_relative_path = calculate_relative_path(
                file_path,
                Path(new_absolute_path)
            )

            # 添加锚点（如果有）
            new_url = new_relative_path + anchor

            # 替换链接
            new_match = f"[{link_text}]({new_url})"
            content = content.replace(full_match, new_match, 1)

            updates.append(f"  {link_url} → {new_url}")

    # 如果有更新，写回文件
    if content != original_content:
        if not dry_run:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)

        return len(updates), updates
    else:
        return 0, []


def scan_and_update_docs(
    base_path: Path,
    file_moves: Dict[str, str],
    dry_run: bool = False
):
    """
    扫描所有 Markdown 文件并更新链接
    """
    # 查找所有 Markdown 文件
    markdown_files = [
        base_path / "README.md",
        base_path / "PRD.md",
    ]

    # 添加 docs 目录下的所有文件
    docs_dir = base_path / "docs"
    if docs_dir.exists():
        markdown_files.extend(docs_dir.rglob("*.md"))

    total_updates = 0
    updated_files = []

    print(f"\n🔍 扫描 {len(markdown_files)} 个 Markdown 文件...")
    print("-" * 80)

    for md_file in markdown_files:
        if not md_file.is_file():
            continue

        update_count, updates = update_links_in_file(
            md_file,
            file_moves,
            dry_run=dry_run
        )

        if update_count > 0:
            relative_path = md_file.relative_to(base_path)
            status = "🔄 Would update" if dry_run else "✅ Updated"
            print(f"\n{status}: {relative_path}")
            print(f"  {update_count} link(s) updated:")

            for update in updates:
                print(update)

            total_updates += update_count
            updated_files.append(str(relative_path))

    return total_updates, updated_files


def main():
    import argparse

    parser = argparse.ArgumentParser(description="更新文档中的链接")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="预览操作但不实际执行",
    )

    args = parser.parse_args()

    # 获取项目根目录
    base_path = Path(__file__).parent

    print("=" * 80)
    print("🔗 文档链接更新脚本")
    print("=" * 80)

    if args.dry_run:
        print("🔍 预览模式 - 不会实际修改文件")

    # 扫描并更新文档
    total_updates, updated_files = scan_and_update_docs(
        base_path,
        FILE_MOVES,
        dry_run=args.dry_run
    )

    # 总结
    print("\n" + "=" * 80)
    print("📊 更新统计")
    print("=" * 80)
    print(f"总共更新: {total_updates} 个链接")
    print(f"影响文件: {len(updated_files)} 个")

    if updated_files:
        print("\n受影响的文件:")
        for file in updated_files:
            print(f"  - {file}")

    print("\n" + "=" * 80)
    if args.dry_run:
        print("✅ 预览完成！使用不带 --dry-run 参数执行实际操作")
    else:
        print("✅ 链接更新完成！")
    print("=" * 80)


if __name__ == "__main__":
    main()
