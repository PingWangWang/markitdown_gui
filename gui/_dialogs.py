"""
MarkItDown GUI - 对话框组件

包含：
  - show_about(app)          关于窗口
  - ask_overwrite(app, filename)  文件覆盖确认窗口
"""
import threading
import tkinter as tk
import webbrowser

from _version import APP_VERSION


def show_about(app):
    """显示关于信息（使用 ttkbootstrap 主题色）"""
    dlg = tk.Toplevel(app.root)
    dlg.overrideredirect(True)
    dlg.configure(bg=app.C_BG)
    dlg.resizable(False, False)

    c = app.style.colors

    # 标题栏
    header = tk.Frame(dlg, bg=app.C_HEADER_BG, height=46)
    header.pack(fill=tk.X)
    header.pack_propagate(False)
    tk.Label(header, text=f"关于  MarkItDown v{APP_VERSION}",
             bg=app.C_HEADER_BG, fg=app.C_HEADER_FG,
             font=('Microsoft YaHei UI', 12, 'bold')).pack(
                 side=tk.LEFT, padx=16, pady=8)

    # 内容区
    body = tk.Frame(dlg, bg=app.C_BG, padx=24, pady=16)
    body.pack(fill=tk.BOTH)

    sections = [
        ("支持格式", [
            "文档：PDF、Word(DOCX/PPTX)、Excel(XLSX)、HTML、EPUB、"
            "RTF、Outlook 邮件、Jupyter Notebook",
            "数据：CSV、JSON、XML",
            "图片：JPEG、PNG、GIF、BMP（含 EXIF 和 OCR）",
            "音频：WAV、MP3（含音频转录）",
            "其他：ZIP 压缩包、RSS 订阅",
        ]),
        ("功能", [
            "批量文件转换为 Markdown",
            "支持图片提取、嵌入或忽略",
            "简单易用的图形界面，支持拖拽导入文件",
        ]),
        ("注意事项", [
            ".doc 旧版 Word 格式：请使用 Microsoft Word 或 "
            "LibreOffice 手动转为 .docx 后重新处理",
            "转换大文件时请耐心等待，程序不会卡死",
            "输出的 Markdown 文件保存在所选的保存位置目录中",
            "本程序为独立可执行文件，无需安装 Python 或任何依赖",
        ]),
        ("相关工具", [
            "Markdown 转 Word: https://markdowntoword.io/zh",
        ]),
        ("项目信息", [
            "官方项目: https://github.com/microsoft/markitdown",
        ]),
    ]

    for title, items in sections:
        tk.Label(body, text=title, bg=app.C_BG, fg=c.primary,
                 font=('Microsoft YaHei UI', 10, 'bold')).pack(
                     anchor=tk.W, pady=(8, 2))
        for item in items:
            if 'http://' in item or 'https://' in item:
                url_start = item.find('http')
                prefix = item[:url_start].rstrip(': ').rstrip()
                url = item[url_start:]

                item_frame = tk.Frame(body, bg=app.C_BG)
                item_frame.pack(fill=tk.X, anchor=tk.W, pady=1)

                txt = f"  • {prefix}: " if prefix else "  • "
                tk.Label(item_frame, text=txt,
                         bg=app.C_BG, fg=app.C_LABEL_FG,
                         font=('Microsoft YaHei UI', 9),
                         justify='left').pack(side=tk.LEFT, anchor=tk.W)

                link_label = tk.Label(
                    item_frame, text=url,
                    bg=app.C_BG, fg=c.info,
                    font=('Microsoft YaHei UI', 9, 'underline'),
                    cursor='hand2', justify='left')
                link_label.pack(side=tk.LEFT, anchor=tk.W)
                link_label.bind('<Button-1>',
                                lambda e, u=url: webbrowser.open(u))
                link_label.bind('<Enter>',
                                lambda e: e.widget.config(fg=c.primary))
                link_label.bind('<Leave>',
                                lambda e: e.widget.config(fg=c.info))
            else:
                tk.Label(body, text=f"  • {item}",
                         bg=app.C_BG, fg=app.C_LABEL_FG,
                         font=('Microsoft YaHei UI', 9),
                         justify='left').pack(anchor=tk.W, pady=1)

    # 底部
    tk.Frame(dlg, bg=app.C_BORDER, height=1).pack(fill=tk.X, pady=(8, 0))
    btn_frame = tk.Frame(dlg, bg=app.C_BG, pady=10)
    btn_frame.pack()
    ok_btn = tk.Button(btn_frame, text="确  定", width=10,
                       bg=c.primary, fg='#FFFFFF', relief='flat',
                       font=('Microsoft YaHei UI', 9, 'bold'),
                       cursor='hand2', command=dlg.destroy)
    ok_btn.pack()
    ok_btn.bind('<Enter>',
                lambda e: ok_btn.config(bg=_darken(c.primary, 0.15)))
    ok_btn.bind('<Leave>', lambda e: ok_btn.config(bg=c.primary))

    # 居中
    dlg.update_idletasks()
    w, h = dlg.winfo_width(), dlg.winfo_height()
    rx = app.root.winfo_x() + (app.root.winfo_width()  - w) // 2
    ry = app.root.winfo_y() + (app.root.winfo_height() - h) // 2
    dlg.geometry(f'+{rx}+{ry}')
    dlg.grab_set()


