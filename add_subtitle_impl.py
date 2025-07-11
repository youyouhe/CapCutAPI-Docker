import pyJianYingDraft as draft
from util import generate_draft_url, hex_to_rgb
from create_draft import get_or_create_draft
from pyJianYingDraft.text_segment import TextBubble, TextEffect
from typing import Optional
import requests

def add_subtitle_impl(
    srt_path: str,
    draft_id: str = None,
    track_name: str = "subtitle",
    time_offset: float = 0,
    # 字体样式参数
    font_size: float = 8.0,
    bold: bool = False,
    italic: bool = False,
    underline: bool = False,
    font_color: str = "#FFFFFF",
    
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
    # 图像调节参数
    transform_x: float = 0.0,
    transform_y: float = -0.8,  # 字幕默认位置在底部
    scale_x: float = 1.0,
    scale_y: float = 1.0,
    rotation: float = 0.0,
    style_reference: draft.Text_segment = None,
    vertical: bool = True,  # 新增参数：是否垂直显示
    alpha: float = 0.4,
    width: int = 1080,  # 新增参数
    height: int = 1920  # 新增参数
):
    """
    向草稿添加字幕
    :param srt_path: 字幕文件路径或URL或SRT文本内容
    :param draft_id: 草稿ID，如果为None则创建新草稿
    :param track_name: 轨道名称，默认为"subtitle"
    :param time_offset: 时间偏移量，默认为"0"s
    :param text_style: 文本样式，默认为None
    :param clip_settings: 片段设置，默认为None
    :param style_reference: 样式参考，默认为None
    :return: 草稿信息
    """
    # 获取或创建草稿
    draft_id, script = get_or_create_draft(
        draft_id=draft_id,
        width=width,
        height=height
    )
    
    # 处理字幕内容
    srt_content = None
    
    # 检查是否为URL
    if srt_path.startswith(('http://', 'https://')):
        try:
            response = requests.get(srt_path)
            response.raise_for_status()

            response.encoding = 'utf-8'
            srt_content = response.text
        except Exception as e:
            raise Exception(f"下载字幕文件失败: {str(e)}")
    else:
        # 如果不是URL，直接使用内容
        srt_content = srt_path
        # 处理可能包含的转义字符
        srt_content = srt_content.replace('\\n', '\n').replace('/n', '\n')
    
    # 导入字幕
    # 转换十六进制颜色为RGB
    rgb_color = hex_to_rgb(font_color)

    # 创建text_border (描边)
    text_border = None
    if border_width > 0:
        text_border = draft.Text_border(
            alpha=border_alpha,
            color=hex_to_rgb(border_color),
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
    
    # 创建text_style
    text_style = draft.Text_style(
        size=font_size,
        bold=bold,
        italic=italic,
        underline=underline,
        color=rgb_color,
        align=1,  # 保持居中对齐
        vertical=vertical,  # 使用传入的vertical参数
        alpha=alpha  # 使用传入的alpha参数
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
            effect_id=effect_effect_id,
            resource_id=effect_effect_id
        )
    
    # 创建clip_settings
    clip_settings = draft.Clip_settings(
        transform_x=transform_x,
        transform_y=transform_y,
        scale_x=scale_x,
        scale_y=scale_y,
        rotation=rotation
    )

    script.import_srt(
        srt_content,
        track_name=track_name,
        time_offset=int(time_offset * 1000000),  # 将秒转换为微秒
        text_style=text_style,
        clip_settings=clip_settings,
        style_reference=style_reference,
        border=text_border,
        background=text_background,
        bubble=text_bubble,
        effect=text_effect
    )

    return {
        "draft_id": draft_id,
        "draft_url": generate_draft_url(draft_id)
    }
