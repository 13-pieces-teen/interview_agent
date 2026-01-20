# 项目文档结构整理方案

## 当前文档分类

### 1. 核心文档（保留在根目录）
这些是项目必需的核心文档，应保持在根目录：

- **[README.md](README.md)** (6.4K) - 项目主入口文档
- **[PRD.md](PRD.md)** (15K) - 产品需求文档（用户手写）
- **一些新想法.md** (65B) - 未来功能构思

### 2. 用户指南类（建议移至 `docs/guides/`）
面向用户的使用指南和快速入门：

- **[GETTING_STARTED.md](GETTING_STARTED.md)** (2.9K) - 快速开始
- **[SETUP_GUIDE.md](SETUP_GUIDE.md)** (6.4K) - 详细安装配置
- **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)** (5.8K) - 快速参考
- **[DEMO_WALKTHROUGH.md](DEMO_WALKTHROUGH.md)** (18K) - 演示教程
- **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** (5.5K) - 故障排查

### 3. 功能文档类（建议移至 `docs/features/`）
具体功能的详细文档：

- **[MULTI_IMAGE_GUIDE.md](MULTI_IMAGE_GUIDE.md)** (8.4K) - 多图上传功能
- **[CONTENT_VALIDATION.md](CONTENT_VALIDATION.md)** (5.7K) - 内容验证功能
- **[THEME_FEATURE.md](THEME_FEATURE.md)** (7.3K) - 主题功能
- **[HISTORY_FEATURE.md](HISTORY_FEATURE.md)** (7.4K) - 历史记录功能
- **[HISTORY_QUICKSTART.md](HISTORY_QUICKSTART.md)** (2.6K) - 历史记录快速入门
- **[ASYNC_ANSWER_GENERATION.md](ASYNC_ANSWER_GENERATION.md)** (6.1K) - 异步答案生成

### 4. 开发文档类（建议移至 `docs/development/`）
面向开发者的技术文档：

- **[ARCHITECTURE.md](ARCHITECTURE.md)** (14K) - 系统架构
- **[WEB_INTERFACE_SUMMARY.md](WEB_INTERFACE_SUMMARY.md)** (11K) - Web界面实现总结
- **[CONTENT_VALIDATION_SUMMARY.md](CONTENT_VALIDATION_SUMMARY.md)** (6.8K) - 内容验证实现总结
- **[IMAGE_OCR_FIX.md](IMAGE_OCR_FIX.md)** (7.0K) - OCR修复文档
- **[BUGFIXES.md](BUGFIXES.md)** (2.6K) - Bug修复记录

### 5. 变更日志类（建议移至 `docs/changelog/`）
版本更新和变更记录：

- **[CHANGELOG.md](CHANGELOG.md)** (8.0K) - 更新日志

---

## 推荐目录结构

```
interview_agent/
├── README.md                          # 主入口文档
├── PRD.md                             # 产品需求文档
├── 一些新想法.md                      # 未来构思
│
├── docs/                              # 文档目录
│   ├── guides/                        # 用户指南
│   │   ├── getting-started.md         # 快速开始
│   │   ├── setup-guide.md             # 安装配置
│   │   ├── quick-reference.md         # 快速参考
│   │   ├── demo-walkthrough.md        # 演示教程
│   │   └── troubleshooting.md         # 故障排查
│   │
│   ├── features/                      # 功能文档
│   │   ├── multi-image-guide.md       # 多图上传
│   │   ├── content-validation.md      # 内容验证
│   │   ├── theme-feature.md           # 主题功能
│   │   ├── history-feature.md         # 历史记录
│   │   ├── history-quickstart.md      # 历史快速入门
│   │   └── async-answer-generation.md # 异步答案生成
│   │
│   ├── development/                   # 开发文档
│   │   ├── architecture.md            # 系统架构
│   │   ├── web-interface-summary.md   # Web界面总结
│   │   ├── content-validation-summary.md # 验证实现总结
│   │   ├── image-ocr-fix.md           # OCR修复
│   │   └── bugfixes.md                # Bug修复记录
│   │
│   └── changelog/                     # 变更日志
│       └── CHANGELOG.md               # 更新日志
│
├── src/                               # 源代码
├── frontend/                          # 前端代码
├── tests/                             # 测试代码
└── ...
```

---

## 文档内容优化建议

### 合并重复内容

#### 1. 历史记录功能（可合并）
- `HISTORY_FEATURE.md` (7.4K) - 详细功能文档
- `HISTORY_QUICKSTART.md` (2.6K) - 快速入门

**建议**: 合并为一个文档 `docs/features/history-feature.md`，包含：
- 概览部分（来自 QUICKSTART）
- 详细功能部分（来自 FEATURE）

#### 2. 内容验证功能（可合并）
- `CONTENT_VALIDATION.md` (5.7K) - 用户文档
- `CONTENT_VALIDATION_SUMMARY.md` (6.8K) - 实现总结

**建议**:
- 保留 `CONTENT_VALIDATION.md` 给用户
- 将 `CONTENT_VALIDATION_SUMMARY.md` 移至开发文档

