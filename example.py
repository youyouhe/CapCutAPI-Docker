import requests
import json
import sys
import time
from util import timing_decorator
import functools
import threading


# 服务的基础URL，请根据实际情况修改
BASE_URL = "http://localhost:9000"
LICENSE_KEY = "539C3FEB-74AE48D4-A964D52B-C520F801"  # 使用体验版license key'

def make_request(endpoint, data, method='POST'):
    """发送HTTP请求到服务端并处理响应"""
    url = f"{BASE_URL}/{endpoint}"
    headers = {'Content-Type': 'application/json'}
    
    try:
        if method == 'POST':
            response = requests.post(url, data=json.dumps(data), headers=headers)
        elif method == 'GET':
            response = requests.get(url, params=data, headers=headers)
        else:
            raise ValueError(f"不支持的HTTP方法: {method}")
            
        response.raise_for_status()  # 如果请求失败，抛出异常
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"请求错误: {e}")
        sys.exit(1)
    except json.JSONDecodeError:
        print("无法解析服务器响应")
        sys.exit(1)

def add_audio_track(audio_url, start, end, target_start, volume=1.0, 
                    speed=1.0, track_name="main_audio", effect_type=None, effect_params=None, draft_id=None):
    """添加音频轨道的API调用"""
    data = {
        "license_key": LICENSE_KEY,  # 使用体验版license key
        "audio_url": audio_url,
        "start": start,
        "end": end,
        "target_start": target_start,
        "volume": volume,
        "speed": speed,
        "track_name": track_name,
        "effect_type": effect_type,
        "effect_params": effect_params
    }
    
    if draft_id:
        data["draft_id"] = draft_id
        
    return make_request("add_audio", data)

def add_text_impl(text, start, end, font, font_color, font_size, track_name,draft_folder="123", draft_id=None,
                  vertical=False, transform_x=0.5, transform_y=0.5, font_alpha=1.0,
                  border_color=None, border_width=0.0, border_alpha=1.0,
                  background_color=None, background_alpha=1.0, background_style=None,
                  bubble_effect_id=None, bubble_resource_id=None,
                  effect_effect_id=None, outro_animation=None):
    """添加文本的API调用"""
    data = {
        "license_key": LICENSE_KEY,  # 使用体验版license key
        "draft_folder": draft_folder,
        "text": text,
        "start": start,
        "end": end,
        "font": font,
        "color": font_color,
        "size": font_size,
        "alpha": font_alpha,
        "track_name": track_name,
        "vertical": vertical,
        "transform_x": transform_x,
        "transform_y": transform_y
    }
    
    # 添加描边参数
    if border_color:
        data["border_color"] = border_color
        data["border_width"] = border_width
        data["border_alpha"] = border_alpha
    
    # 添加背景参数
    if background_color:
        data["background_color"] = background_color
        data["background_alpha"] = background_alpha
        if background_style:
            data["background_style"] = background_style
    
    # 添加气泡效果参数
    if bubble_effect_id:
        data["bubble_effect_id"] = bubble_effect_id
        if bubble_resource_id:
            data["bubble_resource_id"] = bubble_resource_id
    
    # 添加花字效果参数
    if effect_effect_id:
        data["effect_effect_id"] = effect_effect_id
    
    if draft_id:
        data["draft_id"] = draft_id
        
    if outro_animation:
        data["outro_animation"] = outro_animation
        
    return make_request("add_text", data)

def add_image_impl(image_url, width, height, start, end, track_name, draft_id=None,
                  transform_x=0, transform_y=0, scale_x=1.0, scale_y=1.0, transition=None, transition_duration=None,
                  # 新增蒙版相关参数
                  mask_type=None, mask_center_x=0.0, mask_center_y=0.0, mask_size=0.5,
                  mask_rotation=0.0, mask_feather=0.0, mask_invert=False,
                  mask_rect_width=None, mask_round_corner=None):
    """添加图片的API调用"""
    data = {
        "license_key": LICENSE_KEY,  # 使用体验版license key
        "image_url": image_url,
        "width": width,
        "height": height,
        "start": start,
        "end": end,
        "track_name": track_name,
        "transform_x": transform_x,
        "transform_y": transform_y,
        "scale_x": scale_x,
        "scale_y": scale_y,
        "transition": transition,
        "transition_duration": transition_duration or 0.5,  # 默认转场持续时间为0.5秒
        # 添加蒙版相关参数
        "mask_type": mask_type,
        "mask_center_x": mask_center_x,
        "mask_center_y": mask_center_y,
        "mask_size": mask_size,
        "mask_rotation": mask_rotation,
        "mask_feather": mask_feather,
        "mask_invert": mask_invert,
        "mask_rect_width": mask_rect_width,
        "mask_round_corner": mask_round_corner
    }
    
    if draft_id:
        data["draft_id"] = draft_id
        
    return make_request("add_image", data)

def generate_image_impl(prompt, width, height, start, end, track_name, draft_id=None,
                  transform_x=0, transform_y=0, scale_x=1.0, scale_y=1.0, transition=None, transition_duration=None):
    """添加图片的API调用"""
    data = {
        "license_key": LICENSE_KEY,  # 使用体验版license key
        "prompt": prompt,
        "width": width,
        "height": height,
        "start": start,
        "end": end,
        "track_name": track_name,
        "transform_x": transform_x,
        "transform_y": transform_y,
        "scale_x": scale_x,
        "scale_y": scale_y,
        "transition": transition,
        "transition_duration": transition_duration or 0.5  # 默认转场持续时间为0.5秒
    }
    
    if draft_id:
        data["draft_id"] = draft_id
        
    return make_request("generate_image", data)

def add_sticker_impl(resource_id, start, end, draft_id=None, transform_x=0, transform_y=0,
                    alpha=1.0, flip_horizontal=False, flip_vertical=False, rotation=0.0,
                    scale_x=1.0, scale_y=1.0, track_name="sticker_main", relative_index=0,
                    width=1080, height=1920):
    """添加贴纸的API调用"""
    data = {
        "license_key": LICENSE_KEY,  # 使用体验版license key
        "sticker_id": resource_id,
        "start": start,
        "end": end,
        "transform_x": transform_x,
        "transform_y": transform_y,
        "alpha": alpha,
        "flip_horizontal": flip_horizontal,
        "flip_vertical": flip_vertical,
        "rotation": rotation,
        "scale_x": scale_x,
        "scale_y": scale_y,
        "track_name": track_name,
        "relative_index": relative_index,
        "width": width,
        "height": height
    }
    
    if draft_id:
        data["draft_id"] = draft_id
        
    return make_request("add_sticker", data)

def add_video_keyframe_impl(draft_id, track_name, property_type=None, time=None, value=None, 
                           property_types=None, times=None, values=None):
    """添加视频关键帧的API调用
    
    支持两种模式：
    1. 单个关键帧：使用 property_type, time, value 参数
    2. 批量关键帧：使用 property_types, times, values 参数（列表形式）
    """
    data = {
        "license_key": LICENSE_KEY,  # 使用体验版license key
        "draft_id": draft_id,
        "track_name": track_name
    }
    
    # 添加单个关键帧参数（如果提供）
    if property_type is not None:
        data["property_type"] = property_type
    if time is not None:
        data["time"] = time
    if value is not None:
        data["value"] = value
    
    # 添加批量关键帧参数（如果提供）
    if property_types is not None:
        data["property_types"] = property_types
    if times is not None:
        data["times"] = times
    if values is not None:
        data["values"] = values
    
    return make_request("add_video_keyframe", data)

def add_video_impl(video_url, start=None, end=None, width=None, height=None, track_name="main",
                   draft_id=None, transform_y=0, scale_x=1, scale_y=1, transform_x=0,
                   speed=1.0, target_start=0, relative_index=0, transition=None, transition_duration=None,
                   # 蒙版相关参数
                   mask_type=None, mask_center_x=0.5, mask_center_y=0.5, mask_size=1.0,
                   mask_rotation=0.0, mask_feather=0.0, mask_invert=False,
                   mask_rect_width=None, mask_round_corner=None):
    """添加视频轨道的API调用"""
    data = {
        "license_key": LICENSE_KEY,  # 使用体验版license key
        "video_url": video_url,
        "height": height,
        "track_name": track_name,
        "transform_y": transform_y,
        "scale_x": scale_x,
        "scale_y": scale_y,
        "transform_x": transform_x,
        "speed": speed,
        "target_start": target_start,
        "relative_index": relative_index,
        "transition": transition,
        "transition_duration": transition_duration or 0.5,  # 默认转场持续时间为0.5秒
        # 蒙版相关参数
        "mask_type": mask_type,
        "mask_center_x": mask_center_x,
        "mask_center_y": mask_center_y,
        "mask_size": mask_size,
        "mask_rotation": mask_rotation,
        "mask_feather": mask_feather,
        "mask_invert": mask_invert,
        "mask_rect_width": mask_rect_width,
        "mask_round_corner": mask_round_corner
    }
    if start:
        data["start"] = start
    if end:
        data["end"] = end
    if width:
        data["width"] = width
    if height:
        data["height"] = height
    return make_request("add_video", data)

def add_effect(effect_type, start, end, draft_id=None, track_name="effect_01",
              params=None, width=1080, height=1920):
    """添加特效的API调用"""
    data = {
        "license_key": LICENSE_KEY,  # 使用体验版license key
        "effect_type": effect_type,
        "start": start,
        "end": end,
        "track_name": track_name,
        "params": params or [],
        "width": width,
        "height": height
    }
    
    if draft_id:
        data["draft_id"] = draft_id
        
    return make_request("add_effect", data)

def test_effect_01():
    """测试添加特效的服务"""
    # draft_folder = "/Users/sunguannan/Movies/JianyingPro/User Data/Projects/com.lveditor.draft"
    draft_folder = "/Users/sunguannan/Movies/CapCut/User Data/Projects/com.lveditor.draft"
    
    print("\n测试：添加特效")
    effect_result = add_effect(
        start=0,
        end=5,
        track_name="effect_01",
        # effect_type="金粉闪闪",  # 示例使用发光特效
        effect_type="Gold_Sparkles",
        params=[100, 50, 34]  # 示例参数，根据具体特效类型而定
    )
    print(f"特效添加结果: {effect_result}")
    print(save_draft_impl(effect_result['output']['draft_id'], draft_folder))
    
    # 如果需要可以在这里继续添加其他测试案例
    
    # 返回第一个测试结果用于后续操作（如果有的话）
    return effect_result


