#!/usr/bin/env python3
"""
jarvis.py — Double-clap home automation script.

Listens for 2 claps via microphone, speaks a welcome message via TTS,
opens a URL in the browser, and launches configurable apps side by side.

Supports: macOS and Windows.

Dependencies:
    pip install sounddevice numpy
    (Windows only) pip install pyttsx3 pygetwindow

Usage:
    python jarvis.py
"""

import os
import sys
import time
import platform
import subprocess
import webbrowser
import threading

import numpy as np
import sounddevice as sd

# ──────────────────────────────────────────────────────────────────────────────
#  Load .env (no external dependencies)
# ──────────────────────────────────────────────────────────────────────────────
_env_path = os.path.join(os.path.dirname(__file__), ".env")
if os.path.isfile(_env_path):
    with open(_env_path) as _f:
        for _line in _f:
            _line = _line.strip()
            if _line and not _line.startswith("#") and "=" in _line:
                _k, _v = _line.split("=", 1)
                os.environ.setdefault(_k.strip(), _v.strip())

# ──────────────────────────────────────────────────────────────────────────────
#  Configuration (from .env with sensible defaults)
# ──────────────────────────────────────────────────────────────────────────────
PLATFORM       = platform.system()          # "Darwin" | "Windows" | "Linux"
NOMBRE         = os.getenv("JARVIS_NOMBRE", "")
SPOTIFY_URL    = os.getenv("JARVIS_SPOTIFY_URL", "spotify:track:2zYzyRzz6pRmhPzyfMEC8s")
_default_apps  = "Terminal,Claude" if PLATFORM == "Darwin" else "cmd,Claude"
APPS_RAW       = os.getenv("JARVIS_APPS", _default_apps)
APPS           = [a.strip() for a in APPS_RAW.split(",") if a.strip()]
THRESHOLD      = float(os.getenv("JARVIS_THRESHOLD", "0.20"))
VOICE_MAC      = os.getenv("JARVIS_VOICE_MAC", "Monica")
VOICE_LANG     = os.getenv("JARVIS_VOICE_LANG", "es")
VOICE_RATE     = int(os.getenv("JARVIS_VOICE_RATE", "148"))

# Clap detection tuning
SAMPLE_RATE    = 16000
BLOCK_SIZE     = int(SAMPLE_RATE * 0.05)   # 50 ms per block
COOLDOWN       = 0.15                       # minimum seconds between clap events
DOUBLE_WINDOW  = 2.0                        # seconds to wait for the second clap

# ──────────────────────────────────────────────────────────────────────────────
#  Text-to-Speech
# ──────────────────────────────────────────────────────────────────────────────
def speak(message: str) -> None:
    """Speak a message using the platform's TTS engine."""
    if PLATFORM == "Darwin":
        # macOS: use the built-in `say` command
        cmd = ["say", "-v", VOICE_MAC, "-r", str(VOICE_RATE), message]
        subprocess.run(cmd, check=False)
    elif PLATFORM == "Windows":
        try:
            import pyttsx3
            engine = pyttsx3.init()
            engine.setProperty("rate", VOICE_RATE)
            # Try to find a voice matching the configured language
            for voice in engine.getProperty("voices"):
                if VOICE_LANG.lower() in voice.id.lower():
                    engine.setProperty("voice", voice.id)
                    break
            engine.say(message)
            engine.runAndWait()
        except ImportError:
            print("[TTS] pyttsx3 not installed. Run: pip install pyttsx3")
    else:
        # Linux fallback: try espeak
        subprocess.run(["espeak", "-v", VOICE_LANG, message], check=False)

# ──────────────────────────────────────────────────────────────────────────────
#  App launcher
# ──────────────────────────────────────────────────────────────────────────────
def open_app(app_name: str) -> None:
    """Open an application by name, cross-platform."""
    if PLATFORM == "Darwin":
        if app_name.lower() == "terminal":
            subprocess.Popen(["open", "-a", "Terminal"])
        else:
            subprocess.Popen(["open", "-a", app_name])
    elif PLATFORM == "Windows":
        if app_name.lower() in ("cmd", "terminal"):
            subprocess.Popen("start cmd", shell=True)
        else:
            subprocess.Popen(["start", "", app_name], shell=True)
    else:
        subprocess.Popen([app_name])

def open_spotify() -> None:
    """Open Spotify with the configured track."""
    print(f"[Jarvis] Opening Spotify: {SPOTIFY_URL}")
    if PLATFORM == "Darwin":
        subprocess.Popen(["open", SPOTIFY_URL])
    elif PLATFORM == "Windows":
        subprocess.Popen(["start", SPOTIFY_URL], shell=True)
    else:
        subprocess.Popen(["xdg-open", SPOTIFY_URL])

def open_apps_and_url() -> None:
    """Open Spotify and all configured apps."""
    open_spotify()
    time.sleep(0.8)

    for app in APPS:
        print(f"[Jarvis] Opening app: {app}")
        open_app(app)
        time.sleep(0.8)

