# lumivox/core.py
# Optimized Lumivox core: GUI, serial (ESP32), Vosk model + mic with low-latency partial results.

import os
import json
import queue
import traceback
import time
import tkinter as tk
import serial
import sounddevice as sd
import numpy as np
from vosk import Model, KaldiRecognizer

# Safety: avoid illegal CPU instructions in some Kaldi builds
os.environ["KALDI_DISABLE_CPU_FEATURES"] = "1"


# ----------------- utils fallback (if utils.py missing) -----------------
try:
    from .utils import ensure_model, auto_input_device
except Exception:
    def ensure_model():
        """Fallback: expect model downloaded into %LOCALAPPDATA%/lumivox/models/vosk-model-en-in-0.5"""
        base = os.path.join(os.path.expanduser("~"), "AppData", "Local", "lumivox", "models")
        folder = os.path.join(base, "vosk-model-en-in-0.5")
        if os.path.exists(folder):
            print("✅ Model folder exists (fallback ensure_model).")
            return folder
        raise RuntimeError("Vosk model not found (fallback). Please download or provide utils.ensure_model.")
    def auto_input_device():
        # best-effort placeholder
        print("[utils fallback] auto_input_device() not available; using default input device.")


# ----------------- Serial (ESP32) -----------------
def connect_serial(port="COM4", baudrate=115200, timeout=1):
    """Open serial port to ESP32. Return Serial object or None (GUI-only)."""
    try:
        ser = serial.Serial(port, baudrate, timeout=timeout)
        time.sleep(2)  # allow ESP32 to reset
        print(f"[serial] ✅ Connected to {port}")
        return ser
    except Exception as e:
        print(f"[serial] ⚠️ Could not open serial port {port}: {e} — continuing in GUI-only mode.")
        return None


def send_to_esp32(ser, color, state):
    """Send `SET R,G,B` command to ESP32 if connected; otherwise print simulated command."""
    if not ser:
        # for debugging when ESP not connected
        print("[serial] (sim) would send:", color, "->", "ON" if state else "OFF")
        return
    try:
        rgb_map = {
            "red": (255, 0, 0),
            "green": (0, 255, 0),
            "blue": (0, 0, 255)
        }
        r, g, b = rgb_map.get(color, (0, 0, 0))
        if not state:
            r = g = b = 0
        cmd = f"SET {r},{g},{b}\n"
        ser.write(cmd.encode())
        print("[serial] Sent:", cmd.strip())
    except Exception as e:
        print("[serial] ❌ Error sending command:", e)


# ----------------- GUI -----------------
class LED_GUI:
    """Simple animated LED GUI. Must be run from main thread (tkinter requirement)."""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🎤 Lumivox - Voice LED Controller")
        self.root.geometry("520x300")
        self.root.configure(bg="black")
        self.root.resizable(False, False)

        self.canvas = tk.Canvas(self.root, width=520, height=300, highlightthickness=0)
        self.canvas.pack()

        # background split
        self.canvas.create_rectangle(0, 0, 260, 300, fill="#0077ff", outline="")
        self.canvas.create_rectangle(260, 0, 520, 300, fill="#00cc66", outline="")

        self.root.bind("<Escape>", lambda e: self.safe_exit())

        self.positions = {"red": 110, "green": 260, "blue": 410}
        self.leds = {}
        self.glow = {c: 0.0 for c in self.positions}
        self.target = {c: 0 for c in self.positions}
        for color, x in self.positions.items():
            self.leds[color] = self.draw_led(x, 110, color)

        self.status = self.canvas.create_text(
            260, 260,
            text="Say: 'turn on red', 'turn off blue'",
            fill="white", font=("Consolas", 11, "italic")
        )

        self.running = True
        self._animate()  # start animation loop

    def draw_led(self, x, y, color):
        led = {}
        led["body"] = self.canvas.create_arc(x - 25, y - 25, x + 25, y + 25,
                                             start=0, extent=180, fill="#111", outline=color, width=3)
        led["leg1"] = self.canvas.create_line(x - 10, y + 25, x - 10, y + 55, fill="#888", width=3)
        led["leg2"] = self.canvas.create_line(x + 10, y + 25, x + 10, y + 55, fill="#888", width=3)
        return led

    def update_led(self, color, state):
        """Set target (0/1) for smooth animation."""
        if color in self.target:
            self.target[color] = 1 if state else 0

    def _animate(self):
        for color, led in self.leds.items():
            cur = self.glow[color]
            tgt = self.target[color]
            cur += (tgt - cur) * 0.18  # faster smoothing for snappier visuals
            self.glow[color] = cur
            b = int(50 + 205 * cur)
            color_code = {
                "red": f"#{b:02x}0000",
                "green": f"#00{b:02x}00",
                "blue": f"#0000{b:02x}"
            }[color]
            self.canvas.itemconfig(led["body"], fill=color_code)

        if self.running:
            # shorter interval for snappier UI
            self.root.after(45, self._animate)

    def set_status(self, text):
        self.canvas.itemconfig(self.status, text=text)

    def safe_exit(self):
        self.running = False
        try:
            self.root.destroy()
        except Exception:
            pass
        print("🛑 GUI closed cleanly.")

    def run(self):
        self.root.mainloop()


