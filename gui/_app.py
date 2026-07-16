"""
MarkItDown GUI - 主应用类

包含 MarkItDownGUI 类，负责：
  - 窗口初始化与图标设置
  - 界面样式（ttkbootstrap 主题系统）
  - 界面构建（文件列表、输出目录、图片模式、日志、操作栏）
  - 文件选择、目录操作
  - 文件处理（多线程转换）
  - 对话框委托（关于、覆盖确认）
  - 亮暗主题切换与持久化
"""
import sys
import os
import subprocess
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path

from ttkbootstrap import Style
from ttkbootstrap.widgets.scrolled import ScrolledText

from _version import APP_VERSION
from _dialogs import show_about, ask_overwrite
from _config import load_config, save_config


# 文件后缀 → 可读类型名
_FILE_TYPE_MAP = {
    '.pdf':   'PDF 文档',
    '.docx':  'Word 文档',
    '.doc':   'Word 文档(旧版)',
    '.xlsx':  'Excel 表格',
    '.xls':   'Excel 表格(旧版)',
    '.pptx':  'PowerPoint 演示文稿',
    '.jpg':   'JPEG 图片',
    '.jpeg':  'JPEG 图片',
    '.png':   'PNG 图片',
    '.gif':   'GIF 图片',
    '.bmp':   'BMP 图片',
    '.html':  'HTML 网页',
    '.htm':   'HTML 网页',
    '.csv':   'CSV 数据',
    '.json':  'JSON 数据',
    '.xml':   'XML 数据',
    '.zip':   'ZIP 压缩包',
    '.epub':  'EPUB 电子书',
    '.wav':   'WAV 音频',
    '.mp3':   'MP3 音频',
    '.msg':   'Outlook 邮件',
    '.ipynb': 'Jupyter Notebook',
    '.rss':   'RSS 订阅',
    '.rtf':   'RTF 文档',
}


