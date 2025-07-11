import os
import pyJianYingDraft as draft
import time
from settings.local import IS_CAPCUT_ENV
from util import generate_draft_url, is_windows_path, url_to_hash
from pyJianYingDraft import trange, Clip_settings
import re
from typing import Optional, Dict
from pyJianYingDraft import exceptions
from create_draft import get_or_create_draft

def add_video_track(
    video_url: str,
    draft_folder: Optional[str] = None,
    width: int = 1080,
    height: int = 1920,
    start: float = 0,
    end: Optional[float] = None,
    target_start: float = 0,
    draft_id: Optional[str] = None,
    transform_y: float = 0,
    scale_x: float = 1,
    scale_y: float = 1,
    transform_x: float = 0,
    speed: float = 1.0,
    track_name: str = "main",
    relative_index: int = 0,
    duration: Optional[float] = None,  # 新增 duration 参数
    transition: Optional[str] = None,  # 转场类型
    transition_duration: Optional[float] = 0.5,  # 转场时长（秒）
    # 蒙版相关参数
    mask_type: Optional[str] = None,  # 蒙版类型
    mask_center_x: float = 0.5,  # 蒙版中心X坐标（0-1）
    mask_center_y: float = 0.5,  # 蒙版中心Y坐标（0-1）
    mask_size: float = 1.0,  # 蒙版大小（0-1）
    mask_rotation: float = 0.0,  # 蒙版旋转角度（度）
    mask_feather: float = 0.0,  # 蒙版羽化程度（0-1）
    mask_invert: bool = False,  # 是否反转蒙版
    mask_rect_width: Optional[float] = None,  # 矩形蒙版宽度(仅矩形蒙版)
    mask_round_corner: Optional[float] = None,  # 矩形蒙版圆角(仅矩形蒙版，0-100)
    volume: float = 1.0  # 音量大小，默认1.0
) -> Dict[str, str]:
    """
    向指定草稿添加视频轨道
    :param draft_folder: 草稿文件夹路径，可选参数
    :param video_url: 视频URL
    :param width: 视频宽度，默认1080
    :param height: 视频高度，默认1920
    :param start: 源视频开始时间（秒），默认0
    :param end: 源视频结束时间（秒），默认None（使用视频总时长）
    :param target_start: 目标视频开始时间（秒），默认0
    :param draft_id: 草稿ID，如果为None或找不到对应的zip文件，则创建新草稿
    :param transform_y: Y轴变换，默认0
    :param scale_x: X轴缩放，默认1
    :param scale_y: Y轴缩放，默认1
    :param transform_x: X轴变换，默认0
    :param speed: 视频播放速度，默认1.0
    :param track_name: 当只有一个视频的时候，轨道名称可以省略
    :param relative_index: 轨道渲染顺序索引，默认0
    :param duration: 视频时长（秒），如果提供则跳过时长检测
    :param transition: 转场类型，可选参数
    :param transition_duration: 转场时长（秒），默认使用转场类型的默认时长
    :param mask_type: 蒙版类型（线性、镜面、圆形、矩形、爱心、星形），可选参数
    :param mask_center_x: 蒙版中心X坐标（0-1），默认0.5
    :param mask_center_y: 蒙版中心Y坐标（0-1），默认0.5
    :param mask_size: 蒙版大小（0-1），默认1.0
    :param mask_rotation: 蒙版旋转角度（度），默认0.0
    :param mask_feather: 蒙版羽化程度（0-1），默认0.0
    :param mask_invert: 是否反转蒙版，默认False
    :param mask_rect_width: 矩形蒙版的宽度，仅在蒙版类型为矩形时允许设置，以占素材宽度的比例表示
    :param mask_round_corner: 矩形蒙版的圆角参数，仅在蒙版类型为矩形时允许设置，取值范围0~100
    :param volume: 音量大小，默认1.0（0.0为静音，1.0为原音量）
    :return: 更新后的草稿信息，包含draft_id和draft_url
    """
    # 获取或创建草稿
    draft_id, script = get_or_create_draft(
        draft_id=draft_id,
        width=width,
        height=height
    )
    
    # 检查是否存在视频轨道，如果不存在则添加一条默认视频轨道
    try:
        script.get_track(draft.Track_type.video, track_name=None)
    except exceptions.TrackNotFound:
        script.add_track(draft.Track_type.video, relative_index=0)
    except NameError:
        # 如果存在多个视频轨道(NameError)，则不做任何操作
        pass

    # 添加视频轨道（仅当轨道不存在时）
    if track_name is not None:
        try:
            imported_track=script.get_imported_track(draft.Track_type.video, name=track_name)
            # 如果没有抛出异常，说明轨道已存在
        except exceptions.TrackNotFound:
            # 轨道不存在，创建新轨道
            script.add_track(draft.Track_type.video, track_name=track_name, relative_index=relative_index)
    else:
        script.add_track(draft.Track_type.video, relative_index=relative_index)
    
    # 如果传递了 duration 参数，优先使用它；否则使用默认时长0秒，在下载草稿时，才会获取真实时长
    if duration is not None:
        # 使用传递进来的 duration，跳过时长获取和检查
        video_duration = duration
    else:
        # 使用默认时长0秒，在下载草稿时，才会获取真实时长
        video_duration = 0.0  # 默认视频时长为0秒
        # duration_result = get_video_duration(video_url)
        # if not duration_result["success"]:
        #     print(f"获取视频时长失败: {duration_result['error']}")
        
        # # 检查视频时长是否超过2分钟
        # if duration_result["output"] > 120:  # 120秒 = 2分钟
        #     raise Exception(f"视频时长超过2分钟限制，当前时长: {duration_result['output']}秒")
        
        # video_duration = duration_result["output"]
    
    # 生成本地文件名
    material_name = f"video_{url_to_hash(video_url)}.mp4"
    # local_video_path = download_video(video_url, draft_dir)
    
    # 构建draft_video_path
    draft_video_path = None
    if draft_folder:
        # 检测输入路径类型并处理
        if is_windows_path(draft_folder):
            # Windows路径处理
            windows_drive, windows_path = re.match(r'([a-zA-Z]:)(.*)', draft_folder).groups()
            parts = [p for p in windows_path.split('\\') if p]  # 分割路径并过滤空部分
            draft_video_path = os.path.join(windows_drive, *parts, draft_id, "assets", "video", material_name)
            # 规范化路径（确保分隔符一致）
            draft_video_path = draft_video_path.replace('/', '\\')
        else:
            # macOS/Linux路径处理
            draft_video_path = os.path.join(draft_folder, draft_id, "assets", "video", material_name)
        
        # 打印路径信息
        print('replace_path:', draft_video_path)

    # 设置视频结束时间
    video_end = end if end is not None else video_duration
    
    # 计算源视频时长
    source_duration = video_end - start
    # 计算目标视频时长（考虑速度因素）
    target_duration = source_duration / speed
    
    # 创建视频片段
    if draft_video_path:
        video_material = draft.Video_material(material_type='video', replace_path=draft_video_path, remote_url=video_url, material_name=material_name, duration=video_duration, width=0, height=0)
    else:
        video_material = draft.Video_material(material_type='video', remote_url=video_url, material_name=material_name, duration = video_duration, width=0, height=0)
    
    # 创建source_timerange和target_timerange
    source_timerange = trange(f"{start}s", f"{source_duration}s")
    target_timerange = trange(f"{target_start}s", f"{target_duration}s")
    
    video_segment = draft.Video_segment(
        video_material,
        target_timerange=target_timerange,
        source_timerange=source_timerange,
        speed=speed,
        clip_settings=Clip_settings(
            transform_y=transform_y,
            scale_x=scale_x,
            scale_y=scale_y,
            transform_x=transform_x
        ),
        volume=volume
    )
    
    # 添加转场效果
    if transition:
        try:
            # 获取转场类型
            if IS_CAPCUT_ENV:
                transition_type = getattr(draft.CapCut_Transition_type, transition)
            else:
                transition_type = getattr(draft.Transition_type, transition)
            
            # 设置转场时长（转换为微秒）
            duration_microseconds = int(transition_duration * 1e6)
            
            # 添加转场
            video_segment.add_transition(transition_type, duration=duration_microseconds)
        except AttributeError:
            raise ValueError(f"不支持的转场类型: {transition}，已跳过转场设置")
    
    # 添加蒙版效果
    if mask_type:
        try:
            if IS_CAPCUT_ENV:
                mask_type_enum = getattr(draft.CapCut_Mask_type, mask_type)
            else:
                mask_type_enum = getattr(draft.Mask_type, mask_type)
            video_segment.add_mask(
                script,
                mask_type_enum,
                center_x=mask_center_x,
                center_y=mask_center_y,
                size=mask_size,
                rotation=mask_rotation,
                feather=mask_feather,
                invert=mask_invert,
                rect_width=mask_rect_width,
                round_corner=mask_round_corner
            )
        except:
            raise ValueError(f"不支持的蒙版类型 {mask_type}，支持的类型包括：线性、镜面、圆形、矩形、爱心、星形")
    
    # 添加视频片段到轨道
    # if imported_track is not None:
    #     imported_track.add_segment(video_segment)
    # else:
    script.add_segment(video_segment, track_name=track_name)
    
    return {
        "draft_id": draft_id,
        "draft_url": generate_draft_url(draft_id)
    }
