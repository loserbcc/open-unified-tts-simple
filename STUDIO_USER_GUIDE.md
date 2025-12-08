# Studio User Guide - Multi-Speaker TTS Production Interface

## What is the Studio?

The **TTS Production Studio** is a web-based interface for creating professional multi-speaker audio productions. Think podcast episodes, audiobook chapters, or character dialogues - all generated from a simple script format.

## Quick Start (3 Steps)

### 1. Start the Studio

```bash
cd /path/to/open-unified-tts-simple
uv run python studio_v2.py
```

Open your browser to: **http://localhost:7860**

### 2. Configure Your TTS Backend

**Option A: Auto-detect (recommended)**
1. Go to **Settings** tab
2. Click **🔍 Auto-Detect Backends**
3. Select a detected backend
4. Click **Save Settings**

**Option B: Manual configuration**
1. Go to **Settings** tab
2. Enter backend details:
   - **Backend Name**: e.g., "Kokoro Local"
   - **TTS API URL**: e.g., `http://localhost:8766`
   - **Profile**: balanced
   - **Max Words**: 75
   - **Optimal Chunk**: 50
3. Click **Save Settings**

### 3. Create Your First Production

1. Go to **Studio** tab
2. Paste or type a script:
   ```
   Rick: Morty, we need to test this system.
   Morty: Oh geez Rick, I don't know about this.
   ```
3. Click **🔍 Auto-Detect Speakers**
4. Assign voices from the dropdowns (type to search!)
5. Click **🎬 Generate Production**
6. Listen to the result in the audio player

---

## Studio Interface Overview

### Tab 1: Studio (Main Production)

This is where the magic happens. The Studio tab has three main sections:

#### Section 1: Script Input
- **Script Editor**: Write or paste your dialogue
  - Format: `Speaker: Their line of dialogue`
  - One speaker per line
  - Blank lines are ignored
- **File Upload**: Import `.txt` or `.pdf` files
  - Automatically loads on selection (no extra clicks!)
- **AI Tools** (optional, requires LM Studio):
  - **Cleanup Format**: Fixes inconsistent speaker labels
  - **Expand Dialog**: AI adds more dialogue before/after

#### Section 2: Voice Assignment
- **Auto-Detect Speakers**: Scans your script for all speaker names
- **Voice Dropdowns**: Assign a voice to each detected speaker
  - **Type to search**: Start typing voice names (e.g., "adam", "bella")
  - Filters in real-time through all available voices
  - Much faster than scrolling!
- **Detected Speakers**: Shows which speakers were found
- **Debug View**: Technical details of voice assignments

#### Section 3: Production
- **Output Format**: Choose MP3 (default), WAV, or OGG
- **Generate Production**: Creates the multi-speaker audio
- **Audio Player**: Play your generated production
- **Status Messages**: Shows progress and any errors

### Tab 2: Import Tools (Advanced)

For importing text from various sources:

- **Plain Text**: Paste text directly
- **PDF Import**: Extract text from PDF files
- **Web Import**: Fetch content from URLs
- **OCR** (if configured): Extract text from images

After importing, the text appears in the Script Editor on the Studio tab.

### Tab 3: Settings

Configure backends and AI tools:

#### TTS Backend Settings
- **Backend Name**: Friendly name for this backend
- **TTS API URL**: Where your TTS service is running
- **Profile**: Performance profile (fast/balanced/high-quality)
- **Max Words**: Maximum words per chunk
- **Optimal Chunk**: Target chunk size for best quality

#### AI Backend Settings (Optional)
- **AI Backend**: LM Studio or Ollama
- **Endpoint**: API URL for AI service
- **Model**: Which model to use for AI features

#### Output Settings
- **Output Directory**: Where generated audio files are saved

---

## Script Format Guide

### Basic Format

```
Speaker1: What they say
Speaker2: Their response
Speaker1: Another line
```

### Rules
1. Each line must start with `SpeakerName:`
2. Speaker names are case-sensitive
3. Blank lines are ignored
4. No special formatting needed

### Example Scripts

