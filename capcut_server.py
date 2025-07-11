import requests
from flask import Flask, request, jsonify, Response
from datetime import datetime
import pyJianYingDraft as draft
import random
import uuid
import json
import codecs
from add_audio_track import add_audio_track
from add_video_track import add_video_track
from add_text_impl import add_text_impl
from add_subtitle_impl import add_subtitle_impl
from add_image_impl import add_image_impl
from add_video_keyframe_impl import add_video_keyframe_impl
from save_draft_impl import save_draft_impl, query_task_status, query_script_impl
from add_effect_impl import add_effect_impl
from add_sticker_impl import add_sticker_impl
from create_draft import create_draft
from util import generate_draft_url as utilgenerate_draft_url

from settings.local import IS_CAPCUT_ENV, DRAFT_DOMAIN, PREVIEW_ROUTER

app = Flask(__name__)
 
@app.route('/add_video', methods=['POST'])
def add_video():
    data = request.get_json()
    # 获取必要参数
    draft_folder = data.get('draft_folder')
    video_url = data.get('video_url')
    start = data.get('start', 0)
    end = data.get('end', 0)
    width = data.get('width', 1080)
    height = data.get('height', 1920)
    draft_id = data.get('draft_id')
    transform_y = data.get('transform_y', 0)
    scale_x = data.get('scale_x', 1)
    scale_y = data.get('scale_y', 1)
    transform_x = data.get('transform_x', 0)
    speed = data.get('speed', 1.0)  # 新增速度参数
    target_start = data.get('target_start', 0)  # 新增目标开始时间参数
    track_name = data.get('track_name', "video_main")  # 新增轨道名称参数
    relative_index = data.get('relative_index', 0)  # 新增相对索引参数
    duration = data.get('duration')  # 新增时长参数
    transition = data.get('transition')  # 新增转场类型参数
    transition_duration = data.get('transition_duration', 0.5)  # 新增转场持续时间参数，默认0.5秒
    volume = data.get('volume', 1.0)  # 新增音量参数，默认1.0 
    
    # 获取蒙版相关参数
    mask_type = data.get('mask_type')  # 蒙版类型
    mask_center_x = data.get('mask_center_x', 0.5)  # 蒙版中心X坐标
    mask_center_y = data.get('mask_center_y', 0.5)  # 蒙版中心Y坐标
    mask_size = data.get('mask_size', 1.0)  # 蒙版大小，相对屏幕高度的大小
    mask_rotation = data.get('mask_rotation', 0.0)  # 蒙版旋转角度
    mask_feather = data.get('mask_feather', 0.0)  # 蒙版羽化程度
    mask_invert = data.get('mask_invert', False)  # 是否反转蒙版
    mask_rect_width = data.get('mask_rect_width')  # 矩形蒙版宽度
    mask_round_corner = data.get('mask_round_corner')  # 矩形蒙版圆角

    result = {
        "success": False,
        "output": "",
        "error": ""
    }

    # 验证必要参数
    if not video_url:
        error_message = "Hi, the required parameters 'video_url' are missing."
        result["error"] = error_message
        return jsonify(result)

    try:
        draft_result = add_video_track(
            draft_folder=draft_folder,
            video_url=video_url,
            width=width,
            height=height,
            start=start,
            end=end,
            target_start=target_start,
            draft_id=draft_id,
            transform_y=transform_y,
            scale_x=scale_x,
            scale_y=scale_y,
            transform_x=transform_x,
            speed=speed,
            track_name=track_name,
            relative_index=relative_index,
            duration=duration,
            transition=transition,  # 传入转场类型参数
            transition_duration=transition_duration,  # 传入转场持续时间参数
            volume=volume,  # 传入音量参数
            # 传入蒙版相关参数
            mask_type=mask_type,
            mask_center_x=mask_center_x,
            mask_center_y=mask_center_y,
            mask_size=mask_size,
            mask_rotation=mask_rotation,
            mask_feather=mask_feather,
            mask_invert=mask_invert,
            mask_rect_width=mask_rect_width,
            mask_round_corner=mask_round_corner
        )
        
        result["success"] = True
        result["output"] = draft_result
        return jsonify(result)

    except Exception as e:
        error_message = f"Error occurred while processing video: {str(e)}."
        result["error"] = error_message
        return jsonify(result)

