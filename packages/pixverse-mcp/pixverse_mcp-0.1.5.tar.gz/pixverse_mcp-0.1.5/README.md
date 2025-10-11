# Pixverse MCP

A Model Context Protocol (MCP) server for Pixverse video generation APIs.

## Features

- **Complete API Coverage**: All 7 Pixverse generation endpoints
- **Type Safety**: Full Pydantic model validation
- **Error Handling**: Comprehensive error handling with retries
- **Rate Limiting**: Built-in rate limiting and throttling
- **Logging**: Structured logging with loguru
- **MCP Integration**: Native MCP server implementation

## Supported Endpoints

1. **Text to Video** (`/openapi/v2/video/text/generate`)
2. **Image to Video** (`/openapi/v2/video/img/generate`)
3. **Transition Video** (`/openapi/v2/video/transition/generate`)
4. **Extend Video** (`/openapi/v2/video/extend/generate`)
5. **Lip Sync Video** (`/openapi/v2/video/lip_sync/generate`)
6. **Sound Effect Video** (`/openapi/v2/video/sound_effect/generate`)
7. **Fusion Video** (`/openapi/v2/video/fusion/generate`)

## Installation

### From Source

```bash
git clone <repository-url>
cd pixverse_mcp
pip install -e .
```

### Development Installation

```bash
pip install -e ".[dev]"
```

## Configuration

### 配置方式

#### 方式1: 配置文件（推荐）

复制并编辑配置文件：
```bash
cp config.yaml my_config.yaml
```

配置文件示例：
```yaml
# API Configuration
api_key: "your_api_key_here"
base_url: "https://app-api.pixverseai.cn"

# Request Configuration
timeout: 30
max_retries: 3
retry_delay: 1.0

# Rate Limiting
rate_limit_requests: 100
rate_limit_window: 60

# Logging
log_level: "INFO"
log_file: null

# MCP Server Configuration
server_name: "pixverse-mcp"
server_version: "1.0.0"
```

#### 方式2: 环境变量

Copy `env.example` to `.env` and configure:

```bash
cp env.example .env
```

Required variables:
- `PIXVERSE_API_KEY`: Your Pixverse API key

