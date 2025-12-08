# Complete A-Z Tutorial: Zero to Audiobook in 15 Minutes

## What We'll Build

By the end of this tutorial, you'll have:
- ✅ Kokoro TTS backend running (67 voices, CPU-friendly)
- ✅ Production Studio web interface
- ✅ A complete multi-speaker audio production

**Time:** ~15 minutes
**Cost:** $0 (everything is open source)
**Requirements:** Docker installed

---

## Part 1: Install Kokoro TTS Backend (5 minutes)

### Step 1: Get the Code

```bash
# Clone the repository
git clone https://github.com/loserbcc/open-tts-studio.git
cd open-tts-studio
```

### Step 2: Start Kokoro with Docker

```bash
# Single command to start Kokoro
docker compose -f docker-compose.kokoro.yml up -d
```

**What this does:**
- Downloads Kokoro model (~2GB)
- Starts TTS service on port 8766
- Runs in background (detached mode)

### Step 3: Verify Kokoro is Running

```bash
# Check container status
docker ps | grep kokoro

# Test the API
curl http://localhost:8766/v1/voices | jq -r '.voices[:5][]'
```

**Expected output:**
```
af_alloy
af_aoede
af_bella
af_heart
af_jadzia
```

✅ **Checkpoint:** You should see 67 voices available!

---

## Part 2: Install the Studio (2 minutes)

### Step 1: Install Python Dependencies

```bash
# Using uv (recommended - faster)
uv sync

# Or using pip
pip install -r requirements.txt
```

### Step 2: Start the Studio

```bash
# Start the web interface
uv run python studio_v2.py

# Or with pip
python studio_v2.py
```

**What you'll see:**
```
Running on local URL:  http://127.0.0.1:7860
Running on public URL: https://xxxxx.gradio.live
```

### Step 3: Open in Browser

Open: **http://localhost:7860**

✅ **Checkpoint:** You should see the Studio interface with 3 tabs: Studio, Import Tools, Settings

---

## Part 3: Configure the Studio (2 minutes)

### Step 1: Go to Settings Tab

Click on **"Settings"** tab at the top.

### Step 2: Enter Kokoro Configuration

Fill in these values:

| Field | Value |
|-------|-------|
| **Backend Name** | `Kokoro Local` |
| **TTS API URL** | `http://localhost:8766` |
| **Output Directory** | `/path/to/your/output` (or leave default) |
| **Profile** | `balanced` |
| **Max Words** | `75` |
| **Optimal Chunk** | `50` |

### Step 3: Save Settings

Click **"💾 Save Settings"** button.

**Expected result:**
```
✅ Settings saved & switched to: Kokoro Local

TTS: http://localhost:8766
Profile: balanced (75 words)

🎤 Found 67 voices: af_alloy, af_aoede, af_bella, af_heart, af_jadzia... (+62 more)

⚠️ Go to Studio tab and click '🔍 Auto-Detect Speakers' to refresh voice dropdowns!
```

✅ **Checkpoint:** Settings saved, backend connected!

---

## Part 4: Create Your First Production (6 minutes)

### Step 1: Write a Script

Go to **"Studio"** tab.

Paste this sample script in the **Script Editor**:

```
Narrator: Welcome to our tutorial on creating audiobooks with AI voices.
Alice: Hi everyone! I'm Alice, and I'm excited to show you how easy this is.
Bob: And I'm Bob. Together, we'll walk you through the process step by step.
Narrator: First, let's talk about what makes this tool special.
Alice: It can handle multiple speakers, like a real conversation.
Bob: And it's completely free and open source!
Narrator: Let's see it in action.
```

### Step 2: Detect Speakers

Click **"🔍 Auto-Detect Speakers"** button.

**What happens:**
- Studio scans your script
- Finds 3 speakers: Narrator, Alice, Bob
- Shows 3 voice assignment rows

**Detected Speakers display:**
```
Narrator, Alice, Bob
```

### Step 3: Assign Voices

For each speaker, click the voice dropdown and **type to search**:

| Speaker | Suggested Voice | Why |
|---------|----------------|-----|
| **Narrator** | `am_adam` | Male American narrator voice |
| **Alice** | `af_bella` | Female American voice |
| **Bob** | `am_michael` | Different male voice than narrator |

**How to search:**
1. Click in "Voice" dropdown
2. Type "adam" → filters to voices with "adam"
3. Select `am_adam`
4. Repeat for other speakers

✅ **Checkpoint:** All 3 speakers have voices assigned!

### Step 4: Generate Production

1. Select **Output Format:** MP3 (default is fine)
2. Click **"🎬 Generate Production"** button

**What happens:**
- Studio generates audio for each line
- Stitches segments together with 100ms gaps
- Shows progress in Status Messages
- Displays audio player when done

