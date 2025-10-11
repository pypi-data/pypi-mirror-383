#!/usr/bin/env python3
"""
测试图片生成视频功能
"""

import asyncio
import sys
from pathlib import Path

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent / ".." / "src"))

from pixverse_mcp.client import PixverseClient
from pixverse_mcp.models.requests import ImageToVideoRequest
from pixverse_mcp.models.responses import VideoStatus
from pixverse_mcp.models.common import AspectRatio


async def test_image_to_video():
    """测试图片生成视频功能"""
    print("🎬 Pixverse 图片生成视频测试")
    print("=" * 50)
    
    # 初始化客户端
    client = PixverseClient(
        api_key="sk-xxx",
        base_url="https://app-api.pixverseai.cn"
    )
    
    # 测试图片路径
    image_paths = [
        "/Users/jolsnow/pixverse_platform/猫儿.jpeg",
        "/Users/jolsnow/pixverse_platform/橘猫.jpeg"
    ]
    
    for i, image_path in enumerate(image_paths, 1):
        print(f"\n🐱 测试图片 {i}: {Path(image_path).name}")
        print("-" * 30)
        
        # 检查文件是否存在
        if not Path(image_path).exists():
            print(f"❌ 图片文件不存在: {image_path}")
            continue
            
        try:
            # 第一步：上传图片
            print("📤 正在上传图片...")
            upload_result = await client.upload_image(image_path)
            
            print(f"✅ 图片上传成功!")
            print(f"📋 Image ID: {upload_result.img_id}")
            print(f"🔗 图片URL: {upload_result.img_url}")
            
            # 第二步：使用图片生成视频
            print(f"\n🎬 正在生成视频...")
            
            # 为不同的猫咪使用不同的提示词
            if "猫儿" in image_path:
                prompt = "A cute cat playing in a sunny garden, gentle movements, warm lighting"
            else:
                prompt = "An orange cat stretching and yawning, cozy atmosphere, soft natural light"
            
            print(f"📝 提示词: {prompt}")
            print(f"🔧 模型: v5")
            print(f"⏱️ 时长: 5秒")
            print(f"📺 质量: 540p")
            
            # 创建图片生成视频请求
            request = ImageToVideoRequest(
                prompt=prompt,
                img_id=upload_result.img_id,
                model="v5",
                duration=5,
                quality="540p"
            )
            
            # 提交生成任务
            response = await client.image_to_video(request)
            
            print(f"✅ 视频生成任务提交成功!")
            print(f"📋 Video ID: {response.video_id}")
            
            # 开始轮询状态
            print("🔄 开始查询生成状态...")
            video_id = response.video_id
            max_attempts = 60  # 最多等待10分钟
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
        
        print("\n" + "="*50)


async def main():
    """主函数"""
    await test_image_to_video()


if __name__ == "__main__":
    asyncio.run(main())
