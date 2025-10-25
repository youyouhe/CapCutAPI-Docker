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

# 全局变量跟踪当前活跃的script对象
_active_scripts = {}

def update_cache(key: str, value: draft.Script_file) -> None:
    """更新缓存 - 现在使用文件系统缓存"""
    print(f"DEBUG: update_cache({key}) - using filesystem cache")
    fs_update_cache(key, value)
    # 更新活跃对象缓存
    _active_scripts[key] = value

def get_cache(key: str):
    """获取缓存 - 现在使用文件系统缓存"""
    # 首先检查是否有活跃的script对象
    if key in _active_scripts:
        print(f"DEBUG: get_cache({key}) -> found in active scripts")
        return _active_scripts[key]

    # 从文件系统缓存加载
    result = fs_get_cache(key)
    if result is not None:
        # 缓存到活跃对象中
        _active_scripts[key] = result
        print(f"DEBUG: get_cache({key}) -> loaded from filesystem and cached in active scripts")
    else:
        print(f"DEBUG: get_cache({key}) -> None")
    return result

def cache_contains(key: str) -> bool:
    """检查缓存是否存在 - 现在使用文件系统缓存"""
    # 首先检查活跃对象
    if key in _active_scripts:
        print(f"DEBUG: cache_contains({key}) -> True (found in active scripts)")
        return True

    # 检查文件系统缓存
    result = fs_cache_contains(key)
    print(f"DEBUG: cache_contains({key}) -> {result} (filesystem cache)")
    return result

def cache_update_access(key: str) -> None:
    """更新缓存访问时间 - 现在使用文件系统缓存"""
    print(f"DEBUG: cache_update_access({key}) - using filesystem cache")
    fs_cache_update_access(key)

def save_script_changes(key: str, script: draft.Script_file) -> None:
    """保存script对象的更改到缓存

    这个函数应该在每次修改script对象后调用，确保更改被持久化
    """
    print(f"DEBUG: save_script_changes({key}) - saving script modifications to cache")
    fs_update_cache(key, script)
    _active_scripts[key] = script

def get_active_script(key: str):
    """获取活跃的script对象（如果存在）"""
    return _active_scripts.get(key)

def clear_active_script(key: str) -> None:
    """清除活跃的script对象"""
    if key in _active_scripts:
        del _active_scripts[key]
        print(f"DEBUG: clear_active_script({key}) - removed from active scripts")

# 新增的缓存管理功能
def clear_cache():
    """清空所有缓存"""
    _active_scripts.clear()
    return cache_clear()

def cleanup_expired_cache():
    """清理过期缓存"""
    return cache_cleanup_expired()

def get_cache_size():
    """获取缓存大小"""
    return cache_size()