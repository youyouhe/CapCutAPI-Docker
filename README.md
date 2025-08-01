# CapCutAPI

Open source CapCut API tool with MCP (Model Context Protocol) support.

Try It: https://www.capcutapi.top

[中文说明](https://github.com/sun-guannan/CapCutAPI/blob/main/README-zh.md) | [MCP Documentation](./MCP_Documentation_English.md) | [MCP 中文文档](./MCP_文档_中文.md)

## 🎬 Gallery

**Connect AI generated via CapCutAPI**

[![Horse](https://img.youtube.com/vi/IF1RDFGOtEU/hqdefault.jpg)](https://www.youtube.com/watch?v=IF1RDFGOtEU)

[![Song](https://img.youtube.com/vi/rGNLE_slAJ8/hqdefault.jpg)](https://www.youtube.com/watch?v=rGNLE_slAJ8)

## 🚀 Project Features

This project is a Python-based CapCut processing tool that offers comprehensive video editing capabilities through multiple interfaces:

### 🎯 Core Features

- **Draft File Management**: Create, read, modify, and save CapCut draft files
- **Material Processing**: Support adding and editing various materials such as videos, audios, images, texts, stickers, etc.
- **Effect Application**: Support adding multiple effects like transitions, filters, masks, animations, etc.
- **API Service**: Provide HTTP API interfaces to support remote calls and automated processing
- **AI Integration**: Integrate multiple AI services to support intelligent generation of subtitles, texts, and images
- **🆕 MCP Support**: Model Context Protocol integration for seamless AI assistant integration

### 📡 Available Interfaces

#### HTTP API Endpoints
- `/create_draft`: Create a draft
- `/add_video`: Add video material to the draft
- `/add_audio`: Add audio material to the draft
- `/add_image`: Add image material to the draft
- `/add_text`: Add text material to the draft
- `/add_subtitle`: Add subtitles to the draft
- `/add_effect`: Add effects to materials
- `/add_sticker`: Add stickers to the draft
- `/save_draft`: Save the draft file

#### 🆕 MCP Tools (11 Tools Available)
- `create_draft`: Create new video draft project
- `add_video`: Add video track with transitions and effects
- `add_audio`: Add audio track with volume control
- `add_image`: Add image assets with animations
- `add_text`: Add text with shadows, backgrounds, and multi-styles
- `add_subtitle`: Add SRT subtitles with styling
- `add_effect`: Add visual effects
- `add_sticker`: Add sticker elements
- `add_video_keyframe`: Add keyframe animations
- `get_video_duration`: Get video duration
- `save_draft`: Save draft project

## 🛠️ Installation & Setup

### Prerequisites

#### ffmpeg
This project depends on ffmpeg. Ensure ffmpeg is installed and added to your system's PATH.

#### Python Environment
Requires Python 3.8.20 or higher. Ensure the correct Python version is installed.

### Installation Steps

1. **Clone the repository**
```bash
git clone https://github.com/sun-guannan/CapCutAPI.git
cd CapCutAPI
```

2. **Install dependencies**
```bash
# For HTTP API server
pip install -r requirements.txt

# For MCP server (additional)
pip install -r requirements-mcp.txt
```

3. **Configuration**
```bash
cp config.json.example config.json
# Edit config.json as needed
```

## 🚀 Usage

### HTTP API Server

Start the HTTP API server:

```bash
python capcut_server.py
```

### 🆕 MCP Server

The MCP server provides seamless integration with AI assistants and other MCP-compatible clients.

#### Quick Start

1. **Start MCP Server**
```bash
python mcp_server.py
```

2. **Configure MCP Client**
Create or update your `mcp_config.json`:
```json
{
  "mcpServers": {
    "capcut-api": {
      "command": "python3",
      "args": ["mcp_server.py"],
      "cwd": "/path/to/CapCutAPI",
      "env": {
        "PYTHONPATH": "/path/to/CapCutAPI"
      }
    }
  }
}
```

3. **Test MCP Connection**
```bash
python test_mcp_client.py
```

#### MCP Features

- **🎨 Advanced Text Styling**: Multi-color text, shadows, backgrounds
- **🎬 Video Processing**: Keyframe animations, transitions, effects
- **🔊 Audio Control**: Volume adjustment, speed control
- **📱 Multi-format Support**: Various video dimensions and formats
- **⚡ Real-time Processing**: Immediate draft updates and previews

## 📖 Usage Examples

### HTTP API Examples

#### Adding a Video
```python
import requests

response = requests.post("http://localhost:9001/add_video", json={
    "video_url": "http://example.com/video.mp4",
    "start": 0,
    "end": 10,
    "width": 1080,
    "height": 1920
})

print(response.json())
```

#### Adding Text
```python
import requests

response = requests.post("http://localhost:9001/add_text", json={
    "text": "Hello, World!",
    "start": 0,
    "end": 3,
    "font": "ZY_Courage",
    "font_color": "#FF0000",
    "font_size": 30.0
})

print(response.json())
```

#### Saving a Draft
```python
import requests

response = requests.post("http://localhost:9001/save_draft", json={
    "draft_id": "123456",
    "draft_folder": "your capcut draft folder"
})

print(response.json())
```

### 🆕 MCP Usage Examples

#### Basic Workflow
```python
# Create a new draft
draft = mcp_client.call_tool("create_draft", {
    "width": 1080,
    "height": 1920
})

# Add text with advanced styling
mcp_client.call_tool("add_text", {
    "text": "Welcome to CapCut!",
    "start": 0,
    "end": 5,
    "draft_id": draft["draft_id"],
    "font_size": 48,
    "shadow_enabled": True,
    "background_color": "#000000"
})

# Save the project
mcp_client.call_tool("save_draft", {
    "draft_id": draft["draft_id"]
})
```

#### Advanced Features
```python
# Add video with keyframe animation
mcp_client.call_tool("add_video_keyframe", {
    "draft_id": draft_id,
    "track_name": "main_video",
    "property_types": ["scale_x", "scale_y", "alpha"],
    "times": [0, 2, 4],
    "values": ["1.0", "1.5", "0.8"]
})
```

### Testing with REST Client

You can use the `rest_client_test.http` file with REST Client IDE plugins for HTTP testing.

### Draft Management

Calling `save_draft` generates a folder starting with `dfd_` in the server's current directory. Copy this folder to your CapCut draft directory to access the generated draft in CapCut.

## 📚 Documentation

- **[MCP English Documentation](./MCP_Documentation_English.md)**: Complete MCP server usage guide
- **[MCP 中文文档](./MCP_文档_中文.md)**: 完整的 MCP 服务器使用指南
- **[API Reference](./example.py)**: More usage examples including audio and effects

## 🌟 Project Highlights

- **🌍 Cross-platform Support**: Supports both CapCut China version and CapCut International version
- **🤖 Automated Processing**: Supports batch processing and automated workflows
- **🔌 Rich APIs**: Provides comprehensive API interfaces for easy integration
- **⚙️ Flexible Configuration**: Achieve flexible function customization through configuration files
- **🧠 AI Enhancement**: Integrate multiple AI services to improve video production efficiency
- **🆕 MCP Integration**: Seamless integration with AI assistants and automation tools

## 🔧 Advanced Configuration

### MCP Server Configuration

For production use, you can configure the MCP server with additional options:

```json
{
  "mcpServers": {
    "capcut-api": {
      "command": "python3",
      "args": ["mcp_server.py"],
      "cwd": "/path/to/CapCutAPI",
      "env": {
        "PYTHONPATH": "/path/to/CapCutAPI",
        "DEBUG": "1"
      }
    }
  }
}
```

### Environment Variables

- `DEBUG`: Enable debug logging
- `CAPCUT_PATH`: Custom CapCut installation path
- `DRAFT_OUTPUT_PATH`: Custom draft output directory

## 🤝 Contributing

We welcome contributions! Please feel free to submit issues and pull requests.

## 📈 Star History

[![Star History Chart](https://api.star-history.com/svg?repos=sun-guannan/CapCutAPI&type=Date)](https://www.star-history.com/#sun-guannan/CapCutAPI&Date)

## 📄 License

This project is open source. Please check the license file for details.

---

**🎉 New**: Now with MCP support for seamless AI assistant integration! Try the MCP server for advanced video editing automation.
