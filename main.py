import sys
import os
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import logging
import queue
import time
import threading
import random
import ctypes
import ctypes.wintypes
import pystray
from pynput import keyboard
from PIL import Image, ImageDraw

# --- Windows API constants for SendInput ---
INPUT_KEYBOARD = 1
KEYEVENTF_KEYUP = 0x0002
KEYEVENTF_UNICODE = 0x0004
VK_RETURN = 0x0D
VK_ESCAPE = 0x1B
VK_CONTROL = 0x11

class KEYBDINPUT(ctypes.Structure):
    _fields_ = [("wVk", ctypes.wintypes.WORD),
                ("wScan", ctypes.wintypes.WORD),
                ("dwFlags", ctypes.wintypes.DWORD),
                ("time", ctypes.wintypes.DWORD),
                ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong))]

class INPUT(ctypes.Structure):
    class _INPUT(ctypes.Union):
        _fields_ = [("ki", KEYBDINPUT)]
    _fields_ = [("type", ctypes.wintypes.DWORD),
                ("_input", _INPUT)]

def _send_key(vk, flags=0):
    """Send a single virtual key event via Windows SendInput."""
    inp = INPUT(type=INPUT_KEYBOARD)
    inp._input.ki = KEYBDINPUT(wVk=vk, wScan=0, dwFlags=flags, time=0,
                                dwExtraInfo=ctypes.pointer(ctypes.c_ulong(0)))
    ctypes.windll.user32.SendInput(1, ctypes.pointer(inp), ctypes.sizeof(INPUT))

def _send_unicode_char(char):
    """Send a single unicode character via SendInput (KEYEVENTF_UNICODE)."""
    inp_down = INPUT(type=INPUT_KEYBOARD)
    inp_down._input.ki = KEYBDINPUT(wVk=0, wScan=ord(char), dwFlags=KEYEVENTF_UNICODE,
                                     time=0, dwExtraInfo=ctypes.pointer(ctypes.c_ulong(0)))
    inp_up = INPUT(type=INPUT_KEYBOARD)
    inp_up._input.ki = KEYBDINPUT(wVk=0, wScan=ord(char),
                                   dwFlags=KEYEVENTF_UNICODE | KEYEVENTF_KEYUP,
                                   time=0, dwExtraInfo=ctypes.pointer(ctypes.c_ulong(0)))
    ctypes.windll.user32.SendInput(1, ctypes.pointer(inp_down), ctypes.sizeof(INPUT))
    ctypes.windll.user32.SendInput(1, ctypes.pointer(inp_up), ctypes.sizeof(INPUT))

def send_string(text):
    """Type an entire string using Unicode SendInput (no clipboard needed)."""
    for char in text:
        _send_unicode_char(char)
        time.sleep(0.02)  # 20ms between characters — safe for Minecraft Java

def press_key(vk):
    """Press and release a virtual key."""
    _send_key(vk)
    time.sleep(0.01)
    _send_key(vk, KEYEVENTF_KEYUP)

def press_t_key():
    """Press 'T' to open Minecraft chat via virtual key code."""
    VK_T = 0x54
    _send_key(VK_T)
    time.sleep(0.01)
    _send_key(VK_T, KEYEVENTF_KEYUP)

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class GuiLogHandler(logging.Handler):
    """Custom logging handler to send logs to a Tkinter ScrolledText widget."""
    def __init__(self, log_queue):
        super().__init__()
        self.log_queue = log_queue

    def emit(self, record):
        self.log_queue.put(self.format(record))


class MinecraftSpammerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("MC Chat Spammer v1.0")
        self.root.geometry("620x680")
        self.root.minsize(550, 650)
        
        # UI Styles
        self.bg_color = "#f4f4f9"
        self.accent_color = "#2c3e50"
        self.root.configure(bg=self.bg_color)
        
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure("Custom.TLabelframe", background=self.bg_color)
        self.style.configure("Custom.TLabelframe.Label", font=("Segoe UI", 10, "bold"), foreground=self.accent_color)
        self.style.configure("Action.TButton", font=("Segoe UI", 9, "bold"))

        # Variables
        self.message_vars = [tk.StringVar() for _ in range(4)]
        self.interval_var = tk.DoubleVar(value=2.0)
        self.variance_var = tk.BooleanVar(value=True)
        self.unique_id_var = tk.BooleanVar(value=True)
        self.messages_sent = 0
        self.log_queue = queue.Queue()
        self.is_running = False
        self.stop_event = threading.Event()
        self.current_msg_index = 0

        # Grid weight configuration
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(2, weight=1)

        self._create_widgets()
        self._setup_logging()
        self._setup_hotkeys()
        self._setup_tray()
        
        self.root.protocol("WM_DELETE_WINDOW", self._on_window_close)
        self.root.after(100, self._poll_log_queue)
        self.logger.info("Ready. Press F6 to Start (Global), F7 to Stop.")

    def _create_widgets(self):
        # --- Top Section: Messages ---
        msg_frame = ttk.LabelFrame(self.root, text=" Message Slots (Sequential Cycle) ", padding=15, style="Custom.TLabelframe")
        msg_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 10))
        msg_frame.columnconfigure(1, weight=1)

        for i in range(4):
            ttk.Label(msg_frame, text=f"Msg {i+1}:", font=("Segoe UI", 9)).grid(row=i, column=0, sticky="w", pady=6)
            ent = ttk.Entry(msg_frame, textvariable=self.message_vars[i], font=("Segoe UI", 10))
            ent.grid(row=i, column=1, sticky="ew", padx=(10, 0), pady=6)

        # --- Middle Section: Config ---
        cfg_frame = ttk.LabelFrame(self.root, text=" Engine Settings ", padding=15, style="Custom.TLabelframe")
        cfg_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=10)
        cfg_frame.columnconfigure(1, weight=1)

        # Controls Row
        ctrl_frame = ttk.Frame(cfg_frame)
        ctrl_frame.grid(row=0, column=0, columnspan=2, sticky="w")
        
        ttk.Label(ctrl_frame, text="Interval (s):").pack(side="left")
        ttk.Spinbox(ctrl_frame, from_=0.1, to=60.0, increment=0.1, textvariable=self.interval_var, width=6).pack(side="left", padx=5)
        
        ttk.Checkbutton(ctrl_frame, text="±30% Random Variance", variable=self.variance_var).pack(side="left", padx=15)
        ttk.Checkbutton(ctrl_frame, text="Append Unique ID", variable=self.unique_id_var).pack(side="left", padx=10)

        # Status & Hotkey Info
        info_frame = ttk.Frame(cfg_frame)
        info_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(15, 0))
        
        self.status_dot = tk.Label(info_frame, text=" ● ", foreground="gray", font=("Segoe UI", 14), bg=self.bg_color)
        self.status_dot.pack(side="left")
        
        self.status_lbl = ttk.Label(info_frame, text="IDLE", font=("Segoe UI", 10, "bold"))
        self.status_lbl.pack(side="left")
        
        ttk.Label(info_frame, text=" |  Start: F6  |  Stop: F7", foreground="#7f8c8d").pack(side="left", padx=10)
        
        ttk.Button(info_frame, text="Reset Count", command=self._reset_counter, style="Action.TButton").pack(side="right")

        # --- Bottom Section: Logs ---
        log_frame = ttk.Frame(self.root, padding=20)
        log_frame.grid(row=2, column=0, sticky="nsew")
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(1, weight=1)

        self.counter_lbl = ttk.Label(log_frame, text=f"MESSAGES SENT: {self.messages_sent}", font=("Impact", 12))
        self.counter_lbl.grid(row=0, column=0, sticky="w", pady=(0, 8))

        self.log_text = scrolledtext.ScrolledText(log_frame, state='disabled', bg="#1e1e1e", fg="#00ff66", 
                                                  font=("Consolas", 9), borderwidth=0, padx=5, pady=5)
        self.log_text.grid(row=1, column=0, sticky="nsew")

    def _setup_logging(self):
        self.logger = logging.getLogger("Spammer")
        self.logger.setLevel(logging.INFO)
        if self.logger.hasHandlers(): self.logger.handlers.clear()
        
        fmt = logging.Formatter('[%(asctime)s] %(message)s', datefmt='%H:%M:%S')
        self.gui_handler = GuiLogHandler(self.log_queue)
        self.gui_handler.setFormatter(fmt)
        self.logger.addHandler(self.gui_handler)

    def _setup_hotkeys(self):
        self.hotkey_listener = keyboard.GlobalHotKeys({
            '<f6>': self._trigger_start,
            '<f7>': self._trigger_stop
        })
        self.hotkey_listener.start()

    def _create_tray_image(self):
        icon_path = resource_path("assets/icon.png")
        if os.path.exists(icon_path):
            try:
                return Image.open(icon_path)
            except Exception:
                pass
        
        # Fallback icon
        image = Image.new('RGB', (64, 64), color=(44, 62, 80))
        d = ImageDraw.Draw(image)
        d.rectangle([16, 16, 48, 48], fill=(46, 204, 113))
        return image

    def _setup_tray(self):
        menu = pystray.Menu(
            pystray.MenuItem("Show Window", self._show_window, default=True),
            pystray.MenuItem("Hide Window", self._hide_window),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Exit Application", self._quit_app)
        )
        self.tray_icon = pystray.Icon("mc_spammer", self._create_tray_image(), "MC Spammer", menu)
        threading.Thread(target=self.tray_icon.run, daemon=True).start()

    def _trigger_start(self):
        if self.is_running: return
        
        # Validation
        messages = [v.get().strip() for v in self.message_vars]
        if not any(messages):
            self.logger.error("[SYSTEM] Please fill at least one message slot!")
            return

        self.is_running = True
        self.stop_event.clear()
        threading.Thread(target=self._spam_worker, daemon=True).start()
        self.root.after(0, lambda: self._update_status_ui("ACTIVE", "#2ecc71"))

    def _trigger_stop(self):
        if not self.is_running: return
        self.stop_event.set()
        self.is_running = False
        self.logger.info("[ENGINE] Spammer stopped.")
        self.root.after(0, lambda: self._update_status_ui("IDLE", "gray"))

    def _spam_worker(self):
        try:
            # Countdown
            for i in range(5, 0, -1):
                if self.stop_event.is_set():
                    return
                self.logger.info(f"[ENGINE] Starting in {i}s... Switch Window!")
                time.sleep(1)

            if self.stop_event.is_set():
                return
            self.logger.info("[ENGINE] Status: RUNNING")

            while not self.stop_event.is_set():
                # Snapshot messages once per full cycle
                messages = [v.get().strip() for v in self.message_vars]
                filled = [(i, m) for i, m in enumerate(messages) if m]

                if not filled:
                    self.logger.warning("[ENGINE] No messages. Stopping.")
                    break

                for slot_index, msg in filled:
                    if self.stop_event.is_set():
                        break

                    # Build the final message
                    send_msg = msg
                    if self.unique_id_var.get():
                        send_msg = f"{msg} {random.randint(1000, 9999)}"

                    # Step 1: Escape to close any stale chat/menu
                    press_key(VK_ESCAPE)
                    time.sleep(0.3)

                    # Step 2: T to open fresh chat
                    press_t_key()
                    time.sleep(0.5)

                    # Step 3: Type message character by character
                    send_string(send_msg)
                    time.sleep(0.2)

                    # Step 4: Enter to send
                    press_key(VK_RETURN)
                    time.sleep(0.3)

                    self.messages_sent += 1
                    self.logger.info(f"[SENT] Slot {slot_index + 1}: {send_msg}")
                    self.root.after(0, self._refresh_counter)

                    # Wait for interval before next message
                    if self.stop_event.is_set():
                        break
                    try:
                        base = float(self.interval_var.get())
                    except (ValueError, tk.TclError):
                        base = 1.0

                    wait_time = base + (random.uniform(-base * 0.3, base * 0.3) if self.variance_var.get() else 0)
                    wait_time = max(0.5, wait_time)

                    elapsed = time.time()
                    while time.time() - elapsed < wait_time:
                        if self.stop_event.is_set():
                            break
                        time.sleep(0.05)

        except Exception as e:
            self.logger.error(f"[FATAL] {e}")
        finally:
            self.is_running = False
            self.root.after(0, lambda: self._update_status_ui("IDLE", "gray"))

    def _show_window(self, icon=None, item=None):
        self.root.after(0, self.root.deiconify)
        self.root.after(0, self.root.attributes, "-topmost", True)
        self.root.after(100, self.root.attributes, "-topmost", False)

    def _hide_window(self, icon=None, item=None):
        self.root.after(0, self.root.withdraw)

    def _on_window_close(self):
        self._hide_window()

    def _quit_app(self, icon=None, item=None):
        if hasattr(self, 'hotkey_listener'): self.hotkey_listener.stop()
        if hasattr(self, 'tray_icon'): self.tray_icon.stop()
        self.root.after(0, self.root.destroy)
        sys.exit(0)

    def _reset_counter(self):
        self.messages_sent = 0
        self._refresh_counter()
        self.logger.info("[UI] Counter reset.")

    def _refresh_counter(self):
        self.counter_lbl.config(text=f"MESSAGES SENT: {self.messages_sent}")

    def _update_status_ui(self, text, color):
        self.status_lbl.config(text=text)
        self.status_dot.config(foreground=color)

    def _poll_log_queue(self):
        try:
            while True:
                msg = self.log_queue.get_nowait()
                self.log_text.configure(state='normal')
                self.log_text.insert(tk.END, msg + "\n")
                self.log_text.see(tk.END)
                self.log_text.configure(state='disabled')
        except queue.Empty: pass
        self.root.after(100, self._poll_log_queue)


if __name__ == "__main__":
    root = tk.Tk()
    app = MinecraftSpammerApp(root)
    root.mainloop()
