# MCP Integration Guide

Use Open TTS Studio directly from Claude Code or Claude Desktop through the Model Context Protocol (MCP).

## What is MCP?

MCP (Model Context Protocol) lets Claude AI tools interact directly with your local TTS system. You can ask Claude to generate speech, and it will use your local TTS backend.

## Quick Install

```bash
# Navigate to the MCP server directory
cd mcp-server

# Install dependencies
uv sync

# Add to Claude
claude mcp add open-tts-studio uv run python server.py
```

## Prerequisites

Before setting up the MCP server, make sure you have:

1. **TTS Backend Running** - Either Kokoro or VoxCPM container
2. **API Server Running** - `uv run python server.py` from the main directory
3. **Claude Desktop or Claude Code** - Installed and configured

## Setup Steps

### 1. Start Your TTS Backend

```bash
# From the main open-tts-studio directory
docker compose -f docker-compose.kokoro.yml up -d
```

### 2. Start the API Server

```bash
# From the main directory
uv run python server.py
```

The API should be running at `http://localhost:8765`

### 3. Configure the MCP Server

Edit `mcp-server/.env` to configure your setup:

```bash
# TTS API URL (where your server.py is running)
TTS_API_URL=http://localhost:8765

# Where to save generated audio files
TTS_OUTPUT_DIR=~/tts-output

# Optional: Default voice to use
DEFAULT_VOICE=af_bella
```

### 4. Add to Claude

```bash
cd mcp-server
uv sync
claude mcp add open-tts-studio uv run python server.py
```

### 5. Verify Installation

In Claude Desktop or Claude Code, you should now see the `open-tts-studio` MCP server listed.

Test it by asking Claude:
```
"Can you check if the TTS service is running?"
```

Claude should use the `tts_status` tool to verify connectivity.

## Available MCP Tools

### `speak` - Generate Speech

Generate speech from text with various options.

**Parameters:**
- `text` (required) - The text to convert to speech
- `voice` (optional) - Voice ID (e.g., "af_bella", "am_adam")
- `action` (optional) - What to do with the audio:
  - `"play"` - Play immediately (default)
  - `"save"` - Save to file
  - `"both"` - Play and save
- `filename` (optional) - Custom filename when saving (without extension)
- `speed` (optional) - Speech speed (0.5 to 2.0, default 1.0)
- `format` (optional) - Audio format (mp3, wav, opus, aac, flac)

**Examples:**

```
User: "Say hello world with Emma's voice"
Claude: speak(text="Hello world", voice="bf_emma", action="play")

User: "Generate an audiobook intro and save it"
Claude: speak(text="Welcome to chapter one...", voice="am_adam", action="save", filename="chapter1_intro")

User: "Say this quickly: The quick brown fox"
Claude: speak(text="The quick brown fox", speed=1.5, action="play")
```

### `list_voices` - Show Available Voices

List all voices available from your TTS backend.

**Parameters:** None

**Example:**

```
User: "What voices are available?"
Claude: list_voices()
```

Returns a formatted list of all available voices with their IDs.

### `tts_status` - Check Service Status

Verify that the TTS API is running and accessible.

**Parameters:** None

**Example:**

```
User: "Is the TTS service working?"
Claude: tts_status()
```

Returns connection status and API URL.

## Common Workflows

### Generate and Play Audio

```
User: "Read this text aloud with a British male voice"
Claude: [Uses speak() with appropriate British male voice]
```

### Create Audiobook Chapter

```
User: "Generate chapter 3 with Adam's voice and save it as chapter3"
Claude: speak(
    text="[full chapter text]",
    voice="am_adam",
    action="save",
    filename="chapter3"
)
```

### Test Multiple Voices

```
User: "Say 'Hello there' with 5 different voices so I can compare"
Claude: [Uses speak() 5 times with different voices]
```

### Batch Generation

```
User: "Generate these 3 paragraphs as separate audio files"
Claude: [Uses speak() 3 times with action="save" and different filenames]
```

## Environment Variables

