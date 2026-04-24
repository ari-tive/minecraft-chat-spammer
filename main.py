import sys
import tkinter as tk
from tkinter import ttk
from tkinter import scrolledtext
import logging
import queue
import time
import threading

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

        self._create_widgets()
        self._setup_logging()
        
        # Start the queue polling
        self.root.after(100, self._poll_log_queue)

    def _create_widgets(self):
        style = ttk.Style()
        style.theme_use('clam')
        
        # --- Top Section: Message Slots ---
        messages_frame = ttk.LabelFrame(self.root, text="Messages", padding=10)
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

        # Test Button
        test_btn = ttk.Button(config_frame, text="Test Log", command=self._test_log)
        test_btn.grid(row=1, column=3, sticky="e")

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
        
        # Remove any existing handlers
        if self.logger.hasHandlers():
            self.logger.handlers.clear()

        gh_formatter = logging.Formatter('[%(asctime)s] %(levelname)s: %(message)s', datefmt='%H:%M:%S')
        
        # Console handler just in case
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(gh_formatter)
        
        # GUI handler
        self.gui_handler = GuiLogHandler(self.log_queue)
        self.gui_handler.setFormatter(gh_formatter)
        
        self.logger.addHandler(console_handler)
        self.logger.addHandler(self.gui_handler)

    def _poll_log_queue(self):
        """Check the queue periodically and update the text widget safely from the main thread."""
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
        
    def _test_log(self):
        """Test button callback to emit a log."""
        self.logger.info("Test log generated.")
        self.messages_sent += 1
        self._update_counter_lbl()

    def _update_counter_lbl(self):
        self.counter_lbl.config(text=f"Messages Sent: {self.messages_sent}")


if __name__ == "__main__":
    root = tk.Tk()
    app = MinecraftSpammerApp(root)
    # emit an initial log
    app.logger.info("Application started. Waiting for configuration.")
    root.mainloop()
