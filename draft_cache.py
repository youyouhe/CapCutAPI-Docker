from collections import OrderedDict
import pyJianYingDraft as draft
from typing import Dict

# 修改全局变量，使用OrderedDict实现LRU缓存，限制最大数量为10000
DRAFT_CACHE: Dict[str, 'draft.Script_file'] = OrderedDict()  # 使用 Dict 进行类型提示
MAX_CACHE_SIZE = 10000

def update_cache(key: str, value: draft.Script_file) -> None:
    """更新LRU缓存"""
    if key in DRAFT_CACHE:
        # 如果键存在，删除旧的项
        DRAFT_CACHE.pop(key)
    elif len(DRAFT_CACHE) >= MAX_CACHE_SIZE:
        print(f"{key}, 缓存已满，删除最久未使用的项")
        # 如果缓存已满，删除最久未使用的项（第一个项）
        DRAFT_CACHE.popitem(last=False)
    # 添加新项到末尾（最近使用）
    DRAFT_CACHE[key] = value