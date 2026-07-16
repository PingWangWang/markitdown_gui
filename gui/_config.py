"""
MarkItDown GUI - 配置持久化模块

负责：
  - 确定配置文件路径（开发 / PyInstaller 打包环境均适用）
  - 读取/保存用户偏好（当前主题、窗口设置等）
"""
import json
import os
import sys
from pathlib import Path


def _config_dir():
    """返回配置文件存放目录（跨环境兼容）"""
    if getattr(sys, 'frozen', False):
        # PyInstaller 打包：exe 同级目录
        base = Path(sys.executable).parent
    else:
        # 开发模式：项目根目录
        base = Path(__file__).parent.parent
    return base


CONFIG_FILE = _config_dir() / 'config.json'

_DEFAULT_CONFIG = {
    'theme': 'litera',  # 默认亮色主题
}


def load_config() -> dict:
    """加载配置文件，缺失字段用默认值填充"""
    config = _DEFAULT_CONFIG.copy()
    try:
        if CONFIG_FILE.exists():
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                user_config = json.load(f)
            if isinstance(user_config, dict):
                config.update(user_config)
    except (json.JSONDecodeError, OSError):
        pass  # 配置损坏时静默使用默认值
    return config


def save_config(config: dict):
    """保存配置到文件"""
    try:
        CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
    except OSError:
        pass  # 写失败时静默忽略
