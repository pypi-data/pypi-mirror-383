# lumivox_core.py
# Core logic: serial, GUI, microphone + Vosk loader, and helpers with detailed debug output.

import os
import json
import queue
import traceback
import threading
import time
import tkinter as tk
import serial
from vosk import Model, KaldiRecognizer

# Try to import utils functions if you have a utils.py in same package
try:
    from .utils import ensure_model, auto_input_device
except Exception:
    # Fallback ensure_model and auto_input_device (very small safe placeholders)
    def ensure_model():
        # If you already downloaded the model into %LOCALAPPDATA%/lumivox/models/vosk-model-en-in-0.5
        base = os.path.join(os.path.expanduser("~"), "AppData", "Local", "lumivox", "models")
        folder = os.path.join(base, "vosk-model-en-in-0.5")
        if os.path.exists(folder):
            print("✅ Model folder already present (fallback ensure_model).")
            return folder
        raise RuntimeError("Model not found and no utils.ensure_model available. Please download model manually.")
    def auto_input_device():
        print("[utils fallback] auto_input_device() not available. Using defaults.")


# Safety env to avoid illegal CPU instructions in some Kaldi builds
os.environ["KALDI_DISABLE_CPU_FEATURES"] = "1"


# ----------------- Serial (ESP32) -----------------
def connect_serial(port="COM4", baudrate=115200, timeout=1):
    """Try to open a serial port to ESP32. Returns Serial object or None."""
    try:
        ser = serial.Serial(port, baudrate, timeout=timeout)
        time.sleep(2)
        print(f"[serial] ✅ Connected to {port}")
        return ser
    except Exception as e:
        print(f"[serial] ⚠️ Could not open serial port ({e}) — continuing in GUI-only mode.")
        return None


def send_to_esp32(ser, color, state):
    """Send 'SET R,G,B' to the ESP32 if connected."""
    if not ser:
        print("[serial] (no serial) would send:", color, state)
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
        print("[serial] Error sending to ESP32:", e)


# ----------------- GUI -----------------
class LED_GUI:
    """Simple animated LED GUI using tkinter. Safe to run in main thread only."""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🎤 Lumivox - Voice Controlled LED")
        self.root.geometry("520x300")
        self.root.configure(bg="black")
        self.root.resizable(False, False)

        self.canvas = tk.Canvas(self.root, width=520, height=300, highlightthickness=0)
        self.canvas.pack()

        self.canvas.create_rectangle(0, 0, 260, 300, fill="#0077ff", outline="")
        self.canvas.create_rectangle(260, 0, 520, 300, fill="#00cc66", outline="")

        self.root.bind("<Escape>", lambda e: self.safe_exit())

        self.positions = {"red": 110, "green": 260, "blue": 410}
        self.led_shapes = {}
        self.glow = {c: 0 for c in self.positions}
        self.target = {c: 0 for c in self.positions}

        for color, x in self.positions.items():
            self.led_shapes[color] = self.draw_led(x, 110, color)

        self.status = self.canvas.create_text(
            260, 260, text="Say: 'turn on red', 'turn off blue'", fill="white",
            font=("Consolas", 11, "italic")
        )

        self.running = True
        self.animate()

    def draw_led(self, x, y, color):
        led = {}
        led["body"] = self.canvas.create_arc(x - 25, y - 25, x + 25, y + 25,
                                             start=0, extent=180, fill="#111", outline=color, width=3)
        led["leg1"] = self.canvas.create_line(x - 10, y + 25, x - 10, y + 55, fill="#888", width=3)
        led["leg2"] = self.canvas.create_line(x + 10, y + 25, x + 10, y + 55, fill="#888", width=3)
        led["rays"] = [self.canvas.create_line(x - 35, y - 30, x - 50, y - 50, fill=""),
                       self.canvas.create_line(x, y - 35, x, y - 55, fill=""),
                       self.canvas.create_line(x + 35, y - 30, x + 50, y - 50, fill="")]
        return led

    def update_led(self, color, state):
        if color in self.target:
            self.target[color] = 1 if state else 0

    def animate(self):
        for color, led in self.led_shapes.items():
            current, target = self.glow[color], self.target[color]
            new = current + (target - current) * 0.1
            self.glow[color] = new
            b = int(50 + 205 * new)
            color_code = {
                "red": f"#{b:02x}0000",
                "green": f"#00{b:02x}00",
                "blue": f"#0000{b:02x}"
            }[color]
            self.canvas.itemconfig(led["body"], fill=color_code)
            ray_color = color_code if new > 0.2 else ""
            for ray in led["rays"]:
                self.canvas.itemconfig(ray, fill=ray_color)
        if self.running:
            self.root.after(80, self.animate)

    def set_status(self, text):
        self.canvas.itemconfig(self.status, text=text)

    def safe_exit(self):
        self.running = False
        try:
            self.root.destroy()
        except Exception:
            pass
        print("🛑 Exiting GUI (safe_exit).")

    def run(self):
        self.root.mainloop()


