#!/usr/bin/env python3
"""
Pixverse Upload Example
演示如何使用上传功能和完整的工作流程
"""

import asyncio
import os
from pathlib import Path

from pixverse_mcp.client import PixverseClient
from pixverse_mcp.models.requests import ImageToVideoRequest


async def upload_image_example():
    """演示图片上传功能"""
    print("🖼️ 图片上传示例")
    print("=" * 50)
    
    # 初始化客户端
    client = PixverseClient(
        api_key=os.getenv("PIXVERSE_API_KEY", "355649246276410/sk-xxx"),
        base_url="https://app-api.pixverseai.cn"
    )
    
    try:
        # 上传图片
        image_path = "path/to/your/image.jpg"  # 替换为实际图片路径
        
        if not Path(image_path).exists():
            print(f"❌ 图片文件不存在: {image_path}")
            print("💡 请将 image_path 替换为实际的图片路径")
            return
        
        print(f"📤 正在上传图片: {image_path}")
        upload_result = await client.upload_image(image_path)
        
        print(f"✅ 图片上传成功!")
        print(f"   📋 img_id: {upload_result.img_id}")
        print(f"   📁 文件名: {upload_result.file_name}")
        print(f"   📏 文件大小: {upload_result.file_size} bytes")
        print(f"   🔗 图片URL: {upload_result.image_url}")
        
        return upload_result.img_id
        
    except Exception as e:
        print(f"❌ 上传失败: {e}")
    finally:
        await client.close()


async def upload_media_example():
    """演示媒体文件上传功能"""
    print("\n🎬 媒体文件上传示例")
    print("=" * 50)
    
    client = PixverseClient(
        api_key=os.getenv("PIXVERSE_API_KEY", "355649246276410/sk-xxx"),
        base_url="https://app-api.pixverseai.cn"
    )
    
    try:
        # 上传视频文件
        video_path = "path/to/your/video.mp4"  # 替换为实际视频路径
        
        if not Path(video_path).exists():
            print(f"❌ 视频文件不存在: {video_path}")
            print("💡 请将 video_path 替换为实际的视频路径")
            return
        
        print(f"📤 正在上传视频: {video_path}")
        upload_result = await client.upload_media(video_path, media_type="video")
        
        print(f"✅ 视频上传成功!")
        print(f"   📋 media_id: {upload_result.media_id}")
        print(f"   📁 文件名: {upload_result.file_name}")
        print(f"   📏 文件大小: {upload_result.file_size} bytes")
        print(f"   🎬 媒体类型: {upload_result.media_type}")
        
        return upload_result.media_id
        
    except Exception as e:
        print(f"❌ 上传失败: {e}")
    finally:
        await client.close()


async def complete_workflow_example():
    """演示完整工作流程：上传图片 -> 生成视频 -> 自动轮询"""
    print("\n🚀 完整工作流程示例")
    print("=" * 50)
    
    client = PixverseClient(
        api_key=os.getenv("PIXVERSE_API_KEY", "355649246276410/sk-xxxx"),
        base_url="https://app-api.pixverseai.cn"
    )
    
    try:
        image_path = "path/to/your/image.jpg"  # 替换为实际图片路径
        
        if not Path(image_path).exists():
            print(f"❌ 图片文件不存在: {image_path}")
            print("💡 请将 image_path 替换为实际的图片路径")
            return
        
        print("🎯 开始完整工作流程...")
        
        # 一键完成：上传 + 生成 + 轮询
        final_result = await client.upload_and_generate_video(
            image_path=image_path,
            prompt="A magical transformation with sparkles and light effects",
            model="v5",
            duration=5,
            quality="540p",
            wait_for_completion=True,  # 自动轮询等待完成
            max_wait_time=300  # 最多等待5分钟
        )
        
        print("🎉 完整工作流程成功!")
        print(f"   🎬 视频ID: {final_result.video_id}")
        print(f"   📊 状态: {final_result.status}")
        print(f"   🔗 视频URL: {final_result.video_url}")
        print(f"   🖼️ 缩略图: {final_result.thumbnail_url}")
        
    except Exception as e:
        print(f"❌ 工作流程失败: {e}")
    finally:
        await client.close()


async def manual_workflow_example():
    """演示手动分步工作流程"""
    print("\n🛠️ 手动分步工作流程示例")
    print("=" * 50)
    
    client = PixverseClient(
        api_key=os.getenv("PIXVERSE_API_KEY", "355649246276410/sk-xxxx"),
        base_url="https://app-api.pixverseai.cn"
    )
    
    try:
        image_path = "path/to/your/image.jpg"  # 替换为实际图片路径
        
        if not Path(image_path).exists():
            print(f"❌ 图片文件不存在: {image_path}")
            print("💡 请将 image_path 替换为实际的图片路径")
            return
        
        # 步骤1: 上传图片
        print("📤 步骤1: 上传图片...")
        upload_result = await client.upload_image(image_path)
        print(f"✅ 图片上传成功，img_id: {upload_result.img_id}")
        
        # 步骤2: 生成视频
        print("🎬 步骤2: 生成视频...")
        request = ImageToVideoRequest(
            img_id=upload_result.img_id,
            prompt="A beautiful sunset with gentle movements",
            model="v5",
            duration=5,
            quality="540p",
            aspect_ratio="16:9"
        )
        
        video_response = await client.image_to_video(request)
        print(f"✅ 视频生成任务已提交，video_id: {video_response.video_id}")
        
        # 步骤3: 自动轮询等待完成
        print("⏳ 步骤3: 等待视频生成完成...")
        final_result = await client.wait_for_video_completion(
            video_response.video_id,
            max_wait_time=300,
            poll_interval=10
        )
        
        print("🎉 视频生成完成!")
        print(f"   🔗 视频URL: {final_result.video_url}")
        print(f"   🖼️ 缩略图: {final_result.thumbnail_url}")
        
    except Exception as e:
        print(f"❌ 工作流程失败: {e}")
    finally:
        await client.close()


async def main():
    """主函数"""
    print("🎨 Pixverse 上传功能演示")
    print("=" * 60)
    
    # 运行各种示例
    await upload_image_example()
    await upload_media_example()
    await complete_workflow_example()
    await manual_workflow_example()
    
    print("\n✨ 所有示例演示完成!")


if __name__ == "__main__":
    asyncio.run(main())