@app.route('/add_audio', methods=['POST'])
def add_audio():
    data = request.get_json()
    
    # 获取必要参数
    draft_folder = data.get('draft_folder')
    audio_url = data.get('audio_url')
    start = data.get('start', 0)
    end = data.get('end', None)
    draft_id = data.get('draft_id')
    volume = data.get('volume', 1.0)  # 默认音量1.0
    target_start = data.get('target_start', 0)  # 新增目标开始时间参数
    speed = data.get('speed', 1.0)  # 新增速度参数
    track_name = data.get('track_name', 'audio_main')  # 新增轨道名称参数
    duration = data.get('duration', None)  # 新增 duration 参数
    # 音效参数分开获取
    effect_type = data.get('effect_type', None)  # 音效类型名称
    effect_params = data.get('effect_params', None)  # 音效参数列表
    width = data.get('width', 1080)
    height = data.get('height', 1920)
    
    # # 如果有音效参数，将其组合成sound_effects格式
    sound_effects = None
    if effect_type is not None:
        sound_effects = [(effect_type, effect_params)]

    result = {
        "success": False,
        "output": "",
        "error": ""
    }

    # 验证必要参数
    if not audio_url:
        error_message = "Hi, the required parameters 'audio_url' are missing."
        result["error"] = error_message
        return jsonify(result)

    try:
        # 调用修改后的 add_audio_track 方法
        draft_result = add_audio_track(
            draft_folder=draft_folder,
            audio_url=audio_url,
            start=start,
            end=end,
            target_start=target_start,
            draft_id=draft_id,
            volume=volume,
            track_name=track_name,
            speed=speed,
            sound_effects=sound_effects,  # 添加音效参数
            width=width,
            height=height,
            duration=duration  # 添加 duration 参数
        )
        
        result["success"] = True
        result["output"] = draft_result
        return jsonify(result)

    except Exception as e:
        error_message = f"Error occurred while processing audio: {str(e)}."
        result["error"] = error_message
        return jsonify(result)

@app.route('/create_draft', methods=['POST'])
def create_draft_service():
    data = request.get_json()
    
    # 获取参数
    width = data.get('width', 1080)
    height = data.get('height', 1920)
    
    result = {
        "success": False,
        "output": "",
        "error": ""
    }
    
    try:
        # 创建新草稿
        script, draft_id = create_draft(width=width, height=height)
        
        result["success"] = True
        result["output"] = {
            "draft_id": draft_id,
            "draft_url": utilgenerate_draft_url(draft_id)
        }
        return jsonify(result)
        
    except Exception as e:
        error_message = f"Error occurred while creating draft: {str(e)}."
        result["error"] = error_message
        return jsonify(result)
        
@app.route('/add_subtitle', methods=['POST'])
def add_subtitle():
    data = request.get_json()
    
    # 获取必要参数
    srt = data.get('srt')  # 字幕内容或URL
    draft_id = data.get('draft_id')
    time_offset = data.get('time_offset', 0.0)  # 默认0秒
    
    # 字体样式参数
    font_size = data.get('font_size', 5.0)  # 默认大小5.0
    bold = data.get('bold', False)  # 默认不加粗
    italic = data.get('italic', False)  # 默认不斜体
    underline = data.get('underline', False)  # 默认不下划线
    font_color = data.get('font_color', '#FFFFFF')  # 默认白色
    vertical = data.get('vertical', False)  # 新增：是否垂直显示，默认False
    alpha = data.get('alpha', 1)  # 新增：透明度，默认1
    # 边框参数
    border_alpha = data.get('border_alpha', 1.0)
    border_color = data.get('border_color', '#000000')
    border_width = data.get('border_width', 0.0)
    
    # 背景参数
    background_color = data.get('background_color', '#000000')
    background_style = data.get('background_style', 0)
    background_alpha = data.get('background_alpha', 0.0)
        
    # 图像调节参数
    transform_x = data.get('transform_x', 0.0)  # 默认0
    transform_y = data.get('transform_y', -0.8)  # 默认-0.8
    scale_x = data.get('scale_x', 1.0)  # 默认1.0
    scale_y = data.get('scale_y', 1.0)  # 默认1.0
    rotation = data.get('rotation', 0.0)  # 默认0.0
    track_name = data.get('track_name', 'subtitle')  # 默认轨道名称为'subtitle'
    width = data.get('width', 1080)
    height = data.get('height', 1920)

    result = {
        "success": False,
        "output": "",
        "error": ""
    }

    # 验证必要参数
    if not srt:
        error_message = "Hi, the required parameters 'srt' are missing."
        result["error"] = error_message
        return jsonify(result)

    try:
        # 调用 add_subtitle_impl 方法
        draft_result = add_subtitle_impl(
            srt_path=srt,
            draft_id=draft_id,
            track_name=track_name,
            time_offset=time_offset,
            # 字体样式参数
            font_size=font_size,
            bold=bold,
            italic=italic,
            underline=underline,
            font_color=font_color,
            vertical=vertical,  # 新增：传递vertical参数
            alpha=alpha,  # 新增：传递alpha参数
            border_alpha=border_alpha,
            border_color=border_color,
            border_width=border_width,
            background_color=background_color,
            background_style=background_style,
            background_alpha=background_alpha,
            # 图像调节参数
            transform_x=transform_x,
            transform_y=transform_y,
            scale_x=scale_x,
            scale_y=scale_y,
            rotation=rotation,
            width=width,
            height=height
        )
        
        result["success"] = True
        result["output"] = draft_result
        return jsonify(result)

    except Exception as e:
        error_message = f"Error occurred while processing subtitle: {str(e)}."
        result["error"] = error_message
        return jsonify(result)

