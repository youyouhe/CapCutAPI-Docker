"""
Draft缓存模块 - 使用文件系统缓存解决多进程环境下的一致性问题
"""
import pyJianYingDraft as draft
from file_system_cache import (
    update_cache as fs_update_cache,
    get_cache as fs_get_cache,
    cache_contains as fs_cache_contains,
    cache_update_access as fs_cache_update_access,
    cache_clear,
    cache_cleanup_expired,
    cache_size
)

# 为了兼容性，保留原有接口但重定向到文件系统缓存
def update_cache(key: str, value: draft.Script_file) -> None:
    """更新缓存 - 现在使用文件系统缓存"""
    print(f"DEBUG: update_cache({key}) - using filesystem cache")
    fs_update_cache(key, value)

def get_cache(key: str):
    """获取缓存 - 现在使用文件系统缓存"""
    result = fs_get_cache(key)
    print(f"DEBUG: get_cache({key}) -> {result is not None}")
    return result

def cache_contains(key: str) -> bool:
    """检查缓存是否存在 - 现在使用文件系统缓存"""
    result = fs_cache_contains(key)
    print(f"DEBUG: cache_contains({key}) -> {result}")
    return result

def cache_update_access(key: str) -> None:
    """更新缓存访问时间 - 现在使用文件系统缓存"""
    print(f"DEBUG: cache_update_access({key}) - using filesystem cache")
    fs_cache_update_access(key)

# 新增的缓存管理功能
def clear_cache():
    """清空所有缓存"""
    return cache_clear()

def cleanup_expired_cache():
    """清理过期缓存"""
    return cache_cleanup_expired()

def get_cache_size():
    """获取缓存大小"""
    return cache_size()