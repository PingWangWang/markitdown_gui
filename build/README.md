# MarkItDown GUI 打包指南

## �️ 环境要求

- Windows 10/11 x64
- Python 3.11 或以上（建议 3.12+），需加入 PATH
- 网络畅通（首次安装依赖时需要）

---

## 🧰 推荐：创建并激活虚拟环境（强烈建议）

在开发或打包时建议使用虚拟环境，避免污染系统 Python 以及减少依赖冲突。

Windows (PowerShell):

```powershell
# 在仓库根目录创建虚拟环境
py -3 -m venv .venv
# 临时放宽执行策略（如果提示无法运行 Activate.ps1）
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
# 激活
.\.venv\Scripts\Activate.ps1
# 更新 pip（可选但推荐）
python -m pip install --upgrade pip
```

激活虚拟环境后，后续的 python / pip 调用都会作用于该虚拟环境。

---

## 📦 第一步：安装依赖

在新电脑上首次打包前，需安装以下所有 Python 库。推荐在已激活的虚拟环境中执行安装。

我们在仓库中提供了一个依赖清单文件：`requirements.txt`，可以通过下面的命令一次性安装所有依赖：

```bash
# 在仓库根目录，并且虚拟环境已激活的情况下：
pip install -r requirements.txt
```
---

## 🚀 第二步：执行打包（在虚拟环境中）

在仓库根目录，且虚拟环境已激活的情况下运行：

```bash
cd d:\Code\markitdown_fork
# 推荐：使用虚拟环境里的 python 来执行打包脚本
python build\build_exe.py
# 或者（兼容旧写法）
py -3 build\build_exe.py
```

> **注意**：若终端中文乱码，请先执行：
>
> ```powershell
> $OutputEncoding = [Console]::OutputEncoding = [System.Text.Encoding]::UTF8
> ```

---

## 📌 在开发环境直接运行 GUI（无需打包）

如果只是想在开发/调试时直接运行 GUI：

```bash
# 在仓库根目录并激活虚拟环境后：
python gui\main.py
# 或（Windows）
py -3 gui\main.py
```

---

## 📂 第三步：获取产物

打包完成后，exe 在项目根目录的 `dist/` 下：

```
d:\Code\markitdown_fork\
├── build\                 ← 临时构建文件（打包后可删除）
└── dist\
    └── MarkItDown_v0.1.6b2_20260424-xxxxxx.exe  ← 直接发给对方即可
```

**单文件模式，对方无需安装 Python，直接运行 exe 即可。**

---