def test_text():
    """测试添加文本"""
    draft_folder = "/Users/sunguannan/Movies/JianyingPro/User Data/Projects/com.lveditor.draft"

    # 测试用例1：基本文本添加
    print("\n测试：添加基本文本")
    text_result = add_text_impl(
        text="你好，我是剪映助手",
        start=0,
        end=3,
        font="思源中宋",
        font_color="#FF0000",  # 红色
        track_name="main_text",
        transform_y=0.8,
        transform_x=0.5,
        font_size=30.0
    )
    print("测试用例1（基本文本）成功:", text_result)

    # 测试用例2：竖排文本
    result2 = add_text_impl(
        draft_id=text_result['output']['draft_id'],
        text="竖排文本演示",
        start=3,
        end=6,
        font="云书法三行魏碑体",
        font_color="#00FF00",  # 绿色
        font_size=8.0,
        track_name="main_text",
        vertical=True,  # 启用竖排
        transform_y=-0.5,
        outro_animation='晕开'
    )
    print("测试用例2（竖排文本）成功:", result2)

    # 测试用例3：带描边和背景的文本
    result3 = add_text_impl(
        draft_id=result2['output']['draft_id'],
        text="描边和背景测试",
        start=6,
        end=9,
        font="思源中宋",
        font_color="#FFFFFF",  # 白色文字
        font_size=24.0,
        track_name="main_text",
        transform_y=0.0,
        transform_x=0.5,
        border_color="#FF0000",  # 黑色描边
        border_width=20.0,
        border_alpha=1.0,
        background_color="#0000FF",  # 蓝色背景
        background_alpha=0.5,  # 半透明背景
        background_style=0  # 气泡样式背景
    )
    print("测试用例3（描边和背景）成功:", result3)
    
    # 最后保存并上传草稿
    if result3.get('success') and result3.get('output'):
        save_result = save_draft_impl(result3['output']['draft_id'],draft_folder)
        print(f"草稿保存结果: {save_result}")
    
    # 返回最后一个测试结果用于后续操作（如果有的话）
    return result3


def test_image01():
    """测试添加图片"""
    # draft_folder = "/Users/sunguannan/Movies/JianyingPro/User Data/Projects/com.lveditor.draft"
    draft_folder = "/Users/sunguannan/Movies/CapCut/User Data/Projects/com.lveditor.draft"

    print("\n测试：添加图片1")
    image_result = add_image_impl(
        image_url="https://cdn.wanx.aliyuncs.com/wanx/1719234057367822001/text_to_image_v2/d6e33c84d7554146a25b1093b012838b_0.png?x-oss-process=image/resize,w_500/watermark,image_aW1nL3dhdGVyMjAyNDExMjkwLnBuZz94LW9zcy1wcm9jZXNzPWltYWdlL3Jlc2l6ZSxtX2ZpeGVkLHdfMTQ1LGhfMjU=,t_80,g_se,x_10,y_10/format,webp",
        width=480,
        height=480,
        start=0,
        end=5.0,
        transform_y=0.7,
        scale_x=2.0,
        scale_y=1.0,
        transform_x=0,
        track_name="main"
    )
    print(f"添加图片成功！{image_result['output']['draft_id']}")
    print(save_draft_impl(image_result['output']['draft_id'], draft_folder))


def test_image02():
    """测试添加多个图片"""
    draft_folder = "/Users/sunguannan/Movies/JianyingPro/User Data/Projects/com.lveditor.draft"

    print("\n测试：添加图片1")
    image_result = add_image_impl(
        image_url="https://cdn.wanx.aliyuncs.com/wanx/1719234057367822001/text_to_image_v2/d6e33c84d7554146a25b1093b012838b_0.png?x-oss-process=image/resize,w_500/watermark,image_aW1nL3dhdGVyMjAyNDExMjkwLnBuZz94LW9zcy1wcm9jZXNzPWltYWdlL3Jlc2l6ZSxtX2ZpeGVkLHdfMTQ1LGhfMjU=,t_80,g_se,x_10,y_10/format,webp",
        width=480,
        height=480,
        start=0,
        end=5.0,
        transform_y=0.7,
        scale_x=2.0,
        scale_y=1.0,
        transform_x=0,
        track_name="main"
    )
    print(f"添加图片成功1！{image_result['output']['draft_id']}")
    
    print("\n测试：添加图片2")
    image_result = add_image_impl(
        draft_id=image_result['output']['draft_id'],
        image_url="https://cdn.wanx.aliyuncs.com/wanx/1719234057367822001/text_to_image_v2/d6e33c84d7554146a25b1093b012838b_0.png?x-oss-process=image/resize,w_500/watermark,image_aW1nL3dhdGVyMjAyNDExMjkwLnBuZz94LW9zcy1wcm9jZXNzPWltYWdlL3Jlc2l6ZSxtX2ZpeGVkLHdfMTQ1LGhfMjU=,t_80,g_se,x_10,y_10/format,webp",
        width=480,
        height=480,
        start=5,
        end=10.0,
        transform_y=0.7,
        scale_x=2.0,
        scale_y=1.0,
        transform_x=0,
        track_name="main"
    )
    print(f"添加图片成功2！{image_result['output']['draft_id']}")
    print(save_draft_impl(image_result['output']['draft_id'], draft_folder))


def test_image03():
    """测试在不同轨道添加图片"""
    draft_folder = "/Users/sunguannan/Movies/JianyingPro/User Data/Projects/com.lveditor.draft"

    print("\n测试：添加图片1")
    image_result = add_image_impl(
        image_url="https://cdn.wanx.aliyuncs.com/wanx/1719234057367822001/text_to_image_v2/d6e33c84d7554146a25b1093b012838b_0.png?x-oss-process=image/resize,w_500/watermark,image_aW1nL3dhdGVyMjAyNDExMjkwLnBuZz94LW9zcy1wcm9jZXNzPWltYWdlL3Jlc2l6ZSxtX2ZpeGVkLHdfMTQ1LGhfMjU=,t_80,g_se,x_10,y_10/format,webp",
        width=480,
        height=480,
        start=0,
        end=5.0,
        transform_y=0.7,
        scale_x=2.0,
        scale_y=1.0,
        transform_x=0,
        track_name="main"
    )
    print(f"添加图片成功1！{image_result['output']['draft_id']}")
    
    print("\n测试：添加图片2")
    image_result = add_image_impl(
        draft_id=image_result['output']['draft_id'],
        image_url="https://cdn.wanx.aliyuncs.com/wanx/1719234057367822001/text_to_image_v2/d6e33c84d7554146a25b1093b012838b_0.png?x-oss-process=image/resize,w_500/watermark,image_aW1nL3dhdGVyMjAyNDExMjkwLnBuZz94LW9zcy1wcm9jZXNzPWltYWdlL3Jlc2l6ZSxtX2ZpeGVkLHdfMTQ1LGhfMjU=,t_80,g_se,x_10,y_10/format,webp",
        width=480,
        height=480,
        start=5,
        end=10.0,
        transform_y=0.7,
        scale_x=2.0,
        scale_y=1.0,
        transform_x=0,
        track_name="main"
    )
    print(f"添加图片成功2！{image_result['output']['draft_id']}")

    print("\n测试：添加图片3")
    image_result = add_image_impl(
        draft_id=image_result['output']['draft_id'],
        image_url="https://cdn.wanx.aliyuncs.com/wanx/1719234057367822001/text_to_image_v2/d6e33c84d7554146a25b1093b012838b_0.png?x-oss-process=image/resize,w_500/watermark,image_aW1nL3dhdGVyMjAyNDExMjkwLnBuZz94LW9zcy1wcm9jZXNzPWltYWdlL3Jlc2l6ZSxtX2ZpeGVkLHdfMTQ1LGhfMjU=,t_80,g_se,x_10,y_10/format,webp",
        width=480,
        height=480,
        start=10,
        end=15.0,
        transform_y=0.7,
        scale_x=2.0,
        scale_y=1.0,
        transform_x=0,
        track_name="main_2"  # 使用不同的轨道名称
    )
    print(f"添加图片成功3！{image_result['output']['draft_id']}")
    query_draft_status_impl_polling(image_result['output']['draft_id'])
    save_draft_impl(image_result['output']['draft_id'], draft_folder)

def test_image04():
    """测试添加图片"""
    draft_folder = "/Users/sunguannan/Movies/JianyingPro/User Data/Projects/com.lveditor.draft"

    print("\n测试：添加图片1")
    image_result = add_image_impl(
        image_url="https://cdn.wanx.aliyuncs.com/wanx/1719234057367822001/text_to_image_v2/d6e33c84d7554146a25b1093b012838b_0.png?x-oss-process=image/resize,w_500/watermark,image_aW1nL3dhdGVyMjAyNDExMjkwLnBuZz94LW9zcy1wcm9jZXNzPWltYWdlL3Jlc2l6ZSxtX2ZpeGVkLHdfMTQ1LGhfMjU=,t_80,g_se,x_10,y_10/format,webp",
        width=480,
        height=480,
        start=5.0,
        end=10.0,
        transform_y=0.7,
        scale_x=2.0,
        scale_y=1.0,
        transform_x=0,
        track_name="image_main"
    )
    print(f"添加图片成功！{image_result['output']['draft_id']}")
    print(save_draft_impl(image_result['output']['draft_id'], draft_folder))


