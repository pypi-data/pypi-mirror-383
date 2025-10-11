#!/usr/bin/env python3
"""
Pixverse SSE服务器 - 集成完整的视频生成功能
"""

import sys
from pathlib import Path

# 添加src路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

import asyncio
import json
import uuid
from datetime import datetime
from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# 导入Pixverse客户端
from pixverse_mcp.client.pixverse import PixverseClient
from pixverse_mcp.models.requests import TextToVideoRequest, ImageToVideoRequest
from pixverse_mcp.models.common import AspectRatio, Duration, ModelVersion, VideoQuality

print("🚀 启动Pixverse SSE服务器...")

# 全局变量存储任务状态和SSE连接
active_tasks: Dict[str, Dict[str, Any]] = {}
sse_connections: Dict[str, asyncio.Queue] = {}

# 创建FastAPI应用
app = FastAPI(
    title="Pixverse SSE Server",
    description="Pixverse视频生成的SSE实时监控服务器",
    version="1.0.0"
)

# 添加CORS支持
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 请求模型
class TextToVideoSSERequest(BaseModel):
    prompt: str
    aspect_ratio: str = "16:9"
    duration: int = 5
    model: str = "v5"  # 默认模型版本
    quality: str = "1080p"  # 默认质量

class ImageToVideoSSERequest(BaseModel):
    image_url: str
    prompt: Optional[str] = None
    aspect_ratio: str = "16:9"
    duration: int = 5
    model: str = "v5"  # 默认模型版本
    quality: str = "1080p"  # 默认质量

class TaskStatusResponse(BaseModel):
    task_id: str
    status: str
    progress: Optional[int] = None
    message: str
    video_url: Optional[str] = None
    error: Optional[str] = None

# 初始化Pixverse客户端
pixverse_client = PixverseClient(
    api_key="sk-xxx",
    base_url="https://app-api.pixverseai.cn"
)

@app.get("/")
async def root():
    return {
        "status": "success",
        "message": "🎬 Pixverse SSE服务器运行正常！",
        "endpoints": {
            "health": "/health",
            "events": "/events/{connection_id}",
            "text_to_video": "/api/text-to-video",
            "image_to_video": "/api/image-to-video",
            "task_status": "/api/task/{task_id}/status",
            "active_tasks": "/api/tasks"
        },
        "usage": {
            "1": "连接SSE: GET /events/{connection_id}",
            "2": "提交任务: POST /api/text-to-video 或 /api/image-to-video",
            "3": "监控进度: 通过SSE实时接收任务状态更新"
        }
    }

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "port": 8080,
        "sse": "enabled",
        "pixverse": "connected",
        "active_tasks": len(active_tasks),
        "sse_connections": len(sse_connections)
    }

@app.get("/api/tasks")
async def get_active_tasks():
    """获取所有活跃任务"""
    return {
        "active_tasks": len(active_tasks),
        "tasks": {
            task_id: {
                "status": task["status"],
                "type": task["type"],
                "created_at": task["created_at"],
                "progress": task.get("progress", 0)
            }
            for task_id, task in active_tasks.items()
        }
    }

@app.get("/api/task/{task_id}/status")
async def get_task_status(task_id: str):
    """获取特定任务状态"""
    if task_id not in active_tasks:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    task = active_tasks[task_id]
    return TaskStatusResponse(
        task_id=task_id,
        status=task["status"],
        progress=task.get("progress"),
        message=task["message"],
        video_url=task.get("video_url"),
        error=task.get("error")
    )

async def send_sse_event(event_type: str, data: Dict[str, Any], task_id: Optional[str] = None):
    """向所有SSE连接发送事件"""
    event = {
        "type": event_type,
        "timestamp": datetime.now().isoformat(),
        "data": data
    }
    
    if task_id:
        event["task_id"] = task_id
    
    # 发送到所有活跃的SSE连接
    disconnected_connections = []
    for connection_id, queue in sse_connections.items():
        try:
            await queue.put(event)
        except Exception as e:
            print(f"❌ SSE连接 {connection_id} 发送失败: {e}")
            disconnected_connections.append(connection_id)
    
    # 清理断开的连接
    for connection_id in disconnected_connections:
        sse_connections.pop(connection_id, None)

