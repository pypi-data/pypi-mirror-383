# =============================================
# LUMIVOX CORE MODULE (Stable + ESP32 + Auto Mic)
# =============================================

import os, json, queue, traceback, time, tkinter as tk, serial, sounddevice as sd, numpy as np
from vosk import Model, KaldiRecognizer

# ---------- Safe environment fix ----------
os.environ["KALDI_DISABLE_CPU_FEATURES"] = "1"

# ---------- Optional local imports ----------
try:
    from .utils import ensure_model, auto_input_device
except Exception:
    def ensure_model():
        base = os.path.join(os.path.expanduser("~"), "AppData", "Local", "lumivox", "models")
        folder = os.path.join(base, "vosk-model-en-in-0.5")
        if os.path.exists(folder):
            print("✅ Model folder exists.")
            return folder
        raise RuntimeError("Vosk model missing — download manually.")
    def auto_input_device():
        print("[utils] Using default input device.")


# ---------- SERIAL ----------
def connect_serial(port="COM4", baudrate=115200, timeout=1):
    try:
        ser = serial.Serial(port, baudrate, timeout=timeout)
        time.sleep(2)
        print(f"[serial] ✅ Connected to {port}")
        return ser
    except Exception as e:
        print(f"[serial] ⚠️ Could not connect to {port}: {e}")
        return None


def send_to_esp32(ser, color, state):
    if not ser:
        return
    try:
        rgb = {"red": (255, 0, 0), "green": (0, 255, 0), "blue": (0, 0, 255)}.get(color, (0, 0, 0))
        if not state:
            rgb = (0, 0, 0)
        cmd = f"SET {rgb[0]},{rgb[1]},{rgb[2]}\n"
        ser.write(cmd.encode())
        print("[serial] Sent:", cmd.strip())
    except Exception as e:
        print("[serial] ❌ Send error:", e)


# ---------- GUI ----------
class LED_GUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🎤 Lumivox - Voice LED Controller")
        self.root.geometry("520x300")
        self.root.configure(bg="black")
        self.root.resizable(False, False)

        self.canvas = tk.Canvas(self.root, width=520, height=300, highlightthickness=0)
        self.canvas.pack()

        # BG colors
        self.canvas.create_rectangle(0, 0, 260, 300, fill="#0077ff", outline="")
        self.canvas.create_rectangle(260, 0, 520, 300, fill="#00cc66", outline="")

        self.root.bind("<Escape>", lambda e: self.safe_exit())
        self.positions = {"red": 110, "green": 260, "blue": 410}
        self.leds, self.glow, self.target = {}, {}, {}
        for c, x in self.positions.items():
            self.leds[c] = self.draw_led(x, 110, c)
            self.glow[c] = 0
            self.target[c] = 0

        self.status = self.canvas.create_text(
            260, 260, text="Say: 'turn on red', 'turn off blue'",
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
        for color, led in self.leds.items():
            current, target = self.glow[color], self.target[color]
            new = current + (target - current) * 0.1
            self.glow[color] = new
            b = int(50 + 205 * new)
            col = {"red": f"#{b:02x}0000", "green": f"#00{b:02x}00", "blue": f"#0000{b:02x}"}[color]
            self.canvas.itemconfig(led["body"], fill=col)
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
        print("🛑 GUI closed cleanly.")

    def run(self):
        self.root.mainloop()


# ---------- MODEL + MIC ----------
def load_model():
    path = ensure_model()
    print("🎤 Loading Vosk model from:", path)
    return Model(path)


def start_mic(model, prefer_wasapi=True):
    rec = KaldiRecognizer(model, 16000)
    rec.SetWords(True)
    q = queue.Queue()

    # --- find mic device automatically ---
    try:
        devices = sd.query_devices()
        input_devices = [i for i, d in enumerate(devices) if d["max_input_channels"] > 0]
        device_id = input_devices[0] if input_devices else None
        print(f"[mic] 🎙️ Auto-selected input device: {devices[device_id]['name']}")
    except Exception as e:
        print("[mic] ⚠️ Could not auto-detect device:", e)
        device_id = None

    def callback(indata, frames, t, status):
        q.put(bytes(indata))

    try:
        stream = sd.RawInputStream(samplerate=16000, channels=1, dtype='int16',
                                   device=device_id, callback=callback)
        stream.start()
        print("[mic] 🎧 Microphone stream started.")
        return rec, q, stream
    except Exception as e:
        print("[mic] ❌ Stream failed:", e)
        return rec, None, None


def listen_once(mic):
    if mic is None:
        return ""
    rec, q, stream = mic
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
        print("[mic] ⚠️ Error:", e)
    return ""


# ---------- COMMAND PARSING ----------
def parse_command(text):
    text = text.lower().strip().replace("reed", "red").replace("blew", "blue").replace("grin", "green")
    for color in ("red", "green", "blue"):
        if f"turn on {color}" in text or f"on {color}" in text:
            return color, True
        if f"turn off {color}" in text or f"off {color}" in text:
            return color, False
    return None, None


def check_exit(gui): return not gui.running
def cleanup(gui): gui.safe_exit()
