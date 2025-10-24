#!/usr/bin/env python3
"""
检查代码版本，确认是否包含我们的修复
"""

def check_debug_logs():
    """检查是否包含调试日志代码"""
    print("🔍 检查代码版本...")

    # 检查 script_file.py 中是否有调试日志
    try:
        with open('/home/cat/CapCutAPI-Docker/pyJianYingDraft/script_file.py', 'r') as f:
            content = f.read()
            if 'DEBUG: add_material called' in content:
                print("✅ script_file.py 包含调试日志")
            else:
                print("❌ script_file.py 不包含调试日志")
    except Exception as e:
        print(f"❌ 读取 script_file.py 失败: {e}")

    # 检查 save_draft_impl.py 中是否有修复
    try:
        with open('/home/cat/CapCutAPI-Docker/save_draft_impl.py', 'r') as f:
            content = f.read()
            if 'CRITICAL ERROR: Requested draft' in content:
                print("✅ save_draft_impl.py 包含 draft_id 检查修复")
            else:
                print("❌ save_draft_impl.py 不包含 draft_id 检查修复")
    except Exception as e:
        print(f"❌ 读取 save_draft_impl.py 失败: {e}")

    # 检查 create_draft.py 中的调试日志
    try:
        with open('/home/cat/CapCutAPI-Docker/create_draft.py', 'r') as f:
            content = f.read()
            if 'Getting draft from cache:' in content:
                print("✅ create_draft.py 包含缓存调试日志")
            else:
                print("❌ create_draft.py 不包含缓存调试日志")
    except Exception as e:
        print(f"❌ 读取 create_draft.py 失败: {e}")

def test_simple_material_add():
    """测试简单的素材添加"""
    print("\n🧪 测试素材添加功能...")

    try:
        from create_draft import get_or_create_draft
        import pyJianYingDraft as draft

        # 创建草稿
        draft_id, script = get_or_create_draft()
        print(f"✅ 创建草稿成功: {draft_id}")

        # 创建视频素材
        video_material = draft.Video_material(
            material_type='video',
            remote_url='http://example.com/test.mp4',
            material_name='test_video.mp4',
            duration=10.0
        )
        print(f"✅ 创建视频素材: {video_material.material_id}")

        # 添加素材
        script.add_material(video_material)
        print(f"✅ 调用 add_material 完成")

        # 检查素材数量
        print(f"📊 视频素材数量: {len(script.materials.videos)}")
        print(f"📊 音频素材数量: {len(script.materials.audios)}")

        # 尝试获取草稿
        retrieved_draft_id, retrieved_script = get_or_create_draft(draft_id=draft_id)
        print(f"✅ 获取草稿成功: {retrieved_draft_id}")
        print(f"📊 获取后的视频素材数量: {len(retrieved_script.materials.videos)}")

        if retrieved_draft_id != draft_id:
            print("❌ 警告：获取的 draft_id 不匹配！")
        else:
            print("✅ draft_id 匹配")

    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_debug_logs()
    test_simple_material_add()