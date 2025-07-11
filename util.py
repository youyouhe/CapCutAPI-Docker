import shutil
import subprocess
import json
import re
import hashlib
import functools
import time
from settings.local import DRAFT_DOMAIN, PREVIEW_ROUTER

def hex_to_rgb(hex_color: str) -> tuple:
    """将十六进制颜色代码转换为 RGB 元组（范围 0.0-1.0）"""
    hex_color = hex_color.lstrip('#')
    if len(hex_color) == 3:
        hex_color = ''.join([c*2 for c in hex_color])  # 处理简写形式（如 #fff）
    try:
        r = int(hex_color[0:2], 16) / 255.0
        g = int(hex_color[2:4], 16) / 255.0
        b = int(hex_color[4:6], 16) / 255.0
        return (r, g, b)
    except ValueError:
        raise ValueError(f"无效的十六进制颜色代码: {hex_color}")


def is_windows_path(path):
    """检测路径是否是Windows风格"""
    # 检查是否以驱动器号开头 (如 C:\) 或包含Windows风格的分隔符
    return re.match(r'^[a-zA-Z]:\\|\\\\', path) is not None


def zip_draft(draft_name):
    # 压缩文件夹
    zip_path = f"./tmp/zip/{draft_name}.zip"
    shutil.make_archive(f"./tmp/zip/{draft_name}", 'zip', draft_name)
    return zip_path

def url_to_hash(url, length=16):
    """
    将 URL 转换为固定长度的哈希字符串（不含扩展名）
    
    参数:
    - url: 原始 URL 字符串
    - length: 哈希字符串的长度（最大64，默认16）
    
    返回:
    - 哈希字符串（如：3a7f9e7d9a1b4e2d）
    """
    # 确保 URL 是字节类型
    url_bytes = url.encode('utf-8')
    
    # 使用 SHA-256 生成哈希（安全且唯一性强）
    hash_object = hashlib.sha256(url_bytes)
    
    # 截取指定长度的十六进制字符串
    return hash_object.hexdigest()[:length]


def timing_decorator(func_name):
    """装饰器：用于监控函数执行时间"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            print(f"[{func_name}] 开始执行...")
            try:
                result = func(*args, **kwargs)
                end_time = time.time()
                duration = end_time - start_time
                print(f"[{func_name}] 执行完成，耗时: {duration:.3f}秒")
                return result
            except Exception as e:
                end_time = time.time()
                duration = end_time - start_time
                print(f"[{func_name}] 执行失败，耗时: {duration:.3f}秒，错误: {e}")
                raise
        return wrapper
    return decorator

def generate_draft_url(draft_id):
    return f"{DRAFT_DOMAIN}{PREVIEW_ROUTER}?draft_id={draft_id}"