async def process_video_generation(task_id: str, task_type: str, request_data: Dict[str, Any]):
    """处理视频生成任务"""
    try:
        # 更新任务状态：开始处理
        active_tasks[task_id]["status"] = "processing"
        active_tasks[task_id]["message"] = "正在提交视频生成任务..."
        active_tasks[task_id]["progress"] = 10
        
        await send_sse_event("task_update", {
            "task_id": task_id,
            "status": "processing",
            "message": "正在提交视频生成任务...",
            "progress": 10
        }, task_id)
        
        # 根据任务类型调用相应的API
        if task_type == "text_to_video":
            print(f"📝 开始文生视频任务 {task_id}: {request_data['prompt']}")
            
            request = TextToVideoRequest(
                prompt=request_data["prompt"],
                aspect_ratio=AspectRatio(request_data["aspect_ratio"]),
                duration=request_data["duration"],
                model=ModelVersion(request_data["model"]),
                quality=VideoQuality(request_data["quality"])
            )
            response = await pixverse_client.text_to_video(request)
            video_id = response.video_id
            
        elif task_type == "image_to_video":
            print(f"🖼️ 开始图生视频任务 {task_id}: {request_data.get('prompt', '无提示词')}")
            
            request = ImageToVideoRequest(
                image_url=request_data["image_url"],
                prompt=request_data.get("prompt"),
                aspect_ratio=AspectRatio(request_data["aspect_ratio"]),
                duration=request_data["duration"],
                model=ModelVersion(request_data["model"]),
                quality=VideoQuality(request_data["quality"])
            )
            response = await pixverse_client.image_to_video(request)
            video_id = response.video_id
        
        else:
            raise ValueError(f"不支持的任务类型: {task_type}")
        
        # 更新任务状态：任务已提交
        active_tasks[task_id]["video_id"] = video_id
        active_tasks[task_id]["status"] = "submitted"
        active_tasks[task_id]["message"] = f"任务已提交，视频ID: {video_id}"
        active_tasks[task_id]["progress"] = 30
        
        await send_sse_event("task_update", {
            "task_id": task_id,
            "status": "submitted",
            "message": f"任务已提交，视频ID: {video_id}",
            "progress": 30,
            "video_id": video_id
        }, task_id)
        
        # 开始轮询视频状态
        print(f"🔄 开始轮询视频状态: {video_id}")
        max_attempts = 60  # 最多轮询5分钟
        attempt = 0
        
        while attempt < max_attempts:
            attempt += 1
            await asyncio.sleep(5)  # 每5秒轮询一次
            
            try:
                status_response = await pixverse_client.get_video_result(video_id)
                status = status_response.status
                
                # 计算进度
                progress = min(30 + (attempt * 2), 90)  # 30-90%的进度
                
                active_tasks[task_id]["status"] = status
                active_tasks[task_id]["progress"] = progress
                
                if status == "completed":
                    # 视频生成完成
                    active_tasks[task_id]["status"] = "completed"
                    active_tasks[task_id]["message"] = "视频生成完成！"
                    active_tasks[task_id]["progress"] = 100
                    active_tasks[task_id]["video_url"] = status_response.video_url
                    
                    await send_sse_event("task_completed", {
                        "task_id": task_id,
                        "status": "completed",
                        "message": "视频生成完成！",
                        "progress": 100,
                        "video_id": video_id,
                        "video_url": status_response.video_url
                    }, task_id)
                    
                    print(f"✅ 任务 {task_id} 完成！视频URL: {status_response.video_url}")
                    break
                    
                elif status == "failed":
                    # 视频生成失败
                    error_msg = f"视频生成失败: {getattr(status_response, 'error', '未知错误')}"
                    active_tasks[task_id]["status"] = "failed"
                    active_tasks[task_id]["message"] = error_msg
                    active_tasks[task_id]["error"] = error_msg
                    
                    await send_sse_event("task_failed", {
                        "task_id": task_id,
                        "status": "failed",
                        "message": error_msg,
                        "error": error_msg
                    }, task_id)
                    
                    print(f"❌ 任务 {task_id} 失败: {error_msg}")
                    break
                    
                else:
                    # 仍在处理中
                    message = f"正在生成视频... (状态: {status}, 轮询: {attempt}/{max_attempts})"
                    active_tasks[task_id]["message"] = message
                    
                    await send_sse_event("task_update", {
                        "task_id": task_id,
                        "status": status,
                        "message": message,
                        "progress": progress,
                        "video_id": video_id
                    }, task_id)
                    
                    print(f"🔄 任务 {task_id} 状态: {status} (轮询 {attempt}/{max_attempts})")
                    
            except Exception as e:
                print(f"❌ 轮询视频状态失败: {e}")
                await asyncio.sleep(5)  # 出错时也等待5秒再重试
        
        # 如果轮询超时
        if attempt >= max_attempts and active_tasks[task_id]["status"] not in ["completed", "failed"]:
            timeout_msg = "视频生成超时，请稍后手动检查状态"
            active_tasks[task_id]["status"] = "timeout"
            active_tasks[task_id]["message"] = timeout_msg
            active_tasks[task_id]["error"] = timeout_msg
            
            await send_sse_event("task_timeout", {
                "task_id": task_id,
                "status": "timeout",
                "message": timeout_msg,
                "error": timeout_msg
            }, task_id)
            
            print(f"⏰ 任务 {task_id} 超时")
    
    except Exception as e:
        error_msg = f"任务处理失败: {str(e)}"
        active_tasks[task_id]["status"] = "failed"
        active_tasks[task_id]["message"] = error_msg
        active_tasks[task_id]["error"] = error_msg
        
        await send_sse_event("task_failed", {
            "task_id": task_id,
            "status": "failed",
            "message": error_msg,
            "error": error_msg
        }, task_id)
        
        print(f"❌ 任务 {task_id} 处理失败: {e}")