def test_mask_01():
    """测试在不同轨道添加图片"""
    draft_folder = "/Users/sunguannan/Movies/JianyingPro/User Data/Projects/com.lveditor.draft"

    print("\n测试：添加图片1")
    image_result = add_image_impl(
        image_url="https://cdn.wanx.aliyuncs.com/wanx/1719234057367822001/text_to_image_v2/d6e33c84d7554146a25b1093b012838b_0.png?x-oss-process=image/resize,w_500/watermark,image_aW1nL3dhdGVyMjAyNDExMjkwLnBuZz94LW9zcy1wcm9jZXNzPWltYWdlL3Jlc2l6ZSxtX2ZpeGVkLHdfMTQ1LGhfMjU=,t_80,g_se,x_10,y_10/format,webp",
        width=480,
        height=480,
        start=0,
        end=5.0,
        transform_y=0.7,
        scale_x=2.0,
        scale_y=1.0,
        transform_x=0,
        track_name="main"
    )
    print(f"添加图片成功1！{image_result['output']['draft_id']}")
    
    print("\n测试：添加图片2")
    image_result = add_image_impl(
        draft_id=image_result['output']['draft_id'],
        image_url="https://cdn.wanx.aliyuncs.com/wanx/1719234057367822001/text_to_image_v2/d6e33c84d7554146a25b1093b012838b_0.png?x-oss-process=image/resize,w_500/watermark,image_aW1nL3dhdGVyMjAyNDExMjkwLnBuZz94LW9zcy1wcm9jZXNzPWltYWdlL3Jlc2l6ZSxtX2ZpeGVkLHdfMTQ1LGhfMjU=,t_80,g_se,x_10,y_10/format,webp",
        width=480,
        height=480,
        start=5,
        end=10.0,
        transform_y=0.7,
        scale_x=2.0,
        scale_y=1.0,
        transform_x=0,
        track_name="main"
    )
    print(f"添加图片成功2！{image_result['output']['draft_id']}")

    print("\n测试：添加图片3")
    image_result = add_image_impl(
        draft_id=image_result['output']['draft_id'],
        image_url="https://cdn.wanx.aliyuncs.com/wanx/1719234057367822001/text_to_image_v2/d6e33c84d7554146a25b1093b012838b_0.png?x-oss-process=image/resize,w_500/watermark,image_aW1nL3dhdGVyMjAyNDExMjkwLnBuZz94LW9zcy1wcm9jZXNzPWltYWdlL3Jlc2l6ZSxtX2ZpeGVkLHdfMTQ1LGhfMjU=,t_80,g_se,x_10,y_10/format,webp",
        width=480,
        height=480,
        start=10,
        end=15.0,
        transform_y=0.7,
        scale_x=2.0,
        scale_y=1.0,
        transform_x=0,
        track_name="main_2",  # 使用不同的轨道名称
        mask_type="圆形",  # 添加圆形蒙版
        mask_center_x=0.5,  # 蒙版中心X坐标（0.5表示居中）
        mask_center_y=0.5,  # 蒙版中心Y坐标（0.5表示居中）
        mask_size=0.8,  # 蒙版大小（0.8表示80%）
        mask_feather=0.1  # 蒙版羽化程度（0.1表示10%）
    )
    print(f"添加图片成功3！{image_result['output']['draft_id']}")
    print(save_draft_impl(image_result['output']['draft_id'], draft_folder))

def test_mask_02():
    """测试在不同轨道添加视频"""
    draft_folder = "/Users/sunguannan/Movies/JianyingPro/User Data/Projects/com.lveditor.draft"
    video_url = "https://cdn.wanx.aliyuncs.com/wanx/1719234057367822001/text_to_video/092faf3c94244973ab752ee1280ba76f.mp4?spm=5176.29623064.0.0.41ed26d6cBOhV3&file=092faf3c94244973ab752ee1280ba76f.mp4" # 替换为实际视频URL
    draft_id = None  # 初始化draft_id
    
    # 在第一个轨道添加视频
    video_result = add_video_impl(
        draft_id=draft_id,  # 传入draft_id
        video_url=video_url,
        width=1920,
        height=1080,
        start=0,
        end=5.0, # 截取视频前5秒
        target_start=0,
        track_name="main_video_track"
    )
    draft_id = video_result['output']['draft_id']  # 更新draft_id
    print(f"第一次视频添加结果: {video_result}")
    
    # 在第二个轨道添加视频
    video_result = add_video_impl(
        draft_id=draft_id,  # 使用上一次的draft_id
        video_url=video_url,
        width=1920,
        height=1080,
        start=0,
        end=5.0, # 截取视频前5秒
        target_start=0,
        track_name="main_video_track_2",  # 使用不同的轨道名称
        speed=1.0,  # 改变播放速度
        scale_x=0.5,  # 缩小视频宽度
        transform_y=0.5  # 将视频放在屏幕下方
    )
    draft_id = video_result['output']['draft_id']  # 更新draft_id
    print(f"第二次视频添加结果: {video_result}")
    
    # 第三次在另一个轨道添加视频，并添加圆形蒙版
    video_result = add_video_impl(
        draft_id=draft_id,  # 使用上一次的draft_id
        video_url=video_url,
        width=1920,
        height=1080,
        start=0,
        end=5.0, # 截取视频前5秒
        target_start=0,
        track_name="main_video_track_3",  # 使用第三个轨道
        speed=1.5,  # 更快的播放速度
        scale_x=0.3,  # 更小的视频宽度
        transform_y=-0.5,  # 将视频放在屏幕上方
        mask_type="圆形",  # 添加圆形蒙版
        mask_center_x=0.5,  # 蒙版中心X坐标
        mask_center_y=0.5,  # 蒙版中心Y坐标
        mask_size=0.8,  # 蒙版大小
        mask_feather=0.1  # 蒙版羽化
    )
    draft_id = video_result['output']['draft_id']  # 更新draft_id
    print(f"第三次视频添加结果: {video_result}")
    
    # 最后保存并上传草稿
    save_result = save_draft_impl(draft_id, draft_folder)
    print(f"草稿保存结果: {save_result}")


def test_audio01():
    """测试添加音频"""
    # draft_folder = "/Users/sunguannan/Movies/JianyingPro/User Data/Projects/com.lveditor.draft"
    draft_folder = "/Users/sunguannan/Movies/CapCut/User Data/Projects/com.lveditor.draft"

    print("\n测试：添加音频")
    audio_result = add_audio_track(
        audio_url="https://lf3-lv-music-tos.faceu.com/obj/tos-cn-ve-2774/oYACBQRCMlWBIrZipvQZhI5LAlUFYii0RwEPh",
        start=4,
        end=5,
        target_start=15,
        volume=0.8,
        speed=1.0,
        track_name="main_audio101",
        # effect_type="麦霸",
        effect_type="Tremble",
        effect_params=[90.0, 50.0]
    )
    print(f"音频添加结果: {audio_result}")
    print(save_draft_impl(audio_result['output']['draft_id'], draft_folder))


def test_audio02():
    """测试添加多个音频片段"""
    # draft_folder = "/Users/sunguannan/Movies/JianyingPro/User Data/Projects/com.lveditor.draft"
    draft_folder = "/Users/sunguannan/Movies/CapCut/User Data/Projects/com.lveditor.draft"

    print("\n测试：添加音频1")
    audio_result = add_audio_track(
        audio_url="https://lf3-lv-music-tos.faceu.com/obj/tos-cn-ve-2774/oYACBQRCMlWBIrZipvQZhI5LAlUFYii0RwEPh",
        start=4,
        end=5,
        target_start=0,
        volume=0.8,
        speed=1.0,
        track_name="main_audio101",
        # effect_type="麦霸",
        effect_type="Tremble",
        effect_params=[90.0, 50.0]
    )
    print(f"音频添加结果1: {audio_result}")

    print("\n测试：添加音频2")
    audio_result = add_audio_track(
        draft_id=audio_result['output']['draft_id'],
        audio_url="https://lf3-lv-music-tos.faceu.com/obj/tos-cn-ve-2774/oYACBQRCMlWBIrZipvQZhI5LAlUFYii0RwEPh",
        start=4,
        end=5,
        target_start=1.5,
        volume=0.8,
        speed=1.0,
        track_name="main_audio101",
        # effect_type="麦霸",
        effect_type="Tremble",
        effect_params=[90.0, 50.0]
    )
    print(f"音频添加结果2: {audio_result}")
    print(save_draft_impl(audio_result['output']['draft_id'], draft_folder))


def test_audio03():
    """测试循环添加音频"""
    # draft_folder = "/Users/sunguannan/Movies/JianyingPro/User Data/Projects/com.lveditor.draft"
    draft_folder = "/Users/sunguannan/Movies/CapCut/User Data/Projects/com.lveditor.draft"

    draft_id = None  # 初始化draft_id
    
    for i in range(10):
        target_start = i * 1.5  # 每次递增1.5秒
        
        audio_result = add_audio_track(
            audio_url="https://lf3-lv-music-tos.faceu.com/obj/tos-cn-ve-2774/oYACBQRCMlWBIrZipvQZhI5LAlUFYii0RwEPh",
            start=4,
            end=5,
            target_start=target_start,
            volume=0.8,
            speed=1.0,
            track_name="main_audio101",
            # effect_type="麦霸",
            effect_type="Tremble",
            effect_params=[90.0, 50.0],
            draft_id=draft_id  # 传递上一次的draft_id（第一次为None）
        )
        
        draft_id = audio_result['output']['draft_id']  # 更新draft_id
        print(f"第 {i+1} 次音频添加结果: {audio_result}")
    
    # 最后保存并上传草稿
    save_result = save_draft_impl(draft_id, draft_folder)
    print(f"草稿保存结果: {save_result}")


def test_audio04():
    """测试在不同轨道添加音频"""
    # draft_folder = "/Users/sunguannan/Movies/JianyingPro/User Data/Projects/com.lveditor.draft"
    draft_folder = "/Users/sunguannan/Movies/CapCut/User Data/Projects/com.lveditor.draft"

    print("\n测试：添加音频1")
    audio_result = add_audio_track(
        audio_url="https://lf3-lv-music-tos.faceu.com/obj/tos-cn-ve-2774/oYACBQRCMlWBIrZipvQZhI5LAlUFYii0RwEPh",
        start=4,
        end=5,
        target_start=0,
        volume=0.8,
        speed=1.0,
        track_name="main_audio101",
        # effect_type="麦霸",
        effect_type="Tremble",
        effect_params=[90.0, 50.0]
    )
    print(f"音频添加结果1: {audio_result}")

    print("\n测试：添加音频2")
    audio_result = add_audio_track(
        draft_id=audio_result['output']['draft_id'],
        audio_url="https://lf3-lv-music-tos.faceu.com/obj/tos-cn-ve-2774/oYACBQRCMlWBIrZipvQZhI5LAlUFYii0RwEPh",
        start=4,
        end=5,
        target_start=1.5,
        volume=0.8,
        speed=1.0,
        track_name="main_audio102",  # 使用不同的轨道名称
        # effect_type="麦霸",
        effect_type="Tremble",
        effect_params=[90.0, 50.0]
    )
    print(f"音频添加结果2: {audio_result}")
    query_draft_status_impl_polling(audio_result['output']['draft_id'])
    save_draft_impl(audio_result['output']['draft_id'], draft_folder)