#### 3. 入门指南（可合并）
- `GETTING_STARTED.md` (2.9K)
- `SETUP_GUIDE.md` (6.4K)
- `README.md` 的部分内容

**建议**:
- README 保留简短介绍和 Quick Start
- GETTING_STARTED 作为详细入门
- SETUP_GUIDE 作为深度配置指南

### 删除冗余文档

这些文档的内容可能已经过时或被其他文档覆盖：
- `BUGFIXES.md` - 如果内容已合并到 CHANGELOG，可删除
- `WEB_INTERFACE_SUMMARY.md` - 如果 ARCHITECTURE 已包含，可删除

---

## 文档命名规范建议

统一使用小写加连字符的命名方式，便于跨平台使用：

```
大写命名（当前）          →  小写命名（推荐）
GETTING_STARTED.md       →  getting-started.md
CONTENT_VALIDATION.md    →  content-validation.md
MULTI_IMAGE_GUIDE.md     →  multi-image-guide.md
```

---

## 实施步骤

### 步骤 1: 创建目录结构
```bash
mkdir -p docs/guides
mkdir -p docs/features
mkdir -p docs/development
mkdir -p docs/changelog
```

### 步骤 2: 移动文件
```bash
# 用户指南
mv GETTING_STARTED.md docs/guides/getting-started.md
mv SETUP_GUIDE.md docs/guides/setup-guide.md
mv QUICK_REFERENCE.md docs/guides/quick-reference.md
mv DEMO_WALKTHROUGH.md docs/guides/demo-walkthrough.md
mv TROUBLESHOOTING.md docs/guides/troubleshooting.md

# 功能文档
mv MULTI_IMAGE_GUIDE.md docs/features/multi-image-guide.md
mv CONTENT_VALIDATION.md docs/features/content-validation.md
mv THEME_FEATURE.md docs/features/theme-feature.md
mv HISTORY_FEATURE.md docs/features/history-feature.md
mv HISTORY_QUICKSTART.md docs/features/history-quickstart.md
mv ASYNC_ANSWER_GENERATION.md docs/features/async-answer-generation.md

# 开发文档
mv ARCHITECTURE.md docs/development/architecture.md
mv WEB_INTERFACE_SUMMARY.md docs/development/web-interface-summary.md
mv CONTENT_VALIDATION_SUMMARY.md docs/development/content-validation-summary.md
mv IMAGE_OCR_FIX.md docs/development/image-ocr-fix.md
mv BUGFIXES.md docs/development/bugfixes.md

# 变更日志
mv CHANGELOG.md docs/changelog/CHANGELOG.md
```

### 步骤 3: 更新 README.md

在 README.md 中添加文档导航：

```markdown
## 📚 文档

### 快速开始
- [快速开始](docs/guides/getting-started.md) - 5分钟上手
- [安装配置](docs/guides/setup-guide.md) - 详细配置指南
- [快速参考](docs/guides/quick-reference.md) - 常用命令速查

### 功能指南
- [多图上传](docs/features/multi-image-guide.md) - 批量处理面经截图
- [内容验证](docs/features/content-validation.md) - 智能内容过滤
- [历史记录](docs/features/history-feature.md) - 查看处理历史
- [主题切换](docs/features/theme-feature.md) - 深色/浅色模式

### 开发文档
- [系统架构](docs/development/architecture.md) - 技术架构说明
- [API参考](docs/development/api-reference.md) - API接口文档

### 更新日志
- [更新日志](docs/changelog/CHANGELOG.md) - 版本变更记录
```

### 步骤 4: 更新文档内部链接

使用脚本批量更新文档中的相互引用链接。

---

## 优先级

### 🔴 高优先级（立即执行）
1. 创建 `docs/` 目录结构
2. 移动文档到对应目录
3. 更新 README.md 添加文档导航

### 🟡 中优先级（本周完成）
1. 合并重复文档
2. 统一命名规范
3. 更新内部链接

### 🟢 低优先级（逐步优化）
1. 优化文档内容
2. 添加更多示例
3. 改进文档格式

---

## 维护建议

### 新增文档规则
1. 用户指南 → `docs/guides/`
2. 功能文档 → `docs/features/`
3. 开发文档 → `docs/development/`
4. 版本变更 → `docs/changelog/`

### 文档更新原则
1. 每次新功能必须更新对应文档
2. Bug修复需要更新 CHANGELOG
3. 架构变更需要更新 ARCHITECTURE
4. 定期清理过时内容

### 文档质量检查
- [ ] 所有链接可访问
- [ ] 代码示例可运行
- [ ] 截图/图表清晰
- [ ] 格式统一规范
- [ ] 内容准确最新

---

## 总结

**当前问题:**
- 19个 Markdown 文档散落在根目录
- 文档分类不清晰
- 部分内容重复
- 命名规范不统一

**解决方案:**
- 创建 `docs/` 目录，分类存放
- 合并重复内容
- 统一命名规范
- 建立维护机制

**预期效果:**
- 文档结构清晰
- 易于查找和维护
- 用户体验提升
- 开发效率提高
