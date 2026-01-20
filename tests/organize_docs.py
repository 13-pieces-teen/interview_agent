#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文档自动整理脚本
自动将项目中的 Markdown 文档按分类移动到 docs 目录
"""

import os
import sys
import shutil
from pathlib import Path

# Fix Windows console encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


# 文档分类映射
DOC_MAPPING = {
    "guides": [
        "GETTING_STARTED.md",
        "SETUP_GUIDE.md",
        "QUICK_REFERENCE.md",
        "DEMO_WALKTHROUGH.md",
        "TROUBLESHOOTING.md",
    ],
    "features": [
        "MULTI_IMAGE_GUIDE.md",
        "CONTENT_VALIDATION.md",
        "THEME_FEATURE.md",
        "HISTORY_FEATURE.md",
        "HISTORY_QUICKSTART.md",
        "ASYNC_ANSWER_GENERATION.md",
    ],
    "development": [
        "ARCHITECTURE.md",
        "WEB_INTERFACE_SUMMARY.md",
        "CONTENT_VALIDATION_SUMMARY.md",
        "IMAGE_OCR_FIX.md",
        "BUGFIXES.md",
    ],
    "changelog": [
        "CHANGELOG.md",
    ],
}

# 文件名转换映射（可选：将大写下划线改为小写连字符）
NAME_MAPPING = {
    "GETTING_STARTED.md": "getting-started.md",
    "SETUP_GUIDE.md": "setup-guide.md",
    "QUICK_REFERENCE.md": "quick-reference.md",
    "DEMO_WALKTHROUGH.md": "demo-walkthrough.md",
    "TROUBLESHOOTING.md": "troubleshooting.md",
    "MULTI_IMAGE_GUIDE.md": "multi-image-guide.md",
    "CONTENT_VALIDATION.md": "content-validation.md",
    "THEME_FEATURE.md": "theme-feature.md",
    "HISTORY_FEATURE.md": "history-feature.md",
    "HISTORY_QUICKSTART.md": "history-quickstart.md",
    "ASYNC_ANSWER_GENERATION.md": "async-answer-generation.md",
    "ARCHITECTURE.md": "architecture.md",
    "WEB_INTERFACE_SUMMARY.md": "web-interface-summary.md",
    "CONTENT_VALIDATION_SUMMARY.md": "content-validation-summary.md",
    "IMAGE_OCR_FIX.md": "image-ocr-fix.md",
    "BUGFIXES.md": "bugfixes.md",
    "CHANGELOG.md": "CHANGELOG.md",  # 保持大写
}


def create_directory_structure(base_path: Path):
    """创建 docs 目录结构"""
    docs_dir = base_path / "docs"

    directories = [
        docs_dir / "guides",
        docs_dir / "features",
        docs_dir / "development",
        docs_dir / "changelog",
    ]

    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
        print(f"✅ Created directory: {directory.relative_to(base_path)}")


def move_documents(base_path: Path, dry_run: bool = False):
    """移动文档到对应目录"""
    docs_dir = base_path / "docs"
    moved_count = 0
    skipped_count = 0

    for category, files in DOC_MAPPING.items():
        category_dir = docs_dir / category

        for filename in files:
            source = base_path / filename

            if not source.exists():
                print(f"⚠️  File not found: {filename}")
                skipped_count += 1
                continue

            # 获取新文件名（可选转换为小写连字符）
            new_filename = NAME_MAPPING.get(filename, filename)
            destination = category_dir / new_filename

            if dry_run:
                print(f"🔄 Would move: {filename} → {destination.relative_to(base_path)}")
            else:
                try:
                    shutil.move(str(source), str(destination))
                    print(f"✅ Moved: {filename} → {destination.relative_to(base_path)}")
                    moved_count += 1
                except Exception as e:
                    print(f"❌ Failed to move {filename}: {e}")
                    skipped_count += 1

    return moved_count, skipped_count


def update_readme_links(base_path: Path, dry_run: bool = False):
    """更新 README.md 中的文档链接"""
    readme_path = base_path / "README.md"

    if not readme_path.exists():
        print("⚠️  README.md not found")
        return

    # 读取 README 内容
    with open(readme_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 链接替换映射
    link_replacements = {
        "ARCHITECTURE.md": "docs/development/architecture.md",
        "SETUP_GUIDE.md": "docs/guides/setup-guide.md",
        # 可以添加更多链接映射
    }

    updated_content = content
    for old_link, new_link in link_replacements.items():
        updated_content = updated_content.replace(old_link, new_link)

    if updated_content != content:
        if dry_run:
            print("🔄 Would update README.md links")
        else:
            with open(readme_path, "w", encoding="utf-8") as f:
                f.write(updated_content)
            print("✅ Updated README.md links")
    else:
        print("ℹ️  No links to update in README.md")


def create_docs_index(base_path: Path, dry_run: bool = False):
    """创建 docs/README.md 索引文件"""
    docs_dir = base_path / "docs"
    index_path = docs_dir / "README.md"

    index_content = """# 文档目录