def add_subtitle_impl(srt, draft_id=None, time_offset=0.0, font_size=5.0,
                    bold=False, italic=False, underline=False, font_color="#ffffff",
                    transform_x=0.0, transform_y=0.0, scale_x=1.0, scale_y=1.0,
                    vertical=False, track_name="subtitle", alpha=1,
                    border_alpha=1.0, border_color="#000000", border_width=0.0,
                    background_color="#000000", background_style=1, background_alpha=0.0,
                    rotation=0.0, width=1080, height=1920):
    """调用add_subtitle服务的API封装"""
    data = {
        "license_key": LICENSE_KEY,  # 使用体验版license key
        "srt": srt,  # 修改参数名称以匹配服务端
        "draft_id": draft_id,
        "time_offset": time_offset,
        "font_size": font_size,
        "bold": bold,
        "italic": italic,
        "underline": underline,
        "font_color": font_color,
        "transform_x": transform_x,
        "transform_y": transform_y,
        "scale_x": scale_x,
        "scale_y": scale_y,
        "vertical": vertical,
        "track_name": track_name,
        "alpha": alpha,
        "border_alpha": border_alpha,
        "border_color": border_color,
        "border_width": border_width,
        "background_color": background_color,
        "background_style": background_style,
        "background_alpha": background_alpha,
        "rotation": rotation,
        "width": width,
        "height": height
    }
    return make_request("add_subtitle", data)

def save_draft_impl(draft_id, draft_folder):
    """调用save_draft服务的API封装"""
    data = {
        "license_key": LICENSE_KEY,  # 使用体验版license key
        "draft_id": draft_id,
        "draft_folder": draft_folder
    }
    return make_request("save_draft", data)

def query_script_impl(draft_id):
    """调用query_script服务的API封装"""
    data = {
        "draft_id": draft_id
    }
    return make_request("query_script", data)

def query_draft_status_impl(task_id):
    """调用query_draft_status服务的API封装"""
    data = {
        "license_key": LICENSE_KEY,  # 使用体验版license key
        "task_id": task_id
    }
    return make_request("query_draft_status", data)
    
def query_draft_status_impl_polling(task_id, timeout=300, callback=None):
    """
    轮询查询草稿下载状态，使用异步线程实现，避免阻塞主线程
    
    :param task_id: save_draft_impl 返回的任务ID
    :param timeout: 超时时间（秒），默认5分钟
    :param callback: 可选的回调函数，当任务完成、失败或超时时调用，参数为最终状态
    :return: 线程对象和结果容器的元组，可用于后续获取结果
    """
    # 创建结果容器，用于存储最终结果
    result_container = {"result": None}
    
    def _polling_thread():
        start_time = time.time()
        print(f"开始查询任务 {task_id} 的状态...")
        
        while True:
            try:
                # 获取当前任务状态
                task_status = query_draft_status_impl(task_id).get("output", {})
                
                # 打印当前状态
                status = task_status.get("status", "unknown")
                message = task_status.get("message", "")
                progress = task_status.get("progress", 0)
                print(f"当前状态: {status}, 进度: {progress}%, 消息: {message}")
                
                # 检查是否完成或失败
                if status == "completed":
                    print(f"任务完成! 草稿URL: {task_status.get('draft_url', '未提供')}")
                    result_container["result"] = task_status.get('draft_url', '未提供')
                    if callback:
                        callback(task_status.get('draft_url', '未提供'))
                    break
                elif status == "failed":
                    print(f"任务失败: {message}")
                    result_container["result"] = task_status
                    if callback:
                        callback(task_status)
                    break
                elif status == "not_found":
                    print(f"任务不存在: {task_id}")
                    result_container["result"] = task_status
                    if callback:
                        callback(task_status)
                    break
                
                # 检查是否超时
                elapsed_time = time.time() - start_time
                if elapsed_time > timeout:
                    print(f"查询超时，已经等待 {timeout} 秒")
                    result_container["result"] = task_status
                    if callback:
                        callback(task_status)
                    break
            except Exception as e:
                # 捕获所有异常，防止线程崩溃
                print(f"查询过程中出现异常: {e}")
                time.sleep(1)  # 出错后等待一秒再重试
                continue
            
            # 等待1秒后再次查询
            time.sleep(1)
    
    # 创建并启动线程
    thread = threading.Thread(target=_polling_thread)
    # thread.daemon = True  # 设置为守护线程，主线程结束时自动终止
    thread.start()
    
    # 返回线程对象和结果容器，方便外部代码获取结果
    return thread, result_container

def test_subtitle():
    draft_folder = "/Users/sunguannan/Movies/JianyingPro/User Data/Projects/com.lveditor.draft"

    # 测试用例：添加文本字幕
    print("\n测试：添加文本字幕")
    text_result = add_subtitle_impl(
        srt="1\n00:00:00,000 --> 00:00:04,433\n你333好，我是孙关南开发的剪映草稿助手。\n\n2\n00:00:04,433 --> 00:00:11,360\n我擅长将音频、视频、图片素材拼接在一起剪辑输出剪映草稿。\n",
        font_size=8.0,
        bold=True,
        italic=True,
        underline=True,
        font_color="#FF0000",
        transform_y=0,
        transform_x=0.4,
        time_offset=42,
        scale_x=1.0,
        scale_y=2.0,
        vertical=True,
        # 添加背景颜色参数
        background_color="#FFFF00",  # 黄色背景
        background_style=1,  # 样式1表示矩形背景
        background_alpha=0.7,  # 70%不透明度
        # 添加描边参数
        border_color="#0000FF",  # 蓝色描边
        border_width=20.0,  # 描边宽度为2
        border_alpha=1.0  # 完全不透明
    )
    print(f"文本添加结果: {text_result}")
    
    # 保存草稿
    if text_result.get('success') and text_result.get('output'):
        save_result = save_draft_impl(text_result['output']['draft_id'], draft_folder)
        print(f"保存草稿结果: {save_result}")

def test01():
    draft_folder = "/Users/sunguannan/Movies/JianyingPro/User Data/Projects/com.lveditor.draft"
    # draft_folder = "/Users/sunguannan/Movies/CapCut/User Data/Projects/com.lveditor.draft"

    # 组合测试
    print("\n测试2：添加音频")
    audio_result = add_audio_track(
        audio_url = "https://lf3-lv-music-tos.faceu.com/obj/tos-cn-ve-2774/oYACBQRCMlWBIrZipvQZhI5LAlUFYii0RwEPh",
        start=4,
        end=5,
        target_start=2,
        volume=0.8,
        speed=1.0,
        track_name="main_audio100",
        effect_type="麦霸",
        effect_params=[90.0, 50.0]
    )
    print(f"音频添加结果1: {audio_result}")

    audio_result = add_audio_track(
        draft_id=audio_result['output']['draft_id'],
        audio_url = "https://lf3-lv-music-tos.faceu.com/obj/tos-cn-ve-2774/oYACBQRCMlWBIrZipvQZhI5LAlUFYii0RwEPh",
        start=4,
        end=5,
        target_start=4,
        volume=0.8,
        speed=1.0,
        track_name="main_audio100",
        effect_type="麦霸",
        effect_params=[90.0, 50.0]
    )
    print(f"音频添加结果2: {audio_result}")

    audio_result = add_audio_track(
        draft_id=audio_result['output']['draft_id'],
        audio_url = "https://lf3-lv-music-tos.faceu.com/obj/tos-cn-ve-2774/oYACBQRCMlWBIrZipvQZhI5LAlUFYii0RwEPh",
        start=4,
        end=5,
        target_start=6,
        volume=0.8,
        speed=1.0,
        track_name="main_audio101",
        effect_type="麦霸",
        effect_params=[90.0, 50.0]
    )
    print(f"音频添加结果3: {audio_result}")

    # 测试用例1：基本文本添加
    text_result = add_text_impl(
        draft_folder=draft_folder,
        text="测试文本1",
        draft_id=audio_result['output']['draft_id'],
        start=0,
        end=3,
        font="思源中宋",  # 使用思源黑体
        font_color="#FF0000",  # 红色
        track_name="main_text",
        transform_y=0.8,
        transform_x=0.5,
        font_size=30.0
    )
    print("测试用例1（基本文本）成功:", text_result)

    # 测试用例2：竖排文本
    result2 = add_text_impl(
        draft_id=text_result['output']['draft_id'],
        text="竖排文本测试",
        start=3,
        end=6,
        font="云书法三行魏碑体",
        font_color="#00FF00",  # 绿色
        font_size=8.0,
        track_name="main_text",
        vertical=True,  # 启用竖排
        transform_y=-0.5,
        outro_animation='晕开'
    )
    print("测试用例2（竖排文本）成功:", result2)

    print("测试完成")
    # 测试添加图片
    image_result = add_image_impl(
        draft_id=result2['output']['draft_id'],  # 替换为实际的草稿ID
        image_url="https://cdn.wanx.aliyuncs.com/wanx/1719234057367822001/text_to_image_v2/d6e33c84d7554146a25b1093b012838b_0.png?x-oss-process=image/resize,w_500/watermark,image_aW1nL3dhdGVyMjAyNDExMjkwLnBuZz94LW9zcy1wcm9jZXNzPWltYWdlL3Jlc2l6ZSxtX2ZpeGVkLHdfMTQ1LGhfMjU=,t_80,g_se,x_10,y_10/format,webp",  # 替换为实际的图片URL
        width=480,
        height=480,
        start = 0,
        end=5.0,  # 显示5秒
        transform_y=0.7,
        scale_x=2.0,
        scale_y=1.0,
        transform_x=0,
        track_name="main"
    )
    print("添加图片成功！")


    # 测试添加图片
    image_result = add_image_impl(
        draft_id=result2['output']['draft_id'],  # 替换为实际的草稿ID
        image_url="http://gips0.baidu.com/it/u=3602773692,1512483864&fm=3028&app=3028&f=JPEG&fmt=auto?w=960&h=1280",  # 替换为实际的图片URL
        width=480,
        height=480,
        start = 0,
        end=5.0,  # 显示5秒
        transform_y=0.7,
        scale_x=2.0,
        scale_y=1.0,
        transform_x=0,
        track_name="main_2"
    )
    print("添加图片成功！")

    image_result = add_image_impl(
        draft_id=image_result['output']['draft_id'],  # 替换为实际的草稿ID
        image_url="https://cdn.wanx.aliyuncs.com/wanx/1719234057367822001/text_to_image_v2/d6e33c84d7554146a25b1093b012838b_0.png?x-oss-process=image/resize,w_500/watermark,image_aW1nL3dhdGVyMjAyNDExMjkwLnBuZz94LW9zcy1wcm9jZXNzPWltYWdlL3Jlc2l6ZSxtX2ZpeGVkLHdfMTQ1LGhfMjU=,t_80,g_se,x_10,y_10/format,webp",  # 替换为实际的图片URL
        width=480,
        height=480,
        start = 5,
        end=10.0,  # 显示5秒
        transform_y=0.7,
        scale_x=2.0,
        scale_y=1.0,
        transform_x=0,
        track_name="main"
    )
    print("添加图片2成功！")

    # 测试添加视频关键帧
    print("\n测试：添加视频关键帧")
    keyframe_result = add_video_keyframe_impl(
        draft_id=image_result['output']['draft_id'],  # 使用已存在的草稿ID
        track_name="main",
        property_type="position_y",  # 测试不透明度
        time=1.5,  # 在3.5秒处添加关键帧
        value="0.2"  # 移动300px
    )
    print(f"关键帧添加结果: {keyframe_result}")

    print("\n测试：添加视频关键帧")
    keyframe_result = add_video_keyframe_impl(
        draft_id=image_result['output']['draft_id'],  # 使用已存在的草稿ID
        track_name="main",
        property_type="position_y",  # 测试不透明度
        time=3.5,  # 在3.5秒处添加关键帧
        value="0.4"  # 移动300px
    )
    print(f"关键帧添加结果: {keyframe_result}")
    
    query_draft_status_impl_polling(keyframe_result['output']['draft_id'])
    save_draft_impl(keyframe_result['output']['draft_id'], draft_folder)

