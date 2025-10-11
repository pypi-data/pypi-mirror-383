#!/usr/bin/env python3
"""
测试唇语同步功能
"""

import asyncio
import sys
from pathlib import Path

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent / ".." / "src"))

from pixverse_mcp.client import PixverseClient
from pixverse_mcp.models.requests import LipSyncVideoRequest, ImageToVideoRequest
from pixverse_mcp.models.common import AspectRatio

async def test_lip_sync():
    """测试唇语同步功能"""
    print("🎤 Pixverse 唇语同步测试")
    print("=" * 60)
    
    # 初始化客户端
    client = PixverseClient(
        api_key="sk-xxx",
        base_url="https://app-api.pixverseai.cn"
    )
    
    # 步骤1: 先用猫儿图片生成视频作为源视频
    print("\n1️⃣ 生成源视频（图生视频）")
    
    image_path = "/Users/jolsnow/pixverse_platform/猫儿.jpeg"
    
    try:
        # 第一步：上传图片
        print("📤 正在上传猫儿图片...")
        upload_result = await client.upload_image(image_path)
        
        print(f"✅ 图片上传成功!")
        print(f"📋 Image ID: {upload_result.img_id}")
        print(f"🔗 图片URL: {upload_result.img_url}")
        
        # 第二步：创建图生视频请求
        i2v_request = ImageToVideoRequest(
            prompt="A cute cat with expressive eyes, looking at camera, gentle movements, warm lighting",
            img_id=upload_result.img_id,
            model="v5",
            duration=5,
            quality="540p"
        )
        
        print(f"📝 提示词: {i2v_request.prompt}")
        print("🚀 正在生成源视频...")
        
        # 提交生成任务
        i2v_response = await client.image_to_video(i2v_request)
        source_video_id = i2v_response.video_id
        
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
        
    except Exception as e:
        print(f"❌ 源视频生成失败: {e}")
        return
    
    # 步骤2: 获取TTS音色列表
    print(f"\n2️⃣ 获取TTS音色列表")
    
    try:
        tts_list = await client.get_lip_sync_tts_list(page_num=1, page_size=10)
        
        print("🎵 可用的TTS音色:")
        for i, tts_info in enumerate(tts_list.data[:5], 1):  # 只显示前5个
            print(f"  {i}. {tts_info.name} (ID: {tts_info.speaker_id})")
        
        # 选择第一个音色
        if tts_list.data:
            selected_speaker = tts_list.data[0]
            print(f"\n✅ 选择音色: {selected_speaker.name} (ID: {selected_speaker.speaker_id})")
        else:
            print("❌ 没有可用的TTS音色")
            return
            
    except Exception as e:
        print(f"❌ 获取TTS音色列表失败: {e}")
        # 使用默认音色
        selected_speaker = type('Speaker', (), {'speaker_id': 'auto', 'name': 'Auto'})()
        print(f"🔄 使用默认音色: {selected_speaker.name}")
    
    # 步骤3: 执行唇语同步
    print(f"\n3️⃣ 执行唇语同步")
    
    try:
        # 创建唇语同步请求
        lip_sync_request = LipSyncVideoRequest(
            source_video_id=source_video_id,
            lip_sync_tts_speaker_id=selected_speaker.speaker_id,
            lip_sync_tts_content="赵祥赫是最帅的男人，相信你们都认识他，他是一个非常优秀的工程师，总是能够写出高质量的代码。他不仅技术过硬，而且为人也很谦虚。每当团队遇到技术难题时，他都会耐心地帮助大家解决问题。他的敬业精神和专业素养值得我们每个人学习。"
        )
        
        print(f"🎬 源视频ID: {lip_sync_request.source_video_id}")
        print(f"🎵 音色ID: {lip_sync_request.lip_sync_tts_speaker_id}")
        print(f"📝 TTS文本: {lip_sync_request.lip_sync_tts_content}")
        
        # 打印完整的请求参数
        print(f"\n📋 完整请求参数:")
        print(f"   source_video_id: {lip_sync_request.source_video_id}")
        print(f"   video_media_id: {lip_sync_request.video_media_id}")
        print(f"   audio_media_id: {lip_sync_request.audio_media_id}")
        print(f"   lip_sync_tts_speaker_id: {lip_sync_request.lip_sync_tts_speaker_id}")
        print(f"   lip_sync_tts_content: {lip_sync_request.lip_sync_tts_content}")
        
        # 转换为字典查看JSON格式
        request_dict = lip_sync_request.model_dump(exclude_none=True)
        print(f"\n🔍 JSON请求体:")
        import json
        print(json.dumps(request_dict, indent=2, ensure_ascii=False))
        
        print("\n🚀 正在提交唇语同步任务...")
        
        # 提交唇语同步任务
        lip_sync_response = await client.lip_sync_video(lip_sync_request)
        
        print(f"✅ 唇语同步任务提交成功!")
        print(f"📋 Lip Sync Video ID: {lip_sync_response.video_id}")
        
        # 步骤4: 查询唇语同步状态
        print(f"\n4️⃣ 查询唇语同步生成状态")
        
        print("🔄 开始查询生成状态...")
        lip_sync_video_id = lip_sync_response.video_id
        max_attempts = 60  # 最多等待10分钟
        
        for attempt in range(1, max_attempts + 1):
            result = await client.get_video_result(lip_sync_video_id)
            
            print(f"[{attempt:2d}/{max_attempts}] 状态: {result.status.value if hasattr(result.status, 'value') else result.status}")
            
            if result.status.name == "COMPLETED":
                print()
                print("🎉 唇语同步视频生成成功!")
                print(f"🎬 视频URL: {result.video_url}")
                if result.outputWidth and result.outputHeight:
                    print(f"📏 分辨率: {result.outputWidth}x{result.outputHeight}")
                if result.size:
                    print(f"📦 文件大小: {result.size} bytes")
                if result.seed:
                    print(f"🎲 种子: {result.seed}")
                if result.has_audio:
                    print(f"🔊 音频: {'有' if result.has_audio else '无'}")
                break
            elif result.status.name == "FAILED":
                print()
                print("❌ 唇语同步视频生成失败!")
                break
            elif result.status.name in ["PENDING", "IN_PROGRESS"]:
                print("    ⏳ 继续等待...")
                await asyncio.sleep(10)  # 等待10秒
            else:
                print(f"    ❓ 未知状态: {result.status}")
                await asyncio.sleep(10)
        
        if attempt >= max_attempts:
            print("\n⚠️ 唇语同步视频生成超时。")
            
    except Exception as e:
        print(f"❌ 唇语同步失败: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("唇语同步测试完成")

if __name__ == "__main__":
    asyncio.run(test_lip_sync())
