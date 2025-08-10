import requests
import json
import time
import sys
import os

# 添加当前目录到Python路径，以便导入本地模块
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from get_duration_impl import get_video_duration

def get_video_info(video_url):
    """获取视频信息，包括时长"""
    print(f"正在获取视频信息: {video_url}")
    duration_result = get_video_duration(video_url)
    
    if not duration_result["success"]:
        print(f"获取视频时长失败: {duration_result['error']}")
        return None
    
    duration = duration_result["output"]
    print(f"视频时长: {duration:.2f} 秒")
    return {"duration": duration}

def create_draft_with_video_and_bubble_audio():
    # 服务器地址
    BASE_URL = "http://localhost:9002"
    
    # 两个视频URL（使用前两个视频作为示例）
    video_urls = [
        "http://192.168.8.107:9000/youtube-videos/users/1/projects/1/slices/21f965d5-bddf-4121-a317-78470742f5c7/sub_2a273b6b-9919-478d-a33d-882157c467ae_20250809_072408.mp4",
        "http://192.168.8.107:9000/youtube-videos/users/1/projects/1/slices/f7e800bb-c7a3-4e3b-a5a2-03d974f98b99/sub_c46291e7-a0ad-4439-8ea4-4869b57b76eb_20250809_072409.mp4"
    ]
    
    # 草稿文件夹地址 (Windows路径)
    draft_folder = "E:\\Users\\Administrator\\AppData\\Local\\JianyingPro\\User Data\\Projects\\com.lveditor.draft"
    
    print("=== CapCutAPI 视频+水滴音频特效测试程序 ===")
    print(f"服务器地址: {BASE_URL}")
    print(f"草稿文件夹: {draft_folder}")
    print()
    
    try:
        # 1. 创建草稿
        print("1. 正在创建草稿...")
        create_response = requests.post(f"{BASE_URL}/create_draft", json={
            "width": 1080,
            "height": 1920
        }, timeout=30)
        
        draft_info = create_response.json()
        if not draft_info["success"]:
            print("创建草稿失败:", draft_info["error"])
            return
        
        draft_id = draft_info["output"]["draft_id"]
        print(f"✓ 草稿创建成功，ID: {draft_id}")
        print()
        
        # 2. 获取所有视频的时长信息
        print("2. 正在获取视频信息...")
        video_info_list = []
        total_duration = 0
        
        for i, video_url in enumerate(video_urls):
            print(f"  获取第{i+1}个视频信息...")
            video_info = get_video_info(video_url)
            if video_info is None:
                print(f"获取第{i+1}个视频信息失败，跳过该视频")
                return
            video_info_list.append(video_info)
            total_duration += video_info["duration"]
        
        print(f"所有视频总时长: {total_duration:.2f} 秒")
        print()
        
        # 3. 添加水滴音频文件 - 将在第4步中与视频特效一起添加
        print()
        
        # 4. 依次添加视频和视频特效
        current_time = 0
        for i, (video_url, video_info) in enumerate(zip(video_urls, video_info_list)):
            # 添加视频特效 (水波纹)
            print(f"{i*2+3}. 正在添加第{i+1}个视频的水波纹特效...")
            effect_response = requests.post(f"{BASE_URL}/add_effect", json={
                "draft_id": draft_id,
                "effect_type": "水波纹",  # 水波纹特效
                "start": current_time,    # 特效开始时间 (视频开始时)
                "end": current_time + 3,  # 特效持续3秒
                "track_name": f"effect_track_{i+1}",
                "width": 1080,
                "height": 1920
            }, timeout=30)
            
            effect_result = effect_response.json()
            if not effect_result["success"]:
                print(f"添加第{i+1}个视频的特效失败:", effect_result["error"])
                print("跳过特效，继续添加视频...")
            else:
                print(f"✓ 第{i+1}个视频的水波纹特效添加成功")
            
            # 添加水滴音频（与特效时长相同）
            print(f"{i*2+4}. 正在添加第{i+1}个视频的水滴音频...")
            audio_response = requests.post(f"{BASE_URL}/add_audio", json={
                "draft_id": draft_id,
                "audio_url": "http://tmpfiles.org/dl/9816523/mixkit-liquid-bubble-3000.wav",  # 使用在线音频文件
                "start": 0,
                "end": 3,  # 只覆盖特效时长（3秒）
                "track_name": f"bubble_audio_track_{i+1}",
                "volume": 0.5,  # 设置音量
                "target_start": current_time,  # 音频在时间线上的起始位置（与特效同步）
                "width": 1080,
                "height": 1920
            }, timeout=60)
            
            audio_result = audio_response.json()
            if not audio_result["success"]:
                print(f"添加第{i+1}个视频的水滴音频失败:", audio_result["error"])
                print("继续执行其他步骤...")
            else:
                print(f"✓ 第{i+1}个视频的水滴音频添加成功")
            
            # 添加视频
            print(f"{i*2+5}. 正在添加第{i+1}个视频...")
            video_response = requests.post(f"{BASE_URL}/add_video", json={
                "draft_id": draft_id,
                "video_url": video_url,
                "start": 0,
                "end": video_info["duration"],  # 使用视频实际时长
                "width": 1080,
                "height": 1920,
                "track_name": f"video_track_{i+1}",
                "target_start": current_time  # 视频在时间线上的起始位置
            }, timeout=60)
            
            video_result = video_response.json()
            if not video_result["success"]:
                print(f"添加第{i+1}个视频失败:", video_result["error"])
                return
            
            print(f"✓ 第{i+1}个视频添加成功 (时长: {video_info['duration']:.2f}秒, 起始时间: {current_time:.2f}秒)")
            current_time += video_info["duration"]
        
        print()
        
        # 5. 添加覆盖文本
        print(f"{len(video_urls)*3+3}. 正在添加覆盖文本...")
        text_response = requests.post(f"{BASE_URL}/add_text", json={
            "draft_id": draft_id,
            "text": "视频+水滴音频特效测试",
            "start": 0,
            "end": total_duration,  # 覆盖整个视频时长
            "font": "挥墨体",
            "font_color": "#ffde00",
            "font_size": 12.0,
            "track_name": "text_track_1",
            "transform_x": 0,    # 最左侧
            "transform_y": 0.15, # 靠近顶部
            "font_alpha": 1.0,
            "border_alpha": 1.0,
            "border_color": "#000000",
            "border_width": 15.0,
            "width": 1080,
            "height": 1920
        }, timeout=30)
        
        text_result = text_response.json()
        if not text_result["success"]:
            print("添加文本失败:", text_result["error"])
            return
        
        print("✓ 文本添加成功")
        print()
        
        # 6. 保存草稿并上传到MinIO
        print(f"{len(video_urls)*3+4}. 正在保存草稿并上传到MinIO...")
        save_response = requests.post(f"{BASE_URL}/save_draft", json={
            "draft_id": draft_id,
            "draft_folder": draft_folder
        }, timeout=120)  # 增加超时时间，因为上传可能需要更长时间
        
        save_result = save_response.json()
        print("保存草稿完整响应:", json.dumps(save_result, indent=2, ensure_ascii=False))
        
        if not save_result["success"]:
            print("保存草稿失败:", save_result["error"])
            return
        
        print("✓ 草稿保存并上传成功")
        if "draft_url" in save_result["output"]:
            print("下载链接:", save_result["output"]["draft_url"])
        else:
            print("下载链接未生成")
        print()
        
        print("=== 测试完成 ===")
        print(f"草稿ID: {draft_id}")
        print("时间线:")
        current_time = 0
        for i, video_info in enumerate(video_info_list):
            start_time = current_time
            end_time = current_time + video_info["duration"]
            print(f"  {start_time:.2f}-{end_time:.2f}秒: 第{i+1}个视频")
            print(f"  {start_time:.2f}-{start_time+3:.2f}秒: 水波纹特效 + 水滴音频 (开头3秒)")
            current_time = end_time
        print(f"  0-{total_duration:.2f}秒: 文本显示 (覆盖整个视频)")
        print("请在剪映中查看生成的草稿文件")
        
    except requests.exceptions.ConnectionError:
        print("错误: 无法连接到服务器，请确保 capcut_server.py 正在运行")
    except requests.exceptions.Timeout:
        print("错误: 请求超时，请检查网络连接或服务器状态")
    except Exception as e:
        print(f"发生错误: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    create_draft_with_video_and_bubble_audio()