def test02():
    # draft_folder = "/Users/sunguannan/Movies/JianyingPro/User Data/Projects/com.lveditor.draft"
    draft_folder = "/Users/sunguannan/Movies/CapCut/User Data/Projects/com.lveditor.draft"

    # 组合测试
    print("\n测试2：添加音频")
    audio_result = add_audio_track(
        audio_url = "https://lf3-lv-music-tos.faceu.com/obj/tos-cn-ve-2774/oYACBQRCMlWBIrZipvQZhI5LAlUFYii0RwEPh",
        start=4,
        end=5,
        target_start=2,
        volume=0.8,
        speed=1.0,
        track_name="main_audio100",
        effect_type = "Big_House",
        effect_params = [50.0]
    )
    print(f"音频添加结果1: {audio_result}")

    audio_result = add_audio_track(
        draft_id=audio_result['output']['draft_id'],
        audio_url = "https://lf3-lv-music-tos.faceu.com/obj/tos-cn-ve-2774/oYACBQRCMlWBIrZipvQZhI5LAlUFYii0RwEPh",
        start=4,
        end=5,
        target_start=4,
        volume=0.8,
        speed=1.0,
        track_name="main_audio100",
        effect_type = "Big_House",
        effect_params = [50.0]
    )
    print(f"音频添加结果2: {audio_result}")

    audio_result = add_audio_track(
        draft_id=audio_result['output']['draft_id'],
        audio_url = "https://lf3-lv-music-tos.faceu.com/obj/tos-cn-ve-2774/oYACBQRCMlWBIrZipvQZhI5LAlUFYii0RwEPh",
        start=4,
        end=5,
        target_start=6,
        volume=0.8,
        speed=1.0,
        track_name="main_audio101",
        effect_type = "Big_House",
        effect_params = [50.0]
    )
    print(f"音频添加结果3: {audio_result}")

    # 测试用例1：基本文本添加
    text_result = add_text_impl(
        draft_folder=draft_folder,
        text="测试文本1",
        draft_id=audio_result['output']['draft_id'],
        start=0,
        end=3,
        font="思源中宋",  # 使用思源黑体
        font_color="#FF0000",  # 红色
        track_name="main_text",
        transform_y=0.8,
        transform_x=0.5,
        font_size=30.0
    )
    print("测试用例1（基本文本）成功:", text_result)

    # 测试用例2：竖排文本
    result2 = add_text_impl(
        draft_id=text_result['output']['draft_id'],
        text="竖排文本测试",
        start=3,
        end=6,
        font="云书法三行魏碑体",
        font_color="#00FF00",  # 绿色
        font_size=8.0,
        track_name="main_text",
        vertical=True,  # 启用竖排
        transform_y=-0.5,
        outro_animation='Throw_Back'
    )
    print("测试用例2（竖排文本）成功:", result2)

    print("测试完成")
    # 测试添加图片
    image_result = add_image_impl(
        draft_id=result2['output']['draft_id'],  # 替换为实际的草稿ID
        image_url="https://cdn.wanx.aliyuncs.com/wanx/1719234057367822001/text_to_image_v2/d6e33c84d7554146a25b1093b012838b_0.png?x-oss-process=image/resize,w_500/watermark,image_aW1nL3dhdGVyMjAyNDExMjkwLnBuZz94LW9zcy1wcm9jZXNzPWltYWdlL3Jlc2l6ZSxtX2ZpeGVkLHdfMTQ1LGhfMjU=,t_80,g_se,x_10,y_10/format,webp",  # 替换为实际的图片URL
        width=480,
        height=480,
        start = 0,
        end=5.0,  # 显示5秒
        transform_y=0.7,
        scale_x=2.0,
        scale_y=1.0,
        transform_x=0,
        track_name="main"
    )
    print("添加图片成功！")


    # 测试添加图片
    image_result = add_image_impl(
        draft_id=result2['output']['draft_id'],  # 替换为实际的草稿ID
        image_url="http://gips0.baidu.com/it/u=3602773692,1512483864&fm=3028&app=3028&f=JPEG&fmt=auto?w=960&h=1280",  # 替换为实际的图片URL
        width=480,
        height=480,
        start = 0,
        end=5.0,  # 显示5秒
        transform_y=0.7,
        scale_x=2.0,
        scale_y=1.0,
        transform_x=0,
        track_name="main_2"
    )
    print("添加图片成功！")

    image_result = add_image_impl(
        draft_id=image_result['output']['draft_id'],  # 替换为实际的草稿ID
        image_url="https://cdn.wanx.aliyuncs.com/wanx/1719234057367822001/text_to_image_v2/d6e33c84d7554146a25b1093b012838b_0.png?x-oss-process=image/resize,w_500/watermark,image_aW1nL3dhdGVyMjAyNDExMjkwLnBuZz94LW9zcy1wcm9jZXNzPWltYWdlL3Jlc2l6ZSxtX2ZpeGVkLHdfMTQ1LGhfMjU=,t_80,g_se,x_10,y_10/format,webp",  # 替换为实际的图片URL
        width=480,
        height=480,
        start = 5,
        end=10.0,  # 显示5秒
        transform_y=0.7,
        scale_x=2.0,
        scale_y=1.0,
        transform_x=0,
        track_name="main"
    )
    print("添加图片2成功！")

    # 测试添加视频关键帧
    print("\n测试：添加视频关键帧")
    keyframe_result = add_video_keyframe_impl(
        draft_id=image_result['output']['draft_id'],  # 使用已存在的草稿ID
        track_name="main",
        property_type="position_y",  # 测试不透明度
        time=1.5,  # 在3.5秒处添加关键帧
        value="0.2"  # 移动300px
    )
    print(f"关键帧添加结果: {keyframe_result}")

    print("\n测试：添加视频关键帧")
    keyframe_result = add_video_keyframe_impl(
        draft_id=image_result['output']['draft_id'],  # 使用已存在的草稿ID
        track_name="main",
        property_type="position_y",  # 测试不透明度
        time=3.5,  # 在3.5秒处添加关键帧
        value="0.4"  # 移动300px
    )
    print(f"关键帧添加结果: {keyframe_result}")
    
    query_draft_status_impl_polling(keyframe_result['output']['draft_id'])
    save_draft_impl(keyframe_result['output']['draft_id'], draft_folder)

def test_video_track01():
    """测试添加视频轨道"""
    draft_folder = "/Users/sunguannan/Movies/JianyingPro/User Data/Projects/com.lveditor.draft"
    video_url = "https://cdn.wanx.aliyuncs.com/wanx/1719234057367822001/text_to_video/092faf3c94244973ab752ee1280ba76f.mp4?spm=5176.29623064.0.0.41ed26d6cBOhV3&file=092faf3c94244973ab752ee1280ba76f.mp4" # 替换为实际视频URL

    print("\n测试：添加视频轨道")
    video_result = add_video_impl(
        video_url=video_url,
        width=1920,
        height=1080,
        start=0,
        end=5.0, # 截取视频前5秒
        target_start=0,
        track_name="main_video_track"
    )
    print(f"视频轨道添加结果: {video_result}")

    if video_result and 'output' in video_result and 'draft_id' in video_result['output']:
        draft_id = video_result['output']['draft_id']
        print(f"保存草稿: {save_draft_impl(draft_id, draft_folder)}")
    else:
        print("无法获取草稿ID，跳过保存操作。")


