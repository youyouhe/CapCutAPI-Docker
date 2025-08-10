import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 测试直接访问特效类型
try:
    import pyJianYingDraft as draft
    from settings import IS_CAPCUT_ENV
    
    print("IS_CAPCUT_ENV:", IS_CAPCUT_ENV)
    
    # 测试直接访问Ripple
    if IS_CAPCUT_ENV:
        try:
            effect = draft.CapCut_Video_scene_effect_type["Ripple"]
            print("CapCut Ripple effect found:", effect)
        except KeyError as e:
            print("CapCut Ripple not found, error:", e)
            
        try:
            effect = draft.CapCut_Video_character_effect_type["Ripple"]
            print("CapCut Ripple character effect found:", effect)
        except KeyError as e:
            print("CapCut Ripple character not found, error:", e)
    else:
        try:
            effect = draft.Video_scene_effect_type["Ripple"]
            print("JianYing Ripple effect found:", effect)
        except KeyError as e:
            print("JianYing Ripple not found, error:", e)
            
        try:
            effect = draft.Video_character_effect_type["Ripple"]
            print("JianYing Ripple character effect found:", effect)
        except KeyError as e:
            print("JianYing Ripple character not found, error:", e)
            
except Exception as e:
    print("Error:", e)
    import traceback
    traceback.print_exc()