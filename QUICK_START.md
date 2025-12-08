# 60-Second Quick Start

Get multi-speaker AI audio in one minute flat.

## Prerequisites

- **Docker** installed and running
- **Python 3.10+** with `uv` (or pip)

Don't have uv? Install it: `curl -LsSf https://astral.sh/uv/install.sh | sh`

## Steps

```bash
# 1. Get the code
git clone https://github.com/loserbcc/open-tts-studio.git
cd open-tts-studio

# 2. Start TTS backend (Kokoro - 67 voices, CPU-friendly)
docker compose -f docker-compose.kokoro.yml up -d

# 3. Start Studio
uv sync && uv run python studio_v2.py

# 4. Open http://localhost:7860 in your browser

# 5. In the Studio, paste this test script:
# Rick: Testing, testing. Is this thing on?
# Morty: Oh geez Rick, I think it's working!

# 6. Click "Auto-Detect Speakers"
# 7. Click "Generate Production"
```

**Done!** You just made multi-speaker audio.

## What Just Happened?

1. **Docker container** - Downloaded and started Kokoro TTS (the AI that generates voices)
2. **Studio interface** - Launched a web UI at http://localhost:7860
3. **Auto-detection** - Studio found "Rick" and "Morty" as speakers in your script
4. **Voice assignment** - You can now pick voices from 67 options for each speaker
5. **Generation** - Studio split your text into chunks, generated each part, and stitched them together seamlessly

## Next Steps

### Try Different Voices

1. Click on the voice dropdown for "Rick"
2. Start typing to search (try "american" or "british")
3. Pick a voice you like
4. Click "Generate Production" again

### Import a Longer Script

1. Go to **Import Tools** tab
2. Upload a .txt or .pdf file
3. Or paste a longer script
4. Studio handles unlimited length automatically

### Learn More Features

- **Settings Tab** - Switch backends, configure API endpoints
- **Voice search** - Type partial names to filter (e.g., "fem" shows all female voices)
- **Speaker gaps** - Adjust silence between speakers
- **File export** - Download your production as MP3

See [STUDIO_USER_GUIDE.md](STUDIO_USER_GUIDE.md) for all features.

## Common Issues

### "Connection refused" when starting Studio

**Fix:** Make sure the Docker container is running:
```bash
docker ps | grep kokoro
```

Should show a running container. If not:
```bash
docker compose -f docker-compose.kokoro.yml up -d
```

### "No voices available"

**Fix:** Backend hasn't finished starting. Wait 30 seconds and refresh the page.

Check backend health:
```bash
curl http://localhost:8766/v1/voices
```

Should return a JSON list of voices.

### Studio won't start - "Address already in use"

**Fix:** Port 7860 is taken. Either:

1. Stop the other service using port 7860, or
2. Use a different port:
```bash
uv run python studio_v2.py --server-port 7861
```

Then open http://localhost:7861

### Audio has gaps or sounds wrong

**Fix:** This is usually a chunking issue. Try:

1. Use shorter paragraphs in your script
2. Check that the backend is running smoothly: `docker logs <container-id>`
3. Regenerate - sometimes it's just a one-off issue

## Different Backend Options

### Kokoro (Default - Recommended)

- **67 voices** (American, British, OpenAI-style)
- **CPU-friendly** - No GPU needed
- **Fast** - Generates in near real-time
- **Start:** `docker compose -f docker-compose.kokoro.yml up -d`

### VoxCPM (Voice Cloning)

- **Unlimited voices** - Upload a sample, clone any voice
- **GPU required** - Needs NVIDIA GPU with 6GB+ VRAM
- **Slower** - Takes longer to generate
- **Start:** `docker compose -f docker-compose.voxcpm.yml up -d`

After starting VoxCPM, go to Settings tab and select "VoxCPM" as backend.

## API-Only Mode (No Web Interface)

If you just need the OpenAI-compatible API:

```bash
# 1. Start backend
docker compose -f docker-compose.kokoro.yml up -d

# 2. Start API server (not Studio)
uv run python server.py

# 3. Use the API
curl -X POST http://localhost:8765/v1/audio/speech \
  -H "Content-Type: application/json" \
  -d '{"input":"Hello world","voice":"af_bella"}' \
  -o hello.mp3
```

See [MCP_GUIDE.md](MCP_GUIDE.md) for Claude integration.

## What's Next?

- **[Complete Tutorial](COMPLETE_TUTORIAL.md)** - Detailed walkthrough with examples
- **[Studio User Guide](STUDIO_USER_GUIDE.md)** - All features explained
- **[FAQ](FAQ.md)** - Troubleshooting and tips
- **[Roadmap](ROADMAP.md)** - Upcoming features

## Need Help?

- **Issues:** https://github.com/loserbcc/open-tts-studio/issues
- **Email:** buddy@loser.com

---

**Made it through in 60 seconds?** Give us a ⭐ on [GitHub](https://github.com/loserbcc/open-tts-studio)!
