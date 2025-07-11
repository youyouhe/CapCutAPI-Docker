# 导入必要的模块
import os
import pyJianYingDraft as draft
import time
from util import generate_draft_url, is_windows_path, url_to_hash
import re
from typing import Optional, Dict, Tuple, List
from pyJianYingDraft import exceptions, Audio_scene_effect_type, Tone_effect_type, Speech_to_song_type, CapCut_Voice_filters_effect_type,CapCut_Voice_characters_effect_type,CapCut_Speech_to_song_effect_type, trange
from create_draft import get_or_create_draft
from settings.local import IS_CAPCUT_ENV

def add_audio_track(
    audio_url: str,
    draft_folder: Optional[str] = None,
    start: float = 0,
    end: Optional[float] = None,
    target_start: float = 0,
    draft_id: Optional[str] = None,
    volume: float = 1.0,
    track_name: str = "audio_main",
    speed: float = 1.0,
    sound_effects: Optional[List[Tuple[str, Optional[List[Optional[float]]]]]]=None,
    width: int = 1080,
    height: int = 1920,
    duration: Optional[float] = None  # 新增 duration 参数
) -> Dict[str, str]:
    """
    向指定草稿添加音频轨道
    :param draft_folder: 草稿文件夹路径，可选参数
    :param audio_url: 音频URL
    :param start: 开始时间（秒），默认0
    :param end: 结束时间（秒），默认None（使用音频总时长）
    :param target_start: 目标轨道的插入位置（秒），默认0
    :param draft_id: 草稿ID，如果为None或找不到对应的zip文件，则创建新草稿
    :param volume: 音量大小，范围0.0-1.0，默认1.0
    :param track_name: 轨道名称，默认"audio_main"
    :param speed: 播放速度，默认1.0
    :param sound_effects: 场景音效果列表，每个元素是一个元组，包含效果类型名称和参数列表，默认None
    :return: 更新后的草稿信息
    """
    # 获取或创建草稿
    draft_id, script = get_or_create_draft(
        draft_id=draft_id,
        width=width,
        height=height
    )
    
    # 添加音频轨道（仅当轨道不存在时）
    if track_name is not None:
        try:
            imported_track = script.get_imported_track(draft.Track_type.audio, name=track_name)
            # 如果没有抛出异常，说明轨道已存在
        except exceptions.TrackNotFound:
            # 轨道不存在，创建新轨道
            script.add_track(draft.Track_type.audio, track_name=track_name)
    else:
       script.add_track(draft.Track_type.audio)

    # 如果传递了 duration 参数，优先使用它；否则使用默认音频时长0秒，在下载时，才会获取真实时长
    if duration is not None:
        # 使用传递进来的 duration，跳过时长获取和检查
        audio_duration = duration
    else:
        # 使用默认音频时长0秒，在下载草稿时，才会获取真实时长
        audio_duration = 0.0  # 默认音频时长为0秒
        # duration_result = get_video_duration(audio_url)  # 复用视频时长获取函数
        # if not duration_result["success"]:
        #     print(f"获取音频时长失败: {duration_result['error']}")
        
        # # 检查音频时长是否超过10分钟
        # if duration_result["output"] > 600:  # 600秒 = 10分钟
        #     raise Exception(f"音频时长超过10分钟限制，当前时长: {duration_result['output']}秒")
        
        # audio_duration = duration_result["output"]
    
    # 下载音频到本地
    # local_audio_path = download_audio(audio_url, draft_dir)

    material_name = f"audio_{url_to_hash(audio_url)}.mp3"  # 使用原始文件名+时间戳+固定mp3扩展名
    
    # 构建draft_audio_path
    draft_audio_path = None
    if draft_folder:
        if is_windows_path(draft_folder):
            # Windows路径处理
            windows_drive, windows_path = re.match(r'([a-zA-Z]:)(.*)', draft_folder).groups()
            parts = [p for p in windows_path.split('\\') if p]
            draft_audio_path = os.path.join(windows_drive, *parts, draft_id, "assets", "audio", material_name)
            # 规范化路径（确保分隔符一致）
            draft_audio_path = draft_audio_path.replace('/', '\\')
        else:
            # macOS/Linux路径处理
            draft_audio_path = os.path.join(draft_folder, draft_id, "assets", "audio", material_name)
    
    # 设置音频结束时间的默认值
    audio_end = end if end is not None else audio_duration
    
    # 计算音频时长
    duration = audio_end - start
    
    # 创建音频片段
    if draft_audio_path:
        print('replace_path:', draft_audio_path)
        audio_material = draft.Audio_material(replace_path=draft_audio_path, remote_url=audio_url, material_name=material_name, duration=audio_duration)
    else:
        audio_material = draft.Audio_material(remote_url=audio_url, material_name=material_name, duration=audio_duration)
    audio_segment = draft.Audio_segment(
        audio_material,  # 传入素材对象
        target_timerange=trange(f"{target_start}s", f"{duration}s"),  # 使用target_start和duration
        source_timerange=trange(f"{start}s", f"{duration}s"),
        speed=speed,  # 设置播放速度
        volume=volume  # 设置音量
    )
    
    # 添加场景音效果
    if sound_effects:
        for effect_name, params in sound_effects:
            # 根据IS_CAPCUT_ENV选择不同的效果类型
            effect_type = None
            
            if IS_CAPCUT_ENV:
                # CapCut环境下，查找CapCut_Voice_filters_effect_type中的效果
                effect_type = getattr(CapCut_Voice_filters_effect_type, effect_name)
                # 如果在Voice_filters中没找到，可以继续在其他CapCut效果类型中查找
                if effect_type is None:
                    # 查找CapCut_Voice_characters_effect_type中的效果
                    effect_type = getattr(CapCut_Voice_characters_effect_type, effect_name)
                # 如果仍未找到，查找CapCut_Speech_to_song_effect_type中的效果
                if effect_type is None:
                    effect_type = getattr(CapCut_Speech_to_song_effect_type, effect_name)
            else:
                # 剪映环境下，查找Audio_scene_effect_type中的效果
                effect_type = getattr(Audio_scene_effect_type, effect_name)
                # 如果在Audio_scene_effect_type中没找到，可以继续在其他效果类型中查找
                if effect_type is None:
                    effect_type = getattr(Tone_effect_type, effect_name)
                # 如果仍未找到，查找Speech_to_song_type中的效果
                if effect_type is None:
                    effect_type = getattr(Speech_to_song_type, effect_name)
                # 这里可以根据需要添加其他效果类型的查找逻辑
            
            # 如果找到了对应的效果类型，则添加到音频片段
            if effect_type:
                audio_segment.add_effect(effect_type, params)
            else:
                print(f"警告: 未找到名为 {effect_name} 的音频效果")
    
    # 添加音频片段到轨道
    script.add_segment(audio_segment, track_name=track_name)
    
    return {
        "draft_id": draft_id,
        "draft_url": generate_draft_url(draft_id)
    }
