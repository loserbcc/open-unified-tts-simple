"""Open Unified TTS Simple - Single backend with unlimited length.

Drop-in OpenAI TTS API with smart chunking and seamless stitching.
Configure BACKEND env var to switch between kokoro/voxcpm/vibevoice.
"""
import io
import logging
import os
import re
import subprocess
import tempfile
from pathlib import Path
from typing import List, Literal

import numpy as np
import requests
from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel
from scipy.io import wavfile

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Configuration from environment
BACKEND = os.environ.get("TTS_BACKEND", "kokoro")
BACKEND_URL = os.environ.get("BACKEND_URL", "http://localhost:8880")

# Backend profiles - chunk limits for each backend
PROFILES = {
    "kokoro": {"max_words": 200, "max_chars": 1200, "crossfade_ms": 30},
    "voxcpm": {"max_words": 150, "max_chars": 800, "crossfade_ms": 50},
    "vibevoice": {"max_words": 100, "max_chars": 500, "crossfade_ms": 100},
}

app = FastAPI(title="Open Unified TTS Simple", version="1.0.0")


class SpeechRequest(BaseModel):
    model: str = "tts-1"
    input: str
    voice: str
    response_format: Literal["mp3", "opus", "aac", "flac", "wav", "pcm"] = "mp3"
    speed: float = 1.0


# =============================================================================
# CHUNKING - Split long text at natural boundaries
# =============================================================================

def estimate_words(text: str) -> int:
    return len(text.split())


def chunk_text(text: str) -> List[str]:
    """Split text into chunks respecting backend limits."""
    profile = PROFILES.get(BACKEND, PROFILES["kokoro"])
    max_chars = profile["max_chars"]
    max_words = profile["max_words"]

    if len(text) <= max_chars and estimate_words(text) <= max_words:
        return [text]

    logger.info(f"Chunking: {len(text)} chars, {estimate_words(text)} words")

    chunks = []
    current_chunk = ""
    sentences = re.split(r'([.!?]+\s+)', text)

    for i in range(0, len(sentences), 2):
        sentence = sentences[i]
        separator = sentences[i + 1] if i + 1 < len(sentences) else ""
        full_sentence = sentence + separator

        # Handle overly long sentences
        if len(full_sentence) > max_chars or estimate_words(full_sentence) > max_words:
            if current_chunk.strip():
                chunks.append(current_chunk.strip())
                current_chunk = ""
            # Force split by words
            words = full_sentence.split()
            for j in range(0, len(words), max_words):
                chunks.append(" ".join(words[j:j + max_words]))
            continue

        test_chunk = current_chunk + full_sentence
        if len(test_chunk) > max_chars or estimate_words(test_chunk) > max_words:
            if current_chunk.strip():
                chunks.append(current_chunk.strip())
            current_chunk = full_sentence
        else:
            current_chunk += full_sentence

    if current_chunk.strip():
        chunks.append(current_chunk.strip())

    logger.info(f"Split into {len(chunks)} chunks")
    return chunks


# =============================================================================
# STITCHING - Seamless audio joining with crossfade
# =============================================================================

def stitch_audio(chunks: List[bytes], crossfade_ms: int = 50) -> bytes:
    """Stitch audio chunks with seamless crossfades."""
    if not chunks:
        return b""
    if len(chunks) == 1:
        return normalize_audio(chunks[0])

    logger.info(f"Stitching {len(chunks)} chunks with {crossfade_ms}ms crossfade")

    normalized = [normalize_audio(c) for c in chunks]
    result = load_wav(normalized[0])
    sample_rate = result['rate']

    for chunk_bytes in normalized[1:]:
        next_audio = load_wav(chunk_bytes)
        if next_audio['rate'] != sample_rate:
            next_audio = resample(next_audio, sample_rate)
        result = crossfade(result, next_audio, crossfade_ms)

    return wav_to_bytes(result)


def normalize_audio(wav_bytes: bytes) -> bytes:
    """Normalize audio levels."""
    audio = load_wav(wav_bytes)
    max_val = np.max(np.abs(audio['data']))
    if max_val == 0:
        return wav_bytes
    target = 0.9 * 32767 if audio['data'].dtype == np.int16 else 0.9
    audio['data'] = (audio['data'] * (target / max_val)).astype(audio['data'].dtype)
    return wav_to_bytes(audio)


def load_wav(wav_bytes: bytes) -> dict:
    with io.BytesIO(wav_bytes) as f:
        rate, data = wavfile.read(f)
    return {'rate': rate, 'data': data}


def wav_to_bytes(audio: dict) -> bytes:
    buf = io.BytesIO()
    wavfile.write(buf, audio['rate'], audio['data'])
    return buf.getvalue()