class MarkItDownGUI:

    # ── 主题对 ────────────────────────────────────────────────────────────────
    # 亮色 ↔ 暗色 映射表
    THEME_PAIRS = {
        'litera':   'darkly',
        'flatly':   'superhero',
        'cosmo':    'cyborg',
        'minty':    'solar',
        'pulse':    'vapor',
    }
    # 自动生成反向映射
    _REVERSE_PAIRS = {v: k for k, v in THEME_PAIRS.items()}
    # 全部可用主题列表
    ALL_THEMES = set(THEME_PAIRS.keys()) | set(_REVERSE_PAIRS.keys())

    # ── 初始化 ────────────────────────────────────────────────────────────────

    def __init__(self, root):
        self.root = root
        self.root.title(f"MarkItDown v{APP_VERSION}")

        window_width, window_height = 680, 500
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        self.root.geometry(
            f"{window_width}x{window_height}"
            f"+{(sw - window_width) // 2}+{(sh - window_height) // 2}"
        )
        self.root.resizable(False, False)

        self._set_window_icon()

        self.input_files      = []
        self.output_dir       = tk.StringVar()
        self.image_mode       = tk.StringVar(value='embed')  # 'file' | 'embed' | 'none'
        self.is_processing    = False
        self.last_output_file = None

        self._config = load_config()
        self.setup_styles()
        self.create_widgets()
        self.setup_drag_drop()

        # 绑定主题切换事件（刷新 tk 原生控件颜色）
        self.root.bind('<<ThemeChanged>>', self._on_theme_changed)

        # 窗口完全显示后再次应用图标，确保任务栏图标生效
        self.root.after(100, self._set_window_icon)

    # ── 图标 ──────────────────────────────────────────────────────────────────

    def _get_icon_path(self):
        """返回 ProductIcon.ico 的路径，打包/开发环境均适用；找不到则返回 None"""
        meipass = getattr(sys, '_MEIPASS', None)
        p = Path(meipass) / 'res' / 'ProductIcon.ico' if meipass \
            else Path(__file__).parent.parent / 'res' / 'ProductIcon.ico'
        return p if p.exists() else None

    def _set_window_icon(self):
        """设置窗口图标（标题栏 & 任务栏）"""
        try:
            if sys.platform == 'win32':
                import ctypes
                ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
                    'MarkItDown.GUI.App')

            icon_path = self._get_icon_path()
            if icon_path:
                self.root.iconbitmap(default=str(icon_path))
                try:
                    from PIL import Image, ImageTk
                    img32 = Image.open(str(icon_path)).resize(
                        (32, 32), Image.LANCZOS)
                    self._taskbar_photo = ImageTk.PhotoImage(img32)
                    self.root.wm_iconphoto(True, self._taskbar_photo)
                except Exception:
                    pass
        except Exception:
            pass

    # ── 样式 ──────────────────────────────────────────────────────────────────

    def setup_styles(self):
        """初始化 ttkbootstrap 主题，从配置加载上次主题"""
        theme_name = self._config.get('theme', 'litera')
        if theme_name not in self.ALL_THEMES:
            theme_name = 'litera'
        self.style = Style(theme=theme_name)
        self._update_color_aliases()

    def _update_color_aliases(self):
        """从 style.colors 刷新颜色别名（供对话框等外部模块使用）"""
        c = self.style.colors
        self.C_BG         = c.bg
        self.C_PANEL_BG   = c.light
        self.C_LABEL_FG   = c.fg
        self.C_ENTRY_BG   = c.inputbg
        self.C_BTN_SEL    = c.primary
        self.C_BTN_SEL_A  = c.primary  # 由主题 hover 自动处理
        self.C_BTN_RUN    = c.success
        self.C_BTN_RUN_A  = c.success
        self.C_BTN_OPEN   = c.warning
        self.C_BTN_OPEN_A = c.warning
        self.C_LOG_BG     = c.bg
        self.C_LOG_FG     = c.fg
        self.C_LINK       = c.info
        self.C_LINK_RED   = c.danger
        self.C_BORDER     = c.border
        self.C_HEADER_BG  = c.primary
        self.C_HEADER_FG  = c.get_foreground('primary')
        # 对浅色/深色背景取反色作为 select 文本色
        self._SELECT_FG = c.selectfg if hasattr(c, 'selectfg') else '#FFFFFF'

    def _on_theme_changed(self, event=None):
        """<<ThemeChanged>> 事件回调：刷新颜色别名 + tk 原生控件"""
        self._update_color_aliases()

        # 刷新 tk 原生控件（Listbox、ScrolledText 等）
        c = self.style.colors
        if hasattr(self, 'file_listbox'):
            self.file_listbox.configure(
                bg=c.inputbg, fg=c.fg,
                selectbackground=c.primary,
                selectforeground=self._SELECT_FG,
            )
        if hasattr(self, 'log_text'):
            self.log_text.text.configure(bg=c.bg, fg=c.fg)
            self.log_text.tag_configure('success', foreground=c.success)
            self.log_text.tag_configure('error',   foreground=c.danger)
            self.log_text.tag_configure('info',    foreground=c.warning)
            self.log_text.tag_configure('arrow',   foreground=c.warning)
            self.log_text.tag_configure('complete', foreground=c.info)
            self.log_text.tag_configure('normal',  foreground=c.fg)

        # 持久化
        current = self.style.theme_use()
        self._config['theme'] = current
        save_config(self._config)

    # ── 界面构建 ──────────────────────────────────────────────────────────────

    def create_widgets(self):
        """构建主界面所有控件"""
        mf = ttk.Frame(self.root, padding="14 10 14 6")
        mf.pack(fill=tk.BOTH, expand=True)
        mf.columnconfigure(1, weight=1)
        row = 0

        # 标题行：选择待处理文件 + 主题切换按钮
        header_frame = ttk.Frame(mf)
        header_frame.grid(row=row, column=0, columnspan=2,
                          sticky=(tk.W, tk.E), pady=4)
        header_frame.columnconfigure(0, weight=1)
        ttk.Label(header_frame, text="选择待处理文件:",
                  font=('Microsoft YaHei UI', 9)).grid(
            row=0, column=0, sticky=tk.W)

        self.theme_btn = ttk.Button(
            header_frame, text="🌙",
            command=self.toggle_theme,
            width=3,
        )
        self.theme_btn.grid(row=0, column=1, sticky=tk.E, padx=(0, 2))
        row += 1

        # 文件列表 + 操作按钮
        ff = ttk.Frame(mf)
        ff.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=2)
        ff.columnconfigure(0, weight=1)

        self.file_listbox = tk.Listbox(
            ff, height=5, font=('Microsoft YaHei UI', 9),
            relief='flat', borderwidth=0,
        )
        self.file_listbox.grid(
            row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 6))

        btn_frame = ttk.Frame(ff)
        btn_frame.grid(row=0, column=1, sticky=tk.N)
        ttk.Button(btn_frame, text="添加文件",
                   command=self.select_files,
                   bootstyle="primary-outline",
                   width=10).pack(pady=2)
        ttk.Button(btn_frame, text="删除选中",
                   command=self.remove_selected_files,
                   bootstyle="primary-outline",
                   width=10).pack(pady=2)
        ttk.Button(btn_frame, text="清空列表",
                   command=self.clear_file_list,
                   bootstyle="primary-outline",
                   width=10).pack(pady=2)

        ff.rowconfigure(0, weight=1)
        row += 1

        # 选择保存位置
        ttk.Label(mf, text="选择保存位置:",
                  font=('Microsoft YaHei UI', 9)).grid(
            row=row, column=0, sticky=tk.W, pady=4, padx=(0, 8))
        sf = ttk.Frame(mf)
        sf.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=4)
        sf.columnconfigure(0, weight=1)
        ttk.Entry(sf, textvariable=self.output_dir, state='readonly').grid(
            row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 6))
        ttk.Button(sf, text="保存位置",
                   command=self.select_output_dir,
                   bootstyle="primary-outline",
                   width=10).grid(row=0, column=1)
        row += 1

        # 图片处理方式
        ttk.Label(mf, text="图片处理方式:",
                  font=('Microsoft YaHei UI', 9)).grid(
            row=row, column=0, sticky=tk.W, pady=4, padx=(0, 8))
        rf = ttk.Frame(mf)
        rf.grid(row=row, column=1, sticky=tk.W, pady=4)
        ttk.Radiobutton(rf, text="提取为文件（推荐）",
                        variable=self.image_mode,
                        value='file').pack(side=tk.LEFT, padx=(0, 12))
        ttk.Radiobutton(rf, text="嵌入 base64",
                        variable=self.image_mode,
                        value='embed').pack(side=tk.LEFT, padx=(0, 12))
        ttk.Radiobutton(rf, text="忽略图片",
                        variable=self.image_mode,
                        value='none').pack(side=tk.LEFT)
        row += 1

        # 分割线
        ttk.Separator(mf, orient='horizontal').grid(
            row=row, column=0, columnspan=2,
            sticky=(tk.W, tk.E), pady=6)
        row += 1

        # 操作按钮
        bf = ttk.Frame(mf)
        bf.grid(row=row, column=0, columnspan=2, pady=4)
        self.process_button = ttk.Button(
            bf, text="▶  开始处理",
            command=self.start_processing,
            bootstyle="success",
            width=14)
        self.process_button.pack(side=tk.LEFT, padx=6)
        ttk.Button(bf, text="📂  打开输出目录",
                   command=self.open_output_dir,
                   bootstyle="warning",
                   width=14).pack(side=tk.LEFT, padx=6)
        self.open_doc_button = ttk.Button(
            bf, text="📄  打开文档",
            command=self.open_last_document,
            bootstyle="warning",
            width=14,
            state='disabled')
        self.open_doc_button.pack(side=tk.LEFT, padx=6)
        row += 1

        # 日志区域
        ttk.Label(mf, text="处理日志:",
                  font=('Microsoft YaHei UI', 9)).grid(
            row=row, column=0, sticky=tk.NW, pady=(8, 2), padx=(0, 8))
        c = self.style.colors
        self.log_text = ScrolledText(
            mf, height=8, wrap=tk.WORD,
            font=('Consolas', 9),
            autohide=True,
            state='disabled')
        self.log_text.grid(
            row=row, column=1,
            sticky=(tk.W, tk.E, tk.N, tk.S), pady=(8, 2))
        mf.rowconfigure(row, weight=1)
        for tag, color in [('success', c.success),
                           ('error',   c.danger),
                           ('info',    c.warning),
                           ('arrow',   c.warning),
                           ('complete', c.info),
                           ('normal',  c.fg)]:
            self.log_text.tag_configure(tag, foreground=color)
        row += 1

        # 底部链接
        lf = ttk.Frame(mf)
        lf.grid(row=row, column=0, columnspan=2,
                pady=(4, 2), sticky=(tk.W, tk.E))
        lbl = ttk.Label(lf, text="软件教程及注意事项>>",
                        foreground=c.info,
                        cursor='hand2',
                        font=('Microsoft YaHei UI', 9, 'underline'))
        lbl.pack(side=tk.LEFT)
        lbl.bind('<Button-1>', lambda e: self.show_about())

        # 应用初始主题颜色到 tk 原生控件
        self._on_theme_changed()

    # ── 主题切换 ──────────────────────────────────────────────────────────────

    def toggle_theme(self):
        """在亮色和暗色主题间切换"""
        current = self.style.theme_use()
        # 在当前映射表中查找配对
        if current in self.THEME_PAIRS:
            new_theme = self.THEME_PAIRS[current]
        elif current in self._REVERSE_PAIRS:
            new_theme = self._REVERSE_PAIRS[current]
        else:
            # 不在映射中则切到默认暗/亮
            new_theme = 'darkly' if current in ('litera',) else 'litera'
        self.style.theme_use(new_theme)
        # 主题切换事件会自动触发 _on_theme_changed 持久化

    def _update_theme_btn_text(self):
        """根据当前主题切换按钮图标"""
        current = self.style.theme_use()
        is_dark = current in ('darkly', 'superhero', 'cyborg', 'solar', 'vapor')
        self.theme_btn.config(text="☀️" if is_dark else "🌙")

    # ── 日志 ──────────────────────────────────────────────────────────────────

    def log_message(self, message):
        self.log_text.text.configure(state='normal')
        s = message.strip()
        if   s.startswith(('✓', '✅')):                      tag = 'success'
        elif s.startswith(('✗', '❌')):                      tag = 'error'
        elif s.startswith('[') and ']' in s:                  tag = 'info'
        elif s.startswith(('→', '  →')):                     tag = 'arrow'
        elif s.startswith(('处理完成', '开始处理')):          tag = 'complete'
        else:                                                  tag = 'normal'
        self.log_text.insert(tk.END, message + '\n', tag)
        self.log_text.see(tk.END)
        self.log_text.text.configure(state='disabled')

    # ── 文件选择 & 目录操作 ───────────────────────────────────────────────────

    def select_files(self):
        filetypes = [
            ('所有支持的文件',
             '*.pdf *.docx *.doc *.xlsx *.pptx *.jpg *.jpeg *.png '
             '*.html *.csv *.json *.xml *.zip *.epub'),
            ('PDF 文件', '*.pdf'),
            ('Word 文件', '*.docx *.doc'),
            ('Excel 文件', '*.xlsx'),
            ('PowerPoint 文件', '*.pptx'),
            ('图片文件', '*.jpg *.jpeg *.png'),
            ('HTML 文件', '*.html'),
            ('所有文件', '*.*'),
        ]
        files = filedialog.askopenfilenames(
            title="选择要转换的文件", filetypes=filetypes)
        if not files:
            return
        for f in files:
            if f not in self.input_files:
                self.input_files.append(f)
        self.update_file_listbox()
        if not self.output_dir.get() and self.input_files:
            self.output_dir.set(str(Path(self.input_files[0]).parent))

    def select_output_dir(self):
        d = filedialog.askdirectory(title="选择保存位置")
        if d:
            self.output_dir.set(d)

    def update_file_listbox(self):
        """更新文件列表框的显示"""
        self.file_listbox.delete(0, tk.END)
        for f in self.input_files:
            name = Path(f).name
            if len(name) > 50:
                name = name[:47] + "..."
            self.file_listbox.insert(tk.END, name)

    def remove_selected_files(self):
        """删除选中的文件"""
        selection = self.file_listbox.curselection()
        if not selection:
            return
        for index in reversed(selection):
            del self.input_files[index]
        self.update_file_listbox()

    def clear_file_list(self):
        """清空文件列表"""
        self.input_files.clear()
        self.output_dir.set('')
        self.update_file_listbox()

    def setup_drag_drop(self):
        """设置拖拽支持（Windows 平台）"""
        if sys.platform != 'win32':
            return
        try:
            from tkinterdnd2 import DND_FILES
            self.file_listbox.drop_target_register(DND_FILES)
            self.file_listbox.dnd_bind('<<Drop>>', self._handle_drop)
            self.root.drop_target_register(DND_FILES)
            self.root.dnd_bind('<<Drop>>', self._handle_drop)
        except Exception:
            pass

    def _handle_drop(self, event):
        """处理文件拖拽事件"""
        try:
            files = self.root.splitlist(event.data)
            added = False
            for file_path in files:
                ext = Path(file_path).suffix.lower()
                if ext in _FILE_TYPE_MAP or ext in ('.txt', '.md', '.rtf'):
                    if file_path not in self.input_files:
                        self.input_files.append(file_path)
                        added = True
            if added:
                self.update_file_listbox()
                if not self.output_dir.get() and self.input_files:
                    self.output_dir.set(str(Path(self.input_files[0]).parent))
        except Exception as e:
            self.log_message(f"拖拽文件失败: {e}")

    def open_output_dir(self):
        out = self.output_dir.get()
        if not out:
            messagebox.showwarning("警告", "请先选择保存位置！")
            return
        if not os.path.exists(out):
            messagebox.showerror("错误", f"目录不存在：{out}")
            return
        try:
            if sys.platform == 'win32':
                if self.last_output_file and os.path.exists(self.last_output_file):
                    subprocess.run(['explorer', '/select,', self.last_output_file])
                else:
                    os.startfile(out)
            elif sys.platform == 'darwin':
                if self.last_output_file and os.path.exists(self.last_output_file):
                    subprocess.run(['open', '-R', self.last_output_file])
                else:
                    subprocess.run(['open', out])
            else:
                os.system(f'xdg-open "{out}"')
        except Exception as e:
            messagebox.showerror("错误", f"无法打开目录：{e}")

    # ── 文件处理 ──────────────────────────────────────────────────────────────

    def start_processing(self):
        if not self.input_files:
            messagebox.showwarning("警告", "请先选择要处理的文件！")
            return
        if not self.output_dir.get():
            messagebox.showwarning("警告", "请选择保存位置！")
            return
        self.process_button.configure(state='disabled')
        self.is_processing = True
        t = threading.Thread(target=self.process_files, daemon=True)
        t.start()

    def process_files(self):
        """后台线程：批量转换文件"""
        self._overwrite_all = False
        self._skip_all      = False
        try:
            total = len(self.input_files)
            self.log_message(f"开始处理 {total} 个文件...")
            for i, file_path in enumerate(self.input_files, 1):
                if not self.is_processing:
                    self.log_message("处理已取消")
                    break
                ext = Path(file_path).suffix.lower()
                file_type = _FILE_TYPE_MAP.get(ext, f'{ext.upper()} 文件')
                self.log_message(
                    f"[{i}/{total}] 正在转换: "
                    f"{Path(file_path).name} ({file_type})")
                self.convert_file(file_path)
                self.log_message(f"✓ 转换成功: {Path(file_path).stem}.md")
            self.log_message(f"\n处理完成！共处理 {total} 个文件。")
        except Exception as e:
            self.log_message(f"\n✗ 处理失败: {e}")
        finally:
            self.root.after(0, self.processing_complete)

    def convert_file(self, file_path):
        """转换单个文件并写入输出目录"""
        try:
            stem = Path(file_path).stem
            ext  = Path(file_path).suffix.lower()

            if ext == '.doc':
                self.log_message("  ✗ 暂不支持 .doc 格式")
                self.log_message(
                    "  → 请使用 Microsoft Word 或 LibreOffice 手动转换为 .docx")
                self.log_message(
                    "  → 转换步骤：打开 .doc 文件 → 另存为 .docx → 重新处理")
                raise RuntimeError("不支持的格式：.doc 文件。请先转换为 .docx")

            from markitdown import MarkItDown
            self.log_message("  → 初始化 MarkItDown 转换器...")

            convert_kwargs = {}
            mode = self.image_mode.get()
            if ext in ('.docx',):
                if mode == 'file':
                    images_dir = Path(self.output_dir.get()) / f"{stem}_images"
                    convert_kwargs['docx_images_dir'] = str(images_dir)
                elif mode == 'embed':
                    convert_kwargs['docx_embed_images'] = True
            elif ext in ('.pptx',):
                if mode == 'file':
                    images_dir = Path(self.output_dir.get()) / f"{stem}_images"
                    convert_kwargs['pptx_images_dir'] = str(images_dir)
                elif mode == 'embed':
                    convert_kwargs['pptx_embed_images'] = True
            elif ext in ('.epub',):
                if mode == 'file':
                    images_dir = Path(self.output_dir.get()) / f"{stem}_images"
                    convert_kwargs['epub_images_dir'] = str(images_dir)
                elif mode == 'embed':
                    convert_kwargs['epub_embed_images'] = True
            else:
                if mode == 'embed':
                    convert_kwargs['keep_data_uris'] = True

            result = MarkItDown().convert(file_path, **convert_kwargs)
            output_file = Path(self.output_dir.get()) / f"{stem}.md"
            self.log_message(f"  → 保存结果到: {output_file}")
            if output_file.exists() and not self._ask_overwrite(output_file.name):
                self.log_message(f"  ✗ 已跳过: {output_file.name}")
                return
            output_file.write_text(result.text_content, encoding='utf-8')
            self.last_output_file = str(output_file)
        except ImportError as e:
            raise RuntimeError(f"模块导入失败: {e}")
        except Exception as e:
            raise RuntimeError(f"转换文件 {file_path} 失败: {e}")

    def processing_complete(self):
        self.is_processing = False
        self.process_button.configure(state='normal')
        if (len(self.input_files) == 1
                and self.last_output_file
                and os.path.exists(self.last_output_file)):
            self.open_doc_button.configure(state='normal')
        else:
            self.open_doc_button.configure(state='disabled')

    # ── 对话框（委托给 _dialogs 模块）────────────────────────────────────────

    def _ask_overwrite(self, filename):
        return ask_overwrite(self, filename)

    def show_about(self):
        show_about(self)

    def open_last_document(self):
        """打开最后转换的文档"""
        if not self.last_output_file or not os.path.exists(self.last_output_file):
            messagebox.showwarning("警告", "没有可打开的文档！")
            return
        try:
            if sys.platform == 'win32':
                os.startfile(self.last_output_file)
            elif sys.platform == 'darwin':
                subprocess.run(['open', self.last_output_file])
            else:
                subprocess.run(['xdg-open', self.last_output_file])
        except Exception as e:
            messagebox.showerror("错误", f"无法打开文档：{e}")

    def show_contact(self):
        messagebox.showinfo(
            "联系我们",
            "如有问题或建议，请访问：\n\n"
            "GitHub: https://github.com/microsoft/markitdown\n\n"
            "或提交 Issue 获取帮助。")