# ----------------- VOICE helpers -----------------
def load_model():
    """Ensure model exists and load it. Returns Model path loaded by vosk.Model()."""
    model_path = ensure_model()
    print("🎤 Loading Vosk model from:", model_path)
    return Model(model_path)


def start_mic(model, prefer_wasapi=True, debug=True):
    """
    Start microphone stream, prefer WASAPI on Windows (safer).
    Returns (rec, queue, stream_object) or (rec, queue, None) if mic fails.
    - rec: KaldiRecognizer
    - queue: queue.Queue with raw audio bytes
    - stream_object: sounddevice.RawInputStream or InputStream (so caller can keep reference)
    """
    import sounddevice as sd
    import numpy as np

    rec = KaldiRecognizer(model, 16000)
    rec.SetWords(True)
    q = queue.Queue()

    def _callback(indata, frames, time_info, status):
        try:
            # indata might be a numpy array / memoryview / buffer; convert to int16 bytes
            if hasattr(indata, "tobytes"):
                data = indata.tobytes()
            else:
                data = np.array(indata, dtype=np.int16).tobytes()
            q.put(data)
        except Exception:
            print("[mic] Callback exception:")
            traceback.print_exc()

    # Debug: show hostapis and devices
    try:
        hostapis = sd.query_hostapis()
        if debug:
            print("[debug] sounddevice hostapis:")
            for i, h in enumerate(hostapis):
                print(f"  {i}: {h['name']}")
            print("[debug] sounddevice devices:")
            for i, d in enumerate(sd.query_devices()):
                print(f"  {i}: {d['name']} - in_ch={d['max_input_channels']} out_ch={d['max_output_channels']}")
    except Exception as e:
        print("[debug] Could not query sounddevice hostapis/devices:", e)

    # small delay to avoid race with Tkinter initialization
    time.sleep(0.8)

    # Try selecting WASAPI hostapi if available on Windows
    try:
        if prefer_wasapi:
            hostapis = sd.query_hostapis()
            wasapi_index = None
            for i, h in enumerate(hostapis):
                if "WASAPI" in h["name"].upper():
                    wasapi_index = i
                    break
            if wasapi_index is not None:
                sd.default.hostapi = wasapi_index
                print(f"[mic] ✅ Forcing hostapi to WASAPI (index {wasapi_index}).")
            else:
                print("[mic] ⚠️ WASAPI not found, continuing with default hostapi.")
    except Exception as e:
        print("[mic] Warning: could not set hostapi:", e)

    # Choose a default input device name using auto_input_device (from utils)
    try:
        auto_input_device()
    except Exception as e:
        print("[mic] auto_input_device() failed:", e)

    # Start RawInputStream (gives us bytes directly)
    try:
        stream = sd.RawInputStream(
            samplerate=16000,
            blocksize=8000,
            dtype='int16',
            channels=1,
            callback=_callback
        )
        stream.start()
        print("[mic] 🎧 RawInputStream started (callback attached).")
        return rec, q, stream
    except Exception as e:
        print("[mic] ❌ RawInputStream start failed:", e)
        traceback.print_exc()
        # Try fallback: InputStream
        try:
            stream = sd.InputStream(
                samplerate=16000,
                blocksize=8000,
                dtype='int16',
                channels=1,
                callback=_callback
            )
            stream.start()
            print("[mic] 🎧 InputStream started (fallback).")
            return rec, q, stream
        except Exception as e2:
            print("[mic] ❌ All microphone attempts failed:", e2)
            traceback.print_exc()
            return rec, None, None


def listen_once(mic_tuple):
    """
    Pop a single audio chunk from queue and attempt recognition.
    Returns recognized text or empty string.
    """
    if mic_tuple is None:
        return ""
    rec, q, stream = mic_tuple
    if q is None:
        return ""
    try:
        data = q.get(timeout=5)  # wait up to 5s for audio
    except queue.Empty:
        # no audio in time
        return ""
    try:
        if rec.AcceptWaveform(data):
            res = json.loads(rec.Result())
            return res.get("text", "")
    except Exception:
        print("[mic] Error processing waveform:")
        traceback.print_exc()
    return ""


def parse_command(text):
    """Simple parsing to map phrases to color on/off."""
    text = text.lower().strip()
    text = text.replace("reed", "red").replace("blew", "blue").replace("grin", "green")
    for color in ("red", "green", "blue"):
        if f"turn on {color}" in text or f"on {color}" in text:
            return color, True
        if f"turn off {color}" in text or f"off {color}" in text:
            return color, False
    return None, None
