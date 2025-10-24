import uuid
import pyJianYingDraft as draft
import time
from draft_cache import DRAFT_CACHE, update_cache, get_cache, cache_contains, cache_update_access
from util import timestamp_log

def create_draft(width=1080, height=1920):
    """
    Create new CapCut draft
    :param width: Video width, default 1080
    :param height: Video height, default 1920
    :return: (draft_name, draft_path, draft_id, draft_url)
    """
    # Generate timestamp and draft_id
    unix_time = int(time.time())
    unique_id = uuid.uuid4().hex[:8]  # Take the first 8 digits of UUID
    draft_id = f"dfd_cat_{unix_time}_{unique_id}"  # Use Unix timestamp and UUID combination
    
    # Create CapCut draft with specified resolution
    script = draft.Script_file(width, height)
    
    # Store in global cache
    update_cache(draft_id, script)
    
    return script, draft_id

def get_or_create_draft(draft_id=None, width=1080, height=1920):
    """
    Get or create CapCut draft
    :param draft_id: Draft ID, if None or corresponding zip file not found, create new draft
    :param width: Video width, default 1080
    :param height: Video height, default 1920
    :return: (draft_name, draft_path, draft_id, draft_dir, script)
    """
    global DRAFT_CACHE  # Declare use of global variable
    
    if draft_id is not None and cache_contains(draft_id):
        # Get existing draft information from cache
        print(timestamp_log(f"Getting draft from cache: {draft_id}"))
        # Update last access time
        cache_update_access(draft_id)
        return draft_id, get_cache(draft_id)

    # Create new draft logic
    print(timestamp_log("Creating new draft"))
    script, generate_draft_id = create_draft(
        width=width,
        height=height,
    )

    print(timestamp_log(f"About to add draft {generate_draft_id} to cache"))
    # Add the newly created draft to cache
    update_cache(generate_draft_id, script)
    print(timestamp_log(f"Added new draft to cache: {generate_draft_id}"))

    return generate_draft_id, script
    