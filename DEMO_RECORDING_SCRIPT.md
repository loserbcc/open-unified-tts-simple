# Demo Recording Script

## Video Structure (Total: ~12-15 minutes)

### Intro (30 seconds)
- Title card: "[Project Name] - Multi-Speaker TTS Production Studio"
- Tagline: "From script to audiobook in minutes. Free. Open source."
- Quick preview of final result playing

### Part 1: Installation (3 minutes)

**Terminal Recording:**

```bash
# Scene: Clean terminal, show commands
# Narration: "Let's start from zero. First, clone the repository."

git clone https://github.com/loserbcc/open-unified-tts-simple.git
cd open-unified-tts-simple

# Narration: "Start Kokoro TTS with a single command."
docker compose -f docker-compose.kokoro.yml up -d

# Narration: "In under a minute, we have 67 AI voices ready to go."
# Wait for docker to finish

# Show it's working
curl http://localhost:8766/v1/voices | jq -r '.voices[:10][]'

# Narration: "Perfect! Now let's start the Studio interface."
uv run python studio_v2.py
```

**Cut to browser as it starts**

### Part 2: Configuration (2 minutes)

**Browser Recording - Settings Tab:**

1. **Show Settings tab**
   - Narration: "The Studio auto-detects our backend, but let's configure it properly."

2. **Fill in settings** (speed up with editing):
   - Backend Name: "Kokoro Local"
   - URL: http://localhost:8766
   - Profile: balanced
   - Max Words: 75

3. **Click Save**
   - Narration: "It found 67 voices. We're ready to create."

### Part 3: First Production (4 minutes)

**Browser Recording - Studio Tab:**

1. **Paste script:**
   ```
   Narrator: Welcome to our audiobook creation tutorial.
   Alice: Hi! I'm Alice, and I'll show you how easy this is.
   Bob: And I'm Bob. Let's make something amazing together.
   ```

2. **Click Auto-Detect Speakers**
   - Narration: "The Studio automatically detects our three speakers."
   - Show the three rows appearing

3. **Assign voices** (show typing to search):
   - Narrator → type "adam" → select am_adam
   - Alice → type "bella" → select af_bella
   - Bob → type "michael" → select am_michael
   - Narration: "Just type to search through voices. Super fast."

4. **Click Generate**
   - Show status messages appearing
   - Narration: "Watch as each line gets generated and stitched together."

5. **Play result**
   - Narration: "And there we have it - professional multi-speaker audio in under a minute."
   - Let audio play through

### Part 4: Real Example - Audiobook Chapter (5 minutes)

**Browser Recording:**

1. **Clear editor, paste Frankenstein excerpt:**
   ```
   Narrator: It was on a dreary night of November that I beheld the accomplishment of my toils.
   Victor: With an anxiety that almost amounted to agony, I collected the instruments of life.
   Narrator: It was already one in the morning. The rain pattered dismally against the panes.
   Victor: By the glimmer of the half-extinguished light, I saw the dull yellow eye of the creature open.
   ```

2. **Auto-detect → 2 speakers**
   - Narration: "Let's try something more ambitious - Chapter 5 of Frankenstein."

3. **Assign voices:**
   - Narrator → am_adam
   - Victor → am_eric (more emotional)
   - Narration: "Choosing voices that match the character's emotions."

4. **Generate and play**
   - Narration: "Listen to how natural the pacing is between speakers."
   - Play full audio

5. **Switch voices to show flexibility:**
   - Change to British voices: bm_george, bm_daniel
   - Regenerate
   - Narration: "Don't like how it sounds? Try different voices instantly."
   - Play new version

### Part 5: Advanced Features (2 minutes)

**Quick montage showing:**

1. **File import:**
   - Show uploading a .txt file
   - Auto-loads into editor
   - Narration: "Import from files, PDFs, even web pages."

2. **Searchable voices:**
   - Type in dropdown, show filtering
   - Narration: "67 voices, but you can find the right one in seconds."

3. **Multiple backends:**
   - Quick Settings screen showing VoxCPM option
   - Narration: "Works with any TTS backend. Kokoro, custom voice clones, even cloud APIs."

### Outro (1 minute)

**Split screen: Code + Browser:**