@app.route('/add_text', methods=['POST'])
def add_text():
    data = request.get_json()
    
    # 获取必要参数
    text = data.get('text')
    start = data.get('start', 0)
    end = data.get('end', 5)
    draft_id = data.get('draft_id')
    transform_y = data.get('transform_y', 0)
    transform_x = data.get('transform_x', 0)
    font = data.get('font', "文轩体")
    font_color = data.get('font_color', "#FF0000")
    font_size = data.get('font_size', 8.0)
    track_name = data.get('track_name', "text_main")
    vertical = data.get('vertical', False)
    font_alpha = data.get('font_alpha', 1.0)  
    outro_animation = data.get('outro_animation', None)
    outro_duration = data.get('outro_duration', 0.5)
    track_name = data.get('track_name', 'text_main')
    width = data.get('width', 1080)
    height = data.get('height', 1920)
    
    # 新增固定宽高参数 
    fixed_width = data.get('fixed_width', -1)
    fixed_height = data.get('fixed_height', -1)
    
    # 描边参数
    border_alpha = data.get('border_alpha', 1.0)
    border_color = data.get('border_color', "#000000")
    border_width = data.get('border_width', 0.0)
    
    # 背景参数
    background_color = data.get('background_color', "#000000")
    background_style = data.get('background_style', 0)
    background_alpha = data.get('background_alpha', 0.0)
    
    # 气泡和花字效果
    bubble_effect_id = data.get('bubble_effect_id')
    bubble_resource_id = data.get('bubble_resource_id')
    effect_effect_id = data.get('effect_effect_id')
    
    # 入场动画
    intro_animation = data.get('intro_animation')
    intro_duration = data.get('intro_duration', 0.5)
    
    # 出场动画
    outro_animation = data.get('outro_animation')
    outro_duration = data.get('outro_duration', 0.5)

    result = {
        "success": False,
        "output": "",
        "error": ""
    }

    # 验证必要参数
    if not text or start is None or end is None:
        error_message = "Hi, the required parameters 'text', 'start' or 'end' are missing. "
        result["error"] = error_message
        return jsonify(result)

    try:
        
        # 调用 add_text_impl 方法
        draft_result = add_text_impl(
            text=text,
            start=start,
            end=end,
            draft_id=draft_id,
            transform_y=transform_y,
            transform_x=transform_x,
            font=font,
            font_color=font_color,
            font_size=font_size,
            track_name=track_name,
            vertical=vertical,
            font_alpha=font_alpha,
            border_alpha=border_alpha,
            border_color=border_color,
            border_width=border_width,
            background_color=background_color,
            background_style=background_style,
            background_alpha=background_alpha,
            bubble_effect_id=bubble_effect_id,
            bubble_resource_id=bubble_resource_id,
            effect_effect_id=effect_effect_id,
            intro_animation=intro_animation,
            intro_duration=intro_duration,
            outro_animation=outro_animation,
            outro_duration=outro_duration,
            width=width,
            height=height,
            fixed_width=fixed_width,
            fixed_height=fixed_height
        )
        
        result["success"] = True
        result["output"] = draft_result
        return jsonify(result)

    except Exception as e:
        if is_chinese:
            error_message = f"处理文本时出错啦：{str(e)}。您可以点击下面的链接寻求帮助："
        else:
            error_message = f"Error occurred while processing text: {str(e)}. You can click the link below for help: "
        result["error"] = error_message + purchase_link
        return jsonify(result)

