# RESEARCH.md — Threading & Bundling Investigation

## Threading Architecture
To integrate Tkinter (GUI), Pystray (System Tray), and Pynput (Global Hotkeys) without deadlocks or UI freezes:

### 1. Main Thread: Tkinter
- Must run `root.mainloop()`.
- Use `root.after(100, poll_queue)` to check for updates from background threads.
- Handle all UI widget updates ONLY here.

### 2. Background Thread 1: Pystray
- Run `icon.run()` in a `daemon=True` thread.
- Communicates with the Main Thread via `queue.Queue`.
- Example: "Minimize to Tray" puts a message in the queue for the Main Thread to call `root.withdraw()`.

### 3. Automatic Thread: Pynput
- `keyboard.Listener` starts its own thread.
- Should put event data into the `queue.Queue` (e.g., "START_SPAM" or "STOP_SPAM").

### 4. Background Thread 2: Spam Engine
- The actual loop that waits for the interval and calls `pyautogui` must run in its own thread to avoid freezing the GUI during the "5-second countdown" or the spamming process.
- Must check a `stop_event` flag frequently to allow instant stopping via hotkey.

## PyInstaller Bundling
To create a standalone `.exe` on Windows that includes the tray icon:

### Resource Path Resolution
Use a helper function to find icons inside the bundled temporary directory:
```python
import sys, os
def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)
```

### Build Command
```bash
pyinstaller --noconfirm --onefile --windowed --icon "app.ico" --add-data "icon.png;." main.py
```
- `--onefile`: Bundles everything into a single `.exe`.
- `--windowed`: Prevents a console window from appearing behind the GUI.
- `--add-data`: Essential for including the `.png` or `.ico` file used by the system tray.

## Libraries Needed
- `pyautogui`: Keyboard simulation.
- `pyperclip`: Copy/paste mechanism (more reliable than direct `pyautogui.typewrite`).
- `pynput`: Global hotkey listening.
- `pystray`: System tray icon and menu.
- `Pillows`: Icon image handling.
- `PyInstaller`: Deployment.