- Show GitHub repo
- Narration: "Everything you saw is free and open source."
- Show key features as text overlay:
  - ✅ Unlimited text length
  - ✅ 67+ voices (Kokoro)
  - ✅ Custom voice cloning (VoxCPM)
  - ✅ No cloud, no costs
  - ✅ OpenAI-compatible API
  - ✅ Docker one-command install

- End card:
  - GitHub: github.com/loserbcc/open-unified-tts-simple
  - "Star ⭐ | Fork 🔱 | Contribute 🚀"
  - "Join us in making TTS accessible to everyone"

---

## Technical Recording Setup

### Required Tools

**Terminal recording:**
- [asciinema](https://asciinema.org/) for terminal
- Or OBS for full desktop capture

**Browser recording:**
- OBS Studio (free, cross-platform)
- Or Chrome built-in screen recorder

**Audio:**
- Studio-generated audio (for examples)
- Voice-over narration (your voice or TTS)

**Editing:**
- DaVinci Resolve (free)
- Or iMovie / OpenShot

### Recording Checklist

**Before recording:**
- [ ] Clean terminal (clear history)
- [ ] Clean browser (close tabs, hide bookmarks)
- [ ] Set terminal font size to 18-20pt
- [ ] Set browser zoom to 125-150%
- [ ] Disable notifications
- [ ] Test audio levels

**Terminal recording:**
```bash
# Use asciinema for clean terminal recording
asciinema rec demo_part1_install.cast

# Or set up OBS with:
# - Resolution: 1920x1080
# - FPS: 30
# - Terminal window: Maximize or make prominent
```

**Browser recording:**
```bash
# OBS settings:
# - Browser window: Full screen or maximized
# - Crop to app, not entire desktop
# - Highlight mouse cursor
# - Add zoom effects in editing for important UI elements
```

### Narration Script (Voice-over)

**Intro (30s):**
> "Creating audiobooks used to require expensive software or cloud services. Not anymore. Today I'll show you how to create professional multi-speaker audio productions completely free, running on your own machine. From zero to finished audiobook in 15 minutes. Let's go."

**Installation (30s):**
> "Starting from scratch. Clone the repo. One docker command starts the TTS backend with 67 voices. No GPU required. Install the Studio interface with uv or pip. In under two minutes, we're ready to create."

**Configuration (30s):**
> "The Studio auto-detects our TTS backend. We'll configure it with sensible defaults - balanced profile, 75 words max. Save settings and it connects to 67 voices instantly."

**First Production (1m):**
> "Let's create our first multi-speaker production. Write a simple script - three speakers having a conversation. Click auto-detect and the Studio finds all speakers. Assign voices by typing to search - much faster than scrolling. Hit generate and watch the magic happen. Each line gets converted to speech, then stitched together with natural pacing. Play the result and you'll hear professional quality multi-speaker audio."

**Audiobook Example (1m 30s):**
> "Now something more ambitious - a real audiobook chapter. Chapter 5 of Frankenstein. Paste the text formatted as narrator and character. Auto-detect finds our two speakers. Choose voices that match the mood - a clear narrator and an emotional voice for Victor. Generate and listen. Notice the natural pacing, the emotion, the professional quality. Don't like it? Switch voices instantly and regenerate. Try British voices for a different feel. This is the power of the Studio - experiment freely."

**Advanced Features (45s):**
> "Beyond the basics: Import from files or PDFs. Search through 67 voices in real-time. Switch between backends - use Kokoro for variety or VoxCPM for custom voice clones. It even works with cloud APIs if you want. OpenAI-compatible, so it integrates with your favorite tools."

**Outro (45s):**
> "Everything you saw is free and open source. No subscriptions, no cloud costs, no limits. Create audiobooks, podcasts, educational content - whatever you imagine. The project is on GitHub - star it, fork it, make it yours. We're building this together, making professional TTS accessible to everyone. Thanks for watching, and I can't wait to hear what you create."

---

## Editing Checklist

**Post-production:**
- [ ] Add title cards between sections
- [ ] Zoom in on important UI elements (buttons, dropdowns)
- [ ] Speed up Docker downloads (2x or skip)
- [ ] Add arrows/circles highlighting key features
- [ ] Include generated audio examples
- [ ] Add background music (subtle, royalty-free)
- [ ] Color grade for consistency
- [ ] Add subtitles/captions

**Key moments to emphasize:**
1. Single docker command (show how easy)
2. Voice search/filtering (show typing)
3. Auto-detect speakers (show it working)
4. Generated audio playing (full quality)
5. Voice switching (show flexibility)

**Pacing:**
- Don't rush - let viewers see actions clearly
- Pause after each major step
- Let audio examples play fully
- Use jump cuts to remove waiting/loading

**Graphics to add:**
- Feature callouts ("Type to Search!", "67 Voices!")
- Comparison chart (vs ElevenLabs, vs cloud services)
- GitHub stars/forks counter
- "100% Free & Open Source" badges

---

## Publishing Checklist

**Video platforms:**
- [ ] YouTube (unlisted first, then public after review)
- [ ] Upload to GitHub repo as release asset
- [ ] Link from README.md

**Accompanying materials:**
- [ ] Link to tutorial docs
- [ ] Link to GitHub repo
- [ ] Sample scripts used in video
- [ ] Timestamps in description

**Video metadata:**

**Title options:**
1. "Create Audiobooks with AI: Free, Open Source, Unlimited"
2. "Multi-Speaker TTS Studio: Zero to Audiobook in 15 Minutes"
3. "Professional Audiobook Creation - No Cloud, No Cost"

**Description template:**
```
Create professional multi-speaker audio productions (audiobooks, podcasts,
dialogues) with this free, open-source TTS Studio.

🎬 Timestamps:
0:00 - Introduction
0:30 - Installation (Kokoro TTS)
3:30 - Studio Setup
5:30 - First Multi-Speaker Production
9:30 - Real Audiobook Example
14:30 - Advanced Features
17:00 - Summary & Resources

✨ Features:
- 67 AI voices (Kokoro) - more with other backends
- Multi-speaker dialogue with auto-detection
- Unlimited text length (auto-chunking)
- OpenAI-compatible API
- Docker one-command install
- Custom voice cloning support

📚 Resources:
- GitHub: [URL]
- Complete Tutorial: [URL to COMPLETE_TUTORIAL.md]
- User Guide: [URL to STUDIO_USER_GUIDE.md]
- FAQ: [URL to FAQ.md]

🆓 100% Free & Open Source (Apache 2.0)

#TTS #AudioBook #OpenSource #AI #VoiceAI #Podcast
```

**Tags:**
tts, text to speech, audiobook, open source, docker, kokoro, ai voice,
multi-speaker, podcast, free software, voice cloning, python, gradio

---

## Promotion Strategy

**Where to share:**
1. **Reddit**:
   - r/MachineLearning
   - r/LocalLLaMA
   - r/SelfHosted
   - r/AudioProduction
   - r/Podcasting

2. **Social media**:
   - Twitter/X with demo GIF
   - LinkedIn article
   - Mastodon

3. **Communities**:
   - Hacker News "Show HN:"
   - ProductHunt launch
   - IndieHackers

4. **Cross-reference**:
   - Link from main open-unified-tts repo
   - Mention in Kokoro community
   - Share in TTS Discord servers

**Post template:**
```
🎙️ I built a free, open-source multi-speaker TTS Studio

Create audiobooks, podcasts, or any multi-speaker audio with:
- 67 AI voices (CPU-friendly Kokoro)
- Easy web interface
- Unlimited text length
- One docker command to start

Perfect for beginners who found the main project too complex.
Simple, focused, gets the job done.

Demo video: [URL]
Try it: [GitHub URL]

Feedback welcome! Still in beta, open to contributors.
```

---

## Filming Schedule

**Day 1: Record**
- Morning: Terminal sequences
- Afternoon: Browser recordings
- Evening: Narration voice-over

**Day 2: Edit**
- Morning: Rough cut assembly
- Afternoon: Add graphics, effects
- Evening: Color grade, sound mix

**Day 3: Review & Publish**
- Morning: Final review, corrections
- Afternoon: Render, upload unlisted
- Evening: Test on different devices, publish public

---

**Ready to film?** Set up your recording tools and let's make an awesome demo! 🎬
