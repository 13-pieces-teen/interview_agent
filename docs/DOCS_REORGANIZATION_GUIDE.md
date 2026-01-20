# 文档整理使用指南

本指南将帮助您整理项目中的 Markdown 文档，使其结构更清晰、更易于维护。

## 📋 整理前准备

### 1. 备份当前文档（可选但推荐）

```bash
# 创建备份分支
git checkout -b backup-before-docs-reorg

# 或者直接复制
cp -r *.md docs_backup/
```

### 2. 查看当前文档状态

```bash
# 查看所有 Markdown 文件
ls -lh *.md

# 查看文档数量
ls *.md | wc -l
```

## 🚀 执行整理

### 方法 1: 使用自动化脚本（推荐）

#### 步骤 1: 预览操作

先预览会进行哪些操作，不实际修改文件：

```bash
python organize_docs.py --dry-run
```

预览输出示例：
```
📂 文档整理脚本
================================================================================
🔍 预览模式 - 不会实际修改文件

📁 步骤 1: 创建目录结构
--------------------------------------------------------------------------------
🔄 Would create docs/ directory structure

📦 步骤 2: 移动文档
--------------------------------------------------------------------------------
🔄 Would move: GETTING_STARTED.md → docs/guides/getting-started.md
🔄 Would move: SETUP_GUIDE.md → docs/guides/setup-guide.md
...

📄 步骤 3: 创建文档索引
--------------------------------------------------------------------------------
🔄 Would create docs/README.md

🔗 步骤 4: 更新 README 链接
--------------------------------------------------------------------------------
🔄 Would update README.md links

================================================================================
✅ 预览完成！使用不带 --dry-run 参数执行实际操作
================================================================================
```

#### 步骤 2: 执行整理

确认预览无误后，执行实际操作：

```bash
python organize_docs.py
```

#### 步骤 3: 更新文档链接

文档移动后，更新所有引用链接：

```bash
# 先预览
python update_doc_links.py --dry-run

# 确认无误后执行
python update_doc_links.py
```

### 方法 2: 手动整理

如果您不想使用自动化脚本，可以手动执行：

```bash
# 1. 创建目录
mkdir -p docs/guides docs/features docs/development docs/changelog

# 2. 移动用户指南
mv GETTING_STARTED.md docs/guides/getting-started.md
mv SETUP_GUIDE.md docs/guides/setup-guide.md
mv QUICK_REFERENCE.md docs/guides/quick-reference.md
mv DEMO_WALKTHROUGH.md docs/guides/demo-walkthrough.md
mv TROUBLESHOOTING.md docs/guides/troubleshooting.md

# 3. 移动功能文档
mv MULTI_IMAGE_GUIDE.md docs/features/multi-image-guide.md
mv CONTENT_VALIDATION.md docs/features/content-validation.md
mv THEME_FEATURE.md docs/features/theme-feature.md
mv HISTORY_FEATURE.md docs/features/history-feature.md
mv HISTORY_QUICKSTART.md docs/features/history-quickstart.md
mv ASYNC_ANSWER_GENERATION.md docs/features/async-answer-generation.md

# 4. 移动开发文档
mv ARCHITECTURE.md docs/development/architecture.md
mv WEB_INTERFACE_SUMMARY.md docs/development/web-interface-summary.md
mv CONTENT_VALIDATION_SUMMARY.md docs/development/content-validation-summary.md
mv IMAGE_OCR_FIX.md docs/development/image-ocr-fix.md
mv BUGFIXES.md docs/development/bugfixes.md

# 5. 移动变更日志
mv CHANGELOG.md docs/changelog/CHANGELOG.md
```

## ✅ 验证整理结果

### 1. 检查目录结构

```bash
tree docs/
```

