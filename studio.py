"""Open Unified TTS Studio - Production interface with AI assistance.

Gradio-based production studio for multi-speaker TTS with:
- OCR/Import from multiple sources
- Dialog script editor with speaker assignment
- AI-powered script cleanup and generation (HF/OpenRouter)
- Multi-speaker rendering with voice-per-speaker
- Advanced model options and tags
"""
import gradio as gr
import os
import json
import re
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import requests

# Optional imports for advanced features
try:
    import pytesseract
    from PIL import Image
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False

try:
    import PyPDF2
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False


# =============================================================================
# MODEL PROFILES - Chunking limits per TTS backend
# =============================================================================

MODEL_PROFILES = {
    "kokoro": {
        "max_chars": 1600,  # ~400 words
        "optimal_chunk": 800,  # ~200 words
        "max_words": 400,
        "supports_ssml": False,
        "format": "wav"
    },
    "elevenlabs": {
        "max_chars": 300,  # ~75 words
        "optimal_chunk": 200,  # ~50 words
        "max_words": 75,
        "supports_ssml": True,
        "format": "mp3"
    },
    "openai": {
        "max_chars": 4096,
        "optimal_chunk": 2000,
        "max_words": 1000,
        "supports_ssml": False,
        "format": "mp3"
    },
    "coqui": {
        "max_chars": 800,
        "optimal_chunk": 400,
        "max_words": 200,
        "supports_ssml": False,
        "format": "wav"
    },
    "generic": {
        "max_chars": 1000,
        "optimal_chunk": 500,
        "max_words": 250,
        "supports_ssml": False,
        "format": "mp3"
    }
}

# =============================================================================
# CONFIGURATION
# =============================================================================

OUTPUT_DIR = Path.home() / "tts-studio-output"
OUTPUT_DIR.mkdir(exist_ok=True)

# Load config from file or create default
CONFIG_FILE = Path.home() / ".tts-studio-config.json"
if CONFIG_FILE.exists():
    with open(CONFIG_FILE) as f:
        CONFIG = json.load(f)
else:
    CONFIG = {
        # TTS Backend Configuration
        "tts_backend": "manual",  # manual, auto-detected backend name
        "tts_backends": {
            "manual": {
                "name": "Manual Config",
                "url": "http://localhost:8766",
                "type": "openai-compatible",
                "profile": "generic"  # Model profile for chunking limits
            }
        },
        "tts_active_backend": "manual",

        # AI Backend Selection
        "ai_backend": "disabled",  # disabled, lmstudio, ollama, openai, anthropic, openrouter

        # LM Studio (local, OpenAI-compatible)
        "lmstudio_endpoint": "http://localhost:1234/v1",
        "lmstudio_model": "openai/gpt-oss-20b",  # Model loaded in LM Studio

        # Ollama (local, no API key)
        "ollama_endpoint": "http://localhost:11434",
        "ollama_model": "llama3.2",

        # OpenAI
        "openai_api_key": "",
        "openai_model": "gpt-4o-mini",
        "openai_endpoint": "https://api.openai.com/v1",

        # Anthropic
        "anthropic_api_key": "",
        "anthropic_model": "claude-sonnet-4-5-20250929",

        # OpenRouter
        "openrouter_api_key": "",
        "openrouter_model": "meta-llama/llama-3.1-8b-instruct:free",
    }

# Get active TTS backend URL
def get_tts_url():
    active = CONFIG.get("tts_active_backend", "manual")
    backends = CONFIG.get("tts_backends", {})
    if active in backends:
        return backends[active]["url"]
    return "http://localhost:8766"

TTS_API_URL = get_tts_url()


# =============================================================================
# IMPORT FUNCTIONS
# =============================================================================

def import_from_text(text: str) -> str:
    """Direct text input."""
    return text.strip()


