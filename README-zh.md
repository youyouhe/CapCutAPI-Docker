# 通过CapCutAPI连接AI生成的一切   [🌐 在线体验](https://www.capcutapi.top)

<div align="center">

```
👏👏👏👏 庆祝github 700星，送出价值7000点不记名云渲染券：08B88A2C-1D16-4CE1-982E-E3732F2655F3
```
</div>

## 🎯 项目概览

**CapCutAPI** 是一款强大的云端 API，它赋予您对 AI 生成素材（包括图片、音频、视频和文字）的精确控制权。
它提供了精确的编辑能力来拼接原始的 AI 输出，例如给视频变速或将图片镜像反转。这种能力有效地解决了 AI 生成的结果缺乏精确控制，难以复制的问题，让您能够轻松地将创意想法转化为精致的视频。
所有这些功能均旨在对标剪映软件的功能，确保您在云端也能获得熟悉且高效的剪辑体验。

### 🏆 核心优势

<table>
<tr>
<td width="50%">

**🎬 专业视频编辑**
- 完整的剪映/CapCut 功能支持
- 多轨道时间线编辑
- 高级特效和转场
- 关键帧动画系统

</td>
<td width="50%">

**🤖 AI 智能集成**
- MCP 协议原生支持
- AI 助手无缝对接
- 自动化工作流程
- 批量处理能力

</td>
</tr>
<tr>
<td>

**☁️ 云与本地双模式**
- 支持云端预览与直接生成视频
- 也可导出草稿到本地，能导入剪映或 CapCut 二次编辑
- 灵活选择创作流程

</td>
<td>

**🌍 跨平台兼容**
- 剪映中国版支持
- CapCut 国际版支持
- Windows/macOS 兼容
- 云端部署就绪

</td>
</tr>
</table>

---

## 🎥 产品展示

<div align="center">

## 效果演示
**MCP,创建属于自己的剪辑Agent**

