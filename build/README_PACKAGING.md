# MarkItDown GUI 打包指南

本文档说明如何将 MarkItDown GUI 应用程序打包为 Windows 可执行文件（.exe）。

## 📋 前置要求

- Python 3.11 或更高版本
- PyInstaller（会自动安装）

> **注意**：如果电脑上同时安装了 Python 2.7 和 Python 3.x，请使用 `py -3` 命令代替 `python` 或 `py`。
>
> 例如：
>
> - ❌ `python -m venv .venv`
> - ✅ `py -3 -m venv .venv`
> - ❌ `pip install ...`
> - ✅ `py -3 -m pip install ...`

## 🚀 快速开始

### 1. 创建虚拟环境

```bash
# 在项目根目录创建虚拟环境
py -3 -m venv .venv

# Windows 激活虚拟环境
.venv\Scripts\activate

# macOS/Linux 激活虚拟环境
source .venv/bin/activate
```

> **重要**：所有操作都应在激活的虚拟环境中进行，避免污染全局 Python 环境。

### 2. 安装依赖

**重要提示**：为了控制打包体积，建议只安装需要的功能模块，而不是使用 `[all]`。

```bash
# 升级 pip
py -3 -m pip install --upgrade pip

# 推荐：只安装需要的功能（示例：DOCX + PPTX + XLSX + PDF）
py -3 -m pip install -e packages/markitdown[docx,pptx,xlsx,pdf]

# 或者：安装所有功能（会导致打包体积增大到 300MB+）
# py -3 -m pip install -e packages/markitdown[all]

# 安装 GUI 所需依赖
py -3 -m pip install pyinstaller tkinterdnd2 pillow
```

### 3. 验证环境

```bash
# 检查 Python 版本
py -3 --version

# 检查已安装的包
py -3 -m pip list
```

确保没有意外安装大型科学计算库（如 `scipy`、`scikit-learn`、`marker-pdf`），这些会导致打包体积暴增。

### 4. 执行打包

```bash
# 运行打包脚本
py build/build_exe.py
```

打包完成后，生成的 exe 文件位于 `dist/` 目录。

## 📦 打包输出

- **位置**：`dist/MarkItDown_v{版本号}_{时间戳}.exe`
- **大小**：约 150-200 MB（包含所有转换器依赖）
- **模式**：单文件模式，无需安装 Python，直接运行

## ⚠️ 常见问题

### 问题 1：打包体积过大（>300MB）

**原因**：

1. 使用了 `packages/markitdown[all]` 安装了所有可选依赖
2. `pandas` 和 `numpy` 会显著增加体积（约 +200MB）
3. 其他大型库如 `scipy`、`sklearn`、`torch` 等

**解决**：

```bash
# 方法 1：重建虚拟环境，只安装需要的功能
deactivate
rmdir /s .venv
py -3 -m venv .venv
.venv\Scripts\activate
py -3 -m pip install --upgrade pip
py -3 -m pip install -e packages/markitdown[docx,pptx,xlsx,pdf]  # 只选需要的
py -3 -m pip install pyinstaller tkinterdnd2 pillow
py -3 build/build_exe.py

# 方法 2：如果已安装 [all]，卸载不必要的大库
py -3 -m pip uninstall -y scipy scikit-learn torch tensorflow
py -3 build/build_exe.py
```

**预防**：始终根据实际需求选择依赖，避免使用 `[all]`。

### 问题 2：PermissionError - 无法删除 dist 目录

**原因**：之前生成的 exe 文件正在被使用或未关闭。

**解决**：

```bash
# 方法 1：关闭所有使用该 exe 的程序后重试
py -3 build/build_exe.py

# 方法 2：手动删除 dist 目录
rmdir /s dist
py -3 build/build_exe.py
```

**注意**：构建脚本会自动重试 3 次，每次间隔 1 秒等待文件释放。

### 问题 3：打包失败 - 缺少依赖

**原因**：依赖缺失或版本冲突。

**解决**：

```bash
# 清理虚拟环境，重新安装
deactivate                    # 退出虚拟环境
rmdir /s .venv                # 删除虚拟环境（macOS/Linux: rm -rf .venv）
py -3 -m venv .venv          # 重新创建
.venv\Scripts\activate       # 激活（macOS/Linux: source .venv/bin/activate）
py -3 -m pip install --upgrade pip
py -3 -m pip install -e packages/markitdown[all]
py -3 -m pip install pyinstaller tkinterdnd2 pillow
py -3 build/build_exe.py
```

## 🔍 核心依赖清单

打包前请确认以下包**已安装**：

- ✅ markitdown（主包，包含所有转换器）
- ✅ python-docx（DOCX 支持）
- ✅ openpyxl（XLSX 支持）
- ✅ pptx（PPTX 支持）
- ✅ pdfplumber（PDF 支持）
- ✅ mammoth（DOCX HTML 转换）
- ✅ markdownify（HTML 转 Markdown）
- ✅ pillow（图片处理）
- ✅ tkinterdnd2（拖拽支持）
- ✅ pyinstaller（打包工具）
- ✅ magika（文件类型检测）

以下包**不应存在**（会导致体积过大）：

- ❌ matplotlib
- ❌ jupyter
- ❌ notebook
- ❌ scipy（除非需要音频转录）
- ❌ scikit-learn（除非需要音频转录）

检查命令：

```bash
py -3 -m pip list | findstr /i "matplotlib jupyter scipy scikit"
```

如果输出为空，说明环境干净。

## 💡 最佳实践

1. **始终使用虚拟环境**

   ```bash
   # 每次打包前激活虚拟环境
   .venv\Scripts\activate
   ```

2. **定期清理虚拟环境**

   ```bash
   # 如果发现包体积异常，重建虚拟环境
   deactivate
   rm -rf .venv
   py -3 -m venv .venv
   .venv\Scripts\activate
   py -3 -m pip install -r gui_requirements.txt
   py -3 -m pip install pyinstaller
   ```

3. **记录打包日志**

   ```bash
   # 保存打包输出到文件
   py build/build_exe.py > build_log.txt 2>&1
   ```

4. **测试生成的 exe**
   ```bash
   # 运行生成的 exe，验证功能
   dist\MarkItDown_v*.exe
   ```

## 📝 版本管理

版本号定义在 `packages/markitdown/src/markitdown/__about__.py`：

```python
__version__ = "0.1.6b2"
```

修改版本号后重新打包即可。

## 🎯 快速开始流程

| 步骤             | 命令                                                                             |
| ---------------- | -------------------------------------------------------------------------------- |
| 1. 创建虚拟环境  | `py -3 -m venv .venv`                                                            |
| 2. 激活虚拟环境  | `.venv\Scripts\activate`                                                         |
| 3. 安装主包      | `py -3 -m pip install -e packages/markitdown[docx,pptx,xlsx,pdf]` # 根据需要选择 |
| 4. 安装 GUI 依赖 | `py -3 -m pip install pyinstaller tkinterdnd2 pillow`                            |
| 5. 执行打包      | `py -3 build/build_exe.py`                                                       |

**依赖选择指南**：

- `docx` - Word 文档转换
- `pptx` - PowerPoint 演示文稿转换
- `xlsx` - Excel 表格转换（会引入 pandas，增加 ~200MB）
- `pdf` - PDF 文档转换
- `audio-transcription` - 音频转录（会引入 scipy，增加 ~100MB）

遵循以上流程，可确保打包体积合理并生成可用的 MarkItDown GUI 应用程序。