def import_from_file(file) -> str:
    """Import from uploaded file (txt, docx, pdf)."""
    if file is None:
        return ""

    file_path = Path(file.name)
    suffix = file_path.suffix.lower()

    if suffix == ".txt":
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()

    elif suffix == ".pdf" and PDF_AVAILABLE:
        text = ""
        with open(file_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                text += page.extract_text() + "\n"
        return text

    elif suffix in [".png", ".jpg", ".jpeg"] and OCR_AVAILABLE:
        img = Image.open(file_path)
        return pytesseract.image_to_string(img)

    else:
        return f"Unsupported file type: {suffix}"


def import_from_url(url: str) -> str:
    """Import from URL (webpage or text file)."""
    if not url.strip():
        return ""

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        # If it's plain text, return it
        if 'text/plain' in response.headers.get('Content-Type', ''):
            return response.text

        # Otherwise try to extract text from HTML
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        return soup.get_text(separator='\n', strip=True)

    except Exception as e:
        return f"Error importing from URL: {str(e)}"


# =============================================================================
# DIALOG PARSING
# =============================================================================

def parse_dialog(script: str) -> List[Dict[str, str]]:
    """Parse dialog format: 'Character: text' into structured data."""
    lines = []
    current_speaker = "Narrator"

    for line in script.split('\n'):
        line = line.strip()
        if not line:
            continue

        # Check for "Speaker: dialog" format
        if ':' in line:
            parts = line.split(':', 1)
            speaker = parts[0].strip()
            text = parts[1].strip()

            # Only treat as dialog if speaker is reasonable (not a time/number)
            if speaker and not re.match(r'^\d+$', speaker):
                lines.append({"speaker": speaker, "text": text})
                current_speaker = speaker
                continue

        # Otherwise, attribute to current speaker
        lines.append({"speaker": current_speaker, "text": line})

    return lines


def format_dialog(lines: List[Dict[str, str]]) -> str:
    """Format structured dialog back to script format."""
    return '\n'.join([f"{line['speaker']}: {line['text']}" for line in lines])


def get_speakers(script: str) -> List[str]:
    """Extract unique speaker names from script."""
    lines = parse_dialog(script)
    speakers = list(dict.fromkeys([line['speaker'] for line in lines]))
    return speakers


# =============================================================================
# AI ASSISTANCE (Optional - Ollama/OpenAI/Anthropic/OpenRouter)
# =============================================================================

# Popular HuggingFace free models to check
HF_FREE_MODELS = [
    "mistralai/Mistral-7B-Instruct-v0.2",
    "microsoft/phi-2",
    "HuggingFaceH4/zephyr-7b-beta",
    "google/flan-t5-large",
    "meta-llama/Meta-Llama-3-8B-Instruct",
    "mistralai/Mixtral-8x7B-Instruct-v0.1",
]

def check_hf_models() -> List[Dict[str, str]]:
    """Check which HuggingFace models are currently available on free tier."""
    available = []

    for model in HF_FREE_MODELS:
        try:
            response = requests.post(
                f"https://api-inference.huggingface.co/models/{model}",
                json={"inputs": "test", "parameters": {"max_new_tokens": 5}},
                timeout=10
            )

            if response.status_code == 200:
                status = "✅ Working"
            elif response.status_code == 503:
                status = "⏳ Loading (try again in 20s)"
            else:
                status = f"❌ Error {response.status_code}"

            available.append({
                "model": model,
                "status": status,
                "code": response.status_code
            })
        except Exception as e:
            available.append({
                "model": model,
                "status": f"❌ Failed: {str(e)[:30]}",
                "code": 0
            })

    return available

def call_ai_model(prompt: str, system_prompt: str = "", config: dict = None) -> str:
    """Call AI model via configured backend (LM Studio/Ollama/OpenAI/Anthropic/OpenRouter)."""
    if not config:
        return "Error: AI not configured. Add API endpoint in Settings."

    backend = config.get("ai_backend", "disabled")
    if backend == "disabled":
        return "AI features disabled. Enable in Settings tab."

    try:
        # LM Studio (local, OpenAI-compatible)
        if backend == "lmstudio":
            endpoint = config.get("lmstudio_endpoint", "http://localhost:1234/v1")
            # Ensure endpoint ends with /v1
            if not endpoint.endswith('/v1'):
                endpoint = endpoint.rstrip('/') + '/v1'

            model = config.get("lmstudio_model", "local-model")
            # Add openai/ prefix if missing for gpt-oss models
            if model.startswith('gpt-oss') and not model.startswith('openai/'):
                model = 'openai/' + model

            response = requests.post(
                f"{endpoint}/chat/completions",
                json={
                    "model": model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.7,
                    "max_tokens": 2000
                },
                timeout=120
            )
            response.raise_for_status()
            result = response.json()

            # Handle different response formats
            if "choices" in result and len(result["choices"]) > 0:
                return result["choices"][0]["message"]["content"]
            elif "response" in result:  # Some LM Studio versions
                return result["response"]
            else:
                raise ValueError(f"Unexpected LM Studio response format: {result}")

        # Ollama (local, no API key needed)
        if backend == "ollama":
            endpoint = config.get("ollama_endpoint", "http://localhost:11434")
            model = config.get("ollama_model", "llama3.2")

            response = requests.post(
                f"{endpoint}/api/chat",
                json={
                    "model": model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt}
                    ],
                    "stream": False
                },
                timeout=120
            )
            response.raise_for_status()
            return response.json()["message"]["content"]

        # OpenAI API
        elif backend == "openai":
            api_key = config.get("openai_api_key", "")
            model = config.get("openai_model", "gpt-4o-mini")
            endpoint = config.get("openai_endpoint", "https://api.openai.com/v1")

            response = requests.post(
                f"{endpoint}/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt}
                    ]
                },
                timeout=60
            )
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]

        # Anthropic API
        elif backend == "anthropic":
            api_key = config.get("anthropic_api_key", "")
            model = config.get("anthropic_model", "claude-sonnet-4-5-20250929")

            response = requests.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": api_key,
                    "anthropic-version": "2023-06-01",
                    "Content-Type": "application/json"
                },
                json={
                    "model": model,
                    "max_tokens": 4096,
                    "system": system_prompt,
                    "messages": [{"role": "user", "content": prompt}]
                },
                timeout=60
            )
            response.raise_for_status()
            return response.json()["content"][0]["text"]

        # OpenRouter (supports many models)
        elif backend == "openrouter":
            api_key = config.get("openrouter_api_key", "")
            model = config.get("openrouter_model", "meta-llama/llama-3.1-8b-instruct:free")

            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt}
                    ]
                },
                timeout=60
            )
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]

        else:
            return f"Unknown AI backend: {backend}"

    except Exception as e:
        return f"Error calling {backend}: {str(e)}"


