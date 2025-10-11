"""
Example of using Pixverse MCP as a client.
"""

import asyncio
import json
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def main():
    """Example MCP client usage."""
    
    # Server parameters
    server_params = StdioServerParameters(
        command="python",
        args=["-m", "pixverse_mcp.server"],
        env={"PIXVERSE_API_KEY": "355649246276410/sk-xxxx"}
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize the session
            await session.initialize()
            
            # List available tools
            tools = await session.list_tools()
            print("📋 Available tools:")
            for tool in tools.tools:
                print(f"  - {tool.name}: {tool.description}")
            
            # Example 1: Text to video
            print("\n🎬 Generating text-to-video...")
            result = await session.call_tool(
                "text_to_video",
                {
                    "prompt": "A beautiful sunset over the ocean with waves gently crashing",
                    "model": "v5",
                    "duration": 5,
                    "aspect_ratio": "16:9",
                    "quality": "540p",
                    "sound_effect_switch": True
                }
            )
            
            if result.isError:
                print(f"❌ Error: {result.content[0].text}")
            else:
                response_data = json.loads(result.content[0].text)
                print(f"✅ Video generated! ID: {response_data['video_id']}")
            
            # Example 2: Image to video
            print("\n🖼️ Generating image-to-video...")
            result = await session.call_tool(
                "image_to_video",
                {
                    "prompt": "The person starts dancing energetically",
                    "img_id": 167558521,
                    "model": "v5",
                    "duration": 5,
                    "quality": "540p",
                    "template_id": 315446315336768  # Kiss Kiss template
                }
            )
            
            if result.isError:
                print(f"❌ Error: {result.content[0].text}")
            else:
                response_data = json.loads(result.content[0].text)
                print(f"✅ Video generated! ID: {response_data['video_id']}")
            
            # Example 3: Get TTS speakers
            print("\n🎤 Getting TTS speakers...")
            result = await session.call_tool(
                "get_tts_speakers",
                {
                    "page_num": 1,
                    "page_size": 5
                }
            )
            
            if result.isError:
                print(f"❌ Error: {result.content[0].text}")
            else:
                response_data = json.loads(result.content[0].text)
                print(f"📋 Found {response_data['total']} speakers:")
                for speaker in response_data['data']:
                    print(f"  - {speaker['name']} (ID: {speaker['speaker_id']})")
            
            # Example 4: Fusion video
            print("\n🎭 Generating fusion video...")
            result = await session.call_tool(
                "fusion_video",
                {
                    "prompt": "A @dog and @cat playing together in a beautiful garden",
                    "image_references": [
                        {
                            "type": "subject",
                            "img_id": 167558521,
                            "ref_name": "dog"
                        },
                        {
                            "type": "subject", 
                            "img_id": 167558522,
                            "ref_name": "cat"
                        }
                    ],
                    "duration": 5,
                    "quality": "540p",
                    "aspect_ratio": "16:9"
                }
            )
            
            if result.isError:
                print(f"❌ Error: {result.content[0].text}")
            else:
                response_data = json.loads(result.content[0].text)
                print(f"✅ Fusion video generated! ID: {response_data['video_id']}")


if __name__ == "__main__":
    asyncio.run(main())