@app.route('/add_image', methods=['POST'])
def add_image():
    data = request.get_json()
    
    # 获取必要参数
    draft_folder = data.get('draft_folder')
    image_url = data.get('image_url')
    width = data.get('width', 1080)
    height = data.get('height', 1920)
    start = data.get('start', 0)
    end = data.get('end', 3.0)  # 默认显示3秒
    draft_id = data.get('draft_id')
    transform_y = data.get('transform_y', 0)
    scale_x = data.get('scale_x', 1)
    scale_y = data.get('scale_y', 1)
    transform_x = data.get('transform_x', 0)
    track_name = data.get('track_name', "image_main")  # 默认轨道名称
    relative_index = data.get('relative_index', 0)  # 新增轨道渲染顺序索引参数 
    animation = data.get('animation')  # 入场动画参数（向后兼容）
    animation_duration = data.get('animation_duration', 0.5)  # 入场动画持续时间
    intro_animation = data.get('intro_animation')  # 新增入场动画参数，优先级高于animation
    intro_animation_duration = data.get('intro_animation_duration', 0.5)
    outro_animation = data.get('outro_animation')  # 新增出场动画参数
    outro_animation_duration = data.get('outro_animation_duration', 0.5)  # 新增出场动画持续时间
    combo_animation = data.get('combo_animation')  # 新增组合动画参数
    combo_animation_duration = data.get('combo_animation_duration', 0.5)  # 新增组合动画持续时间
    transition = data.get('transition')  # 转场类型参数
    transition_duration = data.get('transition_duration', 0.5)  # 转场持续时间参数，默认0.5秒
    
    # 新增蒙版相关参数 
    mask_type = data.get('mask_type')  # 蒙版类型
    mask_center_x = data.get('mask_center_x', 0.0)  # 蒙版中心点X坐标
    mask_center_y = data.get('mask_center_y', 0.0)  # 蒙版中心点Y坐标
    mask_size = data.get('mask_size', 0.5)  # 蒙版主要尺寸，相对画布高度
    mask_rotation = data.get('mask_rotation', 0.0)  # 蒙版旋转角度
    mask_feather = data.get('mask_feather', 0.0)  # 蒙版羽化参数
    mask_invert = data.get('mask_invert', False)  # 是否反转蒙版
    mask_rect_width = data.get('mask_rect_width')  # 矩形蒙版宽度
    mask_round_corner = data.get('mask_round_corner')  # 矩形蒙版圆角

    result = {
        "success": False,
        "output": "",
        "error": ""
    }

    # 验证必要参数
    if not image_url:
        error_message = "Hi, the required parameters 'image_url' are missing."
        result["error"] = error_message
        return jsonify(result)

    try:
        draft_result = add_image_impl(
            draft_folder=draft_folder,
            image_url=image_url,
            width=width,
            height=height,
            start=start,
            end=end,
            draft_id=draft_id,
            transform_y=transform_y,
            scale_x=scale_x,
            scale_y=scale_y,
            transform_x=transform_x,
            track_name=track_name,
            relative_index=relative_index,  # 传入轨道渲染顺序索引参数
            animation=animation,  # 传入入场动画参数（向后兼容）
            animation_duration=animation_duration,  # 传入入场动画持续时间
            intro_animation=intro_animation,  # 传入新的入场动画参数
            intro_animation_duration=intro_animation_duration,
            outro_animation=outro_animation,  # 传入出场动画参数
            outro_animation_duration=outro_animation_duration,  # 传入出场动画持续时间
            combo_animation=combo_animation,  # 传入组合动画参数
            combo_animation_duration=combo_animation_duration,  # 传入组合动画持续时间
            transition=transition,  # 传入转场类型参数
            transition_duration=transition_duration,  # 传入转场持续时间参数（秒）
            # 传入蒙版相关参数
            mask_type=mask_type,
            mask_center_x=mask_center_x,
            mask_center_y=mask_center_y,
            mask_size=mask_size,
            mask_rotation=mask_rotation,
            mask_feather=mask_feather,
            mask_invert=mask_invert,
            mask_rect_width=mask_rect_width,
            mask_round_corner=mask_round_corner
        )
        
        result["success"] = True
        result["output"] = draft_result
        return jsonify(result)

    except Exception as e:
        error_message = f"Error occurred while processing image: {str(e)}."
        result["error"] = error_message
        return jsonify(result)