def ai_cleanup_script(script: str, config: dict) -> str:
    """Use AI to clean up script - fix grammar, punctuation, formatting."""
    system_prompt = """You are a script editor. Clean up the provided script by:
- Fixing grammar and punctuation
- Improving dialog formatting
- Preserving the Speaker: dialog format
- Maintaining the original meaning and style
Return only the cleaned script, no explanations."""

    return call_ai_model(script, system_prompt, config)


def ai_expand_dialog(script: str, direction: str, config: dict) -> str:
    """Use AI to expand/improve dialog based on direction."""
    system_prompt = f"""You are a creative dialog writer. Based on this direction:
"{direction}"

Expand or improve the provided script while maintaining the Speaker: dialog format.
Return only the updated script, no explanations."""

    return call_ai_model(script, system_prompt, config)


# =============================================================================
# VOICE MANAGEMENT
# =============================================================================

def get_available_voices() -> List[str]:
    """Get voices from TTS backend."""
    try:
        response = requests.get(f"{TTS_API_URL}/v1/voices", timeout=5)
        data = response.json()
        return data.get("voices", [])
    except Exception:
        # Fallback voices for Kokoro
        return ["af_bella", "af_sarah", "am_adam", "bf_emma", "bm_george"]


def detect_backend_profile(url: str, name: str) -> str:
    """Try to detect which model profile to use based on backend type."""
    name_lower = name.lower()

    # Match based on name
    if "kokoro" in name_lower:
        return "kokoro"
    elif "elevenlabs" in name_lower or "11labs" in name_lower:
        return "elevenlabs"
    elif "openai" in name_lower:
        return "openai"
    elif "coqui" in name_lower:
        return "coqui"

    # Try to detect from voice list (different backends have characteristic voice names)
    try:
        response = requests.get(f"{url}/v1/voices", timeout=2)
        if response.status_code == 200:
            data = response.json()
            voices = data.get("voices", [])
            if voices:
                # Kokoro has specific voice naming pattern (af_, am_, bf_, bm_)
                if any(v.startswith(("af_", "am_", "bf_", "bm_")) for v in voices):
                    return "kokoro"
    except:
        pass

    return "generic"


