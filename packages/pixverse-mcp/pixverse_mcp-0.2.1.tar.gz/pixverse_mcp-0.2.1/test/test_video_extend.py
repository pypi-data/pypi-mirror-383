#!/usr/bin/env python3
"""
测试视频延长功能
"""

import asyncio
import sys
from pathlib import Path

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent / ".." / "src"))

from pixverse_mcp.client import PixverseClient
from pixverse_mcp.models.requests import ExtendVideoRequest, TextToVideoRequest
from pixverse_mcp.models.common import AspectRatio, ModelVersion, VideoQuality, MotionMode

async def test_video_extend():
    """测试视频延长功能"""
    print("📏 Pixverse 视频延长测试")
    print("=" * 60)
    
    # 初始化客户端
    client = PixverseClient(
        api_key="sk-xxx",
        base_url="https://app-api.pixverseai.cn"
    )
    
    # 步骤1: 先生成一个短视频作为源视频
    print("\n1️⃣ 生成源视频（5秒短视频）")
    
    try:
        # 创建文生视频请求（生成短视频）
        t2v_request = TextToVideoRequest(
            prompt="A serene mountain landscape with flowing clouds, cinematic view, peaceful atmosphere",
            model="v4",  # 延长功能支持v3.5和v4
            duration=5,
            aspect_ratio=AspectRatio.RATIO_16_9,
            quality="540p"
        )
        
        print(f"📝 提示词: {t2v_request.prompt}")
        print(f"🔧 模型: {t2v_request.model}")
        print(f"⏱️ 时长: {t2v_request.duration}秒")
        print("🚀 正在生成源视频...")
        
        # 提交生成任务
        t2v_response = await client.text_to_video(t2v_request)
        source_video_id = t2v_response.video_id
        
        print(f"✅ 源视频任务提交成功!")
        print(f"📋 Source Video ID: {source_video_id}")
        
        # 等待源视频生成完成
        print("⏳ 等待源视频生成完成...")
        source_result = await client.wait_for_video_completion(source_video_id, max_wait_time=600)
        
        if source_result.status.name != "COMPLETED":
            print(f"❌ 源视频生成失败，状态: {source_result.status}")
            return
            
        print("✅ 源视频生成完成!")
        print(f"🎬 源视频URL: {source_result.video_url}")
        if source_result.outputWidth and source_result.outputHeight:
            print(f"📏 源视频分辨率: {source_result.outputWidth}x{source_result.outputHeight}")
        
    except Exception as e:
        print(f"❌ 源视频生成失败: {e}")
        return
    
    # 步骤2: 延长视频
    print(f"\n2️⃣ 延长视频")
    
    try:
        # 创建视频延长请求
        extend_request = ExtendVideoRequest(
            prompt="Continue the peaceful mountain scene with gentle wind moving through trees, maintaining the same cinematic quality",
            source_video_id=source_video_id,
            model=ModelVersion.V4,  # 延长功能支持v3.5和v4
            duration=5,  # 延长5秒
            quality=VideoQuality.Q540P,
            motion_mode=MotionMode.NORMAL
        )
        
        print(f"📝 延长提示词: {extend_request.prompt}")
        print(f"🎬 源视频ID: {extend_request.source_video_id}")
        print(f"🔧 模型: {extend_request.model.value}")
        print(f"⏱️ 延长时长: {extend_request.duration}秒")
        print(f"📺 质量: {extend_request.quality.value}")
        
        print("\n🚀 正在提交视频延长任务...")
        
        # 提交视频延长任务
        extend_response = await client.extend_video(extend_request)
        
        print(f"✅ 视频延长任务提交成功!")
        print(f"📋 Extended Video ID: {extend_response.video_id}")
        
        # 步骤3: 查询延长视频状态
        print(f"\n3️⃣ 查询延长视频生成状态")
        
        print("🔄 开始查询生成状态...")
        extended_video_id = extend_response.video_id
        max_attempts = 60  # 最多等待10分钟
        
        for attempt in range(1, max_attempts + 1):
            result = await client.get_video_result(extended_video_id)
            
            print(f"[{attempt:2d}/{max_attempts}] 状态: {result.status.value if hasattr(result.status, 'value') else result.status}")
            
            if result.status.name == "COMPLETED":
                print()
                print("🎉 视频延长成功!")
                print(f"🎬 延长视频URL: {result.video_url}")
                if result.outputWidth and result.outputHeight:
                    print(f"📏 分辨率: {result.outputWidth}x{result.outputHeight}")
                if result.size:
                    print(f"📦 文件大小: {result.size} bytes")
                if result.seed:
                    print(f"🎲 种子: {result.seed}")
                if result.has_audio:
                    print(f"🔊 音频: {'有' if result.has_audio else '无'}")
                    
                print(f"\n📊 对比信息:")
                print(f"   原视频: 5秒")
                print(f"   延长后: 预计10秒 (5秒原视频 + 5秒延长)")
                break
            elif result.status.name == "FAILED":
                print()
                print("❌ 视频延长失败!")
                break
            elif result.status.name in ["PENDING", "IN_PROGRESS"]:
                print("    ⏳ 继续等待...")
                await asyncio.sleep(10)  # 等待10秒
            else:
                print(f"    ❓ 未知状态: {result.status}")
                await asyncio.sleep(10)
        
        if attempt >= max_attempts:
            print("\n⚠️ 视频延长生成超时。")
            
    except Exception as e:
        print(f"❌ 视频延长失败: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("视频延长测试完成")

if __name__ == "__main__":
    asyncio.run(test_video_extend())