**Simple Conversation:**
```
Alice: Hey, how are you doing?
Bob: I'm great, thanks for asking!
Alice: Want to grab lunch?
Bob: Sure, sounds good!
```

**Multi-character with Narrator:**
```
Narrator: It was a dark and stormy night.
Alice: Did you hear that noise?
Bob: It's just the wind.
Narrator: But they were wrong. Very wrong.
Alice: Bob, I'm scared.
```

**Story with Description Lines:**
```
Morgan: Welcome to today's episode.
Morgan: We'll be exploring the mysteries of the universe.
Morgan: First, let's talk about black holes.
Scientist: Black holes are fascinating objects in space.
Morgan: Tell us more about that.
```

---

## Working with Voice Assignments

### Auto-Assignment

When you click **🔍 Auto-Detect Speakers**, the Studio:
1. Scans your script for all unique speaker names
2. Tries to match speaker names to voice names
3. Assigns default voices if no match is found

### Manual Assignment

**Using the searchable dropdowns:**
1. Click in a voice dropdown
2. Start typing the voice name you want
3. List filters in real-time
4. Select from filtered results

**Tips:**
- Type partial names: "ad" shows all voices with "ad" in the name
- For Kokoro: "af_" shows all American female voices
- For custom clones: Type the character name directly

### Voice Matching Examples

| Script Line | Detected Speaker | Suggested Voice |
|------------|------------------|-----------------|
| `Rick: Hello` | Rick | rick (if available in VoxCPM) |
| `Morgan: Welcome` | Morgan | morgan (custom clone) |
| `Narrator: Meanwhile...` | Narrator | am_adam (male narrator voice) |
| `Alice: Hi there` | Alice | af_alice (female voice) |

---

## Multi-Speaker Audio Production

### How It Works

1. **Parse Script**: Extract speaker lines
2. **Generate Segments**: Each line becomes an audio segment
3. **Stitch Together**: Segments joined with 100ms gaps
4. **Export**: Save as your chosen format

### Audio Quality Tips

**For Best Results:**
- Keep individual lines under 200 words
- Use natural sentence breaks
- Avoid extremely long paragraphs
- Test with short scripts first

**Voice Selection:**
- Use distinct voices for different speakers
- Match voice gender/style to character
- Test voices individually first

**Backend Choice:**
- **Kokoro**: Fast, 67 voices, CPU-friendly, good for variety
- **VoxCPM**: Custom clones, GPU-needed, better for specific characters

---

## Switching Between Backends

You can save multiple backends and switch easily:

### Save Multiple Backends

1. **Configure First Backend:**
   - Go to Settings
   - Enter details for Backend 1 (e.g., Kokoro)
   - Click **Save Settings**

2. **Add Second Backend:**
   - Change the settings to Backend 2 (e.g., VoxCPM)
   - Enter new URL and name
   - Click **Save Settings**

3. **Switch Between Them:**
   - Use the **Backend Switcher** dropdown
   - Select the backend you want
   - Click **Switch Backend**
   - Click **Auto-Detect Speakers** to refresh voices

### When to Use Which Backend

| Use Case | Best Backend |
|----------|-------------|
| Quick tests with variety | Kokoro (67 voices) |
| Character voices (Rick, Morty, etc.) | VoxCPM (custom clones) |
| Narrator work | Kokoro (am_adam, am_michael) |
| Podcast-style content | Either, based on voice preference |

---

## Troubleshooting

### Problem: Voices not showing in dropdowns

**Solution:**
1. Make sure backend is running and reachable
2. Check backend URL in Settings is correct
3. Click **🔍 Auto-Detect Speakers** to refresh
4. Refresh browser page if still not working

### Problem: Audio sounds choppy or has gaps

**Solution:**
- Gaps between speakers: This is by design (100ms)
- Gaps within a speaker's line: Backend quality issue, try:
  - Shorter sentences
  - Different voice
  - Different backend

### Problem: Generation fails with error

**Common causes:**
1. Backend not running: Check URL in Settings
2. Voice doesn't exist: Verify voice name is correct
3. Text too long for one chunk: Should auto-chunk, but check backend limits