Optional variables:
- `PIXVERSE_BASE_URL`: API base URL (default: https://app-api.pixverseai.cn)
- `PIXVERSE_TIMEOUT`: Request timeout in seconds (default: 30)
- `PIXVERSE_MAX_RETRIES`: Max retries for failed requests (default: 3)
- `PIXVERSE_RATE_LIMIT_REQUESTS`: Rate limit per minute (default: 100)
- `PIXVERSE_LOG_LEVEL`: Logging level (default: INFO)

## Usage

### As MCP Server

使用配置文件启动：
```bash
python run_server.py --config my_config.yaml
```

或使用环境变量启动：
```bash
python run_server.py
```

查看帮助：
```bash
python run_server.py --help
```

Or directly:

```bash
python -m pixverse_mcp.server
```

### As Python Library

```python
import asyncio
from pixverse_mcp import PixverseClient
from pixverse_mcp.models import TextToVideoRequest

async def main():
    async with PixverseClient(api_key="your-api-key") as client:
        # Quick text-to-video
        result = await client.quick_text_video(
            prompt="A cat playing piano",
            model="v5",
            duration=5
        )
        print(f"Video ID: {result.video_id}")
        
        # Detailed request
        request = TextToVideoRequest(
            prompt="A beautiful sunset over mountains",
            model="v5",
            duration=5,
            aspect_ratio="16:9",
            quality="540p",
            sound_effect_switch=True
        )
        result = await client.text_to_video(request)
        print(f"Video ID: {result.video_id}")

asyncio.run(main())
```

## MCP Tools

The server provides the following MCP tools:

### text_to_video

Generate video from text prompt.

**Parameters:**
- `prompt` (required): Text description
- `model`: Model version (default: "v5")
- `duration`: Video duration in seconds (5, 8, 10)
- `aspect_ratio`: Video aspect ratio
- `quality`: Video quality
- `style`: Video style (optional)
- `motion_mode`: Motion mode
- `sound_effect_switch`: Enable sound effects

### image_to_video

Generate video from image.

**Parameters:**
- `prompt` (required): Text description
- `img_id` or `img_ids`: Image ID(s)
- `model`: Model version
- `duration`: Video duration
- `quality`: Video quality
- `template_id`: Template ID (optional)

### upload_image

Upload image file and get img_id for video generation.

**Parameters:**
- `file_path` (required): Path to the image file

**Returns:**
- `img_id`: Image ID for use in video generation
- `file_name`: Original file name
- `image_url`: Uploaded image URL

### upload_media

Upload media file (video/audio) and get media_id.

**Parameters:**
- `file_path` (required): Path to the media file
- `media_type`: Type of media ("video" or "audio")

**Returns:**
- `media_id`: Media ID for use in video operations
- `file_name`: Original file name
- `media_type`: Type of uploaded media

### transition_video

Generate transition between two frames.

**Parameters:**
- `prompt` (required): Text description
- `first_frame_img` (required): First frame image ID
- `last_frame_img` (required): Last frame image ID
- `model`: Model version (v3.5+)
- `duration`: Video duration
- `quality`: Video quality

### extend_video

Extend existing video.

**Parameters:**
- `prompt` (required): Extension description
- `source_video_id` or `video_media_id`: Source video
- `model`: Model version
- `duration`: Extension duration
- `quality`: Video quality

### lip_sync_video

Generate lip sync video.

**Parameters:**
- `source_video_id` or `video_media_id`: Source video
- `audio_media_id` or TTS parameters: Audio source

### sound_effect_video

Add sound effects to video.

**Parameters:**
- `sound_effect_content` (required): Sound description
- `source_video_id` or `video_media_id`: Source video
- `original_sound_switch`: Keep original sound

### fusion_video

Generate multi-subject fusion video.

**Parameters:**
- `prompt` (required): Text with @ref_name references
- `image_references` (required): Array of image references
- `duration`: Video duration
- `quality`: Video quality
- `aspect_ratio`: Video aspect ratio

### get_tts_speakers

Get available TTS speakers for lip sync.

**Parameters:**
- `page_num`: Page number (default: 1)
- `page_size`: Page size (default: 30)

## Model Constraints

### V5 Model
- Does not support `motion_mode: "fast"`
- Recommended: `duration: 5`, `quality: "540p"`
- Sound effects enabled by default

### Quality Constraints
- `1080p` does not support `duration > 5`
- `fast` motion mode only supports `duration ≤ 5`

### Parameter Conflicts
- `template_id` and `camera_movement` are mutually exclusive
- `img_id` and `img_ids` are mutually exclusive
- `sound_effect_content` and `sound_mode` are mutually exclusive
- `source_video_id` and `video_media_id` are mutually exclusive

## Error Handling

The client provides comprehensive error handling:

- `PixverseAPIError`: API-level errors
- `PixverseAuthError`: Authentication failures
- `PixverseRateLimitError`: Rate limit exceeded
- `PixverseValidationError`: Request validation errors
- `PixverseTimeoutError`: Request timeouts
- `PixverseConnectionError`: Connection issues

## Development

### Setup

```bash
# Install development dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

### Testing

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=src/pixverse_mcp
```

### Code Quality

```bash
# Format code
black src/ tests/

# Sort imports
isort src/ tests/

# Lint code
flake8 src/ tests/

# Type checking
mypy src/
```

## Popular Templates

| Template ID | Name | Use Case |
|-------------|------|----------|
| 315446315336768 | Kiss Kiss | Romantic scenes |
| 315447659476032 | Kungfu Club | Action scenes |
| 315447659476033 | Earth Zoom | Sci-fi scenes |
| 316826014376384 | General Effects | Universal effects |

## License

MIT License - see LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Run quality checks
6. Submit a pull request

## Support

For issues and questions:
- GitHub Issues: [repository-url]/issues
- Documentation: [docs-url]
