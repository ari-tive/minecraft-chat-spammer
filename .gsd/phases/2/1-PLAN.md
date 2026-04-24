---
phase: 2
plan: 1
wave: 1
---

# Plan 2.1: Global Hotkey Integration

## Objective
Implement a robust global hotkey system that allows the user to start and stop the spamming process from anywhere in Windows, even when the application is minimized or Minecraft is focused.

## Context
- .gsd/SPEC.md
- .gsd/REQUIREMENTS.md
- .gsd/RESEARCH.md
- main.py

## Tasks

<task type="auto">
  <name>Implement Pynput Keyboard Listener</name>
  <files>main.py</files>
  <action>
    Integrate `pynput.keyboard.GlobalHotkeys` into the `MinecraftSpammerApp`.
    - Define a dictionary for hotkeys using the user's preferred defaults (F6 for Start, F7 for Stop).
    - Create handler functions `_on_start_hotkey` and `_on_stop_hotkey`.
    - These handlers must put a command (e.g., `{'type': 'HOTKEY', 'action': 'START'}`) into the `log_queue` (or a dedicated command queue) so the main thread can process them if needed, or trigger the engine directly if implemented.
    - For now, just log "[HOTKEY] Start pressed" and "[HOTKEY] Stop pressed" to the GUI log.
  </action>
  <verify>Run main.py and press F6/F7 while non-focused; check if the GUI log updates.</verify>
  <done>
    - Pynput listener is started in the application.
    - F6 and F7 triggers log messages in the GUI.
  </done>
</task>

<task type="auto">
  <name>Customizable Hotkey Persistence Placeholder</name>
  <files>main.py</files>
  <action>
    Update the GUI to reflect that hotkeys are active.
    - Change the hotkey labels in the "Configuration" frame to use a distinct color when the listener is running.
    - (Optional) Add a "Stop Listener" cleanup method to be used during application exit to ensure the thread closes properly.
  </action>
  <verify>Visually confirm the hotkey section looks integrated and "Enabled".</verify>
  <done>
    - UI correctly indicates active hotkey bindings.
  </done>
</task>

## Success Criteria
- [ ] Pressing F6/F7 global hotkeys triggers log entries in the application regardless of focus.
- [ ] No threading conflicts occur between pynput and Tkinter.