def auto_detect_tts_backends() -> Tuple[Dict[str, dict], str]:
    """Scan network for TTS backends and return discovered backends."""
    import socket

    # Common TTS ports to scan
    scan_targets = [
        ("localhost", 8765, "Unified TTS (default)"),
        ("localhost", 8766, "Unified TTS (alt)"),
        ("localhost", 8880, "Kokoro"),
        ("localhost", 5002, "Coqui TTS"),
        ("localhost", 8080, "OpenAudio"),
    ]

    discovered = {}
    status_lines = ["🔍 Scanning for TTS backends...\n"]

    for host, port, name in scan_targets:
        url = f"http://{host}:{port}"
        try:
            # Quick port check first
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.5)
            result = sock.connect_ex((host, port))
            sock.close()

            if result != 0:
                continue  # Port not open

            # Test API endpoint
            response = requests.get(f"{url}/v1/voices", timeout=2)
            if response.status_code == 200:
                data = response.json()
                voices = data.get("voices", [])

                # Detect backend profile for chunking
                profile = detect_backend_profile(url, name)

                backend_id = f"{host}_{port}"
                discovered[backend_id] = {
                    "name": name,
                    "url": url,
                    "type": "openai-compatible",
                    "profile": profile,
                    "voices": len(voices),
                    "status": "✅ Available"
                }
                status_lines.append(f"✅ Found: {name}")
                status_lines.append(f"   URL: {url}")
                status_lines.append(f"   Voices: {len(voices)}")
                status_lines.append(f"   Profile: {profile} (max {MODEL_PROFILES[profile]['max_words']} words/chunk)")
                status_lines.append("")
        except:
            continue

    if not discovered:
        status_lines.append("\n❌ No TTS backends found!")
        status_lines.append("\nMake sure:")
        status_lines.append("- TTS server is running")
        status_lines.append("- Port is correct")
        status_lines.append("- Docker containers are up")
    else:
        status_lines.append(f"\n🎉 Found {len(discovered)} backend(s)!")
        status_lines.append("\nSelect backend from dropdown above.")

    return discovered, "\n".join(status_lines)


def test_tts_backend(url: str) -> str:
    """Test TTS backend connection and list voices."""
    try:
        response = requests.get(f"{url}/v1/voices", timeout=5)
        response.raise_for_status()
        data = response.json()
        voices = data.get("voices", [])

        status = f"✅ Connected to TTS API!\n\n"
        status += f"🎤 Found {len(voices)} voices\n\n"
        status += f"Sample voices: {', '.join(voices[:10])}"
        if len(voices) > 10:
            status += f"... and {len(voices) - 10} more"

        return status
    except requests.exceptions.ConnectionError:
        return f"❌ Connection failed!\n\nCannot reach {url}\n\nCheck that:\n- Unified TTS API is running\n- Port 8766 is correct\n- Docker containers are up"
    except Exception as e:
        return f"❌ Error: {str(e)}"


def create_voice_assignments(speakers: List[str]) -> Dict[str, str]:
    """Create default voice assignments for speakers."""
    voices = get_available_voices()
    assignments = {}

    for i, speaker in enumerate(speakers):
        # Cycle through available voices
        assignments[speaker] = voices[i % len(voices)] if voices else "af_bella"

    return assignments


# =============================================================================
# MULTI-SPEAKER PRODUCTION
# =============================================================================

def generate_multi_speaker(
    script: str,
    voice_assignments: Dict[str, str],
    output_format: str = "mp3"
) -> Tuple[str, str]:
    """Generate multi-speaker audio by stitching individual lines."""
    import tempfile
    from pydub import AudioSegment

    lines = parse_dialog(script)
    if not lines:
        return None, "No dialog to generate"

    # Generate each line
    segments = []
    status_lines = []

    for i, line in enumerate(lines):
        speaker = line['speaker']
        text = line['text']
        voice = voice_assignments.get(speaker, "af_bella")

        status_lines.append(f"[{i+1}/{len(lines)}] {speaker} ({voice}): {text[:50]}...")

        try:
            # Call TTS API
            response = requests.post(
                f"{TTS_API_URL}/v1/audio/speech",
                json={
                    "model": "tts-1",
                    "voice": voice,
                    "input": text,
                    "response_format": "wav"
                },
                timeout=120
            )
            response.raise_for_status()

            # Load audio segment
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
                f.write(response.content)
                temp_path = f.name

            segment = AudioSegment.from_wav(temp_path)
            segments.append(segment)
            Path(temp_path).unlink()

        except Exception as e:
            status_lines.append(f"Error on line {i+1}: {str(e)}")
            continue

    if not segments:
        return None, "Failed to generate any audio"

    # Stitch together with small gaps
    combined = segments[0]
    gap = AudioSegment.silent(duration=300)  # 300ms gap between speakers

    for segment in segments[1:]:
        combined += gap + segment

    # Export
    output_path = OUTPUT_DIR / f"production_{hash(script)}.{output_format}"
    combined.export(str(output_path), format=output_format)

    status = "\n".join(status_lines) + f"\n\nGenerated: {output_path}"
    return str(output_path), status


# =============================================================================
# GRADIO INTERFACE
# =============================================================================

