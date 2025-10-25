import os
import re
import pyJianYingDraft as draft
import shutil
from util import zip_draft, is_windows_path, timestamp_log
from oss import upload_to_oss
from typing import Dict, Literal, Any
from draft_cache import DRAFT_CACHE
from create_draft import get_or_create_draft
from save_task_cache import DRAFT_TASKS, get_task_status, update_tasks_cache, update_task_field, increment_task_field, update_task_fields, create_task
from downloader import download_audio, download_file, download_image, download_video
from concurrent.futures import ThreadPoolExecutor, as_completed
import imageio.v2 as imageio
import subprocess
import json
from get_duration_impl import get_video_duration
import uuid
import threading
from collections import OrderedDict
import time
import requests # Import requests for making HTTP calls
import logging
# Import configuration
from settings import IS_CAPCUT_ENV, IS_UPLOAD_DRAFT

# --- Get your Logger instance ---
# The name here must match the logger name you configured in app.py
logger = logging.getLogger('flask_video_generator') 

# Define task status enumeration type
TaskStatus = Literal["initialized", "processing", "completed", "failed", "not_found"]

def build_asset_path(draft_folder: str, draft_id: str, asset_type: str, material_name: str) -> str:
    """
    Build asset file path
    :param draft_folder: Draft folder path
    :param draft_id: Draft ID
    :param asset_type: Asset type (audio, image, video)
    :param material_name: Material name
    :return: Built path
    """
    if is_windows_path(draft_folder):
        if os.name == 'nt': # 'nt' for Windows
            draft_real_path = os.path.join(draft_folder, draft_id, "assets", asset_type, material_name)
        else:
            windows_drive, windows_path = re.match(r'([a-zA-Z]:)(.*)', draft_folder).groups()
            parts = [p for p in windows_path.split('\\') if p]
            draft_real_path = os.path.join(windows_drive, *parts, draft_id, "assets", asset_type, material_name)
            draft_real_path = draft_real_path.replace('/', '\\')
    else:
        draft_real_path = os.path.join(draft_folder, draft_id, "assets", asset_type, material_name)
    return draft_real_path