**Expected status:**
```
Generating multi-speaker audio production...

✅ Narrator (am_adam): "Welcome to our tutorial..."
✅ Alice (af_bella): "Hi everyone! I'm Alice..."
✅ Bob (am_michael): "And I'm Bob..."
✅ Narrator (am_adam): "First, let's talk..."
✅ Alice (af_bella): "It can handle multiple speakers..."
✅ Bob (am_michael): "And it's completely free..."
✅ Narrator (am_adam): "Let's see it in action."

Generated: /path/to/output/production_12345.mp3
```

### Step 5: Listen to Your Production

Click ▶️ Play in the audio player!

✅ **Checkpoint:** You should hear all 3 speakers with natural pacing!

---

## Part 5: Create a Real Audiobook Chapter (Bonus)

Now let's try something more substantial - a chapter from a real book!

### Step 1: Get Some Book Text

We'll use a public domain book. Here's Chapter 5 from Frankenstein:

```
Narrator: It was on a dreary night of November that I beheld the accomplishment of my toils.
Victor: With an anxiety that almost amounted to agony, I collected the instruments of life around me.
Narrator: It was already one in the morning. The rain pattered dismally against the panes.
Victor: My candle was nearly burnt out, when, by the glimmer of the half-extinguished light, I saw the dull yellow eye of the creature open.
Narrator: It breathed hard, and a convulsive motion agitated its limbs.
Victor: How can I describe my emotions at this catastrophe? How delineate the wretch whom I had endeavored to form?
Narrator: His limbs were in proportion, and I had selected his features as beautiful.
Victor: Beautiful! Great God! His yellow skin scarcely covered the work of muscles beneath.
```

### Step 2: Import and Generate

1. Paste the script in Script Editor
2. Click "Auto-Detect Speakers" → finds Narrator and Victor
3. Assign voices:
   - **Narrator**: `am_adam` (neutral, clear)
   - **Victor**: `am_eric` (emotional, intense)
4. Click "Generate Production"
5. Listen to your audiobook chapter!

### Step 3: Try Different Voices

Experiment with different voice combinations:

**Gothic/Dark atmosphere:**
- Narrator: `bm_george` (British male, authoritative)
- Victor: `am_eric` (American male, distressed)

**Modern/Accessible:**
- Narrator: `af_sarah` (Female narrator, warm)
- Victor: `am_adam` (Male, clear)

**Dramatic:**
- Narrator: `bf_emma` (British female, theatrical)
- Victor: `bm_daniel` (British male, intense)

✅ **Checkpoint:** You've created a professional audiobook chapter!

---

## Part 6: Production Workflow Tips

### Writing Scripts for Best Results

**Format:**
```
Speaker: Their dialogue here.
```

**Best practices:**
1. **One thought per line** - Don't make lines too long
2. **Natural breaks** - Split at sentence boundaries
3. **Consistent names** - Same speaker = same spelling
4. **Punctuation matters** - Periods, commas affect pacing

**Example - Good:**
```
Alice: I can't believe it's working!
Bob: I know, right?
Alice: This is amazing.
```

**Example - Avoid:**
```
Alice: I can't believe it's working! I know, right? This is amazing.
```

### Voice Selection Guide

**Kokoro Voice Naming:**

| Prefix | Gender | Accent | Examples |
|--------|--------|--------|----------|
| `af_` | Female | American | af_bella, af_sarah, af_nova |
| `am_` | Male | American | am_adam, am_michael, am_eric |
| `bf_` | Female | British | bf_emma, bf_alice, bf_lily |
| `bm_` | Male | British | bm_george, bm_daniel, bm_lewis |

**Use case matching:**

| Content Type | Voice Suggestions |
|-------------|-------------------|
| Narrator (male) | am_adam, am_michael, bm_george |
| Narrator (female) | af_sarah, bf_emma |
| Young female | af_bella, af_nova, bf_alice |
| Young male | am_eric, bm_lewis |
| Authority figure | bm_george, am_michael |
| Warm/friendly | af_sarah, af_bella |

### Keyboard Shortcuts

| Action | Shortcut |
|--------|----------|
| Generate | Ctrl/Cmd + Enter |
| Save Settings | Ctrl/Cmd + S |
| Refresh Page | F5 |

### Quality Optimization

**For best audio quality:**

1. **Keep lines reasonable** - Under 200 words per line
2. **Use punctuation** - Helps with pacing and intonation
3. **Test voices first** - Try single lines before full production
4. **Consistent backend** - Don't switch mid-project
5. **Export format** - MP3 for sharing, WAV for editing

**If audio sounds wrong:**
- Try shorter segments
- Different voice
- Regenerate (sometimes helps)
- Check backend is responding

---

## Part 7: Advanced Workflows