def ask_overwrite(app, filename):
    """在主线程弹出文件覆盖确认对话框，返回 True（覆盖）或 False（跳过）"""
    if getattr(app, '_overwrite_all', False):
        return True
    if getattr(app, '_skip_all', False):
        return False

    result = [False]
    event  = threading.Event()
    is_multi = len(app.input_files) > 1
    c = app.style.colors

    def _show():
        dlg = tk.Toplevel(app.root)
        dlg.overrideredirect(True)
        dlg.configure(bg=app.C_BG)
        dlg.resizable(False, False)

        header = tk.Frame(dlg, bg=c.warning, height=36)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        tk.Label(header, text="文件已存在",
                 bg=c.warning, fg='#FFFFFF',
                 font=('Microsoft YaHei UI', 10, 'bold')).pack(
                     side=tk.LEFT, padx=12, pady=6)

        body = tk.Frame(dlg, bg=app.C_BG, padx=20, pady=16)
        body.pack(fill=tk.BOTH)
        tk.Label(body, text=f"「{filename}」已存在，是否覆盖？",
                 bg=app.C_BG, fg=app.C_LABEL_FG,
                 font=('Microsoft YaHei UI', 10),
                 wraplength=340, justify='left').pack(anchor=tk.W)

        btn_frame = tk.Frame(dlg, bg=app.C_BG, pady=10)
        btn_frame.pack()

        def _btn(parent, text, bg, cmd, padx=6):
            b = tk.Button(parent, text=text, width=8,
                          bg=bg, fg='#FFFFFF',
                          relief='flat',
                          font=('Microsoft YaHei UI', 9, 'bold'),
                          cursor='hand2', command=cmd)
            b.pack(side=tk.LEFT, padx=padx)
            return b

        if is_multi:
            _btn(btn_frame, "本次覆盖", c.success,   on_overwrite_one)
            _btn(btn_frame, "全部覆盖", '#8E44AD',    on_overwrite_all)
            _btn(btn_frame, "本次跳过", c.primary,    on_skip)
            _btn(btn_frame, "全部跳过", '#7F8C8D',    on_skip_all)
        else:
            _btn(btn_frame, "覆  盖", c.success, on_overwrite_one, padx=8)
            _btn(btn_frame, "跳  过", c.primary,  on_skip,          padx=8)

        dlg.update_idletasks()
        w, h = dlg.winfo_width(), dlg.winfo_height()
        rx = app.root.winfo_x() + (app.root.winfo_width()  - w) // 2
        ry = app.root.winfo_y() + (app.root.winfo_height() - h) // 2
        dlg.geometry(f'+{rx}+{ry}')
        dlg.grab_set()
        dlg.wait_window()
        event.set()

    def on_overwrite_one():
        result[0] = True
        dlg.destroy()

    def on_overwrite_all():
        app._overwrite_all = True
        result[0] = True
        dlg.destroy()

    def on_skip():
        result[0] = False
        dlg.destroy()

    def on_skip_all():
        app._skip_all = True
        result[0] = False
        dlg.destroy()

    app.root.after(0, _show)
    event.wait()
    return result[0]


def _darken(hex_color: str, factor: float = 0.15) -> str:
    """将十六进制颜色调暗指定比例，返回十六进制字符串"""
    try:
        hex_color = hex_color.lstrip('#')
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        r = max(0, min(255, int(r * (1 - factor))))
        g = max(0, min(255, int(g * (1 - factor))))
        b = max(0, min(255, int(b * (1 - factor))))
        return f'#{r:02x}{g:02x}{b:02x}'
    except Exception:
        return hex_color
