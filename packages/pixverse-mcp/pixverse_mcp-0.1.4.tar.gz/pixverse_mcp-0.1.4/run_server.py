#!/usr/bin/env python3
"""
Pixverse MCP Server launcher script.
"""

import asyncio
import sys
import os
import argparse
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from pixverse_mcp.server import main

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Pixverse MCP Server")
    parser.add_argument("--config", "-c", help="Path to configuration file (optional)", 
                       default=None)
    parser.add_argument("--mode", "-m", choices=["stdio", "sse"], default="stdio",
                       help="Server mode: stdio (default) or sse")
    parser.add_argument("--host", default="0.0.0.0", help="Host for SSE mode (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=8080, help="Port for SSE mode (default: 8080)")
    args = parser.parse_args()
    
    # Check if config file exists (optional)
    config_path = None
    if args.config:
        config_file = Path(args.config)
        if not config_file.exists():
            # Try relative to script directory
            config_file = Path(__file__).parent / args.config
            if config_file.exists():
                config_path = str(config_file)
            else:
                print(f"💡 Config file not found: {args.config}")
                print("🔧 Using default configuration and environment variables")
        else:
            config_path = str(config_file)
    
    print("🚀 Starting Pixverse MCP Server...")
    if args.mode == "sse":
        print(f"🌐 Server will run in SSE mode on http://{args.host}:{args.port}")
        print("📡 Endpoints:")
        print(f"   - SSE Stream: http://{args.host}:{args.port}/events")
        print(f"   - API Docs: http://{args.host}:{args.port}/docs")
        print(f"   - Text-to-Video: http://{args.host}:{args.port}/api/text-to-video")
        print(f"   - Image-to-Video: http://{args.host}:{args.port}/api/image-to-video")
    else:
        print("📡 Server will listen on stdio for MCP protocol messages")
    
    if config_path:
        print(f"⚙️  Using config file: {config_path}")
    else:
        print("⚙️  Using environment variables")
    print("⏹️  Press Ctrl+C to stop")
    print("-" * 50)
    
    try:
        asyncio.run(main(config_path=config_path, mode=args.mode))
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"\n❌ Server error: {e}")
        sys.exit(1)