def build_interface():
    """Build Gradio production studio interface."""

    with gr.Blocks(title="TTS Production Studio") as app:
        gr.Markdown("# 🎬 TTS Production Studio")
        gr.Markdown("Multi-speaker TTS with AI assistance - paste text, assign voices, generate audio")

        # State variables
        voice_assignments = gr.State({})

        with gr.Tabs():
            # ===== MAIN STUDIO TAB =====
            with gr.Tab("🎙️ Studio"):
                gr.Markdown("## 1️⃣ Input Your Script")
                gr.Markdown("Paste text directly, or upload a file")

                with gr.Row():
                    with gr.Column(scale=3):
                        script_editor = gr.Textbox(
                            label="Script",
                            placeholder="Paste your text here, or upload a file below.\n\nFormat for multi-speaker:\nSpeaker1: Hello there!\nSpeaker2: Welcome to the show!",
                            max_lines=30,
                            lines=20
                        )

                script_editor = gr.Textbox(
                    label="Script",
                    placeholder="Narrator: Welcome to the production.\nCharacter1: Hello world!\nCharacter2: This is amazing!",
                    max_lines=30,
                    lines=20
                )

                with gr.Row():
                    detect_speakers_btn = gr.Button("Detect Speakers")
                    cleanup_btn = gr.Button("🤖 AI Cleanup")
                    expand_btn = gr.Button("🤖 AI Expand")

                speakers_detected = gr.Textbox(label="Detected Speakers", max_lines=3)

                # AI features (optional)
                ai_status = gr.Markdown(
                    f"**AI Status:** {'✅ Enabled (' + CONFIG.get('ai_backend', 'disabled') + ')' if CONFIG.get('ai_backend') != 'disabled' else '❌ Disabled (configure in Settings)'}"
                )

                with gr.Accordion("AI Expansion Options", open=False, visible=(CONFIG.get("ai_backend") != "disabled")):
                    expand_direction = gr.Textbox(
                        label="Expansion Direction",
                        placeholder="e.g., Make it more dramatic, Add humor, etc."
                    )

                # Script editor actions
                detect_speakers_btn.click(
                    fn=lambda s: '\n'.join(get_speakers(s)),
                    inputs=[script_editor],
                    outputs=[speakers_detected]
                )
                cleanup_btn.click(
                    fn=lambda s: ai_cleanup_script(s, CONFIG),
                    inputs=[script_editor],
                    outputs=[script_editor]
                )
                expand_btn.click(
                    fn=lambda s, d: ai_expand_dialog(s, d, CONFIG),
                    inputs=[script_editor, expand_direction],
                    outputs=[script_editor]
                )

            # ===== PRODUCTION TAB =====
            with gr.Tab("🎙️ Production"):
                gr.Markdown("### Assign voices and generate audio")

                production_script = gr.Textbox(
                    label="Script",
                    max_lines=30,
                    lines=20
                )

                with gr.Row():
                    analyze_btn = gr.Button("🔍 Detect Speakers & Auto-Assign Voices")

                speakers_detected = gr.Textbox(
                    label="Detected Speakers",
                    max_lines=2,
                    info="Speakers found in your script"
                )

                speaker_voice_map = gr.JSON(
                    label="Voice Assignments (Auto-Generated - Edit to customize)"
                )

                with gr.Accordion("Voice Assignment Help", open=True):
                    gr.Markdown("""
**How to assign voices:**
1. Click "Analyze Script" above to detect speakers
2. Edit the JSON to assign voices (copy names from list below)
3. Example: `{"Narrator": "af_bella", "Character1": "am_adam"}`
                    """)
                    available_voices = gr.Dropdown(
                        label="🎤 Available Voices (67 Kokoro voices)",
                        choices=get_available_voices(),
                        multiselect=False,
                        interactive=True,
                        info="Click to see all voices, then copy names to JSON above"
                    )
                    refresh_voices_btn = gr.Button("🔄 Refresh Voice List")

                with gr.Row():
                    output_format = gr.Dropdown(
                        label="Output Format",
                        choices=["mp3", "wav", "opus", "flac"],
                        value="mp3"
                    )
                    generate_btn = gr.Button("🎬 Generate Production", variant="primary")

                audio_output = gr.Audio(label="Generated Audio")
                status_output = gr.Textbox(label="Status", max_lines=10)

                # Production actions
                def analyze_and_assign(script):
                    speakers = get_speakers(script)
                    assignments = create_voice_assignments(speakers)
                    speaker_list = ", ".join(speakers) if speakers else "No speakers detected"
                    return assignments, speaker_list

                analyze_btn.click(
                    fn=analyze_and_assign,
                    inputs=[production_script],
                    outputs=[speaker_voice_map, speakers_detected]
                )

                refresh_voices_btn.click(
                    fn=get_available_voices,
                    inputs=[],
                    outputs=[available_voices]
                )

                generate_btn.click(
                    fn=generate_multi_speaker,
                    inputs=[production_script, speaker_voice_map, output_format],
                    outputs=[audio_output, status_output]
                )

            # ===== SETTINGS TAB =====
            with gr.Tab("⚙️ Settings"):
                gr.Markdown("# TTS Backend Configuration")
                gr.Markdown("Configure your TTS backend - auto-detect or manual setup")

                with gr.Row():
                    auto_detect_btn = gr.Button("🔍 Auto-Detect TTS Backends", variant="primary")
                    manual_config_btn = gr.Button("➕ Manual Configuration")

                detected_backends = gr.State({})
                detection_status = gr.Textbox(
                    label="Detection Results",
                    max_lines=15,
                    visible=False
                )

                # Backend selection
                with gr.Row():
                    backend_select = gr.Dropdown(
                        label="Active TTS Backend",
                        choices=["manual"],
                        value="manual",
                        info="Select which TTS backend to use"
                    )
                    refresh_backends_btn = gr.Button("🔄 Refresh List")

                # Manual config section
                manual_accordion = gr.Accordion("Manual Backend Configuration", open=True)
                with manual_accordion:
                    gr.Markdown("### Backend Connection")
                    backend_url = gr.Textbox(
                        label="TTS API Endpoint",
                        value=TTS_API_URL,
                        placeholder="http://localhost:8766",
                        info="OpenAI-compatible TTS API URL"
                    )

                    gr.Markdown("### Model Profile (Chunking Limits)")
                    profile_select = gr.Dropdown(
                        label="Profile Template",
                        choices=list(MODEL_PROFILES.keys()),
                        value="generic",
                        info="Select profile or customize below"
                    )

                    with gr.Row():
                        max_words = gr.Number(
                            label="Max Words/Chunk",
                            value=250,
                            info="Maximum words per TTS request"
                        )
                        optimal_chunk = gr.Number(
                            label="Optimal Chunk Size (chars)",
                            value=500,
                            info="Target chunk size for splitting"
                        )

                    test_backend_btn = gr.Button("🧪 Test Connection")
                    backend_test_status = gr.Textbox(label="Test Results", max_lines=5)

                output_dir = gr.Textbox(
                    label="Output Directory",
                    value=str(OUTPUT_DIR)
                )

                gr.Markdown("---")
                gr.Markdown("# AI Assistant Configuration (Optional)")
                gr.Markdown("Configure AI for script cleanup and expansion. **Not required** for basic TTS functionality.")

                ai_backend_select = gr.Radio(
                    label="AI Backend",
                    choices=["disabled", "lmstudio", "ollama", "openai", "anthropic", "openrouter"],
                    value=CONFIG.get("ai_backend", "disabled"),
                    info="AI is optional - Studio works great without it!"
                )

                gr.Markdown("""
### 💡 Recommended Free Options:
- **OpenRouter** - Free API key, access to free models, no install needed! 🌟
- **LM Studio** - GUI app, easy setup, runs any model locally
- **Ollama** - CLI tool, one-command install, super fast
                """)

                # LM Studio settings
                lmstudio_accordion = gr.Accordion("LM Studio (Local GUI - Easiest!)", open=False)
                with lmstudio_accordion:
                    gr.Markdown("""
✅ **Easy GUI app** - Download from lmstudio.ai
✅ **Completely free** - No API keys, unlimited use
✅ **Any model** - Download models from the app
✅ **OpenAI compatible** - Standard API format

Setup: Download LM Studio → Load a model → Start server (default port 1234)

**Important:** Endpoint must end with `/v1`
                    """)
                    lmstudio_endpoint = gr.Textbox(
                        label="Endpoint (must include /v1)",
                        value=CONFIG.get("lmstudio_endpoint", "http://localhost:1234/v1"),
                        placeholder="http://localhost:1234/v1",
                        info="Must end with /v1 for OpenAI compatibility"
                    )
                    lmstudio_model = gr.Textbox(
                        label="Model",
                        value=CONFIG.get("lmstudio_model", "openai/gpt-oss-20b"),
                        placeholder="openai/gpt-oss-20b"
                    )


                # Ollama settings
                ollama_accordion = gr.Accordion("Ollama Settings (Local, No API Key)", open=False)
                with ollama_accordion:
                    ollama_endpoint = gr.Textbox(
                        label="Ollama Endpoint",
                        value=CONFIG.get("ollama_endpoint", "http://localhost:11434"),
                        placeholder="http://localhost:11434"
                    )
                    ollama_model = gr.Textbox(
                        label="Model",
                        value=CONFIG.get("ollama_model", "llama3.2"),
                        placeholder="llama3.2, mistral, etc."
                    )

                # OpenAI settings
                openai_accordion = gr.Accordion("OpenAI Settings", open=False)
                with openai_accordion:
                    openai_key = gr.Textbox(
                        label="API Key",
                        type="password",
                        value=CONFIG.get("openai_api_key", "")
                    )
                    openai_endpoint = gr.Textbox(
                        label="Endpoint (for OpenAI-compatible APIs)",
                        value=CONFIG.get("openai_endpoint", "https://api.openai.com/v1"),
                        placeholder="https://api.openai.com/v1"
                    )
                    openai_model = gr.Textbox(
                        label="Model",
                        value=CONFIG.get("openai_model", "gpt-4o-mini"),
                        placeholder="gpt-4o-mini, gpt-4o, etc."
                    )

                # Anthropic settings
                anthropic_accordion = gr.Accordion("Anthropic Settings", open=False)
                with anthropic_accordion:
                    anthropic_key = gr.Textbox(
                        label="API Key",
                        type="password",
                        value=CONFIG.get("anthropic_api_key", "")
                    )
                    anthropic_model = gr.Textbox(
                        label="Model",
                        value=CONFIG.get("anthropic_model", "claude-sonnet-4-5-20250929"),
                        placeholder="claude-sonnet-4-5-20250929, claude-opus-4-5-20251101, etc."
                    )

                # OpenRouter settings
                openrouter_accordion = gr.Accordion("OpenRouter (Cloud - Free Models Available!) 🌟", open=False)
                with openrouter_accordion:
                    gr.Markdown("""
✅ **Get a FREE API key** - Visit [openrouter.ai/keys](https://openrouter.ai/keys)
✅ **Free models available** - No credit card required for free tier
✅ **100+ models** - Access latest open source models
✅ **No installation** - Cloud-based, works immediately

**Quick Start:**
1. Visit [openrouter.ai/keys](https://openrouter.ai/keys) and sign up (free!)
2. Copy your API key
3. Paste below and select a free model
4. Click "Save All Settings"

**Popular Free Models:**
- `meta-llama/llama-3.1-8b-instruct:free` - Great all-rounder (recommended!)
- `google/gemma-2-9b-it:free` - Google's efficient model
- `mistralai/mistral-7b-instruct:free` - Fast and capable
                    """)
                    openrouter_key = gr.Textbox(
                        label="API Key (get free at openrouter.ai/keys)",
                        type="password",
                        value=CONFIG.get("openrouter_api_key", ""),
                        placeholder="sk-or-v1-..."
                    )
                    openrouter_model = gr.Textbox(
                        label="Model (use :free for free tier)",
                        value=CONFIG.get("openrouter_model", "meta-llama/llama-3.1-8b-instruct:free"),
                        placeholder="meta-llama/llama-3.1-8b-instruct:free"
                    )
                    gr.Markdown("💡 **Tip:** All models ending in `:free` are available without credits!")

                save_settings_btn = gr.Button("💾 Save All Settings", variant="primary")

                def save_all_settings(
                    tts_url, out_dir, profile, max_w, opt_chunk,
                    ai_backend,
                    lmstudio_ep, lmstudio_mdl,
                    ollama_ep, ollama_mdl,
                    openai_k, openai_ep, openai_mdl,
                    anthropic_k, anthropic_mdl,
                    openrouter_k, openrouter_mdl
                ):
                    global TTS_API_URL, OUTPUT_DIR, CONFIG

                    TTS_API_URL = tts_url
                    OUTPUT_DIR = Path(out_dir)
                    OUTPUT_DIR.mkdir(exist_ok=True)

                    # Update TTS backend config with custom profile
                    if "tts_backends" not in CONFIG:
                        CONFIG["tts_backends"] = {}

                    CONFIG["tts_backends"]["manual"] = {
                        "name": "Manual Config",
                        "url": tts_url,
                        "type": "openai-compatible",
                        "profile": profile,
                        "max_words": int(max_w),
                        "optimal_chunk": int(opt_chunk)
                    }
                    CONFIG["tts_active_backend"] = "manual"

                    CONFIG.update({
                        "ai_backend": ai_backend,
                        "lmstudio_endpoint": lmstudio_ep,
                        "lmstudio_model": lmstudio_mdl,
                        "ollama_endpoint": ollama_ep,
                        "ollama_model": ollama_mdl,
                        "openai_api_key": openai_k,
                        "openai_endpoint": openai_ep,
                        "openai_model": openai_mdl,
                        "anthropic_api_key": anthropic_k,
                        "anthropic_model": anthropic_mdl,
                        "openrouter_api_key": openrouter_k,
                        "openrouter_model": openrouter_mdl,
                    })

                    with open(CONFIG_FILE, 'w') as f:
                        json.dump(CONFIG, f, indent=2)

                    status_msg = f"✅ Settings saved!\n\nTTS Backend: {tts_url}\n"
                    status_msg += f"Profile: {profile} (max {int(max_w)} words/chunk)\n"
                    status_msg += f"AI Backend: {ai_backend}"
                    if ai_backend != "disabled":
                        status_msg += f"\n\n⚠️ Restart the Studio for AI changes to take effect."

                    return status_msg

                settings_status = gr.Textbox(label="Status", max_lines=5)

                # TTS Backend event handlers
                def handle_auto_detect():
                    backends, status = auto_detect_tts_backends()
                    # Update dropdown choices
                    choices = ["manual"] + list(backends.keys())
                    return backends, status, gr.Dropdown(choices=choices), gr.Textbox(visible=True)

                def handle_profile_select(profile_name):
                    """Auto-fill profile values when template selected."""
                    if profile_name in MODEL_PROFILES:
                        profile = MODEL_PROFILES[profile_name]
                        return profile["max_words"], profile["optimal_chunk"]
                    return 250, 500

                def handle_backend_select(backend_id, backends_dict):
                    """Update manual config when backend selected from dropdown."""
                    if backend_id == "manual":
                        return TTS_API_URL, "generic", 250, 500
                    elif backend_id in backends_dict:
                        backend = backends_dict[backend_id]
                        profile = backend.get("profile", "generic")
                        profile_data = MODEL_PROFILES.get(profile, MODEL_PROFILES["generic"])
                        return backend["url"], profile, profile_data["max_words"], profile_data["optimal_chunk"]
                    return TTS_API_URL, "generic", 250, 500

                auto_detect_btn.click(
                    fn=handle_auto_detect,
                    outputs=[detected_backends, detection_status, backend_select, detection_status]
                )

                profile_select.change(
                    fn=handle_profile_select,
                    inputs=[profile_select],
                    outputs=[max_words, optimal_chunk]
                )

                backend_select.change(
                    fn=handle_backend_select,
                    inputs=[backend_select, detected_backends],
                    outputs=[backend_url, profile_select, max_words, optimal_chunk]
                )

                test_backend_btn.click(
                    fn=test_tts_backend,
                    inputs=[backend_url],
                    outputs=[backend_test_status]
                )

                save_settings_btn.click(
                    fn=save_all_settings,
                    inputs=[
                        backend_url, output_dir, profile_select, max_words, optimal_chunk,
                        ai_backend_select,
                        lmstudio_endpoint, lmstudio_model,
                        ollama_endpoint, ollama_model,
                        openai_key, openai_endpoint, openai_model,
                        anthropic_key, anthropic_model,
                        openrouter_key, openrouter_model
                    ],
                    outputs=[settings_status]
                )

                # Auto-open accordion when backend is selected
                def update_accordions(backend):
                    return [
                        gr.Accordion(open=(backend == "lmstudio")),  # LM Studio
                        gr.Accordion(open=(backend == "ollama")),    # Ollama
                        gr.Accordion(open=(backend == "openai")),    # OpenAI
                        gr.Accordion(open=(backend == "anthropic")), # Anthropic
                        gr.Accordion(open=(backend == "openrouter")) # OpenRouter
                    ]

                ai_backend_select.change(
                    fn=update_accordions,
                    inputs=[ai_backend_select],
                    outputs=[
                        lmstudio_accordion,
                        ollama_accordion,
                        openai_accordion,
                        anthropic_accordion,
                        openrouter_accordion
                    ]
                )

        # Flow: Import → Script Editor → Production
        imported_text.change(fn=lambda x: x, inputs=[imported_text], outputs=[script_editor])
        script_editor.change(fn=lambda x: x, inputs=[script_editor], outputs=[production_script])

    return app


if __name__ == "__main__":
    print("🎬 Starting TTS Production Studio...")
    print(f"Output directory: {OUTPUT_DIR}")
    print(f"TTS Backend: {TTS_API_URL}")

    if not OCR_AVAILABLE:
        print("⚠️  OCR not available - install pytesseract and Pillow for image import")
    if not PDF_AVAILABLE:
        print("⚠️  PDF import not available - install PyPDF2")

    app = build_interface()
    app.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=True,
        allowed_paths=[str(OUTPUT_DIR)]
    )
