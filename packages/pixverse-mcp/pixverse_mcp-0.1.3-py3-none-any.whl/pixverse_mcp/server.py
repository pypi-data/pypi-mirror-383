"""
MCP server implementation for Pixverse video generation.
"""

import asyncio
import json
import os
from typing import Any, Dict, List, Optional, Sequence

from loguru import logger
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    CallToolRequest,
    CallToolResult,
    EmbeddedResource,
    ImageContent,
    ListToolsRequest,
    ListToolsResult,
    TextContent,
    Tool,
    ContentBlock,
)
from pydantic import ValidationError

from .client import PixverseClient
from .exceptions import PixverseError
from .config import get_config, PixverseConfig
from .models.requests import (
    ExtendVideoRequest,
    FusionVideoRequest,
    ImageToVideoRequest,
    LipSyncVideoRequest,
    SoundEffectVideoRequest,
    TextToVideoRequest,
    TransitionVideoRequest,
)


class PixverseMCPServer:
    """MCP Server for Pixverse video generation APIs."""

    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path
        self.config: Optional[PixverseConfig] = None
        self.server = Server("pixverse-mcp")
        self.client: Optional[PixverseClient] = None
        self._setup_handlers()

    def _setup_handlers(self):
        """Setup MCP server handlers."""

        @self.server.list_tools()
        async def handle_list_tools() -> List[Tool]:
            """List available tools."""
            return [
                Tool(
                    name="text_to_video",
                    description="Generate video from text prompt using Pixverse API",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "prompt": {
                                "type": "string",
                                "description": "Text prompt for video generation (max 2048 chars)",
                                "maxLength": 2048,
                            },
                            "model": {
                                "type": "string",
                                "enum": ["v1", "v2", "v3", "v3.5", "v4", "v4.5", "v5", "visionary"],
                                "default": "v5",
                                "description": "Model version to use",
                            },
                            "duration": {
                                "type": "integer",
                                "enum": [5, 8, 10],
                                "default": 5,
                                "description": "Video duration in seconds",
                            },
                            "aspect_ratio": {
                                "type": "string",
                                "enum": ["16:9", "4:3", "1:1", "3:4", "9:16"],
                                "default": "16:9",
                                "description": "Video aspect ratio",
                            },
                            "quality": {
                                "type": "string",
                                "enum": ["360p", "540p", "720p", "1080p"],
                                "default": "540p",
                                "description": "Video quality",
                            },
                            "style": {
                                "type": "string",
                                "enum": ["anime", "3d_animation", "clay", "realistic", "comic", "cyberpunk"],
                                "description": "Video style (optional)",
                            },
                            "negative_prompt": {
                                "type": "string",
                                "description": "Negative prompt (optional)",
                                "maxLength": 2048,
                            },
                            "motion_mode": {
                                "type": "string",
                                "enum": ["normal", "fast"],
                                "default": "normal",
                                "description": "Motion mode",
                            },
                            "camera_movement": {
                                "type": "string",
                                "enum": [
                                    "horizontal_right",
                                    "horizontal_left",
                                    "zoom_in",
                                    "zoom_out",
                                    "vertical_up",
                                    "vertical_down",
                                    "crane_up",
                                    "quickly_zoom_in",
                                    "quickly_zoom_out",
                                    "smooth_zoom_in",
                                    "camera_rotation",
                                    "robo_arm",
                                    "super_dolly_out",
                                    "whip_pan",
                                    "hitchcock",
                                    "left_follow",
                                    "right_follow",
                                    "pan_left",
                                    "pan_right",
                                    "fix_bg",
                                    "default",
                                ],
                                "description": "Camera movement (optional, cannot use with template_id)",
                            },
                            "template_id": {
                                "type": "integer",
                                "description": "Template ID (optional, cannot use with camera_movement)",
                            },
                            "seed": {"type": "integer", "description": "Random seed (optional)"},
                            "sound_effect_switch": {
                                "type": "boolean",
                                "default": False,
                                "description": "Enable sound effects",
                            },
                            "sound_effect_content": {
                                "type": "string",
                                "description": "Sound effect description (optional)",
                                "maxLength": 2048,
                            },
                        },
                        "required": ["prompt"],
                    },
                ),
                Tool(
                    name="image_to_video",
                    description="Generate video from image using Pixverse API",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "prompt": {
                                "type": "string",
                                "description": "Text prompt for video generation (max 2048 chars)",
                                "maxLength": 2048,
                            },
                            "img_id": {"type": "integer", "description": "Image ID for single image"},
                            "img_ids": {
                                "type": "array",
                                "items": {"type": "integer"},
                                "description": "Array of image IDs for multiple images",
                            },
                            "model": {
                                "type": "string",
                                "enum": ["v1", "v2", "v3", "v3.5", "v4", "v4.5", "v5", "visionary"],
                                "default": "v5",
                                "description": "Model version to use",
                            },
                            "duration": {
                                "type": "integer",
                                "enum": [5, 8, 10],
                                "default": 5,
                                "description": "Video duration in seconds",
                            },
                            "quality": {
                                "type": "string",
                                "enum": ["360p", "540p", "720p", "1080p"],
                                "default": "540p",
                                "description": "Video quality",
                            },
                            "style": {
                                "type": "string",
                                "enum": ["anime", "3d_animation", "clay", "realistic", "comic", "cyberpunk"],
                                "description": "Video style (optional)",
                            },
                            "template_id": {"type": "integer", "description": "Template ID (optional)"},
                            "motion_mode": {
                                "type": "string",
                                "enum": ["normal", "fast"],
                                "default": "normal",
                                "description": "Motion mode",
                            },
                            "sound_effect_switch": {
                                "type": "boolean",
                                "default": False,
                                "description": "Enable sound effects",
                            },
                        },
                        "required": ["prompt"],
                    },
                ),
                Tool(
                    name="transition_video",
                    description="Generate transition video between two frames",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "prompt": {
                                "type": "string",
                                "description": "Text prompt for video generation",
                                "maxLength": 2048,
                            },
                            "first_frame_img": {"type": "integer", "description": "First frame image ID"},
                            "last_frame_img": {"type": "integer", "description": "Last frame image ID"},
                            "model": {
                                "type": "string",
                                "enum": ["v3.5", "v4", "v4.5", "v5"],
                                "default": "v5",
                                "description": "Model version (v3.5+)",
                            },
                            "duration": {
                                "type": "integer",
                                "enum": [5, 8],
                                "default": 5,
                                "description": "Video duration in seconds",
                            },
                            "quality": {
                                "type": "string",
                                "enum": ["360p", "540p", "720p", "1080p"],
                                "default": "540p",
                                "description": "Video quality",
                            },
                        },
                        "required": ["prompt", "first_frame_img", "last_frame_img"],
                    },
                ),
                Tool(
                    name="extend_video",
                    description="Extend an existing video",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "prompt": {
                                "type": "string",
                                "description": "Text prompt for video extension",
                                "maxLength": 2048,
                            },
                            "source_video_id": {"type": "integer", "description": "Source video ID (generated video)"},
                            "video_media_id": {"type": "integer", "description": "Video media ID (uploaded video)"},
                            "model": {
                                "type": "string",
                                "enum": ["v3.5", "v4", "v4.5", "v5"],
                                "default": "v5",
                                "description": "Model version (v3.5+)",
                            },
                            "duration": {
                                "type": "integer",
                                "enum": [5, 8],
                                "default": 5,
                                "description": "Video duration in seconds",
                            },
                            "quality": {
                                "type": "string",
                                "enum": ["360p", "540p", "720p", "1080p"],
                                "default": "540p",
                                "description": "Video quality",
                            },
                        },
                        "required": ["prompt"],
                    },
                ),
                Tool(
                    name="lip_sync_video",
                    description="Generate lip sync video",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "source_video_id": {"type": "integer", "description": "Source video ID (generated video)"},
                            "video_media_id": {"type": "integer", "description": "Video media ID (uploaded video)"},
                            "audio_media_id": {"type": "integer", "description": "Audio media ID (uploaded audio)"},
                            "lip_sync_tts_speaker_id": {"type": "string", "description": "TTS speaker ID"},
                            "lip_sync_tts_content": {
                                "type": "string",
                                "description": "TTS content (max 200 chars)",
                                "maxLength": 200,
                            },
                        },
                        "required": [],
                    },
                ),
                Tool(
                    name="sound_effect_video",
                    description="Add sound effects to video",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "sound_effect_content": {
                                "type": "string",
                                "description": "Sound effect description",
                                "maxLength": 2048,
                            },
                            "source_video_id": {"type": "integer", "description": "Source video ID (generated video)"},
                            "video_media_id": {"type": "integer", "description": "Video media ID (uploaded video)"},
                            "original_sound_switch": {
                                "type": "boolean",
                                "default": False,
                                "description": "Keep original sound",
                            },
                        },
                        "required": ["sound_effect_content"],
                    },
                ),
                Tool(
                    name="fusion_video",
                    description="Generate fusion video with multiple subjects (v4.5 only)",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "prompt": {
                                "type": "string",
                                "description": "Text prompt with @ref_name references",
                                "maxLength": 2048,
                            },
                            "image_references": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "type": {"type": "string", "enum": ["subject", "background"]},
                                        "img_id": {"type": "integer"},
                                        "ref_name": {"type": "string", "maxLength": 30},
                                    },
                                    "required": ["type", "img_id", "ref_name"],
                                },
                                "minItems": 1,
                                "maxItems": 3,
                            },
                            "duration": {"type": "integer", "enum": [5, 8], "default": 5},
                            "quality": {"type": "string", "enum": ["360p", "540p", "720p", "1080p"], "default": "540p"},
                            "aspect_ratio": {
                                "type": "string",
                                "enum": ["16:9", "4:3", "1:1", "3:4", "9:16"],
                                "default": "16:9",
                            },
                        },
                        "required": ["prompt", "image_references"],
                    },
                ),
                                Tool(
                    name="upload_image",
                    description="Upload image file or from URL to Pixverse for video generation",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "file_path": {
                                "type": "string",
                                "description": "Path to the local image file to upload (supports jpg, jpeg, png, webp formats)",
                            },
                            "image_url": {
                                "type": "string",
                                "description": "URL of the image to upload (alternative to file_path)",
                            },
                        },
                        "oneOf": [
                            {"required": ["file_path"]},
                            {"required": ["image_url"]}
                        ],
                    },
                ),
                Tool(
                    name="upload_video",
                    description="Upload video file or from URL to Pixverse for video extension or other operations",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "file_path": {
                                "type": "string",
                                "description": "Path to the local video file to upload (supports mp4, mov, avi formats)",
                            },
                            "file_url": {
                                "type": "string",
                                "description": "URL of the video file to upload (alternative to file_path)",
                            },
                        },
                        "oneOf": [
                            {"required": ["file_path"]},
                            {"required": ["file_url"]}
                        ],
                    },
                ),
                Tool(
                    name="get_tts_speakers",
                    description="Get list of available TTS speakers for lip sync",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "page_num": {"type": "integer", "default": 1, "description": "Page number"},
                            "page_size": {"type": "integer", "default": 30, "description": "Page size"},
                        },
                    },
                ),
                Tool(
                    name="get_video_status",
                    description="Get video generation status and result by video ID",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "video_id": {
                                "type": "integer",
                                "description": "Video ID to check status for",
                            },
                        },
                        "required": ["video_id"],
                    },
                ),
            ]

        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: Dict[str, Any]):
            """Handle tool calls - Cursor compatible version."""
            try:
                if not self.client:
                    raise PixverseError("Pixverse client not initialized")

                # Check if this is a video generation tool that should include polling
                video_generation_tools = [
                    "text_to_video", "image_to_video", "transition_video", 
                    "extend_video", "lip_sync_video", "sound_effect_video", "fusion_video"
                ]
                
                if name in video_generation_tools:
                    # Handle video generation with automatic polling
                    if name == "text_to_video":
                        request = TextToVideoRequest(**arguments)
                    elif name == "image_to_video":
                        request = ImageToVideoRequest(**arguments)
                    elif name == "transition_video":
                        request = TransitionVideoRequest(**arguments)
                    elif name == "extend_video":
                        request = ExtendVideoRequest(**arguments)
                    elif name == "lip_sync_video":
                        request = LipSyncVideoRequest(**arguments)
                    elif name == "sound_effect_video":
                        request = SoundEffectVideoRequest(**arguments)
                    elif name == "fusion_video":
                        request = FusionVideoRequest(**arguments)
                    else:
                        raise PixverseError(f"Unsupported video generation tool: {name}")
                    
                    # 分步骤流程：快速提交任务，返回video_id供后续查询
                    if name == "text_to_video":
                        result = await self.client.text_to_video(request)
                    elif name == "image_to_video":
                        result = await self.client.image_to_video(request)
                    elif name == "transition_video":
                        result = await self.client.transition_video(request)
                    elif name == "extend_video":
                        result = await self.client.extend_video(request)
                    elif name == "lip_sync_video":
                        result = await self.client.lip_sync_video(request)
                    elif name == "sound_effect_video":
                        result = await self.client.sound_effect_video(request)
                    elif name == "fusion_video":
                        result = await self.client.fusion_video(request)
                    
                    # 返回提交成功的信息，指导LLM进行自动轮询
                    return {
                        "success": True,
                        "message": f"{name} 任务已提交成功",
                        "video_id": result.video_id,
                        "status": "submitted",
                        "next_step": "请每2秒调用一次 get_video_status 工具查询生成状态，最多轮询2分钟(60次)",
                        "polling_config": {
                            "interval_seconds": 2,
                            "timeout_minutes": 2,
                            "max_attempts": 60
                        },
                        "estimated_time": "预计1-2分钟完成生成",
                        "instruction_for_llm": "请立即开始轮询，每2秒调用一次get_video_status直到状态为completed或超时"
                    }
                
                elif name == "upload_image":
                    # Handle image upload (file or URL)
                    file_path = arguments.get("file_path")
                    image_url = arguments.get("image_url")
                    
                    if not file_path and not image_url:
                        raise PixverseError("Either file_path or image_url is required")
                    
                    if file_path and image_url:
                        raise PixverseError("Only one of file_path or image_url should be provided")
                    
                    if file_path:
                        # Local file upload
                        from pathlib import Path
                        if not Path(file_path).exists():
                            raise PixverseError(f"Image file not found: {file_path}")
                        
                        # Check file format
                        allowed_extensions = {'.jpg', '.jpeg', '.png', '.webp'}
                        file_ext = Path(file_path).suffix.lower()
                        if file_ext not in allowed_extensions:
                            raise PixverseError(f"Unsupported file format: {file_ext}. Supported formats: {', '.join(allowed_extensions)}")
                        
                        # Upload image file
                        result = await self.client.upload_image(file_path=file_path)
                        
                        return {
                            "success": True,
                            "message": "图片文件上传成功",
                            "img_id": result.img_id,
                            "img_url": result.img_url,
                            "file_path": file_path,
                            "file_name": Path(file_path).name,
                            "upload_type": "file",
                            "next_step": "现在可以使用 img_id 调用 image_to_video 工具生成视频"
                        }
                    else:
                        # URL upload
                        import re
                        # Basic URL validation
                        url_pattern = re.compile(
                            r'^https?://'  # http:// or https://
                            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
                            r'localhost|'  # localhost...
                            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
                            r'(?::\d+)?'  # optional port
                            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
                        
                        if not url_pattern.match(image_url):
                            raise PixverseError(f"Invalid image URL format: {image_url}")
                        
                        # Upload image from URL
                        result = await self.client.upload_image(image_url=image_url)
                        
                        return {
                            "success": True,
                            "message": "图片URL上传成功",
                            "img_id": result.img_id,
                            "img_url": result.img_url,
                            "source_url": image_url,
                            "upload_type": "url",
                            "next_step": "现在可以使用 img_id 调用 image_to_video 工具生成视频"
                        }
                
                elif name == "upload_video":
                    # Handle video upload (file or URL)
                    file_path = arguments.get("file_path")
                    file_url = arguments.get("file_url")
                    
                    if not file_path and not file_url:
                        raise PixverseError("Either file_path or file_url is required")
                    
                    if file_path and file_url:
                        raise PixverseError("Only one of file_path or file_url should be provided")
                    
                    if file_path:
                        # Local file upload
                        from pathlib import Path
                        if not Path(file_path).exists():
                            raise PixverseError(f"Video file not found: {file_path}")
                        
                        # Check file format
                        allowed_extensions = {'.mp4', '.mov', '.avi', '.mkv', '.webm'}
                        file_ext = Path(file_path).suffix.lower()
                        if file_ext not in allowed_extensions:
                            raise PixverseError(f"Unsupported file format: {file_ext}. Supported formats: {', '.join(allowed_extensions)}")
                        
                        # Upload video file
                        result = await self.client.upload_media(file_path=file_path, media_type="video")
                        
                        return {
                            "success": True,
                            "message": "视频文件上传成功",
                            "video_media_id": result.media_id,
                            "media_url": result.url,
                            "media_type": result.media_type,
                            "file_path": file_path,
                            "file_name": Path(file_path).name,
                            "file_size": Path(file_path).stat().st_size,
                            "upload_type": "file",
                            "next_step": "现在可以使用 video_media_id 调用 extend_video 工具延长视频"
                        }
                    else:
                        # URL upload
                        import re
                        # Basic URL validation
                        url_pattern = re.compile(
                            r'^https?://'  # http:// or https://
                            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
                            r'localhost|'  # localhost...
                            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
                            r'(?::\d+)?'  # optional port
                            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
                        
                        if not url_pattern.match(file_url):
                            raise PixverseError(f"Invalid video URL format: {file_url}")
                        
                        # Upload video from URL
                        result = await self.client.upload_media(file_url=file_url, media_type="video")
                        
                        return {
                            "success": True,
                            "message": "视频URL上传成功",
                            "video_media_id": result.media_id,
                            "media_url": result.url,
                            "media_type": result.media_type,
                            "source_url": file_url,
                            "upload_type": "url",
                            "next_step": "现在可以使用 video_media_id 调用 extend_video 工具延长视频"
                        }

                elif name == "get_tts_speakers":
                    # Handle TTS speakers request
                    page_num = arguments.get("page_num", 1)
                    page_size = arguments.get("page_size", 30)
                    
                    result = await self.client.get_lip_sync_tts_list(page_num=page_num, page_size=page_size)
                    
                    # Format the result
                    if hasattr(result, "model_dump"):
                        result_dict = result.model_dump()
                    elif hasattr(result, "dict"):
                        result_dict = result.dict()
                    else:
                        result_dict = result
                    
                    # 返回字典格式，避免Cursor客户端的字符串解析bug
                    speakers_data = result_dict.get('data', [])
                    total_speakers = result_dict.get('total', len(speakers_data))
                    
                    return {
                        "success": True,
                        "message": "TTS 语音列表获取成功",
                        "total_speakers": total_speakers,
                        "page": page_num,
                        "page_size": page_size,
                        "speakers": speakers_data,
                        "available_speakers": [
                            {
                                "speaker_id": speaker.get("speaker_id", ""),
                                "name": speaker.get("name", "")
                            } for speaker in speakers_data
                        ],
                        "next_step": "使用 speaker_id 调用 lip_sync_video 工具进行唇语同步"
                    }
                
                elif name == "get_video_status":
                    # Handle video status query
                    video_id = arguments.get("video_id")
                    if not video_id:
                        raise PixverseError("video_id is required")
                    
                    result = await self.client.get_video_result(video_id)
                    
                    # Format the result
                    if hasattr(result, "model_dump"):
                        result_dict = result.model_dump()
                    elif hasattr(result, "dict"):
                        result_dict = result.dict()
                    else:
                        result_dict = result
                    
                    status_text = result.status.value if hasattr(result.status, 'value') else str(result.status)
                    
                    status_message = f"""📹 视频状态查询结果

🆔 视频ID: {video_id}
🔄 状态: {status_text}"""
                    
                    if result.status.value == "completed" if hasattr(result.status, 'value') else str(result.status) == "completed":
                        status_message += f"""
🎉 视频生成成功!
🎬 视频URL: {result.video_url if result.video_url else 'N/A'}"""
                        if result.outputWidth and result.outputHeight:
                            status_message += f"\n📏 分辨率: {result.outputWidth}x{result.outputHeight}"
                        if result.size:
                            status_message += f"\n📦 文件大小: {result.size} bytes"
                        if result.seed:
                            status_message += f"\n🎲 种子: {result.seed}"
                    elif result.status.value == "failed" if hasattr(result.status, 'value') else str(result.status) == "failed":
                        error_msg = result.error_message if hasattr(result, 'error_message') and result.error_message else "未知错误"
                        status_message += f"""
❌ 视频生成失败!
🚫 错误信息: {error_msg}"""
                    elif result.status.value in ["pending", "in_progress"] if hasattr(result.status, 'value') else str(result.status) in ["pending", "in_progress"]:
                        status_message += """
⏳ 视频正在生成中，请稍后再查询..."""
                    
                    # 返回结构化状态信息，包含预估时间和LLM指导
                    base_response = {
                        "success": True,
                        "video_id": video_id,
                        "status": status_text,
                        "message": "视频状态查询成功",
                        "video_url": result.video_url if hasattr(result, 'video_url') and result.video_url else None,
                        "resolution": f"{result.outputWidth}x{result.outputHeight}" if hasattr(result, 'outputWidth') and result.outputWidth else None,
                        "file_size": result.size if hasattr(result, 'size') and result.size else None,
                        "seed": result.seed if hasattr(result, 'seed') and result.seed else None,
                        "error_message": result.error_message if hasattr(result, 'error_message') and result.error_message else None,
                        "data": result_dict
                    }
                    
                    # 根据状态添加不同的指导信息
                    if status_text == "completed":
                        base_response.update({
                            "next_step": "视频生成完成，可以停止轮询",
                            "estimated_time": "已完成",
                            "instruction_for_llm": "视频已生成完成，请展示结果给用户"
                        })
                    elif status_text == "failed":
                        base_response.update({
                            "next_step": "视频生成失败，停止轮询",
                            "estimated_time": "生成失败",
                            "instruction_for_llm": "视频生成失败，请告知用户错误信息"
                        })
                    elif status_text in ["pending", "in_progress"]:
                        base_response.update({
                            "next_step": "继续等待2秒后再次查询状态",
                            "estimated_time": "预计还需30-90秒",
                            "instruction_for_llm": "视频正在生成中，请等待2秒后继续调用get_video_status"
                        })
                    else:
                        base_response.update({
                            "next_step": "继续等待2秒后再次查询状态",
                            "estimated_time": "未知",
                            "instruction_for_llm": "状态未知，请等待2秒后继续查询"
                        })
                    
                    return base_response

                else:
                    raise PixverseError(f"Unknown tool: {name}")

            except Exception as e:
                logger.error(f"Error in handle_call_tool: {e}")
                # 返回结构化错误信息
                return {
                    "success": False,
                    "error": str(e),
                    "message": "工具调用失败",
                    "tool_name": name
                }

    async def _generate_video_with_polling(self, tool_name: str, request_obj, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Generate video and poll for completion status"""
        from .models.responses import VideoStatus
        
        # Submit generation request
        logger.info(f"🚀 提交{tool_name}任务...")
        if tool_name == "text_to_video":
            result = await self.client.text_to_video(request_obj)
        elif tool_name == "image_to_video":
            result = await self.client.image_to_video(request_obj)
        elif tool_name == "transition_video":
            result = await self.client.transition_video(request_obj)
        elif tool_name == "extend_video":
            result = await self.client.extend_video(request_obj)
        elif tool_name == "lip_sync_video":
            result = await self.client.lip_sync_video(request_obj)
        elif tool_name == "sound_effect_video":
            result = await self.client.sound_effect_video(request_obj)
        elif tool_name == "fusion_video":
            result = await self.client.fusion_video(request_obj)
        else:
            raise PixverseError(f"Unsupported tool for polling: {tool_name}")
        
        video_id = result.video_id
        logger.info(f"📹 任务已提交，视频ID: {video_id}")
        
        # Start polling for status
        max_attempts = 20  # 最多等待1分钟 (20 * 3秒)
        attempt = 0
        
        status_updates = [f"✅ {tool_name} 任务已提交"]
        status_updates.append(f"📹 视频ID: {video_id}")
        status_updates.append(f"🔄 开始查询生成状态...")
        
        while attempt < max_attempts:
            attempt += 1
            
            try:
                # Query status
                status_result = await self.client.get_video_result(video_id)
                status_text = status_result.status.value if hasattr(status_result.status, 'value') else str(status_result.status)
                
                status_updates.append(f"[{attempt:2d}/20] 状态: {status_text}")
                
                if status_result.status == VideoStatus.COMPLETED:
                    status_updates.append("🎉 视频生成成功!")
                    if status_result.video_url:
                        status_updates.append(f"🎬 视频URL: {status_result.video_url}")
                    
                    # Return complete result with all details
                    return {
                        "success": True,
                        "status": "completed",
                        "message": "视频生成完成！",
                        "video_id": video_id,
                        "video_url": status_result.video_url,
                        "resolution": f"{status_result.outputWidth}x{status_result.outputHeight}" if hasattr(status_result, 'outputWidth') and status_result.outputWidth else None,
                        "file_size": getattr(status_result, 'size', None),
                        "seed": getattr(status_result, 'seed', None),
                        "style": getattr(status_result, 'style', None),
                        "polling_log": status_updates
                    }
                    
                elif status_result.status == VideoStatus.FAILED:
                    status_updates.append("\n❌ 视频生成失败!")
                    error_msg = getattr(status_result, 'error_message', '未知错误')
                    if error_msg:
                        status_updates.append(f"错误信息: {error_msg}")
                    
                    return {
                        "success": False,
                        "status": "failed",
                        "message": "视频生成失败",
                        "video_id": video_id,
                        "error": error_msg,
                        "polling_log": status_updates
                    }
                    
                elif status_result.status in [VideoStatus.PENDING, VideoStatus.IN_PROGRESS]:
                    status_updates.append("    ⏳ 继续等待...")
                    await asyncio.sleep(3)  # 等待3秒
                else:
                    status_updates.append(f"    ❓ 未知状态: {status_result.status}")
                    await asyncio.sleep(3)
                    
            except Exception as e:
                logger.error(f"查询状态时出错: {e}")
                status_updates.append(f"    ⚠️ 查询状态出错: {str(e)}")
                await asyncio.sleep(3)
        
        # Timeout
        status_updates.append(f"\n⏰ 等待超时，请稍后手动查询结果")
        status_updates.append(f"📋 Video ID: {video_id}")
        
        return {
            "success": False,
            "status": "timeout",
            "message": "等待超时，请稍后手动查询结果",
            "video_id": video_id,
            "polling_log": status_updates
        }

    async def initialize(self, config_path: Optional[str] = None):
        """Initialize the Pixverse client using configuration."""
        try:
            # Load configuration
            self.config = get_config(config_path or self.config_path)
            
            # Initialize client with config
            self.client = PixverseClient(
                api_key=self.config.api_key,
                base_url=self.config.base_url
            )
            
            logger.info(f"Pixverse MCP server initialized with config from: {config_path or self.config_path or 'environment'}")
            
        except Exception as e:
            logger.error(f"Failed to initialize Pixverse MCP server: {e}")
            raise

    async def run(self):
        """Run the MCP server."""
        try:
            # Run the server with stdio streams
            async with stdio_server() as (read_stream, write_stream):
                await self.server.run(
                    read_stream,
                    write_stream,
                    InitializationOptions(
                        server_name="pixverse-mcp",
                        server_version="0.1.0",
                        capabilities=self.server.get_capabilities(
                            notification_options=NotificationOptions(),
                            experimental_capabilities=None,
                        ),
                    ),
                )
        except Exception as e:
            logger.error(f"Error running MCP server: {e}")
            raise


async def main(config_path: Optional[str] = None, mode: str = "stdio"):
    """Main entry point."""
    if mode == "sse":
        # Run SSE server
        logger.info("📡 Starting Pixverse MCP Server in SSE mode")
        try:
            from .sse_server import run_sse_server
            await run_sse_server(port=8080, config_path=config_path)
        except ImportError:
            logger.error("SSE server not available. Please install FastAPI dependencies.")
            raise
    else:
        # Run stdio server (default)
        logger.info("📡 Starting Pixverse MCP Server in STDIO mode")
        server = PixverseMCPServer(config_path=config_path)
        await server.initialize(config_path)
        await server.run()


async def cli_main():
    """CLI entry point with argument parsing."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Pixverse MCP Server")
    parser.add_argument("--config", help="Path to configuration file")
    parser.add_argument("--sse", action="store_true", help="Run SSE server instead of stdio")
    parser.add_argument("--port", type=int, default=8080, help="Port for SSE server")
    
    args = parser.parse_args()
    config_path = args.config
    mode = "sse" if args.sse else "stdio"
    
    await main(config_path=config_path, mode=mode)


if __name__ == "__main__":
    asyncio.run(cli_main())
