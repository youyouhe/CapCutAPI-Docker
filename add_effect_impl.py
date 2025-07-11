from pyJianYingDraft import trange, Video_scene_effect_type, Video_character_effect_type, CapCut_Video_scene_effect_type, CapCut_Video_character_effect_type, exceptions
import pyJianYingDraft as draft
from typing import Optional, Dict, List, Union
from create_draft import get_or_create_draft
from util import generate_draft_url
from settings import IS_CAPCUT_ENV

def add_effect_impl(
    effect_type: str,  # 修改为字符串类型
    start: float = 0,
    end: float = 3.0,
    draft_id: Optional[str] = None,
    track_name: Optional[str] = "effect_01",
    params: Optional[List[Optional[float]]] = None,
    width: int = 1080,
    height: int = 1920
) -> Dict[str, str]:
    """
    向指定草稿添加特效
    :param effect_type: 特效类型名称，将从Video_scene_effect_type或Video_character_effect_type中匹配
    :param start: 开始时间（秒），默认0
    :param end: 结束时间（秒），默认3秒
    :param draft_id: 草稿ID，如果为None或找不到对应的zip文件，则创建新草稿
    :param track_name: 轨道名称，当特效轨道仅有一条时可省略
    :param params: 特效参数列表，参数列表中未提供或为None的项使用默认值
    :param width: 视频宽度，默认1080
    :param height: 视频高度，默认1920
    :return: 更新后的草稿信息
    """
    # 获取或创建草稿
    draft_id, script = get_or_create_draft(
        draft_id=draft_id,
        width=width,
        height=height
    )

    # 计算时间范围
    duration = end - start
    t_range = trange(f"{start}s", f"{duration}s")

    # 动态获取特效类型对象
    if IS_CAPCUT_ENV:
        # 如果是CapCut环境，使用CapCut特效
        effect_enum = CapCut_Video_scene_effect_type[effect_type]
        if effect_enum is None:
            effect_enum = CapCut_Video_character_effect_type[effect_type]
    else:
        # 默认使用剪映特效
        effect_enum = Video_scene_effect_type[effect_type]
        if effect_enum is None:
            effect_enum = Video_character_effect_type[effect_type]
    
    if effect_enum is None:
        raise ValueError(f"Unknown effect type: {effect_type}")

    # 添加特效轨道（仅当轨道不存在时）
    if track_name is not None:
        try:
            imported_track=script.get_imported_track(draft.Track_type.effect, name=track_name)
            # 如果没有抛出异常，说明轨道已存在
        except exceptions.TrackNotFound:
            # 轨道不存在，创建新轨道
            script.add_track(draft.Track_type.effect, track_name=track_name)
    else:
        script.add_track(draft.Track_type.effect)

    # 添加特效
    script.add_effect(effect_enum, t_range, params=params[::-1], track_name=track_name)

    return {
        "draft_id": draft_id,
        "draft_url": generate_draft_url(draft_id)
    }
