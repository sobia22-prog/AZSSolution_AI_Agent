import os
import sys
import time
import subprocess
import shutil
import urllib.request
import json

# ==========================================
# CONFIGURATION
# ==========================================
PORT_PROXY = 8020
PORT_XTTS = 8021
SPEAKERS_DIR = "/content/speakers"
DEFAULT_VOICE_FILE = "my_voice.wav"  # Name of your voice file
DEFAULT_LANGUAGE = "en"  # Use "en" for Roman Urdu, or "ar" for Urdu Script (Arabic characters)

# Create speakers directory if it doesn't exist
os.makedirs(SPEAKERS_DIR, exist_ok=True)

def kill_existing_processes():
    """Finds and kills any processes holding ports PORT_PROXY or PORT_XTTS."""
    print("\n" + "="*80)
    print("STEP 0: Checking for orphan processes on ports...")
    print("="*80)
    
    for port in [PORT_PROXY, PORT_XTTS]:
        try:
            # Find PIDs using the port
            cmd = f"fuser -n tcp {port} 2>/dev/null"
            output = subprocess.check_output(cmd, shell=True).decode().strip()
            if output:
                pids = [pid.strip() for pid in output.split() if pid.strip()]
                for pid in pids:
                    print(f"Port {port} is in use by PID {pid}. Terminating process...")
                    subprocess.call(f"kill -9 {pid}", shell=True)
                time.sleep(1)
        except Exception:
            pass
    print("Ports cleared.")

def check_and_setup_environment():
    """Checks if the Python 3.10 virtual environment exists. If not, rebuilds it."""
    venv_path = "/content/venv310"
    if not os.path.exists(venv_path):
        print("\n" + "="*80)
        print("ENVIRONMENT NOT FOUND! Rebuilding Python 3.10 virtual environment...")
        print("This is normal if your Google Colab runtime was recently reset or recycled.")
        print("="*80)
        
        try:
            # 1. Install Python 3.10 and system dependencies
            print("Installing Python 3.10 and system dependencies (portaudio)...")
            subprocess.check_call("sudo apt-get update -y", shell=True)
            subprocess.check_call("sudo apt-get install python3.10 python3.10-venv python3.10-dev portaudio19-dev -y", shell=True)
            
            # 2. Create virtual environment
            print("Creating virtual environment at /content/venv310...")
            subprocess.check_call("python3.10 -m venv /content/venv310", shell=True)
            
            # 3. Upgrade pip
            print("Upgrading pip inside venv...")
            subprocess.check_call("/content/venv310/bin/pip install --upgrade pip", shell=True)
            
            # 4. Install PyTorch with CUDA support (version 2.5.1 to avoid PyTorch 2.6 weights_only=True load issues)
            print("Installing PyTorch (CUDA 12.1)...")
            subprocess.check_call("/content/venv310/bin/pip install torch==2.5.1 torchaudio==2.5.1 --index-url https://download.pytorch.org/whl/cu121", shell=True)
            
            # 5. Install PyAudio
            print("Installing PyAudio...")
            subprocess.check_call("/content/venv310/bin/pip install pyaudio", shell=True)
            
            # 6. Install xtts-api-server
            print("Installing xtts-api-server...")
            subprocess.check_call("/content/venv310/bin/pip install xtts-api-server", shell=True)
            
            print("\nEnvironment successfully rebuilt!")
            print("="*80 + "\n")
        except Exception as e:
            print(f"CRITICAL ERROR during environment rebuild: {e}")
            sys.exit(1)

# Ensure required libraries are installed in the global context for the proxy script
try:
    import fastapi
    import uvicorn
    import httpx
    import pyngrok
