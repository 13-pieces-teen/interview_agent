# 项目文档整理 - 快速指南

## 📊 当前状态

您的项目有 **19个 Markdown 文档**散落在根目录，需要整理。

## 🎯 整理方案

将文档重组为以下结构：

```
docs/
├── guides/        # 用户指南 (5个)
├── features/      # 功能文档 (6个)
├── development/   # 开发文档 (5个)
└── changelog/     # 变更日志 (1个)
```

## 🚀 快速开始

### 1. 预览整理

```bash
python organize_docs.py --dry-run
```

### 2. 执行整理

```bash
python organize_docs.py
```

### 3. 更新链接

```bash
python update_doc_links.py
```

### 4. 验证结果

```bash
tree docs/  # 或 dir /s docs
```

### 5. 提交更改

```bash
git add .
git commit -m "docs: 重组文档结构"
```

## 📚 详细文档

- **[DOCS_ORGANIZATION_SUMMARY.md](DOCS_ORGANIZATION_SUMMARY.md)** - 完整总结
- **[DOCUMENTATION_STRUCTURE.md](DOCUMENTATION_STRUCTURE.md)** - 详细方案
- **[DOCS_REORGANIZATION_GUIDE.md](DOCS_REORGANIZATION_GUIDE.md)** - 使用指南

## ✅ 已准备好的工具

1. **[organize_docs.py](organize_docs.py)** - 自动整理脚本
2. **[update_doc_links.py](update_doc_links.py)** - 链接更新脚本
3. 详细的使用文档和方案

## 💡 注意事项

- ✅ 所有操作支持 `--dry-run` 预览
- ✅ 已修复 Windows 编码问题
- ✅ 自动创建目录结构
- ✅ 智能更新文档链接

## 🎉 开始整理

运行以下命令即可开始：

```bash
python organize_docs.py --dry-run
```

预览无误后，去掉 `--dry-run` 参数执行实际操作。
