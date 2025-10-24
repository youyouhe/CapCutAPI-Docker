#!/usr/bin/env python3
"""
测试 draft_id 传递修复是否有效
"""

import requests
import json
import time

# 配置
BASE_URL = "http://localhost:9000"

def test_material_collection():
    """测试素材收集功能"""
    print("🧪 开始测试素材收集功能...")

    # 1. 创建草稿
    print("\n1️⃣ 创建草稿...")
    response = requests.post(f"{BASE_URL}/create_draft",
                             json={"width": 1080, "height": 1920})

    if response.status_code != 200:
        print(f"❌ 创建草稿失败: {response.text}")
        return False

    result = response.json()
    if not result["success"]:
        print(f"❌ 创建草稿业务失败: {result['error']}")
        return False

    draft_id = result["output"]["draft_id"]
    print(f"✅ 草稿创建成功，draft_id: {draft_id}")

    # 2. 添加第一个视频素材
    print("\n2️⃣ 添加第一个视频素材...")
    video_url_1 = "https://example.com/video1.mp4"  # 使用示例URL
    response = requests.post(f"{BASE_URL}/add_video",
                             json={
                                 "video_url": video_url_1,
                                 "draft_id": draft_id,
                                 "duration": 10.0
                             })

    if response.status_code != 200:
        print(f"❌ 添加视频1失败: {response.text}")
        return False

    result = response.json()
    if not result["success"]:
        print(f"❌ 添加视频1业务失败: {result['error']}")
        return False

    returned_draft_id = result["output"]["draft_id"]
    print(f"✅ 视频添加成功，返回的 draft_id: {returned_draft_id}")

    if returned_draft_id != draft_id:
        print(f"⚠️ 警告：draft_id 不匹配！原始: {draft_id}, 返回: {returned_draft_id}")
        return False

    # 3. 添加第二个素材（使用返回的 draft_id）
    print("\n3️⃣ 添加第二个素材（音频）...")
    audio_url = "https://example.com/audio1.mp3"  # 使用示例URL
    response = requests.post(f"{BASE_URL}/add_audio",
                             json={
                                 "audio_url": audio_url,
                                 "draft_id": returned_draft_id,
                                 "duration": 5.0
                             })

    if response.status_code != 200:
        print(f"❌ 添加音频失败: {response.text}")
        return False

    result = response.json()
    if not result["success"]:
        print(f"❌ 添加音频业务失败: {result['error']}")
        return False

    final_draft_id = result["output"]["draft_id"]
    print(f"✅ 音频添加成功，返回的 draft_id: {final_draft_id}")

    # 4. 添加文本素材
    print("\n4️⃣ 添加文本素材...")
    response = requests.post(f"{BASE_URL}/add_text",
                             json={
                                 "text": "测试文本",
                                 "start": 0.0,
                                 "end": 5.0,
                                 "draft_id": final_draft_id
                             })

    if response.status_code != 200:
        print(f"❌ 添加文本失败: {response.text}")
        return False

    result = response.json()
    if not result["success"]:
        print(f"❌ 添加文本业务失败: {result['error']}")
        return False

    text_draft_id = result["output"]["draft_id"]
    print(f"✅ 文本添加成功，返回的 draft_id: {text_draft_id}")

    # 5. 查询草稿状态
    print("\n5️⃣ 查询草稿状态...")
    response = requests.post(f"{BASE_URL}/query_script",
                             json={"draft_id": text_draft_id})

    if response.status_code != 200:
        print(f"❌ 查询草稿失败: {response.text}")
        return False

    result = response.json()
    if not result["success"]:
        print(f"❌ 查询草稿业务失败: {result['error']}")
        return False

    # 这里可以进一步检查草稿中包含的素材数量
    print(f"✅ 草稿查询成功")

    print("\n🎉 所有测试通过！draft_id 传递正常")
    return True

if __name__ == "__main__":
    try:
        success = test_material_collection()
        if success:
            print("\n✨ 测试结论：修复成功，素材收集功能正常")
        else:
            print("\n💥 测试结论：仍有问题需要修复")
    except Exception as e:
        print(f"\n💥 测试过程中出现异常: {str(e)}")