@app.post("/api/text-to-video")
async def text_to_video_sse(request: TextToVideoSSERequest, background_tasks: BackgroundTasks):
    """文生视频API"""
    task_id = str(uuid.uuid4())
    
    # 创建任务记录
    active_tasks[task_id] = {
        "type": "text_to_video",
        "status": "created",
        "message": "任务已创建",
        "progress": 0,
        "created_at": datetime.now().isoformat(),
        "request_data": request.model_dump()
    }
    
    # 发送任务创建事件
    await send_sse_event("task_created", {
        "task_id": task_id,
        "type": "text_to_video",
        "status": "created",
        "message": "文生视频任务已创建",
        "prompt": request.prompt
    }, task_id)
    
    # 在后台处理任务
    background_tasks.add_task(
        process_video_generation, 
        task_id, 
        "text_to_video", 
        request.model_dump()
    )
    
    return {
        "task_id": task_id,
        "status": "created",
        "message": "文生视频任务已创建，请通过SSE监控进度"
    }

@app.post("/api/image-to-video")
async def image_to_video_sse(request: ImageToVideoSSERequest, background_tasks: BackgroundTasks):
    """图生视频API"""
    task_id = str(uuid.uuid4())
    
    # 创建任务记录
    active_tasks[task_id] = {
        "type": "image_to_video",
        "status": "created",
        "message": "任务已创建",
        "progress": 0,
        "created_at": datetime.now().isoformat(),
        "request_data": request.model_dump()
    }
    
    # 发送任务创建事件
    await send_sse_event("task_created", {
        "task_id": task_id,
        "type": "image_to_video",
        "status": "created",
        "message": "图生视频任务已创建",
        "image_url": request.image_url,
        "prompt": request.prompt
    }, task_id)
    
    # 在后台处理任务
    background_tasks.add_task(
        process_video_generation, 
        task_id, 
        "image_to_video", 
        request.model_dump()
    )
    
    return {
        "task_id": task_id,
        "status": "created",
        "message": "图生视频任务已创建，请通过SSE监控进度"
    }

@app.get("/events/{connection_id}")
async def stream_events(connection_id: str):
    """SSE事件流端点"""
    
    async def event_generator():
        # 创建连接队列
        queue = asyncio.Queue()
        sse_connections[connection_id] = queue
        
        try:
            # 发送连接成功事件
            welcome_event = {
                "type": "connected",
                "timestamp": datetime.now().isoformat(),
                "data": {
                    "connection_id": connection_id,
                    "message": f"SSE连接已建立 (ID: {connection_id})",
                    "active_tasks": len(active_tasks)
                }
            }
            yield f"data: {json.dumps(welcome_event, ensure_ascii=False)}\n\n"
            
            # 持续监听队列中的事件
            while True:
                try:
                    # 等待事件，超时时间30秒
                    event = await asyncio.wait_for(queue.get(), timeout=30.0)
                    yield f"data: {json.dumps(event, ensure_ascii=False)}\n\n"
                except asyncio.TimeoutError:
                    # 发送心跳事件
                    heartbeat = {
                        "type": "heartbeat",
                        "timestamp": datetime.now().isoformat(),
                        "data": {
                            "connection_id": connection_id,
                            "active_tasks": len(active_tasks)
                        }
                    }
                    yield f"data: {json.dumps(heartbeat, ensure_ascii=False)}\n\n"
                    
        except Exception as e:
            print(f"❌ SSE连接 {connection_id} 错误: {e}")
        finally:
            # 清理连接
            sse_connections.pop(connection_id, None)
            print(f"🔌 SSE连接 {connection_id} 已断开")
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "*",
        }
    )

if __name__ == "__main__":
    print("🎬 Pixverse SSE服务器配置:")
    print(f"   - 端口: 8080")
    print(f"   - API密钥: sk-xxx")
    print(f"   - 基础URL: https://app-api.pixverseai.cn")
    print("\n📝 使用方法:")
    print("   1. 连接SSE: GET /events/{connection_id}")
    print("   2. 提交文生视频: POST /api/text-to-video")
    print("   3. 提交图生视频: POST /api/image-to-video")
    print("   4. 查看任务状态: GET /api/task/{task_id}/status")
    print("\n🌐 访问地址:")
    print("   - 主页: http://127.0.0.1:8080/")
    print("   - 健康检查: http://127.0.0.1:8080/health")
    print("   - SSE监控: examples/sse_monitor.html")
    print("\n🚀 启动服务器...")
    
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8080,
        log_level="info",
        access_log=True
    )
