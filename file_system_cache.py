"""
文件系统缓存实现，解决多进程环境下缓存不一致问题
"""
import os
import json
import pickle
import tempfile
from typing import Optional, Any
import threading
import time
from pathlib import Path

class FileSystemCache:
    def __init__(self, cache_dir: str = None):
        """
        初始化文件系统缓存

        Args:
            cache_dir: 缓存目录，默认使用系统临时目录
        """
        if cache_dir is None:
            cache_dir = os.path.join(tempfile.gettempdir(), "capcut_draft_cache")

        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # 线程锁
        self._lock = threading.RLock()

        print(f"FileSystemCache initialized with directory: {self.cache_dir}")

    def _get_cache_file(self, key: str) -> Path:
        """获取缓存文件路径"""
        # 使用安全的文件名
        safe_key = key.replace('/', '_').replace('\\', '_').replace(':', '_')
        return self.cache_dir / f"{safe_key}.cache"

    def _get_meta_file(self, key: str) -> Path:
        """获取元数据文件路径"""
        safe_key = key.replace('/', '_').replace('\\', '_').replace(':', '_')
        return self.cache_dir / f"{safe_key}.meta"

    def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """
        设置缓存项

        Args:
            key: 缓存键
            value: 缓存值
            ttl: 过期时间(秒)，默认1小时
        """
        with self._lock:
            try:
                cache_file = self._get_cache_file(key)
                meta_file = self._get_meta_file(key)

                # 保存主数据
                with open(cache_file, 'wb') as f:
                    pickle.dump(value, f)

                # 保存元数据
                meta = {
                    'created_at': time.time(),
                    'expires_at': time.time() + ttl,
                    'access_count': 1,
                    'last_access': time.time()
                }

                with open(meta_file, 'w') as f:
                    json.dump(meta, f)

                print(f"FileSystemCache: SET {key} -> {cache_file}")
                return True

            except Exception as e:
                print(f"FileSystemCache: Error setting {key}: {e}")
                return False

    def get(self, key: str) -> Optional[Any]:
        """
        获取缓存项

        Args:
            key: 缓存键

        Returns:
            缓存值，如果不存在或过期则返回None
        """
        with self._lock:
            try:
                cache_file = self._get_cache_file(key)
                meta_file = self._get_meta_file(key)

                if not cache_file.exists() or not meta_file.exists():
                    print(f"FileSystemCache: MISS {key} - file not found")
                    return None

                # 读取元数据
                with open(meta_file, 'r') as f:
                    meta = json.load(f)

                # 检查是否过期
                if time.time() > meta['expires_at']:
                    print(f"FileSystemCache: MISS {key} - expired")
                    self.delete(key)
                    return None

                # 读取主数据
                with open(cache_file, 'rb') as f:
                    value = pickle.load(f)

                # 更新访问统计
                meta['access_count'] += 1
                meta['last_access'] = time.time()
                with open(meta_file, 'w') as f:
                    json.dump(meta, f)

                print(f"FileSystemCache: HIT {key} (accessed {meta['access_count']} times)")
                return value

            except Exception as e:
                print(f"FileSystemCache: Error getting {key}: {e}")
                return None

    def contains(self, key: str) -> bool:
        """
        检查缓存项是否存在且未过期

        Args:
            key: 缓存键

        Returns:
            是否存在且未过期
        """
        with self._lock:
            try:
                meta_file = self._get_meta_file(key)
                cache_file = self._get_cache_file(key)

                if not meta_file.exists() or not cache_file.exists():
                    print(f"FileSystemCache: CONTAINS {key} -> False (file not found)")
                    return False

                # 读取元数据检查过期时间
                with open(meta_file, 'r') as f:
                    meta = json.load(f)

                if time.time() > meta['expires_at']:
                    print(f"FileSystemCache: CONTAINS {key} -> False (expired)")
                    self.delete(key)
                    return False

                print(f"FileSystemCache: CONTAINS {key} -> True")
                return True

            except Exception as e:
                print(f"FileSystemCache: Error checking {key}: {e}")
                return False

    def delete(self, key: str) -> bool:
        """
        删除缓存项

        Args:
            key: 缓存键

        Returns:
            是否成功删除
        """
        with self._lock:
            try:
                cache_file = self._get_cache_file(key)
                meta_file = self._get_meta_file(key)

                if cache_file.exists():
                    cache_file.unlink()
                if meta_file.exists():
                    meta_file.unlink()

                print(f"FileSystemCache: DELETE {key}")
                return True

            except Exception as e:
                print(f"FileSystemCache: Error deleting {key}: {e}")
                return False

    def clear(self) -> bool:
        """
        清空所有缓存

        Returns:
            是否成功清空
        """
        with self._lock:
            try:
                for file_path in self.cache_dir.iterdir():
                    if file_path.is_file():
                        file_path.unlink()

                print(f"FileSystemCache: CLEAR all cache")
                return True

            except Exception as e:
                print(f"FileSystemCache: Error clearing cache: {e}")
                return False

    def update_access(self, key: str) -> bool:
        """
        更新缓存项的访问时间（LRU实现）

        Args:
            key: 缓存键

        Returns:
            是否成功更新
        """
        with self._lock:
            try:
                meta_file = self._get_meta_file(key)

                if not meta_file.exists():
                    return False

                # 读取元数据
                with open(meta_file, 'r') as f:
                    meta = json.load(f)

                # 更新访问时间
                meta['last_access'] = time.time()
                meta['access_count'] += 1

                # 写回元数据
                with open(meta_file, 'w') as f:
                    json.dump(meta, f)

                print(f"FileSystemCache: UPDATE_ACCESS {key}")
                return True

            except Exception as e:
                print(f"FileSystemCache: Error updating access for {key}: {e}")
                return False

    def cleanup_expired(self) -> int:
        """
        清理过期的缓存项

        Returns:
            清理的项目数量
        """
        with self._lock:
            try:
                current_time = time.time()
                cleaned_count = 0

                for meta_file in self.cache_dir.glob("*.meta"):
                    try:
                        with open(meta_file, 'r') as f:
                            meta = json.load(f)

                        if current_time > meta['expires_at']:
                            key = meta_file.stem
                            self.delete(key)
                            cleaned_count += 1
                    except:
                        # 如果元数据文件损坏，直接删除
                        try:
                            meta_file.unlink()
                            cleaned_count += 1
                        except:
                            pass

                print(f"FileSystemCache: CLEANUP_EXPIRED removed {cleaned_count} items")
                return cleaned_count

            except Exception as e:
                print(f"FileSystemCache: Error during cleanup: {e}")
                return 0

    def size(self) -> int:
        """
        获取缓存项数量

        Returns:
            缓存项数量
        """
        with self._lock:
            try:
                count = len(list(self.cache_dir.glob("*.meta")))
                print(f"FileSystemCache: SIZE = {count}")
                return count
            except Exception as e:
                print(f"FileSystemCache: Error getting size: {e}")
                return 0

# 全局文件系统缓存实例
_file_cache = FileSystemCache()

# 导出与原有内存缓存兼容的接口
def update_cache(key: str, value) -> None:
    """更新缓存（兼容接口）"""
    _file_cache.set(key, value)

def get_cache(key: str):
    """获取缓存（兼容接口）"""
    return _file_cache.get(key)

def cache_contains(key: str) -> bool:
    """检查缓存是否存在（兼容接口）"""
    return _file_cache.contains(key)

def cache_update_access(key: str) -> None:
    """更新缓存访问时间（兼容接口）"""
    _file_cache.update_access(key)

def cache_clear() -> None:
    """清空缓存（新增接口）"""
    _file_cache.clear()

def cache_cleanup_expired() -> int:
    """清理过期缓存（新增接口）"""
    return _file_cache.cleanup_expired()

def cache_size() -> int:
    """获取缓存大小（新增接口）"""
    return _file_cache.size()