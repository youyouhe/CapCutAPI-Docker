import requests
import json

def test_effect_ripples():
    BASE_URL = "http://localhost:9002"
    
    # 创建草稿
    create_response = requests.post(f"{BASE_URL}/create_draft", json={
        "width": 1080,
        "height": 1920
    }, timeout=30)
    
    draft_info = create_response.json()
    if not draft_info["success"]:
        print("创建草稿失败:", draft_info["error"])
        return
    
    draft_id = draft_info["output"]["draft_id"]
    print(f"草稿创建成功，ID: {draft_id}")
    
    # 测试添加Ripples特效
    effect_response = requests.post(f"{BASE_URL}/add_effect", json={
        "draft_id": draft_id,
        "effect_type": "Ripples",
        "start": 0,
        "end": 3,
        "track_name": "effect_track_1",
        "width": 1080,
        "height": 1920
    }, timeout=30)
    
    effect_result = effect_response.json()
    print("特效添加结果:", json.dumps(effect_result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    test_effect_ripples()