[![AI Cut](https://img.youtube.com/vi/fBqy6WFC78E/hqdefault.jpg)](https://www.youtube.com/watch?v=fBqy6WFC78E)

**通过工具，将AI生成的图片，视频组合起来**

[![Airbnb](https://img.youtube.com/vi/1zmQWt13Dx0/hqdefault.jpg)](https://www.youtube.com/watch?v=1zmQWt13Dx0)

[![Horse](https://img.youtube.com/vi/IF1RDFGOtEU/hqdefault.jpg)](https://www.youtube.com/watch?v=IF1RDFGOtEU)

[![Song](https://img.youtube.com/vi/rGNLE_slAJ8/hqdefault.jpg)](https://www.youtube.com/watch?v=rGNLE_slAJ8)

</div>

---

## 🚀 核心功能

### 📋 功能矩阵

| 功能模块 | HTTP API | MCP 协议 | 描述 |
|---------|----------|----------|------|
| 🎬 **草稿管理** | ✅ | ✅ | 创建、保存剪映/CapCut草稿文件 |
| 🎥 **视频处理** | ✅ | ✅ | 多格式视频导入、剪辑、转场、特效 |
| 🔊 **音频编辑** | ✅ | ✅ | 音频轨道、音量控制、音效处理 |
| 🖼️ **图像处理** | ✅ | ✅ | 图片导入、动画、蒙版、滤镜 |
| 📝 **文本编辑** | ✅ | ✅ | 多样式文本、阴影、背景、动画 |
| 📄 **字幕系统** | ✅ | ✅ | SRT 字幕导入、样式设置、时间同步 |
| ✨ **特效引擎** | ✅ | ✅ | 视觉特效、滤镜、转场动画 |
| 🎭 **贴纸系统** | ✅ | ✅ | 贴纸素材、位置控制、动画效果 |
| 🎯 **关键帧** | ✅ | ✅ | 属性动画、时间轴控制、缓动函数 |
| 📊 **媒体分析** | ✅ | ✅ | 视频时长获取、格式检测 |

### 🛠️ API 接口总览

<details>
<summary><b>📡 HTTP API 端点 (9个接口)</b></summary>
🎬 草稿管理
├── POST /create_draft     # 创建新草稿
└── POST /save_draft       # 保存草稿文件

🎥 媒体素材
├── POST /add_video        # 添加视频素材
├── POST /add_audio        # 添加音频素材
└── POST /add_image        # 添加图片素材

📝 文本内容
├── POST /add_text         # 添加文本元素
└── POST /add_subtitle     # 添加字幕文件

✨ 效果增强
├── POST /add_effect       # 添加视觉特效
└── POST /add_sticker      # 添加贴纸元素

</details>

<details>

<summary><b>🔧 MCP 工具集 (11个工具)</b></summary>

🎬 项目管理
├── create_draft           # 创建视频项目
└── save_draft            # 保存项目文件

🎥 媒体编辑
├── add_video             # 视频轨道 + 转场特效
├── add_audio             # 音频轨道 + 音量控制
└── add_image             # 图片素材 + 动画效果

📝 文本系统
├── add_text              # 多样式文本 + 阴影背景
└── add_subtitle          # SRT字幕 + 样式设置

✨ 高级功能
├── add_effect            # 视觉特效引擎
├── add_sticker           # 贴纸动画系统
├── add_video_keyframe    # 关键帧动画
└── get_video_duration    # 媒体信息获取


</details>

---

## 🛠️ 快速开始

### 📋 系统要求

<table>
<tr>
<td width="30%"><b>🐍 Python 环境</b></td>
<td>Python 3.10+</td>
</tr>
<tr>
<td><b>🎬 剪映应用</b></td>
<td>剪映 或 CapCut 国际版</td>
</tr>
<tr>
<td><b>🎵 FFmpeg</b></td>
<td>用于媒体文件处理和分析</td>
</tr>
<tr>
</tr>
</table>

### ⚡ 一键安装

```bash
# 1. 克隆项目
git clone https://github.com/sun-guannan/CapCutAPI.git
cd CapCutAPI

# 2. 创建虚拟环境 (推荐)
python -m venv venv-capcut
source venv-capcut/bin/activate  # Linux/macOS
# 或 venv-capcut\Scripts\activate  # Windows

# 3. 安装依赖
pip install -r requirements.txt      # HTTP API 基础依赖
pip install -r requirements-mcp.txt  # MCP 协议支持 (可选)

# 4. 配置文件
cp config.json.example config.json
# 根据需要编辑 config.json
```

### 🚀 启动服务

<table>
<tr>
<td width="50%">

**🌐 HTTP API 服务器**
```bash
python capcut_server.py
```
*默认端口: 9001*

</td>
<td width="50%">

**🔧 MCP 协议服务器**
```bash
python mcp_server.py
```
*支持 stdio 通信*

</td>
</tr>
</table>

---

## 🔧 MCP 集成指南

[🔧 MCP 文档](./MCP_文档_中文.md) • [🌍 MCP English Guide](./MCP_Documentation_English.md)

### 📱 客户端配置

创建或更新 `mcp_config.json` 配置文件：

```json
{
  "mcpServers": {
    "capcut-api": {
      "command": "python3",
      "args": ["mcp_server.py"],
      "cwd": "/path/to/CapCutAPI",
      "env": {
        "PYTHONPATH": "/path/to/CapCutAPI",
        "DEBUG": "0"
      }
    }
  }
}
```

### 🧪 连接测试

```bash
# 测试 MCP 连接
python test_mcp_client.py

# 预期输出
✅ MCP 服务器启动成功
✅ 获取到 11 个可用工具
✅ 草稿创建测试通过
```

### 🎯 MCP 特色功能

<div align="center">

| 功能 | 描述 | 示例 |
|------|------|------|
| 🎨 **高级文本样式** | 多色彩、阴影、背景效果 | `shadow_enabled: true` |
| 🎬 **关键帧动画** | 位置、缩放、透明度动画 | `property_types: ["scale_x", "alpha"]` |
| 🔊 **音频精控** | 音量、速度、音效处理 | `volume: 0.8, speed: 1.2` |
| 📱 **多格式支持** | 各种视频尺寸和格式 | `width: 1080, height: 1920` |
| ⚡ **实时处理** | 即时草稿更新和预览 | 毫秒级响应时间 |

</div>

---

## 💡 使用示例

### 🌐 HTTP API 示例
<details>
<summary><b>📹 添加视频素材</b></summary>

```python
import requests

# 添加背景视频
response = requests.post("http://localhost:9001/add_video", json={
    "video_url": "https://example.com/background.mp4",
    "start": 0,
    "end": 10
    "volume": 0.8,
    "transition": "fade_in"
})

print(f"视频添加结果: {response.json()}")
```

</details>

<details>
<summary><b>📝 创建样式文本</b></summary>

```python
import requests

# 添加标题文字
response = requests.post("http://localhost:9001/add_text", json={
    "text": "欢迎使用 CapCutAPI",
    "start": 0,
    "end": 5,
    "font": "思源黑体",
    "font_color": "#FFD700",
    "font_size": 48,
    "shadow_enabled": True,
    "background_color": "#000000"
})

print(f"文本添加结果: {response.json()}")
```

</details>


```
在example.py文件中获取更多示例。
```

### 🔧 MCP 协议示例

<details>
<summary><b>🎯 完整工作流程</b></summary>

```python
# 1. 创建新项目
draft = mcp_client.call_tool("create_draft", {
    "width": 1080,
    "height": 1920
})
draft_id = draft["result"]["draft_id"]

# 2. 添加背景视频
mcp_client.call_tool("add_video", {
    "video_url": "https://example.com/bg.mp4",
    "draft_id": draft_id,
    "start": 0,
    "end": 10,
    "volume": 0.6
})

# 3. 添加标题文字
mcp_client.call_tool("add_text", {
    "text": "AI 驱动的视频制作",
    "draft_id": draft_id,
    "start": 1,
    "end": 6,
    "font_size": 56,
    "shadow_enabled": True,
    "background_color": "#1E1E1E"
})

# 4. 添加关键帧动画
mcp_client.call_tool("add_video_keyframe", {
    "draft_id": draft_id,
    "track_name": "main",
    "property_types": ["scale_x", "scale_y", "alpha"],
    "times": [0, 2, 4],
    "values": ["1.0", "1.2", "0.8"]
})

# 5. 保存项目
result = mcp_client.call_tool("save_draft", {
    "draft_id": draft_id
})

print(f"项目已保存: {result['result']['draft_url']}")
```

</details>

<details>
<summary><b>🎨 高级文本效果</b></summary>

```python
# 多样式彩色文本
mcp_client.call_tool("add_text", {
    "text": "彩色文字效果展示",
    "draft_id": draft_id,
    "start": 2,
    "end": 8,
    "font_size": 42,
    "shadow_enabled": True,
    "shadow_color": "#FFFFFF",
    "background_alpha": 0.8,
    "background_round_radius": 20,
    "text_styles": [
        {"start": 0, "end": 2, "font_color": "#FF6B6B"},
        {"start": 2, "end": 4, "font_color": "#4ECDC4"},
        {"start": 4, "end": 6, "font_color": "#45B7D1"}
    ]
})
```

</details>

### 使用 REST Client 测试

您可以使用 `rest_client_test.http` 文件配合 REST Client IDE 插件进行 HTTP 测试。

### 草稿管理

调用 `save_draft` 会在服务器当前目录下生成一个 `dfd_` 开头的文件夹，将其复制到剪映/CapCut 草稿目录，即可在应用中看到生成的草稿。

---

## 📚 文档中心

<div align="center">

| 📖 文档类型 | 🌍 语言 | 📄 链接 | 📝 描述 |
|------------|---------|---------|----------|
| **MCP 完整指南** | 🇨🇳 中文 | [MCP 中文文档](./MCP_文档_中文.md) | 详细的中文使用说明 |
| **MCP Complete Guide** | 🇺🇸 English | [MCP Documentation](./MCP_Documentation_English.md) | 完整的 MCP 服务器使用指南 |
| **API 参考** | 🇺🇸 English | [example.py](./example.py) | 代码示例和最佳实践 |
| **REST 测试** | 🌐 通用 | [rest_client_test.http](./rest_client_test.http) | HTTP 接口测试用例 |

</div>

---

## 🤝 社区与支持

### 🎯 贡献指南

我们欢迎各种形式的贡献！

```bash
向dev分支提交pr，每周一从dev合并到main分支并发版
```

### 🏆 进群交流

## 进群交流
![交流群](https://github.com/user-attachments/assets/343c0f57-1551-49c1-bec3-c6bbcdbbbf32)

- 反馈问题
- 功能建议
- 最新消息

### 🤝 合作机会

- **出海视频制作**: 想要利用这个API批量制作出海视频吗？我提供免费的咨询服务，帮助你利用这个API制作。相应的，我要将制作的工作流模板放到这个项目中的template目录中**开源**出来。

- **加入我们**: 我们的目标是提供稳定可靠的视频剪辑工具，方便融合AI生成的图片/视频/语音。如果你有兴趣，可以先从将工程里的中文翻译成英文开始！提交pr，我会看到。更深入的，还有MCP剪辑Agent, web剪辑端，云渲染这三个模块代码还没有开源出来。

- **联系方式**:
  - 微信：sguann
  - 抖音：剪映草稿助手

---

## 📈 项目统计

<div align="center">

### ⭐ Star History

[![Star History Chart](https://api.star-history.com/svg?repos=sun-guannan/CapCutAPI&type=Date)](https://www.star-history.com/#sun-guannan/CapCutAPI&Date)

### 📊 项目指标

![GitHub repo size](https://img.shields.io/github/repo-size/sun-guannan/CapCutAPI?style=flat-square)
![GitHub code size](https://img.shields.io/github/languages/code-size/sun-guannan/CapCutAPI?style=flat-square)
![GitHub issues](https://img.shields.io/github/issues/sun-guannan/CapCutAPI?style=flat-square)
![GitHub pull requests](https://img.shields.io/github/issues-pr/sun-guannan/CapCutAPI?style=flat-square)
![GitHub last commit](https://img.shields.io/github/last-commit/sun-guannan/CapCutAPI?style=flat-square)

</div>

---

## 📄 许可证

<div align="center">

本项目采用 Apache 2.0 许可证开源。详情请查看 [LICENSE](LICENSE) 文件。

Apache License 2.0

Copyright (c) 2025 CapCutAPI Contributors

根据 Apache 许可证 2.0 版（"许可证"）获得许可；
除非符合许可证，否则您不得使用此文件。
您可以在以下网址获得许可证副本：

    http://www.apache.org/licenses/LICENSE-2.0

除非适用法律要求或书面同意，否则根据许可证分发的软件
是按"原样"分发的，不附带任何明示或暗示的保证或条件。
请参阅许可证以了解许可证下的特定语言管理权限和
限制。


</div>

---

<div align="center">

## 🎉 立即开始

**现在就体验 CapCutAPI 的强大功能！**

[![立即开始](https://img.shields.io/badge/🚀_立即开始-blue?style=for-the-badge&logo=rocket)](https://www.capcutapi.top)
---

*Made with ❤️ by the CapCutAPI Community*

</div>
