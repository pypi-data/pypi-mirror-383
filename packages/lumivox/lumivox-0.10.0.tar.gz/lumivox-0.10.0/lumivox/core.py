# core.py
# Lumivox Core: Serial, GUI, Voice (Vosk), and safety tools.

import os
import json
import queue
import traceback
import time
import tkinter as tk
import serial
from vosk import Model, KaldiRecognizer

# Optional: import helper functions
try:
    from .utils import ensure_model, auto_input_device
except Exception:
    def ensure_model():
        base = os.path.join(os.path.expanduser("~"), "AppData", "Local", "lumivox", "models")
        folder = os.path.join(base, "vosk-model-en-in-0.5")
        if os.path.exists(folder):
            print("✅ Model folder found (fallback ensure_model).")
            return folder
        raise RuntimeError("Model not found. Please download manually.")

    def auto_input_device():
        print("[utils fallback] auto_input_device() not available — using defaults.")


# -------------------------------------------------
# SAFETY PATCH (prevents illegal CPU instruction crash)
# -------------------------------------------------
os.environ["KALDI_DISABLE_CPU_FEATURES"] = "1"


# -------------------------------------------------
# SERIAL (ESP32)
# -------------------------------------------------
def connect_serial(port="COM4", baudrate=115200, timeout=1):
    """Try to open serial port safely. Returns Serial object or None."""
    try:
        ser = serial.Serial(port, baudrate, timeout=timeout)
        time.sleep(2)
        print(f"[serial] ✅ Connected to {port}")
        return ser
    except Exception as e:
        print(f"[serial] ⚠️ Could not open serial port ({e}) — running GUI-only mode.")
        return None


def send_to_esp32(ser, color, state):
    """Send RGB command to ESP32."""
    if not ser:
        print("[serial] No serial connected — skipping send.")
        return

    try:
        rgb = {"red": (255, 0, 0), "green": (0, 255, 0), "blue": (0, 0, 255)}.get(color, (0, 0, 0))
        r, g, b = rgb if state else (0, 0, 0)
        cmd = f"SET {r},{g},{b}\n"
        ser.write(cmd.encode())
        print(f"[serial] Sent: {cmd.strip()}")
    except Exception as e:
        print(f"[serial] ⚠️ Error sending command: {e}")


# -------------------------------------------------
# GUI (Tkinter-based visualization)
# -------------------------------------------------
class LED_GUI:
    """LED Visualizer GUI."""

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

        # LED layout
        self.positions = {"red": 110, "green": 260, "blue": 410}
        self.led_shapes = {}
        self.glow = {c: 0 for c in self.positions}
        self.target = {c: 0 for c in self.positions}

        for color, x in self.positions.items():
            self.led_shapes[color] = self._draw_led(x, 110, color)

        self.status = self.canvas.create_text(
            260, 260, text="Say: 'turn on red', 'turn off blue'",
            fill="white", font=("Consolas", 11, "italic")
        )

        self.running = True
        self._animate()

    def _draw_led(self, x, y, color):
        led = {}
        led["body"] = self.canvas.create_arc(
            x - 25, y - 25, x + 25, y + 25,
            start=0, extent=180, fill="#111", outline=color, width=3
        )
        led["leg1"] = self.canvas.create_line(x - 10, y + 25, x - 10, y + 55, fill="#888", width=3)
        led["leg2"] = self.canvas.create_line(x + 10, y + 25, x + 10, y + 55, fill="#888", width=3)
        led["rays"] = [
            self.canvas.create_line(x - 35, y - 30, x - 50, y - 50, fill=""),
            self.canvas.create_line(x, y - 35, x, y - 55, fill=""),
            self.canvas.create_line(x + 35, y - 30, x + 50, y - 50, fill="")
        ]
        return led

    def update_led(self, color, state):
        if color in self.target:
            self.target[color] = 1 if state else 0

    def _animate(self):
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
            self.root.after(80, self._animate)

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


# -------------------------------------------------
# VOICE (Vosk)
# -------------------------------------------------
def load_model():
    """Load and return the Vosk Model."""
    path = ensure_model()
    print("🎤 Loading Vosk model from:", path)
    return Model(path)


def start_mic(model, debug=True):
    """Initialize microphone stream for recognition."""
    import sounddevice as sd
    import numpy as np

    rec = KaldiRecognizer(model, 16000)
    rec.SetWords(True)
    q = queue.Queue()

    def callback(indata, frames, time_info, status):
        try:
            data = indata.tobytes() if hasattr(indata, "tobytes") else np.array(indata, dtype=np.int16).tobytes()
            q.put(data)
        except Exception:
            traceback.print_exc()

    try:
        auto_input_device()
        stream = sd.RawInputStream(samplerate=16000, channels=1, dtype='int16', callback=callback)
        stream.start()
        print("[mic] 🎧 Microphone stream started.")
        return rec, q, stream
    except Exception as e:
        print("[mic] ❌ Microphone init failed:", e)
        traceback.print_exc()
        return rec, None, None


def listen_once(mic_tuple):
    """Process one chunk of audio and return recognized text."""
    if not mic_tuple:
        return ""
    rec, q, stream = mic_tuple
    if q is None:
        return ""
    try:
        data = q.get(timeout=3)
        if rec.AcceptWaveform(data):
            result = json.loads(rec.Result())
            return result.get("text", "")
    except queue.Empty:
        return ""
    except Exception as e:
        print("[mic] ⚠️ Recognition error:", e)
    return ""


def parse_command(text):
    """Parse user speech into LED color and state."""
    text = text.lower().strip()
    text = text.replace("reed", "red").replace("blew", "blue").replace("grin", "green")
    for color in ("red", "green", "blue"):
        if f"turn on {color}" in text or f"on {color}" in text:
            return color, True
        if f"turn off {color}" in text or f"off {color}" in text:
            return color, False
    return None, None


# -------------------------------------------------
# SAFE EXIT HELPERS
# -------------------------------------------------
def check_exit(gui):
    """Return True if GUI closed (safe exit)."""
    return not getattr(gui, "running", True)


def cleanup(gui):
    """Safely close GUI."""
    try:
        gui.safe_exit()
    except Exception:
        pass
