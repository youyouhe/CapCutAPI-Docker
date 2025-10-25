import uuid
import pyJianYingDraft as draft
import time
from draft_cache import update_cache, get_cache, cache_contains, cache_update_access, save_script_changes
from util import timestamp_log

class AutoSaveScriptWrapper:
    """Script对象的自动保存包装器

    这个包装器会自动将所有对script对象的修改保存到缓存中
    """

    def __init__(self, script: draft.Script_file, draft_id: str):
        self._script = script
        self._draft_id = draft_id

    def __getattr__(self, name):
        """代理所有未定义的属性到原始script对象"""
        attr = getattr(self._script, name)
        if callable(attr):
            # 如果是方法，返回一个包装后的方法
            def wrapper(*args, **kwargs):
                result = attr(*args, **kwargs)
                # 方法调用后立即保存
                save_script_changes(self._draft_id, self._script)
                return result
            return wrapper
        else:
            # 如果是属性，直接返回
            return attr

    def get_original_script(self):
        """获取原始的script对象（用于调试）"""
        return self._script

def create_draft(width=1080, height=1920):
    """
    Create new CapCut draft
    :param width: Video width, default 1080
    :param height: Video height, default 1920
    :return: (draft_name, draft_path, draft_id, draft_url)
    """
    # Generate timestamp and draft_id
    unix_time = int(time.time())
    unique_id = uuid.uuid4().hex[:8]  # Take the first 8 digits of UUID
    draft_id = f"dfd_cat_{unix_time}_{unique_id}"  # Use Unix timestamp and UUID combination

    print(timestamp_log(f"CREATE_DRAFT: Creating new draft with draft_id={draft_id}"))

    # Create CapCut draft with specified resolution
    script = draft.Script_file(width, height)

    print(timestamp_log(f"CREATE_DRAFT: About to add draft {draft_id} to cache"))
    # Store in global cache
    update_cache(draft_id, script)
    print(timestamp_log(f"CREATE_DRAFT: Successfully created and cached draft {draft_id}"))

    return script, draft_id

def get_or_create_draft(draft_id=None, width=1080, height=1920):
    """
    Get or create CapCut draft
    :param draft_id: Draft ID, if None or corresponding zip file not found, create new draft
    :param width: Video width, default 1080
    :param height: Video height, default 1920
    :return: (draft_name, draft_path, draft_id, draft_dir, script)
    """
    # 现在使用文件系统缓存，不需要global声明

    print(timestamp_log(f"get_or_create_draft called with draft_id={draft_id}"))

    if draft_id is not None:
        print(timestamp_log(f"Checking if draft {draft_id} exists in cache"))
        if cache_contains(draft_id):
            # Get existing draft information from cache
            print(timestamp_log(f"✓ Found draft {draft_id} in cache, reusing it"))
            # Update last access time
            cache_update_access(draft_id)
            script = get_cache(draft_id)
            # 包装为自动保存script对象
            wrapped_script = AutoSaveScriptWrapper(script, draft_id)
            return draft_id, wrapped_script
        else:
            print(timestamp_log(f"✗ DRAFT {draft_id} NOT FOUND IN CACHE!"))
            print(timestamp_log(f"CRITICAL ERROR: Requested draft {draft_id} not found, created new draft instead. This indicates draft caching issues!"))

    # Create new draft logic
    print(timestamp_log("Creating new draft because original was not found"))
    script, generate_draft_id = create_draft(
        width=width,
        height=height,
    )

    print(timestamp_log(f"About to add new draft {generate_draft_id} to cache"))
    # Add the newly created draft to cache
    update_cache(generate_draft_id, script)
    print(timestamp_log(f"✓ Added new draft to cache: {generate_draft_id}"))

    # 包装为自动保存script对象
    wrapped_script = AutoSaveScriptWrapper(script, generate_draft_id)
    return generate_draft_id, wrapped_script
    