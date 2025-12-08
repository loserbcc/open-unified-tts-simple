# Frequently Asked Questions (FAQ)

## General Questions

### What is this project?

This is a **TTS Production Studio** - a complete system for creating professional multi-speaker audio content (audiobooks, podcasts, dialogues) using text-to-speech technology. It combines:
- **Backend-agnostic design**: Works with any TTS engine (Kokoro, VoxCPM, etc.)
- **Smart chunking**: Handles unlimited text length
- **Multi-speaker support**: Easy voice assignment for dialogues
- **Web UI**: No command-line needed

### Do I need a GPU?

**Depends on your TTS backend:**
- **Kokoro**: No GPU needed, runs on CPU
- **VoxCPM**: Yes, needs ~8GB VRAM for voice cloning
- **Studio itself**: No GPU needed

### What's the difference between the Studio and the API?

- **API** (server.py): Headless service, OpenAI-compatible endpoints, for integration
- **Studio** (studio_v2.py): Web UI with multi-speaker features, for human users

You can run both at the same time or just use the Studio.

## Installation Questions

### Which backend should I start with?

**For beginners: Kokoro**
- Easy setup (single Docker command)
- No GPU required
- 67 voices ready to use
- Fast generation

**For custom voices: VoxCPM**
- Requires GPU
- Need to provide reference audio
- Better for specific character voices

### Do I need Docker?

**No, but it's recommended.**

With Docker:
```bash
docker compose -f docker-compose.kokoro.yml up -d
```

Without Docker:
```bash
uv run python studio_v2.py
# Then configure to point at your TTS backend
```

### Can I run this on Windows?

**Yes!** Docker Desktop works on Windows. The Studio is web-based, so it works in any browser.

### How much disk space do I need?

- **Studio**: ~100MB (Python + dependencies)
- **Kokoro Docker**: ~2GB (model + container)
- **VoxCPM Docker**: ~8GB (larger model)
- **Generated audio**: Depends on usage (~1MB per minute of audio)

## Usage Questions

### How do I format my script?

Simple format:
```
SpeakerName: What they say
AnotherSpeaker: Their response
```

Rules:
- Each line starts with `SpeakerName:`
- Speaker names are case-sensitive
- Blank lines are ignored
- No special characters needed

### Why can't I see any voices in the dropdowns?

**Common causes:**
1. Backend not running
2. Backend URL incorrect
3. Didn't click "Auto-Detect Speakers"

**Fix:**
1. Check Settings → TTS API URL is correct
2. Test: `curl http://YOUR_URL/v1/voices`
3. Click "Auto-Detect Speakers" button
4. Refresh browser if still empty

### How do I search for voices instead of scrolling?

**Just start typing!** The voice dropdowns are searchable:
1. Click in the dropdown
2. Type part of the voice name (e.g., "adam", "bella")
3. List filters in real-time
4. Select from filtered results

### Why are there gaps between speakers?

**By design!** Speakers are separated by 100ms of silence to make it clear when the speaker changes. This is normal for dialogue.

If you hear gaps *within* a speaker's line, that's a backend issue - try shorter sentences or a different voice.

### Can I use this for audiobooks?

**Yes!** Two approaches:

**Single narrator:**
```
Narrator: Chapter one. It was a dark and stormy night...
Narrator: The protagonist walked into the room...
```

**Multi-character dialogue:**
```
Narrator: She said to him,
Alice: I can't believe you did that.
Bob: I'm sorry, I didn't mean to.
Narrator: He replied sheepishly.
```

### How long can my script be?

**Unlimited!** The system automatically:
1. Splits text at natural sentence boundaries
2. Generates each chunk within backend limits
3. Stitches chunks together seamlessly

Individual lines should be under ~200 words for best quality, but the total script can be any length.

## Technical Questions

### What's the audio quality like?

