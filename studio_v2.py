"""Open Unified TTS Studio - Simplified single-page interface.

Gradio-based production studio for multi-speaker TTS with:
- Simple text input (paste or upload)
- Optional AI cleanup/expand
- Voice assignment per speaker
- Multi-speaker audio generation
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
        "tts_backend": "manual",
        "tts_backends": {
            "manual": {
                "name": "Manual Config",
                "url": "http://localhost:8766",
                "type": "openai-compatible",
                "profile": "generic"
            }
        },
        "tts_active_backend": "manual",

        # AI Backend Selection
        "ai_backend": "disabled",
        "lmstudio_endpoint": "http://localhost:1234/v1",
        "lmstudio_model": "openai/gpt-oss-20b",
        "ollama_endpoint": "http://localhost:11434",
        "ollama_model": "llama3.2",
        "openai_api_key": "",
        "openai_model": "gpt-4o-mini",
        "openai_endpoint": "https://api.openai.com/v1",
        "anthropic_api_key": "",
        "anthropic_model": "claude-sonnet-4-5-20250929",
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

    return f"Error: Cannot read {suffix} files"


# ============================================================================
# SCRIPT PROCESSING
# =============================================================================

def parse_dialog(script: str) -> List[Dict[str, str]]:
    """Parse dialog format: 'Character: text' into structured data."""
    lines = []
    current_speaker = "Narrator"

    for line in script.split('\n'):
        line = line.strip()
        if not line:
            continue

        if ':' in line:
            parts = line.split(':', 1)
            speaker = parts[0].strip()
            text = parts[1].strip()

            if speaker and not re.match(r'^\d+$', speaker):
                lines.append({"speaker": speaker, "text": text})
                current_speaker = speaker
                continue

        lines.append({"speaker": current_speaker, "text": line})

    return lines


def get_speakers(script: str) -> List[str]:
    """Extract unique speakers from script."""
    lines = parse_dialog(script)
    speakers = []
    seen = set()

    for line in lines:
        speaker = line['speaker']
        if speaker not in seen:
            speakers.append(speaker)
            seen.add(speaker)

    return speakers


def get_available_voices(backend_url: str = None) -> List[str]:
    """Get list of available voices from TTS API."""
    url = backend_url or TTS_API_URL
    try:
        response = requests.get(f"{url}/v1/voices", timeout=5)
        data = response.json()
        voices = data.get("voices", [])
        if not voices:
            # Fallback to default voices if empty
            return ["af_bella", "af_sarah", "am_adam", "bf_emma", "bm_george"]
        return voices
    except Exception as e:
        print(f"Error fetching voices from {url}: {e}")
        return ["af_bella", "af_sarah", "am_adam", "bf_emma", "bm_george"]


def create_voice_assignments(speakers: List[str]) -> Dict[str, str]:
    """Create default voice assignments for speakers."""
    voices = get_available_voices()
    assignments = {}

    for i, speaker in enumerate(speakers):
        assignments[speaker] = voices[i % len(voices)] if voices else "af_bella"

    return assignments


# =============================================================================
# AI FUNCTIONS
# =============================================================================

def call_ai_model(prompt: str, system_prompt: str = "", config: dict = None) -> str:
    """Call AI model via configured backend."""
    if not config:
        return "Error: AI not configured"

    backend = config.get("ai_backend", "disabled")
    if backend == "disabled":
        return "AI features disabled. Enable in Settings tab."

    try:
        if backend == "lmstudio":
            endpoint = config.get("lmstudio_endpoint", "http://localhost:1234/v1")
            if not endpoint.endswith('/v1'):
                endpoint = endpoint.rstrip('/') + '/v1'

            model = config.get("lmstudio_model", "local-model")
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

            if "choices" in result and len(result["choices"]) > 0:
                return result["choices"][0]["message"]["content"]
            elif "response" in result:
                return result["response"]
            else:
                raise ValueError(f"Unexpected response format: {result}")

        # Add other backends (ollama, openai, etc.) here as needed

        return "Error: Unsupported AI backend"

    except Exception as e:
        return f"Error calling AI: {str(e)}"


def ai_cleanup_dialog(script: str, config: dict) -> str:
    """Clean up dialog formatting using AI."""
    system_prompt = "You are a dialog formatting expert. Clean up the given text into proper dialog format with 'Speaker: text' on each line. Preserve the original content but fix formatting issues."
    prompt = f"Clean up this dialog:\n\n{script}"
    return call_ai_model(prompt, system_prompt, config)


def ai_expand_dialog(script: str, direction: str, config: dict) -> str:
    """Expand dialog in specified direction using AI."""
    system_prompt = "You are a creative dialog writer. Expand the given dialog naturally while maintaining character voices and story flow."

    if direction == "before":
        prompt = f"Write dialog that comes BEFORE this scene:\n\n{script}"
    else:
        prompt = f"Write dialog that comes AFTER this scene:\n\n{script}"

    return call_ai_model(prompt, system_prompt, config)


# =============================================================================
# TTS GENERATION
# =============================================================================

def generate_multi_speaker(
    script: str,
    voice_assignments: Dict[str, str],
    output_format: str = "mp3",
    seed: int = None
) -> Tuple[str, str]:
    """Generate multi-speaker audio by stitching individual lines."""
    import tempfile
    from pydub import AudioSegment
    import random

    # Debug: show what voice assignments we received
    print(f"DEBUG: voice_assignments = {voice_assignments}")

    lines = parse_dialog(script)
    if not lines:
        return None, "No dialog to generate"

    segments = []
    status_lines = []
    status_lines.append(f"Voice Assignments: {voice_assignments}")
    if seed is not None:
        status_lines.append(f"Seed: {seed}")
    status_lines.append("")

    # Use provided seed or generate random one
    if seed is None:
        seed = random.randint(0, 2**32 - 1)

    for i, line in enumerate(lines):
        speaker = line['speaker']
        text = line['text']
        voice = voice_assignments.get(speaker, "af_bella")

        # Increment seed for each line for variation
        line_seed = seed + i

        status_lines.append(f"[{i+1}/{len(lines)}] {speaker} ({voice}, seed={line_seed}): {text[:50]}...")

        try:
            # Build request payload
            payload = {
                "model": "tts-1",
                "voice": voice,
                "input": text,
                "response_format": "wav"
            }

            # Add seed if backend supports it (VoxCPM, etc.)
            if seed is not None:
                payload["seed"] = line_seed

            response = requests.post(
                f"{TTS_API_URL}/v1/audio/speech",
                json=payload,
                timeout=120
            )
            response.raise_for_status()

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

    combined = segments[0]
    gap = AudioSegment.silent(duration=100)  # Reduced from 300ms to 100ms for natural pacing

    for segment in segments[1:]:
        combined += gap + segment

    output_path = OUTPUT_DIR / f"production_{hash(script)}.{output_format}"
    combined.export(str(output_path), format=output_format)

    status = "\n".join(status_lines) + f"\n\nGenerated: {output_path}"
    return str(output_path), status


# =============================================================================
# BACKEND DETECTION
# =============================================================================

def detect_backend_profile(url: str, name: str) -> str:
    """Try to detect which model profile to use based on backend type."""
    name_lower = name.lower()

    if "kokoro" in name_lower:
        return "kokoro"
    elif "elevenlabs" in name_lower or "11labs" in name_lower:
        return "elevenlabs"
    elif "openai" in name_lower:
        return "openai"
    elif "coqui" in name_lower:
        return "coqui"

    try:
        response = requests.get(f"{url}/v1/voices", timeout=2)
        if response.status_code == 200:
            data = response.json()
            voices = data.get("voices", [])
            if voices:
                if any(v.startswith(("af_", "am_", "bf_", "bm_")) for v in voices):
                    return "kokoro"
    except:
        pass

    return "generic"


def auto_detect_tts_backends() -> Tuple[Dict[str, dict], str]:
    """Scan network for TTS backends and return discovered backends."""
    import socket

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
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.5)
            result = sock.connect_ex((host, port))
            sock.close()

            if result != 0:
                continue

            response = requests.get(f"{url}/v1/voices", timeout=2)
            if response.status_code == 200:
                data = response.json()
                voices = data.get("voices", [])

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


# =============================================================================
# GRADIO INTERFACE
# =============================================================================

def build_interface():
    """Build simplified single-page Gradio interface."""

    # Define switch_backend function at top level so both Studio and Settings can use it
    def switch_backend(backend_key):
        """Switch active backend and update global TTS_API_URL."""
        global TTS_API_URL, CONFIG

        if backend_key not in CONFIG.get("tts_backends", {}):
            return f"❌ Backend '{backend_key}' not found!"

        backend = CONFIG["tts_backends"][backend_key]
        TTS_API_URL = backend["url"]
        CONFIG["tts_active_backend"] = backend_key

        # Save config
        with open(CONFIG_FILE, 'w') as f:
            json.dump(CONFIG, f, indent=2)

        # Get voices from new backend
        voices = get_available_voices()
        voice_count = len(voices)
        sample_voices = ", ".join(voices[:5])
        if len(voices) > 5:
            sample_voices += f"... (+{len(voices) - 5} more)"

        return f"✅ Switched to: {backend['name']}\n\n🔌 URL: {backend['url']}\n🎤 Found {voice_count} voices: {sample_voices}\n\n⚠️ Click '🔍 Auto-Detect Speakers' below to refresh voice dropdowns!"

    with gr.Blocks(title="TTS Production Studio") as app:
        gr.Markdown("# 🎬 TTS Production Studio")
        gr.Markdown("Multi-speaker TTS - paste text, assign voices, generate audio")

        voice_assignments_state = gr.State({})

        with gr.Tabs():
            # ===== MAIN STUDIO TAB (SINGLE PAGE) =====
            with gr.Tab("🎙️ Studio"):

                # Backend Switcher (at top for easy access)
                with gr.Row():
                    backend_switcher = gr.Dropdown(
                        label="🔌 Active TTS Backend",
                        choices=list(CONFIG.get("tts_backends", {}).keys()) or ["No backends configured"],
                        value=CONFIG.get("tts_active_backend", ""),
                        scale=2,
                        info="Switch between saved TTS backends - add/edit in Settings tab"
                    )
                    switch_btn = gr.Button("↻ Switch", variant="secondary")

                backend_switch_status = gr.Textbox(
                    label="Backend Status",
                    max_lines=5,
                    visible=False
                )

                gr.Markdown("---")

                # Section 1: Input
                gr.Markdown("## 1️⃣ Input Your Script")

                with gr.Row():
                    with gr.Column(scale=4):
                        script_editor = gr.Textbox(
                            label="Script",
                            placeholder="Paste your text here...\n\nFor multi-speaker, format as:\nSpeaker1: Hello there!\nSpeaker2: Welcome!",
                            lines=15,
                            max_lines=25
                        )
                    with gr.Column(scale=1):
                        file_upload = gr.File(
                            label="Or Upload File",
                            file_types=[".txt", ".pdf"]
                        )
                        upload_btn = gr.Button("📂 Load File")

                # Section 2: AI Tools (Optional)
                with gr.Accordion("🤖 AI Tools (Optional)", open=False):
                    gr.Markdown("Use AI to clean up or expand your script")

                    with gr.Row():
                        cleanup_btn = gr.Button("✨ Cleanup Format")
                        expand_direction = gr.Radio(
                            choices=["before", "after"],
                            value="after",
                            label="Expand Direction"
                        )
                        expand_btn = gr.Button("📝 Expand Dialog")

                    ai_status = gr.Textbox(label="AI Status", max_lines=3)

                gr.Markdown("---")

                # Section 3: Voice Assignment
                gr.Markdown("## 2️⃣ Assign Voices to Speakers")

                with gr.Row():
                    detect_btn = gr.Button("🔍 Auto-Detect Speakers", variant="primary")

                speakers_detected = gr.Textbox(
                    label="Detected Speakers",
                    max_lines=2
                )

                gr.Markdown("**Voice Assignments** - Select voice for each speaker")

                # Create 10 speaker/voice dropdown pairs (will show as many as needed)
                voice_choices = get_available_voices()
                speaker_dropdowns = []

                for i in range(10):
                    with gr.Row(visible=False) as row:
                        speaker_label = gr.Textbox(
                            label=f"Speaker {i+1}",
                            interactive=False,
                            scale=1
                        )
                        voice_dropdown = gr.Dropdown(
                            label="Voice",
                            choices=voice_choices,
                            value=voice_choices[i % len(voice_choices)] if voice_choices else "af_bella",
                            scale=2,
                            allow_custom_value=True,  # Enable type-to-search filtering
                            filterable=True  # Make dropdown searchable
                        )
                    speaker_dropdowns.append((row, speaker_label, voice_dropdown))

                # Hidden state for voice assignments
                speaker_voice_map = gr.State({})

                # Debug: Show current voice map
                voice_map_debug = gr.Textbox(
                    label="🔍 Debug: Current Voice Assignments",
                    max_lines=3,
                    interactive=False
                )

                with gr.Accordion("Available Voices", open=False):
                    available_voices_list = gr.Textbox(
                        label="🎤 All Available Voices",
                        lines=8,
                        max_lines=10,
                        interactive=False,
                        value=", ".join(voice_choices)
                    )
                    refresh_voices_btn = gr.Button("🔄 Refresh Voice List")

                gr.Markdown("---")

                # Section 4: Generate
                gr.Markdown("## 3️⃣ Generate Audio")

                with gr.Row():
                    output_format = gr.Dropdown(
                        label="Format",
                        choices=["mp3", "wav"],
                        value="mp3"
                    )
                    seed_input = gr.Number(
                        label="Seed (optional, for VoxCPM)",
                        value=None,
                        precision=0,
                        info="Leave empty for random seed"
                    )
                    generate_btn = gr.Button("🎬 Generate", variant="primary", scale=2)

                audio_output = gr.Audio(label="Generated Audio")
                status_output = gr.Textbox(label="Status", max_lines=10)

                # Event handlers
                def switch_and_refresh_voices(backend_key):
                    """Switch backend and return updated voices for dropdown refresh."""
                    status = switch_backend(backend_key)
                    voices = get_available_voices()
                    # Return status and instruction to refresh dropdowns
                    return status, f"🔄 Backend switched! Click 'Auto-Detect Speakers' to refresh voice assignments with {len(voices)} available voices."

                switch_btn.click(
                    fn=switch_and_refresh_voices,
                    inputs=[backend_switcher],
                    outputs=[backend_switch_status, speakers_detected]
                ).then(
                    fn=lambda: gr.update(visible=True),
                    outputs=[backend_switch_status]
                )

                # Auto-load when file is selected (no button click needed)
                file_upload.change(
                    fn=import_from_file,
                    inputs=[file_upload],
                    outputs=[script_editor]
                )

                # Keep button for manual trigger if needed
                upload_btn.click(
                    fn=import_from_file,
                    inputs=[file_upload],
                    outputs=[script_editor]
                )

                cleanup_btn.click(
                    fn=lambda s: ai_cleanup_dialog(s, CONFIG),
                    inputs=[script_editor],
                    outputs=[script_editor]
                )

                expand_btn.click(
                    fn=lambda s, d: ai_expand_dialog(s, d, CONFIG),
                    inputs=[script_editor, expand_direction],
                    outputs=[script_editor]
                )

                def analyze_and_assign(script):
                    try:
                        speakers = get_speakers(script)
                        assignments = create_voice_assignments(speakers)
                        speaker_list = ", ".join(speakers) if speakers else "No speakers detected"

                        print(f"DEBUG: Found {len(speakers)} speakers: {speakers}")
                        print(f"DEBUG: Assignments: {assignments}")

                        # Get current backend's voices to update dropdown choices
                        current_voices = get_available_voices()
                        print(f"DEBUG: Got {len(current_voices)} voices from backend")

                        # Prepare outputs: show/hide rows, set speaker names and voices
                        outputs = []
                        for i in range(10):
                            if i < len(speakers):
                                speaker = list(speakers)[i]
                                voice = assignments.get(speaker, current_voices[0] if current_voices else "af_bella")
                                print(f"DEBUG: Row {i}: speaker={speaker}, voice={voice}")
                                outputs.extend([
                                    gr.update(visible=True),  # Show row
                                    gr.update(value=speaker),  # Speaker name
                                    gr.update(choices=current_voices, value=voice)  # Updated choices + selected voice
                                ])
                            else:
                                outputs.extend([
                                    gr.update(visible=False),  # Hide row
                                    gr.update(value=""),
                                    gr.update(choices=current_voices, value=current_voices[0] if current_voices else "af_bella")
                                ])

                        outputs.append(assignments)  # Update state
                        outputs.append(speaker_list)  # Update detected speakers text
                        outputs.append(str(assignments))  # Update debug display

                        print(f"DEBUG: Returning {len(outputs)} outputs")
                        return outputs
                    except Exception as e:
                        print(f"ERROR in analyze_and_assign: {e}")
                        import traceback
                        traceback.print_exc()
                        raise

                def update_voice_map(*dropdown_values):
                    """Update voice map when any dropdown changes."""
                    # dropdown_values contains: (speaker0, voice0, speaker1, voice1, ...)
                    voice_map = {}
                    for i in range(0, len(dropdown_values), 2):
                        speaker = dropdown_values[i]
                        if i + 1 < len(dropdown_values):
                            voice = dropdown_values[i + 1]
                            if speaker:  # Only add if speaker name exists
                                voice_map[speaker] = voice
                    print(f"DEBUG update_voice_map: {voice_map}")
                    debug_str = str(voice_map) if voice_map else "No assignments yet"
                    return voice_map, debug_str

                def show_voices():
                    """Format voices list for display."""
                    voices = get_available_voices()
                    return ", ".join(voices)

                # Outputs for detect button: all rows + labels + dropdowns + state + detected text + debug
                detect_outputs = []
                for row, label, dropdown in speaker_dropdowns:
                    detect_outputs.extend([row, label, dropdown])
                detect_outputs.extend([speaker_voice_map, speakers_detected, voice_map_debug])

                detect_btn.click(
                    fn=analyze_and_assign,
                    inputs=[script_editor],
                    outputs=detect_outputs
                )

                refresh_voices_btn.click(
                    fn=show_voices,
                    outputs=[available_voices_list]
                )

                # Update voice map when any dropdown changes
                dropdown_inputs = []
                for row, label, dropdown in speaker_dropdowns:
                    dropdown_inputs.extend([label, dropdown])

                for row, label, dropdown in speaker_dropdowns:
                    dropdown.change(
                        fn=update_voice_map,
                        inputs=dropdown_inputs,
                        outputs=[speaker_voice_map, voice_map_debug]
                    )

                generate_btn.click(
                    fn=generate_multi_speaker,
                    inputs=[script_editor, speaker_voice_map, output_format, seed_input],
                    outputs=[audio_output, status_output]
                )

            # ===== SETTINGS TAB =====
            with gr.Tab("⚙️ Settings"):
                gr.Markdown("# Configuration")
                gr.Markdown("Configure TTS backend and AI assistant")

                # TTS Backend
                gr.Markdown("## TTS Backend")

                with gr.Row():
                    auto_detect_btn = gr.Button("🔍 Auto-Detect", variant="primary")

                detected_backends = gr.State({})
                detection_status = gr.Textbox(
                    label="Detection Results",
                    max_lines=15,
                    visible=False
                )

                backend_select = gr.Dropdown(
                    label="Active Backend",
                    choices=["manual"],
                    value="manual"
                )

                with gr.Accordion("Add/Edit Backend", open=True):
                    backend_name = gr.Textbox(
                        label="Backend Name",
                        value="",
                        placeholder="e.g., 'VoxCPM Scorpy', 'Kokoro Local', 'VibeVoice'"
                    )

                    backend_url = gr.Textbox(
                        label="TTS API URL",
                        value=TTS_API_URL,
                        placeholder="http://localhost:8765"
                    )

                    gr.Markdown("### Model Profile (Chunking)")
                    profile_select = gr.Dropdown(
                        label="Profile",
                        choices=list(MODEL_PROFILES.keys()),
                        value="generic"
                    )

                    with gr.Row():
                        max_words = gr.Number(
                            label="Max Words/Chunk",
                            value=250
                        )
                        optimal_chunk = gr.Number(
                            label="Optimal Chunk (chars)",
                            value=500
                        )

                    test_btn = gr.Button("🧪 Test Connection")
                    test_status = gr.Textbox(label="Test Results", max_lines=5)

                gr.Markdown("---")

                # AI Backend
                gr.Markdown("## AI Assistant (Optional)")

                ai_backend_select = gr.Radio(
                    label="AI Backend",
                    choices=["disabled", "lmstudio", "ollama", "openai", "openrouter"],
                    value=CONFIG.get("ai_backend", "disabled")
                )

                with gr.Accordion("LM Studio", open=False) as lmstudio_acc:
                    lmstudio_endpoint = gr.Textbox(
                        label="Endpoint",
                        value=CONFIG.get("lmstudio_endpoint", "http://localhost:1234/v1")
                    )
                    lmstudio_model = gr.Textbox(
                        label="Model",
                        value=CONFIG.get("lmstudio_model", "openai/gpt-oss-20b")
                    )

                output_dir_input = gr.Textbox(
                    label="Output Directory",
                    value=str(OUTPUT_DIR)
                )

                save_btn = gr.Button("💾 Save Settings", variant="primary")
                settings_status = gr.Textbox(label="Status", max_lines=5)

                # Settings event handlers
                def handle_auto_detect():
                    backends, status = auto_detect_tts_backends()
                    choices = ["manual"] + list(backends.keys())
                    return backends, status, gr.Dropdown(choices=choices), gr.Textbox(visible=True)

                def handle_profile_select(profile_name):
                    if profile_name in MODEL_PROFILES:
                        profile = MODEL_PROFILES[profile_name]
                        return profile["max_words"], profile["optimal_chunk"]
                    return 250, 500

                def handle_backend_select(backend_id, backends_dict):
                    if backend_id == "manual":
                        return TTS_API_URL, "generic", 250, 500
                    elif backend_id in backends_dict:
                        backend = backends_dict[backend_id]
                        profile = backend.get("profile", "generic")
                        profile_data = MODEL_PROFILES.get(profile, MODEL_PROFILES["generic"])
                        return backend["url"], profile, profile_data["max_words"], profile_data["optimal_chunk"]
                    return TTS_API_URL, "generic", 250, 500

                def save_all_settings(backend_name_input, tts_url, out_dir, profile, max_w, opt_chunk, ai_backend, lms_ep, lms_mdl):
                    global TTS_API_URL, OUTPUT_DIR, CONFIG

                    # Use provided name or generate one from URL
                    if not backend_name_input or backend_name_input.strip() == "":
                        backend_name_input = f"Backend {tts_url.split('/')[-1]}"

                    TTS_API_URL = tts_url
                    OUTPUT_DIR = Path(out_dir)
                    OUTPUT_DIR.mkdir(exist_ok=True)

                    if "tts_backends" not in CONFIG:
                        CONFIG["tts_backends"] = {}

                    # Use name as key (sanitized)
                    backend_key = backend_name_input.lower().replace(" ", "_")

                    CONFIG["tts_backends"][backend_key] = {
                        "name": backend_name_input,
                        "url": tts_url,
                        "type": "openai-compatible",
                        "profile": profile,
                        "max_words": int(max_w),
                        "optimal_chunk": int(opt_chunk)
                    }
                    CONFIG["tts_active_backend"] = backend_key
                    CONFIG["ai_backend"] = ai_backend

                    # Get updated voice list from new backend
                    new_voices = get_available_voices(tts_url)
                    CONFIG["lmstudio_endpoint"] = lms_ep
                    CONFIG["lmstudio_model"] = lms_mdl

                    with open(CONFIG_FILE, 'w') as f:
                        json.dump(CONFIG, f, indent=2)

                    voice_count = len(new_voices)
                    sample_voices = ", ".join(new_voices[:5])
                    if len(new_voices) > 5:
                        sample_voices += f"... (+{len(new_voices) - 5} more)"

                    status_msg = f"✅ Settings saved & switched to: {backend_name_input}\n\nTTS: {tts_url}\nProfile: {profile} ({int(max_w)} words)\nAI: {ai_backend}\n\n🎤 Found {voice_count} voices: {sample_voices}\n\n⚠️ Go to Studio tab and click '🔍 Auto-Detect Speakers' to refresh voice dropdowns!"

                    # Return: status message, updated dropdown choices, new selected value
                    backend_choices = list(CONFIG["tts_backends"].keys())
                    return status_msg, gr.update(choices=backend_choices, value=backend_key)

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

                test_btn.click(
                    fn=test_tts_backend,
                    inputs=[backend_url],
                    outputs=[test_status]
                )

                save_btn.click(
                    fn=save_all_settings,
                    inputs=[
                        backend_name, backend_url, output_dir_input, profile_select, max_words, optimal_chunk,
                        ai_backend_select, lmstudio_endpoint, lmstudio_model
                    ],
                    outputs=[settings_status, backend_switcher]
                )

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
