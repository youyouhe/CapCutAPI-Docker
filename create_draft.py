import uuid
import pyJianYingDraft as draft
import time
from draft_cache import DRAFT_CACHE, update_cache

def create_draft(width=1080, height=1920):
    """
    创建新的剪映草稿
    :param width: 视频宽度，默认1080
    :param height: 视频高度，默认1920
    :return: (draft_name, draft_path, draft_id, draft_url)
    """
    # 生成时间戳和draft_id
    unix_time = int(time.time())
    unique_id = uuid.uuid4().hex[:8]  # 取UUID的前8位即可
    draft_id = f"dfd_cat_{unix_time}_{unique_id}"  # 使用Unix时间戳和UUID组合
    
    # 创建指定分辨率的剪映草稿
    script = draft.Script_file(width, height)
    
    # 存入全局缓存
    update_cache(draft_id, script)
    
    return script, draft_id

def get_or_create_draft(draft_id=None, width=1080, height=1920):
    """
    获取或创建剪映草稿
    :param draft_id: 草稿ID，如果为None或找不到对应的zip文件，则创建新草稿
    :param width: 视频宽度，默认1080
    :param height: 视频高度，默认1920
    :return: (draft_name, draft_path, draft_id, draft_dir, script)
    """
    global DRAFT_CACHE  # 声明使用全局变量
    
    if draft_id is not None and draft_id in DRAFT_CACHE:
        # 从缓存中获取已存在的草稿信息
        print(f"从缓存中获取草稿: {draft_id}")
        # 更新最近访问时间
        update_cache(draft_id, DRAFT_CACHE[draft_id])
        return draft_id, DRAFT_CACHE[draft_id]

    # 创建新草稿逻辑
    print("创建新草稿")
    script, generate_draft_id = create_draft(
        width=width,
        height=height,
    )
    return generate_draft_id, script
    