def save_draft_background(draft_id, draft_folder, task_id):
    """Background save draft to OSS"""
    try:
        print(timestamp_log(f"=== SAVE_DRAFT BACKGROUND DEBUG: Called with draft_id={draft_id} ==="))
        print(timestamp_log(f"SAVE_DRAFT BACKGROUND DEBUG: About to call get_or_create_draft with draft_id={draft_id}"))

        # Get draft information from global cache with thread safety
        # Use get_or_create_draft to ensure consistency and proper caching
        retrieved_draft_id, script = get_or_create_draft(draft_id=draft_id)

        print(timestamp_log(f"SAVE_DRAFT BACKGROUND DEBUG: get_or_create_draft returned draft_id={retrieved_draft_id}, script materials count: {len(script.materials) if hasattr(script, 'materials') and hasattr(script.materials, '__len__') else 'N/A'}"))

        # Check if we got the expected draft or a new one was created
        if retrieved_draft_id != draft_id:
            task_status = {
                "status": "failed",
                "message": f"Draft {draft_id} not found in cache, created new draft {retrieved_draft_id} instead. Cannot save requested draft.",
                "progress": 0,
                "completed_files": 0,
                "total_files": 0,
                "draft_url": ""
            }
            update_tasks_cache(task_id, task_status)  # Use new cache management function
            logger.error(f"CRITICAL ERROR: Requested draft {draft_id} not found, created new draft {retrieved_draft_id} instead. This indicates draft caching issues!")
            return

        logger.info(f"Successfully retrieved draft {retrieved_draft_id} from cache.")

        # Add script-level lock to ensure thread safety
        script_lock = getattr(script, '_script_lock', None)
        if not script_lock:
            script._script_lock = threading.RLock()
            script_lock = script._script_lock

        # Update task status to processing
        task_status = {
            "status": "processing",
            "message": "Preparing draft files",
            "progress": 0,
            "completed_files": 0,
            "total_files": 0,
            "draft_url": ""
        }
        update_tasks_cache(task_id, task_status)  # Use new cache management function
        logger.info(f"Task {task_id} status updated to 'processing': Preparing draft files.")
        
        # Delete possibly existing draft_id folder
        if os.path.exists(retrieved_draft_id):
            logger.warning(f"Deleting existing draft folder (current working directory): {retrieved_draft_id}")
            shutil.rmtree(retrieved_draft_id)

        logger.info(f"Starting to save draft: {retrieved_draft_id}")
        # Save draft
        current_dir = os.path.dirname(os.path.abspath(__file__))
        draft_folder_for_duplicate = draft.Draft_folder(current_dir)
        # Choose different template directory based on configuration
        template_dir = "template" if IS_CAPCUT_ENV else "template_jianying"
        draft_folder_for_duplicate.duplicate_as_template(template_dir, retrieved_draft_id)
        
        # Set correct permissions for the newly created draft folder
        new_draft_path = os.path.join(current_dir, retrieved_draft_id)
        if os.path.exists(new_draft_path):
            os.chmod(new_draft_path, 0o755)
            for root, dirs, files in os.walk(new_draft_path):
                for d in dirs:
                    os.chmod(os.path.join(root, d), 0o755)
                for f in files:
                    os.chmod(os.path.join(root, f), 0o644)
        
        # Update task status
        # Note: update_media_metadata() moved to after download completion
        # to ensure accurate media information from local files
        update_task_field(task_id, "message", "Preparing download tasks")
        update_task_field(task_id, "progress", 5)
        logger.info(f"Task {task_id} progress 5%: Preparing download tasks.")
        
        download_tasks = []

        # Debug: Log material counts
        audios = script.materials.audios
        videos = script.materials.videos
        logger.info(f"DEBUG: Found {len(audios)} audio materials and {len(videos)} video materials")

        # Debug: Log audio material details
        if audios:
            logger.info("DEBUG: Audio materials details:")
            for i, audio in enumerate(audios):
                logger.info(f"  Audio {i+1}: material_id={audio.material_id}, material_name={audio.material_name}, remote_url={audio.remote_url}")

        # Debug: Log video material details
        if videos:
            logger.info("DEBUG: Video materials details:")
            for i, video in enumerate(videos):
                logger.info(f"  Video {i+1}: material_id={video.material_id}, material_name={video.material_name}, remote_url={video.remote_url}")

        if audios:
            for audio in audios:
                remote_url = audio.remote_url
                material_name = audio.material_name
                # Use helper function to build path
                if draft_folder:
                    audio.replace_path = build_asset_path(draft_folder, draft_id, "audio", material_name)
                if not remote_url:
                    logger.warning(f"Audio file {material_name} has no remote_url, skipping download.")
                    continue
                
                # Add audio download task
                download_tasks.append({
                    'type': 'audio',
                    'func': download_file,
                    'args': (remote_url, os.path.join(current_dir, f"{draft_id}/assets/audio/{material_name}")),
                    'material': audio
                })
        
        # Collect video and image download tasks
        videos = script.materials.videos
        if videos:
            for video in videos:
                remote_url = video.remote_url
                material_name = video.material_name
                
                if video.material_type == 'photo':
                    # Use helper function to build path
                    if draft_folder:
                        video.replace_path = build_asset_path(draft_folder, draft_id, "image", material_name)
                    if not remote_url:
                        logger.warning(f"Image file {material_name} has no remote_url, skipping download.")
                        continue
                    
                    # Add image download task
                    download_tasks.append({
                        'type': 'image',
                        'func': download_file,
                        'args': (remote_url, os.path.join(current_dir, f"{draft_id}/assets/image/{material_name}")),
                        'material': video
                    })
                
                elif video.material_type == 'video':
                    # Use helper function to build path
                    if draft_folder:
                        video.replace_path = build_asset_path(draft_folder, draft_id, "video", material_name)
                    if not remote_url:
                        logger.warning(f"Video file {material_name} has no remote_url, skipping download.")
                        continue
                    
                    # Add video download task
                    download_tasks.append({
                        'type': 'video',
                        'func': download_file,
                        'args': (remote_url, os.path.join(current_dir, f"{draft_id}/assets/video/{material_name}")),
                        'material': video
                    })

        update_task_field(task_id, "message", f"Collected {len(download_tasks)} download tasks in total")
        update_task_field(task_id, "progress", 10)
        logger.info(f"Task {task_id} progress 10%: Collected {len(download_tasks)} download tasks in total.")

        # Execute all download tasks concurrently
        downloaded_paths = []
        completed_files = 0
        if download_tasks:
            logger.info(f"Starting concurrent download of {len(download_tasks)} files...")
            
            # Use thread pool for concurrent downloads, maximum concurrency of 16
            with ThreadPoolExecutor(max_workers=16) as executor:
                # Submit all download tasks
                future_to_task = {
                    executor.submit(task['func'], *task['args']): task 
                    for task in download_tasks
                }
                
                # Wait for all tasks to complete
                for future in as_completed(future_to_task):
                    task = future_to_task[future]
                    try:
                        local_path = future.result()
                        downloaded_paths.append(local_path)
                        
                        # Update task status - only update completed files count
                        completed_files += 1
                        update_task_field(task_id, "completed_files", completed_files)
                        task_status = get_task_status(task_id)
                        completed = task_status["completed_files"]
                        total = len(download_tasks)
                        update_task_field(task_id, "total_files", total)
                        # Download part accounts for 60% of the total progress
                        download_progress = 10 + int((completed / total) * 60)
                        update_task_field(task_id, "progress", download_progress)
                        update_task_field(task_id, "message", f"Downloaded {completed}/{total} files")
                        
                        logger.info(f"Task {task_id}: Successfully downloaded {task['type']} file, progress {download_progress}.")
                    except Exception as e:
                        logger.error(f"Task {task_id}: Download {task['type']} file failed: {str(e)}", exc_info=True)
                        # Continue processing other files, don't interrupt the entire process
            
            logger.info(f"Task {task_id}: Concurrent download completed, downloaded {len(downloaded_paths)} files in total.")

        # Update media metadata after all files are downloaded
        # This ensures accurate duration and dimension information from local files
        update_task_field(task_id, "message", "Updating media file metadata")
        update_task_field(task_id, "progress", 65)
        logger.info(f"Task {task_id} progress 65%: Updating media file metadata.")
        update_media_metadata(script, task_id)

        # Update task status - Start saving draft information
        update_task_field(task_id, "progress", 70)
        update_task_field(task_id, "message", "Saving draft information")
        logger.info(f"Task {task_id} progress 70%: Saving draft information.")

        # 确保草稿目录存在
        draft_dir = os.path.join(current_dir, draft_id)
        if not os.path.exists(draft_dir):
            logger.warning(f"Draft directory {draft_dir} does not exist, recreating...")
            # 重新创建目录结构
            draft_folder_for_duplicate = draft.Draft_folder(current_dir)
            template_dir = "template" if IS_CAPCUT_ENV else "template_jianying"
            draft_folder_for_duplicate.duplicate_as_template(template_dir, retrieved_draft_id)
            logger.info(f"Recreated draft directory: {draft_dir}")

        logger.info(f"Acquiring script lock for draft {retrieved_draft_id} before writing draft_info.json")
        with script_lock:
            logger.info(f"Script lock acquired for draft {retrieved_draft_id}, writing draft_info.json")
            script.dump(os.path.join(draft_dir, "draft_info.json"))
            logger.info(f"Draft information has been saved to {os.path.join(current_dir, retrieved_draft_id)}/draft_info.json.")

        draft_url = ""
        # Only upload draft information when IS_UPLOAD_DRAFT is True
        if IS_UPLOAD_DRAFT:
            # Update task status - Start compressing draft
            update_task_field(task_id, "progress", 80)
            update_task_field(task_id, "message", "Compressing draft files")
            logger.info(f"Task {task_id} progress 80%: Compressing draft files.")
            
            # Compress the entire draft directory
            zip_path = zip_draft(draft_id)
            logger.info(f"Draft directory {os.path.join(current_dir, draft_id)} has been compressed to {zip_path}.")
            
            # Update task status - Start uploading to OSS
            update_task_field(task_id, "progress", 90)
            update_task_field(task_id, "message", "Uploading to cloud storage")
            logger.info(f"Task {task_id} progress 90%: Uploading to cloud storage.")
            
            # Upload to OSS
            logger.info(f"Starting upload of {zip_path} to OSS/MinIO")
            draft_url = upload_to_oss(zip_path)
            logger.info(f"Draft archive has been uploaded to OSS, URL: {draft_url}")
            update_task_field(task_id, "draft_url", draft_url)

            # Clean up temporary files
            if os.path.exists(os.path.join(current_dir, draft_id)):
                shutil.rmtree(os.path.join(current_dir, draft_id))
                logger.info(f"Cleaned up temporary draft folder: {os.path.join(current_dir, draft_id)}")

    
        # Update task status - Completed
        update_task_field(task_id, "status", "completed")
        update_task_field(task_id, "progress", 100)
        update_task_field(task_id, "message", "Draft creation completed")
        update_task_field(task_id, "draft_url", draft_url)  # Save draft_url to task status
        logger.info(f"Task {task_id} completed, draft URL: {draft_url}")
        return draft_url

    except Exception as e:
        # Update task status - Failed
        update_task_fields(task_id, 
                          status="failed",
                          message=f"Failed to save draft: {str(e)}")
        logger.error(f"Saving draft {draft_id} task {task_id} failed: {str(e)}", exc_info=True)
        return ""