期望输出：
```
docs/
├── README.md
├── guides/
│   ├── getting-started.md
│   ├── setup-guide.md
│   ├── quick-reference.md
│   ├── demo-walkthrough.md
│   └── troubleshooting.md
├── features/
│   ├── multi-image-guide.md
│   ├── content-validation.md
│   ├── theme-feature.md
│   ├── history-feature.md
│   ├── history-quickstart.md
│   └── async-answer-generation.md
├── development/
│   ├── architecture.md
│   ├── web-interface-summary.md
│   ├── content-validation-summary.md
│   ├── image-ocr-fix.md
│   └── bugfixes.md
└── changelog/
    └── CHANGELOG.md
```

### 2. 检查链接是否有效

使用 markdown-link-check 工具（如果已安装）：

```bash
# 安装工具
npm install -g markdown-link-check

# 检查所有文档
find docs -name "*.md" -exec markdown-link-check {} \;
```

### 3. 手动测试链接

在 VS Code 或其他 Markdown 编辑器中：
1. 打开 [README.md](README.md)
2. Ctrl+点击文档链接
3. 确认能正确跳转

## 📝 提交更改

确认无误后，提交到 Git：

```bash
# 查看更改
git status

# 添加所有更改
git add .

# 提交
git commit -m "docs: 重组文档结构

- 创建 docs/ 目录并按分类组织文档
- 将文档分为 guides/features/development/changelog 四类
- 更新所有文档内部链接
- 创建文档索引 docs/README.md
"

# 推送（如果需要）
git push origin main
```

## 🔄 整理后的维护

### 新增文档规则

以后添加新文档时，遵循以下规则：

1. **用户指南** → `docs/guides/`
   - 快速开始、安装配置、使用教程等

2. **功能文档** → `docs/features/`
   - 具体功能的详细说明

3. **开发文档** → `docs/development/`
   - 架构设计、API文档、实现细节等

4. **更新日志** → `docs/changelog/`
   - 版本变更记录

### 文档命名规范

使用小写字母和连字符：

```
✅ good:  getting-started.md
❌ bad:   GETTING_STARTED.md

✅ good:  api-reference.md
❌ bad:   API_Reference.md
```

## 🆘 常见问题

### Q1: 执行脚本后发现问题，如何回滚？

```bash
# 如果已提交
git revert HEAD

# 如果未提交
git restore .
git clean -fd
```

### Q2: 某些文档没有被移动？

检查文件是否在 `organize_docs.py` 的 `DOC_MAPPING` 中定义。如果没有，手动添加：

```python
DOC_MAPPING = {
    "guides": [
        "YOUR_NEW_DOC.md",  # 添加这里
        # ...
    ],
}
```

### Q3: 链接更新后仍然失效？

可能是相对路径计算问题，手动检查：

```bash
# 查找所有 Markdown 链接
grep -r "\[.*\](.*\.md)" docs/
```

### Q4: 我想保留原来的大写命名？

编辑 `organize_docs.py`，将 `NAME_MAPPING` 中的转换改为保持原名：

```python
NAME_MAPPING = {
    "GETTING_STARTED.md": "GETTING_STARTED.md",  # 保持大写
    # ...
}
```

## 📚 参考资源

- [文档结构说明](DOCUMENTATION_STRUCTURE.md) - 详细的整理方案
- [组织文档脚本](organize_docs.py) - 自动化整理脚本
- [链接更新脚本](update_doc_links.py) - 链接更新脚本

## 🎯 下一步

整理完成后，考虑：

1. ✅ 更新 README.md，添加文档导航
2. ✅ 合并重复内容（如 HISTORY_FEATURE + HISTORY_QUICKSTART）
3. ✅ 添加文档构建工具（如 MkDocs、Docusaurus）
4. ✅ 设置 CI 检查文档链接有效性
5. ✅ 编写贡献指南，规范文档更新流程

---

如有问题，请查看 [DOCUMENTATION_STRUCTURE.md](DOCUMENTATION_STRUCTURE.md) 或提交 Issue。
