# MarkItDown

> 将各种文档/文件自动转换为结构化 Markdown 的桌面应用（GUI-only，可通过 build/build_exe.py 打包为 Windows exe）。

版本: `0.1.6b2`（见 `src/markitdown/__about__.py`）

- 适合谁用：需要把大量富格式或二进制文档快速转为 Markdown 用于 LLM、笔记/知识库导入、静态站点或文本分析的开发者与工程团队。

---

## ✨ 项目亮点
- 支持广泛的输入格式（PDF / Word / Excel / PowerPoint / 图片 / EPUB / ZIP / 网页 / RSS / Jupyter Notebook / 音频 等）。
- 带桌面 GUI（Windows）与打包脚本（见 `gui/` 与 `build/`）。
- 该仓库已迁移为 GUI-only 分发：不再通过 pip 发布 console script 或公开顶层 API。转换实现作为 GUI 的内部模块被捆绑到 EXE 中。

---

## 🚀 快速开始 — GUI

开发模式运行（在开发环境中可运行）：

```bash
python gui/main.py
# 或者运行打包生成的可执行文件（dist/ 下的 MarkItDown_v*.exe）
```

EXE 打包：

```bash
py -3 build/build_exe.py
# 打包脚本会基于当前源码生成单文件 exe（需要 PyInstaller 及若干二进制依赖）。
```

---

## ⚠️ Breaking change（重要）
本仓库已移除对命令行（CLI）和 pip 安装的官方支持：
- 不再为 `markitdown` 提供 console script。请用 GUI 可执行文件代替命令行工具。
- 顶层导出 `from markitdown import MarkItDown` 不再受支持。GUI 会在内部使用 `markitdown._markitdown.MarkItDown`。

如果你依赖原先的 CLI 或库 API，请参考 Release note 中的迁移建议或在仓库 issue 里寻求帮助。

---

## 📁 仓库快速目录
- `src/` — 核心实现（`_markitdown.py`, 各 `converters/`, `converter_utils/` 等），供 GUI 内部使用
- `gui/` — 桌面 GUI 源码（Windows 环境）
- `build/` — 打包说明与 PyInstaller/Exe 配置
- `archive/` — 若干已归档的子包示例（`markitdown-mcp`, `markitdown-ocr`, `markitdown-sample-plugin`, ...）

---

## 🧪 开发与测试（简要）
建议使用虚拟环境，要求 Python >= 3.10（见 `pyproject.toml`）。

快速安装（开发）：
```bash
python -m venv .venv
source .venv/bin/activate   # macOS / Linux
.\.venv\Scripts\activate  # Windows PowerShell / cmd
# 运行 GUI（开发）
python gui/main.py
```

运行测试（建议）：
```bash
pytest -q -k "not cli and not plugin"
```

---

## 📝 许可证
MIT（见 `pyproject.toml` 中的 license 字段）
