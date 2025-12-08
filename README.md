# Open TTS Studio

![Version](https://img.shields.io/badge/version-0.0.1--alpha-orange)
![License](https://img.shields.io/badge/license-Apache%202.0-blue)
![Status](https://img.shields.io/badge/status-alpha-red)

**The open-source multi-speaker TTS production interface.**

Create professional audiobooks, podcasts, and multi-speaker audio in minutes - not hours. Simple web interface, unlimited text length, works with any TTS backend.

> ⚠️ **Alpha Software** - This is v0.0.1, expect rough edges! Early adopters welcome. Please report bugs and share feedback.

> **New to TTS?** Start here! This is the user-friendly front-end.
> **Need the powerful API?** See [open-unified-tts](https://github.com/loserbcc/open-unified-tts) for backend routing and production features.

---

## 🚀 Try It Now - Free Alpha Demo

**Don't want to install anything?** Try the full-featured hosted version free while we're in alpha:

### **[lessfortts.loser.com](https://lessfortts.loser.com)**

| Feature | What You Get |
|---------|--------------|
| **67 Kokoro voices** | American, British, male, female |
| **10 Vietnamese voices** | Northern & Southern accents |
| **14 character clones** | Morgan Freeman, Rick & Morty, Yoda, GLaDOS, Batman, and more |
| **8 emotion voices** | Happy, sad, calm, excited |

Free signup (no credit card). Just paste text and generate.

> **Alpha notice:** No data retention guaranteed. Download your audio - we're not saving it for you (yet).

> **Note:** The hosted demo runs on the more advanced [open-unified-tts](https://github.com/loserbcc/open-unified-tts) multi-backend architecture. This repo (Open TTS Studio) is a simplified version designed for easy local deployment.

---

## What is Open TTS Studio?

**Two tools in one:**

### 1. Production Studio (Web Interface) 🎬
- **Multi-speaker script editor** - Write dialogues with auto-speaker detection
- **Voice assignment** - Searchable dropdowns (type to find voices instantly)
- **One-click generation** - From script to audio in seconds
- **Perfect for:** Audiobooks, podcasts, character dialogues

### 2. API Server (Developers) 🔧
- **OpenAI-compatible endpoints** - Drop-in replacement
- **Smart chunking** - Handles unlimited text length
- **Works with:** OpenWebUI, SillyTavern, any OpenAI TTS client

## The Problem

Most local TTS models break after 50-100 words. You get gibberish, cutoffs, or errors.

## The Solution

Smart chunking + seamless stitching. Your text splits at natural sentence boundaries, each chunk generates within model limits, then joins with crossfades. No audible seams.

## Quick Start - Production Studio

### Step 1: Start a TTS Backend

**Kokoro (Recommended - 67 voices, CPU-friendly)**
```bash
git clone https://github.com/loserbcc/open-tts-studio.git
cd open-tts-studio
docker compose -f docker-compose.kokoro.yml up -d
```

**OR VoxCPM (Voice cloning, needs GPU)**
```bash
docker compose -f docker-compose.voxcpm.yml up -d
```

### Step 2: Start the Studio

```bash
# Install dependencies
uv sync

# Start the web interface
uv run python studio_v2.py
```

Open http://localhost:7860 in your browser.

### Step 3: Create Your First Production

1. **Go to Settings** → Configure your backend (auto-detected if using Kokoro locally)
2. **Go to Studio** → Paste a script:
   ```
   Alice: Hi! Welcome to our show.
   Bob: Thanks Alice. Today we're talking about TTS.
   Alice: It's amazing how far voice AI has come!
   ```
3. **Click "Auto-Detect Speakers"** → Assigns Alice and Bob
4. **Assign voices** → Type to search, pick voices you like
5. **Click "Generate Production"** → Listen to your multi-speaker audio!

**That's it!** See [COMPLETE_TUTORIAL.md](COMPLETE_TUTORIAL.md) for the full walkthrough.

---

## Quick Start - API Only (For Developers)

If you just need the API (no Studio UI), start the backend and server:

```bash
# Start backend (Kokoro example)
docker compose -f docker-compose.kokoro.yml up -d

# Start API server
uv run python server.py
```

You now have an OpenAI-compatible TTS API at `http://localhost:8765`:

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

## Requirements

- **Docker** (for the containers)
- **ffmpeg** (included in Docker image, but needed if running server.py directly)

## 🤖 MCP Server - The AI-Native Interface

**This is the killer feature.** MCP (Model Context Protocol) lets any AI assistant speak using your TTS system. No web UI, no API calls - just natural language.

### What is MCP?

MCP is an open standard (created by Anthropic) that lets AI assistants use tools. Think of it as "plugins for AI" - once you install an MCP server, your AI can use those capabilities directly.

### Why This Matters

| Without MCP | With MCP |
|-------------|----------|
| Copy text → Open web UI → Paste → Generate → Download | "Read this article aloud with Emma's voice" |
| Write curl commands | "Generate an audiobook from chapter3.txt" |
| Manual workflow | AI handles everything |

**Your AI assistant becomes a voice.**

### Compatible MCP Clients

Works with any MCP-compatible AI tool:

| Client | Type | Notes |
|--------|------|-------|
| [Claude Code](https://claude.ai/code) | CLI | Anthropic's official CLI |
| [Claude Desktop](https://claude.ai/download) | Desktop App | macOS/Windows |
| [Cline](https://github.com/cline/cline) | VS Code Extension | Open source |
| [Cursor](https://cursor.sh) | IDE | AI-first code editor |
| [Windsurf](https://codeium.com/windsurf) | IDE | Codeium's AI IDE |
| [Continue](https://continue.dev) | VS Code/JetBrains | Open source |
| Any MCP client | - | Standard protocol |

### Quick Install

```bash
cd mcp-server

# Install dependencies
uv sync

# Add to Claude Code (one command)
claude mcp add unified-tts-simple uv run python server.py

# Or add to Claude Desktop (~/.claude/claude_desktop_config.json)
```

<details>
<summary>Claude Desktop config example</summary>

```json
{
  "mcpServers": {
    "unified-tts-simple": {
      "command": "uv",
      "args": ["run", "--directory", "/path/to/mcp-server", "python", "server.py"],
      "env": {
        "TTS_API_URL": "http://localhost:8766",
        "TTS_OUTPUT_DIR": "~/tts-output"
      }
    }
  }
}
```
</details>

### MCP Tools

| Tool | Description |
|------|-------------|
| `speak` | Generate speech - play it, save it, or both |
| `list_voices` | Show all available voices |
| `tts_status` | Check if TTS service is running |

### Natural Language Examples

Just talk to your AI naturally:

```
"Say hello world with Emma's voice"
→ speak(text="Hello world", voice="bf_emma", action="play")

"Read this README aloud and save it as intro.mp3"
→ speak(text="...", voice="af_bella", action="save", filename="intro")

"What voices do you have?"
→ list_voices()

"Is the TTS server running?"
→ tts_status()
```

### Real-World Use Cases

| Scenario | What You Say |
|----------|--------------|
| **Proofreading** | "Read my email draft back to me" |
| **Accessibility** | "Read this documentation aloud" |
| **Content creation** | "Generate audio for each section of my blog post" |
| **Learning** | "Read this French text with the French voice" |
| **Podcast prep** | "Create audio for my script, Alice uses Emma's voice, Bob uses Adam's" |

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `TTS_API_URL` | `http://localhost:8766` | URL of the TTS API |
| `TTS_OUTPUT_DIR` | `~/tts-output` | Where to save audio files |

### Zero Setup Option: Use the Hosted SaaS

**Don't want to run your own TTS server?** Point your MCP client at our hosted API:

```json
{
  "env": {
    "TTS_API_URL": "https://lessfortts.loser.com"
  }
}
```

That's it. Install the MCP server, set the URL, and your AI can speak. No Docker, no GPU, no setup.

- **67+ Kokoro voices** included
- **Character clones** (Morgan Freeman, Rick & Morty, etc.)
- **Free during alpha** - no credit card required

> **Coming Soon:** API keys and MCP access tokens for [lessfortts.loser.com](https://lessfortts.loser.com). Currently in dev/testing - free access while we build out authentication. Want early access? Email buddy@loser.com.

### Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   AI Client     │────▶│   MCP Server    │────▶│   TTS API       │
│ (Claude, Cline) │     │ (this package)  │     │ (server.py)     │
└─────────────────┘     └─────────────────┘     └─────────────────┘
      speaks              translates              generates
    naturally            to API calls              audio
```

The MCP server is a thin bridge - it translates natural AI tool calls into HTTP requests to your TTS API. The API handles chunking, stitching, and format conversion.

## Documentation

- **[Complete Tutorial](COMPLETE_TUTORIAL.md)** - Zero to audiobook in 15 minutes
- **[User Guide](STUDIO_USER_GUIDE.md)** - Full Studio features and workflows
- **[FAQ](FAQ.md)** - Common questions and troubleshooting
- **[Architecture](ARCHITECTURE.md)** - Backend design and integration
- **[Roadmap](ROADMAP.md)** - Upcoming features (chapter management, AI tools, etc.)
- **[Demo Script](DEMO_RECORDING_SCRIPT.md)** - For creating video tutorials

## Features

### v0.1 (Current Release)
- ✅ Multi-speaker script editor with auto-detection
- ✅ Searchable voice dropdowns (type to filter)
- ✅ Multiple TTS backend support
- ✅ Smart chunking for unlimited text
- ✅ Natural 100ms gaps between speakers
- ✅ Backend switcher (Kokoro, VoxCPM, custom)
- ✅ File import (.txt, .pdf)
- ✅ OpenAI-compatible API

### Coming in v0.2
- 📋 Chapter/project management
- 🎬 Batch generation queue
- 📦 Export all chapters at once
- 🎵 Background music support
- See [ROADMAP.md](ROADMAP.md) for full list

## Comparison

| Feature | Open TTS Studio | ElevenLabs | Coqui TTS |
|---------|----------------|------------|-----------|
| **Cost** | Free | $5-330/month | Free |
| **Multi-speaker UI** | ✅ Built-in | ❌ Manual | ❌ Code only |
| **Unlimited length** | ✅ Auto-chunked | ❌ Limits | ⚠️ Manual chunking |
| **Local/Private** | ✅ Your hardware | ❌ Cloud | ✅ Your hardware |
| **Voice variety** | 67+ (backend-dependent) | 100+ | DIY training |
| **Ease of use** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ |

## Advanced Use Cases

**For developers:** Need multi-backend routing, voice preferences, and production features? See [open-unified-tts](https://github.com/loserbcc/open-unified-tts) - the full API gateway.

**For enterprise:** Run multiple Studio instances, integrate with your workflow, custom backends.

**For educators:** Create multi-voice learning materials, language lessons, interactive content.

**For podcasters:** Script → Audio in minutes. Multiple hosts, consistent voices.

## Contributing

We're just getting started! Ways to help:

- ⭐ **Star the repo** if you find it useful
- 🐛 **Report bugs** in Issues
- 💡 **Request features** in Discussions
- 📝 **Improve docs** - PRs welcome!
- 🎨 **Share your creations** - Show us what you made!
- 🤝 **Write code** - See [ROADMAP.md](ROADMAP.md) for ideas

## Need Custom Features?

Want something specific for your workflow? Need help integrating this into your pipeline?

**We love building cool stuff!** 🛠️

Email us at **buddy@loser.com** - we'll try to make you happy. That's what we do. :)

## Support the Project

If Open TTS Studio has helped you, consider buying us a coffee! ☕

**Donations welcome:**
- **Bitcoin (BTC):** `151gWJHmr1Gwd9kmCURXCgrMFF7kAoDuP4`
- **Ethereum (ETH):** `0x4A24bAEd9c8aD61eF245CCAE38504eBe882dd334`
- **Monero (XMR):** `49kKhbDzpmwY6mTXcZLzX9VvhkriLmbdsMLGuo3NkabWCPn8yfEL3FLJfLqovnQxVe3aoQXRWtNve5TuQLG7NL5qL62HWxu`

Every donation helps keep the servers running and motivates us to build more awesome features!

Or just ⭐ **star the repo** - that makes us happy too!

## Community

- **GitHub Discussions** - Questions, ideas, show & tell
- **Issues** - Bug reports and feature requests

## License

Apache 2.0 - Use commercially, modify freely, just maintain the license notice.

## Credits

Built with:
- [Gradio](https://gradio.app/) - Web UI framework
- [Kokoro](https://huggingface.co/hexgrad/Kokoro-82M) - CPU-friendly TTS
- [VoxCPM](https://github.com/thuhcsi/VoxCPM) - Voice cloning
- Community contributors - Thank you!

---

**Made with ❤️ by the open-source TTS community**

[⭐ Star this repo](https://github.com/loserbcc/open-tts-studio) • [🐛 Report Bug](https://github.com/loserbcc/open-tts-studio/issues) • [💡 Request Feature](https://github.com/loserbcc/open-tts-studio/discussions)
