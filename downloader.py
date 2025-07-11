import os
import subprocess
import time
import requests
from requests.exceptions import RequestException, Timeout
from urllib.parse import urlparse, unquote

def download_video(video_url, draft_name, material_name):
    """
    下载视频到指定目录
    :param video_url: 视频URL
    :param draft_name: 草稿名称
    :param material_name: 素材名称
    :return: 本地视频路径
    """
    # 确保目录存在
    video_dir = f"{draft_name}/assets/video"
    os.makedirs(video_dir, exist_ok=True)
    
    # 生成本地文件名
    local_path = f"{video_dir}/{material_name}"
    
    # 检查文件是否已存在
    if os.path.exists(local_path):
        print(f"视频文件已存在: {local_path}")
        return local_path
    
    try:
        # 使用ffmpeg下载视频
        command = [
            'ffmpeg',
            '-i', video_url,
            '-c', 'copy',  # 直接复制，不重新编码
            local_path
        ]
        subprocess.run(command, check=True, capture_output=True)
        return local_path
    except subprocess.CalledProcessError as e:
        raise Exception(f"下载视频失败: {e.stderr.decode('utf-8')}")

def download_image(image_url, draft_name, material_name):
    """
    下载图片到指定目录，并统一转换为PNG格式
    :param image_url: 图片URL
    :param draft_name: 草稿名称
    :param material_name: 素材名称
    :return: 本地图片路径
    """
    # 确保目录存在
    image_dir = f"{draft_name}/assets/image"
    os.makedirs(image_dir, exist_ok=True)
    
    # 统一使用png格式
    local_path = f"{image_dir}/{material_name}"
    
    # 检查文件是否已存在
    if os.path.exists(local_path):
        print(f"图片文件已存在: {local_path}")
        return local_path
    
    try:
        # 使用ffmpeg下载并转换图片为PNG格式
        command = [
            'ffmpeg',
            '-i', image_url,
            '-vf', 'format=rgba',  # 转换为RGBA格式以支持透明度
            '-frames:v', '1',      # 确保只处理一帧
            '-y',                  # 覆盖已存在的文件
            local_path
        ]
        subprocess.run(command, check=True, capture_output=True)
        return local_path
    except subprocess.CalledProcessError as e:
        raise Exception(f"下载图片失败: {e.stderr.decode('utf-8')}")

def download_audio(audio_url, draft_name, material_name):
    """
    下载音频并转码为MP3格式到指定目录
    :param audio_url: 音频URL
    :param draft_name: 草稿名称
    :param material_name: 素材名称
    :return: 本地音频路径
    """
    # 确保目录存在
    audio_dir = f"{draft_name}/assets/audio"
    os.makedirs(audio_dir, exist_ok=True)
    
    # 生成本地文件名（保留.mp3后缀）
    local_path = f"{audio_dir}/{material_name}"
    
    # 检查文件是否已存在
    if os.path.exists(local_path):
        print(f"音频文件已存在: {local_path}")
        return local_path
    
    try:
        # 使用ffmpeg下载并转码为MP3（关键修改：指定MP3编码器）
        command = [
            'ffmpeg',
            '-i', audio_url,          # 输入URL
            '-c:a', 'libmp3lame',     # 强制将音频流编码为MP3
            '-q:a', '2',              # 设置音频质量（0-9，0为最佳，2为平衡质量与文件大小）
            '-y',                     # 覆盖已存在文件（可选）
            local_path                # 输出路径
        ]
        subprocess.run(command, check=True, capture_output=True, text=True)
        return local_path
    except subprocess.CalledProcessError as e:
        raise Exception(f"下载音频失败:\n{e.stderr}")

def download_file(url:str, local_filename, max_retries=3, timeout=180):
    # 提取目录部分
    directory = os.path.dirname(local_filename)

    retries = 0
    while retries < max_retries:
        try:
            if retries > 0:
                wait_time = 2 ** retries  # 指数退避策略
                print(f"Retrying in {wait_time} seconds... (Attempt {retries+1}/{max_retries})")
                time.sleep(wait_time)
            
            print(f"Downloading file: {local_filename}")
            start_time = time.time()
            
            # 创建目录（如果不存在）
            if directory and not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)
                print(f"Created directory: {directory}")

            with requests.get(url, stream=True, timeout=timeout) as response:
                response.raise_for_status()
                
                total_size = int(response.headers.get('content-length', 0))
                block_size = 1024
                
                with open(local_filename, 'wb') as file:
                    bytes_written = 0
                    for chunk in response.iter_content(block_size):
                        if chunk:
                            file.write(chunk)
                            bytes_written += len(chunk)
                            
                            if total_size > 0:
                                progress = bytes_written / total_size * 100
                                # 对于频繁更新的进度，可以考虑使用logger.debug或更细粒度的控制，避免日志文件过大
                                # 或者只在控制台输出进度，不写入文件
                                print(f"\r[PROGRESS] {progress:.2f}% ({bytes_written/1024:.2f}KB/{total_size/1024:.2f}KB)", end='')
                                pass # 避免在日志文件中打印过多进度信息
                
                if total_size > 0:
                    # print() # 原始的换行符
                    pass
                print(f"Download completed in {time.time()-start_time:.2f} seconds")
                print(f"File saved as: {os.path.abspath(local_filename)}")
                return True
                
        except Timeout:
            print(f"Download timed out after {timeout} seconds")
        except RequestException as e:
            print(f"Request failed: {e}")
        except Exception as e:
            print(f"Unexpected error during download: {e}")
        
        retries += 1
    
    print(f"Download failed after {max_retries} attempts for URL: {url}")
    return False

