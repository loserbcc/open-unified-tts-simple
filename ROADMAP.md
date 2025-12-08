# Roadmap - Future Features

## Version 0.0.1 (Current - Alpha Release)

**Status:** ✅ Ready for first release

**What this version is:**
- Alpha quality - core features working, expect rough edges
- For early adopters and feedback
- Full documentation, minimal polish
- "Try this and tell us what you think!"

**Core Features:**
- ✅ Multi-speaker script editor
- ✅ Voice assignment with searchable dropdowns
- ✅ Auto-detect speakers from script
- ✅ Generate production audio with stitching
- ✅ Backend switcher (multiple TTS backends)
- ✅ Settings persistence
- ✅ File import (.txt, .pdf)
- ✅ 100ms gap between speakers

**Documentation:**
- ✅ Complete A-Z tutorial
- ✅ User guide
- ✅ FAQ
- ✅ Demo recording script
- ✅ Architecture docs

---

## Version 0.1.0 - Polish & Stability (Post-feedback)

**Goal:** Take v0.0.1 feedback and polish for wider release

**Status:** 📋 Planned after v0.0.1 feedback

### Improvements Based on Feedback
- [ ] **Bug fixes** from v0.0.1 reports
- [ ] **UI polish** based on user confusion points
- [ ] **Performance** improvements
- [ ] **Screenshots** in documentation
- [ ] **Demo video** recorded and published

### Quality of Life
- [ ] **Better error messages**
- [ ] **Loading indicators** during generation
- [ ] **Progress bars** for long operations
- [ ] **Undo/redo** in script editor
- [ ] **Keyboard shortcuts** documented and working

### Platform Support
- [ ] **Tested on Windows** (Docker Desktop)
- [ ] **Tested on macOS** (Intel + Apple Silicon)
- [ ] **Tested on Linux** (Ubuntu, Arch)
- [ ] **Installation troubleshooting** guide

### Ready for Promotion
- ✅ All critical bugs fixed
- ✅ Smooth installation experience
- ✅ Demo video available
- ✅ Screenshots showing workflow
- ✅ Happy early adopters

**Release target:** After collecting feedback from v0.0.1 users

---

## Version 0.2.0 - Chapter Management (Q1 2025)

**Goal:** Support large audiobook projects with multiple chapters

### Chapter Features
- [ ] **Chapter/Project Manager**
  - Create/manage multiple projects
  - Each project = collection of chapters
  - Project-level voice assignments (consistent across chapters)
  - Project settings (backend, output format, etc.)

- [ ] **Chapter List View**
  - See all chapters in project
  - Status: Not Started / In Progress / Complete
  - Play button for each chapter
  - Reorder chapters (drag & drop)

- [ ] **Batch Generation Queue**
  - Queue multiple chapters for generation
  - Progress indicator (Chapter 3 of 15)
  - Pause/resume generation
  - Background processing (continue editing while generating)

### Chapter Workflow
```
Project: "Frankenstein Audiobook"
├── Chapter 1: "The Beginning" ✅ Complete
├── Chapter 2: "The Letter" ✅ Complete
├── Chapter 3: "The Creature" ⏳ Generating...
├── Chapter 4: "The Chase" 📝 Draft
└── Chapter 5: "The End" ➕ Not Started
```

### Export Options
- [ ] Export single chapter
- [ ] Export all chapters (zip)
- [ ] Combine all into single file
- [ ] Generate chaptered m4b (audiobook format)
- [ ] Add metadata (title, author, narrator)

---

## Version 0.3 - Production Enhancements (Q2 2025)

**Goal:** Professional production features

### Audio Improvements
- [ ] **Configurable gaps between speakers**
  - Slider: 0ms - 500ms
  - Different gaps for different speakers
  - Scene breaks vs dialogue breaks

- [ ] **Background music/ambience**
  - Upload background track
  - Auto-ducking (lowers music when speech plays)
  - Fade in/out at chapter start/end

- [ ] **Sound effects**
  - Add sound effects at specific points
  - Library of common SFX (door, footsteps, etc.)
  - Trigger SFX from script markers

### Voice Enhancements
- [ ] **Voice profiles**
  - Save character + voice pairings
  - Reuse across projects
  - Share voice profiles with community

- [ ] **Voice preview**
  - Hear voice before assigning
  - Quick sample generation
  - Compare voices side-by-side

- [ ] **Emotion/style control** (backend-dependent)
  - Happy, sad, angry, neutral
  - Whisper, shout, normal
  - Speed adjustment (0.5x - 2x)

### Editor Enhancements
- [ ] **Inline editing**
  - Edit generated audio segments
  - Re-generate single line without full rebuild
  - A/B compare different takes

- [ ] **Script templates**
  - Save script formats
  - Templates for common structures
  - Import from template library

- [ ] **Collaboration**
  - Share projects (export/import)
  - Version history
  - Comments/notes on scripts

---

## Version 0.4 - Intelligence & Automation (Q2 2025)

**Goal:** AI-assisted production workflow

