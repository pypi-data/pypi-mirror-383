# Pixverse MCP 配置指南

## 📋 概述

本指南将帮助您配置和使用 Pixverse MCP (Model Context Protocol) 服务器，实现与 Cursor IDE 的集成。

## 🚀 快速开始

### 1. 环境准备

确保您的系统已安装：
- Python 3.12+ (当前使用 3.12.10)
- pip
- virtualenv

### 2. 安装依赖

```bash
# 激活虚拟环境
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 3. 配置 API 密钥

复制环境变量模板：
```bash
cp env.example .env
```

### 🎯 **用户最简配置（推荐）**

对于普通用户，只需要配置 API Key：

```bash
# 用户唯一需要配置的环境变量
PIXVERSE_API_KEY=your_actual_api_key_here
```

**说明：** 其他所有配置都有合理的默认值，无需修改。

### 🔧 **MCP程序配置 vs 用户配置**

**配置层级说明：**
- **MCP程序配置** (`config.yaml`) - 包含服务器设置、API端点等
- **用户配置** (`~/.cursor/mcp.json`) - 只需要 API 密钥

**高级用户环境变量覆盖：**
```bash
# 仅在需要覆盖 MCP 程序配置时使用
PIXVERSE_API_KEY=your_api_key_here
PIXVERSE_BASE_URL=https://custom-api-endpoint.com  # 覆盖 config.yaml 中的设置
```

## ⚙️ 配置文件详解

### config.yaml

主要配置文件，包含服务器设置：

```yaml
# Pixverse API 配置
pixverse:
  api_key: "${PIXVERSE_API_KEY}"
  base_url: "${PIXVERSE_BASE_URL}"
  timeout: 30
  max_retries: 3

# MCP 服务器配置
server:
  name: "pixverse-mcp"
  version: "0.1.0"
  
# 日志配置
logging:
  level: "INFO"
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
```

### Cursor MCP 集成

在 `~/.cursor/mcp.json` 中添加 Pixverse MCP 配置：

```json
{
  "mcpServers": {
    "pixverse": {
      "command": "/Users/jolsnow/pixverse_platform/pixverse_mcp/venv/bin/python",
      "args": [
        "/Users/jolsnow/pixverse_platform/pixverse_mcp/run_server.py",
        "--config",
        "/Users/jolsnow/pixverse_platform/pixverse_mcp/config.yaml"
      ],
      "env": {
        "PIXVERSE_API_KEY": "your_api_key_here",
        "PIXVERSE_BASE_URL": "https://app-api.pixverseai.cn"
      }
    }
  }
}
```

## 🛠️ 可用工具

### 视频生成工具

1. **text_to_video** - 文本生成视频
   - 参数：prompt, model, duration, quality, aspect_ratio
   - 支持模型：v1, v2, v3, v3.5, v4, v4.5, v5, visionary

2. **image_to_video** - 图片生成视频
   - 参数：img_id, prompt, model, duration, quality
   - 需要先使用 upload_image 上传图片

3. **transition_video** - 转场视频
   - 参数：first_frame_img, last_frame_img, prompt, duration
   - 创建两张图片间的平滑过渡

4. **extend_video** - 视频延长
   - 参数：source_video_id/video_media_id, prompt, duration
   - 延长现有视频的时长

### 音频和特效工具

5. **lip_sync_video** - 唇语同步
   - 参数：source_video_id, lip_sync_tts_content, lip_sync_tts_speaker_id
   - 为视频添加语音和唇语同步

6. **sound_effect_video** - 音效添加
   - 参数：source_video_id, sound_effect_content
   - 为视频添加背景音效

7. **fusion_video** - 融合视频 (v4.5+)
   - 参数：prompt, image_references
   - 多主体融合视频生成

### 辅助工具

8. **upload_image** - 图片上传
   - 参数：file_path
   - 支持格式：jpg, jpeg, png, webp

9. **upload_video** - 视频上传
   - 参数：file_path
   - 支持格式：mp4, mov, avi, mkv, webm

10. **get_video_status** - 状态查询
    - 参数：video_id
    - 查询视频生成状态和结果

11. **get_tts_speakers** - TTS音色列表
    - 获取可用的语音合成音色

## 🎯 使用示例

### 基础文本生成视频

```python
# 通过 Cursor MCP 调用
prompt = "A beautiful sunset over the ocean with gentle waves"
# 工具会自动处理生成和轮询过程
```

### 图片转视频流程

```python
# 1. 上传图片
upload_image(file_path="/path/to/image.jpg")
# 返回: img_id

# 2. 生成视频
image_to_video(
    img_id=img_id,
    prompt="Make the person in the image wave hello",
    duration=5
)
```

### 唇语同步流程

```python
# 1. 生成或上传源视频
# 2. 获取TTS音色列表
get_tts_speakers()

# 3. 生成唇语同步视频
lip_sync_video(
    source_video_id=video_id,
    lip_sync_tts_content="Hello, this is a test message",
    lip_sync_tts_speaker_id="14"  # 呆萌王小拍
)
```

## 🔧 故障排除

### 常见问题

1. **MCP 服务器红灯**
   - 检查 API 密钥是否正确
   - 确认虚拟环境已激活
   - 查看服务器日志

2. **工具调用失败**
   - 检查参数格式是否正确
   - 确认文件路径存在
   - 验证网络连接

3. **视频生成超时**
   - 视频生成通常需要1-3分钟
   - 复杂场景可能需要更长时间
   - 可以调整轮询间隔

### 日志查看

```bash
# 查看服务器日志
tail -f logs/pixverse_mcp.log

# 手动测试工具
python examples/basic_usage.py
```

## 📚 进阶配置

### 自定义轮询设置

修改 `config.yaml` 中的轮询配置：

```yaml
polling:
  interval_seconds: 2
  timeout_minutes: 3
  max_attempts: 90
```

### 性能优化

1. **并发限制**：避免同时提交过多任务
2. **缓存策略**：重复使用已上传的媒体文件
3. **错误重试**：配置合适的重试次数和间隔

## 🆘 支持

如果遇到问题，请：

1. 查看本配置指南
2. 检查 [README.md](./README.md) 文档
3. 运行测试脚本验证功能
4. 查看项目 Issues

## 📝 更新日志

- v0.1.0: 初始版本，支持基础视频生成功能
- v0.1.1: 添加图片上传和视频延长功能
- v0.1.2: 集成唇语同步和音效功能
- v0.1.3: 添加视频上传和转场功能

---