Configure the MCP server by setting these in `mcp-server/.env`:

| Variable | Default | Description |
|----------|---------|-------------|
| `TTS_API_URL` | `http://localhost:8765` | URL of the TTS API server |
| `TTS_OUTPUT_DIR` | `~/tts-output` | Directory for saved audio files |
| `DEFAULT_VOICE` | `af_bella` | Default voice when none specified |
| `DEFAULT_FORMAT` | `mp3` | Default audio format |
| `DEFAULT_SPEED` | `1.0` | Default speech speed |

## Troubleshooting

### "Connection refused" Error

**Problem:** MCP server can't reach the TTS API.

**Solution:**
1. Make sure `server.py` is running: `uv run python server.py`
2. Check the API URL in `mcp-server/.env`
3. Test manually: `curl http://localhost:8765/health`

### "No voices available" Error

**Problem:** TTS backend isn't running or not configured.

**Solution:**
1. Start the backend: `docker compose -f docker-compose.kokoro.yml up -d`
2. Verify backend: `curl http://localhost:8766/v1/voices`
3. Check backend URL in main `server.py` configuration

### Audio Not Playing

**Problem:** `speak()` with `action="play"` doesn't produce sound.

**Solution:**
1. Check that you have a system audio player installed
2. Try `action="save"` to verify audio is being generated
3. Check MCP server logs for errors

### Permission Denied on Output Directory

**Problem:** Can't save files to `TTS_OUTPUT_DIR`.

**Solution:**
1. Create the directory: `mkdir -p ~/tts-output`
2. Check permissions: `ls -la ~/tts-output`
3. Update `TTS_OUTPUT_DIR` in `.env` to a writable location

## Advanced Usage

### Custom Voice Preferences

Create a `voice_preferences.json` in `mcp-server/` to map character names to voices:

```json
{
  "narrator": "am_adam",
  "alice": "af_bella",
  "bob": "am_michael",
  "british_narrator": "bm_george"
}
```

Then in Claude:
```
User: "Have Alice say hello"
Claude: [Automatically uses af_bella voice]
```

### Multi-Speaker Dialogues

For complex dialogues, use the main Studio interface instead of MCP. The MCP server is designed for single-voice generation.

### Integration with Other Tools

The MCP server can be combined with other MCP servers:

```bash
# Add filesystem MCP for reading scripts
claude mcp add filesystem ...

# Add open-tts-studio for generating audio
claude mcp add open-tts-studio ...

# Now Claude can read a file and generate audio from it
User: "Read the script in story.txt and generate audio"
```

## Development

### Running the MCP Server Manually

```bash
cd mcp-server
uv run python server.py
```

### Testing Without Claude

```bash
# Check if server responds
curl http://localhost:8765/health

# List voices via API
curl http://localhost:8765/v1/voices

# Generate speech via API
curl -X POST http://localhost:8765/v1/audio/speech \
  -H "Content-Type: application/json" \
  -d '{"input":"Test","voice":"af_bella"}' \
  -o test.mp3
```

### Debugging

Enable debug logging by setting in `mcp-server/.env`:

```bash
DEBUG=true
LOG_LEVEL=debug
```

Check logs:
```bash
tail -f mcp-server/mcp-server.log
```

## Security Considerations

- **Local Only**: The MCP server is designed for local use only
- **No Authentication**: By default, no auth is required (local trusted environment)
- **File Access**: The server can write files to `TTS_OUTPUT_DIR` only
- **Network**: The server only connects to your local TTS API

## See Also

- [COMPLETE_TUTORIAL.md](COMPLETE_TUTORIAL.md) - Full setup guide
- [STUDIO_USER_GUIDE.md](STUDIO_USER_GUIDE.md) - Web interface features
- [FAQ.md](FAQ.md) - Common questions
- [Model Context Protocol](https://modelcontextprotocol.io/) - MCP documentation

## Support

Need help?

- Open an issue: https://github.com/loserbcc/open-tts-studio/issues
- Email: buddy@loser.com
