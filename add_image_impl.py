import os
import uuid
import pyJianYingDraft as draft
import time
from settings.local import IS_CAPCUT_ENV
from util import generate_draft_url, is_windows_path, url_to_hash
from pyJianYingDraft import trange, Clip_settings
import re
from typing import Optional, Dict
from pyJianYingDraft import exceptions
from create_draft import get_or_create_draft

def add_image_impl(
    image_url: str,
    draft_folder: Optional[str] = None,
    width: int = 1080,
    height: int = 1920,
    start: float = 0,
    end: float = 3.0,  # 默认显示3秒
    draft_id: Optional[str] = None,
    transform_y: float = 0,
    scale_x: float = 1,
    scale_y: float = 1,
    transform_x: float = 0,
    track_name: str = "main",
    relative_index: int = 0,
    animation: Optional[str] = None,  # 入场动画参数（向后兼容）
    animation_duration: float = 0.5,  # 入场动画持续时间参数，默认0.5秒
    intro_animation: Optional[str] = None,  # 新的入场动画参数，优先级高于animation
    intro_animation_duration: float = 0.5,  # 新的入场动画持续时间参数，默认0.5秒
    outro_animation: Optional[str] = None,  # 出场动画参数
    outro_animation_duration: float = 0.5,  # 出场动画持续时间参数，默认0.5秒
    combo_animation: Optional[str] = None,  # 组合动画参数
    combo_animation_duration: float = 0.5,  # 组合动画持续时间参数，默认0.5秒
    transition: Optional[str] = None,  # 转场类型参数
    transition_duration: Optional[float] = 0.5,  # 转场持续时间参数（秒），默认0.5秒
    # 蒙版相关参数
    mask_type: Optional[str] = None,  # 蒙版类型：线性、镜面、圆形、矩形、爱心、星形
    mask_center_x: float = 0.0,  # 蒙版中心点X坐标
    mask_center_y: float = 0.0,  # 蒙版中心点Y坐标
    mask_size: float = 0.5,  # 蒙版主要尺寸
    mask_rotation: float = 0.0,  # 蒙版旋转角度
    mask_feather: float = 0.0,  # 蒙版羽化参数(0-100)
    mask_invert: bool = False,  # 是否反转蒙版
    mask_rect_width: Optional[float] = None,  # 矩形蒙版宽度(仅矩形蒙版)
    mask_round_corner: Optional[float] = None  # 矩形蒙版圆角(仅矩形蒙版，0-100)
) -> Dict[str, str]:
    """
    向指定草稿添加图片轨道
    :param animation: 入场动画名称，支持的动画包括：缩小、渐显、放大、旋转、Kira游动、抖动下降、镜像翻转、旋转开幕、折叠开幕、漩涡旋转、跳转开幕等
    :param animation_duration: 入场动画持续时间（秒），默认0.5秒
    :param intro_animation: 新的入场动画参数，优先级高于animation
    :param intro_animation_duration: 新的入场动画持续时间（秒），默认0.5秒
    :param outro_animation: 出场动画参数
    :param outro_animation_duration: 出场动画持续时间（秒），默认0.5秒
    :param combo_animation: 组合动画参数
    :param combo_animation_duration: 组合动画持续时间（秒），默认0.5秒
    :param transition: 转场类型，支持的转场包括：叠化、上移、下移、左移、右移、分割、压缩、动漫云朵、动漫漩涡等
    :param transition_duration: 转场持续时间（秒），默认0.5秒
    :param draft_folder: 草稿文件夹路径，可选参数
    :param image_url: 图片URL
    :param width: 视频宽度，默认1080
    :param height: 视频高度，默认1920
    :param start: 开始时间（秒），默认0
    :param end: 结束时间（秒），默认3秒
    :param draft_id: 草稿ID，如果为None或找不到对应的zip文件，则创建新草稿
    :param transform_y: Y轴变换，默认0
    :param scale_x: X轴缩放，默认1
    :param scale_y: Y轴缩放，默认1
    :param transform_x: X轴变换，默认0
    :param track_name: 当只有一个视频的时候，轨道名称可以省略
    :param relative_index: 轨道渲染顺序索引，默认0
    :param mask_type: 蒙版类型，支持：线性、镜面、圆形、矩形、爱心、星形
    :param mask_center_x: 蒙版中心点X坐标(以素材的像素为单位)，默认设置在素材中心
    :param mask_center_y: 蒙版中心点Y坐标(以素材的像素为单位)，默认设置在素材中心
    :param mask_size: 蒙版的主要尺寸，以占素材高度的比例表示，默认为0.5
    :param mask_rotation: 蒙版顺时针旋转的角度，默认不旋转
    :param mask_feather: 蒙版的羽化参数，取值范围0~100，默认无羽化
    :param mask_invert: 是否反转蒙版，默认不反转
    :param mask_rect_width: 矩形蒙版的宽度，仅在蒙版类型为矩形时允许设置，以占素材宽度的比例表示
    :param mask_round_corner: 矩形蒙版的圆角参数，仅在蒙版类型为矩形时允许设置，取值范围0~100
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
    
    # 生成material_name但不下载图片
    material_name = f"image_{url_to_hash(image_url)}.png"
    
    # 构建draft_image_path
    draft_image_path = None
    if draft_folder:
        # 检测输入路径类型并处理
        if is_windows_path(draft_folder):
            # Windows路径处理
            windows_drive, windows_path = re.match(r'([a-zA-Z]:)(.*)', draft_folder).groups()
            parts = [p for p in windows_path.split('\\') if p]  # 分割路径并过滤空部分
            draft_image_path = os.path.join(windows_drive, *parts, draft_id, "assets", "image", material_name)
            # 规范化路径（确保分隔符一致）
            draft_image_path = draft_image_path.replace('/', '\\')
        else:
            # macOS/Linux路径处理
            draft_image_path = os.path.join(draft_folder, draft_id, "assets", "image", material_name)
        
        # 打印路径信息
        print('replace_path:', draft_image_path)
    
    # 创建图片素材
    if draft_image_path:
        image_material = draft.Video_material(path=None, material_type='photo', replace_path=draft_image_path, remote_url=image_url, material_name=material_name)
    else:
        image_material = draft.Video_material(path=None, material_type='photo', remote_url=image_url, material_name=material_name)
    
    # 创建target_timerange（图片
    duration = end - start
    target_timerange = trange(f"{start}s", f"{duration}s")
    source_timerange = trange(f"{0}s", f"{duration}s")
    
    # 创建图片片段
    image_segment = draft.Video_segment(
        image_material,
        target_timerange=target_timerange,
        source_timerange=source_timerange,
        clip_settings=Clip_settings(
            transform_y=transform_y,
            scale_x=scale_x,
            scale_y=scale_y,
            transform_x=transform_x
        )
    )
    
    # 添加入场动画（优先使用intro_animation，其次使用animation）
    intro_anim = intro_animation if intro_animation is not None else animation
    intro_animation_duration = intro_animation_duration if intro_animation_duration is not None else animation_duration
    if intro_anim:
        try:
            if IS_CAPCUT_ENV:
                animation_type = getattr(draft.CapCut_Intro_type, intro_anim)
            else:
                animation_type = getattr(draft.Intro_type, intro_anim)
            image_segment.add_animation(animation_type, intro_animation_duration * 1e6)  # 使用微秒单位的动画持续时间
        except AttributeError:
            raise ValueError(f"警告：不支持的入场动画类型 {intro_anim}，将忽略此参数")
    
    # 添加出场动画
    if outro_animation:
        try:
            if IS_CAPCUT_ENV:
                outro_type = getattr(draft.CapCut_Outro_type, outro_animation)
            else:
                outro_type = getattr(draft.Outro_type, outro_animation)
            image_segment.add_animation(outro_type, outro_animation_duration * 1e6)  # 使用微秒单位的动画持续时间
        except AttributeError:
            raise ValueError(f"警告：不支持的出场动画类型 {outro_animation}，将忽略此参数")
    
    # 添加组合动画
    if combo_animation:
        try:
            if IS_CAPCUT_ENV:
                combo_type = getattr(draft.CapCut_Group_animation_type, combo_animation)
            else:
                combo_type = getattr(draft.Group_animation_type, combo_animation)
            image_segment.add_animation(combo_type, combo_animation_duration * 1e6)  # 使用微秒单位的动画持续时间
        except AttributeError:
            raise ValueError(f"警告：不支持的组合动画类型 {combo_animation}，将忽略此参数")
    
    # 添加转场效果
    if transition:
        try:
            if IS_CAPCUT_ENV:
                transition_type = getattr(draft.CapCut_Transition_type, transition)
            else:
                transition_type = getattr(draft.Transition_type, transition)
            # 将秒转换为微秒（乘以1000000）
            duration_microseconds = int(transition_duration * 1000000) if transition_duration is not None else None
            image_segment.add_transition(transition_type, duration=duration_microseconds)
        except AttributeError:
            raise ValueError(f"警告：不支持的转场类型 {transition}，将忽略此参数")
    
    # 添加蒙版效果
    if mask_type:
        try:
            if IS_CAPCUT_ENV:
                mask_type_enum = getattr(draft.CapCut_Mask_type, mask_type)
            else:
                mask_type_enum = getattr(draft.Mask_type, mask_type)
            image_segment.add_mask(
                script,
                mask_type_enum,  # 移除关键字名称，作为位置参数传递
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
    
    # 添加图片片段到轨道
    script.add_segment(image_segment, track_name=track_name)
    
    return {
        "draft_id": draft_id,
        "draft_url": generate_draft_url(draft_id)
    }