### AI Features
- [ ] **Smart voice matching**
  - AI suggests voices based on character description
  - "Young female, British" → suggests bf_alice
  - Learn from your preferences

- [ ] **Script enhancement**
  - AI fixes formatting
  - Suggests better dialogue breaks
  - Detects and fixes inconsistent speaker names

- [ ] **Auto-narration**
  - Convert plain text to script format
  - AI adds narrator lines
  - Dialogue attribution

### Quality Assurance
- [ ] **Audio quality check**
  - Detect issues before listening
  - Flag weird pronunciations
  - Suggest fixes

- [ ] **Consistency check**
  - Same speaker using different voices
  - Character name variations
  - Timeline/continuity issues

---

## Version 0.5 - Professional Tools (Q3 2025)

**Goal:** Feature parity with professional audiobook tools

### Advanced Features
- [ ] **Multi-track editor**
  - Visual timeline of all speakers
  - Drag segments to adjust timing
  - Overlap speakers (interruptions, crosstalk)

- [ ] **Effects & Processing**
  - Noise reduction
  - Normalization
  - Compression/limiting
  - Reverb for scenes

- [ ] **Mastering**
  - Auto-master for distribution
  - Loudness standards (LUFS)
  - Format conversion (mp3, m4b, wav, flac)

### Distribution
- [ ] **Direct upload**
  - Upload to podcast hosts
  - Push to audiobook platforms
  - YouTube video generation

- [ ] **Metadata editor**
  - ID3 tags
  - Cover art
  - Chapter markers
  - ISBN for commercial

---

## Version 1.0 - Production Ready (Q4 2025)

**Goal:** Stable, polished, professional product

### Polish
- [ ] **Performance optimization**
  - Faster generation
  - Better caching
  - Reduced memory usage

- [ ] **UI/UX refinement**
  - Keyboard shortcuts everywhere
  - Dark mode
  - Accessibility (screen readers)

- [ ] **Mobile support**
  - Responsive design
  - Mobile app (PWA)
  - Voice recording on mobile

### Documentation
- [ ] **Video tutorials**
  - Beginner series
  - Advanced techniques
  - Backend integration

- [ ] **Sample projects**
  - Pre-made templates
  - Example audiobooks
  - Voice showcase

### Community
- [ ] **Plugin system**
  - Custom backends
  - Custom effects
  - Community plugins

- [ ] **Marketplace** (optional)
  - Share voice profiles
  - Share templates
  - Share projects

---

## Long-Term Vision (2026+)

### Cloud Features (Optional)
- [ ] **Cloud sync**
  - Save projects to cloud
  - Access from anywhere
  - Team collaboration

- [ ] **Managed hosting**
  - Pay-per-use backend
  - No local setup needed
  - Hybrid: local or cloud

### Advanced AI
- [ ] **Custom voice training**
  - Train new voices in the UI
  - Few-shot voice cloning
  - Voice morphing

- [ ] **Real-time generation**
  - Stream audio as you type
  - Interactive adjustments
  - Live preview

### Ecosystem
- [ ] **API marketplace**
  - Third-party integrations
  - Webhook support
  - Zapier/Make integration

- [ ] **Commercial licensing**
  - Enterprise features
  - Support contracts
  - Custom development

---

## Community Requests

**Vote for features on GitHub Discussions!**

Current top requests:
1. Chapter management (planned v0.2)
2. Background music (planned v0.3)
3. Voice cloning in UI (long-term)
4. Mobile app (v1.0)
5. Collaboration features (v0.4)

**Have an idea?** Open a discussion or issue!

---

## Contributing

Want to help build these features?

**Easy contributions:**
- Documentation improvements
- Bug fixes
- Voice profile sharing
- Tutorial videos

**Medium contributions:**
- UI enhancements
- New import formats
- Backend adapters
- Test automation

**Advanced contributions:**
- Chapter management system
- AI integration
- Performance optimization
- New audio features

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines (coming soon).

---

## Versioning Strategy

**Semantic Versioning:** MAJOR.MINOR.PATCH

- **MAJOR:** Breaking changes (v1.0, v2.0)
- **MINOR:** New features (v0.2, v0.3)
- **PATCH:** Bug fixes (v0.1.1, v0.1.2)

**Release Cycle:**
- Patch releases: As needed (bug fixes)
- Minor releases: Quarterly (new features)
- Major releases: Yearly (major milestones)

**Beta/Alpha:**
- Features marked `[Beta]` are experimental
- Features marked `[Alpha]` are work-in-progress
- Stable features have no marker

---

## Maintenance & Support

**v0.1 Support:**
- Bug fixes: Through v0.2 release
- Security patches: Indefinite
- Feature backports: Case-by-case

**Upgrade path:**
- Settings migration automatic
- Projects forward-compatible
- Breaking changes announced in advance

---

**This is a living roadmap.** Features may shift based on:
- Community feedback
- Technical challenges
- Resource availability
- Partnership opportunities

**Last updated:** 2025-12-07
