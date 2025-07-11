import subprocess
import json
import time

def get_video_duration(video_url):
    """
    获取视频时长，支持超时重试。
    :param video_url: 视频URL
    :return: 视频时长（秒）
    """
    
    # 定义重试次数和每次重试的等待时间
    max_retries = 3
    retry_delay_seconds = 1 # 每次重试间隔1秒
    timeout_seconds = 10 # 设置每次尝试的超时时间

    for attempt in range(max_retries):
        print(f"尝试获取视频时长 (第 {attempt + 1}/{max_retries} 次尝试) ...")
        result = {"success": False, "output": 0, "error": None} # 每次重试前重置结果
        
        try:
            command = [
                'ffprobe',
                '-v', 'error',
                '-show_entries', 'stream=duration',
                '-show_entries', 'format=duration',
                '-print_format', 'json',
                video_url
            ]
            
            # 使用 subprocess.run 更灵活地处理超时和输出
            process = subprocess.run(command, 
                                     capture_output=True, 
                                     text=True, # 自动解码为文本
                                     timeout=timeout_seconds, # 使用变量设置超时时间
                                     check=True) # 如果返回非零退出码则抛出CalledProcessError

            info = json.loads(process.stdout)
            
            # 优先从流中获取时长，因为更精确
            media_streams = [s for s in info.get('streams', []) if 'duration' in s]
            
            if media_streams:
                duration = float(media_streams[0]['duration'])
                result["output"] = duration
                result["success"] = True
            # 否则从格式信息中获取时长
            elif 'format' in info and 'duration' in info['format']:
                duration = float(info['format']['duration'])
                result["output"] = duration
                result["success"] = True
            else:
                result["error"] = "未找到音视频时长信息。"
            
            # 如果成功获取时长，直接返回结果，不再重试
            if result["success"]:
                print(f"成功获取时长: {result['output']:.2f} 秒")
                return result

        except subprocess.TimeoutExpired:
            result["error"] = f"获取视频时长超时（超过{timeout_seconds}秒）。"
            print(f"尝试 {attempt + 1} 超时。")
        except subprocess.CalledProcessError as e:
            result["error"] = f"执行 ffprobe 命令出错 (退出码 {e.returncode}): {e.stderr.strip()}"
            print(f"尝试 {attempt + 1} 失败。错误: {e.stderr.strip()}")
        except json.JSONDecodeError as e:
            result["error"] = f"解析 JSON 数据出错: {e}"
            print(f"尝试 {attempt + 1} 失败。JSON 解析错误: {e}")
        except FileNotFoundError:
            result["error"] = "ffprobe 命令未找到。请确保 FFmpeg 已安装且在系统 PATH 中。"
            print("错误: ffprobe 命令未找到，请检查安装。")
            return result # ffprobe本身找不到，无需重试
        except Exception as e:
            result["error"] = f"发生未知错误: {e}"
            print(f"尝试 {attempt + 1} 失败。未知错误: {e}")
        
        # 每次失败后都尝试使用远程服务获取时长
        if not result["success"]:
            print(f"本地获取失败")
            # try:
            #     remote_duration = get_duration(video_url)
            #     if remote_duration is not None:
            #         result["success"] = True
            #         result["output"] = remote_duration
            #         result["error"] = None
            #         print(f"远程服务成功获取时长: {remote_duration:.2f} 秒")
            #         return result  # 远程服务成功，直接返回
            #     else:
            #         print(f"远程服务也无法获取时长 (第 {attempt + 1} 次尝试)")
            # except Exception as e:
            #     print(f"远程服务获取时长失败 (第 {attempt + 1} 次尝试): {e}")
        
        # 如果当前尝试失败且未达到最大重试次数，则等待并准备下一次重试
        if not result["success"] and attempt < max_retries - 1:
            print(f"等待 {retry_delay_seconds} 秒后重试...")
            time.sleep(retry_delay_seconds)
        elif not result["success"] and attempt == max_retries - 1:
            print(f"已达到最大重试次数 {max_retries}，本地和远程服务都无法获取时长。")
            
    return result # 所有重试都失败后返回最后一次的失败结果