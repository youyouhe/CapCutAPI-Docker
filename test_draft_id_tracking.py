#!/usr/bin/env python3
"""
测试脚本：检查所有API实现是否正确传递draft_id
"""

import re

# 要检查的文件列表
files_to_check = [
    'add_audio_track.py',
    'add_video_track.py',
    'add_effect_impl.py',
    'add_subtitle_impl.py',
    'add_text_impl.py',
    'add_image_impl.py',
    'add_sticker_impl.py',
    'add_video_keyframe_impl.py',
    'save_draft_impl.py'
]

print("🔍 检查API实现中的draft_id传递情况")

for filename in files_to_check:
    print(f"\n📁 检查文件: {filename}")
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()

        # 查找get_or_create_draft的调用
        pattern = r'get_or_create_draft\s*\('
        matches = re.findall(pattern, content)
        if matches:
            print(f"  ✅ 找到 get_or_create_draft 调用: {len(matches)} 个")
            for i, match in enumerate(matches):
                print(f"    {i+1}. {match}")
        else:
            print(f"  ❌ 未找到 get_or_create_draft 调用")

        # 查找是否直接访问DRAFT_CACHE
        cache_accesses = re.findall(r'DRAFT_CACHE\[.*?\]', content)
        if cache_accesses:
            print(f"  ⚠️  直接访问 DRAFT_CACHE: {len(cache_accesses)} 次")
            for i, match in enumerate(cache_accesses):
                print(f"    {i+1}. {match}")
        else:
            print(f"  ❌ 未找到直接 DRAFT_CACHE 访问")

        # 查找直接使用cache_contains或get_cache
        direct_cache_calls = re.findall(r'(cache_contains|get_cache)\s*\(', content)
        if direct_cache_calls:
            print(f"  ⚠️  直接调用缓存函数: {len(direct_cache_calls)} 次")
            for i, match in enumerate(direct_cache_calls):
                print(f"    {i+1}. {match}")
        else:
            print(f"  ❌ 未找到直接缓存函数调用")

    except FileNotFoundError:
        print(f"  ❌ 文件不存在: {filename}")
    except Exception as e:
        print(f"  ❌ 读取文件时出错: {e}")

print("\n🎯 分析完成!")