**Depends on backend:**
- **Kokoro**: Good quality, natural-sounding, synthetic voices
- **VoxCPM**: Excellent quality for short segments, can degrade on very long segments
- **Format**: MP3 (default), WAV, or OGG

Sample rate: Typically 24kHz (Kokoro) or 22.05kHz (VoxCPM)

### Can I use my own voice clones?

**Yes, with VoxCPM backend:**
1. Prepare reference audio (15-30 seconds of clean speech)
2. Add to VoxCPM's `voice_refs` directory
3. Format: `voice_name.wav` + `voice_name.txt` (transcript)
4. Restart VoxCPM container
5. Voice appears in Studio dropdowns

### What backends are supported?

**Currently tested:**
- ✅ Kokoro (67 voices, CPU-friendly)
- ✅ VoxCPM (custom voice cloning)
- ✅ VibeVoice (preset characters)
- ✅ Any OpenAI-compatible TTS API

**Coming soon:**
- OpenAudio
- FishTTS
- ElevenLabs API
- Custom backends

### Can I run multiple backends at once?

**Yes!** Common setup:
1. Kokoro on port 8766 (CPU, always running)
2. VoxCPM on port 7870 (GPU, on-demand)
3. Switch between them in Studio Settings

### How do I integrate with other tools?

The API endpoint (`/v1/audio/speech`) is OpenAI-compatible:
- **OpenWebUI**: Add as TTS provider
- **SillyTavern**: Configure as OpenAI TTS endpoint
- **Any app with OpenAI TTS**: Drop-in replacement

## Troubleshooting

### "Connection refused" error

**Backend not running.** Check:
```bash
# For Docker
docker ps | grep kokoro

# For direct run
curl http://localhost:8766/v1/voices
```

**Fix:**
```bash
# Start Kokoro Docker
docker compose -f docker-compose.kokoro.yml up -d

# Or check if running elsewhere
lsof -i :8766
```

### Voices sound wrong or garbled

**Common causes:**
1. Wrong voice name (case-sensitive)
2. Backend overloaded (too many concurrent requests)
3. Text too complex for the voice

**Fix:**
1. Test voice with simple text first
2. Check voice name exactly matches available voices
3. Try a different voice
4. Reduce text complexity

### Browser shows JavaScript errors

**Usually harmless!** Common after updating many dropdowns.

**Fix:**
1. Refresh page (F5)
2. Clear cache (Ctrl+Shift+R)
3. Errors often don't affect functionality

**If actually broken:**
- Check browser console for real errors
- Try different browser
- Verify Studio is still running

### Generation is slow

**Expected:**
- Kokoro: ~1-2 seconds per sentence
- VoxCPM: ~3-5 seconds per sentence (GPU)
- Long scripts: Time multiplies by number of segments

**Speed it up:**
1. Use "fast" profile in Settings
2. Use Kokoro instead of VoxCPM
3. Reduce text length for testing
4. Ensure backend isn't running other tasks

### Audio has pops or clicks

**Stitching issue.** Usually happens if:
- Backend returns inconsistent audio formats
- Sample rates don't match
- Crossfade failed

**Fix:**
1. Regenerate (sometimes fixes itself)
2. Try different backend
3. Export as WAV instead of MP3
4. Check backend logs for errors

### Can't save settings