except ImportError:
    print("Installing required proxy dependencies (fastapi, uvicorn, httpx, pyngrok)...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "fastapi", "uvicorn", "httpx", "pyngrok"])
    import fastapi
    import uvicorn
    import httpx
    import pyngrok

from fastapi import FastAPI, Request, Response
from fastapi.responses import StreamingResponse
from pyngrok import ngrok

print("\n" + "="*80)
print(f"STEP 1: Checking Speaker reference files in {SPEAKERS_DIR}")
print("="*80)

# Check for custom-voice files in Drive
possible_drive_voices = [
    "/content/drive/MyDrive/custom-voice-2.mp3",
    "/content/drive/MyDrive/custom-voice-2.wav",
    "/content/drive/MyDrive/my_voice.mp3",
    "/content/drive/MyDrive/my_voice.wav"
]

copied_any = False
for path in possible_drive_voices:
    if os.path.exists(path):
        target_name = os.path.basename(path)
        if target_name.endswith(".mp3"):
            # Convert directly from Drive to target WAV
            target_wav_name = target_name[:-4] + ".wav"
            target_wav = os.path.join(SPEAKERS_DIR, target_wav_name)
            print(f"Found MP3 in Drive: {path} -> Converting to WAV: {target_wav}")
            try:
                subprocess.check_call([
                    "ffmpeg", "-y", "-i", path, 
                    "-ac", "1", "-ar", "22050", 
                    target_wav
                ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                copied_any = True
            except Exception as e:
                print(f"Error converting Drive file: {e}")
        else:
            # WAV file - copy directly
            target_path = os.path.join(SPEAKERS_DIR, target_name)
            print(f"Found WAV in Drive: {path} -> Copying to {target_path}")
            shutil.copy(path, target_path)
            copied_any = True

# Convert any existing mp3 files in the SPEAKERS_DIR itself
for file in os.listdir(SPEAKERS_DIR):
    if file.endswith(".mp3"):
        mp3_path = os.path.join(SPEAKERS_DIR, file)
        wav_name = file[:-4] + ".wav"
        wav_path = os.path.join(SPEAKERS_DIR, wav_name)
        print(f"Converting local MP3 to WAV: {file} -> {wav_name}")
        try:
            subprocess.check_call([
                "ffmpeg", "-y", "-i", mp3_path, 
                "-ac", "1", "-ar", "22050", 
                wav_path
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            os.remove(mp3_path)  # Delete MP3 so XTTS only sees WAV
        except Exception as e:
            print(f"Error converting local {file}: {e}")

# List speakers currently in the folder
current_speakers = [f for f in os.listdir(SPEAKERS_DIR) if f.endswith('.wav')]
print(f"Current speakers in folder (WAV format): {current_speakers}")

if not current_speakers:
    print("\nWARNING: No speaker WAV files found in /content/speakers!")
    print("Writing a fallback silent WAV so the server can start...")
    import wave
    dummy_path = os.path.join(SPEAKERS_DIR, "my_voice.wav")
    with wave.open(dummy_path, 'wb') as wav_file:
        wav_file.setparams((1, 2, 24000, 24000 * 2, 'NONE', 'not compressed'))
        wav_file.writeframes(b'\x00' * (24000 * 2 * 2))
    current_speakers = ["my_voice.wav"]

# ==========================================
# FASTAPI PROXY IMPLEMENTATION
# ==========================================
app = FastAPI(title="XTTS OpenAI-Compatible Proxy")
client = httpx.AsyncClient(base_url=f"http://localhost:{PORT_XTTS}")

def extract_pcm_from_wav(wav_bytes: bytes) -> bytes:
    """Parses WAV bytes and returns raw 16-bit PCM bytes (stripping header)."""
    if len(wav_bytes) < 12:
        return wav_bytes
    
    # Check if it's a RIFF WAVE file
    if wav_bytes[0:4] != b"RIFF" or wav_bytes[8:12] != b"WAVE":
        return wav_bytes
        
    idx = 12
    while idx + 8 <= len(wav_bytes):
        chunk_id = wav_bytes[idx:idx+4]
        try:
            chunk_size = int.from_bytes(wav_bytes[idx+4:idx+8], byteorder="little")
        except Exception:
            break
            
        if chunk_id == b"data":
            # Found data chunk! Return only the raw PCM payload
            return wav_bytes[idx+8 : idx+8+chunk_size]
            
        idx += 8 + chunk_size
        
    # Fallback to standard 44 bytes if chunk parsing fails
    if len(wav_bytes) > 44:
        return wav_bytes[44:]
    return wav_bytes

@app.post("/v1/audio/speech")
@app.post("/v1/audio/speech/")
async def openai_tts_proxy(request: Request):
    """Intercepts OpenAI-format TTS requests and maps them to xtts-api-server."""
    try:
        body = await request.json()
    except Exception:
        body = {}
        
    text = body.get("input", "")
    voice = body.get("voice", DEFAULT_VOICE_FILE)
    lang = body.get("language", DEFAULT_LANGUAGE)
    
    # Extract filename from voice parameter (in case of paths or names)
    voice_file = os.path.basename(voice)
    
    # Map .mp3 extension to .wav since the backend only indexes WAVs
    if voice_file.endswith(".mp3"):
        voice_file = voice_file[:-4] + ".wav"
        
    # Check if this voice exists in our speakers directory, otherwise fall back to the first available speaker
    available = [f for f in os.listdir(SPEAKERS_DIR) if f.endswith('.wav')]
    if voice_file not in available and available:
        print(f"Requested voice '{voice}' -> mapped to '{voice_file}' not found. Falling back to '{available[0]}'")
        voice_file = available[0]
        
    print(f"Proxying TTS Request: '{text[:50]}...' -> voice={voice_file}, lang={lang}")
    
    # Payload for xtts-api-server
    payload = {
        "text": text,
        "language": lang,
        "speaker_wav": voice_file
    }
    
    try:
        # Request full audio generation from xtts-api-server
        resp = await client.post("/tts_to_audio", json=payload, timeout=60.0)
        if resp.status_code != 200:
            # Try trailing slash as fallback
            resp = await client.post("/tts_to_audio/", json=payload, timeout=60.0)
    except Exception as e:
        print(f"Error calling XTTS backend: {e}")
        return Response(content=f"Proxy error connecting to XTTS backend: {str(e)}", status_code=502)
        
    if resp.status_code != 200:
        print(f"XTTS backend returned error: {resp.status_code} - {resp.text}")
        return Response(content=resp.content, status_code=resp.status_code)
        
    audio_data = resp.content
    response_format = body.get("response_format", "pcm")
    
    if response_format == "pcm":
        # Extract raw PCM bytes from the WAV returned by backend
        pcm_data = extract_pcm_from_wav(audio_data)
        return Response(content=pcm_data, media_type="audio/pcm")
    else:
        # Return standard WAV file
        return Response(content=audio_data, media_type="audio/wav")

@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD", "PATCH"])
async def reverse_proxy(request: Request, path: str):
    """Transparently reverse-proxies all other endpoints to xtts-api-server."""
    url = httpx.URL(path=request.url.path, query=request.url.query.encode("utf-8"))
    headers = dict(request.headers)
    headers.pop("host", None)  # Remove host to avoid routing issues
    
    try:
        req = client.build_request(
            request.method,
            url,
            headers=headers,
            content=request.stream()
        )
        resp = await client.send(req, stream=True)
    except Exception as e:
        return Response(content=f"Proxy forwarding error: {str(e)}", status_code=502)
        
    return StreamingResponse(
        resp.aiter_raw(),
        status_code=resp.status_code,
        headers=dict(resp.headers),
        background=resp.aclose
    )

def start_xtts_server():
    """Starts xtts-api-server in the background on port PORT_XTTS."""
    print("\n" + "="*80)
    print(f"STEP 2: Starting xtts-api-server on port {PORT_XTTS}")
    print("="*80)
    
    # Use the Python 3.10 virtual environment if available to avoid Python 3.12 coqpit crashes
    python_path = "/content/venv310/bin/python"
    if not os.path.exists(python_path):
        print("WARNING: /content/venv310/bin/python not found, falling back to system python. This might crash on Python 3.12+.")
        python_path = sys.executable
    else:
        print(f"Using Python 3.10 environment: {python_path}")
        
    # Apply coqpit compatibility patch
    print("Applying coqpit-config compatibility patch...")
    subprocess.call(f"{python_path} -m pip uninstall coqpit -y", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    subprocess.call(f"{python_path} -m pip install coqpit-config", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    # We specify MPLBACKEND=agg environment variable to prevent matplotlib window/GUI crashes in Colab
    env = os.environ.copy()
    env["MPLBACKEND"] = "agg"
    
    # Command to start the server
    # We use -sf to specify the speakers folder and -p to set the port
    cmd = [
        python_path, "-m", "xtts_api_server",
        "-sf", SPEAKERS_DIR,
        "-p", str(PORT_XTTS),
        "--listen"
    ]
    
    # Check if user had additional flags like streaming
    # We run it and let logs output to terminal
    process = subprocess.Popen(cmd, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    
    # Wait for the server to load the model
    print("Waiting for model to load (this can take 1-2 minutes)...")
    loaded = False
    for line in iter(process.stdout.readline, ""):
        print(line.strip())
        if "Model successfully loaded" in line or "Uvicorn running on" in line:
            loaded = True
            break
        if process.poll() is not None:
            print(f"ERROR: xtts-api-server process terminated with exit code {process.returncode}")
            sys.exit(1)
            
    # Continue printing logs in background thread
    import threading
    def log_reader():
        for line in iter(process.stdout.readline, ""):
            pass # Keep reading so buffer doesn't fill up
    threading.Thread(target=log_reader, daemon=True).start()
    
    print("\nXTTS Backend Loaded Successfully!")

def start_proxy_server():
    """Starts the FastAPI proxy in a background thread."""
    print("\n" + "="*80)
    print(f"STEP 3: Starting OpenAI-Compatible Proxy on port {PORT_PROXY}")
    print("="*80)
    
    import threading
    def run_uvicorn():
        uvicorn.run(app, host="127.0.0.1", port=PORT_PROXY, log_level="warning")
        
    thread = threading.Thread(target=run_uvicorn, daemon=True)
    thread.start()
    time.sleep(2)  # Wait for uvicorn to bind to port
    print(f"Proxy is running on http://127.0.0.1:{PORT_PROXY}")

def start_ngrok(token):
    """Starts the ngrok tunnel pointing to port PORT_PROXY."""
    print("\n" + "="*80)
    print(f"STEP 4: Setting up Ngrok Tunnel to Port {PORT_PROXY}")
    print("="*80)
    
    ngrok.set_auth_token(token)
    # Close any existing tunnels
    ngrok.kill()
    
    # Open tunnel using your claimed static domain
    tunnel = ngrok.connect(PORT_PROXY, domain="nonsophistical-cathrine-nontoned.ngrok-free.dev")
    public_url = tunnel.public_url
    
    # Append '/v1' since Dograh Speaches provider expects /v1 base URL
    openai_base_url = f"{public_url}/v1"
    
    print("\n" + "="*80)
    print("SUCCESS! COPY AND PASTE THIS URL TO DOGRAH IN THE TTS SETTINGS:")
    print("TTS Provider: Local Models (Speaches)")
    print(f"OpenAI TTS Base URL: {openai_base_url}")
    print(f"Voice ID: {current_speakers[0] if current_speakers else DEFAULT_VOICE_FILE}")
    print(f"Model: kokoro (or any dummy name)")
    print("="*80 + "\n")

if __name__ == "__main__":
    # Get ngrok token from environment or user placeholder
    ngrok_token = os.environ.get("NGROK_TOKEN", "YOUR_NGROK_TOKEN")
    
    # Clean up conflicting ports and ensure the virtual environment is present
    kill_existing_processes()
    check_and_setup_environment()
    
    # Start processes
    start_xtts_server()
    start_proxy_server()
    start_ngrok(ngrok_token)
    
    # Keep main thread alive
    print("Press CTRL+C or stop the Colab cell to terminate.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Shutting down servers...")
        ngrok.kill()