def query_task_status(task_id: str):
    return get_task_status(task_id)

def save_draft_impl(draft_id: str, draft_folder: str = None) -> Dict[str, str]:
    """Submit save draft task to queue"""
    logger.info(f"Received save draft request: draft_id={draft_id}, draft_folder={draft_folder}")

    # Import request queue
    from request_queue import request_queue

    # Generate task ID
    task_id = draft_id

    # Submit task to queue
    success = request_queue.submit_task(
        task_id=task_id,
        func=_queue_save_draft_wrapper,
        draft_id=draft_id,
        draft_folder=draft_folder
    )

    if success:
        # Create task status for compatibility with existing code
        create_task(task_id)
        logger.info(f"Task {task_id} has been submitted to queue.")

        return {
            "success": True,
            "output": {
                "task_id": task_id,
                "message": "任务已提交到队列，请使用 query_draft_status 查询处理进度",
                "queue_info": request_queue.get_queue_info()
            }
        }
    else:
        # Check if task already exists
        existing_status = request_queue.get_task_status(task_id)
        if existing_status:
            logger.info(f"Task {task_id} already exists in queue")
            return {
                "success": True,
                "output": {
                    "task_id": task_id,
                    "message": "任务已在队列中，请使用 query_draft_status 查询处理进度",
                    "status": existing_status["status"],
                    "queue_info": request_queue.get_queue_info()
                }
            }
        else:
            # Queue is full or other error
            logger.error(f"Failed to submit task {task_id} to queue")
            return {
                "success": False,
                "error": "队列已满，请稍后重试"
            }

