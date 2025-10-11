# lumivox/core.py
# Multi-color voice LED core with GUI + ESP32 sync

import os, json, queue, traceback, time, tkinter as tk, serial, sounddevice as sd, numpy as np
from vosk import Model, KaldiRecognizer

os.environ["KALDI_DISABLE_CPU_FEATURES"] = "1"

try:
    from .utils import ensure_model, auto_input_device
except Exception:
    def ensure_model():
        base = os.path.join(os.path.expanduser("~"), "AppData", "Local", "lumivox", "models")
        folder = os.path.join(base, "vosk-model-en-in-0.5")
        if os.path.exists(folder):
            return folder
        raise RuntimeError("Vosk model missing.")
    def auto_input_device(): pass


# ---------------- Serial ----------------
def connect_serial(port="COM4", baudrate=115200, timeout=1):
    try:
        ser = serial.Serial(port, baudrate, timeout=timeout)
        time.sleep(2)
        print(f"[serial] ✅ Connected to {port}")
        return ser
    except Exception as e:
        print(f"[serial] ⚠️ Could not open serial port: {e}")
        return None

def send_to_esp32(ser, r, g, b):
    """Send combined RGB state (0–255)"""
    if not ser: return
    try:
        cmd = f"SET {r},{g},{b}\n"
        ser.write(cmd.encode())
        print("[serial] Sent:", cmd.strip())
    except Exception as e:
        print("[serial] ❌ Send error:", e)


# ---------------- GUI ----------------
class LED_GUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🎤 Lumivox - Voice RGB Controller")
        self.root.geometry("520x300")
        self.root.configure(bg="black")
        self.root.resizable(False, False)
        self.canvas = tk.Canvas(self.root, width=520, height=300, highlightthickness=0)
        self.canvas.pack()

        self.canvas.create_rectangle(0, 0, 260, 300, fill="#0077ff", outline="")
        self.canvas.create_rectangle(260, 0, 520, 300, fill="#00cc66", outline="")
        self.root.bind("<Escape>", lambda e: self.safe_exit())

        self.positions = {"red": 110, "green": 260, "blue": 410}
        self.led_shapes, self.glow, self.target = {}, {}, {}
        for color, x in self.positions.items():
            self.led_shapes[color] = self.draw_led(x, 110, color)
            self.glow[color] = 0
            self.target[color] = 0

        self.status = self.canvas.create_text(
            260, 260, text="Say: 'turn on red', 'turn on blue', 'turn off green'",
            fill="white", font=("Consolas", 11, "italic")
        )
        self.running = True
        self.animate()

    def draw_led(self, x, y, color):
        led = {}
        led["body"] = self.canvas.create_arc(x - 25, y - 25, x + 25, y + 25,
                                             start=0, extent=180, fill="#111", outline=color, width=3)
        led["leg1"] = self.canvas.create_line(x - 10, y + 25, x - 10, y + 55, fill="#888", width=3)
        led["leg2"] = self.canvas.create_line(x + 10, y + 25, x + 10, y + 55, fill="#888", width=3)
        return led

    def update_led(self, color, state):
        if color in self.target:
            self.target[color] = 1 if state else 0

    def animate(self):
        for color, led in self.led_shapes.items():
            current, target = self.glow[color], self.target[color]
            new = current + (target - current) * 0.2
            self.glow[color] = new
            b = int(50 + 205 * new)
            col = {"red": f"#{b:02x}0000", "green": f"#00{b:02x}00", "blue": f"#0000{b:02x}"}[color]
            self.canvas.itemconfig(led["body"], fill=col)
        if self.running:
            self.root.after(70, self.animate)

    def set_status(self, text):
        self.canvas.itemconfig(self.status, text=text)

    def safe_exit(self):
        self.running = False
        try: self.root.destroy()
        except: pass
        print("🛑 GUI closed safely.")

    def run(self):
        self.root.mainloop()


# ---------------- Model + Mic ----------------
def load_model():
    path = ensure_model()
    print("🎤 Loading Vosk model from:", path)
    return Model(path)

def start_mic(model):
    rec = KaldiRecognizer(model, 16000)
    rec.SetWords(True)
    q = queue.Queue()
    def cb(indata, frames, t, status):
        q.put(bytes(indata))
    stream = sd.RawInputStream(samplerate=16000, channels=1, dtype='int16', callback=cb)
    stream.start()
    print("[mic] 🎧 Listening...")
    return rec, q, stream

def listen_once(mic):
    if mic is None: return ""
    rec, q, _ = mic
    try:
        data = q.get(timeout=0.6)
        if rec.AcceptWaveform(data):
            result = json.loads(rec.Result())
            return result.get("text", "")
    except queue.Empty:
        return ""
    return ""


# ---------------- Command Parser + State ----------------
led_state = {"red": 0, "green": 0, "blue": 0}

def parse_command(text):
    """Improved parser with smart corrections"""
    if not text: return None, None
    t = text.lower().strip()

    # 🔧 Fix common recognition mistakes
    for wrong, right in {
        "reed": "red", "read": "red", "rad": "red",
        "blew": "blue", "blu": "blue",
        "grin": "green", "grain": "green"
    }.items():
        t = t.replace(wrong, right)

    for color in ("red", "green", "blue"):
        if f"turn on {color}" in t or f"on {color}" in t:
            led_state[color] = 255
            return color, True
        if f"turn off {color}" in t or f"off {color}" in t:
            led_state[color] = 0
            return color, False
    return None, None


def current_rgb():
    return led_state["red"], led_state["green"], led_state["blue"]

def check_exit(gui): return not gui.running
def cleanup(gui): gui.safe_exit()