def test_video_track02():
    """测试循环添加视频轨道"""
    draft_folder = "/Users/sunguannan/Movies/JianyingPro/User Data/Projects/com.lveditor.draft"
    video_url = "https://cdn.wanx.aliyuncs.com/wanx/1719234057367822001/text_to_video/092faf3c94244973ab752ee1280ba76f.mp4?spm=5176.29623064.0.0.41ed26d6cBOhV3&file=092faf3c94244973ab752ee1280ba76f.mp4" # 替换为实际视频URL
    draft_id = None  # 初始化draft_id
    
    for i in range(5):
        target_start = i * 5  # 每次递增5秒
        
        video_result = add_video_impl(
            draft_id=draft_id,  # 传入draft_id
            video_url=video_url,
            width=1920,
            height=1080,
            start=0,
            end=5.0, # 截取视频前5秒
            target_start=target_start,
            track_name="main_video_track"
        )
        draft_id = video_result['output']['draft_id']  # 更新draft_id
        print(f"第 {i+1} 次视频添加结果: {video_result}")
    
    # 最后保存并上传草稿
    save_result = save_draft_impl(draft_id, draft_folder)
    print(f"草稿保存结果: {save_result}")


def test_video_track03():
    """测试在不同轨道添加视频"""
    draft_folder = "/Users/sunguannan/Movies/JianyingPro/User Data/Projects/com.lveditor.draft"
    video_url = "https://cdn.wanx.aliyuncs.com/wanx/1719234057367822001/text_to_video/092faf3c94244973ab752ee1280ba76f.mp4?spm=5176.29623064.0.0.41ed26d6cBOhV3&file=092faf3c94244973ab752ee1280ba76f.mp4" # 替换为实际视频URL
    draft_id = None  # 初始化draft_id
    
    # 在第一个轨道添加视频
    video_result = add_video_impl(
        draft_id=draft_id,  # 传入draft_id
        video_url=video_url,
        width=1920,
        height=1080,
        start=0,
        end=5.0, # 截取视频前5秒
        target_start=0,
        track_name="main_video_track"
    )
    draft_id = video_result['output']['draft_id']  # 更新draft_id
    print(f"第一次视频添加结果: {video_result}")
    
    # 在第二个轨道添加视频
    video_result = add_video_impl(
        draft_id=draft_id,  # 使用上一次的draft_id
        video_url=video_url,
        width=1920,
        height=1080,
        start=0,
        end=5.0, # 截取视频前5秒
        target_start=0,
        track_name="main_video_track_2",  # 使用不同的轨道名称
        speed=1.0,  # 改变播放速度
        scale_x=0.5,  # 缩小视频宽度
        transform_y=0.5  # 将视频放在屏幕下方
    )
    draft_id = video_result['output']['draft_id']  # 更新draft_id
    print(f"第二次视频添加结果: {video_result}")
    
    # 第三次在另一个轨道添加视频
    video_result = add_video_impl(
        draft_id=draft_id,  # 使用上一次的draft_id
        video_url=video_url,
        width=1920,
        height=1080,
        start=0,
        end=5.0, # 截取视频前5秒
        target_start=0,
        track_name="main_video_track_3",  # 使用第三个轨道
        speed=1.5,  # 更快的播放速度
        scale_x=0.3,  # 更小的视频宽度
        transform_y=-0.5  # 将视频放在屏幕上方
    )
    draft_id = video_result['output']['draft_id']  # 更新draft_id
    print(f"第三次视频添加结果: {video_result}")
    
    # 最后保存并上传草稿
    save_result = save_draft_impl(draft_id, draft_folder)
    print(f"草稿保存结果: {save_result}")

def test_video_track04():
    """测试添加视频轨道"""
    draft_folder = "/Users/sunguannan/Movies/JianyingPro/User Data/Projects/com.lveditor.draft"
    video_url = "https://cdn.wanx.aliyuncs.com/wanx/1719234057367822001/text_to_video/092faf3c94244973ab752ee1280ba76f.mp4?spm=5176.29623064.0.0.41ed26d6cBOhV3&file=092faf3c94244973ab752ee1280ba76f.mp4" # 替换为实际视频URL

    print("\n测试：添加视频轨道")
    video_result = add_video_impl(
        video_url='https://p26-bot-workflow-sign.byteimg.com/tos-cn-i-mdko3gqilj/07bf6797a1834d75beb05c63293af204.mp4~tplv-mdko3gqilj-image.image?rk3s=81d4c505&x-expires=1782141919&x-signature=2ETX83Swh%2FwKzHeWB%2F9oGq9vqt4%3D&x-wf-file_name=output-997160b5.mp4'
    )
    print(f"视频轨道添加结果: {video_result}")

    print("\n测试：添加视频轨道")
    video_result = add_video_impl(
        video_url='https://cdn.wanx.aliyuncs.com/wanx/1719234057367822001/text_to_video/092faf3c94244973ab752ee1280ba76f.mp4?spm=5176.29623064.0.0.41ed26d6cBOhV3&file=092faf3c94244973ab752ee1280ba76f.mp4',
        draft_id=video_result['output']['draft_id'],  # 使用已存在的草稿ID
        target_start=19.84
    )
    print(f"视频轨道添加结果: {video_result}")
    if video_result and 'output' in video_result and 'draft_id' in video_result['output']:
        draft_id = video_result['output']['draft_id']
        print(f"保存草稿: {save_draft_impl(draft_id, draft_folder)}")
    else:
        print("无法获取草稿ID，跳过保存操作。")

def test_keyframe():
    """测试添加关键帧"""
    draft_folder = "/Users/sunguannan/Movies/JianyingPro/User Data/Projects/com.lveditor.draft"
    draft_id = None  # 初始化draft_id
    
    print("\n测试：添加基本视频轨道")
    video_result = add_video_impl(
        video_url="https://cdn.wanx.aliyuncs.com/wanx/1719234057367822001/text_to_video/092faf3c94244973ab752ee1280ba76f.mp4?spm=5176.29623064.0.0.41ed26d6cBOhV3&file=092faf3c94244973ab752ee1280ba76f.mp4",
        width=1920,
        height=1080,
        start=0,
        end=10.0,
        target_start=0,
        track_name="main_video_track"
    )
    print("视频添加结果:", video_result)
    
    if video_result.get('success') and video_result.get('output'):
        draft_id = video_result['output']['draft_id']
        print("使用现有draft_id:", draft_id)
    else:
        print("无法获取草稿ID，终止测试。")
        return

    print("\n测试：添加不透明度关键帧")
    keyframe_result = add_video_keyframe_impl(
        draft_id=draft_id,
        track_name="main_video_track",
        property_type="alpha",
        time=2.0,
        value="1.0"
    )
    print("不透明度关键帧添加结果:", keyframe_result)

    print("\n测试：添加位置Y关键帧")
    keyframe_result = add_video_keyframe_impl(
        draft_id=draft_id,
        track_name="main_video_track",
        property_type="position_y",
        time=2.0,
        value="0.5"
    )
    print("位置Y关键帧添加结果:", keyframe_result)

    print("\n测试：添加缩放X关键帧")
    keyframe_result = add_video_keyframe_impl(
        draft_id=draft_id,
        track_name="main_video_track",
        property_type="position_y",
        time=4.0,
        value="-0.5"
    )
    print("缩放X关键帧添加结果:", keyframe_result)

    print("\n最终保存草稿")
    save_result = save_draft_impl(draft_id, draft_folder)
    print(f"草稿保存结果: {save_result}")


def test_keyframe_02():
    """测试添加关键帧 - 批量添加实现淡入和放大回弹效果"""
    draft_folder = "/Users/sunguannan/Movies/JianyingPro/User Data/Projects/com.lveditor.draft"
    draft_id = None  # 初始化draft_id
    
    print("\n测试：添加基本视频轨道")
    video_result = add_video_impl(
        video_url="https://cdn.wanx.aliyuncs.com/wanx/1719234057367822001/text_to_video/092faf3c94244973ab752ee1280ba76f.mp4?spm=5176.29623064.0.0.41ed26d6cBOhV3&file=092faf3c94244973ab752ee1280ba76f.mp4",
        width=1920,
        height=1080,
        start=0,
        end=10.0,
        target_start=0,
        track_name="main_video_track"
    )
    print("视频添加结果:", video_result)
    
    if video_result.get('success') and video_result.get('output'):
        draft_id = video_result['output']['draft_id']
        print("使用现有draft_id:", draft_id)
    else:
        print("无法获取草稿ID，终止测试。")
        return

    print("\n测试：批量添加不透明度关键帧 - 实现淡入效果")
    # 添加不透明度关键帧，实现从不可见到可见的淡入效果
    alpha_keyframe_result = add_video_keyframe_impl(
        draft_id=draft_id,
        track_name="main_video_track",
        property_types=["alpha", "alpha", "alpha", "alpha"],
        times=[0.0, 1.0, 2.0, 3.0],
        values=["0.0", "0.3", "0.7", "1.0"]
    )
    print("不透明度关键帧批量添加结果:", alpha_keyframe_result)

    print("\n测试：批量添加缩放关键帧 - 实现放大回弹效果")
    # 添加统一缩放关键帧，实现放大回弹效果
    scale_keyframe_result = add_video_keyframe_impl(
        draft_id=draft_id,
        track_name="main_video_track",
        property_types=["uniform_scale", "uniform_scale", "uniform_scale", "uniform_scale", "uniform_scale"],
        times=[0.0, 1.5, 3.0, 4.5, 6.0],
        values=["0.8", "1.3", "1.0", "1.2", "1.0"]
    )
    print("缩放关键帧批量添加结果:", scale_keyframe_result)

    print("\n测试：批量添加位置Y关键帧 - 实现上下浮动效果")
    # 添加位置Y关键帧，实现上下浮动效果
    position_y_keyframe_result = add_video_keyframe_impl(
        draft_id=draft_id,
        track_name="main_video_track",
        property_types=["position_y", "position_y", "position_y", "position_y"],
        times=[2.0, 3.5, 5.0, 6.5],
        values=["0.0", "0.2", "-0.2", "0.0"]
    )
    print("位置Y关键帧批量添加结果:", position_y_keyframe_result)

    print("\n最终保存草稿")
    save_result = save_draft_impl(draft_id, draft_folder)
    print(f"草稿保存结果: {save_result}")

