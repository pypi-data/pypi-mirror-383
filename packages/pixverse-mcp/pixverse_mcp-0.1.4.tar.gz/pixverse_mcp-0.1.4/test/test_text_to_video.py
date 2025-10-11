#!/usr/bin/env python3
"""
测试Pixverse文生视频功能
"""

import asyncio
import sys
import os
from pathlib import Path

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent / ".." / "src"))

from pixverse_mcp.client import PixverseClient
from pixverse_mcp.models.requests import TextToVideoRequest
from pixverse_mcp.models.responses import VideoStatus
from pixverse_mcp.models.common import AspectRatio


async def test_text_to_video():
    """测试文生视频功能"""
    print("🎬 Pixverse 文生视频测试")
    print("=" * 50)
    
    # 初始化客户端
    client = PixverseClient(
        api_key="sk-xxx",
        base_url="https://app-api.pixverseai.cn"
    )
    
    try:
        # 测试提示词
        prompt = "A beautiful sunset over the ocean with gentle waves, cinematic lighting, 4K quality"
        
        print(f"📝 提示词: {prompt}")
        print(f"🔧 模型: v5")
        print(f"⏱️ 时长: 5秒")
        print(f"📺 质量: 540p")
        print()
        
        # 创建请求
        request = TextToVideoRequest(
            prompt=prompt,
            model="v5",
            duration=5,
            aspect_ratio=AspectRatio.RATIO_16_9,
            quality="540p"
        )
        
        print("🚀 正在提交视频生成任务...")
        
        # 提交生成任务
        response = await client.text_to_video(request)
        
        print(f"✅ 任务提交成功!")
        print(f"📋 Video ID: {response.video_id}")
        print()
        
        # 开始轮询状态
        print("🔄 开始查询生成状态...")
        video_id = response.video_id
        max_attempts = 60  # 最多等待10分钟 (60 * 10秒)
        attempt = 0
        
        while attempt < max_attempts:
            attempt += 1
            
            # 查询状态
            result = await client.get_video_result(video_id)
            
            print(f"[{attempt:2d}/60] 状态: {result.status.value if hasattr(result.status, 'value') else result.status}")
            
            if result.status == VideoStatus.COMPLETED:
                print()
                print("🎉 视频生成成功!")
                print(f"🎬 视频URL: {result.video_url}")
                if result.outputWidth and result.outputHeight:
                    print(f"📏 分辨率: {result.outputWidth}x{result.outputHeight}")
                if result.size:
                    print(f"📦 文件大小: {result.size} bytes")
                if result.seed:
                    print(f"🎲 种子: {result.seed}")
                if result.style:
                    print(f"🎨 风格: {result.style}")
                if result.has_audio:
                    print(f"🔊 音频: {'有' if result.has_audio else '无'}")
                break
            elif result.status == VideoStatus.FAILED:
                print()
                print("❌ 视频生成失败!")
                if hasattr(result, 'error_message') and result.error_message:
                    print(f"错误信息: {result.error_message}")
                break
            elif result.status in [VideoStatus.PENDING, VideoStatus.IN_PROGRESS]:
                print("    ⏳ 继续等待...")
                await asyncio.sleep(10)  # 等待10秒
            else:
                print(f"    ❓ 未知状态: {result.status}")
                await asyncio.sleep(10)
        
        if attempt >= max_attempts:
            print()
            print("⏰ 等待超时，请稍后手动查询结果")
            print(f"📋 Video ID: {video_id}")
            
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()


async def main():
    """主函数"""
    await test_text_to_video()


if __name__ == "__main__":
    asyncio.run(main())
