# MarkItDown

> 将各种文档/文件自动转换为结构化 Markdown 的工具包与库（支持 PDF / Word / Excel / PowerPoint / 图片 / EPUB / ZIP / 网页 / RSS / Jupyter Notebook / 音频 等）。

版本: `0.1.6b2`（见 `src/markitdown/__about__.py`）

- 适合谁用：需要把大量富格式或二进制文档快速转为 Markdown 用于 LLM、笔记/知识库导入、静态站点或文本分析的开发者与工程团队。
- 最短安装（30 秒上手）：

```bash
pip install markitdown
# 如果需要 GUI / 文档格式的可选依赖，例如 docx/pptx/pdf/xlsx/image：
# pip install "markitdown[gui]"
# 安装多个 extras：pip install "markitdown[gui,xlsx-pandas]"
# 从源码安装（开发）：
# git clone https://github.com/microsoft/markitdown.git
# cd markitdown
# pip install -e .
```

官方资源
- 源码 / 文档: https://github.com/microsoft/markitdown#readme
- 提交 Issue: https://github.com/microsoft/markitdown/issues

---

## ✨ 项目亮点
- 支持广泛的输入格式：PDF、DOCX、DOC、XLSX、XLS、PPTX、图片（JPEG/PNG 等）、EPUB、ZIP、HTML、RSS、YouTube 页面、Jupyter Notebook、音频等。
- 插件系统：通过 `markitdown.plugin` entry points 扩展功能（仓库中有示例插件 `archive/markitdown-ocr`）。
- 带桌面 GUI（Windows）与打包脚本（见 `gui/` 与 `build/`）。
- 易用的 Python API：直接调用 `MarkItDown().convert(...)` 获取 Markdown 结果。

---

## 🚀 快速开始 — Python API

最短可运行示例：

```python
from markitdown import MarkItDown

md = MarkItDown()
result = md.convert("document.pdf")
print(result.text_content)
```

高级示例（启用插件并使用 LLM 进行图片 OCR / 描述）：

```python
from markitdown import MarkItDown
from openai import OpenAI

md = MarkItDown(enable_plugins=True, llm_client=OpenAI(), llm_model="gpt-4o")
res = md.convert("document_with_images.pdf")
print(res.text_content)
```

关于图片输出策略（可选参数，示例来自 GUI 实现）：
- `docx_images_dir` / `pptx_images_dir` / `epub_images_dir`: 将嵌入图片提取为文件并写入指定目录
- `docx_embed_images` / `pptx_embed_images` / `epub_embed_images`: 将图片以 data URI 嵌入 Markdown
- `keep_data_uris`: 对 HTML / 其他格式保留 data URI

（这些参数在 `gui/_app.py` 中有实际使用，可以直接参照该实现。）

---

## ⚙️ 命令行与 GUI

- CLI: pyproject 中定义了一个 console script：`markitdown = markitdown.__main__:main`。安装后如存在该入口，可能会暴露 `markitdown` 命令（仓库内 `archive/markitdown-cli` 有一个示例实现）。不同发行版/分支可能对 CLI 的实际安装和入口略有差异。

示例（若已安装 CLI）：

```bash
markitdown document.pdf --use-plugins --llm-client openai --llm-model gpt-4o
```

- GUI (开发模式运行)：

```bash
python gui/main.py
# 或者运行打包生成的可执行文件：build/ 或 dist/ 目录下可能存在 MarkItDown_v*.exe
```

---

## 📦 可选依赖（extras）
在 `pyproject.toml` 中定义了若干可选依赖组，常见的有：

- `gui`（最小集合，支持 docx/pptx/pdf/xlsx/image/html）：
  `python-pptx`, `mammoth~=1.11.0`, `openpyxl`, `lxml`, `pdfminer.six>=20251230`, `pdfplumber>=0.11.9`, `python-docx`, `pillow`, `markdownify`
- `xlsx-pandas`：`pandas`
- `audio`：`pydub`, `SpeechRecognition`
- `az-doc-intel`：`azure-ai-documentintelligence`, `azure-identity`
- `youtube-transcription`：`youtube-transcript-api`

示例：
```bash
pip install "markitdown[gui,az-doc-intel]"
```

---

## 🔧 支持的输入类型（摘自源码）
- Plain text, HTML, RSS, Wikipedia 页面, YouTube 页面
- Jupyter Notebook (`.ipynb`)
- PDF、DOCX、DOC、PPTX、XLSX、XLS
- 图片（JPEG/PNG 等）与音频格式
- Outlook `.msg`、EPUB、CSV、ZIP

（具体见 `src/_markitdown.py` 中注册的 converters 与 `src/converters/` 目录）

---

## 📁 仓库快速目录
- `src/` — 核心实现（`_markitdown.py`, 各 `converters/`, `converter_utils/` 等）
- `gui/` — 桌面 GUI 源码（Windows 环境）
- `build/` — 打包说明与 PyInstaller/Exe 配置
- `archive/` — 若干已归档的子包示例（`markitdown-mcp`, `markitdown-ocr`, `markitdown-sample-plugin`, ...）

---

## 🧪 开发与测试（简要）
- 建议使用虚拟环境，要求 Python >= 3.10（见 `pyproject.toml`）。

快速安装（开发）：
```bash
python -m venv .venv
source .venv/bin/activate   # macOS / Linux
.\.venv\Scripts\activate  # Windows PowerShell / cmd
pip install -e .
# 如果使用 GUI/extras：pip install -e .[gui]
```

运行测试：仓库使用 Hatch/pytest 等工具，常见命令：
```bash
hatch test    # 如果已安装并配置 hatch
pytest        # 或直接运行 pytest
```

---

## ⚠️ 安全提示
MarkItDown 在当前进程权限下执行 I/O（与 `open()`、`requests.get()` 类似），会访问该进程可以访问的资源。不要在不受信任或可能包含恶意代码的环境中对未验证内容运行转换；对外部输入请先做清理与隔离。

---

## 🤝 贡献
欢迎通过 Fork + PR 的方式贡献代码。遇到问题或想要讨论的功能，请提交 Issue：
https://github.com/microsoft/markitdown/issues

贡献前建议阅读仓库中的 `archive/` 示例插件和 `build/README_PACKAGING.md` 以了解打包/插件约定。

---

## 📝 许可证
MIT（见 `pyproject.toml` 中的 license 字段）

---

## 注记 / 待补充
- pyproject 中声明了 `markitdown` 的 console script（`markitdown.__main__:main`），但仓库源码中主包 `src/markitdown/` 当前未见 `__main__.py` 的实现（仓库中存在 `archive/markitdown-cli` 作为参考实现）。如果你要将 CLI 入口标准化到 `src/markitdown/__main__.py`，我可以帮你：
  - 迁移 `archive/markitdown-cli/__main__.py` 的实现到 `src/markitdown/__main__.py`，并添加相应的测试；或
  - 把 CLI 文档改为引用 `archive/` 下的实现（保留历史）。

如果你希望我直接把这份 README 写入仓库（覆盖当前 README.md），我已经为你准备好文件并将其写入根目录。如果需要更改首屏文案、添加 badges（例如 GitHub Actions / PyPI）、或按子包拆分 README，请告诉我需要的风格和要点，我会更新。 
