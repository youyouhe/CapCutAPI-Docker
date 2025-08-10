import requests
import json
import time
import sys
import os

# 添加当前目录到Python路径，以便导入本地模块
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
draft_folder = "E:\\Users\\Administrator\\AppData\\Local\\JianyingPro\\User Data\\Projects\\com.lveditor.draft"
def test_official_api_effects():
    # 官网API地址和密钥
    BASE_URL = "https://open.capcutapi.top/cut_jianying"
    API_KEY = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJjZ1UwMk5xeEk4V0Y0UGpTbnhDbGFZVHphSkYzIiwibmFtZSI6ImNnVTAyTnF4SThXRjRQalNueENsYVlUemFKRjMiLCJpYXQiOjB9.RTXRezIRQx_n44rRi4c-RrB6nDYfkczkMj-ogt3SzlNDWKVkB4k0ouezQ-BqnP6rmJjVVa5EKV-8CZ-IkT0cpSX2WdYS_8jACIWE0KJJx7HvtaeRZ1Oz50yV5H5aZhpfg-lZSjLEAwDAuajTQZkSYaattA7YTY4DIqPgUTWQ5bPE41WG_YpzlSv3cGFl6o-rq9dvZ4i6R0hubI4GSzcJlqtlm-BvEIYXosMWEWknozT2AuJvsglXRKwB4adLsXLakKAdjE86gs-L4gy4ck_bCQc0vLeSr3MKDIgc3qAaGB9QFB05ucW4p6J7oCjZjx74CGL4aF5ROXo22R_k_wWd2w"
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    print("=== CapCutAPI 官网特效测试程序 ===")
    print(f"服务器地址: {BASE_URL}")
    print()
    
    try:
        # 1. 创建草稿
        print("1. 正在创建草稿...")
        create_response = requests.post(f"{BASE_URL}/create_draft", 
                                      headers=headers,
                                      json={
                                          "width": 1080,
                                          "height": 1920
                                      }, 
                                      timeout=30)
        
        print(f"创建草稿响应状态码: {create_response.status_code}")
        print(f"创建草稿响应内容: {create_response.text}")
        
        draft_info = create_response.json()
        if not draft_info["success"]:
            print("创建草稿失败:", draft_info["error"])
            return
        
        draft_id = draft_info["output"]["draft_id"]
        print(f"✓ 草稿创建成功，ID: {draft_id}")
        print()
        
        # 2. 测试添加Ripple特效
        print("2. 正在添加Ripple特效...")
        effect_response = requests.post(f"{BASE_URL}/add_effect", 
                                       headers=headers,
                                       json={
                                           "draft_id": draft_id,
                                           "effect_type": "_1998",  # Ripple特效
                                           "start": 0,    # 特效开始时间
                                           "end": 3,      # 特效持续3秒
                                           "track_name": "effect_track_1",
                                           "width": 1080,
                                           "height": 1920
                                       }, 
                                       timeout=30)
        
        print(f"添加特效响应状态码: {effect_response.status_code}")
        print(f"添加特效响应内容: {effect_response.text}")
        
        effect_result = effect_response.json()
        if not effect_result["success"]:
            print("添加Ripple特效失败:", effect_result["error"])
        else:
            print("✓ Ripple特效添加成功")
        
        print()
        
        # 3. 测试其他可能的Ripple相关特效
        ripple_variants = ["水波纹", "老电影", "老电视卡顿"]
        for i, variant in enumerate(ripple_variants):
            print(f"{i+3}. 正在测试 {variant} 特效...")
            effect_response = requests.post(f"{BASE_URL}/add_effect", 
                                           headers=headers,
                                           json={
                                               "draft_id": draft_id,
                                               "effect_type": variant,
                                               "start": i*3,    
                                               "end": i*3 + 3,     
                                               "track_name": f"effect_track_{i+2}",
                                               "width": 1080,
                                               "height": 1920
                                           }, 
                                           timeout=30)
            
            print(f"添加{variant}特效响应状态码: {effect_response.status_code}")
            print(f"添加{variant}特效响应内容: {effect_response.text}")
            
            effect_result = effect_response.json()
            if not effect_result["success"]:
                print(f"添加{variant}特效失败:", effect_result["error"])
            else:
                print(f"✓ {variant}特效添加成功")
            
            print()
        
        # 4. 保存草稿
        print(f"{len(ripple_variants)+3}. 正在保存草稿...")
        save_response = requests.post(f"{BASE_URL}/save_draft", 
                                     headers=headers,
                                     json={
                                         "draft_id": draft_id,
                                         "draft_folder": draft_folder  # 临时目录
                                     }, 
                                     timeout=120)
        
        print(f"保存草稿响应状态码: {save_response.status_code}")
        print(f"保存草稿响应内容: {save_response.text}")
        
        save_result = save_response.json()
        if not save_result["success"]:
            print("保存草稿失败:", save_result["error"])
        else:
            print("✓ 草稿保存成功")
            if "draft_url" in save_result["output"]:
                print("下载链接:", save_result["output"]["draft_url"])
        
        print()
        print("=== 测试完成 ===")
        print(f"草稿ID: {draft_id}")
        
    except requests.exceptions.ConnectionError:
        print("错误: 无法连接到服务器")
    except requests.exceptions.Timeout:
        print("错误: 请求超时")
    except Exception as e:
        print(f"发生错误: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_official_api_effects()