def test_subtitle_01():
    """测试添加文本字幕"""
    draft_folder = "/Users/sunguannan/Movies/JianyingPro/User Data/Projects/com.lveditor.draft"
    
    print("\n测试3：添加文本字幕")
    text_result = add_subtitle_impl(
        srt="1\n00:00:00,000 --> 00:00:04,433\n你333好，我是孙关南开发的剪映草稿助手。\n\n2\n00:00:04,433 --> 00:00:11,360\n我擅长将音频、视频、图片素材拼接在一起剪辑输出剪映草稿。\n",
        font_size=8.0,
        bold=True,
        italic=True,
        underline=True,
        font_color="#FF0000",
        transform_y=0,
        transform_x=0.4,
        time_offset=42,
        scale_x=1.0,
        scale_y=2.0,
        vertical=True
    )
    print(f"文本添加结果: {text_result}")
    
    if text_result.get('success') and text_result.get('output'):
        save_result = save_draft_impl(text_result['output']['draft_id'], draft_folder)
        print(f"保存草稿结果: {save_result}")
    
    return text_result


def test_subtitle_02():
    """测试通过SRT URL添加文本字幕"""
    draft_folder = "/Users/sunguannan/Movies/JianyingPro/User Data/Projects/com.lveditor.draft"
    
    print("\n测试3：添加文本字幕（从URL）")
    text_result = add_subtitle_impl(
        srt="https://oss-oversea-bucket.oss-cn-hongkong.aliyuncs.com/dfd_srt_1748575460_kmtu56iu.srt?Expires=1748707452&OSSAccessKeyId=TMP.3Km5TL5giRLgDkc3CamKPcWZTmSrLVeRxPWxEisNB2CTymvUxrpX8VXzy5r99F6bJkwjwFM5d1RsiV3cF18iaMriAPtA1y&Signature=4JzB4YGiChsxcTFuvUyZ0v3MjMI%3D",
        font_size=8.0,
        bold=True,
        italic=True,
        underline=True,
        font_color="#FF0000",
        transform_y=0,
        transform_x=0.4,
        time_offset=42,
        scale_x=1.0,
        scale_y=2.0,
        vertical=True
    )
    print(f"文本添加结果: {text_result}")
    
    if text_result.get('success') and text_result.get('output'):
        save_result = save_draft_impl(text_result['output']['draft_id'], draft_folder)
        print(f"保存草稿结果: {save_result}")
    
    return text_result


def test_video():
    draft_folder = "/Users/sunguannan/Movies/JianyingPro/User Data/Projects/com.lveditor.draft"

    print("\n测试：添加视频")
    video_result = add_video_impl(
        video_url="https://cdn.wanx.aliyuncs.com/wanx/1719234057367822001/text_to_video/092faf3c94244973ab752ee1280ba76f.mp4?spm=5176.29623064.0.0.41ed26d6cBOhV3&file=092faf3c94244973ab752ee1280ba76f.mp4", # 替换为实际的视频URL
        start=0,
        end=5,
        width=1920,
        height=1080,
        track_name="main_video",
        transform_y=0.1,
        scale_x=0.8,
        scale_y=0.8,
        transform_x=0.1,
        speed=1.2,
        target_start=0,
        relative_index=0
    )
    print(f"视频添加结果: {video_result}")

    # 保存草稿
    if video_result.get('success') and video_result.get('output'):
        query_draft_status_impl_polling(video_result['output']['draft_id'])
        save_draft_impl(video_result['output']['draft_id'], draft_folder)
        
def test_video_02():
    draft_folder = "/Users/sunguannan/Movies/JianyingPro/User Data/Projects/com.lveditor.draft"

    print("\n测试：添加视频")
    video_result = add_video_impl(
        video_url="https://cdn.wanx.aliyuncs.com/wanx/1719234057367822001/text_to_video/092faf3c94244973ab752ee1280ba76f.mp4?spm=5176.29623064.0.0.41ed26d6cBOhV3&file=092faf3c94244973ab752ee1280ba76f.mp4", # 替换为实际的视频URL
        start=0,
        end=5,
        width=1920,
        height=1080,
        track_name="main_video",
        transform_y=0.1,
        scale_x=0.8,
        scale_y=0.8,
        transform_x=0.1,
        speed=1.2,
        target_start=0,
        relative_index=0
    )
    print(f"视频添加结果: {video_result}")

    video_result = add_video_impl(
        video_url="https://videos.pexels.com/video-files/3129769/3129769-hd_1280_720_30fps.mp4", # 替换为实际的视频URL
        draft_id=video_result['output']['draft_id'],
        start=0,
        end=5,
        width=1920,
        height=1080,
        track_name="main_video_2",
        transform_y=0.1,
        scale_x=0.8,
        scale_y=0.8,
        transform_x=0.1,
        speed=1.2,
        target_start=0,
        relative_index=0
    )
    video_result = add_video_impl(
        video_url="https://videos.pexels.com/video-files/3129769/3129769-uhd_3840_2160_30fps.mp4", # 替换为实际的视频URL
        draft_id=video_result['output']['draft_id'],
        start=0,
        end=5,
        width=1920,
        height=1080,
        track_name="main_video_3",
        transform_y=0.1,
        scale_x=0.8,
        scale_y=0.8,
        transform_x=0.1,
        speed=1.2,
        target_start=0,
        relative_index=0
    )
    video_result = add_video_impl(
        video_url="https://videos.pexels.com/video-files/3129769/3129769-sd_426_240_30fps.mp4", # 替换为实际的视频URL
        draft_id=video_result['output']['draft_id'],
        start=0,
        end=5,
        width=1920,
        height=1080,
        track_name="main_video_4",
        transform_y=0.1,
        scale_x=0.8,
        scale_y=0.8,
        transform_x=0.1,
        speed=1.2,
        target_start=0,
        relative_index=0
    )
    video_result = add_video_impl(
        video_url="https://videos.pexels.com/video-files/3129769/3129769-sd_640_360_30fps.mp4", # 替换为实际的视频URL
        draft_id=video_result['output']['draft_id'],
        start=0,
        end=5,
        width=1920,
        height=1080,
        track_name="main_video_5",
        transform_y=0.1,
        scale_x=0.8,
        scale_y=0.8,
        transform_x=0.1,
        speed=1.2,
        target_start=0,
        relative_index=0
    )
    video_result = add_video_impl(
        video_url="https://videos.pexels.com/video-files/3129769/3129769-uhd_2560_1440_30fps.mp4", # 替换为实际的视频URL
        draft_id=video_result['output']['draft_id'],
        start=0,
        end=5,
        width=1920,
        height=1080,
        track_name="main_video_6",
        transform_y=0.1,
        scale_x=0.8,
        scale_y=0.8,
        transform_x=0.1,
        speed=1.2,
        target_start=0,
        relative_index=0
    )

    # 保存草稿
    if video_result.get('success') and video_result.get('output'):
        print(json.loads(query_script_impl(video_result['output']['draft_id'])['output']))
        # query_draft_status_impl_polling(video_result['output']['draft_id'])
        # save_draft_impl(video_result['output']['draft_id'], draft_folder)
   
def test_stiker_01():
    """测试添加贴纸"""
    # 添加贴纸，测试各种参数
    draft_folder = "/Users/sunguannan/Movies/JianyingPro/User Data/Projects/com.lveditor.draft"
    result = add_sticker_impl(
        resource_id="7107529669750066445",
        start=1.0,
        end=4.0,
        transform_y=0.3,      # 向上移动
        transform_x=-0.2,     # 向左移动
        alpha=0.8,            # 设置透明度
        rotation=45.0,        # 旋转45度
        scale_x=1.5,          # 水平放大1.5倍
        scale_y=1.5,          # 垂直放大1.5倍
        flip_horizontal=True  # 水平翻转
    )
    print(f"添加贴纸结果: {save_draft_impl(result['output']['draft_id'], draft_folder)}")

def test_stiker_02():
    """测试添加贴纸"""
    # 添加贴纸，测试各种参数
    draft_folder = "/Users/sunguannan/Movies/JianyingPro/User Data/Projects/com.lveditor.draft"
    result = add_sticker_impl(
        resource_id="7107529669750066445",
        start=1.0,
        end=4.0,
        transform_y=0.3,      # 向上移动
        transform_x=-0.2,     # 向左移动
        alpha=0.8,            # 设置透明度
        rotation=45.0,        # 旋转45度
        scale_x=1.5,          # 水平放大1.5倍
        scale_y=1.5,          # 垂直放大1.5倍
        flip_horizontal=True  # 水平翻转
    )
    result = add_sticker_impl(
        resource_id="7107529669750066445",
        draft_id=result['output']['draft_id'],
        start=5.0,
        end=10.0,
        transform_y=-0.3,      # 向上移动
        transform_x=0.5,     # 向左移动
        alpha=0.1,            # 设置透明度
        rotation=30.0,        # 旋转45度
        scale_x=1.5,          # 水平放大1.5倍
        scale_y=1.2,          # 垂直放大1.5倍
    )
    print(f"添加贴纸结果: {save_draft_impl(result['output']['draft_id'], draft_folder)}")

def test_stiker_03():
    """测试添加贴纸"""
    # 添加贴纸，测试各种参数
    draft_folder = "/Users/sunguannan/Movies/JianyingPro/User Data/Projects/com.lveditor.draft"
    result = add_sticker_impl(
        resource_id="7107529669750066445",
        start=1.0,
        end=4.0,
        transform_y=0.3,      # 向上移动
        transform_x=-0.2,     # 向左移动
        alpha=0.8,            # 设置透明度
        rotation=45.0,        # 旋转45度
        scale_x=1.5,          # 水平放大1.5倍
        scale_y=1.5,          # 垂直放大1.5倍
        flip_horizontal=True,  # 水平翻转
        track_name="stiker_main",
        relative_index=999
    )
    result = add_sticker_impl(
        resource_id="7107529669750066445",
        draft_id=result['output']['draft_id'],
        start=5.0,
        end=10.0,
        transform_y=-0.3,      # 向上移动
        transform_x=0.5,     # 向左移动
        alpha=0.1,            # 设置透明度
        rotation=30.0,        # 旋转45度
        scale_x=1.5,          # 水平放大1.5倍
        scale_y=1.2,          # 垂直放大1.5倍
        track_name="stiker_main_2",
        relative_index=0
    )
    print(f"添加贴纸结果: {save_draft_impl(result['output']['draft_id'], draft_folder)}")


