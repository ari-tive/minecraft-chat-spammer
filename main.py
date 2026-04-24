import sys
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import logging
import queue
import time
import threading
import random
import pystray
from pynput import keyboard
from PIL import Image, ImageDraw
import pyautogui
import pyperclip

# Fail-safe: move mouse to corner to abort pyautogui
pyautogui.FAILSAFE = True

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
        self.root.title("Minecraft Chat Spammer Simulator")
        self.root.geometry("600x650")
        self.root.minsize(500, 600)
        
        # Grid weight configuration
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(2, weight=1)

        # Variables
        self.message_vars = [tk.StringVar() for _ in range(4)]
        self.interval_var = tk.DoubleVar(value=2.0)
        self.variance_var = tk.BooleanVar(value=True)
        self.messages_sent = 0
        self.log_queue = queue.Queue()
        self.is_running = False
        self.stop_event = threading.Event()
        self.current_msg_index = 0

        # UI Components
        self._create_widgets()
        self._setup_logging()
        
        # Threading/System Integration
        self._setup_hotkeys()
        self._setup_tray()
        
        # Protocols
        self.root.protocol("WM_DELETE_WINDOW", self._on_window_close)
        
        # Start the queue polling
        self.root.after(100, self._poll_log_queue)
        self.logger.info("Application initialized. Press F6 to Start (Global), F7 to Stop.")

    def _create_widgets(self):
        style = ttk.Style()
        style.theme_use('clam')
        
        # --- Top Section: Message Slots ---
        messages_frame = ttk.LabelFrame(self.root, text="Messages (Sequenced)", padding=10)
        messages_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        messages_frame.columnconfigure(1, weight=1)

        for i in range(4):
            ttk.Label(messages_frame, text=f"Slot {i+1}:").grid(row=i, column=0, sticky="w", pady=5)
            entry = ttk.Entry(messages_frame, textvariable=self.message_vars[i], width=50)
            entry.grid(row=i, column=1, sticky="ew", padx=5, pady=5)

        # --- Middle Section: Configuration ---
        config_frame = ttk.LabelFrame(self.root, text="Configuration", padding=10)
        config_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=5)
        config_frame.columnconfigure(1, weight=1)
        config_frame.columnconfigure(3, weight=1)

        # Interval
        ttk.Label(config_frame, text="Base Interval (sec):").grid(row=0, column=0, sticky="w", pady=5)
        interval_spin = ttk.Spinbox(config_frame, from_=0.1, to=60.0, increment=0.1, 
                                    textvariable=self.interval_var, width=8)
        interval_spin.grid(row=0, column=1, sticky="w", padx=5, pady=5)

        # Variance
        variance_check = ttk.Checkbutton(config_frame, text="Enable \u00B130% Variance", 
                                         variable=self.variance_var)
        variance_check.grid(row=0, column=2, sticky="w", padx=15, pady=5)

        # Hotkey Labels
        hotkeys_frame = ttk.Frame(config_frame)
        hotkeys_frame.grid(row=1, column=0, columnspan=3, sticky="w", pady=10)
        self.start_hotkey_lbl = ttk.Label(hotkeys_frame, text="Start: F6", font=("Segoe UI", 9, "bold"), foreground="green")
        self.start_hotkey_lbl.pack(side="left", padx=(0, 15))
        self.stop_hotkey_lbl = ttk.Label(hotkeys_frame, text="Stop: F7", font=("Segoe UI", 9, "bold"), foreground="red")
        self.stop_hotkey_lbl.pack(side="left")

        # Status indicator
        self.status_indicator = ttk.Label(config_frame, text="IDLE", foreground="gray", font=("Segoe UI", 10, "bold"))
        self.status_indicator.grid(row=1, column=3, sticky="e")

        # --- Bottom Section: Status & Logging ---
        status_frame = ttk.Frame(self.root, padding=10)
        status_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=5)
        status_frame.columnconfigure(0, weight=1)
        status_frame.rowconfigure(1, weight=1)

        # Counter Label
        self.counter_lbl = ttk.Label(status_frame, text=f"Messages Sent: {self.messages_sent}", font=("Segoe UI", 10, "bold"))
        self.counter_lbl.grid(row=0, column=0, sticky="w", pady=(0, 5))

        # Log Text Area
        self.log_text = scrolledtext.ScrolledText(status_frame, state='disabled', bg="black", fg="#00FF00", 
                                                  font=("Consolas", 10), wrap="word")
        self.log_text.grid(row=1, column=0, sticky="nsew")

    def _setup_logging(self):
        self.logger = logging.getLogger("SpammerLogger")
        self.logger.setLevel(logging.INFO)
        if self.logger.hasHandlers():
            self.logger.handlers.clear()

        gh_formatter = logging.Formatter('[%(asctime)s] %(levelname)s: %(message)s', datefmt='%H:%M:%S')
        self.gui_handler = GuiLogHandler(self.log_queue)
        self.gui_handler.setFormatter(gh_formatter)
        self.logger.addHandler(self.gui_handler)

    def _setup_hotkeys(self):
        """Initialize global hotkeys."""
        self.hotkey_listener = keyboard.GlobalHotKeys({
            '<f6>': self._trigger_start,
            '<f7>': self._trigger_stop
        })
        self.hotkey_listener.start()

    def _trigger_start(self):
        if not self.is_running:
            self.is_running = True
            self.stop_event.clear()
            threading.Thread(target=self._spam_worker, daemon=True).start()
            self.logger.info("[ENGINE] Spammer started via hotkey.")
            self.root.after(0, lambda: self.status_indicator.config(text="ACTIVE", foreground="green"))

    def _trigger_stop(self):
        if self.is_running:
            self.stop_event.set()
            self.is_running = False
            self.logger.info("[ENGINE] Stop signal received.")
            self.root.after(0, lambda: self.status_indicator.config(text="IDLE", foreground="gray"))

    def _spam_worker(self):
        """Main automation loop."""
        try:
            # 5-second countdown
            for i in range(5, 0, -1):
                if self.stop_event.is_set():
                    return
                self.logger.info(f"[ENGINE] Starting in {i} seconds... Switch to Minecraft!")
                time.sleep(1)

            if self.stop_event.is_set():
                return

            self.logger.info("[ENGINE] Automation ACTIVE.")
            
            while not self.stop_event.is_set():
                # Find next filled message slot
                messages = [v.get().strip() for v in self.message_vars]
                filled_slots = [i for i, m in enumerate(messages) if m]
                
                if not filled_slots:
                    self.logger.warning("[ENGINE] No messages to send. Fill at least one slot.")
                    self._trigger_stop()
                    break

                # Sequential cycling
                while True:
                    if self.current_msg_index >= 4:
                        self.current_msg_index = 0
                    
                    msg = messages[self.current_msg_index]
                    if msg:
                        break
                    self.current_msg_index += 1

                # Execute automation
                try:
                    pyautogui.press('t')
                    time.sleep(0.1)
                    pyperclip.copy(msg)
                    pyautogui.hotkey('ctrl', 'v')
                    time.sleep(0.1)
                    pyautogui.press('enter')
                    
                    self.messages_sent += 1
                    self.logger.info(f"[SENT] Slot {self.current_msg_index + 1}: {msg[:20]}...")
                    self.root.after(0, self._update_counter_lbl)
                except Exception as e:
                    self.logger.error(f"[ERROR] Automation failed: {e}")
                    break

                # Sequence to next slot
                self.current_msg_index += 1

                # Calculate next interval
                base = self.interval_var.get()
                if self.variance_var.get():
                    variance = base * 0.3
                    interval = base + random.uniform(-variance, variance)
                else:
                    interval = base
                
                interval = max(0.1, interval) # Safety floor
                
                # Sleep in increments to remain responsive to stop signal
                start_sleep = time.time()
                while time.time() - start_sleep < interval:
                    if self.stop_event.is_set():
                        return
                    time.sleep(0.1)

        except Exception as e:
            self.logger.error(f"[ENGINE] Fatal worker error: {e}")
        finally:
            self.is_running = False
            self.root.after(0, lambda: self.status_indicator.config(text="IDLE", foreground="gray"))

    def _create_tray_image(self):
        image = Image.new('RGB', (64, 64), color=(0, 128, 0))
        d = ImageDraw.Draw(image)
        d.rectangle([16, 16, 48, 48], fill=(255, 255, 255))
        return image

    def _setup_tray(self):
        menu = pystray.Menu(
            pystray.MenuItem("Show", self._show_window),
            pystray.MenuItem("Hide", self._hide_window),
            pystray.MenuItem("Exit", self._quit_app)
        )
        self.tray_icon = pystray.Icon("spammer", self._create_tray_image(), "MC Spammer", menu)
        threading.Thread(target=self.tray_icon.run, daemon=True).start()

    def _show_window(self, icon=None, item=None):
        self.root.after(0, self.root.deiconify)
        self.root.after(0, self.root.lift)

    def _hide_window(self, icon=None, item=None):
        self.root.after(0, self.root.withdraw)

    def _on_window_close(self):
        self.logger.info("Application minimized to tray.")
        self._hide_window()

    def _quit_app(self, icon=None, item=None):
        if hasattr(self, 'hotkey_listener'):
            self.hotkey_listener.stop()
        if hasattr(self, 'tray_icon'):
            self.tray_icon.stop()
        self.root.after(0, self.root.destroy)
        sys.exit(0)

    def _poll_log_queue(self):
        try:
            while True:
                msg = self.log_queue.get_nowait()
                self.log_text.configure(state='normal')
                self.log_text.insert(tk.END, msg + "\n")
                self.log_text.see(tk.END)
                self.log_text.configure(state='disabled')
        except queue.Empty:
            pass
        self.root.after(100, self._poll_log_queue)
        
    def _update_counter_lbl(self):
        self.counter_lbl.config(text=f"Messages Sent: {self.messages_sent}")


if __name__ == "__main__":
    root = tk.Tk()
    app = MinecraftSpammerApp(root)
    root.mainloop()