## 📖 用户指南

快速上手和使用指南：

- [快速开始](guides/getting-started.md) - 5分钟上手
- [安装配置](guides/setup-guide.md) - 详细配置指南
- [快速参考](guides/quick-reference.md) - 常用命令速查
- [演示教程](guides/demo-walkthrough.md) - 完整功能演示
- [故障排查](guides/troubleshooting.md) - 常见问题解决

## ✨ 功能文档

详细功能介绍：

- [多图上传](features/multi-image-guide.md) - 批量处理面经截图
- [内容验证](features/content-validation.md) - 智能内容过滤
- [历史记录](features/history-feature.md) - 查看处理历史
- [主题切换](features/theme-feature.md) - 深色/浅色模式
- [异步答案生成](features/async-answer-generation.md) - 后台答案生成

## 🔧 开发文档

技术架构和实现细节：

- [系统架构](development/architecture.md) - 技术架构说明
- [Web界面实现](development/web-interface-summary.md) - 前端实现总结
- [内容验证实现](development/content-validation-summary.md) - 验证功能实现
- [OCR修复](development/image-ocr-fix.md) - 图片识别问题修复
- [Bug修复记录](development/bugfixes.md) - 历史Bug修复

## 📝 更新日志

- [变更日志](changelog/CHANGELOG.md) - 版本变更记录

---

[返回主页](../README.md)
"""

    if dry_run:
        print("🔄 Would create docs/README.md")
    else:
        with open(index_path, "w", encoding="utf-8") as f:
            f.write(index_content)
        print("✅ Created docs/README.md index")


def main():
    import argparse

    parser = argparse.ArgumentParser(description="整理项目文档")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="预览操作但不实际执行",
    )
    parser.add_argument(
        "--skip-move",
        action="store_true",
        help="跳过文件移动（仅创建目录和索引）",
    )

    args = parser.parse_args()

    # 获取项目根目录
    base_path = Path(__file__).parent

    print("=" * 80)
    print("📂 文档整理脚本")
    print("=" * 80)

    if args.dry_run:
        print("🔍 预览模式 - 不会实际修改文件")
        print()

    # 步骤 1: 创建目录结构
    print("\n📁 步骤 1: 创建目录结构")
    print("-" * 80)
    if not args.dry_run:
        create_directory_structure(base_path)
    else:
        print("🔄 Would create docs/ directory structure")

    # 步骤 2: 移动文档
    if not args.skip_move:
        print("\n📦 步骤 2: 移动文档")
        print("-" * 80)
        moved, skipped = move_documents(base_path, dry_run=args.dry_run)

        if not args.dry_run:
            print(f"\n📊 移动统计: {moved} 个成功, {skipped} 个跳过")

    # 步骤 3: 创建文档索引
    print("\n📄 步骤 3: 创建文档索引")
    print("-" * 80)
    create_docs_index(base_path, dry_run=args.dry_run)

    # 步骤 4: 更新 README 链接
    print("\n🔗 步骤 4: 更新 README 链接")
    print("-" * 80)
    update_readme_links(base_path, dry_run=args.dry_run)

    print("\n" + "=" * 80)
    if args.dry_run:
        print("✅ 预览完成！使用不带 --dry-run 参数执行实际操作")
    else:
        print("✅ 文档整理完成！")
    print("=" * 80)

    if not args.dry_run:
        print("\n💡 后续步骤:")
        print("1. 检查移动后的文档是否正常")
        print("2. 更新文档内部的相互引用链接")
        print("3. 提交 Git 更改: git add docs/ && git commit -m 'docs: 重组文档结构'")


if __name__ == "__main__":
    main()
