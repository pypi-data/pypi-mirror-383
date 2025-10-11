#!/usr/bin/env python3
"""
测试视频转场生成功能
"""

import asyncio
import sys
from pathlib import Path

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent / ".." / "src"))

from pixverse_mcp.client import PixverseClient
from pixverse_mcp.models.requests import TransitionVideoRequest
from pixverse_mcp.models.common import ModelVersion, VideoQuality, MotionMode

async def test_video_transition():
    """测试视频转场生成功能"""
    print("🎬 Pixverse 视频转场测试")
    print("=" * 60)
    
    # 初始化客户端
    client = PixverseClient(
        api_key="xxx",
        base_url="https://app-api.pixverseai.cn"
    )
    
    # 步骤1: 上传两张图片作为首尾帧
    print("\n1️⃣ 上传首帧和尾帧图片")
    
    first_image_path = "/Users/jolsnow/pixverse_platform/猫儿.jpeg"
    second_image_path = "/Users/jolsnow/pixverse_platform/橘猫.jpeg"
    
    if not Path(first_image_path).exists() or not Path(second_image_path).exists():
        print("❌ 测试图片文件不存在")
        return
    
    try:
        # 上传首帧图片
        print(f"📤 上传首帧图片: {Path(first_image_path).name}")
        first_frame_result = await client.upload_image(first_image_path)
        first_frame_img_id = first_frame_result.img_id
        print(f"✅ 首帧上传成功! Image ID: {first_frame_img_id}")
        
        # 上传尾帧图片
        print(f"📤 上传尾帧图片: {Path(second_image_path).name}")
        last_frame_result = await client.upload_image(second_image_path)
        last_frame_img_id = last_frame_result.img_id
        print(f"✅ 尾帧上传成功! Image ID: {last_frame_img_id}")
        
    except Exception as e:
        print(f"❌ 图片上传失败: {e}")
        return
    
    # 步骤2: 生成转场视频
    print(f"\n2️⃣ 生成转场视频")
    
    try:
        # 创建转场请求
        transition_request = TransitionVideoRequest(
            prompt="A smooth transition between two cute cats, cinematic lighting, high quality",
            first_frame_img=first_frame_img_id,
            last_frame_img=last_frame_img_id,
            model=ModelVersion.V4,  # 转场功能支持v3.5和v4
            duration=5,
            quality=VideoQuality.Q540P,
            motion_mode=MotionMode.NORMAL,
            water_mark=False
        )
        
        print(f"📝 提示词: {transition_request.prompt}")
        print(f"🖼️ 首帧ID: {transition_request.first_frame_img}")
        print(f"🖼️ 尾帧ID: {transition_request.last_frame_img}")
        print(f"🔧 模型: {transition_request.model.value}")
        print(f"⏱️ 时长: {transition_request.duration}秒")
        print(f"📺 质量: {transition_request.quality.value}")
        
        print("\n🚀 正在提交转场视频生成任务...")
        
        # 提交转场生成任务
        response = await client.transition_video(transition_request)
        
        print(f"✅ 转场任务提交成功!")
        print(f"📋 Video ID: {response.video_id}")
        
        # 步骤3: 查询生成状态
        print(f"\n3️⃣ 查询转场视频生成状态")
        
        print("🔄 开始查询生成状态...")
        video_id = response.video_id
        max_attempts = 60  # 最多等待10分钟
        
        for attempt in range(1, max_attempts + 1):
            result = await client.get_video_result(video_id)
            
            print(f"[{attempt:2d}/{max_attempts}] 状态: {result.status.value if hasattr(result.status, 'value') else result.status}")
            
            if result.status.name == "COMPLETED":
                print()
                print("🎉 转场视频生成成功!")
                print(f"🎬 视频URL: {result.video_url}")
                if result.outputWidth and result.outputHeight:
                    print(f"📏 分辨率: {result.outputWidth}x{result.outputHeight}")
                if result.size:
                    print(f"📦 文件大小: {result.size} bytes")
                if result.seed:
                    print(f"🎲 种子: {result.seed}")
                break
            elif result.status.name == "FAILED":
                print()
                print("❌ 转场视频生成失败!")
                break
            elif result.status.name in ["PENDING", "IN_PROGRESS"]:
                print("    ⏳ 继续等待...")
                await asyncio.sleep(10)  # 等待10秒
            else:
                print(f"    ❓ 未知状态: {result.status}")
                await asyncio.sleep(10)
        
        if attempt >= max_attempts:
            print("\n⚠️ 转场视频生成超时。")
            
    except Exception as e:
        print(f"❌ 转场视频生成失败: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("转场视频测试完成")

if __name__ == "__main__":
    asyncio.run(test_video_transition())