@app.route('/add_video_keyframe', methods=['POST'])
def add_video_keyframe():
    data = request.get_json()
    
    # 获取必要参数
    draft_id = data.get('draft_id')
    track_name = data.get('track_name', 'video_main')  # 默认主轨道
    
    # 单个关键帧参数（向后兼容）
    property_type = data.get('property_type', 'alpha')  # 默认不透明度
    time = data.get('time', 0.0)  # 默认0秒
    value = data.get('value', '1.0')  # 默认值1.0
    
    # 批量关键帧参数（新增）
    property_types = data.get('property_types')  # 属性类型列表
    times = data.get('times')  # 时间列表
    values = data.get('values')  # 值列表

    result = {
        "success": False,
        "output": "",
        "error": ""
    }

    try:
        # 调用 add_video_keyframe_impl 方法
        draft_result = add_video_keyframe_impl(
            draft_id=draft_id,
            track_name=track_name,
            property_type=property_type,
            time=time,
            value=value,
            property_types=property_types,
            times=times,
            values=values
        )
        
        result["success"] = True
        result["output"] = draft_result
        return jsonify(result)

    except Exception as e:
        error_message = f"Error occurred while adding keyframe: {str(e)}."
        result["error"] = error_message
        return jsonify(result)

@app.route('/add_effect', methods=['POST'])
def add_effect():
    data = request.get_json()
    
    # 获取必要参数
    effect_type = data.get('effect_type')  # 特效类型名称，将从Video_scene_effect_type或Video_character_effect_type中匹配
    start = data.get('start', 0)  # 开始时间（秒），默认0
    end = data.get('end', 3.0)  # 结束时间（秒），默认3秒
    draft_id = data.get('draft_id')  # 草稿ID，如果为None或找不到对应的zip文件，则创建新草稿
    track_name = data.get('track_name', "effect_01")  # 轨道名称，当特效轨道仅有一条时可省略
    params = data.get('params')  # 特效参数列表，参数列表中未提供或为None的项使用默认值
    width = data.get('width', 1080)
    height = data.get('height', 1920)

    result = {
        "success": False,
        "output": "",
        "error": ""
    }

    # 验证必要参数
    if not effect_type:
        error_message = "Hi, the required parameters 'effect_type' are missing. Please add them and try again."
        result["error"] = error_message
        return jsonify(result)

    try:
        # 调用 add_effect_impl 方法
        draft_result = add_effect_impl(
            effect_type=effect_type,
            start=start,
            end=end,
            draft_id=draft_id,
            track_name=track_name,
            params=params,
            width=width,
            height=height
        )
        
        result["success"] = True
        result["output"] = draft_result
        return jsonify(result)

    except Exception as e:
        error_message = f"Error occurred while adding effect: {str(e)}. "
        result["error"] = error_message
        return jsonify(result)

@app.route('/query_script', methods=['POST'])
def query_script():
    data = request.get_json()

    # 获取必要参数
    draft_id = data.get('draft_id')
    force_update = data.get('force_update', True)
    
    result = {
        "success": False,
        "output": "",
        "error": ""
    }

    # 验证必要参数
    if not draft_id:
        error_message = "Hi, the required parameter 'draft_id' is missing. Please add it and try again."
        result["error"] = error_message
        return jsonify(result)

    try:
        # 调用 query_script_impl 方法
        script = query_script_impl(draft_id=draft_id, force_update=force_update)
        
        if script is None:
            error_message = f"Draft {draft_id} does not exist in cache."
            result["error"] = error_message
            return jsonify(result)
        
        # 将脚本对象转换为JSON可序列化的字典
        script_str = script.dumps()
        
        result["success"] = True
        result["output"] = script_str
        return jsonify(result)

    except Exception as e:
        error_message = f"Error occurred while querying script: {str(e)}. "
        result["error"] = error_message
        return jsonify(result)

