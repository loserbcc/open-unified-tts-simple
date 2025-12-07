#!/usr/bin/env python3
"""MCP Server for Open Unified TTS Simple.

Provides tools to generate unlimited-length TTS with automatic chunking.
"""
import asyncio
import os
import subprocess
import tempfile
from datetime import datetime
from pathlib import Path

import httpx
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# Configuration
API_URL = os.environ.get("TTS_API_URL", "http://localhost:8766")
OUTPUT_DIR = os.environ.get("TTS_OUTPUT_DIR", str(Path.home() / "tts-output"))

server = Server("unified-tts-simple")


@server.list_tools()
async def list_tools():
    return [
        Tool(
            name="speak",
            description="Generate speech from text. Supports unlimited length with automatic chunking.",
            inputSchema={
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "Text to convert to speech"
                    },
                    "voice": {
                        "type": "string",
                        "description": "Voice name (e.g., af_bella, am_adam, bf_emma)",
                        "default": "af_bella"
                    },
                    "action": {
                        "type": "string",
                        "enum": ["play", "save", "both"],
                        "description": "What to do with the audio",
                        "default": "play"
                    },
                    "filename": {
                        "type": "string",
                        "description": "Filename for saving (without extension). Auto-generated if not provided."
                    }
                },
                "required": ["text"]
            }
        ),
        Tool(
            name="list_voices",
            description="List all available TTS voices",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="tts_status",
            description="Check if the TTS service is running",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict):
    if name == "speak":
        return await handle_speak(arguments)
    elif name == "list_voices":
        return await handle_list_voices()
    elif name == "tts_status":
        return await handle_status()
    else:
        return [TextContent(type="text", text=f"Unknown tool: {name}")]


async def handle_speak(args: dict):
    text = args.get("text", "")
    voice = args.get("voice", "af_bella")
    action = args.get("action", "play")
    filename = args.get("filename")

    if not text:
        return [TextContent(type="text", text="Error: No text provided")]

    # Generate filename if not provided
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"tts_{timestamp}"

    # Ensure output directory exists
    Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)
    output_path = Path(OUTPUT_DIR) / f"{filename}.mp3"

    try:
        async with httpx.AsyncClient(timeout=300.0) as client:
            response = await client.post(
                f"{API_URL}/v1/audio/speech",
                json={
                    "input": text,
                    "voice": voice,
                    "response_format": "mp3"
                }
            )
            response.raise_for_status()
            audio_data = response.content

        word_count = len(text.split())
        result_parts = [f"Generated {word_count} words with voice '{voice}'"]

        # Handle action
        if action in ("save", "both"):
            output_path.write_bytes(audio_data)
            result_parts.append(f"Saved to: {output_path}")

        if action in ("play", "both"):
            # Save to temp if not already saved
            if action == "play":
                with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
                    f.write(audio_data)
                    play_path = f.name
            else:
                play_path = str(output_path)

            # Play audio (non-blocking)
            try:
                subprocess.Popen(
                    ["paplay", play_path],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                result_parts.append("Playing audio...")
            except FileNotFoundError:
                # Try mpv as fallback
                try:
                    subprocess.Popen(
                        ["mpv", "--no-video", play_path],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL
                    )
                    result_parts.append("Playing audio...")
                except FileNotFoundError:
                    result_parts.append("Could not play (no paplay or mpv)")

        return [TextContent(type="text", text="\n".join(result_parts))]

    except httpx.ConnectError:
        return [TextContent(type="text", text=f"Error: Cannot connect to TTS API at {API_URL}\nIs the service running?")]
    except Exception as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]


async def handle_list_voices():
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{API_URL}/v1/voices")
            response.raise_for_status()
            data = response.json()

        voices = data.get("voices", [])
        if not voices:
            return [TextContent(type="text", text="No voices available")]

        # Group voices by prefix
        groups = {}
        for v in voices:
            prefix = v[:2] if len(v) > 2 else v
            groups.setdefault(prefix, []).append(v)

        lines = ["Available voices:\n"]
        prefix_names = {
            "af": "American Female",
            "am": "American Male",
            "bf": "British Female",
            "bm": "British Male",
        }

        for prefix, voice_list in sorted(groups.items()):
            name = prefix_names.get(prefix, prefix.upper())
            lines.append(f"**{name}:** {', '.join(sorted(voice_list))}")

        return [TextContent(type="text", text="\n".join(lines))]

    except httpx.ConnectError:
        return [TextContent(type="text", text=f"Error: Cannot connect to TTS API at {API_URL}")]
    except Exception as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]


async def handle_status():
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{API_URL}/health")
            data = response.json()

        status = data.get("status", "unknown")
        backend = data.get("backend", "unknown")
        backend_ok = data.get("backend_status", False)

        return [TextContent(type="text", text=f"TTS Service: {status}\nBackend: {backend}\nBackend healthy: {backend_ok}")]

    except httpx.ConnectError:
        return [TextContent(type="text", text=f"TTS Service: OFFLINE\nCannot connect to {API_URL}")]
    except Exception as e:
        return [TextContent(type="text", text=f"Error checking status: {str(e)}")]


def main():
    asyncio.run(stdio_server(server))


if __name__ == "__main__":
    main()