**Common causes:**
1. Permissions issue (can't write config file)
2. Invalid JSON in config
3. Backend URL unreachable

**Fix:**
```bash
# Check permissions
ls -la tts_studio_config.json

# Fix permissions
chmod 644 tts_studio_config.json

# Test backend manually
curl http://YOUR_URL/v1/voices
```

## Performance Questions

### How much RAM do I need?

**For Studio:** 500MB-1GB
**For backends:**
- Kokoro: 2-4GB
- VoxCPM: 8-16GB (depends on GPU)

### Can I run this on a Raspberry Pi?

**Yes, but:**
- Studio itself: Fine
- Kokoro CPU: Very slow, but works
- VoxCPM: No (needs GPU)

**Better option:** Run Studio on Pi, point it at TTS backend on another machine.

### How many concurrent users can it handle?

**Studio:** 1 user at a time (single Gradio instance)
**API:** 5-10 concurrent requests (depends on backend)

**For multiple users:**
- Run multiple Studio instances on different ports
- Or use the API endpoint with a load balancer

## Feature Questions

### Can I adjust voice speed or pitch?

**Not currently.** This depends on backend capabilities. Most backends don't expose these controls via the OpenAI-compatible API.

**Workaround:** Post-process with audio editing tools (Audacity, ffmpeg).

### Can I add background music?

**Not in Studio.** Generate TTS first, then mix with music using:
- Audacity (free, easy)
- ffmpeg (command-line)
- Adobe Audition (professional)
- loserbuddy-produce MCP server (if you have it)

### Can I export to video?

**Not directly.** But you can:
1. Generate audio in Studio
2. Use video editor to combine with visuals
3. Or use ffmpeg to add static image

### Is there an API for automation?

**Yes!** The backend runs a full OpenAI-compatible API:

```bash
curl -X POST http://localhost:8765/v1/audio/speech \
  -H "Content-Type: application/json" \
  -d '{"input":"Your text","voice":"af_bella"}' \
  -o output.mp3
```

See README.md for full API docs.

### Can I use AI to write scripts?

**Yes, with LM Studio or Ollama:**
1. Configure AI backend in Settings
2. Use "Expand Dialog" button
3. AI generates additional dialogue

**Or externally:**
- Write script in ChatGPT/Claude
- Copy into Studio
- Generate audio

## Comparison Questions

### How is this different from ElevenLabs?

**ElevenLabs:**
- Cloud service (costs money)
- Excellent quality
- Limited control
- Web interface only

**This Studio:**
- Local/self-hosted (free)
- Multiple backend options
- Full control over everything
- Open source
- Can point to ElevenLabs API if you want!

### How is this different from Coqui TTS?

**Coqui:**
- Just the TTS engine
- API only, no UI for production
- Single-speaker focused

**This Studio:**
- Works WITH Coqui (or any backend)
- Full production UI
- Multi-speaker workflows
- Script management

### What about OpenAI TTS?

**OpenAI TTS:**
- Cloud API (costs per character)
- Excellent quality
- Limited voices

**This Studio:**
- Can use OpenAI as backend!
- Or local alternatives
- Same API format
- Multi-backend flexibility

## Licensing & Distribution

### Can I use this commercially?

**Yes!** Apache 2.0 license allows commercial use.

**But check:**
- Your backend's license (Kokoro, VoxCPM, etc.)
- Voice cloning rights (don't clone people without permission)
- Generated content rights (you own the output)

### Can I modify the code?

**Yes!** Fork it, modify it, distribute it. Apache 2.0 is very permissive.

**Please:**
- Maintain license notice
- Contribute improvements back (optional but appreciated)

### Can I distribute generated audio?

**Yes, you own the generated audio.** But:
- Don't claim the voices are real people
- Respect character/brand trademarks if using recognizable voices
- Check local laws about synthetic voices

## Getting Help

### Where do I report bugs?

**GitHub Issues:** [github.com/loserbcc/open-tts-studio/issues](https://github.com/loserbcc/open-tts-studio/issues)

Include:
- What you expected
- What actually happened
- Steps to reproduce
- Browser console errors (F12)
- Backend logs if relevant

### Where can I ask questions?

**GitHub Discussions:** For questions, tips, and community help

### How do I request features?

**GitHub Issues** with tag "feature request"

See `IMPROVEMENTS.md` for planned features - your idea might already be on the list!

### Is there a Discord/Slack?

**Not yet!** For now, use GitHub Discussions.

---

**Still have questions?** Check the [User Guide](STUDIO_USER_GUIDE.md) or [Architecture docs](ARCHITECTURE.md)!
