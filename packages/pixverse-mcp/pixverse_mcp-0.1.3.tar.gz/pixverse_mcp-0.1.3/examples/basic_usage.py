"""
Basic usage examples for Pixverse MCP client.
"""

import asyncio
import os
from dotenv import load_dotenv

from pixverse_mcp import PixverseClient
from pixverse_mcp.models import (
    TextToVideoRequest,
    ImageToVideoRequest,
    ModelVersion,
    VideoQuality,
    AspectRatio,
)

# Load environment variables
load_dotenv()


async def text_to_video_example():
    """Example: Generate video from text."""
    print("🎬 Text-to-Video Example")
    
    async with PixverseClient(api_key=os.getenv("PIXVERSE_API_KEY")) as client:
        # Quick method
        result = await client.quick_text_video(
            prompt="A majestic eagle soaring over snow-capped mountains at sunset",
            model="v5",
            duration=5,
            quality="540p",
            aspect_ratio="16:9"
        )
        print(f"✅ Video generated! ID: {result.video_id}")
        
        # Detailed method with all parameters
        request = TextToVideoRequest(
            prompt="A cyberpunk cityscape with neon lights and flying cars",
            model=ModelVersion.V5,
            duration=5,
            aspect_ratio=AspectRatio.RATIO_16_9,
            quality=VideoQuality.Q540P,
            style="cyberpunk",
            sound_effect_switch=True,
            sound_effect_content="Futuristic city ambience with electronic music"
        )
        
        result = await client.text_to_video(request)
        print(f"✅ Cyberpunk video generated! ID: {result.video_id}")


async def image_to_video_example():
    """Example: Generate video from image."""
    print("\n🖼️ Image-to-Video Example")
    
    async with PixverseClient(api_key=os.getenv("PIXVERSE_API_KEY")) as client:
        # Quick method
        result = await client.quick_image_video(
            img_id=167558521,  # Replace with actual image ID
            prompt="The person in the image starts dancing gracefully",
            model="v5",
            duration=5,
            quality="540p"
        )
        print(f"✅ Image animation generated! ID: {result.video_id}")
        
        # With template
        request = ImageToVideoRequest(
            img_id=167558521,
            prompt="Perform amazing martial arts moves",
            model=ModelVersion.V5,
            duration=5,
            quality=VideoQuality.Q540P,
            template_id=315447659476032,  # Kungfu Club template
            sound_effect_switch=True
        )
        
        result = await client.image_to_video(request)
        print(f"✅ Martial arts video generated! ID: {result.video_id}")


async def get_tts_speakers_example():
    """Example: Get available TTS speakers."""
    print("\n🎤 TTS Speakers Example")
    
    async with PixverseClient(api_key=os.getenv("PIXVERSE_API_KEY")) as client:
        speakers = await client.get_lip_sync_tts_list(page_num=1, page_size=10)
        
        print(f"📋 Found {speakers.total} TTS speakers:")
        for speaker in speakers.data[:5]:  # Show first 5
            print(f"  - {speaker.name} (ID: {speaker.speaker_id})")


async def error_handling_example():
    """Example: Error handling."""
    print("\n⚠️ Error Handling Example")
    
    try:
        async with PixverseClient(api_key="355649246276410/sk-xxx") as client:
            await client.quick_text_video(
                prompt="This will fail due to invalid API key"
            )
    except Exception as e:
        print(f"❌ Expected error caught: {type(e).__name__}: {e}")


async def main():
    """Run all examples."""
    print("🚀 Pixverse MCP Client Examples\n")
    
    if not os.getenv("PIXVERSE_API_KEY"):
        print("❌ Please set PIXVERSE_API_KEY environment variable")
        return
    
    try:
        await text_to_video_example()
        await image_to_video_example()
        await get_tts_speakers_example()
        await error_handling_example()
        
        print("\n✨ All examples completed!")
        
    except Exception as e:
        print(f"\n❌ Example failed: {e}")


if __name__ == "__main__":
    asyncio.run(main())
