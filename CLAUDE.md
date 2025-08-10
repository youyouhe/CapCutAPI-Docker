# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

CapCutAPI is a Python-based HTTP API service for programmatically creating and editing CapCut (剪映) draft files. It provides a REST API to add videos, audio, images, text, subtitles, stickers, effects, and keyframes to CapCut projects.

## Development Setup

### Prerequisites
- Python 3.8.20
- ffmpeg (must be installed and in PATH)
- pip dependencies: `pip install -r requirements.txt`

### Configuration
```bash
cp config.json.example config.json
# Edit config.json with your settings
```

### Running the Server
```bash
python capcut_server.py
```

The server runs on port 9000 by default (configurable in config.json).

## API Architecture

### Core Components
- **capcut_server.py**: Main Flask HTTP server with REST endpoints
- **pyJianYingDraft/**: Core library for manipulating CapCut draft files
- **Implementation modules**: Individual modules for specific features
  - add_video_track.py, add_audio_track.py, add_text_impl.py, etc.
- **Utility modules**: Supporting functionality
  - create_draft.py, save_draft_impl.py, util.py, downloader.py

### Key API Endpoints
- POST `/create_draft` - Create new draft
- POST `/add_video` - Add video material
- POST `/add_audio` - Add audio material  
- POST `/add_text` - Add text overlay
- POST `/add_subtitle` - Add subtitle from SRT
- POST `/add_image` - Add image material
- POST `/add_sticker` - Add sticker
- POST `/add_effect` - Add video/audio effects
- POST `/add_video_keyframe` - Add keyframe animations
- POST `/save_draft` - Save draft to CapCut folder
- GET `/get_*_types` - Get available effect/font types
- POST `/query_script` - Query draft script information
- POST `/query_draft_status` - Query draft processing status

### Draft File Structure
Drafts are created as folders starting with `dfd_` containing:
- JSON configuration files (draft_info.json, draft_meta_info.json, etc.)
- Material references and timeline data
- Final saved drafts can be copied to CapCut's draft folder

## Development Commands

### Testing APIs
Use the provided `rest_client_test.http` file with REST Client extension for VS Code, or:

```bash
# Test basic functionality
python example.py

# Individual feature tests (see example.py for all test functions)
python -c "from example import test_text; test_text()"
python -c "from example import test_video_track01; test_video_track01()"
```

### Running Tests
```bash
# Run specific test functions
python -c "from example import test_add_video; test_add_video()"
python -c "from example import test_add_audio; test_add_audio()"
python -c "from example import test_add_text; test_add_text()"
```

### Common Development Tasks
- **Add new material type**: Create `add_<type>_impl.py` and corresponding endpoint in capcut_server.py
- **Add new effects**: Extend metadata in pyJianYingDraft/metadata/
- **Modify draft structure**: Update pyJianYingDraft/draft_folder.py and script_file.py
- **Add new parameters**: Update both the API endpoint and the underlying implementation function

## Key Libraries
- **pyJianYingDraft**: Core CapCut draft manipulation library
- **Flask**: HTTP server
- **requests**: HTTP client for external resources
- **oss2**: Aliyun OSS integration for cloud storage

## Project Structure
```
├── capcut_server.py          # Main HTTP server
├── pyJianYingDraft/          # Core draft manipulation library
│   ├── draft_folder.py       # Draft file management
│   ├── script_file.py        # Timeline/script operations
│   ├── metadata/             # Effect types and constants
│   ├── video_segment.py      # Video track operations
│   ├── audio_segment.py      # Audio track operations
│   └── text_segment.py       # Text/subtitle operations
├── *_impl.py files           # Implementation modules for each feature
├── add_*_track.py files      # Track manipulation modules
├── example.py                # Comprehensive usage examples
├── rest_client_test.http     # HTTP API testing file
├── create_draft.py           # Draft creation and caching
├── save_draft_impl.py        # Draft saving implementation
└── settings/                 # Configuration management
```

## Architecture Overview

### Draft Management
The system uses an in-memory cache (DRAFT_CACHE in draft_cache.py) to store active drafts for performance. The `get_or_create_draft()` function in create_draft.py handles draft retrieval and creation logic.

### Material Processing Pipeline
1. API endpoint receives request with parameters
2. Parameters are validated and passed to implementation function
3. Implementation function calls pyJianYingDraft library to manipulate draft
4. Changes are stored in memory cache
5. Response is returned with draft information

### Key Design Patterns
- **Factory Pattern**: Used in pyJianYingDraft for creating different segment types
- **Strategy Pattern**: Different effect types and animations are handled through enum-based strategies
- **Cache Pattern**: Drafts are cached in memory for performance
- **Modular Architecture**: Each material type has its own implementation module

### Error Handling
- API endpoints return structured JSON responses with success/error status
- Exceptions are caught and converted to user-friendly error messages
- Draft operations validate inputs before processing

### Configuration System
Settings are loaded from config.json and accessed through settings.local module. Key configuration options include:
- IS_CAPCUT_ENV: Whether running in CapCut environment
- PORT: Server port
- DRAFT_DOMAIN/PREVIEW_ROUTER: URL generation for draft previews
- IS_UPLOAD_DRAFT: Whether to upload drafts to cloud storage