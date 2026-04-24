---
phase: 2
plan: 2
wave: 1
---

# Plan 2.2: System Tray & Window Management

## Objective
Provide a "Minimize to Tray" experience to keep the application running in the background without cluttering the taskbar.

## Context
- .gsd/SPEC.md
- .gsd/REQUIREMENTS.md
- .gsd/RESEARCH.md
- main.py

## Tasks

<task type="auto">
  <name>Implement Pystray Daemon Thread</name>
  <files>main.py</files>
  <action>
    Integrate `pystray` into the application lifecycle.
    - Create a basic icon (use a simple colored square or a placeholder image using `PIL`).
    - Implement a `run_tray` method that initializes `pystray.Icon` with a menu: "Show", "Hide", and "Exit".
    - Start this method in a `threading.Thread(daemon=True)`.
    - Handle the "Exit" menu item by calling a new `_quit_app` method that stops the icon, the hotkey listener, and destroys the Tkinter root.
  </action>
  <verify>Check system tray for the icon and test the "Exit" menu item.</verify>
  <done>
    - Tray icon appears when the app starts.
    - Right-click menu contains Show/Hide/Exit.
    - Exit properly terminates all threads.
  </done>
</task>

<task type="auto">
  <name>Bind Tray Actions to Tkinter Visibility</name>
  <files>main.py</files>
  <action>
    Wire the tray menu actions to the GUI window state.
    - "Show": Call `root.after(0, root.deiconify)`.
    - "Hide": Call `root.after(0, root.withdraw)`.
    - Update the window "X" close button to "Minimize to Tray" instead of exiting (if preferred, or just rely on the tray menu). For this task, keep it simple: "Hide" in tray menu hides the window.
  </action>
  <verify>Click "Hide" in tray and verify window disappears; click "Show" and verify it returns.</verify>
  <done>
    - Window visibility can be toggled via the system tray menu.
  </done>
</task>

## Success Criteria
- [ ] Application can be minimized to the system tray.
- [ ] All background threads (Tray, Hotkeys) exit cleanly when the user selects "Exit".
