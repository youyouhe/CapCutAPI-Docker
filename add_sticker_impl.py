import pyJianYingDraft as draft
from pyJianYingDraft import trange
from typing import Optional, Dict
from pyJianYingDraft import exceptions
from create_draft import get_or_create_draft
from util import generate_draft_url

def add_sticker_impl(
    resource_id: str,
    start: float,
    end: float,
    draft_id: str = None,
    transform_y: float = 0,
    transform_x: float = 0,
    alpha: float = 1.0,
    flip_horizontal: bool = False,
    flip_vertical: bool = False,
    rotation: float = 0.0,
    scale_x: float = 1.0,
    scale_y: float = 1.0,
    track_name: str = "sticker_main",
    relative_index: int = 0,
    width: int = 1080,
    height: int = 1920
) -> Dict[str, str]:
    """
    向指定草稿添加贴纸
    :param resource_id: 贴纸资源ID
    :param start: 开始时间（秒）
    :param end: 结束时间（秒）
    :param draft_id: 草稿ID（可选，默认None则创建新草稿）
    :param transform_y: Y轴位置（默认0，屏幕中间）
    :param transform_x: X轴位置（默认0，屏幕中间）
    :param alpha: 图像不透明度，范围0-1（默认1.0，完全不透明）
    :param flip_horizontal: 是否水平翻转（默认False）
    :param flip_vertical: 是否垂直翻转（默认False）
    :param rotation: 顺时针旋转的角度，可正可负（默认0.0）
    :param scale_x: 水平缩放比例（默认1.0）
    :param scale_y: 垂直缩放比例（默认1.0）
    :param track_name: 轨道名称
    :param relative_index: 相对（同类型轨道的）图层位置，越高越接近前景（默认0）
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

    # 添加贴纸轨道
    if track_name is not None:
        try:
            imported_track = script.get_imported_track(draft.Track_type.sticker, name=track_name)
            # 如果没有抛出异常，说明轨道已存在
        except exceptions.TrackNotFound:
            # 轨道不存在，创建新轨道
            script.add_track(draft.Track_type.sticker, track_name=track_name, relative_index=relative_index)
    else:
        script.add_track(draft.Track_type.sticker, relative_index=relative_index)
    
    # 创建贴纸片段
    sticker_segment = draft.Sticker_segment(
        resource_id,
        trange(f"{start}s", f"{end-start}s"),
        clip_settings=draft.Clip_settings(
            transform_y=transform_y,
            transform_x=transform_x,
            alpha=alpha,
            flip_horizontal=flip_horizontal,
            flip_vertical=flip_vertical,
            rotation=rotation,
            scale_x=scale_x,
            scale_y=scale_y
        )
    )

    # 添加贴纸片段到轨道
    script.add_segment(sticker_segment, track_name=track_name)

    return {
        "draft_id": draft_id,
        "draft_url": generate_draft_url(draft_id)
    }
