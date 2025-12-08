# Changelog

All notable changes to Open TTS Studio will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned for v0.1.0 (Post-feedback)
- Screenshots in documentation
- Demo video
- Better error messages
- Loading indicators
- Progress bars for long operations
- Undo/redo in script editor
- Cross-platform testing (Windows, macOS, Linux)

### Planned for v0.2.0 (Chapter Management)
- Project/chapter organization
- Batch generation queue
- Export all chapters at once
- Background music support
- See [ROADMAP.md](ROADMAP.md) for full details

## [0.0.1] - 2025-12-07 (Alpha)

### Added
- 🎬 **Multi-speaker production studio** with web interface (Gradio)
- 📝 **Script editor** with auto-speaker detection
- 🎙️ **Voice assignment** with searchable/filterable dropdowns
- 🔍 **Type-to-search** voice selection (handles 67+ voices smoothly)
- 🎛️ **Backend switcher** (tested: Kokoro, VoxCPM)
- ⚙️ **Settings persistence** (JSON config)
- 📁 **File import** (.txt auto-loads on selection)
- 🔄 **Auto-switch backend** when saving settings
- 📊 **Smart chunking** for unlimited text length
- 🎵 **Audio stitching** with 100ms natural gaps between speakers
- 🔌 **OpenAI-compatible API** endpoint (server.py)
- 📚 **Complete documentation suite**:
  - User Guide (STUDIO_USER_GUIDE.md)
  - FAQ (FAQ.md)
  - Complete Tutorial (COMPLETE_TUTORIAL.md)
  - Demo Recording Script (DEMO_RECORDING_SCRIPT.md)
  - Architecture docs (ARCHITECTURE.md)
  - Roadmap (ROADMAP.md)
- ⚖️ **Apache 2.0 License**

### Fixed
- ✅ **Morty voice** now available in VoxCPM (was missing from voice_refs)
- ✅ **Reduced speaker gaps** from 300ms to 100ms for natural pacing
- ✅ **JavaScript errors** eliminated with searchable dropdowns
- ✅ **Auto-load file uploads** without requiring button click
- ✅ **Backend dropdown updates** automatically on settings save

### Changed
- 🏷️ **Project renamed** from "open-unified-tts-simple" to "Open TTS Studio"
- 🎯 **Positioning:** User-friendly front-end vs. powerful backend API
- 📏 **Voice dropdowns:** Now searchable/filterable for better UX with many voices

### Known Limitations (v0.0.1)
- Single project/chapter at a time (v0.2.0 will add chapter management)
- No background music support (v0.3.0)
- No inline editing of generated segments (v0.3.0)
- Desktop only, no mobile responsive design (v1.0.0)
- Manual voice assignment (v0.4.0 will add AI suggestions)
- No batch processing (v0.2.0)
- No project templates (v0.4.0)

### Technical Details
- **Supported backends:** Kokoro (67 voices), VoxCPM (custom clones), any OpenAI-compatible TTS
- **Audio format:** MP3, WAV, OGG
- **Dependencies:** Python 3.12+, Gradio 6.x, ffmpeg, pydub
- **Deployment:** Docker Compose (backends) + uv/pip (Studio)

### Testing
- ✅ Tested on: Linux (Arch), macOS
- ⚠️ Windows testing pending
- ✅ Kokoro backend working (67 voices)
- ✅ VoxCPM backend working (7 custom voice clones)
- ✅ Multi-speaker generation tested (2-10 speakers)
- ✅ Long-form text tested (500+ words auto-chunked)

### Contributors
- Initial release by loserbcc
- Built with community feedback during development

---

## Version History

- **v0.0.1** (2025-12-07) - Alpha release, core features working
- **v0.1.0** (Planned) - Polished beta after feedback
- **v0.2.0** (Planned Q1 2025) - Chapter management
- **v0.3.0** (Planned Q2 2025) - Production enhancements
- **v0.4.0** (Planned Q2 2025) - AI features
- **v1.0.0** (Planned Q4 2025) - Production ready

---

## Links

- [GitHub Repository](https://github.com/loserbcc/open-tts-studio)
- [Complete Tutorial](COMPLETE_TUTORIAL.md)
- [User Guide](STUDIO_USER_GUIDE.md)
- [FAQ](FAQ.md)
- [Roadmap](ROADMAP.md)

---

**Format Notes:**
- **Added** for new features
- **Changed** for changes in existing functionality
- **Deprecated** for soon-to-be removed features
- **Removed** for now removed features
- **Fixed** for any bug fixes
- **Security** for security-related changes
