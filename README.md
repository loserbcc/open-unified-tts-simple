# Open Unified TTS Simple

**Unlimited-length TTS in one command.** Pick a backend, run docker compose, done.

## The Problem

Most local TTS models break after 50-100 words. You get gibberish, cutoffs, or errors.

## The Solution

Smart chunking + seamless stitching. Your text splits at natural sentence boundaries, each chunk generates within model limits, then joins with 50ms crossfades. No audible seams.

## Quick Start

### Option 1: Kokoro (Recommended for beginners)
- 50+ built-in voices
- Runs on CPU (no GPU needed)
- No voice cloning setup required

```bash
git clone https://github.com/loserbcc/open-unified-tts-simple.git
cd open-unified-tts-simple
docker compose -f docker-compose.kokoro.yml up -d
```

### Option 2: VoxCPM 1.5 (Voice cloning)
- High-quality voice cloning
- Requires GPU (~8GB VRAM)
- Needs reference audio files

```bash
docker compose -f docker-compose.voxcpm.yml up -d
```

### Option 3: VibeVoice (Preset characters)
- Pre-trained character voices
- Requires GPU

```bash
docker compose -f docker-compose.vibevoice.yml up -d
```

## Usage

Once running, you have an OpenAI-compatible TTS API at `http://localhost:8765`:

```bash
# Short text
curl -X POST http://localhost:8765/v1/audio/speech \
  -H "Content-Type: application/json" \
  -d '{"input":"Hello world","voice":"af_bella"}' \
  -o hello.mp3

# Long text (auto-chunked)
curl -X POST http://localhost:8765/v1/audio/speech \
  -H "Content-Type: application/json" \
  -d '{"input":"Your entire 5000 word article here...","voice":"af_bella"}' \
  -o audiobook.mp3
```

## Works With

- **OpenWebUI** - Add as TTS provider
- **SillyTavern** - OpenAI TTS endpoint
- **Any OpenAI TTS client** - Drop-in replacement

## Kokoro Voices

| Style | Voices |
|-------|--------|
| American Female | af_bella, af_sarah, af_nova, af_sky, af_jessica |
| American Male | am_adam, am_michael, am_eric, am_onyx |
| British Female | bf_emma, bf_alice, bf_lily |
| British Male | bm_george, bm_daniel, bm_lewis |
| OpenAI Names | alloy, echo, fable, onyx, nova, shimmer |

## API Endpoints

| Endpoint | Description |
|----------|-------------|
| `POST /v1/audio/speech` | Generate speech (OpenAI-compatible) |
| `GET /v1/voices` | List available voices |
| `GET /health` | Health check |

## How It Works

1. Text comes in
2. Chunker splits at sentence boundaries (respecting backend limits)
3. Each chunk generates as WAV
4. Stitcher joins with crossfade (no audible seams)
5. Converts to requested format (mp3, wav, opus, etc.)

## MCP Server (Claude Integration)

Use TTS directly from Claude Code or Claude Desktop:

```bash
cd mcp-server
uv sync
claude mcp add unified-tts-simple uv run python server.py
```

### MCP Tools

| Tool | Description |
|------|-------------|
| `speak` | Generate speech - play it, save it, or both |
| `list_voices` | Show all available voices |
| `tts_status` | Check if TTS service is running |

### Example Usage (in Claude)

```
"Say hello world with Emma's voice"
→ speak(text="Hello world", voice="bf_emma", action="play")

"Generate an audiobook intro and save it"
→ speak(text="Welcome to...", voice="am_adam", action="save", filename="intro")
```

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `TTS_API_URL` | `http://localhost:8766` | URL of the TTS API |
| `TTS_OUTPUT_DIR` | `~/tts-output` | Where to save audio files |

## Need More?

This is the simple version. For multi-backend routing, voice preferences, and production features, see [open-unified-tts](https://github.com/loserbcc/open-unified-tts).

## License

Apache 2.0