def _queue_save_draft_wrapper(draft_id: str, draft_folder: str) -> Dict[str, Any]:
    """
    Queue wrapper for save_draft_background function
    This function is executed by the queue worker threads
    """
    # Create task status for compatibility with existing code
    create_task(draft_id)

    # Call the original save_draft_background function
    draft_url = save_draft_background(draft_id, draft_folder, draft_id)

    # Get the complete task status from the cache system
    task_status = get_task_status(draft_id)

    # Ensure the draft_url is included in the result
    if task_status and isinstance(task_status, dict):
        task_status["draft_url"] = draft_url
        return task_status
    else:
        # Fallback if task status is not available
        return {
            "status": "completed",
            "message": "Draft creation completed",
            "progress": 100,
            "draft_url": draft_url
        }

def get_media_info_with_fallback(remote_url, local_path=None, material_name="", command_func=None):
    """
    Get media information with fallback logic: try remote URL first, then local path
    
    :param remote_url: Remote URL of the media file
    :param local_path: Local file path (optional)
    :param material_name: Name of the material for logging
    :param command_func: Function that takes a file path and returns a command list
    :return: tuple (success, result, error_message)
    """
    # Try remote URL first
    if remote_url:
        try:
            command = command_func(remote_url)
            result = subprocess.check_output(command, stderr=subprocess.STDOUT)
            return True, result, None
        except Exception as e:
            logger.debug(f"Remote URL failed for {material_name}: {str(e)}")
    
    # Try local path if available
    if local_path:
        try:
            command = command_func(local_path)
            result = subprocess.check_output(command, stderr=subprocess.STDOUT)
            return True, result, None
        except Exception as e:
            logger.debug(f"Local path failed for {material_name}: {str(e)}")
    
    # Both failed
    return False, None, f"Both remote and local paths failed for {material_name}"

def get_duration_with_fallback(remote_url, local_path=None, material_name=""):
    """
    Get media duration with fallback logic
    
    :param remote_url: Remote URL of the media file
    :param local_path: Local file path (optional)
    :param material_name: Name of the material for logging
    :return: duration result from get_video_duration
    """
    # Try remote URL first
    if remote_url:
        duration_result = get_video_duration(remote_url)
        if duration_result["success"]:
            return duration_result
        else:
            logger.debug(f"Remote URL duration check failed for {material_name}: {duration_result['error']}")
    
    # Try local path if available
    if local_path:
        duration_result = get_video_duration(local_path)
        if duration_result["success"]:
            return duration_result
        else:
            logger.debug(f"Local path duration check failed for {material_name}: {duration_result['error']}")
    
    # Both failed
    return {"success": False, "error": f"Unable to get duration for {material_name} from both remote and local paths"}

