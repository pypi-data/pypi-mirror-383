# ====================================================
# LUMIVOX CORE MODULE (FINAL FIXED)
# Voice-controlled LED + ESP32 + Offline Vosk
# ====================================================

import os, json, queue, traceback, time, tkinter as tk, serial, sounddevice as sd
from vosk import Model, KaldiRecognizer

# Safety setting
os.environ["KALDI_DISABLE_CPU_FEATURES"] = "1"

# ----------------- Utility fallback -----------------
try:
    from .utils import ensure_model, auto_input_device
except Exception:
    def ensure_model():
        base = os.path.join(os.path.expanduser("~"), "AppData", "Local", "lumivox", "models")
        folder = os.path.join(base, "vosk-model-en-in-0.5")
        if os.path.exists(folder):
            print("✅ Model folder exists (fallback ensure_model).")
            return folder
        raise RuntimeError("Vosk model not found. Please download manually.")

    def auto_input_device():
        print("[utils fallback] Using default input device.")


# ----------------- SERIAL (ESP32) -----------------
def connect_serial(port="COM4", baudrate=115200, timeout=1):
    """Connect to ESP32 and return serial object."""
    try:
        ser = serial.Serial(port, baudrate, timeout=timeout)
        time.sleep(2)
        print(f"[serial] ✅ Connected to {port}")
        return ser
    except Exception as e:
        print(f"[serial] ⚠️ Could not open {port}: {e}")
        return None


def send_to_esp32(ser, color, state):
    """Send SET R,G,B command to ESP32."""
    if not ser:
        return
    try:
        rgb_map = {"red": (255, 0, 0), "green": (0, 255, 0), "blue": (0, 0, 255)}
        r, g, b = rgb_map.get(color, (0, 0, 0))
        if not state:
            r = g = b = 0
        cmd = f"SET {r},{g},{b}\n"
        ser.write(cmd.encode())
        print(f"[serial] Sent: {cmd.strip()}")
    except Exception as e:
        print("[serial] ❌ Send error:", e)


# ----------------- GUI -----------------
class LED_GUI:
    """LED GUI for Red, Green, Blue."""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🎤 Lumivox - Voice LED Controller")
        self.root.geometry("520x300")
        self.root.configure(bg="black")
        self.root.resizable(False, False)

        self.canvas = tk.Canvas(self.root, width=520, height=300, highlightthickness=0)
        self.canvas.pack()

        # Background
        self.canvas.create_rectangle(0, 0, 260, 300, fill="#0077ff", outline="")
        self.canvas.create_rectangle(260, 0, 520, 300, fill="#00cc66", outline="")

        self.positions = {"red": 110, "green": 260, "blue": 410}
        self.leds = {}
        self.glow = {c: 0.0 for c in self.positions}
        self.target = {c: 0 for c in self.positions}
        for color, x in self.positions.items():
            self.leds[color] = self._draw_led(x, 110, color)

        self.status = self.canvas.create_text(
            260, 260, text="Say: 'turn on red', 'turn off blue'",
            fill="white", font=("Consolas", 11, "italic")
        )

        self.running = True
        self._animate()
        self.root.bind("<Escape>", lambda e: self.safe_exit())

    def _draw_led(self, x, y, color):
        led = {}
        led["body"] = self.canvas.create_arc(x - 25, y - 25, x + 25, y + 25,
                                             start=0, extent=180, fill="#111", outline=color, width=3)
        led["leg1"] = self.canvas.create_line(x - 10, y + 25, x - 10, y + 55, fill="#888", width=3)
        led["leg2"] = self.canvas.create_line(x + 10, y + 25, x + 10, y + 55, fill="#888", width=3)
        return led

    def update_led(self, color, state):
        if color in self.target:
            self.target[color] = 1 if state else 0

    def _animate(self):
        for color, led in self.leds.items():
            cur, tgt = self.glow[color], self.target[color]
            cur += (tgt - cur) * 0.18
            self.glow[color] = cur
            b = int(50 + 205 * cur)
            col = {"red": f"#{b:02x}0000", "green": f"#00{b:02x}00", "blue": f"#0000{b:02x}"}[color]
            self.canvas.itemconfig(led["body"], fill=col)
        if self.running:
            self.root.after(50, self._animate)

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
    path = ensure_model()
    print("🎤 Loading Vosk model from:", path)
    return Model(path)


def start_mic(model):
    """Start microphone for Vosk recognition."""
    rec = KaldiRecognizer(model, 16000)
    rec.SetWords(True)
    q = queue.Queue()

    try:
        devices = sd.query_devices()
        input_devices = [i for i, d in enumerate(devices) if d["max_input_channels"] > 0]
        device_id = input_devices[0] if input_devices else None
        print(f"[mic] 🎙️ Using: {devices[device_id]['name']}")
    except Exception:
        device_id = None

    def _cb(indata, frames, t, status):
        q.put(bytes(indata))

    try:
        stream = sd.RawInputStream(samplerate=16000, channels=1, dtype='int16',
                                   device=device_id, callback=_cb)
        stream.start()
        print("[mic] 🎧 Stream started.")
        return rec, q, stream
    except Exception as e:
        print("[mic] ❌ Mic failed:", e)
        return rec, None, None


def listen_once(mic):
    """Return recognized text."""
    if mic is None:
        return ""
    rec, q, stream = mic
    if q is None:
        return ""
    try:
        data = q.get(timeout=1)
        if rec.AcceptWaveform(data):
            result = json.loads(rec.Result())
            return result.get("text", "")
        else:
            pr = json.loads(rec.PartialResult()).get("partial", "")
            return pr
    except queue.Empty:
        return ""
    except Exception as e:
        print("[mic] ⚠️ Error:", e)
        return ""


# ----------------- FIXED COMMAND PARSER -----------------
def parse_command(text):
    """Convert speech text into (color, on/off) with fuzzy correction."""
    if not text:
        return None, None

    t = text.lower().strip()

    # Fix common misheard words
    corrections = {
        "reed": "red", "read": "red", "bread": "red",
        "blew": "blue", "bluetooth": "blue",
        "grin": "green", "grain": "green", "dream": "green"
    }
    for wrong, right in corrections.items():
        t = t.replace(wrong, right)

    for color in ("red", "green", "blue"):
        if f"turn on {color}" in t or f"on {color}" in t:
            return color, True
        if f"turn off {color}" in t or f"off {color}" in t:
            return color, False

    return None, None


# ----------------- HELPERS -----------------
def check_exit(gui):
    return not gui.running


def cleanup(gui):
    try:
        gui.safe_exit()
    except Exception:
        pass
