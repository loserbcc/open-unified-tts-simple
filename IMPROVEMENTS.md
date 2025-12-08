# Open Unified TTS Studio - Improvements & Roadmap

## Critical Requirements Documentation

### System Dependencies
- **ffmpeg** (required for multi-speaker audio stitching)
  - macOS: Already at `/opt/homebrew/bin/ffmpeg` (add to PATH)
  - Linux: `apt-get install ffmpeg` or `yum install ffmpeg`
  - Need to auto-detect or warn if missing

### Python Dependencies
- Core: fastapi, uvicorn, pydantic, requests, numpy, scipy
- Studio: gradio, pydub
- Optional AI: openai, anthropic (for API backends)
- Optional Import: PyPDF2, pytesseract, Pillow, beautifulsoup4, lxml

## UX/UI Improvements Needed

### Auto-Detection & Smart Defaults
- [ ] **Auto-detect ffmpeg** and show warning if missing with install instructions
- [ ] **Auto-detect available AI backends** (LM Studio, Ollama) on startup
- [ ] **Auto-discover TTS backends** on local network
- [ ] **Auto-validate configurations** before saving (test connections)
- [ ] **Smart endpoint completion** - auto-add `/v1` for OpenAI-compatible APIs
- [ ] **Model auto-discovery** - query LM Studio/Ollama for available models

### Streamlined Workflow
- [ ] **Single-page quick start** mode (paste text → select voice → generate)
- [ ] **Wizard mode** for first-time setup (detect backends, test, configure)
- [ ] **Presets system** - save common voice/speaker configurations
- [ ] **Batch processing** - upload multiple scripts, auto-generate all
- [ ] **Progress indicators** for long operations (AI processing, audio generation)

### Better Layout
- [ ] **Tab consolidation** - reduce Import/Script/Production to 2 tabs max
- [ ] **Inline editing** - edit and generate in same view
- [ ] **Preview pane** - see/hear results without switching tabs
- [ ] **Settings as sidebar** not separate tab (always accessible)

### Intelligent Features
- [ ] **Auto-detect speakers** from script format without button click
- [ ] **Voice matching suggestions** based on speaker names (Rick → rick voice)
- [ ] **Background TTS generation** while editing (pre-cache common phrases)
- [ ] **Smart chunking preview** - show how text will be split before generating
- [ ] **Quality presets** - Fast/Balanced/HQ (auto-configure backend settings)

### Documentation & Onboarding
- [ ] **Interactive tutorial** on first launch
- [ ] **Embedded help tooltips** for every feature
- [ ] **Video demo** showing complete workflow
- [ ] **Quick start guide** - 5 steps to first audio
- [ ] **Troubleshooting guide** for common issues (ffmpeg, ports, etc.)

### Backend Intelligence
- [ ] **Health checks** - auto-detect if Kokoro/LM Studio are running
- [ ] **Automatic reconnection** if backend goes down
- [ ] **Fallback backends** - if primary fails, try alternatives
- [ ] **Queue system** for multiple simultaneous generations
- [ ] **Resume support** - save progress, continue later

## Current Pain Points (Dec 2025)

1. **Too many configuration steps** - endpoint URLs, model names, manual testing
2. **Poor error messages** - "choices" error didn't explain missing `/v1`
3. **Hidden requirements** - ffmpeg not mentioned until it fails
4. **No validation** - can save broken configs that fail later
5. **Manual accordion opening** - now fixed, but should auto-detect more
6. **Separate tabs disrupt flow** - back and forth between Import/Script/Production

## Quick Wins (Easy to implement)

1. **Startup health check** - test all backends on launch, show status
2. **One-click setup** - "Detect Everything" button that finds backends
3. **Smart config defaults** - scan network for common ports (1234, 8765, etc.)
4. **Better text area sizing** - already done, but make responsive
5. **Inline help** - show examples in placeholders, tooltips everywhere
6. **Config validation** - test before save, show green/red indicators

## Big Ideas (Future)

1. **Plugin system** - easy to add new TTS backends
2. **Voice marketplace** - share/download voice profiles
3. **Cloud sync** - save projects, access from anywhere
4. **Real-time collaboration** - multiple users editing same script
5. **Auto-subtitles** - generate SRT from multi-speaker audio
6. **Video integration** - add TTS audio to video timeline

---

**Philosophy**: Make it work like a modern DAW (Digital Audio Workstation) - everything visible, immediate feedback, undo/redo, save presets, minimal clicks from idea to audio.

## OCR Feature (Requested Dec 2025)

### Remote OCR Service Support
- [ ] **Drop-in OCR URL** - Support external OCR models/Gradio endpoints
- [ ] **URL configuration** - Similar to LM Studio, allow users to point to OCR service
- [ ] **Format support** - Images, PDFs, scanned documents
- [ ] **Auto-convert to text** - OCR → text → script editor
- [ ] **Example endpoints** - Document popular OCR services (Tesseract online, cloud APIs)

**Use case:** Upload image/PDF → OCR service extracts text → edit in Studio → generate TTS