def test_transition_01():
    """测试添加多个图片"""
    draft_folder = "/Users/sunguannan/Movies/JianyingPro/User Data/Projects/com.lveditor.draft"

    print("\n测试：添加图片1")
    image_result = add_image_impl(
        image_url="https://cdn.wanx.aliyuncs.com/wanx/1719234057367822001/text_to_image_v2/d6e33c84d7554146a25b1093b012838b_0.png?x-oss-process=image/resize,w_500/watermark,image_aW1nL3dhdGVyMjAyNDExMjkwLnBuZz94LW9zcy1wcm9jZXNzPWltYWdlL3Jlc2l6ZSxtX2ZpeGVkLHdfMTQ1LGhfMjU=,t_80,g_se,x_10,y_10/format,webp",
        width=480,
        height=480,
        start=0,
        end=5.0,
        transform_y=0.7,
        scale_x=2.0,
        scale_y=1.0,
        transform_x=0,
        track_name="main",
        transition="动漫漩涡",
        transition_duration=1.0
    )
    print(f"添加图片成功1！{image_result['output']['draft_id']}")
    
    print("\n测试：添加图片2")
    image_result = add_image_impl(
        draft_id=image_result['output']['draft_id'],
        image_url="https://cdn.wanx.aliyuncs.com/wanx/1719234057367822001/text_to_image_v2/d6e33c84d7554146a25b1093b012838b_0.png?x-oss-process=image/resize,w_500/watermark,image_aW1nL3dhdGVyMjAyNDExMjkwLnBuZz94LW9zcy1wcm9jZXNzPWltYWdlL3Jlc2l6ZSxtX2ZpeGVkLHdfMTQ1LGhfMjU=,t_80,g_se,x_10,y_10/format,webp",
        width=480,
        height=480,
        start=5,
        end=10.0,
        transform_y=0.7,
        scale_x=2.0,
        scale_y=1.0,
        transform_x=0,
        track_name="main"
    )
    print(f"添加图片成功2！{image_result['output']['draft_id']}")
    print(save_draft_impl(image_result['output']['draft_id'], draft_folder))


def test_transition_02():
    """测试添加视频轨道"""
    draft_folder = "/Users/sunguannan/Movies/JianyingPro/User Data/Projects/com.lveditor.draft"
    video_url = "https://cdn.wanx.aliyuncs.com/wanx/1719234057367822001/text_to_video/092faf3c94244973ab752ee1280ba76f.mp4?spm=5176.29623064.0.0.41ed26d6cBOhV3&file=092faf3c94244973ab752ee1280ba76f.mp4" # 替换为实际视频URL

    print("\n测试：添加视频轨道")
    video_result = add_video_impl(
        video_url=video_url,
        width=1920,
        height=1080,
        start=0,
        end=5.0, # 截取视频前5秒
        target_start=0,
        track_name="main_video_track",
        transition="动漫漩涡",
        transition_duration=1.0
    )
    print(f"视频轨道添加结果: {video_result}")

    print("\n测试：添加视频轨道")
    video_result = add_video_impl(
        video_url=video_url,
        draft_id=video_result['output']['draft_id'],
        width=1920,
        height=1080,
        start=0,
        end=5.0, # 截取视频前5秒
        target_start=5.0,
        track_name="main_video_track"
    )
    print(f"视频轨道添加结果: {video_result}")

    if video_result and 'output' in video_result and 'draft_id' in video_result['output']:
        draft_id = video_result['output']['draft_id']
        print(f"保存草稿: {save_draft_impl(draft_id, draft_folder)}")
    else:
        print("无法获取草稿ID，跳过保存操作。")

def test_generate_image01():
    """测试添加图片"""
    draft_folder = "/Users/sunguannan/Movies/JianyingPro/User Data/Projects/com.lveditor.draft"

    print("\n测试：添加图片1")
    image_result = generate_image_impl(
        prompt="An Asian style doodle person floating in rough sea waves labeled 'Job Market', throwing paper boats made of resumes that are sinking, with a bank account notification bubble showing low balance. Atmosphere: Lost, anxious, turbulent. Art style: Minimalist line art, black and white cartoon style, bold outlines, extremely thick lines, expressive emotions, simple doodle, monochromatic. Composition: Wide angle showing person in center of chaotic elements. Lighting: Harsh contrast.",
        width=1024,
        height=1024,
        start=0,
        end=5.0,
        transform_y=0.7,
        scale_x=2.0,
        scale_y=1.0,
        transform_x=0,
        track_name="main"
    )
    print(f"生成图片成功！{image_result['output']['draft_id']}")
    print(save_draft_impl(image_result['output']['draft_id'], draft_folder))

def generate_speech_impl(texts, draft_id=None, audio_track_name=None, language="中文", 
                        speaker_id="爽快思思/Skye",azure_speaker_id=None, speed_ratio=1.0, start_offset=0.0,
                        end_padding=0.0, interval_time=0.5, volume=1.0, width=1080, height=1920,
                        add_subtitle=True, text_track_name=None, font="文轩体", 
                        font_color="#ffffff", font_size=8.0, transform_y=-0.8, transform_x=0,
                        vertical=False, font_alpha=1.0, border_alpha=1.0, border_color="#000000",
                        border_width=0.0, background_color="#000000", background_style=1,
                        background_alpha=0.0, bubble_effect_id=None, bubble_resource_id=None,
                        effect_effect_id=None, intro_animation=None, intro_duration=0.5,
                        outro_animation=None, outro_duration=0.5):
    """生成TTS语音并添加到草稿中的API调用"""
    data = {
        "license_key": LICENSE_KEY,  # 使用体验版license key
        "texts": texts,
        "audio_track_name": audio_track_name,
        "language": language,
        "speaker_id": speaker_id,
        "azure_speaker_id": azure_speaker_id,
        "speed_ratio": speed_ratio,
        "start_offset": start_offset,
        "end_padding": end_padding,
        "interval_time": interval_time,
        "volume": volume,
        "width": width,
        "height": height,
        "add_subtitle": add_subtitle,
        "text_track_name": text_track_name,
        "font": font,
        "font_color": font_color,
        "font_size": font_size,
        "transform_y": transform_y,
        "transform_x": transform_x,
        "vertical": vertical,
        "font_alpha": font_alpha,
        "border_alpha": border_alpha,
        "border_color": border_color,
        "border_width": border_width,
        "background_color": background_color,
        "background_style": background_style,
        "background_alpha": background_alpha,
        "bubble_effect_id": bubble_effect_id,
        "bubble_resource_id": bubble_resource_id,
        "effect_effect_id": effect_effect_id,
        "intro_animation": intro_animation,
        "intro_duration": intro_duration,
        "outro_animation": outro_animation,
        "outro_duration": outro_duration
    }
    
    if draft_id:
        data["draft_id"] = draft_id
        
    return make_request("generate_speech", data)

def test_generate_image02():
    """测试添加图片"""
    draft_folder = "/Users/sunguannan/Movies/JianyingPro/User Data/Projects/com.lveditor.draft"

    print("\n测试：添加图片1")
    image_result = generate_image_impl(
        prompt="一只猫咪在花园里",
        width=1024,
        height=1024,
        start=0,
        end=5.0,
        transform_y=0.7,
        scale_x=2.0,
        scale_y=1.0,
        transform_x=0,
        track_name="main"
    )
    print("\n测试：添加图片2")
    image_result = generate_image_impl(
        prompt="3只狗在雪地里跑",
        draft_id=image_result['output']['draft_id'],
        width=576,
        height=1024,
        start=5.0,
        end=10.0,
        transform_y=-0.7,
        scale_x=2.0,
        scale_y=2.0,
        transform_x=0,
        track_name="main"
    )
    print(f"生成图片成功！{image_result['output']['draft_id']}")
    print(save_draft_impl(image_result['output']['draft_id'], draft_folder))

@timing_decorator('TTS语音生成')
def test_speech_01():
    """测试TTS语音生成和字幕添加"""
    draft_folder = "/Users/sunguannan/Movies/JianyingPro/User Data/Projects/com.lveditor.draft"

    print("\n测试：生成TTS语音并添加字幕")
    speech_result = generate_speech_impl(
        texts=["大家好，欢迎来到我的视频", "今天我们要讲解一个有趣的话题","孩子不想要去上学该怎么办", "希望大家能够喜欢这个内容","大家好，欢迎来到我的视频", "今天我们要讲解一个有趣的话题","孩子不想要去上学该怎么办", "希望大家能够喜欢这个内容","大家好，欢迎来到我的视频", "今天我们要讲解一个有趣的话题","孩子不想要去上学该怎么办", "希望大家能够喜欢这个内容"],
        language="中文",
        draft_id="123",
        speaker_id="渊博小叔",
        azure_speaker_id="zh-CN-YunjianNeural",
        speed_ratio=1.0,
        start_offset=1.0,
        end_padding=1.0,
        interval_time=0.5,
        volume=0.8,
        width=1080,
        height=1920,
        add_subtitle=True,
        font="文轩体",
        font_color="#ffffff",
        font_size=8.0,
        transform_y=-0.8,
        transform_x=0,
        border_width=2.0,
        border_color="#000000",
        border_alpha=0.8
    )
    print(f"TTS语音生成结果: {speech_result}")
    
    # if speech_result.get('success'):
    #     # 保存草稿
    #     save_result = save_draft_impl(speech_result['output']['draft_id'], draft_folder)
    #     print(f"保存草稿结果: {save_result}")
    # else:
    #     print(f"TTS生成失败: {speech_result.get('error')}")

if __name__ == "__main__":
    # test01()
    # test02()
    # test_effect_01()  # 运行特效测试
    # test_audio01()
    # test_audio02()
    # test_audio03()
    # test_audio04()
    test_image01()
    # test_image02()
    # test_image03()
    # test_image04()
    # test_video()
    # test_video_02()
    # test_text()
    # test_video_track01()
    # test_video_track02()
    # test_video_track03()
    # test_video_track04()
    # test_keyframe()
    # test_keyframe_02()
    # test_subtitle_01()
    # test_subtitle_02()
    # test_subtitle()
    # test_stiker_01()
    # test_stiker_02()
    # test_stiker_03()
    # test_transition_01()
    # test_transition_02()
    # test_generate_image01()
    # test_generate_image02()
    # test_speech_01()
    # test_mask_01()
    # test_mask_02()