@app.route('/save_draft', methods=['POST'])
def save_draft():
    data = request.get_json()
    
    # 获取必要参数
    draft_id = data.get('draft_id')
    draft_folder = data.get('draft_folder')  # 草稿文件夹参数
    
    result = {
        "success": False,
        "output": "",
        "error": ""
    }
    
    # 验证必要参数
    if not draft_id:
        error_message = "Hi, the required parameter 'draft_id' is missing. Please add it and try again."
        result["error"] = error_message
        return jsonify(result)
    
    try:
        # 调用 save_draft_impl 方法，启动后台任务
        draft_result = save_draft_impl(draft_id, draft_folder)
        
        result["success"] = True
        result["output"] = draft_result
        return jsonify(result)
        
    except Exception as e:
        error_message = f"Error occurred while saving draft: {str(e)}. "
        result["error"] = error_message
        return jsonify(result)

# 添加新的查询状态接口
@app.route('/query_draft_status', methods=['POST'])
def query_draft_status():
    data = request.get_json()
    
    # 获取必要参数
    task_id = data.get('task_id')
    
    result = {
        "success": False,
        "output": "",
        "error": ""
    }
    
    # 验证必要参数
    if not task_id:
        error_message = "Hi, the required parameter 'task_id' is missing. Please add it and try again."
        result["error"] = error_message
        return jsonify(result)
    
    try:
        # 获取任务状态
        task_status = query_task_status(task_id)
        
        if task_status["status"] == "not_found":
            error_message = f"Task with ID {task_id} not found. Please check if the task ID is correct."
            result["error"] = error_message
            return jsonify(result)
        
        result["success"] = True
        result["output"] = task_status
        return jsonify(result)
        
    except Exception as e:
        error_message = f"Error occurred while querying task status: {str(e)}."
        result["error"] = error_message
        return jsonify(result)

@app.route('/generate_draft_url', methods=['POST'])
def generate_draft_url():
    data = request.get_json()
    
    # 获取必要参数
    draft_id = data.get('draft_id')
    draft_folder = data.get('draft_folder')  # 新增draft_folder参数
    
    result = {
        "success": False,
        "output": "",
        "error": ""
    }
    
    # 验证必要参数
    if not draft_id:
        error_message = "Hi, the required parameter 'draft_id' is missing. Please add it and try again."
        result["error"] = error_message
        return jsonify(result)
    
    try:
        draft_result = { "draft_url" : f"{DRAFT_DOMAIN}{PREVIEW_ROUTER}?={draft_id}"}
        
        result["success"] = True
        result["output"] = draft_result
        return jsonify(result)
        
    except Exception as e:
        error_message = f"Error occurred while saving draft: {str(e)}."
        result["error"] = error_message
        return jsonify(result)

@app.route('/add_sticker', methods=['POST'])
def add_sticker():
    data = request.get_json()
    # 获取必要参数
    resource_id = data.get('sticker_id')
    start = data.get('start', 0)
    end = data.get('end', 5.0)  # 默认显示5秒
    draft_id = data.get('draft_id')
    transform_y = data.get('transform_y', 0)
    transform_x = data.get('transform_x', 0)
    alpha = data.get('alpha', 1.0)
    flip_horizontal = data.get('flip_horizontal', False)
    flip_vertical = data.get('flip_vertical', False)
    rotation = data.get('rotation', 0.0)
    scale_x = data.get('scale_x', 1.0)
    scale_y = data.get('scale_y', 1.0)
    track_name = data.get('track_name', 'sticker_main')
    relative_index = data.get('relative_index', 0)
    width = data.get('width', 1080)
    height = data.get('height', 1920)

    result = {
        "success": False,
        "output": "",
        "error": ""
    }

    # 验证必要参数
    if not resource_id:
        error_message = "Hi, the required parameter 'sticker_id' is missing. Please add it and try again. "
        result["error"] = error_message
        return jsonify(result)

    try:
        # 调用 add_sticker_impl 方法
        draft_result = add_sticker_impl(
            resource_id=resource_id,
            start=start,
            end=end,
            draft_id=draft_id,
            transform_y=transform_y,
            transform_x=transform_x,
            alpha=alpha,
            flip_horizontal=flip_horizontal,
            flip_vertical=flip_vertical,
            rotation=rotation,
            scale_x=scale_x,
            scale_y=scale_y,
            track_name=track_name,
            relative_index=relative_index,
            width=width,
            height=height
        )

        result["success"] = True
        result["output"] = draft_result
        return jsonify(result)

    except Exception as e:
        error_message = f"Error occurred while adding sticker: {str(e)}. "
        result["error"] = error_message
        return jsonify(result)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9000)