import requests
import json
import time

def create_draft_with_videos_and_text():
    # 服务器地址
    BASE_URL = "http://localhost:9002"
    
    # 两个真实的视频URL
    video1_url = "http://192.168.8.107:9000/youtube-videos/users/1/projects/1/slices/21f965d5-bddf-4121-a317-78470742f5c7/sub_2a273b6b-9919-478d-a33d-882157c467ae_20250809_072408.mp4"
    video2_url = "http://192.168.8.107:9000/youtube-videos/users/1/projects/1/slices/f7e800bb-c7a3-4e3b-a5a2-03d974f98b99/sub_c46291e7-a0ad-4439-8ea4-4869b57b76eb_20250809_072409.mp4"
    
    # 草稿文件夹地址 (Windows路径)
    draft_folder = "E:\\Users\\Administrator\\AppData\\Local\\JianyingPro\\User Data\\Projects\\com.lveditor.draft"
    
    print("=== CapCutAPI 测试程序 (带文本) ===")
    print(f"服务器地址: {BASE_URL}")
    print(f"视频1 URL: {video1_url}")
    print(f"视频2 URL: {video2_url}")
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
        
        # 2. 添加第一个视频 (0-10秒)
        print("2. 正在添加第一个视频...")
        video1_response = requests.post(f"{BASE_URL}/add_video", json={
            "draft_id": draft_id,
            "video_url": video1_url,
            "start": 0,
            "end": 10,
            "width": 1080,
            "height": 1920,
            "track_name": "video_track_1"
        }, timeout=60)
        
        video1_result = video1_response.json()
        if not video1_result["success"]:
            print("添加第一个视频失败:", video1_result["error"])
            return
        
        print("✓ 第一个视频添加成功")
        print()
        
        # 3. 添加文本 (覆盖整个视频时长，25秒)
        print("3. 正在添加文本...")
        text_response = requests.post(f"{BASE_URL}/add_text", json={
            "draft_id": draft_id,
            "text": "快速前馈网络的出现与新挑战",
            "start": 0,
            "end": 25,  # 覆盖整个视频时长 (第一个视频10秒 + 第二个视频15秒)
            "font": "挥墨体",
            "font_color": "#ffde00",
            "font_size": 12.0,
            "track_name": "text_track_1",
            "transform_x": 0,    # 最左侧
            "transform_y": 0.75, # 靠近顶部
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
        
        # 4. 添加第二个视频 (从第10秒开始，持续15秒，即10-25秒)
        print("4. 正在添加第二个视频...")
        video2_response = requests.post(f"{BASE_URL}/add_video", json={
            "draft_id": draft_id,
            "video_url": video2_url,
            "start": 0,
            "end": 15,
            "width": 1080,
            "height": 1920,
            "track_name": "video_track_2",
            "target_start": 10  # 第二个视频从第10秒开始
        }, timeout=60)
        
        video2_result = video2_response.json()
        if not video2_result["success"]:
            print("添加第二个视频失败:", video2_result["error"])
            return
        
        print("✓ 第二个视频添加成功")
        print()
        
        # 5. 添加字幕
        print("5. 正在添加字幕...")
        subtitle_response = requests.post(f"{BASE_URL}/add_subtitle", json={
            "draft_id": draft_id,
            "srt": "/home/cat/CapCutAPI/subtitle_clean.srt",  # 使用清理后的SRT文件
            "font": "文轩体",  # 使用支持的字体
            "font_size": 8.0,
            "font_color": "#ffde00",
            "transform_x": 0,
            "transform_y": -0.75,  # 靠近底部
            "border_alpha": 1.0,
            "border_color": "#000000",
            "border_width": 15.0,
            "width": 1080,
            "height": 1920
        }, timeout=30)
        
        subtitle_result = subtitle_response.json()
        if not subtitle_result["success"]:
            print("添加字幕失败:", subtitle_result["error"])
            return
        
        print("✓ 字幕添加成功")
        print()
        
        # 6. 保存草稿并上传到MinIO
        print("6. 正在保存草稿并上传到MinIO...")
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
        print("  0-10秒: 第一个视频")
        print("  0-25秒: 文本显示 (覆盖整个视频)")
        print("  10-25秒: 第二个视频")
        print("  0-25秒: 字幕显示 (根据SRT文件时间)")
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
    create_draft_with_videos_and_text()