def crossfade(a1: dict, a2: dict, ms: int) -> dict:
    rate = a1['rate']
    samples = min(int((ms / 1000.0) * rate), len(a1['data']), len(a2['data']))

    if samples <= 0:
        return {'rate': rate, 'data': np.concatenate([a1['data'], a2['data']])}

    fade_out = np.linspace(1.0, 0.0, samples)
    fade_in = np.linspace(0.0, 1.0, samples)

    pre = a1['data'][:-samples]
    cross = a1['data'][-samples:] * fade_out + a2['data'][:samples] * fade_in
    post = a2['data'][samples:]

    if a1['data'].dtype == np.int16:
        cross = np.clip(cross, -32768, 32767).astype(np.int16)

    return {'rate': rate, 'data': np.concatenate([pre, cross, post])}


def resample(audio: dict, target_rate: int) -> dict:
    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
        wavfile.write(f, audio['rate'], audio['data'])
        inp = f.name
    out = inp.replace('.wav', '_rs.wav')
    try:
        subprocess.run(['ffmpeg', '-y', '-i', inp, '-ar', str(target_rate), out], capture_output=True)
        with open(out, 'rb') as f:
            return load_wav(f.read())
    finally:
        Path(inp).unlink(missing_ok=True)
        Path(out).unlink(missing_ok=True)


def convert_format(wav_bytes: bytes, fmt: str) -> bytes:
    """Convert WAV to requested format."""
    if fmt == "wav":
        return wav_bytes

    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
        f.write(wav_bytes)
        inp = f.name
    out = inp.rsplit('.', 1)[0] + f".{fmt}"

    try:
        cmd = ["ffmpeg", "-y", "-i", inp]
        if fmt == "mp3":
            cmd.extend(["-codec:a", "libmp3lame", "-q:a", "2"])
        elif fmt == "opus":
            cmd.extend(["-codec:a", "libopus", "-b:a", "128k"])
        elif fmt == "flac":
            cmd.extend(["-codec:a", "flac"])
        cmd.append(out)

        subprocess.run(cmd, capture_output=True, timeout=30)
        with open(out, "rb") as f:
            return f.read()
    finally:
        Path(inp).unlink(missing_ok=True)
        Path(out).unlink(missing_ok=True)


# =============================================================================
# BACKEND GENERATION
# =============================================================================

def generate_tts(text: str, voice: str) -> bytes:
    """Generate TTS from backend (always WAV for stitching)."""
    response = requests.post(
        f"{BACKEND_URL}/v1/audio/speech",
        json={"model": "tts-1", "voice": voice, "input": text, "response_format": "wav"},
        timeout=120,
    )
    response.raise_for_status()
    return response.content


# =============================================================================
# API ENDPOINTS
# =============================================================================

@app.get("/")
async def root():
    return {
        "service": "Open Unified TTS Simple",
        "backend": BACKEND,
        "backend_url": BACKEND_URL,
        "unlimited_length": True,
    }


@app.get("/health")
async def health():
    try:
        r = requests.get(f"{BACKEND_URL}/health", timeout=2)
        return {"status": "ok", "backend": BACKEND, "backend_status": r.status_code == 200}
    except Exception:
        return {"status": "ok", "backend": BACKEND, "backend_status": False}


@app.get("/v1/models")
async def list_models():
    return {"object": "list", "data": [{"id": "tts-1", "object": "model"}]}


@app.get("/v1/voices")
async def list_voices():
    try:
        r = requests.get(f"{BACKEND_URL}/v1/audio/voices", timeout=5)
        return r.json()
    except Exception:
        return {"voices": [], "backend": BACKEND}


@app.post("/v1/audio/speech")
async def create_speech(request: SpeechRequest):
    """Generate unlimited-length speech with automatic chunking."""
    profile = PROFILES.get(BACKEND, PROFILES["kokoro"])

    # Check if chunking needed
    needs_chunk = (
        estimate_words(request.input) > profile["max_words"] or
        len(request.input) > profile["max_chars"]
    )

    try:
        if needs_chunk:
            # Chunk, generate each, stitch
            chunks = chunk_text(request.input)
            audio_chunks = []
            for i, chunk in enumerate(chunks):
                logger.info(f"Generating chunk {i+1}/{len(chunks)}")
                audio_chunks.append(generate_tts(chunk, request.voice))

            wav_bytes = stitch_audio(audio_chunks, profile["crossfade_ms"])
            output = convert_format(wav_bytes, request.response_format)
        else:
            # Direct generation
            logger.info(f"Direct generation: {len(request.input)} chars")
            wav_bytes = generate_tts(request.input, request.voice)
            output = convert_format(wav_bytes, request.response_format)

        media_types = {
            "mp3": "audio/mpeg", "wav": "audio/wav", "opus": "audio/opus",
            "flac": "audio/flac", "aac": "audio/aac", "pcm": "audio/pcm",
        }
        return Response(content=output, media_type=media_types.get(request.response_format, "audio/mpeg"))

    except Exception as e:
        logger.exception(f"TTS failed: {e}")
        raise HTTPException(500, f"Generation failed: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", "8765"))
    logger.info(f"Starting Open Unified TTS Simple on port {port}")
    logger.info(f"Backend: {BACKEND} @ {BACKEND_URL}")
    uvicorn.run(app, host="0.0.0.0", port=port)