# ----------------- MODEL + MICROPHONE -----------------
def load_model():
    """Ensure model exists and return a loaded vosk Model object."""
    path = ensure_model()
    print("🎤 Loading Vosk model from:", path)
    return Model(path)


def start_mic(model, prefer_wasapi=True, blocksize=4000):
    """
    Start microphone stream with low-latency blocks.
    Returns (rec, queue, stream) where queue receives raw audio bytes.
    """
    rec = KaldiRecognizer(model, 16000)
    rec.SetWords(True)
    q = queue.Queue()

    # Attempt to choose a sensible input device
    device_id = None
    try:
        devs = sd.query_devices()
        input_dev_indices = [i for i, d in enumerate(devs) if d['max_input_channels'] > 0]
        if input_dev_indices:
            device_id = input_dev_indices[0]
            print(f"[mic] 🎙️ Auto-selected input device: {devs[device_id]['name']}")
        else:
            print("[mic] ⚠️ No input device found.")
    except Exception as e:
        print("[mic] ⚠️ Could not list devices:", e)
        device_id = None

    # Try to set WASAPI on Windows (helps some systems); ignore failures
    try:
        if prefer_wasapi:
            hostapis = sd.query_hostapis()
            for i, h in enumerate(hostapis):
                if "WASAPI" in h.get("name", "").upper():
                    sd.default.hostapi = i
                    print(f"[mic] Using hostapi WASAPI (index {i})")
                    break
    except Exception:
        pass

    def _cb(indata, frames, t, status):
        try:
            # RawInputStream yields a bytes-like object (or numpy buffer); normalize to bytes
            if hasattr(indata, "tobytes"):
                data = indata.tobytes()
            else:
                data = bytes(indata)
            q.put(data)
        except Exception:
            traceback.print_exc()

    # Start RawInputStream with small blocksize for lower latency
    try:
        stream = sd.RawInputStream(
            samplerate=16000,
            blocksize=blocksize,
            dtype='int16',
            channels=1,
            callback=_cb,
            device=device_id
        )
        stream.start()
        print("[mic] 🎧 RawInputStream started (low-latency).")
        return rec, q, stream
    except Exception as e:
        print("[mic] ❌ RawInputStream failed:", e)
        traceback.print_exc()
        # fallback to InputStream
        try:
            stream = sd.InputStream(
                samplerate=16000,
                blocksize=blocksize,
                dtype='int16',
                channels=1,
                callback=_cb,
                device=device_id
            )
            stream.start()
            print("[mic] 🎧 InputStream started (fallback).")
            return rec, q, stream
        except Exception as e2:
            print("[mic] ❌ All microphone attempts failed:", e2)
            traceback.print_exc()
            return rec, None, None


_TRIGGER_WORDS = ("turn on", "turn off", "on ", "off ", "red", "green", "blue")


def listen_once(mic, timeout=0.6):
    """
    Wait for one chunk and return recognized text.
    - Uses AcceptWaveform for final results.
    - Uses PartialResult to return early if a trigger word appears.
    - timeout: seconds to wait for queue data (short for snappy behavior)
    """
    if mic is None:
        return ""
    rec, q, stream = mic
    if q is None:
        return ""

    try:
        # Wait for one audio block (short timeout for snappy behavior)
        data = q.get(timeout=timeout)
    except queue.Empty:
        return ""

    try:
        # If Vosk treats chunk as a final waveform part
        if rec.AcceptWaveform(data):
            result = json.loads(rec.Result())
            return result.get("text", "")
        else:
            # partial result is quick and helps early reaction
            pr = json.loads(rec.PartialResult()).get("partial", "")
            if pr:
                low = pr.lower()
                # if we see trigger words in partial, return partial (early action)
                for w in _TRIGGER_WORDS:
                    if w in low:
                        return pr
    except Exception:
        print("[mic] ⚠️ Error in recognition:")
        traceback.print_exc()

    return ""


# ----------------- COMMAND PARSING & HELPERS -----------------
def parse_command(text):
    """Map spoken text to (color, state)"""
    if not text:
        return None, None
    t = text.lower().strip()
    t = t.replace("reed", "red").replace("blew", "blue").replace("grin", "green")
    for color in ("red", "green", "blue"):
        if f"turn on {color}" in t or f"on {color}" in t:
            return color, True
        if f"turn off {color}" in t or f"off {color}" in t:
            return color, False
    return None, None


def check_exit(gui):
    """Return True if GUI is closed (so caller can stop background loops)."""
    return not gui.running


def cleanup(gui):
    """Cleanup resources; closes GUI safely."""
    try:
        gui.safe_exit()
    except Exception:
        pass
