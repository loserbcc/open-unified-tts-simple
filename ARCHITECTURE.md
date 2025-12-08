# Open Unified TTS Studio - Architecture

## Core Principle: Backend-Agnostic Design

**The Studio is JUST the interface** - it doesn't ship with TTS engines.

```
┌─────────────────────────────────────┐
│   Studio (Docker Container)         │
│   - Web UI (Gradio)                 │
│   - API orchestration               │
│   - Config management               │
│   - Audio stitching                 │
└─────────────────────────────────────┘
            ↓ (talks to)
┌─────────────────────────────────────┐
│   User's TTS Backend (any!)         │
│   - Kokoro                          │
│   - Coqui                           │
│   - ElevenLabs API                  │
│   - OpenAI TTS API                  │
│   - Custom backend                  │
└─────────────────────────────────────┘
```

## Backend Interface Specification

Any TTS backend that implements these endpoints works:

### Required Endpoints

```
GET  /v1/voices          → { "voices": ["voice1", "voice2", ...] }
POST /v1/audio/speech    → audio file (WAV/MP3)
     Body: {
       "model": "tts-1",
       "voice": "voice_name",
       "input": "text to speak",
       "response_format": "mp3"
     }
```

### Optional Endpoints

```
GET  /health            → { "status": "ok", "backend": "kokoro" }
GET  /v1/voices/:id     → { "name": "...", "preview_url": "..." }
POST /v1/audio/preview  → Short audio preview
```

That's it! If a backend speaks this simple API, Studio works with it.

## Auto-Detection System

### Discovery Process

When Studio starts or user clicks "🔍 Auto-Detect Backends":

```python
# Scan common ports on localhost and local network
scan_targets = [
    "http://localhost:8765",   # Unified TTS
    "http://localhost:8766",   # Alternative port
    "http://localhost:5002",   # Coqui TTS default
    "http://localhost:8080",   # OpenAudio
    # Add your own network endpoints here
]

for target in scan_targets:
    try:
        response = requests.get(f"{target}/v1/voices", timeout=1)
        if response.ok:
            backends.append({
                "url": target,
                "name": detect_backend_name(response),
                "voices": response.json()["voices"],
                "status": "✅ Available"
            })
    except:
        continue

# Show results to user
```

### Configuration Drop-ins

Users can drop in config files or paste URLs:

```yaml
# tts-backend.yaml
backends:
  - name: "My Kokoro Server"
    url: "http://your-server:8766"
    type: "openai-compatible"

  - name: "ElevenLabs"
    url: "https://api.elevenlabs.io/v1"
    type: "elevenlabs"
    api_key: "${ELEVENLABS_KEY}"

  - name: "Local Coqui"
    url: "http://localhost:5002"
    type: "coqui"
```

Or simply paste a URL and Studio probes it:
- User pastes: `http://your-server:8766`
- Studio fetches `/v1/voices`
- Auto-detects backend type
- Saves configuration
- ✅ Ready to use!

## Docker Packaging Strategy

### Studio Container (Lightweight)

```dockerfile
# Dockerfile (Studio only - no TTS engines!)
FROM python:3.12-slim

# System deps: ffmpeg for audio stitching only
RUN apt-get update && apt-get install -y ffmpeg

# Python deps: Gradio, FastAPI, audio processing
COPY requirements.txt .
RUN pip install -r requirements.txt

# Studio code
COPY studio.py server.py ./
COPY static/ ./static/

# Config directory (mount user configs here)
VOLUME /config

# Output directory
VOLUME /output

EXPOSE 7860

CMD ["python", "studio.py"]
```

**Container size:** ~500MB (just Python + deps, no TTS models!)

### Backend Containers (User's Choice)

Users run whatever TTS backend they want:

```yaml
# docker-compose.yml (Example with Kokoro)
version: '3.8'

services:
  # Studio (always the same)
  tts-studio:
    image: ghcr.io/youruser/tts-studio:latest
    ports:
      - "7860:7860"
    volumes:
      - ./config:/config
      - ./output:/output
    environment:
      - AUTO_DETECT_BACKENDS=true

  # User's choice of backend (optional, configurable)
  kokoro:
    image: ghcr.io/remsky/kokoro-fastapi:latest
    ports:
      - "8880:8880"
```

Or users can point Studio to existing backends elsewhere on their network!

## Backend Adapter System

Studio includes adapters for common backend types:

```python
class BackendAdapter:
    def get_voices(self) -> List[str]: pass
    def synthesize(self, text: str, voice: str) -> bytes: pass

class OpenAIAdapter(BackendAdapter):
    # Kokoro, Unified TTS, most custom backends
    endpoint = "/v1/audio/speech"

class CoquiAdapter(BackendAdapter):
    # Coqui TTS specific API
    endpoint = "/api/tts"

class ElevenLabsAdapter(BackendAdapter):
    # ElevenLabs cloud API
    endpoint = "/text-to-speech"
```

Studio auto-detects which adapter to use based on API responses.

## Configuration UI Flow

1. **First Launch:**
   - "No TTS backend detected"
   - Button: "🔍 Auto-Detect" or "➕ Add Backend"

2. **Auto-Detect:**
   - Scans network
   - Shows found backends: "✅ Kokoro (67 voices) at http://your-server:8766"
   - User clicks "Use This"
   - ✅ Configured!

3. **Manual Add:**
   - User pastes URL: `http://your-server:8766`
   - Studio tests endpoint
   - Shows: "✅ Found 67 voices, Backend: Kokoro"
   - User clicks "Save"
   - ✅ Configured!

## Multi-Backend Support (Future)

Users can configure multiple backends and choose per-project:

```
Available Backends:
  ✅ Kokoro Local (67 voices) - http://localhost:8766
  ✅ ElevenLabs Cloud (120+ voices) - api.elevenlabs.io
  ✅ Coqui Custom (15 voices) - http://your-coqui-server:5002

For this script, use: [Dropdown: Kokoro Local ▼]
```

## Benefits of This Architecture

1. **Lightweight Studio** - Docker image ~500MB vs 5GB+ with bundled models
2. **User Choice** - Use any TTS backend, even paid APIs
3. **Easy Updates** - Update Studio without re-downloading TTS models
4. **Mix & Match** - Use Kokoro for some voices, ElevenLabs for others
5. **Network-Aware** - Auto-discover TTS servers on local network
6. **Future-Proof** - New TTS backends? Just implement the interface!

## Migration Path

### Phase 1: Current (Hardcoded Kokoro)
```python
TTS_API_URL = "http://localhost:8766"  # Hardcoded
```

### Phase 2: Configurable (Implemented ✅)
```python
TTS_API_URL = os.environ.get("TTS_API_URL", "http://localhost:8766")
# User can set via Settings UI
```

### Phase 3: Auto-Detect (Next)
```python
backends = auto_detect_backends()
if backends:
    TTS_API_URL = backends[0]["url"]
else:
    show_setup_wizard()
```

### Phase 4: Multi-Backend (Future)
```python
backends = {
    "kokoro": "http://localhost:8766",
    "elevenlabs": "https://api.elevenlabs.io/v1"
}
# User selects per-script or per-speaker
```

---

## Docker Distribution Strategy

**GitHub Container Registry:**
```bash
# Users pull Studio only
docker pull ghcr.io/youruser/tts-studio:latest

# Run with any backend they want
docker run -p 7860:7860 \
  -e TTS_BACKEND_URL=http://their-backend:8080 \
  tts-studio:latest
```

**Docker Hub:**
```bash
docker pull youruser/tts-studio:latest
```

**Standalone:**
```bash
# Studio discovers backends automatically
docker-compose up
# → Scans network
# → Finds TTS backends
# → Ready to use!
```

This is the way! 🚀
