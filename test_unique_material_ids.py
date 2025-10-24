#!/usr/bin/env python3
"""
测试素材ID唯一性修复的脚本
验证相同URL的素材是否能生成不同的material_id
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'pyJianYingDraft'))

from pyJianYingDraft.local_materials import Audio_material, Video_material

def test_audio_material_uniqueness():
    """测试Audio_material的material_id唯一性"""
    print("🎵 测试Audio_material的material_id唯一性...")

    # 使用相同URL创建多个Audio_material实例
    test_url = "https://example.com/bubble.mp3"
    material_ids = []

    for i in range(6):
        audio = Audio_material(
            remote_url=test_url,
            material_name=f"bubble_audio_track_{i+1}",
            duration=1.0  # 传入duration避免ffprobe检查
        )
        material_ids.append(audio.material_id)
        print(f"  音频{i+1}: {audio.material_id}")

    # 检查唯一性
    unique_ids = set(material_ids)
    if len(unique_ids) == len(material_ids):
        print("✅ Audio_material的material_id全部唯一！")
        return True
    else:
        print(f"❌ Audio_material的material_id有重复！预期{len(material_ids)}个，实际{len(unique_ids)}个唯一")
        return False

def test_video_material_uniqueness():
    """测试Video_material的material_id唯一性"""
    print("\n🎬 测试Video_material的material_id唯一性...")

    # 使用相同URL创建多个Video_material实例
    test_url = "https://example.com/background.mp4"
    material_ids = []

    for i in range(6):
        video = Video_material(
            remote_url=test_url,
            material_name=f"video_track_{i+1}",
            material_type="video",
            duration=2.0,  # 传入duration避免ffprobe检查
            width=1920,    # 传入width避免ffprobe检查
            height=1080    # 传入height避免ffprobe检查
        )
        material_ids.append(video.material_id)
        print(f"  视频{i+1}: {video.material_id}")

    # 检查唯一性
    unique_ids = set(material_ids)
    if len(unique_ids) == len(material_ids):
        print("✅ Video_material的material_id全部唯一！")
        return True
    else:
        print(f"❌ Video_material的material_id有重复！预期{len(material_ids)}个，实际{len(unique_ids)}个唯一")
        return False

def test_mixed_materials():
    """测试混合类型的素材不会冲突"""
    print("\n🔄 测试混合类型素材的唯一性...")

    test_url = "https://example.com/test.mp4"
    all_material_ids = []

    # 创建音频素材
    for i in range(3):
        audio = Audio_material(
            remote_url=test_url,
            material_name=f"audio_test_{i+1}",
            duration=1.0  # 传入duration避免ffprobe检查
        )
        all_material_ids.append(audio.material_id)
        print(f"  音频{i+1}: {audio.material_id}")

    # 创建视频素材
    for i in range(3):
        video = Video_material(
            remote_url=test_url,
            material_name=f"video_test_{i+1}",
            material_type="video",
            duration=2.0,  # 传入duration避免ffprobe检查
            width=1920,    # 传入width避免ffprobe检查
            height=1080    # 传入height避免ffprobe检查
        )
        all_material_ids.append(video.material_id)
        print(f"  视频{i+1}: {video.material_id}")

    # 检查全局唯一性
    unique_ids = set(all_material_ids)
    if len(unique_ids) == len(all_material_ids):
        print("✅ 所有素材的material_id都唯一！")
        return True
    else:
        print(f"❌ 素材的material_id有重复！预期{len(all_material_ids)}个，实际{len(unique_ids)}个唯一")
        return False

if __name__ == "__main__":
    print("🚀 开始测试素材ID唯一性修复...")

    test_results = []
    test_results.append(test_audio_material_uniqueness())
    test_results.append(test_video_material_uniqueness())
    test_results.append(test_mixed_materials())

    print(f"\n📊 测试结果总结:")
    print(f"   通过测试: {sum(test_results)}/{len(test_results)}")

    if all(test_results):
        print("🎉 所有测试通过！素材ID唯一性修复成功！")
        sys.exit(0)
    else:
        print("❌ 部分测试失败，需要进一步检查")
        sys.exit(1)