# ──────────────────────────────────────────────────────────────────────────────
#  Window management
# ──────────────────────────────────────────────────────────────────────────────
def tile_windows_mac() -> None:
    """Tile the two most recently opened windows side by side using AppleScript (macOS)."""
    script = """
    tell application "System Events"
        set allProcs to every process whose visible is true
        set appList to {}
        repeat with p in allProcs
            set appList to appList & {name of p}
        end repeat
    end tell

    if (count of appList) < 2 then return

    set screenWidth to do shell script "system_profiler SPDisplaysDataType | awk '/Resolution/{print $2; exit}'"
    set w to (screenWidth as integer) / 2
    set h to 900

    tell application "System Events"
        set proc1 to item -1 of allProcs
        set proc2 to item -2 of allProcs
        set position of window 1 of proc1 to {0, 0}
        set size of window 1 of proc1 to {w, h}
        set position of window 1 of proc2 to {w, 0}
        set size of window 1 of proc2 to {w, h}
    end tell
    """
    subprocess.run(["osascript", "-e", script], check=False)

def tile_windows_win() -> None:
    """Tile the two most recently opened windows side by side (Windows)."""
    try:
        import pygetwindow as gw
        import ctypes
        user32 = ctypes.windll.user32
        screen_w = user32.GetSystemMetrics(0)
        screen_h = user32.GetSystemMetrics(1)

        windows = [w for w in gw.getAllWindows() if w.visible and w.title]
        if len(windows) < 2:
            return
        w1, w2 = windows[-1], windows[-2]
        half = screen_w // 2
        w1.moveTo(0, 0)
        w1.resizeTo(half, screen_h)
        w2.moveTo(half, 0)
        w2.resizeTo(half, screen_h)
    except ImportError:
        print("[Windows] pygetwindow not installed. Run: pip install pygetwindow")

def tile_windows() -> None:
    """Arrange two windows side by side, platform-aware."""
    # Give apps time to open before tiling
    time.sleep(2.5)
    if PLATFORM == "Darwin":
        tile_windows_mac()
    elif PLATFORM == "Windows":
        tile_windows_win()
    else:
        print("[Jarvis] Window tiling not supported on this platform.")

# ──────────────────────────────────────────────────────────────────────────────
#  Welcome sequence
# ──────────────────────────────────────────────────────────────────────────────
def welcome_sequence() -> None:
    """Run the full welcome sequence after detecting two claps."""
    greeting = "Bienvenido a casa"
    if NOMBRE:
        greeting += f", {NOMBRE}"
    greeting += "."

    print(f"\n[Jarvis] Claps detected! Running welcome sequence...")
    print(f"[Jarvis] Speaking: {greeting}")

    # Speak and open apps concurrently
    speak_thread = threading.Thread(target=speak, args=(greeting,), daemon=True)
    speak_thread.start()

    open_apps_and_url()
    tile_windows()

    speak_thread.join(timeout=10)
    print("[Jarvis] Welcome sequence complete. Listening for next trigger...\n")

# ──────────────────────────────────────────────────────────────────────────────
#  Clap detection
# ──────────────────────────────────────────────────────────────────────────────
_last_rms    = 0.0
_clap_times  = []
_sequence_running = False

def audio_callback(indata: np.ndarray, frames: int, time_info, status) -> None:
    """Called by sounddevice for each audio block. Detects transient claps."""
    global _last_rms, _clap_times, _sequence_running

    if _sequence_running:
        return

    rms = float(np.sqrt(np.mean(indata ** 2)))

    # Detect a transient: RMS spikes above threshold from a quiet state
    is_clap = rms > THRESHOLD and _last_rms < THRESHOLD * 0.5
    _last_rms = rms

    if not is_clap:
        return

    now = time.monotonic()

    # Enforce minimum cooldown between clap events
    if _clap_times and (now - _clap_times[-1]) < COOLDOWN:
        return

    _clap_times.append(now)
    print(f"[Jarvis] Clap detected (RMS={rms:.3f}) — total: {len(_clap_times)}")

    # Remove claps outside the detection window
    _clap_times = [t for t in _clap_times if now - t <= DOUBLE_WINDOW]

    if len(_clap_times) >= 2:
        _clap_times.clear()
        _sequence_running = True
        t = threading.Thread(target=_run_sequence, daemon=True)
        t.start()

def _run_sequence() -> None:
    """Thread wrapper: runs the welcome sequence then re-enables detection."""
    global _sequence_running
    try:
        welcome_sequence()
    finally:
        _sequence_running = False

# ──────────────────────────────────────────────────────────────────────────────
#  Main
# ──────────────────────────────────────────────────────────────────────────────
def main() -> None:
    print("=" * 60)
    print("  Jarvis — Double-Clap Home Automation")
    print("=" * 60)
    print(f"  Platform  : {PLATFORM}")
    print(f"  User      : {NOMBRE or '(not set)'}")
    print(f"  Spotify   : {SPOTIFY_URL}")
    print(f"  Apps      : {', '.join(APPS) if APPS else '(none)'}")
    print(f"  Threshold : {THRESHOLD}")
    print(f"  TTS voice : {VOICE_MAC if PLATFORM == 'Darwin' else VOICE_LANG}")
    print("=" * 60)
    print("  Clap twice to activate! Press Ctrl+C to exit.\n")

    try:
        with sd.InputStream(
            samplerate=SAMPLE_RATE,
            blocksize=BLOCK_SIZE,
            channels=1,
            dtype="float32",
            callback=audio_callback,
        ):
            while True:
                time.sleep(0.1)
    except KeyboardInterrupt:
        print("\n[Jarvis] Shutting down. Goodbye!")
    except Exception as exc:
        print(f"[Jarvis] Audio error: {exc}")
        sys.exit(1)

if __name__ == "__main__":
    main()
