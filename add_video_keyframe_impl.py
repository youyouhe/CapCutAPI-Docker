import pyJianYingDraft as draft
from pyJianYingDraft import exceptions
from create_draft import get_or_create_draft
from typing import Optional, Dict, List

from util import generate_draft_url

def add_video_keyframe_impl(
    draft_id: Optional[str] = None,
    track_name: str = "main",
    property_type: str = "alpha",
    time: float = 0.0,
    value: str = "1.0",
    property_types: Optional[List[str]] = None,
    times: Optional[List[float]] = None,
    values: Optional[List[str]] = None
) -> Dict[str, str]:
    """
    向指定片段添加关键帧
    :param draft_id: 草稿ID，如果为None或找不到对应的zip文件，则创建新草稿
    :param track_name: 轨道名称，默认"main"
    :param property_type: 关键帧属性类型，支持以下值：
        - position_x: 水平位置，范围[-1,1]，0表示居中，1表示最右边
        - position_y: 垂直位置，范围[-1,1]，0表示居中，1表示最下边
        - rotation: 顺时针旋转角度
        - scale_x: X轴缩放比例(1.0为不缩放)，与uniform_scale互斥
        - scale_y: Y轴缩放比例(1.0为不缩放)，与uniform_scale互斥
        - uniform_scale: 整体缩放比例(1.0为不缩放)，与scale_x和scale_y互斥
        - alpha: 不透明度，1.0为完全不透明
        - saturation: 饱和度，0.0为原始饱和度，范围为-1.0到1.0
        - contrast: 对比度，0.0为原始对比度，范围为-1.0到1.0
        - brightness: 亮度，0.0为原始亮度，范围为-1.0到1.0
        - volume: 音量，1.0为原始音量
    :param time: 关键帧时间点（秒），默认0.0
    :param value: 关键帧值，格式根据property_type不同而不同：
        - position_x/position_y: "0"表示居中位置，范围[-1,1]
        - rotation: "45deg"表示45度
        - scale_x/scale_y/uniform_scale: "1.5"表示放大1.5倍
        - alpha: "50%"表示50%不透明度
        - saturation/contrast/brightness: "+0.5"表示增加0.5，"-0.5"表示减少0.5
        - volume: "80%"表示原始音量的80%
    :param property_types: 批量模式：关键帧属性类型列表，如 ["alpha", "position_x", "rotation"]
    :param times: 批量模式：关键帧时间点列表（秒），如 [0.0, 1.0, 2.0]
    :param values: 批量模式：关键帧值列表，如 ["1.0", "0.5", "45deg"]
    注意：property_types、times、values 三个参数必须同时提供且长度相等，如果提供了这些参数，将忽略单个关键帧参数
    :return: 更新后的草稿信息
    """
    # 获取或创建草稿
    draft_id, script = get_or_create_draft(
        draft_id=draft_id
    )
    
    try:
        # 获取指定轨道
        track = script.get_track(draft.Video_segment, track_name=track_name)
        
        # 获取轨道中的片段
        segments = track.segments
        if not segments:
            raise Exception(f"轨道 {track_name} 中没有片段")
        
        # 确定要处理的关键帧列表
        if property_types is not None or times is not None or values is not None:
            # 批量模式：使用三个数组参数
            if property_types is None or times is None or values is None:
                raise Exception("批量模式下，property_types、times、values 三个参数必须同时提供")
            
            if not (isinstance(property_types, list) and isinstance(times, list) and isinstance(values, list)):
                raise Exception("property_types、times、values 必须都是列表类型")
            
            if len(property_types) == 0:
                raise Exception("批量模式下，参数列表不能为空")
            
            if not (len(property_types) == len(times) == len(values)):
                raise Exception(f"property_types、times、values 的长度必须相等，当前长度分别为：{len(property_types)}, {len(times)}, {len(values)}")
            
            keyframes_to_process = [
                {
                    "property_type": prop_type,
                    "time": t,
                    "value": val
                }
                for prop_type, t, val in zip(property_types, times, values)
            ]
        else:
            # 单个模式：使用原有参数
            keyframes_to_process = [{
                "property_type": property_type,
                "time": time,
                "value": value
            }]
        
        # 处理每个关键帧
        added_count = 0
        for i, kf in enumerate(keyframes_to_process):
            try:
                _add_single_keyframe(track, kf["property_type"], kf["time"], kf["value"])
                added_count += 1
            except Exception as e:
                raise Exception(f"添加第{i+1}个关键帧失败 (property_type={kf['property_type']}, time={kf['time']}, value={kf['value']}): {str(e)}")
        
        result = {
            "draft_id": draft_id,
            "draft_url": generate_draft_url(draft_id)
        }
        
        # 如果是批量模式，返回添加的关键帧数量
        if property_types is not None:
            result["added_keyframes_count"] = added_count
        
        return result
        
    except exceptions.TrackNotFound:
        raise Exception(f"找不到名为 {track_name} 的轨道")
    except Exception as e:
        raise Exception(f"添加关键帧失败: {str(e)}")


def _add_single_keyframe(track, property_type: str, time: float, value: str):
    """
    添加单个关键帧的内部函数
    """
    # 将属性类型字符串转换为枚举值，验证属性类型是否有效
    try:
        property_enum = getattr(draft.Keyframe_property, property_type)
    except:
        raise Exception(f"不支持的关键帧属性类型: {property_type}")
        
    # 根据属性类型解析value值
    try:
        if property_type in ['position_x', 'position_y']:
            # 处理位置，范围[0,1]
            float_value = float(value)
            if not -10 <= float_value <= 10:
                raise ValueError(f"{property_type}的值必须在-10到10之间")
        elif property_type == 'rotation':
            # 处理旋转角度
            if value.endswith('deg'):
                float_value = float(value[:-3])
            else:
                float_value = float(value)
        elif property_type == 'alpha':
            # 处理不透明度
            if value.endswith('%'):
                float_value = float(value[:-1]) / 100
            else:
                float_value = float(value)
        elif property_type == 'volume':
            # 处理音量
            if value.endswith('%'):
                float_value = float(value[:-1]) / 100
            else:
                float_value = float(value)
        elif property_type in ['saturation', 'contrast', 'brightness']:
            # 处理饱和度、对比度、亮度
            if value.startswith('+'):
                float_value = float(value[1:])
            elif value.startswith('-'):
                float_value = -float(value[1:])
            else:
                float_value = float(value)
        else:
            # 其他属性直接转换为浮点数
            float_value = float(value)
    except ValueError:
        raise Exception(f"无效的值格式: {value}")
    
    # 如果提供了轨道对象，则使用轨道的add_pending_keyframe方法
    track.add_pending_keyframe(property_type, time, value)