from collections import OrderedDict
import pyJianYingDraft as draft
from typing import Dict
import threading

# Modify global variable, use OrderedDict to implement LRU cache, limit the maximum number to 10000
DRAFT_CACHE: Dict[str, 'draft.Script_file'] = OrderedDict()  # Use Dict for type hinting
MAX_CACHE_SIZE = 10000

# Add thread lock for cache operations
_cache_lock = threading.RLock()  # Use RLock for nested lock support

def update_cache(key: str, value: draft.Script_file) -> None:
    """Update LRU cache with thread safety"""
    with _cache_lock:
        print(f"DEBUG: update_cache({key}) - adding to cache, current size: {len(DRAFT_CACHE)}")
        if key in DRAFT_CACHE:
            # If the key exists, delete the old item
            DRAFT_CACHE.pop(key)
        elif len(DRAFT_CACHE) >= MAX_CACHE_SIZE:
            print(f"{key}, Cache is full, deleting least recently used item")
            # If the cache is full, delete the least recently used item (the first item)
            DRAFT_CACHE.popitem(last=False)
        # Add new item to the end (most recently used)
        DRAFT_CACHE[key] = value
        print(f"DEBUG: update_cache({key}) - successfully added, new size: {len(DRAFT_CACHE)}")

def get_cache(key: str):
    """Get cache item with thread safety"""
    with _cache_lock:
        result = DRAFT_CACHE.get(key)
        print(f"DEBUG: get_cache({key}) -> {result is not None}")
        return result

def cache_contains(key: str) -> bool:
    """Check if cache contains key with thread safety"""
    with _cache_lock:
        result = key in DRAFT_CACHE
        print(f"DEBUG: cache_contains({key}) -> {result}, total items: {len(DRAFT_CACHE)}")
        return result

def cache_update_access(key: str) -> None:
    """Update cache access time (move to end) with thread safety"""
    with _cache_lock:
        if key in DRAFT_CACHE:
            value = DRAFT_CACHE.pop(key)
            DRAFT_CACHE[key] = value