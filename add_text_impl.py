import pyJianYingDraft as draft
from settings.local import IS_CAPCUT_ENV
from util import generate_draft_url, hex_to_rgb
from pyJianYingDraft import trange, Font_type
from typing import Optional
from pyJianYingDraft import exceptions
from create_draft import get_or_create_draft
from pyJianYingDraft.text_segment import TextBubble, TextEffect

def add_text_impl(
    text: str,
    start: float,
    end: float,
    draft_id: str = None,
    transform_y: float = -0.8,
    transform_x: float = 0,
    font: str = "文轩体",
    font_color: str = "#ffffff",
    font_size: float = 8.0,
    track_name: str = "text_main",
    vertical: bool = False,  # 是否竖排显示
    font_alpha: float = 1.0,  # 透明度，范围0.0-1.0
    # 描边参数
    border_alpha: float = 1.0,
    border_color: str = "#000000",
    border_width: float = 0.0,  # 默认不显示描边
    # 背景参数
    background_color: str = "#000000",
    background_style: int = 1,
    background_alpha: float = 0.0,  # 默认不显示背景
    # 气泡效果
    bubble_effect_id: Optional[str] = None,
    bubble_resource_id: Optional[str] = None,
    # 文本花字
    effect_effect_id: Optional[str] = None,
    intro_animation: Optional[str] = None,  # 入场动画类型
    intro_duration: float = 0.5,  # 入场动画持续时间（秒），默认0.5秒
    outro_animation: Optional[str] = None,  # 出场动画类型
    outro_duration: float = 0.5,  # 出场动画持续时间（秒），默认0.5秒
    width: int = 1080,
    height: int = 1920,
    fixed_width: float = -1,  # 文本固定宽度比例，默认-1表示不固定
    fixed_height: float = -1,  # 文本固定高度比例，默认-1表示不固定
):
    """
    向指定草稿添加文本字幕（参数可配置版本）
    :param text: 文本内容
    :param start: 开始时间（秒）
    :param end: 结束时间（秒）
    :param draft_id: 草稿ID（可选，默认None则创建新草稿）
    :param transform_y: Y轴位置（默认-0.8，屏幕下方）
    :param transform_x: X轴位置（默认0，屏幕中间）
    :param font: 字体名称（支持Font_type中的所有字体）
    :param font_color: 字体颜色 #FFF0FF
    :param font_size: 字体大小（浮点值，默认8.0）
    :param track_name: 轨道名称
    :param vertical: 是否竖排显示（默认False）
    :param font_alpha: 文字透明度，范围0.0-1.0（默认1.0，完全不透明）
    :param border_alpha: 描边透明度，范围0.0-1.0（默认1.0）
    :param border_color: 描边颜色（默认黑色）
    :param border_width: 描边宽度（默认0.0，不显示描边）
    :param background_color: 背景颜色（默认黑色）
    :param background_style: 背景样式（默认1）
    :param background_alpha: 背景透明度（默认0.0，不显示背景）
    :param bubble_effect_id: 气泡效果ID
    :param bubble_resource_id: 气泡资源ID
    :param effect_effect_id: 花字效果ID
    :param intro_animation: 入场动画类型
    :param intro_duration: 入场动画持续时间（秒），默认0.5秒
    :param outro_animation: 出场动画类型
    :param outro_duration: 出场动画持续时间（秒），默认0.5秒
    :param width: 视频宽度（像素）
    :param height: 视频高度（像素）
    :param fixed_width: 文本固定宽度比例，范围0.0-1.0，默认-1表示不固定
    :param fixed_height: 文本固定高度比例，范围0.0-1.0，默认-1表示不固定
    :return: 更新后的草稿信息
    """
    # 校验字体是否在Font_type中
    try:
        font_type = getattr(Font_type, font)
    except:
        available_fonts = [attr for attr in dir(Font_type) if not attr.startswith('_')]
        raise ValueError(f"不支持的字体：{font}，请使用Font_type中的字体之一：{available_fonts}")
    
    # 校验alpha值范围
    if not 0.0 <= font_alpha <= 1.0:
        raise ValueError("alpha值必须在0.0到1.0之间")
    if not 0.0 <= border_alpha <= 1.0:
        raise ValueError("border_alpha值必须在0.0到1.0之间")
    if not 0.0 <= background_alpha <= 1.0:
        raise ValueError("background_alpha值必须在0.0到1.0之间")
    
    # 获取或创建草稿
    draft_id, script = get_or_create_draft(
        draft_id=draft_id,
        width=width,
        height=height
    )

    # 添加文本轨道
    if track_name is not None:
        try:
            imported_track = script.get_imported_track(draft.Track_type.text, name=track_name)
            # 如果没有抛出异常，说明轨道已存在
        except exceptions.TrackNotFound:
            # 轨道不存在，创建新轨道
            script.add_track(draft.Track_type.text, track_name=track_name)
    else:
        script.add_track(draft.Track_type.audio)

    # 转换十六进制颜色为 RGB 元组
    try:
        rgb_color = hex_to_rgb(font_color)
        rgb_border_color = hex_to_rgb(border_color)
    except ValueError as e:
        raise ValueError(f"颜色参数错误: {str(e)}")
    
    # 创建text_border (描边)
    text_border = None
    if border_width > 0:
        text_border = draft.Text_border(
            alpha=border_alpha,
            color=rgb_border_color,
            width=border_width
        )
    
    # 创建text_background (背景)
    text_background = None
    if background_alpha > 0:
        text_background = draft.Text_background(
            color=background_color,
            style=background_style,
            alpha=background_alpha
        )
    
    # 创建气泡效果
    text_bubble = None
    if bubble_effect_id and bubble_resource_id:
        text_bubble = TextBubble(
            effect_id=bubble_effect_id,
            resource_id=bubble_resource_id
        )
    
    # 创建花字效果
    text_effect = None
    if effect_effect_id:
        text_effect = TextEffect(
            effect_id=effect_effect_id
        )
    
    # 将比例转换为像素值
    pixel_fixed_width = -1
    pixel_fixed_height = -1
    if fixed_width > 0:
        pixel_fixed_width = int(fixed_width * script.width)
    if fixed_height > 0:
        pixel_fixed_height = int(fixed_height * script.height)
    
    # 创建文本片段（使用可配置参数）
    text_segment = draft.Text_segment(
        text,
        trange(f"{start}s", f"{end-start}s"),
        font=font_type,  # 使用Font_type中的字体
        style=draft.Text_style(
            color=rgb_color,
            size=font_size,
            align=1,
            vertical=vertical,  # 设置是否竖排
            alpha=font_alpha  # 设置透明度
        ),
        clip_settings=draft.Clip_settings(transform_y=transform_y, transform_x=transform_x),
        border=text_border,
        background=text_background,
        fixed_width=pixel_fixed_width,
        fixed_height=pixel_fixed_height
    )

    if text_bubble:
        text_segment.add_bubble(text_bubble.effect_id, text_bubble.resource_id)
    if text_effect:
        text_segment.add_effect(text_effect.effect_id)

    # 添加入场动画
    if intro_animation:
        try:
            if IS_CAPCUT_ENV:
                animation_type = getattr(draft.CapCut_Text_intro, intro_animation)
            else:
                animation_type = getattr(draft.Text_intro, intro_animation)
            # 将秒转换为微秒
            duration_microseconds = int(intro_duration * 1000000)
            text_segment.add_animation(animation_type, duration_microseconds)  # 添加入场动画，设置持续时间
        except:
            print(f"警告：不支持的入场动画类型 {intro_animation}，将忽略此参数")

    # 添加出场动画
    if outro_animation:
        try:
            if IS_CAPCUT_ENV:
                animation_type = getattr(draft.CapCut_Text_outro, outro_animation)
            else:
                animation_type = getattr(draft.Text_outro, outro_animation)
            # 将秒转换为微秒
            duration_microseconds = int(outro_duration * 1000000)
            text_segment.add_animation(animation_type, duration_microseconds)  # 添加出场动画，设置持续时间
        except:
            print(f"警告：不支持的出场动画类型 {outro_animation}，将忽略此参数")

    # 添加文本片段到轨道
    script.add_segment(text_segment, track_name=track_name)

    return {
        "draft_id": draft_id,
        "draft_url": generate_draft_url(draft_id)
    }