**Debug steps:**
1. Check Status Messages for error details
2. Test backend directly: `curl http://localhost:8766/v1/voices`
3. Try with single speaker and short text first
4. Check browser console (F12) for JS errors

### Problem: Can't find a voice in dropdown

**Solution:**
- **Type to search!** Click dropdown and start typing
- Voice names are exact-match (case-sensitive)
- For Kokoro: Use prefixes like `af_`, `am_`, `bf_`, `bm_`
- For VoxCPM: Type character name exactly (rick, morty, morgan, etc.)

### Problem: JavaScript errors in browser console

**These are usually harmless** but if things feel broken:
1. Refresh the page (F5)
2. Clear browser cache (Ctrl+Shift+R or Cmd+Shift+R)
3. Try a different browser
4. Check if Studio is still running on the server

---

## Advanced Features

### AI Tools (Optional)

Requires LM Studio or Ollama running:

**Cleanup Format:**
- Fixes inconsistent speaker names
- Standardizes dialogue format
- Removes extra whitespace

**Expand Dialog:**
- Adds AI-generated dialogue
- Choose "before" or "after" current script
- Uses LM Studio/Ollama for generation

**Configuration:**
1. Go to Settings
2. Set AI Backend (LM Studio or Ollama)
3. Enter endpoint URL (e.g., `http://localhost:1234/v1`)
4. Enter model name
5. Save settings

### File Import

**Supported formats:**
- Plain text (.txt)
- PDF documents (.pdf)
- Web pages (via URL)

**Using file import:**
1. Go to Import tab
2. Select import method
3. Upload file or enter URL
4. Content appears in Script Editor
5. Format as speaker dialogue if needed

### Batch Production (Future)

Coming soon: Upload multiple scripts, generate all at once!

---

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| **Ctrl+S** / **Cmd+S** | Save settings (when in Settings tab) |
| **Ctrl+Enter** / **Cmd+Enter** | Generate production (when in Studio tab) |
| **F5** | Refresh page |

---

## Best Practices

### Script Writing

1. **Write naturally**: Don't try to game the TTS
2. **Use punctuation**: Periods, commas help pacing
3. **Short lines**: Better than long paragraphs
4. **Test incrementally**: Start small, build up

### Voice Assignment

1. **Consistent voices**: Same speaker = same voice
2. **Distinct voices**: Different speakers = different voices
3. **Match style**: Match voice to character personality
4. **Test first**: Try voices individually before production

### Production Workflow

1. **Draft script** in external editor
2. **Import** to Studio
3. **Auto-detect speakers**
4. **Assign voices** carefully
5. **Generate** short test
6. **Adjust** if needed
7. **Generate** full production
8. **Save** the output file

---

## Tips & Tricks

### Finding the Right Voice

**Kokoro naming convention:**
- `af_` = American Female (af_bella, af_sarah, af_nova)
- `am_` = American Male (am_adam, am_michael, am_eric)
- `bf_` = British Female (bf_emma, bf_alice, bf_lily)
- `bm_` = British Male (bm_george, bm_daniel, bm_lewis)

**VoxCPM custom clones:**
- Character names: rick, morty, batman, yoda, morgan, picard
- Use exact names (lowercase)

### Speed Up Workflow

1. **Save backend configs** so you can switch quickly
2. **Type to search** in dropdowns instead of scrolling
3. **Auto-detect first**, then adjust manually
4. **Keep test scripts** for different backends
5. **Reuse voice assignments** for similar projects

### Quality Optimization

**For Kokoro:**
- Balanced profile works for most use cases
- Fast profile if you need speed
- High-quality for final productions

**For VoxCPM:**
- Shorter segments = better quality
- May retry generation if quality detection fails
- Check logs if you hear issues

---

## Getting Help

### Resources

- **Architecture docs**: See `ARCHITECTURE.md` for backend design
- **Improvements roadmap**: See `IMPROVEMENTS.md` for planned features
- **Main README**: See `README.md` for API usage

### Support

- **GitHub Issues**: Report bugs or request features
- **Discussions**: Ask questions or share tips

---

**That's it!** You're ready to create professional multi-speaker audio productions with the Studio. Start with a simple two-speaker script and experiment from there. 🎙️