def update_media_metadata(script, task_id=None):
    """
    Update metadata for all media files in the script (duration, width/height, etc.)
    
    :param script: Draft script object
    :param task_id: Optional task ID for updating task status
    :return: None
    """
    # Process audio file metadata
    audios = script.materials.audios
    if not audios:
        logger.info("No audio files found in the draft.")
    else:
        for audio in audios:
            remote_url = audio.remote_url
            material_name = audio.material_name
            if not remote_url:
                logger.warning(f"Warning: Audio file {material_name} has no remote_url, skipped.")
                continue
            
            # Get local path if available
            local_path = audio.replace_path if hasattr(audio, 'replace_path') and audio.replace_path else None
            
            # Check if audio contains video streams using fallback logic
            try:
                def build_video_check_command(path):
                    return [
                        'ffprobe',
                        '-v', 'error',
                        '-select_streams', 'v:0',
                        '-show_entries', 'stream=codec_type',
                        '-of', 'json',
                        path
                    ]
                
                success, video_result, error_msg = get_media_info_with_fallback(
                    remote_url, local_path, material_name, build_video_check_command
                )
                
                if success:
                    video_result_str = video_result.decode('utf-8')
                    # Find JSON start position (first '{')
                    video_json_start = video_result_str.find('{')
                    if video_json_start != -1:
                        video_json_str = video_result_str[video_json_start:]
                        video_info = json.loads(video_json_str)
                        if 'streams' in video_info and len(video_info['streams']) > 0:
                            logger.warning(f"Warning: Audio file {material_name} contains video tracks, skipped its metadata update.")
                            continue
                else:
                    logger.debug(f"Video stream check failed for {material_name}: {error_msg}")
            except Exception as e:
                logger.error(f"Error occurred while checking if audio {material_name} contains video streams: {str(e)}", exc_info=True)

            # Get audio duration and set it using fallback logic
            try:
                duration_result = get_duration_with_fallback(remote_url, local_path, material_name)
                if duration_result["success"]:
                    if task_id:
                        update_task_field(task_id, "message", f"Processing audio metadata: {material_name}")
                    # Convert seconds to microseconds
                    audio.duration = int(duration_result["output"] * 1000000)
                    logger.info(f"Successfully obtained audio {material_name} duration: {duration_result['output']:.2f} seconds ({audio.duration} microseconds).")
                    
                    # Update timerange for all segments using this audio material
                    for track_name, track in script.tracks.items():
                        if track.track_type == draft.Track_type.audio:
                            for segment in track.segments:
                                if isinstance(segment, draft.Audio_segment) and segment.material_id == audio.material_id:
                                    # Get current settings
                                    current_target = segment.target_timerange
                                    current_source = segment.source_timerange
                                    speed = segment.speed.speed
                                    
                                    # If the end time of source_timerange exceeds the new audio duration, adjust it
                                    if current_source.end > audio.duration or current_source.end <= 0:
                                        # Adjust source_timerange to fit the new audio duration
                                        new_source_duration = audio.duration - current_source.start
                                        if new_source_duration <= 0:
                                            logger.warning(f"Warning: Audio segment {segment.segment_id} start time {current_source.start} exceeds audio duration {audio.duration}, will skip this segment.")
                                            continue
                                            
                                        # Update source_timerange
                                        segment.source_timerange = draft.Timerange(current_source.start, new_source_duration)
                                        
                                        # Update target_timerange based on new source_timerange and speed
                                        new_target_duration = int(new_source_duration / speed)
                                        segment.target_timerange = draft.Timerange(current_target.start, new_target_duration)
                                        
                                        logger.info(f"Adjusted audio segment {segment.segment_id} timerange to fit the new audio duration.")
                else:
                    logger.warning(f"Warning: Unable to get audio {material_name} duration: {duration_result['error']}.")
            except Exception as e:
                logger.error(f"Error occurred while getting audio {material_name} duration: {str(e)}", exc_info=True)
    
    # Process video and image file metadata
    videos = script.materials.videos
    if not videos:
        logger.info("No video or image files found in the draft.")
    else:
        for video in videos:
            remote_url = video.remote_url
            material_name = video.material_name
            if not remote_url:
                logger.warning(f"Warning: Media file {material_name} has no remote_url, skipped.")
                continue
            
            # Get local path if available
            local_path = video.replace_path if hasattr(video, 'replace_path') and video.replace_path else None
                
            if video.material_type == 'photo':
                # Use imageio to get image width/height and set it with fallback logic
                try:
                    if task_id:
                        update_task_field(task_id, "message", f"Processing image metadata: {material_name}")
                    
                    # Try remote URL first, then local path
                    img = None
                    if remote_url:
                        try:
                            img = imageio.imread(remote_url)
                            logger.info(f"Successfully read image {material_name} from remote URL.")
                        except Exception as e:
                            logger.debug(f"Failed to read image {material_name} from remote URL: {str(e)}")
                    
                    if img is None and local_path:
                        try:
                            img = imageio.imread(local_path)
                            logger.info(f"Successfully read image {material_name} from local path.")
                        except Exception as e:
                            logger.debug(f"Failed to read image {material_name} from local path: {str(e)}")
                    
                    if img is not None:
                        video.height, video.width = img.shape[:2]
                        logger.info(f"Successfully set image {material_name} dimensions: {video.width}x{video.height}.")
                    else:
                        raise Exception("Both remote and local image reading failed")
                        
                except Exception as e:
                    logger.error(f"Failed to set image {material_name} dimensions: {str(e)}, using default values 1920x1080.", exc_info=True)
                    video.width = 1920
                    video.height = 1080
            
            elif video.material_type == 'video':
                # Get video duration and width/height information using fallback logic
                try:
                    if task_id:
                        update_task_field(task_id, "message", f"Processing video metadata: {material_name}")
                    
                    # Build ffprobe command for video info
                    def build_video_info_command(path):
                        return [
                            'ffprobe',
                            '-v', 'error',
                            '-select_streams', 'v:0',  # Select the first video stream
                            '-show_entries', 'stream=width,height,duration',
                            '-show_entries', 'format=duration',
                            '-of', 'json',
                            path
                        ]
                    
                    success, result, error_msg = get_media_info_with_fallback(
                        remote_url, local_path, material_name, build_video_info_command
                    )
                    
                    if not success:
                        raise Exception(error_msg)
                    result_str = result.decode('utf-8')
                    # Find JSON start position (first '{')
                    json_start = result_str.find('{')
                    if json_start != -1:
                        json_str = result_str[json_start:]
                        info = json.loads(json_str)
                        
                        if 'streams' in info and len(info['streams']) > 0:
                            stream = info['streams'][0]
                            # Set width and height
                            video.width = int(stream.get('width', 0))
                            video.height = int(stream.get('height', 0))
                            logger.info(f"Successfully set video {material_name} dimensions: {video.width}x{video.height}.")
                            
                            # Set duration
                            # Prefer stream duration, if not available use format duration
                            duration = stream.get('duration') or info['format'].get('duration', '0')
                            video.duration = int(float(duration) * 1000000)  # Convert to microseconds
                            logger.info(f"Successfully obtained video {material_name} duration: {float(duration):.2f} seconds ({video.duration} microseconds).")
                            
                            # Update timerange for all segments using this video material
                            for track_name, track in script.tracks.items():
                                if track.track_type == draft.Track_type.video:
                                    for segment in track.segments:
                                        if isinstance(segment, draft.Video_segment) and segment.material_id == video.material_id:
                                            # Get current settings
                                            current_target = segment.target_timerange
                                            current_source = segment.source_timerange
                                            speed = segment.speed.speed

                                            # If the end time of source_timerange exceeds the new video duration, adjust it
                                            if current_source.end > video.duration or current_source.end <= 0:
                                                # Adjust source_timerange to fit the new video duration
                                                new_source_duration = video.duration - current_source.start
                                                if new_source_duration <= 0:
                                                    logger.warning(f"Warning: Video segment {segment.segment_id} start time {current_source.start} exceeds video duration {video.duration}, will skip this segment.")
                                                    continue
                                                    
                                                # Update source_timerange
                                                segment.source_timerange = draft.Timerange(current_source.start, new_source_duration)
                                                
                                                # Update target_timerange based on new source_timerange and speed
                                                new_target_duration = int(new_source_duration / speed)
                                                segment.target_timerange = draft.Timerange(current_target.start, new_target_duration)
                                                
                                                logger.info(f"Adjusted video segment {segment.segment_id} timerange to fit the new video duration.")
                        else:
                            logger.warning(f"Warning: Unable to get video {material_name} stream information.")
                            # Set default values
                            video.width = 1920
                            video.height = 1080
                    else:
                        logger.warning(f"Warning: Could not find JSON data in ffprobe output.")
                        # Set default values
                        video.width = 1920
                        video.height = 1080
                except Exception as e:
                    logger.error(f"Error occurred while getting video {material_name} information: {str(e)}, using default values 1920x1080.", exc_info=True)
                    # Set default values
                    video.width = 1920
                    video.height = 1080
                    
                    # Try to get duration separately using fallback logic
                    try:
                        duration_result = get_duration_with_fallback(remote_url, local_path, material_name)
                        if duration_result["success"]:
                            # Convert seconds to microseconds
                            video.duration = int(duration_result["output"] * 1000000)
                            logger.info(f"Successfully obtained video {material_name} duration: {duration_result['output']:.2f} seconds ({video.duration} microseconds).")
                        else:
                            logger.warning(f"Warning: Unable to get video {material_name} duration: {duration_result['error']}.")
                    except Exception as e2:
                        logger.error(f"Error occurred while getting video {material_name} duration: {str(e2)}.", exc_info=True)

    # After updating all segments' timerange, check if there are time range conflicts in each track, and delete the later segment in case of conflict
    logger.info("Checking track segment time range conflicts...")
    for track_name, track in script.tracks.items():
        # Use a set to record segment indices that need to be deleted
        to_remove = set()
        
        # Check for conflicts between all segments
        for i in range(len(track.segments)):
            # Skip if current segment is already marked for deletion
            if i in to_remove:
                continue
                
            for j in range(len(track.segments)):
                # Skip self-comparison and segments already marked for deletion
                if i == j or j in to_remove:
                    continue
                    
                # Check if there is a conflict
                if track.segments[i].overlaps(track.segments[j]):
                    # Always keep the segment with the smaller index (added first)
                    later_index = max(i, j)
                    logger.warning(f"Time range conflict between segments {track.segments[min(i, j)].segment_id} and {track.segments[later_index].segment_id} in track {track_name}, deleting the later segment")
                    to_remove.add(later_index)
        
        # Delete marked segments from back to front to avoid index change issues
        for index in sorted(to_remove, reverse=True):
            track.segments.pop(index)

    # After updating all segments' timerange, recalculate the total duration of the script
    max_duration = 0
    for track_name, track in script.tracks.items():
        for segment in track.segments:
            max_duration = max(max_duration, segment.end)
    script.duration = max_duration
    logger.info(f"Updated script total duration to: {script.duration} microseconds.")
    
    # Process all pending keyframes in tracks
    logger.info("Processing pending keyframes...")
    for track_name, track in script.tracks.items():
        if hasattr(track, 'pending_keyframes') and track.pending_keyframes:
            logger.info(f"Processing {len(track.pending_keyframes)} pending keyframes in track {track_name}...")
            track.process_pending_keyframes()
            logger.info(f"Pending keyframes in track {track_name} have been processed.")

