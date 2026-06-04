# MarkItDown

> 将各种文档/文件自动转换为结构化 Markdown 的桌面 GUI 工具（GUI-only，可通过 build/build_exe.py 打包为 Windows exe）。

[![Version](https://img.shields.io/badge/version-0.1.6b2-blue)](src/markitdown/__about__.py) [![License](https://img.shields.io/badge/license-MIT-green)](LICENSE) [![Python](https://img.shields.io/badge/python-%3E%3D3.10-3776AB)](https://www.python.org/)

## 适用场景

- 需要把 PDF / Word / Excel / PowerPoint / 图片 / EPUB / ZIP / 网页 等文件批量转换为 Markdown 用于 LLM、笔记或知识库导入
- 想通过一个桌面应用完成文件转换与输出，而不使用命令行
- 希望把复杂的文档内容（表格、图片、数学公式、附件）规范化为可读的 Markdown

## 功能特性

- 多格式输入：支持 PDF、DOCX、DOC、XLSX、XLS、PPTX、图片（JPEG/PNG 等）、EPUB、ZIP、HTML、RSS、Jupyter Notebook、音频等
- 桌面 GUI：拖拽、选择文件、选择输出目录、批量转换、转换日志和输出文件直接打开
- 图片处理策略：提取图片为文件 / 嵌入 base64 / 忽略图片（针对 DOCX、PPTX、EPUB 等）
- 输出冲突处理：支持覆盖、跳过、全部覆盖/全部跳过
- 单文件 EXE 打包：使用 build/build_exe.py 将程序打包为单文件 exe（无需安装 Python）
- 内部实现保留为模块化转换器，便于在打包时选择需要的依赖以控制体积

## 快速开始

### 环境要求

- Windows 推荐使用（GUI 已在 Windows 下测试）
- Python 3.10+

### 启动（开发模式）

```bash
# 在开发环境运行 GUI
python gui/main.py
```

或在打包后直接运行生成的 exe（位于 dist/ 目录）：

```bash
# 运行生成的 exe
dist\MarkItDown_v<version>_<timestamp>.exe
```

### 打包为 EXE（快速示例）

```bash
# 创建并激活虚拟环境（Windows 示例）
py -3 -m venv .venv
.venv\Scripts\activate

# 安装打包与 GUI 所需依赖（按需选择 extras，避免安装 all 导致体积膨胀）
py -3 -m pip install pyinstaller tkinterdnd2 pillow

# 运行打包脚本（会在 dist/ 下产出单文件 exe）
py -3 build/build_exe.py
```

详细打包步骤与依赖管理请参阅 `build/README_PACKAGING.md`。

## 项目结构

```
markitdown/
├── src/                    # 核心实现（_markitdown.py、converters/、converter_utils/ 等）
├── gui/                    # 桌面 GUI 源码
│   ├── main.py             # 程序入口
│   ├── _app.py             # 主窗口类 MarkItDownGUI
│   ├── _dialogs.py         # 对话框（关于、覆盖确认）
│   └── _version.py         # GUI 版本号
├── build/                  # 打包相关脚本与说明
│   ├── build_exe.py        # PyInstaller 打包脚本
│   └── README_PACKAGING.md # 打包说明
├── res/                    # 资源文件（图标等）
├── archive/                # 已归档的子包示例（markitdown-mcp、markitdown-ocr 等）
├── pytest.ini              # 测试配置（GUI-only 分支已忽略 archive/）
└── README.md               # 本文件（GUI-only 说明）
```

## 开发与测试

```bash
# 建议使用虚拟环境
py -3 -m venv .venv
.venv\Scripts\activate

# 运行 GUI（开发）
python gui/main.py

# 运行测试（archive/ 已被 pytest.ini 忽略）
pytest -q
```

## 主要运行/打包依赖（建议在打包前安装）

| 包 | 用途 |
| --- | --- |
| `magika` | 文件类型检测 / 内容识别 |
| `pdfplumber` / `pdfminer.six` | PDF 解析 |
| `mammoth` | DOCX → HTML/文本辅助 |
| `python-docx` | DOCX 处理 |
| `python-pptx` | PPTX 处理 |
| `openpyxl` / `xlrd` | Excel 处理 |
| `pillow` | 图片处理 |
| `markdownify` | HTML → Markdown |
| `tkinterdnd2` | 拖拽支持 |
| `pyinstaller` | 打包为 exe |

> 提示：为控制打包体积，请只安装所需的 extras，而不是全部依赖（`[all]`）。

## 重要变更说明（Breaking change）

- 本仓库已迁移为 GUI-only 分发：不再默认提供 CLI 命令或 pip 安装产生的 console script；顶层导出 `from markitdown import MarkItDown` 不再保持兼容。请使用 GUI 或在内部通过 `from markitdown._markitdown import MarkItDown` 调用内部 API（仅供开发/测试）。

## 许可证

MIT

## 作者

pingwang1994