### Batch Production

**For multiple chapters:**

1. Save each chapter as separate script file
2. Generate one at a time
3. Name outputs clearly: `chapter_01.mp3`, `chapter_02.mp3`
4. Can concatenate later with audio editor

### Using Multiple Backends

**Set up VoxCPM for custom voices:**

```bash
# Start VoxCPM (requires GPU)
docker compose -f docker-compose.voxcpm.yml up -d
```

**Switch between backends:**
1. Go to Settings
2. Change TTS API URL to `http://localhost:7870`
3. Save settings
4. Click "Auto-Detect Speakers" to refresh voices

**Best of both worlds:**
- Kokoro for variety and narrator
- VoxCPM for specific character voices

### Exporting for Distribution

**Podcast distribution:**
1. Generate as MP3
2. Add metadata with audio editor
3. Upload to podcast host

**Audiobook distribution:**
1. Generate all chapters
2. Combine with Audacity or ffmpeg
3. Export as single file or chaptered m4b

**Video narration:**
1. Generate narration
2. Import to video editor
3. Sync with visuals

---

## Troubleshooting Common Issues

### Issue: "Connection refused" when generating

**Fix:**
```bash
# Check Kokoro is running
docker ps | grep kokoro

# Restart if needed
docker compose -f docker-compose.kokoro.yml restart
```

### Issue: No voices in dropdowns

**Fix:**
1. Check Settings → TTS API URL is correct
2. Test: `curl http://localhost:8766/v1/voices`
3. Click "Auto-Detect Speakers" again
4. Refresh browser (F5)

### Issue: Audio sounds choppy

**Fix:**
- Normal 100ms gaps between speakers is expected
- If gaps within speech, try shorter sentences
- Or try different voice

### Issue: JavaScript errors in console

**Usually harmless!** But if broken:
1. Refresh page (F5)
2. Clear cache (Ctrl+Shift+R)
3. Try different browser

### Issue: Generation is slow

**Expected times:**
- Kokoro: 1-2 seconds per sentence
- Longer for first generation (model loading)
- Multiple speakers = multiple segments = longer

**Speed up:**
- Use "fast" profile in Settings
- Reduce text for testing
- Ensure nothing else using CPU/GPU

---

## What's Next?

### Experiment with Features

1. **Try all 67 voices** - Find your favorites
2. **Import PDFs** - Extract book text automatically
3. **Use AI tools** - Expand dialogue with LM Studio
4. **Multiple backends** - Compare Kokoro vs VoxCPM

### Create Real Content

1. **Audiobook** - Convert your favorite public domain book
2. **Podcast** - Create multi-host discussions
3. **Educational** - Make learning materials
4. **Stories** - Bring your stories to life

### Advanced Setup

1. **Voice cloning** - Add custom voices with VoxCPM
2. **Network setup** - Run Studio on one machine, TTS on another
3. **Docker optimization** - Configure resource limits
4. **Production workflow** - Create templates and presets

### Join the Community

1. **Share your creations** - Show what you made!
2. **Report bugs** - Help improve the project
3. **Request features** - What do you need?
4. **Contribute** - It's open source!

---

## Quick Reference Card

### Essential Commands

```bash
# Start Kokoro backend
docker compose -f docker-compose.kokoro.yml up -d

# Stop Kokoro backend
docker compose -f docker-compose.kokoro.yml down

# Start Studio
uv run python studio_v2.py

# Test backend
curl http://localhost:8766/v1/voices

# View logs
docker logs -f kokoro
```

### Script Format

```
SpeakerName: What they say
AnotherSpeaker: Their response
```

### Best Voice Combos

| Use Case | Voices |
|----------|--------|
| Male + Female | am_adam + af_bella |
| Two Males | am_adam + am_michael |
| Two Females | af_sarah + af_nova |
| British Duo | bm_george + bf_emma |
| Narrator + Character | am_adam + af_bella |

### Settings Reference

| Setting | Kokoro | VoxCPM |
|---------|--------|--------|
| URL | localhost:8766 | localhost:7870 |
| Profile | balanced | balanced |
| Max Words | 75 | 100 |
| Optimal Chunk | 50 | 75 |

---

## Success Checklist

- ✅ Kokoro backend running
- ✅ Studio interface accessible
- ✅ Settings configured
- ✅ Sample script generated successfully
- ✅ Multiple voices tested
- ✅ Audio sounds natural
- ✅ Ready for real projects!

**Congratulations!** You're now ready to create professional multi-speaker audio productions. 🎉

---

**Need help?** Check [FAQ.md](FAQ.md) or [User Guide](STUDIO_USER_GUIDE.md)

**Want to contribute?** See [IMPROVEMENTS.md](IMPROVEMENTS.md) for ideas!