def query_script_impl(draft_id: str, force_update: bool = True):
    """
    Query draft script object, with option to force refresh media metadata

    :param draft_id: Draft ID
    :param force_update: Whether to force refresh media metadata, default is True
    :return: Script object
    """
    # Get draft information from global cache with thread safety
    try:
        retrieved_draft_id, script = get_or_create_draft(draft_id=draft_id)
        if retrieved_draft_id != draft_id:
            logger.warning(f"Requested draft {draft_id} not found, created new draft {retrieved_draft_id}")
            return None
        logger.info(f"Retrieved draft {draft_id} from cache.")
    except Exception as e:
        logger.error(f"Failed to retrieve draft {draft_id} from cache: {str(e)}")
        return None
    
    # If force_update is True, force refresh media metadata
    if force_update:
        logger.info(f"Force refreshing media metadata for draft {draft_id}.")
        update_media_metadata(script)
    
    # Return script object
    return script

def download_script(draft_id: str, draft_folder: str = None, script_data: Dict = None) -> Dict[str, str]:
    """Downloads the draft script and its associated media assets.

    This function fetches the script object from a remote API,
    then iterates through its materials (audios, videos, images)
    to download them to the specified draft folder. It also updates
    task status and progress throughout the process.

    :param draft_id: The ID of the draft to download.
    :param draft_folder: The base folder where the draft's assets will be stored.
                         If None, assets will be stored directly under a folder named
                         after the draft_id in the current working directory.
    :return: A dictionary indicating success and, if successful, the URL where the draft
             would eventually be saved (though this function primarily focuses on download).
             If failed, it returns an error message.
    """

    logger.info(f"Starting to download draft: {draft_id} to folder: {draft_folder}")
    # Copy template to target directory
    template_path = os.path.join("./", 'template') if IS_CAPCUT_ENV else os.path.join("./", 'template_jianying')
    new_draft_path = os.path.join(draft_folder, draft_id)
    if os.path.exists(new_draft_path):
        logger.warning(f"Deleting existing draft target folder: {new_draft_path}")
        shutil.rmtree(new_draft_path)

    # Copy draft folder
    shutil.copytree(template_path, new_draft_path)
    
    try:
        # 1. Fetch the script from the remote endpoint
        if script_data is None:
            query_url = "https://cut-jianying-vdvswivepm.cn-hongkong.fcapp.run/query_script"
            headers = {"Content-Type": "application/json"}
            payload = {"draft_id": draft_id}

            logger.info(f"Attempting to get script for draft ID: {draft_id} from {query_url}.")
            response = requests.post(query_url, headers=headers, json=payload)
            response.raise_for_status()  # Raise an exception for HTTP errors (4xx or 5xx)
            
            script_data = json.loads(response.json().get('output'))
            logger.info(f"Successfully retrieved script data for draft {draft_id}.")
        else:
            logger.info(f"Using provided script_data, skipping remote retrieval.")

        # Collect download tasks
        download_tasks = []
        
        # Collect audio download tasks
        audios = script_data.get('materials',{}).get('audios',[])
        if audios:
            for audio in audios:
                remote_url = audio['remote_url']
                material_name = audio['name']
                # Use helper function to build path
                if draft_folder:
                    audio['path']=build_asset_path(draft_folder, draft_id, "audio", material_name)
                    logger.debug(f"Local path for audio {material_name}: {audio['path']}")
                if not remote_url:
                    logger.warning(f"Audio file {material_name} has no remote_url, skipping download.")
                    continue
                
                # Add audio download task
                download_tasks.append({
                    'type': 'audio',
                    'func': download_file,
                    'args': (remote_url, audio['path']),
                    'material': audio
                })
        
        # Collect video and image download tasks
        videos = script_data['materials']['videos']
        if videos:
            for video in videos:
                remote_url = video['remote_url']
                material_name = video['material_name']
                
                if video['type'] == 'photo':
                    # Use helper function to build path
                    if draft_folder:
                        video['path'] = build_asset_path(draft_folder, draft_id, "image", material_name)
                    if not remote_url:
                        logger.warning(f"Image file {material_name} has no remote_url, skipping download.")
                        continue
                    
                    # Add image download task
                    download_tasks.append({
                        'type': 'image',
                        'func': download_file,
                        'args': (remote_url, video['path']),
                        'material': video
                    })
                
                elif video['type'] == 'video':
                    # Use helper function to build path
                    if draft_folder:
                        video['path'] = build_asset_path(draft_folder, draft_id, "video", material_name)
                    if not remote_url:
                        logger.warning(f"Video file {material_name} has no remote_url, skipping download.")
                        continue
                    
                    # Add video download task
                    download_tasks.append({
                        'type': 'video',
                        'func': download_file,
                        'args': (remote_url, video['path']),
                        'material': video
                    })

        # Execute all download tasks concurrently
        downloaded_paths = []
        completed_files = 0
        if download_tasks:
            logger.info(f"Starting concurrent download of {len(download_tasks)} files...")
            
            # Use thread pool for concurrent downloads, maximum concurrency of 16
            with ThreadPoolExecutor(max_workers=16) as executor:
                # Submit all download tasks
                future_to_task = {
                    executor.submit(task['func'], *task['args']): task 
                    for task in download_tasks
                }
                
                # Wait for all tasks to complete
                for future in as_completed(future_to_task):
                    task = future_to_task[future]
                    try:
                        local_path = future.result()
                        downloaded_paths.append(local_path)
                        
                        # Update task status - only update completed files count
                        completed_files += 1
                        logger.info(f"Downloaded {completed_files}/{len(download_tasks)} files.")
                    except Exception as e:
                        logger.error(f"Failed to download {task['type']} file {task['args'][0]}: {str(e)}", exc_info=True)
                        logger.error("Download failed.")
                        # Continue processing other files, don't interrupt the entire process
            
            logger.info(f"Concurrent download completed, downloaded {len(downloaded_paths)} files in total.")
        
        """Write draft file content to file"""
        with open(f"{draft_folder}/{draft_id}/draft_info.json", "w", encoding="utf-8") as f:
            f.write(json.dumps(script_data))
        logger.info(f"Draft has been saved.")

        # No draft_url for download, but return success
        return {"success": True, "message": f"Draft {draft_id} and its assets downloaded successfully"}

    except requests.exceptions.RequestException as e:
        logger.error(f"API request failed: {e}", exc_info=True)
        return {"success": False, "error": f"Failed to fetch script from API: {str(e)}"}
    except Exception as e:
        logger.error(f"Unexpected error during download: {e}", exc_info=True)
        return {"success": False, "error": f"An unexpected error occurred: {str(e)}"}

if __name__ == "__main__":
    print('hello')
    download_script("dfd_cat_1751012163_a7e8c315",'/Users/sunguannan/Movies/JianyingPro/User Data/Projects/com.lveditor.draft')